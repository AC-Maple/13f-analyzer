"""
analyze.py -- Step 7: automated portfolio analysis.

Consumes classified filing rows (raw, per-CUSIP-per-instrumentClass
rows already through integrity checks) and produces the actual
investment analytics: economic positions, true long exposure, position
status across quarters, concentration, and the index hedge ratio.

Does NOT compute liquidity (position size against ADV) -- that's
liquidity.py, deliberately separate because it needs a verified price
and ADV from price_verify.py / the Bloomberg hand-off, which this
script does not touch. Does NOT compute delta-equivalent option
exposure -- that needs an options-chain data source (strikes,
expiries, implied vol) not in scope anywhere in this pipeline; see
SKILL.md known limitations.
"""
import json
from collections import defaultdict

from resolution_log import make_exception_id, get_resolution, derive_quarter_label


# =========================================================
# Economic position aggregation
# =========================================================

def aggregate_to_economic_positions(rows):
    """Rolls raw filing line items up to economic positions, one per
    Security ID (CUSIP + instrumentClass). Sums value and shares within
    a Security ID -- this is deliberately the same aggregation check 8
    flags as an audit item but never blocks: 13F discloses no strike or
    expiry, so two option rows on the same CUSIP+class are indistinguishable
    from a duplicate, but for TOTAL exposure purposes summing them is the
    economically correct thing to do regardless of whether they're a true
    duplicate or two genuinely separate strikes. Check 8's flag exists so
    a human knows this happened, not to prevent it from happening.
    """
    groups = defaultdict(list)
    for r in rows:
        key = (r["cusip"], r["instrumentClass"])
        groups[key].append(r)

    positions = []
    for (cusip, instrument_class), group in groups.items():
        total_value = sum(r["value"] for r in group if r["value"] is not None)
        total_shares = sum(r["sshPrnamt"] for r in group if r["sshPrnamt"] is not None)
        positions.append({
            "cusip": cusip,
            "instrumentClass": instrument_class,
            "nameOfIssuer": group[0]["nameOfIssuer"],
            "value": total_value,
            "shares": total_shares,
            "row_count": len(group),
            "raw_row_numbers": [r["raw_row_number"] for r in group],
        })
    return positions


# =========================================================
# True long exposure -- re-aggregates ACROSS instrumentClass,
# back up to CUSIP level, deliberately undoing the Security ID split
# that check 5/8 depend on. Two different aggregation levels serving
# two different purposes; do not conflate them.
# =========================================================

LONG_CLASSES = {
    "COMMON", "ETF_INDEX", "SECTOR_ETF", "FIXED_INCOME_ETF",
    "COMMODITY_ETF", "INTL_REGIONAL_ETF", "FUND_UNVERIFIED", "WARRANT",
}
CALL_CLASSES = {c for c in (
    "CALL", "ETF_INDEX_CALL", "SECTOR_ETF_CALL", "FIXED_INCOME_ETF_CALL",
    "COMMODITY_ETF_CALL", "INTL_REGIONAL_ETF_CALL", "FUND_UNVERIFIED_CALL",
)}
PUT_CLASSES = {c for c in (
    "PUT", "ETF_INDEX_PUT", "SECTOR_ETF_PUT", "FIXED_INCOME_ETF_PUT",
    "COMMODITY_ETF_PUT", "INTL_REGIONAL_ETF_PUT", "FUND_UNVERIFIED_PUT",
)}


def compute_true_long_exposure(positions):
    """Per CUSIP: common/fund value + call notional - put notional.
    This is gap #1's headline number -- verified against Armistice
    Q1 2026 Cytokinetics: common $50,390,700 + calls $56,023,500 x2
    - put $13,182,000 = $149,255,700, matching the $149.3M figure
    cited throughout SKILL.md.

    Returns one record per CUSIP with the full breakdown, not just the
    final number -- so a person can see exactly what fed the exposure
    figure, per the provenance principle (SKILL.md data model)."""
    by_cusip = defaultdict(lambda: {"common": 0, "call": 0, "put": 0, "issuer": None})
    for p in positions:
        entry = by_cusip[p["cusip"]]
        entry["issuer"] = p["nameOfIssuer"]
        if p["instrumentClass"] in LONG_CLASSES:
            entry["common"] += p["value"]
        elif p["instrumentClass"] in CALL_CLASSES:
            entry["call"] += p["value"]
        elif p["instrumentClass"] in PUT_CLASSES:
            entry["put"] += p["value"]
        # OTHER falls through uncounted -- never silently folded into a bucket

    results = []
    for cusip, entry in by_cusip.items():
        true_long = entry["common"] + entry["call"] - entry["put"]
        option_ratio = (entry["call"] / entry["common"] * 100) if entry["common"] else None
        results.append({
            "cusip": cusip, "issuer": entry["issuer"],
            "commonValue": entry["common"], "callValue": entry["call"],
            "putValue": entry["put"], "trueLongExposure": true_long,
            "optionToCommonRatioPct": round(option_ratio, 1) if option_ratio is not None else None,
        })
    return results


def flag_related_security_families(positions):
    """Flags cases where a fund holds MULTIPLE DIFFERENT CUSIPs that are
    very likely the same underlying company -- e.g. a SPAC's unit,
    warrant, and separated common stock, each with its own CUSIP.

    This is deliberately NOT the same problem as compute_true_long_exposure
    (which combines common/call/put rows sharing ONE CUSIP -- the
    ordinary case). Different CUSIPs for the same company (SPAC families,
    and in general anywhere a corporate action splits one security into
    several tradeable pieces) need an external reference dataset to
    reliably link and combine into one economic-exposure number --
    that's a real, separate, licensed-data dependency, not built here.

    What IS achievable without that dependency: nameOfIssuer is already
    present on every row, and -- verified against a real case -- GS
    Acquisition Holdings Corp's unit, warrant, and Class A common all
    carry the IDENTICAL issuer string across three different CUSIPs
    within the same filing. Grouping by normalized issuer name and
    flagging any group spanning more than one CUSIP gives a fund
    manager exactly "this SPAC/warrant is the same company as this
    equity position" without pretending to compute a blended exposure
    figure this pipeline doesn't have the data to compute correctly.

    Deliberately conservative: light normalization only (uppercase,
    strip trailing corporate-suffix punctuation noise), no fuzzy
    matching. A missed family (false negative) is a minor loss; wrongly
    grouping two unrelated companies with similar names (false
    positive) actively misleads, so this errs toward under-flagging."""
    import re

    def normalize_issuer(name):
        n = name.upper().strip()
        n = re.sub(r"[.,]", "", n)          # strip periods/commas only
        n = re.sub(r"\s+", " ", n)           # collapse whitespace
        return n

    by_name = {}
    for p in positions:
        key = normalize_issuer(p["nameOfIssuer"])
        by_name.setdefault(key, []).append(p)

    families = []
    for name, group in by_name.items():
        distinct_cusips = {p["cusip"] for p in group}
        if len(distinct_cusips) > 1:
            families.append({
                "issuerNameNormalized": name,
                "cusipCount": len(distinct_cusips),
                "members": [
                    {"cusip": p["cusip"], "instrumentClass": p["instrumentClass"],
                     "value": p["value"], "shares": p["shares"]}
                    for p in group
                ],
                "note": ("Multiple CUSIPs share this issuer name -- likely the same "
                         "underlying company (e.g. a SPAC's unit/warrant/common, or a "
                         "convertible bond alongside the issuer's equity). Review "
                         "together; NOT combined into one exposure figure -- that would "
                         "need external reference data this pipeline doesn't have."),
            })
    return families


# =========================================================
# Position status -- share-count based, never value-based (gap #2)
# =========================================================

def compute_position_status(old_positions, new_positions):
    """Security-ID-keyed (cusip, instrumentClass) NEW/CLOSED/INCREASED/
    DECREASED/UNCHANGED, computed from share count. Value deltas are
    reported alongside for context but never drive the classification --
    a value change can be pure mark-to-market; a share change is the
    manager doing something."""
    old_by_key = {(p["cusip"], p["instrumentClass"]): p for p in old_positions}
    new_by_key = {(p["cusip"], p["instrumentClass"]): p for p in new_positions}
    all_keys = set(old_by_key) | set(new_by_key)

    results = []
    for key in all_keys:
        old_p, new_p = old_by_key.get(key), new_by_key.get(key)
        cusip, instrument_class = key

        if old_p is None:
            status = "NEW"
            old_shares, old_value = 0, 0
            new_shares, new_value = new_p["shares"], new_p["value"]
            issuer = new_p["nameOfIssuer"]
        elif new_p is None:
            status = "CLOSED"
            old_shares, old_value = old_p["shares"], old_p["value"]
            new_shares, new_value = 0, 0
            issuer = old_p["nameOfIssuer"]
        else:
            old_shares, old_value = old_p["shares"], old_p["value"]
            new_shares, new_value = new_p["shares"], new_p["value"]
            issuer = new_p["nameOfIssuer"]
            if new_shares == old_shares:
                status = "UNCHANGED"
            elif new_shares > old_shares:
                status = "INCREASED"
            else:
                status = "DECREASED"

        shares_change_pct = (
            round((new_shares - old_shares) / old_shares * 100, 2)
            if old_shares else None
        )
        value_change_pct = (
            round((new_value - old_value) / old_value * 100, 2)
            if old_value else None
        )

        results.append({
            "cusip": cusip, "instrumentClass": instrument_class, "issuer": issuer,
            "status": status,
            "oldShares": old_shares, "newShares": new_shares,
            "sharesChangePct": shares_change_pct,
            "oldValue": old_value, "newValue": new_value,
            "valueChangePct": value_change_pct,
        })
    return results


def chain_position_status(positions_by_quarter):
    """Chains compute_position_status across every consecutive quarter
    pair -- N-1 calls to the exact same, already-tested per-pair logic
    for N quarters, not a new comparison algorithm. A single two-quarter
    diff can't distinguish "held flat for 3 quarters" from "sold in Q2,
    rebought in Q4" -- both look like isolated snapshots without the
    full chain.

    positions_by_quarter: list of (quarter_label, positions) tuples, in
    chronological order (oldest first), at least 2 entries. positions
    is whatever aggregate_to_economic_positions returns for that quarter.

    Returns one record per Security ID (cusip, instrumentClass) that
    appears in ANY quarter, with:
      - transitions: the full list of pairwise status changes, in order
      - everClosed: CLOSED appeared at some point in the chain
      - reenteredAfterClose: CLOSED appears, then NEW appears in a LATER
        transition for the same Security ID -- the genuinely new signal
        no single pairwise comparison can see. A plain NEW with no prior
        CLOSED does not set this; only found by testing that a position
        NEW only once (never previously closed within the window) is
        correctly left False.
      - heldAllQuarters: present with a real share count in every
        quarter in the window, never NEW or CLOSED within it
      - netSharesChangePct: first-quarter-in-window to last-quarter-in-
        window share change. None if the position didn't exist yet in
        the first quarter (no baseline to measure from), matching
        compute_position_status's own convention for a zero base."""
    if len(positions_by_quarter) < 2:
        raise ValueError("chain_position_status needs at least 2 quarters")

    transitions_by_key = defaultdict(list)
    all_keys = set()

    for i in range(len(positions_by_quarter) - 1):
        old_label, old_positions = positions_by_quarter[i]
        new_label, new_positions = positions_by_quarter[i + 1]
        statuses = compute_position_status(old_positions, new_positions)
        for s in statuses:
            key = (s["cusip"], s["instrumentClass"])
            all_keys.add(key)
            transitions_by_key[key].append({
                "fromQuarter": old_label, "toQuarter": new_label,
                "status": s["status"], "sharesChangePct": s["sharesChangePct"],
                "oldShares": s["oldShares"], "newShares": s["newShares"],
                "issuer": s["issuer"],
            })

    results = []
    for key in all_keys:
        transitions = transitions_by_key[key]
        statuses_seq = [t["status"] for t in transitions]

        reentered = False
        seen_closed = False
        for st in statuses_seq:
            if st == "CLOSED":
                seen_closed = True
            elif st == "NEW" and seen_closed:
                reentered = True

        first_shares = transitions[0]["oldShares"]
        last_shares = transitions[-1]["newShares"]
        net_change_pct = round((last_shares - first_shares) / first_shares * 100, 2) if first_shares else None

        results.append({
            "cusip": key[0], "instrumentClass": key[1],
            "issuer": transitions[-1]["issuer"],
            "transitions": transitions,
            "everClosed": "CLOSED" in statuses_seq,
            "reenteredAfterClose": reentered,
            "heldAllQuarters": all(st in ("UNCHANGED", "INCREASED", "DECREASED") for st in statuses_seq),
            "netSharesChangePct": net_change_pct,
        })
    return results


# =========================================================
# Concentration -- full book vs covered book, always labeled separately
# =========================================================

def compute_concentration(true_long_exposures, covered_threshold=10_000_000):
    """Ranked by true long exposure per CUSIP (not raw reported value,
    not common-only) -- the economically meaningful figure per gap #1.
    This is a stated design choice, not the only valid one: a risk desk
    might instead want this ranked on common-only exposure. Flagged here
    so it's an explicit convention, not an implicit accident.

    EXCLUDES pure hedges (commonValue == 0 AND callValue == 0 -- a CUSIP
    that appears ONLY as a put, e.g. an index or sector hedge) from the
    long-book ranking entirely. Caught by testing: SPY and IWM, with no
    common position, compute a large NEGATIVE "true long exposure"
    (0 - put value) -- summing that into "full book total" alongside
    real holdings drags the total negative and produces nonsensical
    percentages. This is exactly what gap #3 warns against ("never let
    index puts enter portfolio longs"); it applies here as much as it
    does to the index-hedge-ratio calc. Pure hedges are reported
    separately, not silently dropped.

    Returns full-book and covered-book percentages SEPARATELY and
    labeled -- SKILL.md step 7 is explicit that a bare "% Bk" column is
    misleading once positions are filtered for detailed work."""
    long_positions = [e for e in true_long_exposures
                       if e["commonValue"] > 0 or e["callValue"] > 0]
    pure_hedges = [e for e in true_long_exposures
                   if e["commonValue"] == 0 and e["callValue"] == 0 and e["putValue"] > 0]

    full_book_total = sum(e["trueLongExposure"] for e in long_positions)
    covered = [e for e in long_positions if e["trueLongExposure"] >= covered_threshold]
    covered_book_total = sum(e["trueLongExposure"] for e in covered)

    ranked = sorted(long_positions, key=lambda e: -e["trueLongExposure"])
    for e in ranked:
        e["pctFullBook"] = round(e["trueLongExposure"] / full_book_total * 100, 3) if full_book_total else None
        e["pctCoveredBook"] = (
            round(e["trueLongExposure"] / covered_book_total * 100, 3)
            if covered_book_total and e["trueLongExposure"] >= covered_threshold else None
        )

    def top_n_pct(n):
        top = ranked[:n]
        return round(sum(e["trueLongExposure"] for e in top) / full_book_total * 100, 2) if full_book_total else None

    return {
        "fullBookTotal": full_book_total,
        "coveredBookTotal": covered_book_total,
        "coveredThreshold": covered_threshold,
        "positionCountFullBook": len(long_positions),
        "positionCountCoveredBook": len(covered),
        "top5PctOfFullBook": top_n_pct(5),
        "top10PctOfFullBook": top_n_pct(10),
        "top20PctOfFullBook": top_n_pct(20),
        "ranked": ranked,
        "pureHedgesExcluded": pure_hedges,
    }


UNCLASSIFIED_SECTOR = "Unclassified"


def compute_sector_concentration(true_long_exposures, sector_by_cusip):
    """Same shape as compute_concentration, one level up: groups true
    long exposure by sector instead of by individual position. Which
    GICS field counts as "sector" is the CALLER's choice, not this
    function's -- pass a CUSIP -> sector-name dict built from whichever
    of GICS_INDUSTRY_NAME / GICS_SUB_INDUSTRY_NAME (or any other
    sector-shaped field) is wanted. This mirrors compute_concentration's
    own stated-design-choice pattern (ranked on true long exposure, not
    common-only) rather than hard-coding one GICS granularity as
    "correct" -- sub-industry fragments into many single-position
    buckets, industry groups more coarsely; both are legitimate views.

    EXCLUDES pure hedges the same way and for the same reason as
    compute_concentration: a CUSIP with commonValue == 0 and
    callValue == 0 (put-only, e.g. an index or sector-ETF hedge) would
    contribute a negative trueLongExposure to whatever sector bucket
    its underlying happens to classify into, corrupting that sector's
    total the same way it would corrupt the full-book total. Excluded
    from every sector bucket, not just dropped from the ranking.

    fullBookTotal is computed here with the IDENTICAL filter
    compute_concentration uses (commonValue > 0 or callValue > 0,
    summed trueLongExposure) rather than accepting it as a parameter --
    given the same true_long_exposures input, a pure function recomputes
    the identical number every time, so this is redundant-but-guaranteed
    consistency, not two independently-maintained totals that could
    silently drift apart from each other.

    A position whose CUSIP has no entry in sector_by_cusip (Bloomberg
    hasn't been pulled yet, GICS_INDUSTRY_NAME came back
    PENDING_EXTERNAL_DATA/REVIEW, or the CUSIP is genuinely missing from
    the map) lands in the explicit "Unclassified" bucket -- never
    dropped silently, per SKILL.md's human-review-exceptions-not-data
    principle. A dashboard showing sector concentration with no
    Unclassified bucket at all, on a real filing that hasn't had 100%
    of its Bloomberg GICS fields resolved, would be hiding coverage
    gaps rather than surfacing them."""
    long_positions = [e for e in true_long_exposures
                       if e["commonValue"] > 0 or e["callValue"] > 0]
    full_book_total = sum(e["trueLongExposure"] for e in long_positions)

    by_sector = defaultdict(lambda: {"trueLongExposure": 0, "positionCount": 0})
    for e in long_positions:
        sector = sector_by_cusip.get(e["cusip"]) or UNCLASSIFIED_SECTOR
        bucket = by_sector[sector]
        bucket["trueLongExposure"] += e["trueLongExposure"]
        bucket["positionCount"] += 1

    ranked = [
        {
            "sector": sector,
            "trueLongExposure": bucket["trueLongExposure"],
            "pctFullBook": round(bucket["trueLongExposure"] / full_book_total * 100, 3) if full_book_total else None,
            "positionCount": bucket["positionCount"],
        }
        for sector, bucket in by_sector.items()
    ]
    ranked.sort(key=lambda r: -r["trueLongExposure"])

    return {
        "fullBookTotal": full_book_total,
        "sectorCount": len(ranked),
        "ranked": ranked,
    }


# =========================================================
# Index hedge ratio -- ONLY broad-index puts, never sector/fixed-income
# =========================================================

def compute_index_hedge_ratio(positions):
    """(SPY/IWM-class put notional) / long book. Long book here =
    common + call value across all classes (single-name puts are NOT
    subtracted for this ratio -- it's a hedge-vs-gross-long measure,
    not the true-long-exposure figure above). Sector, fixed-income, and
    commodity fund puts are deliberately excluded from the numerator --
    only ETF_INDEX_PUT counts, per gap #3."""
    index_put_value = sum(p["value"] for p in positions if p["instrumentClass"] == "ETF_INDEX_PUT")
    long_book = sum(
        p["value"] for p in positions
        if p["instrumentClass"] in LONG_CLASSES or p["instrumentClass"] in CALL_CLASSES
    )
    ratio_pct = round(index_put_value / long_book * 100, 1) if long_book else None
    return {
        "indexPutNotional": index_put_value,
        "longBook": long_book,
        "indexHedgeRatioPct": ratio_pct,
    }


NON_BROAD_INDEX_PUT_CLASSES = {
    "SECTOR_ETF_PUT": "Sector",
    "FIXED_INCOME_ETF_PUT": "Fixed Income",
    "COMMODITY_ETF_PUT": "Commodity",
    "INTL_REGIONAL_ETF_PUT": "International/Regional",
}


GICS_ROTATION_COVERAGE_THRESHOLD = 0.80


def compute_gics_l3_rotation(prior_exposures, current_exposures,
                             prior_gics_by_cusip, current_gics_by_cusip):
    """GICS Level 3 industry rotation on true-long exposure.

    Uses quarter-specific classification maps. Never apply the current
    quarter's GICS map to a prior-quarter holding (and never the reverse).

    Inclusion rules:
      CONTINUING (held both quarters) -- usable L3 in EACH respective map
      NEW (current only)              -- usable current-quarter L3
      CLOSED (prior only)             -- usable prior-quarter L3
    Anything else is excluded from the industry ranking; its true-long
    exposure is the reconciliation remainder, not a fake Unclassified
    industry.

    Missing economic exposure (a name not held that quarter) is zero.
    Missing classification is not treated as zero -- it is excluded.

    Does not call or modify compute_sector_concentration.
    """
    prior_long = [e for e in prior_exposures
                  if e["commonValue"] > 0 or e["callValue"] > 0]
    current_long = [e for e in current_exposures
                    if e["commonValue"] > 0 or e["callValue"] > 0]
    prior_by_cusip = {e["cusip"]: e for e in prior_long}
    current_by_cusip = {e["cusip"]: e for e in current_long}
    prior_total = sum(e["trueLongExposure"] for e in prior_long)
    current_total = sum(e["trueLongExposure"] for e in current_long)

    included_prior = 0
    included_current = 0
    excluded_prior = 0
    excluded_current = 0
    industry_prior = defaultdict(float)
    industry_current = defaultdict(float)
    current_cusips = defaultdict(list)
    closed_cusips = defaultdict(list)
    new_cusips = defaultdict(list)
    continuing_cusips = defaultdict(list)

    for cusip in set(prior_by_cusip) | set(current_by_cusip):
        prior_e = prior_by_cusip.get(cusip)
        current_e = current_by_cusip.get(cusip)
        prior_gics = prior_gics_by_cusip.get(cusip) if prior_e else None
        current_gics = current_gics_by_cusip.get(cusip) if current_e else None

        if prior_e and current_e:
            if prior_gics and current_gics:
                industry_prior[prior_gics] += prior_e["trueLongExposure"]
                industry_current[current_gics] += current_e["trueLongExposure"]
                included_prior += prior_e["trueLongExposure"]
                included_current += current_e["trueLongExposure"]
                continuing_cusips[current_gics].append(cusip)
                if prior_gics != current_gics:
                    continuing_cusips[prior_gics].append(cusip)
                current_cusips[current_gics].append(cusip)
            else:
                excluded_prior += prior_e["trueLongExposure"]
                excluded_current += current_e["trueLongExposure"]
        elif current_e and not prior_e:
            if current_gics:
                industry_current[current_gics] += current_e["trueLongExposure"]
                included_current += current_e["trueLongExposure"]
                new_cusips[current_gics].append(cusip)
                current_cusips[current_gics].append(cusip)
            else:
                excluded_current += current_e["trueLongExposure"]
        else:
            if prior_gics:
                industry_prior[prior_gics] += prior_e["trueLongExposure"]
                included_prior += prior_e["trueLongExposure"]
                closed_cusips[prior_gics].append(cusip)
            else:
                excluded_prior += prior_e["trueLongExposure"]

    prior_coverage = (included_prior / prior_total) if prior_total else 0.0
    current_coverage = (included_current / current_total) if current_total else 0.0
    available = (
        prior_coverage >= GICS_ROTATION_COVERAGE_THRESHOLD
        and current_coverage >= GICS_ROTATION_COVERAGE_THRESHOLD
    )

    industries = set(industry_prior) | set(industry_current)
    ranked = []
    for sector in industries:
        prior_tl = industry_prior[sector]
        current_tl = industry_current[sector]
        ranked.append({
            "sector": sector,
            "priorTrueLong": prior_tl,
            "currentTrueLong": current_tl,
            "deltaTrueLong": current_tl - prior_tl,
            "currentCusips": sorted(set(current_cusips[sector])),
            "closedCusips": sorted(set(closed_cusips[sector])),
            "newCusips": sorted(set(new_cusips[sector])),
            "continuingCusips": sorted(set(continuing_cusips[sector])),
        })
    ranked.sort(key=lambda r: -abs(r["deltaTrueLong"]))

    return {
        "available": available,
        "coverageThreshold": GICS_ROTATION_COVERAGE_THRESHOLD,
        "priorCoveragePct": round(prior_coverage * 100, 1),
        "currentCoveragePct": round(current_coverage * 100, 1),
        "priorTrueLongTotal": prior_total,
        "currentTrueLongTotal": current_total,
        "excludedPriorTrueLong": excluded_prior,
        "excludedCurrentTrueLong": excluded_current,
        "ranked": ranked if available else [],
    }


def get_hedge_position_detail(positions):
    """Per-position breakdown behind the two hedge-ratio aggregates --
    compute_index_hedge_ratio above only ever returns a single summed
    dollar figure, with no way to see which specific tickers make it up.
    Deliberately a separate function rather than a change to the one
    above: that function is already tested and used for the headline
    ratio calculation, and this one only ever feeds display, so keeping
    them apart means a display change can't risk the ratio math.

    Returns broad-market index puts (ETF_INDEX_PUT -- the ones that DO
    count toward compute_index_hedge_ratio's numerator) and, separately,
    every non-broad-index ETF put class that function deliberately
    excludes (sector, fixed-income, commodity, international/regional --
    see NON_BROAD_INDEX_PUT_CLASSES). Both were found to matter in
    practice, not just in theory: a real fund's book (Pinnbrook) carried
    a meaningfully-sized sector ETF put (SMH) AND a fixed-income ETF put
    (BKLN) simultaneously -- grouping only "sector" and leaving fixed-
    income/commodity/international invisible would have hidden exactly
    the kind of position this was built to catch. No ticker here --
    tickers come from Bloomberg's PARSEKYABLE_DES in market_data.json,
    which this function's caller (analyze.py) doesn't have; dashboard.py
    joins that on afterward, the same layering already used everywhere
    else in this pipeline (position logic here, market-data joins there)."""
    index_positions = [
        {"cusip": p["cusip"], "issuer": p["nameOfIssuer"], "value": p["value"]}
        for p in positions if p["instrumentClass"] == "ETF_INDEX_PUT"
    ]
    sector_positions = [
        {"cusip": p["cusip"], "issuer": p["nameOfIssuer"], "value": p["value"],
         "category": NON_BROAD_INDEX_PUT_CLASSES[p["instrumentClass"]]}
        for p in positions if p["instrumentClass"] in NON_BROAD_INDEX_PUT_CLASSES
    ]
    return {
        "indexHedgePositions": sorted(index_positions, key=lambda x: -x["value"]),
        "sectorHedgePositions": sorted(sector_positions, key=lambda x: -x["value"]),
        "sectorHedgeTotal": sum(p["value"] for p in sector_positions),
    }


if __name__ == "__main__":
    import sys

    with open("data/classified_rows.json") as f:
        rows = json.load(f)

    # FUND_NAME is an optional 3rd positional arg -- python analyze.py
    # [old_path] [new_path] [fund_name] -- so the existing tested 2-arg
    # quarter-comparison invocation keeps working exactly as before.
    FUND_NAME = sys.argv[3] if len(sys.argv) > 3 else "fund"
    QUARTER = derive_quarter_label(rows)

    positions = aggregate_to_economic_positions(rows)
    print(f"Aggregated {len(rows)} raw rows -> {len(positions)} economic positions "
          f"(Security ID = CUSIP + instrumentClass)")

    print("\n" + "=" * 70)
    print("TRUE LONG EXPOSURE (per CUSIP: common + calls - puts)")
    exposures = compute_true_long_exposure(positions)
    for e in sorted(exposures, key=lambda x: -x["trueLongExposure"]):
        ratio = f"  calls={e['optionToCommonRatioPct']}% of common" if e["optionToCommonRatioPct"] else ""
        print(f"  {e['issuer']:30s} common=${e['commonValue']:>14,d}  "
              f"calls=${e['callValue']:>12,d}  puts=${e['putValue']:>12,d}  "
              f"-> trueLong=${e['trueLongExposure']:>14,d}{ratio}")

    print("\n" + "=" * 70)
    print("CONCENTRATION (long book only -- pure hedges excluded, see below)")
    conc = compute_concentration(exposures)
    print(f"  Full book total:    ${conc['fullBookTotal']:,d}  ({conc['positionCountFullBook']} positions)")
    print(f"  Covered book total: ${conc['coveredBookTotal']:,d}  "
          f"({conc['positionCountCoveredBook']} positions >= ${conc['coveredThreshold']:,d})")
    print(f"  Top 5 / 10 / 20 as % of FULL book: "
          f"{conc['top5PctOfFullBook']}% / {conc['top10PctOfFullBook']}% / {conc['top20PctOfFullBook']}%")
    if conc["pureHedgesExcluded"]:
        print(f"\n  {len(conc['pureHedgesExcluded'])} pure hedge(s) excluded from concentration "
              f"(no common/call position -- put-only, e.g. index/sector hedges):")
        for h in conc["pureHedgesExcluded"]:
            print(f"    {h['issuer']:30s} put=${h['putValue']:,d}")

    print("\n" + "=" * 70)
    print("SECTOR CONCENTRATION (GICS_INDUSTRY_NAME, from data/market_data.json)")
    # Sector data is a Bloomberg hand-off product (export_bloomberg_template.py
    # / import_bloomberg_data.py), not something classify_securities.py ever
    # produces -- so it's loaded here, separately from classified_rows.json,
    # and only where GICS_INDUSTRY_NAME actually came back PASS. A CUSIP
    # that's PENDING_EXTERNAL_DATA/REVIEW_MARKET_DATA/missing from the file
    # entirely all fall through the same way, into compute_sector_concentration's
    # "Unclassified" bucket -- not three different silent-drop paths.
    try:
        with open("data/market_data.json") as f:
            market_data = json.load(f)
        sector_by_cusip = {
            m["cusip"]: m["GICS_INDUSTRY_NAME"]
            for m in market_data
            if m.get("GICS_INDUSTRY_NAME_status") == "PASS"
        }
    except FileNotFoundError:
        sector_by_cusip = {}
    sector_conc = compute_sector_concentration(exposures, sector_by_cusip)
    if not sector_by_cusip:
        print("  No GICS_INDUSTRY_NAME data available yet (data/market_data.json "
              "missing or not refreshed) -- everything falls into Unclassified.")
    print(f"  Full book total: ${sector_conc['fullBookTotal']:,d}  ({sector_conc['sectorCount']} sectors)")
    for s in sector_conc["ranked"]:
        print(f"    {s['sector']:30s} ${s['trueLongExposure']:>14,d}  "
              f"{s['pctFullBook']}% of full book  ({s['positionCount']} positions)")

    print("\n" + "=" * 70)
    print("INDEX HEDGE RATIO")
    hedge = compute_index_hedge_ratio(positions)
    print(f"  Index put notional: ${hedge['indexPutNotional']:,d}")
    print(f"  Long book:          ${hedge['longBook']:,d}")
    print(f"  Index hedge ratio:  {hedge['indexHedgeRatioPct']}%")

    print("\n" + "=" * 70)
    print("RELATED SECURITY FAMILIES (same issuer name, different CUSIPs)")
    families = flag_related_security_families(positions)
    for fam in families:
        fam["exception_id"] = make_exception_id(FUND_NAME, QUARTER, "familyflag",
                                                  fam["issuerNameNormalized"])
        resolution = get_resolution(fam["exception_id"])
        fam["human_resolution"] = (
            f"{resolution['decision']} by {resolution['reviewer']} at {resolution['timestamp']}"
            + (f" -- {resolution['note']}" if resolution.get("note") else "")
        ) if resolution else None

    if not families:
        print("  None found -- every issuer name maps to exactly one CUSIP in this filing.")
    still_open = [f for f in families if not f["human_resolution"]]
    reviewed = [f for f in families if f["human_resolution"]]
    for fam in families:
        tag = f"  [{fam['human_resolution']}]" if fam["human_resolution"] else f"  [{fam['exception_id']}]"
        print(f"  {fam['issuerNameNormalized']} ({fam['cusipCount']} CUSIPs){tag}:")
        for m in fam["members"]:
            print(f"    {m['cusip']}  {m['instrumentClass']:10s} "
                  f"value=${m['value']:>12,d}  shares/principal={m['shares']:>12,d}")
    if reviewed:
        print(f"\n{len(reviewed)} family flag(s) already reviewed by a human -- see labels above.")

    if len(sys.argv) > 2:
        print("\n" + "=" * 70)
        print("POSITION STATUS (quarter over quarter)")
        with open(sys.argv[1]) as f:
            old_rows = json.load(f)
        with open(sys.argv[2]) as f:
            new_rows = json.load(f)
        old_positions = aggregate_to_economic_positions(old_rows)
        new_positions = aggregate_to_economic_positions(new_rows)
        statuses = compute_position_status(old_positions, new_positions)
        for s in sorted(statuses, key=lambda x: x["status"]):
            print(f"  [{s['status']:9s}] {s['issuer']:30s} "
                  f"shares {s['oldShares']:>10,d} -> {s['newShares']:>10,d} "
                  f"({s['sharesChangePct']}%)")
    else:
        print("\nPOSITION STATUS: skipped (pass two classified_rows.json paths "
              "as args to compare quarters)")

    with open("data/analysis_results.json", "w") as f:
        json.dump({
            "positions": positions, "trueLongExposure": exposures,
            "concentration": conc, "sectorConcentration": sector_conc,
            "indexHedgeRatio": hedge, "relatedSecurityFamilies": families,
        }, f, indent=2)
    print("\nWrote data/analysis_results.json")
