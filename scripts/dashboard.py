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
"""
import json
import sys
from pathlib import Path

from analyze import (
    aggregate_to_economic_positions, compute_true_long_exposure,
    compute_concentration, compute_index_hedge_ratio, flag_related_security_families,
    compute_position_status, chain_position_status, compute_sector_concentration,
    get_hedge_position_detail,
)
from liquidity import (
    load_market_data, compute_liquidity, bucket_summary, discrete_bucket_summary,
    compute_liquidation_curve, days_to_reach_pct,
)
from resolution_log import derive_quarter_label

PARTICIPATION_RATES = [0.05, 0.10, 0.15, 0.20, 0.25]
POSITION_BASES = ["common", "common_plus_calls"]


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
        if not m or not m.get("PARSEKYABLE_DES") or m.get("PARSEKYABLE_DES_status") != "PASS":
            return None
        return m["PARSEKYABLE_DES"].split(" ")[0]

    positions = aggregate_to_economic_positions(classified_rows)

    exposures = compute_true_long_exposure(positions)
    concentration = compute_concentration(exposures)
    hedge = compute_index_hedge_ratio(positions)
    hedge_detail = get_hedge_position_detail(positions)
    for p in hedge_detail["indexHedgePositions"] + hedge_detail["sectorHedgePositions"]:
        p["ticker"] = ticker_from_market_data(p["cusip"])
    families = flag_related_security_families(positions)

    # Top 10 by % of full book -- distinct from "top liquidity risks"
    # (sorted by days-to-liquidate). Reuses compute_concentration's
    # already-computed, already-tested pctFullBook per position; no new
    # calculation, just a different slice of existing output.
    top10_by_book = concentration["ranked"][:10]

    # Sector concentration -- both GICS levels actually wired into the
    # real Bloomberg template (Level 3 GICS_INDUSTRY_NAME, Level 4
    # GICS_SUB_INDUSTRY_NAME; there is no Level 2/1 pull in this pipeline,
    # so the toggle is Industry/Sub-Industry, not Sector/Industry-Group).
    # Only PASS-status values count as classified -- PENDING_EXTERNAL_DATA,
    # REVIEW, or a missing CUSIP entirely all fall through the same way,
    # into compute_sector_concentration's own explicit "Unclassified"
    # bucket, matching analyze.py's own CLI reporting block exactly.
    sector_by_cusip_l3 = {
        cusip: m["GICS_INDUSTRY_NAME"] for cusip, m in market_data.items()
        if m.get("GICS_INDUSTRY_NAME_status") == "PASS"
    }
    sector_by_cusip_l4 = {
        cusip: m["GICS_SUB_INDUSTRY_NAME"] for cusip, m in market_data.items()
        if m.get("GICS_SUB_INDUSTRY_NAME_status") == "PASS"
    }
    sector_concentration = {
        "industry": compute_sector_concentration(exposures, sector_by_cusip_l3),
        "subIndustry": compute_sector_concentration(exposures, sector_by_cusip_l4),
    }

    # QoQ / multi-quarter chain -- optional, since it needs prior
    # quarters the user may not have fetched yet. Share-count based, per
    # gap #2: a value change can be pure mark-to-market, a share change
    # is the manager doing something.
    position_status_by_cusip = {}   # immediate (latest) transition only -- feeds the existing per-liquidity-record "qoq" field, unchanged shape
    chain_by_cusip = {}             # CUSIP-keyed, for joining onto liquidity records only -- see note below
    quarter_labels = []
    reentered_count = 0
    held_all_count = 0

    if prior_quarters_rows:
        quarters = [(derive_quarter_label(rows), aggregate_to_economic_positions(rows))
                    for rows in prior_quarters_rows]
        quarters.append((derive_quarter_label(classified_rows), positions))
        quarter_labels = [label for label, _ in quarters]

        chain = chain_position_status(quarters)

        # Summary counts computed from the full per-Security-ID chain,
        # NOT from chain_by_cusip below. Found by testing against a real
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
            # This dict IS still legitimately CUSIP-keyed, unlike the
            # summary counts above -- it only ever feeds a liquidity
            # record lookup (line ~141 below), and every liquidity
            # record is itself COMMON-only per CUSIP (per compute_liquidity's
            # own convention), so a CUSIP with multiple instrument classes
            # collapsing to one entry here changes nothing observable:
            # only the COMMON leg's chain data is ever actually joined
            # onto anything downstream of this dict.
            chain_by_cusip[c["cusip"]] = c
            last_t = c["transitions"][-1]
            position_status_by_cusip[c["cusip"]] = {
                "status": last_t["status"], "sharesChangePct": last_t["sharesChangePct"],
                "oldShares": last_t["oldShares"], "newShares": last_t["newShares"],
            }

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
                s = position_status_by_cusip.get(r["cusip"])
                r["qoq"] = {
                    "status": s["status"], "sharesChangePct": s["sharesChangePct"],
                    "oldShares": s["oldShares"], "newShares": s["newShares"],
                } if s else None
                # Full chain, only when 2+ total quarters were supplied
                # (chain_by_cusip is empty otherwise) -- carries the
                # signals a single "qoq" transition can't: has this
                # position been closed and reopened, has it been held
                # every quarter in the window.
                c = chain_by_cusip.get(r["cusip"])
                r["reenteredAfterClose"] = c["reenteredAfterClose"] if c else False
                r["heldAllQuarters"] = c["heldAllQuarters"] if c else None
                r["netSharesChangePct"] = c["netSharesChangePct"] if c else None
                # % of fund size -- same denominator as every other "% of
                # book" figure on this dashboard (concentration.fullBookTotal,
                # hedges excluded), not the raw SEC-reported total. Computed
                # against THIS row's own verifiedValue (common-only, exactly
                # what's displayed) rather than reusing exposures' netted
                # trueLongExposure -- a position with a call overlay would
                # otherwise show a % that doesn't match value/total using
                # the number actually printed in the same row.
                r["pctOfBook"] = (
                    round(r["verifiedValue"] / concentration["fullBookTotal"] * 100, 3)
                    if concentration["fullBookTotal"] else None
                )
                r["ticker"] = ticker_from_market_data(r["cusip"])
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
    compounding_flags = sorted(
        [r for r in default_liquidity if r["compoundingIlliquidity"]],
        key=lambda r: -(r["daysToLiquidate_20d"] or 0),
    )
    threshold_flags = [r for r in default_liquidity if r["thresholdProximityFlag"]]

    # reentered_count / held_all_count already computed above, directly
    # from the full per-Security-ID chain -- see the note there. Only
    # meaningful with 2+ total quarters (a single prior quarter can show
    # NEW/CLOSED/INCREASED/DECREASED, but reenteredAfterClose and
    # heldAllQuarters both need a real chain to mean anything -- with
    # only 2 quarters "held all quarters" is the same as "not new and
    # not closed"); both default to 0 above when prior_quarters_rows is
    # empty, matching that case correctly.

    return {
        "fundName": fund_name,
        "fullBookValue": full_book_value,
        "positionCount": len(positions),
        "exposures": sorted(exposures, key=lambda e: -e["trueLongExposure"]),
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
        "participationRates": PARTICIPATION_RATES,
        "positionBases": POSITION_BASES,
        "qoqAvailable": bool(prior_quarters_rows),
        "quarterCount": len(quarter_labels) if quarter_labels else (1 if prior_quarters_rows is not None else 0),
        "quarterLabels": quarter_labels,
        "chainAvailable": len(quarter_labels) >= 3,   # 2 prior + current, or more -- enough for reenter/held-all to mean something beyond a plain 2-quarter diff
        "reenteredCount": reentered_count,
        "heldAllQuartersCount": held_all_count,
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__FUND_NAME__ — 13F Liquidity &amp; Exposure</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
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
    data = build_dashboard_data(fund_name, classified_rows, market_data, prior_quarters_rows)

    from dashboard_render import CSS, JS
    html = (HTML_TEMPLATE
            .replace("__FUND_NAME__", fund_name)
            .replace("__CSS__", CSS)
            .replace("__DATA_JSON__", json.dumps(data))
            .replace("__JS__", JS))

    Path(output_file).write_text(html, encoding="utf-8")
    print(f"Wrote {output_file}  ({len(html):,} bytes)")
    print(f"{data['positionCount']} economic positions, "
          f"${data['fullBookValue']:,.0f} full book value")
