"""
dashboard.py -- Step 9: presentation layer only.

Every number in the rendered HTML is computed by analyze.py's and
liquidity.py's already-tested functions -- this script imports and calls
them directly, it does not recompute anything itself, and it does not read
from the *_results.json files (those are single-participation-rate
snapshots from a prior run; the dashboard needs several rates at once for
the toggle).

Participation-rate toggle: precomputed in Python at five standard rates
(5/10/15/20/25%), all embedded in the page's data blob. The browser only
ever switches which precomputed dataset is on screen -- it never
recalculates liquidity itself. This is deliberate: "nothing should be
computed for the first time inside dashboard-rendering code" (SKILL.md
data model) applies to client-side JS as much as it does to this script.
A continuous slider would need the same math ported to JS, which risks a
silent mismatch against the tested Python version; discrete precomputed
rates avoid that at the cost of only offering five fixed choices, not
"custom" yet.

Usage: python dashboard.py [fund_name] [output_file.html] [prior_quarter_paths...]
Reads:  data/classified_rows.json, data/market_data.json
Writes: <output_file.html> if given; otherwise defaults to
        dashboard_{fund_name}_{current_quarter}.html so different funds
        and different quarters of the same fund never silently collide.

Production rebuilds that must not swap those shared working files:
  python build_fund_dashboard.py --manager NAME --quarter YYYY-MM-DD
  python build_fund_dashboard.py --all
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from fund_io import read_market_meta, write_market_snapshot
from analyze import (
    aggregate_to_economic_positions, compute_true_long_exposure,
    compute_concentration, compute_index_hedge_ratio, flag_related_security_families,
    compute_position_status, chain_position_status, compute_sector_concentration,
    get_hedge_position_detail, compute_gics_l3_rotation,
    LONG_CLASSES, CALL_CLASSES, PUT_CLASSES,
)
from liquidity import (
    load_market_data, compute_liquidity, bucket_summary, discrete_bucket_summary,
    compute_liquidation_curve, days_to_reach_pct, USABLE_MARKET_DATA_STATUSES,
    ADV_ELIGIBLE_CLASSES,
)
from resolution_log import derive_quarter_label, load_all_resolutions
from trends import compute_quarter_snapshot
from integrity import summarize_integrity_status

PARTICIPATION_RATES = [0.05, 0.10, 0.15, 0.20, 0.25]
POSITION_BASES = ["common", "common_plus_calls"]

# Calendar-quarter-end month -> fiscal quarter number. Every real filing
# in this pipeline so far reports on one of these four boundaries (see
# SKILL.md's Pinnbrook filename-collision note: "most 13F filers report
# on standard calendar-quarter boundaries").
_QUARTER_END_MONTH = {"03": "Q1", "06": "Q2", "09": "Q3", "12": "Q4"}


def format_quarter_label(period_str):
    """"2026-03-31" -> "Q1 2026". Found needed by testing a prior
    quarter as the "current" one for the first time (Pinnbrook Q1 2026
    treated as data/classified_rows.json, to exercise the Sector &
    Other ETF Hedges box against real non-zero data) -- the header's
    quarter label was a literal hardcoded "Q2 2026" string in
    dashboard_render.py, never actually derived from the period being
    displayed. It happened to be correct on every real dashboard built
    before this one, purely because every fund's current quarter
    tested so far genuinely was Q2 2026 -- coincidence, not a working
    label. Falls back to the raw string unchanged for anything that
    doesn't parse as YYYY-MM-DD (e.g. derive_quarter_label's own
    "unknown_quarter" placeholder for data not sourced via
    fetch_edgar.py), rather than guessing a quarter number for it."""
    parts = (period_str or "").split("-")
    if len(parts) == 3 and parts[1] in _QUARTER_END_MONTH:
        return f"{_QUARTER_END_MONTH[parts[1]]} {parts[0]}"
    return period_str


def _normalize_issuer(name):
    n = (name or "").upper().strip()
    n = re.sub(r"[.,]", "", n)
    n = re.sub(r"\s+", " ", n)
    return n


def user_facing_exclusion_reason(reason):
    """Map liquidity.py internal exclusion reasons to analyst-facing copy.

    Does not change who is excluded or any ADV math. The liquidity module
    keeps its own CLI wording (including the module-docstring pointer);
    the dashboard never surfaces that internal note."""
    text = reason or ""
    if "option or warrant" in text or text.startswith("not ADV-modeled"):
        return "Excluded from ADV liquidity model"
    if "no market data" in text:
        return "No Bloomberg market data for this CUSIP"
    if "PX_LAST" in text:
        return "PX_LAST not verified"
    return text or "Excluded from ADV liquidity model"


def _registry_paths():
    return (
        Path("references/manager_registry.json"),
        Path("../references/manager_registry.json"),
        Path(__file__).resolve().parent.parent / "references" / "manager_registry.json",
    )


def resolve_manager_display_name(fund_name):
    """Legal/display name from the hand-verified registry. Never appends
    a hardcoded 'Capital' suffix -- that was wrong for Melqart and
    Pinnbrook. Filename slugs such as eminence_capital map to the
    registry entry's full_name so the dashboard never presents the
    internal slug when a legal name exists."""
    registry = {}
    for path in _registry_paths():
        if path.exists():
            with open(path) as f:
                registry = json.load(f)
            break
    key = (fund_name or "").lower().strip()
    if not key:
        return fund_name
    if key in registry:
        return registry[key]["full_name"]
    spaced = re.sub(r"[_]+", " ", key).strip()
    if spaced in registry:
        return registry[spaced]["full_name"]
    for k, v in registry.items():
        slug = re.sub(r"[^a-z0-9]+", "_", k).strip("_")
        if key == slug:
            return v["full_name"]
        if key and (key in k or k.startswith(key) or spaced in k or k.startswith(spaced)):
            return v["full_name"]
    return fund_name


def gics_map_from_market_data(market_data, field="GICS_INDUSTRY_NAME"):
    return {
        cusip: m[field]
        for cusip, m in market_data.items()
        if m.get(f"{field}_status") in USABLE_MARKET_DATA_STATUSES and m.get(field)
    }


def gics_for_cusip(cusip, market_data):
    m = market_data.get(cusip) or {}
    industry = (
        m.get("GICS_INDUSTRY_NAME")
        if m.get("GICS_INDUSTRY_NAME_status") in USABLE_MARKET_DATA_STATUSES
        else None
    )
    sub = (
        m.get("GICS_SUB_INDUSTRY_NAME")
        if m.get("GICS_SUB_INDUSTRY_NAME_status") in USABLE_MARKET_DATA_STATUSES
        else None
    )
    return industry, sub


def quarter_market_data_path(rows):
    if not rows:
        return None
    cik = rows[0].get("_source_cik")
    period = derive_quarter_label(rows)
    if cik in (None, "") or not period or period == "unknown_quarter":
        return None
    return Path(f"data/market_data_{cik}_{period}.json")


MARKET_STAMP_MIN_PRECISION = 0.80


class MarketDataStampMismatch(ValueError):
    """Raised when market_data.json does not belong to this filing."""


def filing_cusips_from_rows(rows):
    return {r.get("cusip") for r in (rows or []) if r.get("cusip")}


def persist_quarter_market_data(rows, market_data):
    """Write THIS quarter's own market-data pull. Used later as that
    quarter's classification snapshot -- never as a substitute for a
    different quarter's missing GICS.

    Guards against a shared working market_data.json from another fund:
    at least MARKET_STAMP_MIN_PRECISION of the market-data CUSIPs must
    appear in this filing. On success, only matching CUSIPs are written
    so leftover template rows cannot become this quarter's GICS map.
    Does not change any financial calculation."""
    path = quarter_market_data_path(rows)
    if path is None:
        return
    records = list(market_data.values()) if isinstance(market_data, dict) else list(market_data or [])
    filing_cusips = filing_cusips_from_rows(rows)
    market_cusips = {r.get("cusip") for r in records if r.get("cusip")}
    matched = filing_cusips & market_cusips
    if not market_cusips:
        raise MarketDataStampMismatch(
            f"Refusing to write {path}: market data has no CUSIPs, so it "
            f"cannot be this filing's quarter-specific snapshot "
            f"({len(filing_cusips)} filing CUSIPs)."
        )
    precision = len(matched) / len(market_cusips)
    if precision < MARKET_STAMP_MIN_PRECISION:
        raise MarketDataStampMismatch(
            f"Refusing to write {path}: only {len(matched)} of "
            f"{len(market_cusips)} market-data CUSIPs ({precision:.1%}) "
            f"appear in this filing ({len(filing_cusips)} CUSIPs). "
            f"Need {MARKET_STAMP_MIN_PRECISION:.0%} overlap so a different "
            f"fund's pull cannot overwrite this quarter's GICS snapshot. "
            f"Copy the matching market_data_{{cik}}_{{period}}.json into "
            f"data/market_data.json before rebuilding."
        )
    matched_records = [r for r in records if r.get("cusip") in matched]
    existing_meta = read_market_meta(path) if path.exists() else {}
    write_market_snapshot(path, matched_records, existing_meta)
    dropped = len(records) - len(matched_records)
    if dropped:
        print(f"Quarter market snapshot {path} wrote {len(matched_records)} "
              f"CUSIPs matching this filing; dropped {dropped} unmatched "
              f"market-data row(s).")


def load_quarter_specific_market_data(rows):
    """Load GICS/market data that belongs to this quarter's own snapshot.
    Returns {} if no snapshot exists -- does NOT fall back to the live
    current-quarter market_data.json."""
    path = quarter_market_data_path(rows)
    if path is None or not path.exists():
        return {}
    return load_market_data(str(path))


def build_qoq_buckets(statuses, common_book_total):
    by_status = defaultdict(list)
    for s in statuses:
        by_status[s["status"]].append(s)
    buckets = []
    for status in ("NEW", "INCREASED", "DECREASED", "CLOSED", "UNCHANGED"):
        items = by_status.get(status, [])
        dollar_change = sum((s["newValue"] - s["oldValue"]) for s in items)
        top = sorted(items, key=lambda s: -abs(s["newValue"] - s["oldValue"]))[:5]
        buckets.append({
            "status": status,
            "count": len(items),
            "dollarChange": dollar_change,
            "pctOfCommonBook": (
                round(dollar_change / common_book_total * 100, 2)
                if common_book_total else None
            ),
            "topNames": [
                {
                    "cusip": s["cusip"],
                    "instrumentClass": s["instrumentClass"],
                    "issuer": s["issuer"],
                    "oldValue": s["oldValue"],
                    "newValue": s["newValue"],
                    "dollarChange": s["newValue"] - s["oldValue"],
                    "sharesChangePct": s["sharesChangePct"],
                }
                for s in top
            ],
        })
    return buckets


def build_companies(positions, exposures, common_book_total, market_data, ticker_from_market_data):
    exp_by_cusip = {e["cusip"]: e for e in exposures}
    groups = defaultdict(list)
    for p in positions:
        groups[_normalize_issuer(p["nameOfIssuer"])].append(p)

    companies = []
    for key, members in groups.items():
        instruments = []
        for p in members:
            industry, sub = gics_for_cusip(p["cusip"], market_data)
            adv_modeled = p["instrumentClass"] in ADV_ELIGIBLE_CLASSES
            e = exp_by_cusip.get(p["cusip"])
            # Long-class legs share the CUSIP common-book weight
            # (commonValue / sum(commonValue)). Calls/puts are overlay,
            # not a second weight.
            pct = e.get("pctOfCommonBook") if e and p["instrumentClass"] in LONG_CLASSES else None
            instruments.append({
                "cusip": p["cusip"],
                "instrumentClass": p["instrumentClass"],
                "filedValue": p["value"],
                "shares": p["shares"],
                "ticker": ticker_from_market_data(p["cusip"]),
                "gicsIndustry": industry,
                "gicsSubIndustry": sub,
                "advModeled": adv_modeled,
                "pctOfCommonBook": pct,
                "excludedFromAdvModel": not adv_modeled,
                "isCall": p["instrumentClass"] in CALL_CLASSES,
                "isPut": p["instrumentClass"] in PUT_CLASSES,
            })
        cusips = {p["cusip"] for p in members}
        rolled = [exp_by_cusip[c] for c in cusips if c in exp_by_cusip]
        common_value = sum(e["commonValue"] for e in rolled)
        call_value = sum(e["callValue"] for e in rolled)
        put_value = sum(e["putValue"] for e in rolled)
        true_long = sum(e["trueLongExposure"] for e in rolled)
        pct_common = (
            round(common_value / common_book_total * 100, 3)
            if common_book_total and common_value else None
        )
        companies.append({
            "issuerKey": key,
            "issuer": members[0]["nameOfIssuer"],
            "instrumentCount": len(members),
            "cusips": sorted(cusips),
            "instruments": instruments,
            "commonValue": common_value,
            "callValue": call_value,
            "putValue": put_value,
            "trueLongExposure": true_long,
            "pctOfCommonBook": pct_common,
            "isCallOnly": common_value == 0 and call_value > 0,
            "optionToCommonRatioPct": (
                rolled[0]["optionToCommonRatioPct"] if len(rolled) == 1 else (
                    round(call_value / common_value * 100, 1) if common_value else None
                )
            ),
            "gicsIndustry": next((e.get("gicsIndustry") for e in rolled if e.get("gicsIndustry")), None),
        })
    companies.sort(key=lambda c: -(c["commonValue"] or 0) - (c["callValue"] or 0))
    return companies


def build_attention_inbox(liquidity, excluded, exposures, qoq_statuses, unclassified_true_long,
                          unclassified_count, integrity, common_book_total, fund_name, quarter):
    """Fixed categories, no composite score. Each item states the rule
    and the number that fired it."""
    regulatory = []
    for r in liquidity:
        flag = r.get("thresholdProximityFlag")
        if not flag:
            continue
        if flag == "WARRANT_BLOCKER_RANGE":
            rule = "Warrant-blocker proximity (4.5–5.0% of shares outstanding)"
        elif flag == "SECTION_16_PROXIMITY_RANGE":
            rule = "Section 16 proximity (9.0–9.99% of shares outstanding)"
        else:
            rule = flag
        regulatory.append({
            "cusip": r["cusip"],
            "instrumentClass": r["instrumentClass"],
            "issuer": r["issuer"],
            "ticker": r.get("ticker"),
            "rule": rule,
            "numberLabel": "% shares outstanding",
            "numberValue": r.get("pctSharesOutstanding"),
            "dollars": r.get("verifiedValue"),
        })
    regulatory.sort(key=lambda x: -(x["dollars"] or 0))

    concentrated = []
    for r in liquidity:
        if not r.get("concentratedAndIlliquid"):
            continue
        concentrated.append({
            "cusip": r["cusip"],
            "instrumentClass": r["instrumentClass"],
            "issuer": r["issuer"],
            "ticker": r.get("ticker"),
            "rule": "Concentrated and compounding-illiquid",
            "numberLabel": "days to liquidate (20d) · % SO",
            "numberValue": r.get("daysToLiquidate_20d"),
            "numberValueSecondary": r.get("pctSharesOutstanding"),
            "dollars": r.get("verifiedValue"),
        })
    concentrated.sort(key=lambda x: -(x["dollars"] or 0))

    coverage = []
    expected_adv = []
    for e in excluded:
        item = {
            "cusip": e["cusip"],
            "instrumentClass": e.get("instrumentClass"),
            "issuer": e["issuer"],
            "ticker": e.get("ticker"),
            "rule": user_facing_exclusion_reason(e.get("reason")),
            "numberLabel": "instrument",
            "numberValue": e.get("instrumentClass"),
            "dollars": e.get("filedValue"),
        }
        # Methodology exclusions (options/warrants) are not coverage gaps.
        if e.get("instrumentClass") not in ADV_ELIGIBLE_CLASSES:
            expected_adv.append(item)
        else:
            coverage.append(item)
    if unclassified_true_long:
        coverage.append({
            "cusip": None,
            "instrumentClass": None,
            "issuer": "Unclassified GICS (current quarter)",
            "ticker": None,
            "rule": "Current-quarter true-long has no usable GICS L3",
            "numberLabel": "unclassified names",
            "numberValue": unclassified_count,
            "dollars": unclassified_true_long,
        })
    if integrity and integrity.get("openReviewCount"):
        coverage.append({
            "cusip": None,
            "instrumentClass": None,
            "issuer": "Integrity open reviews",
            "ticker": None,
            "rule": "Unresolved pipeline review / correction items",
            "numberLabel": "open items",
            "numberValue": integrity["openReviewCount"],
            "dollars": None,
        })
    resolutions = load_all_resolutions()
    open_for_fund = [
        rec for rec in resolutions.values()
        if rec.get("exception_id", "").startswith(f"{fund_name}:{quarter}:")
        and rec.get("decision") == "ESCALATE"
    ]
    for rec in open_for_fund:
        coverage.append({
            "cusip": None,
            "instrumentClass": None,
            "issuer": rec["exception_id"],
            "ticker": None,
            "rule": f"ESCALATE -- {rec.get('note') or 'unresolved correction'}",
            "numberLabel": "decision",
            "numberValue": rec.get("decision"),
            "dollars": None,
        })
    coverage.sort(key=lambda x: -(x["dollars"] or 0))
    expected_adv.sort(key=lambda x: -(x["dollars"] or 0))

    moves = []
    for s in qoq_statuses:
        delta = s["newValue"] - s["oldValue"]
        if delta == 0:
            continue
        moves.append({
            "cusip": s["cusip"],
            "instrumentClass": s["instrumentClass"],
            "issuer": s["issuer"],
            "ticker": None,
            "rule": f"{s['status']} — filed-value change",
            "numberLabel": "Δ filed value",
            "numberValue": delta,
            "dollars": abs(delta),
            "status": s["status"],
        })
    moves.sort(key=lambda x: -x["dollars"])
    moves = moves[:15]

    return [
        {"id": "regulatory", "label": "Regulatory / threshold proximity", "items": regulatory},
        {"id": "concentratedIlliquid", "label": "Concentrated and illiquid", "items": concentrated},
        {"id": "coverage", "label": "Coverage gaps / unresolved corrections", "items": coverage},
        {"id": "expectedAdvExclusions", "label": "Expected ADV exclusions", "items": expected_adv,
         "countsTowardAttention": False},
        {"id": "dollarMoves", "label": "Largest dollar moves", "items": moves},
    ]


def build_dashboard_data(fund_name, classified_rows, market_data, prior_quarters_rows=None):
    """prior_quarters_rows: list of raw classified_rows lists, chronological
    (oldest first), NOT including the current quarter -- 0, 1, or several.
    A single prior quarter reduces to exactly the old two-quarter QoQ
    behavior; 2+ additionally exposes the full chain (reenteredAfterClose,
    heldAllQuarters, netSharesChangePct) via chain_position_status, which
    calls the same tested pairwise function once per consecutive pair --
    no new comparison logic for the N-quarter case, just more calls to it."""
    def ticker_from_market_data(cusip):
        """Clean ticker parsed from Bloomberg's PARSEKYABLE_DES ("NVDA US
        Equity" -> "NVDA") -- already-verified field (see SKILL.md), just
        never previously surfaced as a display ticker anywhere. None if
        the CUSIP has no market data or PARSEKYABLE_DES didn't resolve --
        shown as an em dash downstream, never guessed or left blank
        silently."""
        m = market_data.get(cusip)
        if not m or not m.get("PARSEKYABLE_DES") or m.get("PARSEKYABLE_DES_status") not in USABLE_MARKET_DATA_STATUSES:
            return None
        return m["PARSEKYABLE_DES"].split(" ")[0]

    persist_quarter_market_data(classified_rows, market_data)

    positions = aggregate_to_economic_positions(classified_rows)
    filed_value_by_sid = {(p["cusip"], p["instrumentClass"]): p["value"] for p in positions}

    exposures = compute_true_long_exposure(positions)
    common_book_total = sum(e["commonValue"] for e in exposures)
    for e in exposures:
        industry, sub = gics_for_cusip(e["cusip"], market_data)
        e["gicsIndustry"] = industry
        e["gicsSubIndustry"] = sub
        e["ticker"] = ticker_from_market_data(e["cusip"])
        e["isCallOnly"] = e["commonValue"] == 0 and e["callValue"] > 0
        e["issuerKey"] = _normalize_issuer(e.get("issuer"))
        e["pctOfCommonBook"] = (
            round(e["commonValue"] / common_book_total * 100, 3)
            if common_book_total and e["commonValue"] else None
        )
    concentration = compute_concentration(exposures)
    hedge = compute_index_hedge_ratio(positions)
    hedge_detail = get_hedge_position_detail(positions)
    for p in hedge_detail["indexHedgePositions"] + hedge_detail["sectorHedgePositions"]:
        p["ticker"] = ticker_from_market_data(p["cusip"])
        industry, sub = gics_for_cusip(p["cusip"], market_data)
        p["gicsIndustry"] = industry
        p["gicsSubIndustry"] = sub
    families = flag_related_security_families(positions)
    pct_common_by_cusip = {e["cusip"]: e["pctOfCommonBook"] for e in exposures}
    common_value_by_cusip = {e["cusip"]: e["commonValue"] for e in exposures}

    # Top 10 by % of full book -- distinct from "top liquidity risks"
    # (sorted by days-to-liquidate). Reuses compute_concentration's
    # already-computed, already-tested pctFullBook per position; no new
    # calculation, just a different slice of existing output.
    top10_by_book = concentration["ranked"][:10]

    # Sector concentration -- both GICS levels actually wired into the
    # real Bloomberg template (Level 3 GICS_INDUSTRY_NAME, Level 4
    # GICS_SUB_INDUSTRY_NAME; there is no Level 2/1 pull in this pipeline,
    # so the toggle is Industry/Sub-Industry, not Sector/Industry-Group).
    # PASS or PASS_HUMAN_CORRECTED counts as classified -- PENDING_EXTERNAL_DATA,
    # REVIEW, or a missing CUSIP entirely all fall through the same way,
    # into compute_sector_concentration's own explicit "Unclassified"
    # bucket, matching analyze.py's own CLI reporting block exactly.
    # Found excluding PASS_HUMAN_CORRECTED on Melqart's real data: Chart
    # Industries' human-corrected GICS_INDUSTRY_NAME ("Machinery") never
    # reached the sector card at all -- Unclassified's count/percentage
    # were bit-for-bit unchanged before and after the correction was
    # applied and confirmed present in market_data.json, and a coincidental
    # real "Entertainment" match (Warner Bros Discovery's own live PASS
    # data, not EA's correction) made the gap easy to miss on a first
    # look. The exact same PASS-only-excludes-corrections bug already
    # fixed in liquidity.py (USABLE_MARKET_DATA_STATUSES) was never
    # applied here -- reusing that same constant rather than a second,
    # independently-maintained status tuple.
    sector_by_cusip_l3 = gics_map_from_market_data(market_data, "GICS_INDUSTRY_NAME")
    sector_by_cusip_l4 = gics_map_from_market_data(market_data, "GICS_SUB_INDUSTRY_NAME")
    sector_concentration = {
        "industry": compute_sector_concentration(exposures, sector_by_cusip_l3),
        "subIndustry": compute_sector_concentration(exposures, sector_by_cusip_l4),
    }

    # QoQ / multi-quarter chain -- optional, since it needs prior
    # quarters the user may not have fetched yet. Share-count based, per
    # gap #2: a value change can be pure mark-to-market, a share change
    # is the manager doing something.
    position_status_by_security_id = {}   # (cusip, instrumentClass)-keyed -- see note below for why cusip-alone was wrong
    chain_by_security_id = {}             # (cusip, instrumentClass)-keyed, for joining onto liquidity records -- see note below
    quarter_labels = []
    reentered_count = 0
    held_all_count = 0
    trends_over_time = []
    last_pairwise_statuses = []
    closed_positions = []
    qoq_buckets = []
    changes_blotter = []
    gics_rotation = None

    if prior_quarters_rows:
        quarters = [(derive_quarter_label(rows), aggregate_to_economic_positions(rows))
                    for rows in prior_quarters_rows]
        quarters.append((derive_quarter_label(classified_rows), positions))
        quarter_labels = [label for label, _ in quarters]

        chain = chain_position_status(quarters)

        # Summary counts computed from the full per-Security-ID chain,
        # NOT from chain_by_security_id below. Found by testing against a real
        # options-heavy fund (Pinnbrook): chain_position_status returns
        # one record per (cusip, instrumentClass), so a CUSIP holding
        # both COMMON and CALL rows produces two chain records -- if a
        # CUSIP's COMMON leg reentered but its CALL leg didn't (or vice
        # versa), collapsing to one dict entry per CUSIP silently drops
        # whichever one iteration order overwrites, undercounting by one
        # per such disagreement. Confirmed directly on real data: 7 of
        # Pinnbrook's CUSIPs had disagreeing COMMON/CALL flags, and the
        # old cusip-collapsed computation undercounted reenteredCount by
        # 2 (16 -> 14) and heldAllQuartersCount by 1 (11 -> 10) as a
        # result. Counting from `chain` directly avoids the collision
        # entirely, since nothing is deduplicated by CUSIP here.
        reentered_count = sum(1 for c in chain if c["reenteredAfterClose"])
        held_all_count = sum(1 for c in chain if c["heldAllQuarters"])

        for c in chain:
            # Keyed by (cusip, instrumentClass) -- the actual Security ID,
            # matching what chain_position_status itself returns one
            # record per. A prior version of this dict was CUSIP-only,
            # reasoned to be safe because "every liquidity record is
            # itself COMMON-only per CUSIP" -- found wrong on real data
            # (Melqart): a CUSIP whose instrumentClass genuinely changes
            # between quarters -- here, Global X Uranium ETF (CUSIP
            # 37954Y871) classified as COMMON in Q1 2026 and SECTOR_ETF
            # in Q2 2026, after a mid-pipeline FUND_CUSIP_MAP fix was
            # added between those two classification runs -- produces
            # TWO Security IDs sharing one CUSIP: (cusip, COMMON) whose
            # last transition is CLOSED, and (cusip, SECTOR_ETF) whose
            # last transition is NEW. The CUSIP-only dict let whichever
            # one iteration processed last silently overwrite the other,
            # so the real, current SECTOR_ETF liquidity record displayed
            # the OTHER Security ID's CLOSED status instead of its own
            # NEW one. This isn't a freak one-off: a CUSIP moving from
            # FUND_UNVERIFIED to a verified class between quarters, as
            # this pipeline's own FUND_UNVERIFIED workflow explicitly
            # expects and encourages, hits the identical shape.
            key = (c["cusip"], c["instrumentClass"])
            chain_by_security_id[key] = c
            last_t = c["transitions"][-1]
            position_status_by_security_id[key] = {
                "status": last_t["status"], "sharesChangePct": last_t["sharesChangePct"],
                "oldShares": last_t["oldShares"], "newShares": last_t["newShares"],
            }

        # Trends over time -- reuses trends.py's compute_quarter_snapshot,
        # itself pure orchestration over already-tested analyze.py
        # functions (see trends.py's own docstring). Same prior_quarters_rows
        # already loaded for the chain above, plus the current quarter,
        # in the same chronological order -- no separate file, no second
        # script run required. Reuses sector_by_cusip_l3/l4, already built
        # above for the current quarter's own sector concentration card.
        last_pairwise_statuses = compute_position_status(quarters[-2][1], quarters[-1][1])
        qoq_buckets = build_qoq_buckets(last_pairwise_statuses, common_book_total)

        immediate_prior_rows = prior_quarters_rows[-1]
        prior_snapshot = load_quarter_specific_market_data(immediate_prior_rows)
        prior_gics_l3 = gics_map_from_market_data(prior_snapshot, "GICS_INDUSTRY_NAME")
        current_gics_l3 = gics_map_from_market_data(market_data, "GICS_INDUSTRY_NAME")
        prior_exposures = compute_true_long_exposure(quarters[-2][1])
        gics_rotation = compute_gics_l3_rotation(
            prior_exposures, exposures, prior_gics_l3, current_gics_l3
        )

        changes_blotter = []
        for s in last_pairwise_statuses:
            if s["status"] == "CLOSED":
                industry = prior_gics_l3.get(s["cusip"])
            else:
                industry = current_gics_l3.get(s["cusip"])
            row = {
                "cusip": s["cusip"],
                "instrumentClass": s["instrumentClass"],
                "issuer": s["issuer"],
                "ticker": ticker_from_market_data(s["cusip"]),
                "status": s["status"],
                "priorExposure": s["oldValue"],
                "currentExposure": s["newValue"],
                "dollarChange": s["newValue"] - s["oldValue"],
                "oldShares": s["oldShares"],
                "newShares": s["newShares"],
                "sharesChangePct": s["sharesChangePct"],
                "gicsIndustry": industry,
            }
            changes_blotter.append(row)
            if s["status"] == "CLOSED":
                closed_positions.append({
                    **row,
                    "currentExposure": 0,
                })

        # Trends still uses each quarter's snapshot when one exists;
        # compute_quarter_snapshot itself is unchanged. Current-quarter
        # GICS is NOT copied onto prior quarters here.
        trend_quarters_rows = list(prior_quarters_rows) + [classified_rows]
        trends_over_time = []
        for rows in trend_quarters_rows:
            snap = load_quarter_specific_market_data(rows)
            if snap:
                l3, l4 = gics_map_from_market_data(snap, "GICS_INDUSTRY_NAME"), gics_map_from_market_data(snap, "GICS_SUB_INDUSTRY_NAME")
            elif rows is classified_rows:
                l3, l4 = sector_by_cusip_l3, sector_by_cusip_l4
            else:
                l3, l4 = {}, {}
            trends_over_time.append(compute_quarter_snapshot(rows, l3, l4))

    full_book_value = sum(p["value"] for p in positions)

    # Precomputed across every (basis x rate) combination -- 2 x 5 = 10
    # full liquidity computations, all in tested Python. The browser only
    # ever switches which precomputed dataset is on screen; it never
    # recalculates liquidity itself, for either the rate or the basis
    # toggle. See module docstring for why this matters.
    by_basis = {}
    for basis in POSITION_BASES:
        by_rate = {}
        for rate in PARTICIPATION_RATES:
            liquidity_records, excluded = compute_liquidity(positions, market_data, rate, basis)
            for r in liquidity_records:
                security_id = (r["cusip"], r["instrumentClass"])
                s = position_status_by_security_id.get(security_id)
                r["qoq"] = {
                    "status": s["status"], "sharesChangePct": s["sharesChangePct"],
                    "oldShares": s["oldShares"], "newShares": s["newShares"],
                } if s else None
                # Full chain, only when 2+ total quarters were supplied
                # (chain_by_security_id is empty otherwise) -- carries the
                # signals a single "qoq" transition can't: has this
                # position been closed and reopened, has it been held
                # every quarter in the window.
                c = chain_by_security_id.get(security_id)
                r["reenteredAfterClose"] = c["reenteredAfterClose"] if c else False
                r["heldAllQuarters"] = c["heldAllQuarters"] if c else None
                r["netSharesChangePct"] = c["netSharesChangePct"] if c else None
                # Filed common-book weight -- NOT verifiedValue / true-long.
                # Numerator and denominator are filed commonValue, same as-of.
                r["pctOfCommonBook"] = pct_common_by_cusip.get(r["cusip"])
                r["filedCommonValue"] = common_value_by_cusip.get(r["cusip"])
                r["filedValue"] = filed_value_by_sid.get(security_id)
                industry, sub = gics_for_cusip(r["cusip"], market_data)
                r["gicsIndustry"] = industry
                r["gicsSubIndustry"] = sub
                r["ticker"] = ticker_from_market_data(r["cusip"])
            for e in excluded:
                e["filedValue"] = filed_value_by_sid.get((e["cusip"], e["instrumentClass"]))
                e["ticker"] = ticker_from_market_data(e["cusip"])
                industry, sub = gics_for_cusip(e["cusip"], market_data)
                e["gicsIndustry"] = industry
                e["gicsSubIndustry"] = sub
                e["excludedFromAdvModel"] = True
                e["reason"] = user_facing_exclusion_reason(e.get("reason"))
            curve_20d = compute_liquidation_curve(liquidity_records, positions, window="20d")
            curve_3m = compute_liquidation_curve(liquidity_records, positions, window="3m")
            by_rate[str(rate)] = {
                "liquidity": liquidity_records,
                "excluded": excluded,
                "bucket20d": bucket_summary(liquidity_records, "20d"),
                "bucket3m": bucket_summary(liquidity_records, "3m"),
                "discreteBucket20d": discrete_bucket_summary(liquidity_records, "20d"),
                "curve20d": curve_20d,
                "curve3m": curve_3m,
                "days50pct20d": days_to_reach_pct(curve_20d, 50),
                "days90pct20d": days_to_reach_pct(curve_20d, 90),
            }
        by_basis[basis] = by_rate

    default_basis = POSITION_BASES[0]
    default_rate = str(PARTICIPATION_RATES[2])
    default_liquidity = by_basis[default_basis][default_rate]["liquidity"]
    default_excluded = by_basis[default_basis][default_rate]["excluded"]
    compounding_flags = sorted(
        [r for r in default_liquidity if r["compoundingIlliquidity"]],
        key=lambda r: -(r["daysToLiquidate_20d"] or 0),
    )
    threshold_flags = [r for r in default_liquidity if r["thresholdProximityFlag"]]

    sc_industry = sector_concentration["industry"]
    unclassified_row = next((s for s in sc_industry["ranked"] if s["sector"] == "Unclassified"), None)
    unclassified_true_long = unclassified_row["trueLongExposure"] if unclassified_row else 0
    unclassified_count = unclassified_row["positionCount"] if unclassified_row else 0

    filing_period = derive_quarter_label(classified_rows)
    manager_display_name = resolve_manager_display_name(fund_name)
    integrity = summarize_integrity_status(classified_rows, fund_name, market_data)
    companies = build_companies(
        positions, exposures, common_book_total, market_data, ticker_from_market_data
    )
    attention_inbox = build_attention_inbox(
        default_liquidity, default_excluded, exposures, last_pairwise_statuses,
        unclassified_true_long, unclassified_count, integrity,
        common_book_total, fund_name, filing_period,
    )
    call_notional_total = sum(e["callValue"] for e in exposures)
    put_notional_total = sum(e["putValue"] for e in exposures)
    market_path = quarter_market_data_path(classified_rows)
    bloomberg_pulled_at = (
        read_market_meta(market_path).get("bloombergPulledAt")
        if market_path else None
    )

    return {
        "fundName": fund_name,
        "managerDisplayName": manager_display_name,
        "fullBookValue": full_book_value,
        "commonBookTotal": common_book_total,
        "callNotionalTotal": call_notional_total,
        "putNotionalTotal": put_notional_total,
        "positionCount": len(positions),
        "exposures": sorted(exposures, key=lambda e: -e["trueLongExposure"]),
        "companies": companies,
        "concentration": concentration,
        "top10ByBook": top10_by_book,
        "sectorConcentration": sector_concentration,
        "hedge": hedge,
        "hedgeDetail": hedge_detail,
        "families": families,
        "byBasis": by_basis,
        "defaultBasis": default_basis,
        "defaultRate": default_rate,
        "compoundingFlags": compounding_flags,
        "thresholdFlags": threshold_flags,
        "attentionInbox": attention_inbox,
        "closedPositions": closed_positions,
        "changesBlotter": changes_blotter,
        "qoqBuckets": qoq_buckets,
        "gicsRotation": gics_rotation,
        "integrity": integrity,
        "asOf": {
            "filedPeriod": filing_period,
            "filedPeriodLabel": format_quarter_label(filing_period),
            "filingDate": classified_rows[0].get("_source_filing_date") if classified_rows else None,
            "filedValueLabel": "Filed value — quarter-end",
            "verifiedValueLabel": "Verified market value — Bloomberg PX_LAST",
            "bloombergPulledAt": bloomberg_pulled_at,
        },
        "participationRates": PARTICIPATION_RATES,
        "positionBases": POSITION_BASES,
        "qoqAvailable": bool(prior_quarters_rows),
        "quarterCount": len(quarter_labels) if quarter_labels else (1 if prior_quarters_rows is not None else 0),
        "quarterLabels": quarter_labels,
        "chainAvailable": len(quarter_labels) >= 3,
        "reenteredCount": reentered_count,
        "heldAllQuartersCount": held_all_count,
        "trendsOverTime": trends_over_time,
        "trendsAvailable": len(trends_over_time) >= 2,
        "currentQuarterLabel": format_quarter_label(filing_period),
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__FUND_NAME__ — 13F Overview</title>
<style>
__CSS__
</style>
</head>
<body>
<div id="app"></div>
<script>
const DATA = __DATA_JSON__;
__JS__
</script>
</body>
</html>
"""

def write_dashboard_html(data, output_file, fund_name="fund"):
    """Wrap a precomputed payload in the existing renderer. No new math."""
    from dashboard_render import CSS, JS
    html = (HTML_TEMPLATE
            .replace("__FUND_NAME__", data.get("managerDisplayName") or fund_name)
            .replace("__CSS__", CSS)
            .replace("__DATA_JSON__", json.dumps(data))
            .replace("__JS__", JS))
    Path(output_file).write_text(html, encoding="utf-8")
    return html


def render_and_write_dashboard(fund_name, classified_rows, market_data,
                               prior_quarters_rows, output_file):
    data = build_dashboard_data(fund_name, classified_rows, market_data, prior_quarters_rows)
    html = write_dashboard_html(data, output_file, fund_name=fund_name)
    print(f"Wrote {output_file}  ({len(html):,} bytes)")
    print(f"{data['positionCount']} economic positions, "
          f"${data['fullBookValue']:,.0f} full book value")
    return data


if __name__ == "__main__":
    fund_name = sys.argv[1] if len(sys.argv) > 1 else "fund"
    explicit_output_file = sys.argv[2] if len(sys.argv) > 2 else None
    prior_quarter_paths = sys.argv[3:]   # 0, 1, or several -- chronological, oldest first, current quarter NOT included

    with open("data/classified_rows.json") as f:
        classified_rows = json.load(f)
    market_data = load_market_data()

    # Default filename includes fund + current quarter, so different
    # funds and different quarters of the same fund can never silently
    # overwrite one another -- an explicit filename (2nd argument) still
    # always wins over this default.
    if explicit_output_file:
        output_file = explicit_output_file
    else:
        current_period = derive_quarter_label(classified_rows)
        safe_fund = fund_name.lower().replace(" ", "_")
        output_file = f"dashboard_{safe_fund}_{current_period}.html"

    prior_quarters_rows = None
    if prior_quarter_paths:
        prior_quarters_rows = []
        for path in prior_quarter_paths:
            with open(path) as f:
                prior_quarters_rows.append(json.load(f))
        if len(prior_quarter_paths) == 1:
            print(f"QoQ comparison enabled against {prior_quarter_paths[0]}")
        else:
            print(f"Multi-quarter chain enabled across {len(prior_quarter_paths)} prior quarters "
                  f"(+ current = {len(prior_quarter_paths) + 1} total): {', '.join(prior_quarter_paths)}")
    else:
        print("No prior-quarter files given -- QoQ position status will show as "
              "unavailable. Pass one or more prior quarters' classified_rows.json paths, "
              "chronological (oldest first), as trailing arguments to enable it. Two or "
              "more prior quarters (three or more total) also enables reenter-after-close "
              "and held-all-quarters detection.")

    print(f"Computing across {len(PARTICIPATION_RATES)} participation rates...")
    try:
        render_and_write_dashboard(
            fund_name, classified_rows, market_data, prior_quarters_rows, output_file
        )
    except MarketDataStampMismatch as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
