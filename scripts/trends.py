"""
trends.py -- concentration, index-hedge-ratio, and sector-concentration
trends across multiple quarters of the same fund.

THIN ORCHESTRATION ONLY, deliberately -- no new calculation logic lives
here. For each quarter this script calls the exact same, already-tested
functions used everywhere else in this pipeline (aggregate_to_economic_
positions, compute_true_long_exposure, compute_concentration,
compute_index_hedge_ratio, compute_sector_concentration, all from
analyze.py) and assembles the per-quarter results into a time series.
If a number here is wrong, the bug is in this file's assembly, not in
math that's already been verified elsewhere -- there is no other math
to distrust.

METHODOLOGICAL LIMITATION -- named directly, not buried in a comment
nobody reads: GICS sector labels (GICS_INDUSTRY_NAME / GICS_SUB_INDUSTRY_NAME)
only exist in data/market_data.json, which is a LIVE Bloomberg pull as of
whenever it was last refreshed -- there is no historical Bloomberg
snapshot for prior quarters anywhere in this pipeline. This script
applies the CURRENT market_data.json's sector mapping uniformly to
every prior quarter's positions as well, because that's the only sector
data that exists. This is a reasonable approximation -- GICS
classification rarely changes quarter to quarter for an established
operating company -- but it is an assumption, not a fact, and it can be
wrong in specific, nameable ways:
  - a company that changed its primary line of business, or was
    reclassified by MSCI/S&P, between the prior quarter's report date
    and today
  - a position that existed in a prior quarter but has since been
    acquired, delisted, or gone private (see SKILL.md's Catalyst
    Pharmaceuticals case) has NO current market_data.json entry at
    all, and falls into compute_sector_concentration's "Unclassified"
    bucket for every quarter it appears in, not just the ones where it
    was actually unresolved
  - a CUSIP that changed (merger, reincorporation -- see SKILL.md's
    AMBIGUOUS_SECURITY_MAPPING section) would look unclassified in the
    old quarter even if the successor security is well-covered today
Sector-concentration TREND LINES this script produces should be read
as "today's sector lens applied retroactively to prior quarters' real
positions," not as an independently-verified historical record. Gross
Long, concentration, and hedge-ratio trends do NOT have this limitation
-- they depend only on each quarter's own SEC-reported values, not on
any current-day external data.

Usage: python trends.py [fund_name] [prior_quarter_paths...]
  prior_quarter_paths: 0 or more prior quarters' classified_rows.json
  paths, chronological (oldest first), NOT including the current
  quarter -- same convention as dashboard.py's trailing arguments.
Reads: data/classified_rows.json (current quarter, implicit -- same
       convention as dashboard.py and analyze.py's own __main__ block),
       data/market_data.json (current sector mapping, see limitation
       above)
Writes: data/trends_results.json
"""
import json
import sys

from analyze import (
    aggregate_to_economic_positions, compute_true_long_exposure,
    compute_concentration, compute_index_hedge_ratio, compute_sector_concentration,
)
from liquidity import load_market_data, USABLE_MARKET_DATA_STATUSES
from resolution_log import derive_quarter_label


def compute_quarter_snapshot(rows, sector_by_cusip_l3, sector_by_cusip_l4):
    """One quarter's worth of trend metrics -- every number here comes
    from calling an existing, already-tested function exactly once.
    Nothing is recomputed or re-derived from a different formula than
    the one already verified elsewhere in this pipeline."""
    positions = aggregate_to_economic_positions(rows)
    exposures = compute_true_long_exposure(positions)
    concentration = compute_concentration(exposures)
    hedge = compute_index_hedge_ratio(positions)
    sector_industry = compute_sector_concentration(exposures, sector_by_cusip_l3)
    sector_sub_industry = compute_sector_concentration(exposures, sector_by_cusip_l4)

    return {
        "quarter": derive_quarter_label(rows),
        "positionCount": len(positions),
        "grossLong": concentration["fullBookTotal"],
        "coveredBookTotal": concentration["coveredBookTotal"],
        "positionCountFullBook": concentration["positionCountFullBook"],
        "top5PctOfFullBook": concentration["top5PctOfFullBook"],
        "top10PctOfFullBook": concentration["top10PctOfFullBook"],
        "top20PctOfFullBook": concentration["top20PctOfFullBook"],
        "indexPutNotional": hedge["indexPutNotional"],
        "longBook": hedge["longBook"],
        "indexHedgeRatioPct": hedge["indexHedgeRatioPct"],
        "sectorConcentration": {
            "industry": sector_industry,
            "subIndustry": sector_sub_industry,
        },
    }


def build_sector_maps(market_data):
    """Identical dict-comprehension pattern already used in
    dashboard.py's build_dashboard_data -- duplicated here rather than
    imported because it's data reshaping to match compute_sector_
    concentration's input contract, not calculation logic. PASS or
    PASS_HUMAN_CORRECTED counts as classified (see
    liquidity.USABLE_MARKET_DATA_STATUSES); PENDING_EXTERNAL_DATA,
    REVIEW, or a CUSIP missing from market_data.json entirely all fall
    through into compute_sector_concentration's own "Unclassified"
    bucket, matching every other consumer of this data in this
    pipeline. A strict PASS-only version of this exact check shipped
    in dashboard.py first and was found excluding human-corrected GICS
    values entirely on Melqart's real data (Chart Industries'
    corrected "Machinery" classification never reached the sector
    card) -- fixed there and mirrored here so this file's standalone
    CLI path doesn't carry the same gap forward."""
    sector_by_cusip_l3 = {
        cusip: m["GICS_INDUSTRY_NAME"] for cusip, m in market_data.items()
        if m.get("GICS_INDUSTRY_NAME_status") in USABLE_MARKET_DATA_STATUSES
    }
    sector_by_cusip_l4 = {
        cusip: m["GICS_SUB_INDUSTRY_NAME"] for cusip, m in market_data.items()
        if m.get("GICS_SUB_INDUSTRY_NAME_status") in USABLE_MARKET_DATA_STATUSES
    }
    return sector_by_cusip_l3, sector_by_cusip_l4


if __name__ == "__main__":
    fund_name = sys.argv[1] if len(sys.argv) > 1 else "fund"
    prior_quarter_paths = sys.argv[2:]   # chronological, oldest first -- same convention as dashboard.py

    with open("data/classified_rows.json") as f:
        current_rows = json.load(f)
    market_data = load_market_data()
    sector_by_cusip_l3, sector_by_cusip_l4 = build_sector_maps(market_data)

    quarters_rows = [
        json.load(open(path)) for path in prior_quarter_paths
    ]
    quarters_rows.append(current_rows)   # current quarter always last -- chronological order preserved

    snapshots = [
        compute_quarter_snapshot(rows, sector_by_cusip_l3, sector_by_cusip_l4)
        for rows in quarters_rows
    ]

    print(f"Computed trends across {len(snapshots)} quarter(s) for {fund_name}: "
          f"{', '.join(s['quarter'] for s in snapshots)}")
    print(f"\nGross Long by quarter:")
    for s in snapshots:
        print(f"  {s['quarter']}: ${s['grossLong']:,d}  "
              f"(top10={s['top10PctOfFullBook']}%, indexHedge={s['indexHedgeRatioPct']}%)")

    with open("data/trends_results.json", "w") as f:
        json.dump({"fundName": fund_name, "quarters": snapshots}, f, indent=2)
    print(f"\nWrote data/trends_results.json")
    print(
        "\nNOTE: sector-concentration figures above apply CURRENT market_data.json's "
        "GICS mapping to every quarter's positions, including prior quarters this "
        "market data was never pulled for. See module docstring -- this is a stated "
        "approximation, not an independently-verified historical record."
    )
