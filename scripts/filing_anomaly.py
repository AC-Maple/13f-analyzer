"""Anomalous 13F review gate.

Pre-classification / pre-Bloomberg check for obviously unusable 13F
content (stub / dummy information tables). Intended for
build_fund_history.py now and run_13f_workflow.py later.

Does not change 13F amendment overlay, confidential-treatment handling,
or any financial calculation. A large quarter-over-quarter decline or an
early filing date alone is never a hard stop.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal


class ReviewRequired(Exception):
    """Human review is required before this quarter can continue."""


PLACEHOLDER_ISSUERS = frozenset({
    "", "none", "nan", "n/a", "na", "null", "0", "-", "--",
})

# Corroborating-only thresholds. None of these fire the hard stop alone.
ROW_COLLAPSE_RATIO = 0.20
VALUE_COLLAPSE_RATIO = 0.10
EARLY_FILING_DAYS = 15
SMALL_FILING_BYTES = 8000
SMALL_INFOTABLE_BYTES = 2000


def _as_number(value):
    if value is None or value == "":
        return None
    try:
        if isinstance(value, bool):
            return None
        if isinstance(value, Decimal):
            return int(value)
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None


def _is_zero(value) -> bool:
    number = _as_number(value)
    return number is not None and number == 0


def issuer_missing(name) -> bool:
    if name is None:
        return True
    try:
        if name != name:  # pandas / float NaN
            return True
    except Exception:
        pass
    text = str(name).strip()
    return text.casefold() in PLACEHOLDER_ISSUERS


def dummy_cusip(cusip) -> bool:
    if cusip is None:
        return True
    digits = "".join(ch for ch in str(cusip) if ch.isalnum())
    return digits == "" or set(digits) <= {"0"}


def is_dummy_row(row: dict) -> bool:
    """Structural stub row: dummy identity plus zero value and shares."""
    return (
        issuer_missing(row.get("nameOfIssuer"))
        and dummy_cusip(row.get("cusip"))
        and _is_zero(row.get("value"))
        and _is_zero(row.get("sshPrnamt"))
    )


def cover_page_totals(thirteenf):
    """Return as-reported (tableEntryTotal, tableValueTotal).

    Uses the primary-document summary page, not ThirteenF.total_value,
    which may scale thousands-unit filings.
    """
    info = getattr(thirteenf, "primary_form_information", None)
    summary = getattr(info, "summary_page", None) if info is not None else None
    if summary is None:
        return None, None
    holdings = _as_number(getattr(summary, "total_holdings", None))
    value = _as_number(getattr(summary, "total_value", None))
    return holdings, value


def infotable_size_bytes(thirteenf) -> int | None:
    xml = getattr(thirteenf, "infotable_xml", None)
    if isinstance(xml, str):
        return len(xml.encode("utf-8"))
    if isinstance(xml, (bytes, bytearray)):
        return len(xml)
    return None


def _parse_iso_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()[:10]
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def days_from_period_to_filing(period: str, filing_date) -> int | None:
    period_d = _parse_iso_date(period)
    filed_d = _parse_iso_date(filing_date)
    if period_d is None or filed_d is None:
        return None
    return (filed_d - period_d).days


def format_usd_compact(value) -> str:
    number = _as_number(value)
    if number is None:
        return "n/a"
    if number == 0:
        return "$0"
    sign = "-" if number < 0 else ""
    abs_n = abs(number)
    if abs_n >= 1_000_000_000:
        text = f"{abs_n / 1_000_000_000:.2f}".rstrip("0").rstrip(".")
        return f"{sign}${text}B"
    if abs_n >= 1_000_000:
        text = f"{abs_n / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"{sign}${text}M"
    return f"{sign}${abs_n:,}"


@dataclass
class AnomalyDecision:
    review_required: bool
    manager_name: str
    cik: str
    period: str
    accession: str
    row_count: int
    table_entry_total: int | None
    table_value_total: int | None
    reported_value: int | None
    dummy_cusips: list[str] = field(default_factory=list)
    missing_issuer: bool = False
    structural_dummy_table: bool = False
    corroborating: list[str] = field(default_factory=list)
    prior_quarters: list[dict] = field(default_factory=list)


def assess_anomalous_13f(
    *,
    manager_name: str,
    cik: str,
    period: str,
    accession: str,
    rows: list,
    table_entry_total=None,
    table_value_total=None,
    infotable_bytes=None,
    filing_bytes=None,
    filing_date=None,
    prior_quarters=None,
) -> AnomalyDecision:
    """Hard-stop only on structural dummy/stub evidence.

    Cover-page 1-entry / $0 plus a dummy CUSIP / missing issuer / zero
    value / zero shares table is sufficient. Prior-quarter collapse,
    tiny filing size, and early filing date only corroborate.
    """
    prior_quarters = list(prior_quarters or [])
    row_count = len(rows)
    dummy_rows = [row for row in rows if is_dummy_row(row)]
    structural = bool(rows) and len(dummy_rows) == row_count

    parsed_value_sum = 0
    saw_value = False
    for row in rows:
        number = _as_number(row.get("value"))
        if number is not None:
            parsed_value_sum += number
            saw_value = True
    cover_value = _as_number(table_value_total)
    reported_value = cover_value if cover_value is not None else (
        parsed_value_sum if saw_value else None
    )

    dummy_cusips = []
    for row in rows:
        if dummy_cusip(row.get("cusip")):
            dummy_cusips.append(str(row.get("cusip") or ""))
    missing = any(issuer_missing(row.get("nameOfIssuer")) for row in rows)

    corroborating = []
    if prior_quarters:
        prior_rows = [p.get("row_count") for p in prior_quarters if p.get("row_count")]
        prior_vals = [p.get("value_total") for p in prior_quarters if p.get("value_total")]
        if prior_rows:
            max_prior_rows = max(prior_rows)
            if max_prior_rows >= 10 and row_count <= 1:
                corroborating.append("extreme collapse in row count")
            elif row_count / max_prior_rows <= ROW_COLLAPSE_RATIO:
                corroborating.append("extreme collapse in row count")
        if prior_vals and reported_value is not None:
            max_prior_val = max(prior_vals)
            if max_prior_val > 0 and reported_value == 0:
                corroborating.append("extreme collapse in filed value")
            elif reported_value / max_prior_val <= VALUE_COLLAPSE_RATIO:
                corroborating.append("extreme collapse in filed value")
        prior_sizes = [p.get("filing_bytes") for p in prior_quarters if p.get("filing_bytes")]
        if filing_bytes is not None and prior_sizes and filing_bytes < 0.3 * min(prior_sizes):
            corroborating.append("unusually small filing")
        elif filing_bytes is not None and filing_bytes < SMALL_FILING_BYTES:
            corroborating.append("unusually small filing")
        prior_xml = [p.get("infotable_bytes") for p in prior_quarters if p.get("infotable_bytes")]
        if infotable_bytes is not None and prior_xml and infotable_bytes < 0.3 * min(prior_xml):
            corroborating.append("unusually small information table")
        elif infotable_bytes is not None and infotable_bytes < SMALL_INFOTABLE_BYTES:
            corroborating.append("unusually small information table")
    else:
        if filing_bytes is not None and filing_bytes < SMALL_FILING_BYTES:
            corroborating.append("unusually small filing")
        if infotable_bytes is not None and infotable_bytes < SMALL_INFOTABLE_BYTES:
            corroborating.append("unusually small information table")

    lag = days_from_period_to_filing(period, filing_date)
    if lag is not None and 0 <= lag < EARLY_FILING_DAYS:
        corroborating.append("unusually early filing date")

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for item in corroborating:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    return AnomalyDecision(
        review_required=structural,
        manager_name=manager_name,
        cik=str(cik),
        period=period,
        accession=accession,
        row_count=row_count,
        table_entry_total=_as_number(table_entry_total),
        table_value_total=cover_value,
        reported_value=reported_value,
        dummy_cusips=dummy_cusips,
        missing_issuer=missing,
        structural_dummy_table=structural,
        corroborating=unique,
        prior_quarters=prior_quarters,
    )


def format_review_report(decision: AnomalyDecision) -> str:
    cik = decision.cik.lstrip("0") or "0"
    lines = [
        "REVIEW REQUIRED — ANOMALOUS 13F FILING",
        "",
        f"Manager: {decision.manager_name}",
        f"CIK: {cik}",
        f"Period: {decision.period}",
        f"Accession: {decision.accession}",
        "",
        "Current filing:",
        f"- {decision.row_count} information-table row"
        f"{'' if decision.row_count == 1 else 's'}",
        f"- {format_usd_compact(decision.reported_value)} reported value",
    ]
    if decision.dummy_cusips:
        shown = decision.dummy_cusips[0] or "000000000"
        lines.append(f"- dummy CUSIP {shown}")
    if decision.missing_issuer:
        lines.append("- missing issuer")
    lines += ["", "Prior quarters:"]
    if decision.prior_quarters:
        priors = sorted(
            decision.prior_quarters,
            key=lambda p: str(p.get("period") or ""),
            reverse=True,
        )
        for prior in priors:
            lines.append(
                f"- {prior.get('period')}: {prior.get('row_count')} rows / "
                f"{format_usd_compact(prior.get('value_total'))}"
            )
    else:
        lines.append("- none available in this run")
    lines += [
        "",
        "Action:",
        "Hold this quarter until a valid replacement/amendment appears "
        "or a documented manual resolution is entered.",
        "",
        "STATUS: REVIEW REQUIRED",
    ]
    return "\n".join(lines)
