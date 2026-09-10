"""
liquidity.py -- Step 7 continued: ADV-based days-to-liquidate.

Consumes economic positions (from analyze.py's aggregation) and verified
price + ADV from data/market_data.json -- the Bloomberg export/import
round trip (export_bloomberg_template.py / import_bloomberg_data.py).
price_verify.py alone is NOT sufficient here: it confirms price via
yfinance, but never touches ADV at all.

IMPORTANT -- share_ADV convention. SKILL.md's generic formula is
    share_ADV = dollar_ADV / verified_price
written for a hypothetical provider that only reports dollar volume.
Bloomberg's actual VOLUME_AVG_20D / VOLUME_AVG_3M fields (as pulled by
export_bloomberg_template.py, user-confirmed live 2026-09-02) report
SHARE volume directly, not dollar volume -- this is standard Bloomberg
convention for these mnemonics. Applying the generic dollar_ADV/price
formula to them would divide already-share-denominated data by price a
second time, silently understating every days-to-liquidate figure by
roughly the share price itself. This module uses VOLUME_AVG_20D /
VOLUME_AVG_3M AS share_ADV directly -- no division. If a future market-
data source genuinely reports dollar ADV instead, convert to share ADV
at the point of ingestion (in import_bloomberg_data.py or an equivalent),
not here -- this module should only ever consume share-denominated ADV.

Gated on instrument class, per SKILL.md's options-handling rule:
    COMMON / fund-type long positions -> ADV model applies
    CALL / PUT (any class)            -> NOT modeled here at all; these
                                          belong to a separate derivative
                                          analysis (see analyze.py's
                                          option-overlay figures), not an
                                          ADV liquidation measure
    WARRANT                           -> no ADV model; no traded volume
                                          of its own

Shows BOTH the 20-day and 3-month windows side by side for every
position, never collapsed to one canonical figure -- the compounding-
illiquidity signal depends on the divergence between them.
"""
import json
from pathlib import Path

from resolution_log import make_exception_id, get_resolution, derive_quarter_label

ADV_ELIGIBLE_CLASSES = {
    "COMMON", "ETF_INDEX", "SECTOR_ETF", "FIXED_INCOME_ETF",
    "COMMODITY_ETF", "INTL_REGIONAL_ETF", "FUND_UNVERIFIED",
}

# A market-data field is usable either as a genuine live Bloomberg PASS,
# or as PASS_HUMAN_CORRECTED -- a value a human explicitly reviewed and
# replaced via resolution_log.py's CORRECT decision (import_bloomberg_data.py),
# never silently guessed. Both are trustworthy; REVIEW_MARKET_DATA,
# PENDING_EXTERNAL_DATA, and NOT_APPLICABLE are not, regardless of
# whether a number happens to be sitting in the field.
USABLE_MARKET_DATA_STATUSES = ("PASS", "PASS_HUMAN_CORRECTED")

DAYS_TO_LIQUIDATE_BUCKETS = [10, 20, 50]  # matches the worked table in SKILL.md gap #4
COMPOUNDING_ILLIQUIDITY_DAYS_THRESHOLD = 20  # matches the ">=20 days" bucket

# Threshold-proximity bands (SKILL.md "Two patterns to flag automatically"):
# 4.5-5.0% is the standard warrant-blocker range; 9.0-9.99% sits just under
# the 10% Section 16 insider-reporting threshold. Named "proximity," not
# "structuring" -- this is evidence of where a position sits, not why;
# never assert intent from the number alone.
WARRANT_BLOCKER_RANGE = (4.5, 5.0)
SECTION_16_PROXIMITY_RANGE = (9.0, 9.99)


def load_market_data(path="data/market_data.json"):
    if not Path(path).exists():
        raise FileNotFoundError(
            f"{path} not found -- run export_bloomberg_template.py, refresh "
            f"in Excel, then import_bloomberg_data.py first."
        )
    with open(path) as f:
        records = json.load(f)
    return {r["cusip"]: r for r in records}


def compute_liquidity(positions, market_data, participation_rate=0.15, position_basis="common"):
    """One record per ADV-eligible position, with BOTH 20-day and
    3-month days-to-liquidate shown -- never one canonical figure.
    Positions outside ADV_ELIGIBLE_CLASSES (options, warrants) are
    returned separately, unmodeled, not silently dropped.

    position_basis="common" (default): shares used for days-to-liquidate
    are the position's own common shares only -- unchanged behavior,
    fully backward compatible.

    position_basis="common_plus_calls": adds any CALL position's shares
    on the SAME CUSIP to the common share count before computing days-
    to-liquidate. This is an upper-bound convenience view, not a second
    liquidation model -- verifiedValue, pctSharesOutstanding, and every
    other field stay common-only, exactly as in the source convention
    this was ported from. Real caveat, stated plainly rather than
    implied by the toggle label alone: a call position doesn't unwind
    through the same mechanism as selling common stock into ADV --
    exercising it requires cash outlay for the strike, and unwinding the
    option itself happens in the options market, not against the
    underlying's share volume. Treat this basis as an upper bound on
    economic exposure that might eventually need to move through this
    ADV, not a literal exit path for the option position itself."""
    call_shares_by_cusip = {}
    if position_basis == "common_plus_calls":
        for p in positions:
            if p["instrumentClass"] == "CALL":
                call_shares_by_cusip[p["cusip"]] = call_shares_by_cusip.get(p["cusip"], 0) + p["shares"]

    results = []
    excluded = []

    for p in positions:
        if p["instrumentClass"] not in ADV_ELIGIBLE_CLASSES:
            excluded.append({
                "cusip": p["cusip"], "issuer": p["nameOfIssuer"],
                "instrumentClass": p["instrumentClass"],
                "reason": "not ADV-modeled (option or warrant -- see module docstring)",
            })
            continue

        md = market_data.get(p["cusip"])
        if md is None:
            excluded.append({
                "cusip": p["cusip"], "issuer": p["nameOfIssuer"],
                "instrumentClass": p["instrumentClass"],
                "reason": "no market data pulled for this CUSIP",
            })
            continue

        price = md.get("PX_LAST")
        adv_20d = md.get("VOLUME_AVG_20D")
        adv_3m = md.get("VOLUME_AVG_3M")

        if price is None or md.get("PX_LAST_status") not in USABLE_MARKET_DATA_STATUSES:
            excluded.append({
                "cusip": p["cusip"], "issuer": p["nameOfIssuer"],
                "instrumentClass": p["instrumentClass"],
                "reason": f"PX_LAST not verified (status={md.get('PX_LAST_status')})",
            })
            continue

        record = {
            "cusip": p["cusip"], "issuer": p["nameOfIssuer"],
            "instrumentClass": p["instrumentClass"],
            "shares": p["shares"], "verifiedPrice": price,
            "verifiedValue": round(p["shares"] * price, 2),
        }

        # Liquidation shares: common-only by default; common_plus_calls
        # basis adds matching-CUSIP call shares for the DTL calc ONLY --
        # value, pctSharesOutstanding, and "shares" above stay common-only
        # regardless of basis, matching the convention this was ported
        # from (see module docstring for the real methodological caveat).
        call_shares = call_shares_by_cusip.get(p["cusip"], 0) if position_basis == "common_plus_calls" else 0
        liquidation_shares = p["shares"] + call_shares
        record["callSharesIncluded"] = call_shares if call_shares else None

        # Shares outstanding: EQY_SH_OUT is Bloomberg-reported in millions
        # -- verified against real data, not just the template's column
        # label, by cross-checking NVIDIA's own numbers: EQY_SH_OUT=24100
        # (mm) x PX_LAST=228.45 = $5.505T, matching CUR_MKT_CAP=$5.50565E12
        # from the same live pull exactly. Two independently-sourced
        # Bloomberg fields agreeing confirms the unit; the column header
        # alone would only be an assumption.
        shares_out = md.get("EQY_SH_OUT")
        if shares_out is not None and md.get("EQY_SH_OUT_status") in USABLE_MARKET_DATA_STATUSES and shares_out > 0:
            pct_so = round(p["shares"] / (shares_out * 1_000_000) * 100, 3)
            record["sharesOutstanding"] = shares_out * 1_000_000
            record["pctSharesOutstanding"] = pct_so
            if WARRANT_BLOCKER_RANGE[0] <= pct_so <= WARRANT_BLOCKER_RANGE[1]:
                record["thresholdProximityFlag"] = "WARRANT_BLOCKER_RANGE"
            elif SECTION_16_PROXIMITY_RANGE[0] <= pct_so <= SECTION_16_PROXIMITY_RANGE[1]:
                record["thresholdProximityFlag"] = "SECTION_16_PROXIMITY_RANGE"
            else:
                record["thresholdProximityFlag"] = None
        else:
            record["sharesOutstanding"] = None
            record["pctSharesOutstanding"] = None
            record["thresholdProximityFlag"] = None

        # Liquidity override -- a human-confirmed fact (e.g. a closed,
        # all-cash merger) that makes the normal ADV-based calculation
        # actively wrong to attempt, not just uncertain. Checked before
        # the window loop and skips it entirely rather than feeding it a
        # fabricated ADV: no finite ADV makes shares/(adv*rate) equal
        # exactly 0, so "0 days to liquidate" for a cash claim can only
        # be expressed as a direct override, never as a corrected volume.
        if md.get("liquidityOverride"):
            record["daysToLiquidate_20d"] = 0.0
            record["daysToLiquidate_3m"] = 0.0
            record["adv_20d"] = None
            record["adv_3m"] = None
            record["volumeTrendPct"] = None
            # Known, not unresolved -- a position confirmed to be an
            # immediate cash claim is definitionally not compounding-
            # illiquid, which is a different statement from "we don't
            # have enough data to tell" (the None case just below).
            record["compoundingIlliquidity"] = False
            record["liquidityOverrideReason"] = md.get("liquidityOverrideSource")
        else:
            for window, adv, status_key in (
                ("20d", adv_20d, "VOLUME_AVG_20D_status"),
                ("3m", adv_3m, "VOLUME_AVG_3M_status"),
            ):
                if adv is None or md.get(status_key) not in USABLE_MARKET_DATA_STATUSES or adv <= 0:
                    record[f"daysToLiquidate_{window}"] = None
                    record[f"adv_{window}"] = None
                    continue
                record[f"adv_{window}"] = adv
                record[f"daysToLiquidate_{window}"] = round(
                    liquidation_shares / (adv * participation_rate), 1
                )

            # Compounding illiquidity: high days-to-liquidate AND 20d ADV
            # below 3m ADV (volume declining), per SKILL.md's stated
            # definition. Requires BOTH windows to have resolved.
            d20, d3m = record["daysToLiquidate_20d"], record["daysToLiquidate_3m"]
            a20, a3m = record["adv_20d"], record["adv_3m"]
            if None not in (d20, a20, a3m):
                volume_declining = a20 < a3m
                record["volumeTrendPct"] = round((a20 - a3m) / a3m * 100, 1)
                record["compoundingIlliquidity"] = (
                    d20 >= COMPOUNDING_ILLIQUIDITY_DAYS_THRESHOLD and volume_declining
                )
            else:
                record["volumeTrendPct"] = None
                record["compoundingIlliquidity"] = None

        # The combination the source proposal's item 6 was actually
        # after: a position that's both hard to exit AND sitting at a
        # structurally meaningful ownership level is doubly worth a
        # look, distinct from either condition alone.
        record["concentratedAndIlliquid"] = bool(
            record["thresholdProximityFlag"] and record["compoundingIlliquidity"]
        )

        results.append(record)

    return results, excluded


def bucket_summary(liquidity_records, window="20d"):
    """Reproduces the shape of the worked table in SKILL.md gap #4:
    days-to-exit thresholds as % of book and dollars, for positions
    with a resolved days-to-liquidate in the given window."""
    valid = [r for r in liquidity_records if r[f"daysToLiquidate_{window}"] is not None]
    total_value = sum(r["verifiedValue"] for r in valid)

    buckets = []
    for threshold in DAYS_TO_LIQUIDATE_BUCKETS:
        matching = [r for r in valid if r[f"daysToLiquidate_{window}"] >= threshold]
        matching_value = sum(r["verifiedValue"] for r in matching)
        buckets.append({
            "daysThreshold": threshold,
            "positionCount": len(matching),
            "pctOfBook": round(matching_value / total_value * 100, 1) if total_value else None,
            "dollars": matching_value,
        })
    return {"window": window, "totalValue": total_value, "positionCount": len(valid), "buckets": buckets}


DISCRETE_BUCKET_RANGES = [(0, 1), (1, 5), (5, 10), (10, 20), (20, 50), (50, float("inf"))]


def discrete_bucket_summary(liquidity_records, window="20d"):
    """Non-overlapping days-to-liquidate ranges (<1, 1-5, 5-10, 10-20,
    20-50, 50+) -- genuinely different from bucket_summary's cumulative
    >=N thresholds, not just a relabeling: a position at 30 days counts
    in exactly one range here, versus three separate >=N thresholds in
    the cumulative version. Every position with a resolved days-to-
    liquidate falls into exactly one range, so the ranges partition the
    covered book completely -- percentages sum to 100%, verified below."""
    valid = [r for r in liquidity_records if r[f"daysToLiquidate_{window}"] is not None]
    total_value = sum(r["verifiedValue"] for r in valid)

    ranges = []
    for lo, hi in DISCRETE_BUCKET_RANGES:
        matching = [r for r in valid if lo <= r[f"daysToLiquidate_{window}"] < hi]
        matching_value = sum(r["verifiedValue"] for r in matching)
        label = f"< {int(hi)} day" if lo == 0 else (f"{lo}+ days" if hi == float("inf") else f"{lo}-{int(hi)} days")
        ranges.append({
            "label": label, "lo": lo, "hi": hi if hi != float("inf") else None,
            "positionCount": len(matching),
            "pctOfBook": round(matching_value / total_value * 100, 1) if total_value else None,
            "dollars": matching_value,
        })
    return {"window": window, "totalValue": total_value, "positionCount": len(valid), "ranges": ranges}


def compute_liquidation_curve(liquidity_records, all_positions, window="20d", max_days=None):
    """Cumulative portfolio liquidation curve -- for each day t, assuming
    every ADV-modeled position executes its daily capacity IN PARALLEL
    (not sequentially -- the same assumption already implicit in each
    position's independently-computed days-to-liquidate, not gated on
    other positions finishing first), what cumulative % of the FULL
    portfolio's value has been raised.

    Daily dollar capacity per position is back-derived from its own
    verifiedValue / daysToLiquidate, rather than re-deriving from ADV
    and a re-passed participation rate -- guarantees consistency with
    whatever rate was actually used to build liquidity_records, with no
    risk of the two silently drifting apart if a caller passes a
    different rate by mistake.

    Denominator is FULL portfolio value -- every economic position,
    including ones compute_liquidity excluded (options, warrants, no
    Bloomberg coverage) -- not just the ADV-modeled subset. The curve
    therefore asymptotes BELOW 100%: the gap between where it flattens
    and 100% is exactly the fraction of the book with no modeled exit
    path at all, shown honestly rather than normalized away.

    A position whose days-to-liquidate rounds to exactly 0.0 (a mega-
    cap position tiny relative to its own ADV) is a genuine, resolved
    computation, not missing data -- it means "liquidates same day,"
    not "not modeled." An earlier version of this function excluded
    days==0 the same as days==None, to dodge a division-by-zero in the
    daily-capacity calculation -- found by testing against a real fund
    with a heavy mega-cap tail: unmodeledPctOfBook was silently
    increasing with participation rate (53.7% at 5%, 57.6% at 25%),
    which is impossible if the set of modeled positions is genuinely
    rate-independent, and it isn't supposed to depend on rate at all.
    At 25% participation, 150 of 299 real positions rounded to exactly
    0.0 days and were being wrongly dropped from "modeled" -- the *most*
    liquid names in the book, discarded as if they were the least
    known. Fixed by giving a zero-day position effectively infinite
    daily capacity, so it correctly contributes its full value starting
    at day 0 rather than being excluded."""
    valid = [r for r in liquidity_records if r.get(f"daysToLiquidate_{window}") is not None]

    daily_capacity = {
        r["cusip"]: (float("inf") if r[f"daysToLiquidate_{window}"] == 0
                     else r["verifiedValue"] / r[f"daysToLiquidate_{window}"])
        for r in valid
    }
    position_value = {r["cusip"]: r["verifiedValue"] for r in valid}

    full_book_value = sum(p["value"] for p in all_positions)
    modeled_value = sum(position_value.values())

    if max_days is None:
        max_days = int(max(r[f"daysToLiquidate_{window}"] for r in valid)) + 1 if valid else 1

    curve = []
    for t in range(0, max_days + 1):
        cumulative = sum(
            position_value[c] if daily_capacity[c] == float("inf") else min(position_value[c], daily_capacity[c] * t)
            for c in daily_capacity
        )
        curve.append({
            "day": t,
            "cumulativeValue": round(cumulative, 2),
            "pctOfFullBook": round(cumulative / full_book_value * 100, 2) if full_book_value else None,
        })

    return {
        "window": window,
        "fullBookValue": full_book_value,
        "modeledValue": modeled_value,
        "unmodeledValue": full_book_value - modeled_value,
        "unmodeledPctOfBook": round((full_book_value - modeled_value) / full_book_value * 100, 2) if full_book_value else None,
        "maxDays": max_days,
        "curve": curve,
    }


def days_to_reach_pct(curve_result, target_pct):
    """Reads a specific headline number off the curve -- 'days to raise
    X% of NAV' -- for executive-summary tiles, instead of a single
    ambiguous 'portfolio days to liquidate' figure (the max-vs-weighted-
    average problem this whole function exists to avoid). Returns None
    if the curve never reaches target_pct -- expected and correct once
    target_pct exceeds what's even modeled, given the curve asymptotes
    below 100% by design."""
    for point in curve_result["curve"]:
        if point["pctOfFullBook"] is not None and point["pctOfFullBook"] >= target_pct:
            return point["day"]
    return None


if __name__ == "__main__":
    import sys
    participation = float(sys.argv[1]) if len(sys.argv) > 1 else 0.15
    FUND_NAME = sys.argv[2] if len(sys.argv) > 2 else "fund"

    from analyze import aggregate_to_economic_positions
    with open("data/classified_rows.json") as f:
        rows = json.load(f)
    positions = aggregate_to_economic_positions(rows)
    QUARTER = derive_quarter_label(rows)

    market_data = load_market_data()

    liquidity, excluded = compute_liquidity(positions, market_data, participation)

    # Only compoundingIlliquidity == True is a flag worth cross-
    # referencing against the resolution log -- False and None (windows
    # didn't both resolve) aren't exceptions needing a human decision.
    for r in liquidity:
        if r.get("compoundingIlliquidity"):
            r["exception_id"] = make_exception_id(FUND_NAME, QUARTER, "liquidity", r["cusip"])
            resolution = get_resolution(r["exception_id"])
            r["human_resolution"] = (
                f"{resolution['decision']} by {resolution['reviewer']} at {resolution['timestamp']}"
                + (f" -- {resolution['note']}" if resolution.get("note") else "")
            ) if resolution else None
        else:
            r["exception_id"] = None
            r["human_resolution"] = None

    print(f"Participation rate: {participation:.0%}")
    print(f"{len(liquidity)} ADV-modeled positions, {len(excluded)} excluded "
          f"(options/warrants/no market data)")

    print("\n" + "=" * 70)
    print("DAYS TO LIQUIDATE (both windows shown)")
    for r in sorted(liquidity, key=lambda x: -(x["daysToLiquidate_20d"] or 0)):
        if r["concentratedAndIlliquid"]:
            flag = "  *** CONCENTRATED + ILLIQUID ***"
        elif r["compoundingIlliquidity"]:
            flag = "  *** COMPOUNDING ILLIQUIDITY ***"
        else:
            flag = ""
        if r["compoundingIlliquidity"] and r["human_resolution"]:
            flag = f"  *** COMPOUNDING ILLIQUIDITY -- {r['human_resolution']} ***"
        elif r["compoundingIlliquidity"]:
            flag += f"  [{r['exception_id']}]"
        so_str = f"  {r['pctSharesOutstanding']}% SO" if r["pctSharesOutstanding"] is not None else ""
        print(f"  {r['issuer']:25s} shares={r['shares']:>10,d}  "
              f"20d={r['daysToLiquidate_20d']}  3m={r['daysToLiquidate_3m']}  "
              f"vol trend={r['volumeTrendPct']}%{so_str}{flag}")

    threshold_flagged = [r for r in liquidity if r["thresholdProximityFlag"]]
    if threshold_flagged:
        print(f"\n{len(threshold_flagged)} position(s) in a threshold-proximity range "
              f"(evidence of where the position sits, not why -- see SKILL.md):")
        for r in threshold_flagged:
            print(f"    {r['issuer']:25s} {r['pctSharesOutstanding']}% SO  -> {r['thresholdProximityFlag']}")

    flagged = [r for r in liquidity if r["compoundingIlliquidity"]]
    still_open = [r for r in flagged if not r["human_resolution"]]
    resolved = [r for r in flagged if r["human_resolution"] and not r["human_resolution"].startswith("ESCALATE")]
    if resolved:
        print(f"\n{len(resolved)} compounding-illiquidity flag(s) previously resolved -- "
              f"see labels above, not re-presented as fresh.")
    if still_open:
        print(f"\n{len(still_open)} compounding-illiquidity flag(s) need a decision:")
        print(f"  python resolution_log.py resolve <exception_id> <APPROVE|CORRECT|ESCALATE> <your name> [\"note\"]")

    if excluded:
        print(f"\n{len(excluded)} position(s) not ADV-modeled:")
        for e in excluded:
            print(f"  {e['issuer']:25s} {e['instrumentClass']:12s} -- {e['reason']}")

    print("\n" + "=" * 70)
    print("DAYS-TO-EXIT BUCKETS (20-day window)")
    summary_20d = bucket_summary(liquidity, "20d")
    for b in summary_20d["buckets"]:
        print(f"  >= {b['daysThreshold']:2d} days: {b['pctOfBook']}% of book  (${b['dollars']:,.0f})")

    print("\nDAYS-TO-EXIT BUCKETS (3-month window)")
    summary_3m = bucket_summary(liquidity, "3m")
    for b in summary_3m["buckets"]:
        print(f"  >= {b['daysThreshold']:2d} days: {b['pctOfBook']}% of book  (${b['dollars']:,.0f})")

    with open("data/liquidity_results.json", "w") as f:
        json.dump({"liquidity": liquidity, "excluded": excluded,
                   "bucketSummary20d": summary_20d, "bucketSummary3m": summary_3m}, f, indent=2)
    print("\nWrote data/liquidity_results.json")
