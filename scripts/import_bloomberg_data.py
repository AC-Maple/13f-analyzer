"""
import_bloomberg_data.py -- Reads the refreshed Bloomberg workbook back
in and produces a clean market-data file for price_verify.py / liquidity.py.

Read with load_workbook(data_only=True). This ONLY works on a file that
was actually opened and refreshed in real Excel with the Bloomberg
Add-in -- that's what leaves cached values behind for the formula cells.
A file passed through openpyxl/LibreOffice without ever touching a
Bloomberg session reads back as None everywhere (see xlsx skill notes on
data_only + recalc).

Bloomberg writes literal error TEXT into a cell when a lookup fails --
it does not leave the cell blank and does not raise. These strings must
be caught explicitly or they get treated as data:
  #N/A Invalid Security   -- identifier didn't resolve (bad CUSIP, no
                              Bloomberg coverage -- common for OTC
                              warrants and thinly-covered small caps)
  #N/A Field Not Applicable -- security exists but this field doesn't
                              apply to it (e.g. EQY_SH_OUT on some
                              structures)
  #N/A Requesting Data    -- the Add-in hadn't finished refreshing when
                              the file was saved; re-open and re-save
Never treat any of these as zero, blank, or "no position" -- they mean
"the market-data layer has nothing for this security," which is a
PENDING_EXTERNAL_DATA / REVIEW state, not a clean zero.

Cross-references resolution_log.py for the "no PX_LAST at all" case
specifically -- this is the one that fully excludes a security from
liquidity.py's ADV model, so it's the one worth a recorded human
decision, not every PENDING_EXTERNAL_DATA field individually (a
warrant's blank VOLUME_AVG_3M, for instance, is expected by design and
not worth a resolution-log entry). Without this, a name with genuinely
no Bloomberg coverage re-surfaces identically on every future import,
with no way to record "yes, checked, this one just isn't covered."

Usage (from the repo root, or from scripts/; PowerShell):

  python scripts/import_bloomberg_data.py --input data/bloomberg_template_1856103_2026-06-30.xlsx --classified data/classified_rows_1856103_2026-06-30.json --output data/market_data_1856103_2026-06-30.json

  python scripts/import_bloomberg_data.py bloomberg_template.xlsx pinnbrook
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import load_workbook

from fund_io import (
    CLASSIFIED_NAME_RE,
    DATA_DIR,
    SCRIPTS_DIR,
    FundBuildError,
    load_json,
    market_write_path,
    normalize_cik,
    parse_quarter,
    resolve_manager,
    shared_working_files,
    validate_classified,
    write_market_snapshot,
)
from resolution_log import make_exception_id, get_resolution, derive_quarter_label

DEFAULT_INPUT_FILE = "bloomberg_template.xlsx"
DEFAULT_FUND_NAME = "fund"
DEFAULT_OUTPUT_FILE = "data/market_data.json"

BLOOMBERG_ERROR_PATTERN = re.compile(r"^#N/A", re.IGNORECASE)

# Same 80% gate as dashboard.persist_quarter_market_data -- duplicated
# here so this module does not import dashboard.py. Do not change the
# formula independently of that function.
MARKET_STAMP_MIN_PRECISION = 0.80

TEMPLATE_NAME_RE = re.compile(
    r"^bloomberg_template_(.+)_(\d{4}-\d{2}-\d{2})\.xlsx$"
)
MARKET_NAME_RE = re.compile(
    r"^market_data_(.+)_(\d{4}-\d{2}-\d{2})\.json$"
)

# (column, expected_type) -- PARSEKYABLE_DES is a string identifier
# ("NVDA US Equity"), not a number, and needs different validation than
# the five numeric market-data fields. Both /cusip/ identifiers and all
# six fields below are user-confirmed against a live Bloomberg session,
# 2026-09-02.
FIELD_COLUMNS = {
    "PX_LAST": (4, "numeric"),
    "EQY_SH_OUT": (5, "numeric"),
    "CUR_MKT_CAP": (6, "numeric"),
    "VOLUME_AVG_20D": (7, "numeric"),
    "VOLUME_AVG_3M": (8, "numeric"),
    "PARSEKYABLE_DES": (9, "string"),
    # Restored 2026-09-11 -- these two entries and the ws.cell()-based
    # row loop below (see the note there) were both silently dropped
    # when this file was rewritten for the liquidity_override feature,
    # reverting two already-shipped, already-verified fixes without
    # anyone deciding to. Found by testing against Melqart's real
    # refreshed workbook: it has real, populated GICS data for all 40
    # positions (confirmed by reading the raw cell values directly),
    # but zero of the 40 resulting market_data.json records carried a
    # GICS_INDUSTRY_NAME key at all until this was restored. GICS
    # mnemonics live-confirmed 2026-09-08 -- see SKILL.md's "Sector
    # classification field verification (GICS, live-tested)" section.
    "GICS_INDUSTRY_NAME": (10, "string"),
    "GICS_SUB_INDUSTRY_NAME": (11, "string"),
}
HEADER_ROW = 4


def classify_cell(value, expected_type):
    """Returns (clean_value, status). status is PASS, PENDING_EXTERNAL_DATA
    (Bloomberg error or genuinely blank), NOT_APPLICABLE (warrant ADV,
    by design), or REVIEW_MARKET_DATA (a value that parsed but looks
    structurally wrong for its expected type)."""
    if value is None:
        return None, "PENDING_EXTERNAL_DATA"

    if isinstance(value, str):
        if BLOOMBERG_ERROR_PATTERN.match(value.strip()):
            return None, "PENDING_EXTERNAL_DATA"
        if value.strip().upper() in ("N/A -- WARRANT, NO ADV MODEL",):
            return None, "NOT_APPLICABLE"
        if expected_type == "string":
            # A real Bloomberg identifier, e.g. "NVDA US Equity" --
            # this is the expected, valid shape for this field.
            if value.strip():
                return value.strip(), "PASS"
            return None, "PENDING_EXTERNAL_DATA"
        # A stray string in a NUMERIC field is unexpected -- never
        # coerce it silently.
        return None, "REVIEW_MARKET_DATA"

    if isinstance(value, (int, float)):
        if expected_type == "string":
            # Bloomberg identifiers should never come back numeric.
            return None, "REVIEW_MARKET_DATA"
        if value < 0:
            return value, "REVIEW_MARKET_DATA"
        if value == 0:
            # A genuine zero is implausible for every numeric field this
            # pipeline pulls (price, shares outstanding, market cap,
            # 20-day/3-month average volume) -- a real, currently-held
            # 13F position cannot have a $0 price or 0 shares outstanding,
            # and an actively-traded common stock cannot average literally
            # zero shares traded across an entire 20-day or 3-month window.
            # Found on real data (Melqart): Electronic Arts and Chart
            # Industries both showed VOLUME_AVG_20D=0 after a genuine,
            # deliberate live re-refresh (ruling out a stale/mid-calculation
            # read) -- while PX_LAST, PARSEKYABLE_DES, and other fields on
            # the same rows resolved correctly, so this wasn't a broader
            # identifier-resolution failure either. A 0 that PASSES here
            # was already silently distrusted downstream: compute_liquidity
            # (liquidity.py) has its own "adv <= 0" guard that treats it as
            # unusable regardless of this status -- meaning the status
            # field was claiming "trustworthy" for a value the rest of the
            # pipeline was already treating as worthless. That inconsistency
            # is the actual bug: a crash was never the risk (the downstream
            # guard already prevented one), a misleading PASS status was.
            return value, "REVIEW_MARKET_DATA"
        return value, "PASS"

    return None, "REVIEW_MARKET_DATA"


@contextmanager
def _scripts_cwd():
    previous = Path.cwd()
    os.chdir(SCRIPTS_DIR)
    try:
        yield
    finally:
        os.chdir(previous)


def _die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def read_workbook(input_file):
    wb = load_workbook(input_file, data_only=True)
    ws = wb.active

    results = []
    for row_num in range(HEADER_ROW + 1, ws.max_row + 1):
        # Restored 2026-09-11 -- addressed by (row, column) via ws.cell(),
        # not by indexing into the row tuple from iter_rows(). That tuple
        # is only as wide as openpyxl thinks the sheet's used range is,
        # which can be narrower than max(FIELD_COLUMNS) on a workbook
        # exported before a newer column existed (e.g. a pre-GICS
        # bloomberg_template.xlsx re-run through a newer FIELD_COLUMNS).
        # ws.cell() on a column past the sheet's populated range just
        # returns an empty cell (value=None), which classify_cell already
        # treats as PENDING_EXTERNAL_DATA -- exactly the right outcome for
        # "this workbook predates this field," not a crash. This exact fix
        # was already shipped once (Pinnbrook session) and was silently
        # reverted when this file was rewritten for liquidity_override;
        # restoring it here rather than leaving the fragile version in
        # place now that the regression was found.
        cusip_val = ws.cell(row=row_num, column=2).value
        if cusip_val in (None, ""):
            continue
        cusip = str(cusip_val).strip()
        issuer = ws.cell(row=row_num, column=1).value

        record = {"cusip": cusip, "issuer": issuer}
        for field, (col_idx, expected_type) in FIELD_COLUMNS.items():
            cell = ws.cell(row=row_num, column=col_idx)
            clean_value, status = classify_cell(cell.value, expected_type)
            record[field] = clean_value
            record[f"{field}_status"] = status
        results.append(record)
    return results


def apply_resolutions(results, fund_name, quarter):
    # Per-(cusip, field) exception IDs, covering EVERY field this pipeline
    # pulls -- not just PX_LAST's "no coverage at all" case as before. The
    # VOLUME_AVG_20D=0 fix above produces REVIEW_MARKET_DATA on individual
    # fields (found on Melqart's real data: EA, Chart Industries, Catalyst
    # Pharmaceuticals) that had no exception ID at all under the old,
    # PX_LAST-only scope -- meaning there was no way to even attach a
    # resolution to them. This replaces that narrower mechanism rather than
    # running two parallel ones; PX_LAST is just one of the fields covered
    # now, not a special case.
    still_open = []
    already_resolved_no_value = []

    for r in results:
        for field in FIELD_COLUMNS:
            status = r[f"{field}_status"]
            if status not in ("REVIEW_MARKET_DATA", "PENDING_EXTERNAL_DATA"):
                continue
            exception_id = make_exception_id(fund_name, quarter, f"marketdata_{field}", r["cusip"])
            resolution = get_resolution(exception_id)

            if resolution and resolution["decision"] == "CORRECT" and resolution.get("correction") is not None:
                _, expected_type = FIELD_COLUMNS[field]
                raw_correction = resolution["correction"]
                if expected_type == "numeric":
                    try:
                        corrected_value = float(raw_correction)
                    except (TypeError, ValueError):
                        # A human recorded a CORRECT decision but the stored
                        # correction doesn't parse as a number for a numeric
                        # field -- never silently apply it. Surfaced as still
                        # open, same as no resolution at all, rather than
                        # guessing what was meant.
                        r[f"{field}_exception_id"] = exception_id
                        still_open.append((r, field, exception_id, None))
                        continue
                else:
                    corrected_value = raw_correction
                r[field] = corrected_value
                r[f"{field}_status"] = "PASS_HUMAN_CORRECTED"
                r[f"{field}_correction_source"] = (
                    f"CORRECT by {resolution['reviewer']} at {resolution['timestamp']}"
                    + (f" -- {resolution['note']}" if resolution.get("note") else "")
                )
            elif resolution:
                # APPROVE or ESCALATE -- a human has looked at this, but
                # there's no replacement value to apply. Still flagged (the
                # underlying value is still whatever Bloomberg returned),
                # but shown as already-reviewed, not a fresh gap.
                r[f"{field}_exception_id"] = exception_id
                r[f"{field}_human_resolution"] = (
                    f"{resolution['decision']} by {resolution['reviewer']} at {resolution['timestamp']}"
                    + (f" -- {resolution['note']}" if resolution.get("note") else "")
                )
                already_resolved_no_value.append((r, field, exception_id, resolution))
            else:
                r[f"{field}_exception_id"] = exception_id
                still_open.append((r, field, exception_id, None))

        # Liquidity override -- separate from the per-field mechanism above
        # and checked unconditionally for every CUSIP, not just ones with a
        # flagged field. A resolved cash merger (Chart Industries / Baker
        # Hughes, $210.00/share all-cash, closed 7/16/2026) isn't a
        # correction to what Bloomberg's VOLUME_AVG_20D "really" is -- no
        # finite ADV number produces exactly 0 days to liquidate through the
        # normal shares/(adv*rate) formula, it only ever approaches zero.
        # Forcing this through the per-field correction mechanism would mean
        # inventing a fake trading volume for a security that no longer
        # trades at all. This is a distinct kind of fact -- "this position
        # is now a contractually guaranteed cash claim" -- so it gets its
        # own exception scope and bypasses the ADV math entirely in
        # liquidity.py, rather than feeding a fabricated number into it.
        liq_override_id = make_exception_id(fund_name, quarter, "liquidity_override", r["cusip"])
        liq_resolution = get_resolution(liq_override_id)
        if liq_resolution and liq_resolution["decision"] == "CORRECT" and liq_resolution.get("correction"):
            r["liquidityOverride"] = liq_resolution["correction"]
            r["liquidityOverrideSource"] = (
                f"CORRECT by {liq_resolution['reviewer']} at {liq_resolution['timestamp']}"
                + (f" -- {liq_resolution['note']}" if liq_resolution.get("note") else "")
            )
        r["liquidity_override_exception_id"] = liq_override_id  # always recorded, whether resolved or not -- lets a human resolve it later without re-deriving the id

    return still_open, already_resolved_no_value


def print_import_report(results, input_file, output_file, still_open, already_resolved_no_value):
    print(f"Read {len(results)} securities from {input_file}")

    all_statuses = [record[f"{field}_status"] for record in results for field in FIELD_COLUMNS]
    pending = sum(1 for s in all_statuses if s == "PENDING_EXTERNAL_DATA")
    review = sum(1 for s in all_statuses if s == "REVIEW_MARKET_DATA")
    na = sum(1 for s in all_statuses if s == "NOT_APPLICABLE")
    passed = sum(1 for s in all_statuses if s == "PASS")
    corrected = sum(1 for s in all_statuses if s == "PASS_HUMAN_CORRECTED")
    print(f"  {passed} field values PASS")
    if corrected:
        print(f"  {corrected} PASS_HUMAN_CORRECTED (Bloomberg value replaced by a recorded human correction)")
    print(f"  {pending} PENDING_EXTERNAL_DATA (Bloomberg error or blank -- no coverage or not yet refreshed)")
    print(f"  {review} REVIEW_MARKET_DATA (unexpected value -- needs a look)")
    print(f"  {na} NOT_APPLICABLE (warrant ADV, as expected)")

    if still_open:
        print(f"\n{len(still_open)} field(s) need a decision:")
        for r, field, exception_id, _ in still_open:
            print(f"    {r['cusip']}  {r['issuer']:30s} {field:16s} [{exception_id}]")
        print(f"\n  python resolution_log.py resolve <exception_id> APPROVE <reviewer> [note]")
        print(f"  python resolution_log.py resolve <exception_id> ESCALATE <reviewer> [note]")
        print(f"  python resolution_log.py resolve <exception_id> CORRECT <reviewer> <correction_value> [note]")

    if already_resolved_no_value:
        print(f"\n{len(already_resolved_no_value)} field(s) previously reviewed (APPROVE/ESCALATE, no replacement value) -- not fresh flags:")
        for r, field, exception_id, resolution in already_resolved_no_value:
            print(f"    {r['cusip']}  {r['issuer']:30s} {field:16s} -- {resolution['decision']} by {resolution['reviewer']}")

    print(f"\nWrote {output_file}")


def bloomberg_pulled_at_now():
    """UTC stamp taken when this import accepts a refreshed workbook.

    Not workbook mtime, not dashboard build time, not HTML-open time.
    The workbook has no Bloomberg LAST_UPDATE column — Excel core.xml
    modified is save time, not a Bloomberg refresh field — so import
    time is the authoritative provenance.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def write_market_json(path, records, meta=None):
    write_market_snapshot(Path(path), records, meta)


def filing_cusips_from_rows(rows):
    return {r.get("cusip") for r in (rows or []) if r.get("cusip")}


def filter_matched_market_records(records, classified_rows, output_path):
    """Same 80% precision gate as dashboard.persist_quarter_market_data."""
    filing_cusips = filing_cusips_from_rows(classified_rows)
    market_cusips = {r.get("cusip") for r in records if r.get("cusip")}
    matched = filing_cusips & market_cusips
    if not market_cusips:
        raise FundBuildError(
            f"Refusing to write {output_path}: market data has no CUSIPs, so it "
            f"cannot be this filing's quarter-specific snapshot "
            f"({len(filing_cusips)} filing CUSIPs)."
        )
    precision = len(matched) / len(market_cusips)
    if precision < MARKET_STAMP_MIN_PRECISION:
        raise FundBuildError(
            f"Refusing to write {output_path}: only {len(matched)} of "
            f"{len(market_cusips)} market-data CUSIPs ({precision:.1%}) "
            f"appear in this filing ({len(filing_cusips)} CUSIPs). "
            f"Need {MARKET_STAMP_MIN_PRECISION:.0%} overlap so a different "
            f"fund's pull cannot overwrite this quarter's GICS snapshot."
        )
    matched_records = [r for r in records if r.get("cusip") in matched]
    dropped = len(records) - len(matched_records)
    return matched_records, dropped


def _assert_not_shared_classified(path: Path) -> None:
    _parsed_shared, classified_shared, _market_shared = shared_working_files()
    if path.name == "classified_rows.json" or _resolved(path) == _resolved(classified_shared):
        raise FundBuildError(
            "Stamped import does not read data/classified_rows.json. "
            "Pass a stamped classified_rows_{cik}_{period}.json."
        )


def _assert_not_shared_output(path: Path, canonical: Path) -> None:
    _parsed_shared, _classified_shared, market_shared = shared_working_files()
    if path.name == "market_data.json" or _resolved(path) == _resolved(market_shared):
        raise FundBuildError(
            f"Stamped import refuses to write shared {market_shared}. "
            f"Use {canonical.name}."
        )


def load_stamped_classified(path: Path):
    _assert_not_shared_classified(path)
    if not path.exists():
        raise FundBuildError(f"Classified file not found: {path}")
    match = CLASSIFIED_NAME_RE.match(path.name)
    if not match:
        raise FundBuildError(
            f"{path.name} is not a stamped classified_rows_{{cik|slug}}_"
            f"{{period}}.json. Refusing to use it as a stamped classified file."
        )
    rows = load_json(path)
    if not rows:
        raise FundBuildError(f"{path}: classified file is empty")
    cik = normalize_cik(rows[0].get("_source_cik"))
    period = rows[0].get("_source_period_of_report")
    if not period:
        raise FundBuildError(
            f"{path}: classified rows have no _source_period_of_report. "
            "Refusing to guess the quarter."
        )
    period = parse_quarter(str(period))
    validate_classified(rows, cik, period, path)

    token, file_period = match.group(1), match.group(2)
    if file_period != period:
        raise FundBuildError(
            f"{path}: filename period {file_period!r} does not match "
            f"classified rows period {period!r}."
        )
    manager = resolve_manager(cik)
    if token not in (manager.cik, manager.slug):
        raise FundBuildError(
            f"{path}: filename token {token!r} is not CIK {manager.cik} "
            f"or slug {manager.slug!r}. Refusing to use another fund's file."
        )
    return rows, manager, period


def validate_template_stamp(path: Path, cik: str, period: str) -> None:
    match = TEMPLATE_NAME_RE.match(path.name)
    if not match:
        return
    token, file_period = match.group(1), match.group(2)
    try:
        token_cik = normalize_cik(token)
    except FundBuildError:
        raise FundBuildError(
            f"{path}: Bloomberg template stamp {token!r} is not a CIK. "
            f"Expected bloomberg_template_{cik}_{period}.xlsx."
        ) from None
    if token_cik != cik or file_period != period:
        raise FundBuildError(
            f"{path}: template is CIK {token_cik} period {file_period}, "
            f"not {cik} / {period}. Refusing to import another "
            f"fund/quarter's workbook."
        )


def validate_output_path(output: Path, cik: str, period: str, canonical: Path) -> None:
    _assert_not_shared_output(output, canonical)
    match = MARKET_NAME_RE.match(output.name)
    if not match:
        raise FundBuildError(
            f"{output}: output is not a stamped market_data_{{cik}}_"
            f"{{period}}.json. Expected {canonical}."
        )
    token, file_period = match.group(1), match.group(2)
    try:
        token_cik = normalize_cik(token)
    except FundBuildError:
        token_cik = None
    if token_cik != cik or file_period != period:
        raise FundBuildError(
            f"{output}: output stamp is {token!r} / {file_period}, not "
            f"{cik} / {period}. Refusing to overwrite another "
            f"fund/quarter snapshot."
        )
    if _resolved(output) != _resolved(canonical):
        raise FundBuildError(
            f"{output}: resolved path is not the canonical snapshot {canonical}."
        )


def finalize_and_write(
    results, fund_name, classified_rows, input_file, output_file,
    bloomberg_pulled_at=None,
):
    quarter = derive_quarter_label(classified_rows)
    still_open, already_resolved_no_value = apply_resolutions(
        results, fund_name, quarter
    )
    meta = {}
    output_path = Path(output_file)
    if bloomberg_pulled_at and MARKET_NAME_RE.match(output_path.name):
        meta["bloombergPulledAt"] = bloomberg_pulled_at
    write_market_json(output_file, results, meta or None)
    if meta.get("bloombergPulledAt"):
        print(f"Bloomberg pulled at {meta['bloombergPulledAt']}")
    print_import_report(
        results, input_file, output_file, still_open, already_resolved_no_value
    )


def run_legacy(input_file, fund_name):
    results = read_workbook(input_file)
    try:
        with open("data/classified_rows.json") as f:
            classified_rows = json.load(f)
    except FileNotFoundError:
        classified_rows = []
    finalize_and_write(
        results, fund_name, classified_rows, input_file, DEFAULT_OUTPUT_FILE,
        bloomberg_pulled_at=None,
    )


def run_stamped(input_file, classified_path, output_arg, fund_arg):
    classified_path = Path(classified_path)
    input_path = Path(input_file)
    rows, manager, period = load_stamped_classified(classified_path)
    if not input_path.exists():
        raise FundBuildError(f"Bloomberg workbook not found: {input_path}")
    validate_template_stamp(input_path, manager.cik, period)

    canonical = market_write_path(manager, period)
    if output_arg:
        output_path = Path(output_arg)
        validate_output_path(output_path, manager.cik, period, canonical)
    else:
        output_path = canonical
        _assert_not_shared_output(output_path, canonical)

    results = read_workbook(str(input_path))
    matched, dropped = filter_matched_market_records(results, rows, output_path)
    if dropped:
        print(
            f"Quarter market snapshot {output_path} keeping "
            f"{len(matched)} CUSIPs matching this filing; dropped "
            f"{dropped} unmatched market-data row(s)."
        )

    fund_name = fund_arg if fund_arg else manager.slug
    finalize_and_write(
        matched, fund_name, rows, str(input_path), output_path,
        bloomberg_pulled_at=bloomberg_pulled_at_now(),
    )
    print(
        "Shared working files were not used: classified_rows.json, "
        "market_data.json."
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Import a refreshed Bloomberg workbook into market-data JSON. "
            "Stamped flag mode writes only data/market_data_{cik}_{period}.json. "
            "Legacy positional mode still writes data/market_data.json."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Stamped import (PowerShell, one line):\n"
            "  python scripts/import_bloomberg_data.py --input data/bloomberg_template_1856103_2026-06-30.xlsx --classified data/classified_rows_1856103_2026-06-30.json --output data/market_data_1856103_2026-06-30.json\n"
            "\n"
            "Legacy:\n"
            "  python scripts/import_bloomberg_data.py bloomberg_template.xlsx pinnbrook"
        ),
    )
    parser.add_argument(
        "positional_input",
        nargs="?",
        help="Legacy: refreshed workbook (default bloomberg_template.xlsx)",
    )
    parser.add_argument(
        "positional_fund",
        nargs="?",
        help="Legacy: fund name for exception IDs (default 'fund')",
    )
    parser.add_argument(
        "--input",
        dest="flag_input",
        metavar="XLSX",
        help="Refreshed Bloomberg workbook (stamped mode)",
    )
    parser.add_argument(
        "--classified",
        help="Stamped classified_rows_{cik}_{period}.json",
    )
    parser.add_argument(
        "--output",
        help=(
            "Canonical market_data_{cik}_{period}.json. Derived from the "
            "classified file when omitted."
        ),
    )
    parser.add_argument(
        "--fund",
        dest="flag_fund",
        metavar="NAME",
        help="Exception-ID fund name (stamped default: registry slug)",
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    stamped = any(
        value is not None
        for value in (args.flag_input, args.classified, args.output, args.flag_fund)
    )
    try:
        with _scripts_cwd():
            if stamped:
                if args.positional_input is not None or args.positional_fund is not None:
                    raise FundBuildError(
                        "Do not mix legacy positional arguments with "
                        "--input / --classified / --output / --fund."
                    )
                if not args.flag_input or not args.classified:
                    raise FundBuildError(
                        "Stamped import requires --input and --classified. "
                        "--output is optional and is derived when omitted."
                    )
                run_stamped(
                    args.flag_input,
                    args.classified,
                    args.output,
                    args.flag_fund,
                )
            else:
                input_file = args.positional_input or DEFAULT_INPUT_FILE
                fund_name = args.positional_fund or DEFAULT_FUND_NAME
                run_legacy(input_file, fund_name)
    except FundBuildError as exc:
        _die(str(exc))


if __name__ == "__main__":
    main()
