"""
integrity.py — Integrity checks. Fund-agnostic: consumes the output of
classify_securities.py rather than re-deriving classification inline.

Derivative detection in checks 3 and 5 uses the RAW putCall field, not
instrumentClass. This matters: after classify_securities.py's fund-identity
fix, a put on SPY classifies as "ETF_INDEX_PUT", not "PUT" -- a check that
tests instrumentClass == "PUT" would silently stop recognizing it as a
derivative. putCall is stable regardless of what fund bucket the
underlying falls into, so it's the correct field for "is this an option"
questions. instrumentClass is still correct for "which exposure bucket
does this belong to" questions (check 2's COMMON-only floor, check 8's
grouping).

Checks 1 and 6 require external data not available from the filing alone
-> PENDING_EXTERNAL_DATA. Check 4 requires a second quarter. Check 9
requires a market-data provider (see price_verify.py) and check 4's
REVIEW output as input (see corporate_actions.py). Neither runs here.
"""
import json
from collections import defaultdict

from resolution_log import make_exception_id, get_resolution, derive_quarter_label


def apply_resolution_log(items, fund, quarter, check_name, id_fn, review_statuses):
    """Cross-references a list of check results against resolution_log.py.
    Only items whose status is in review_statuses get a real exception_id
    and resolution lookup; everything else passes through with both set
    to None. id_fn(item) -> the identifier component (row number, cusip,
    etc.) -- combined with fund/quarter/check_name via make_exception_id
    so the scheme stays identical to what corporate_actions.py already
    uses."""
    annotated = []
    for item in items:
        if item.get("status") not in review_statuses:
            annotated.append({**item, "exception_id": None, "human_resolution": None})
            continue
        eid = make_exception_id(fund, quarter, check_name, id_fn(item))
        resolution = get_resolution(eid)
        human_resolution = (
            f"{resolution['decision']} by {resolution['reviewer']} at {resolution['timestamp']}"
            + (f" -- {resolution['note']}" if resolution.get("note") else "")
        ) if resolution else None
        annotated.append({**item, "exception_id": eid, "human_resolution": human_resolution})
    return annotated


def split_by_resolution(items):
    """Splits resolution-log-annotated items into (still_open, escalated,
    closed) -- the same three-way split corporate_actions.py uses, so
    every producer presents human-review state the same way."""
    still_open = [i for i in items if i.get("exception_id") and not i.get("human_resolution")]
    escalated = [i for i in items if (i.get("human_resolution") or "").startswith("ESCALATE")]
    closed = [i for i in items if i.get("human_resolution") and not i["human_resolution"].startswith("ESCALATE")]
    return still_open, escalated, closed

TOLERANCE_PCT_OPTIONS_CONSISTENCY = 1.0  # check 5
PRICE_CONTINUITY_THRESHOLD_PCT = 80.0    # check 4
IMPLIED_PRICE_CEILING = 10000            # check 2
IMPLIED_PRICE_FLOOR = 0.01               # check 2, COMMON only


def check_1_total_reconciliation(rows, third_party_total=None):
    sec_total = sum(r["value"] for r in rows if r["value"] is not None)
    if third_party_total is None:
        return {"sec_reported_total": sec_total, "status": "PENDING_EXTERNAL_DATA",
                "detail": "Compare against an independent third-party 13F total "
                          "after normalizing units."}
    diff_pct = abs(sec_total - third_party_total) / third_party_total * 100
    status = "PASS" if diff_pct <= 2.0 else "REVIEW_VALUE_SCALING"
    return {"sec_reported_total": sec_total, "third_party_total": third_party_total,
            "diff_pct": round(diff_pct, 3), "status": status}


def check_2_implied_price_sanity(rows):
    """Ceiling breach is a hard FAIL -- almost certainly a digit-boundary
    error. Floor breach is REVIEW and scoped to COMMON only -- warrants
    and sub-penny equities legitimately price there.

    CONVERTIBLE_BOND rows are excluded entirely, not silently included --
    see check_2c. value / sshPrnamt for a PRN row is price-as-fraction-of-
    par, not a per-share price; applying this check's equity-calibrated
    floor/ceiling to it would be checking the wrong thing against the
    wrong bounds."""
    results = []
    for r in rows:
        if r["instrumentClass"] == "CONVERTIBLE_BOND":
            results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                             "class": r["instrumentClass"], "status": "NOT_APPLICABLE",
                             "detail": "PRN-type (principal amount) row -- see check 2c"})
            continue
        if r["sshPrnamt"] in (None, 0) or r["value"] is None:
            results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                             "status": "REVIEW_SHARE_COUNT",
                             "detail": "missing value or shares"})
            continue
        implied = r["value"] / r["sshPrnamt"]
        if implied > IMPLIED_PRICE_CEILING:
            status = "FAIL"
        elif r["instrumentClass"] == "COMMON" and implied < IMPLIED_PRICE_FLOOR:
            status = "REVIEW_VALUE_SCALING"
        else:
            status = "PASS"
        results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                         "class": r["instrumentClass"], "implied": round(implied, 4),
                         "status": status})
    return results


def check_2c_convertible_bond_price_sanity(rows):
    """The bond-appropriate companion to check 2. For a CONVERTIBLE_BOND
    (sshPrnamtType == PRN) row, sshPrnamt is principal amount (face
    value in dollars), not a share count -- the meaningful figure is
    price as a percentage of par (value / principal * 100), not a
    per-share implied price. This is also the convention that would
    match a bond's Bloomberg PX_LAST (quoted per 100 face), unlike
    value/principal directly, which lands near 1.0 for a bond near par
    and would silently mismatch a bond-pricing source without this
    conversion.

    Verified against real Ghisallo Capital Management Q1 2026 holdings
    (CIK 1825214): four real convertible bonds price at 94.6%-100.5%
    of par, all comfortably inside a plausible range -- distressed debt
    can legitimately trade well below par, so the floor here is wide
    (10%) rather than equity-calibrated."""
    PCT_OF_PAR_FLOOR, PCT_OF_PAR_CEILING = 10.0, 300.0
    results = []
    for r in rows:
        if r["instrumentClass"] != "CONVERTIBLE_BOND":
            continue
        if r["sshPrnamt"] in (None, 0) or r["value"] is None:
            results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                             "status": "REVIEW_SHARE_COUNT",
                             "detail": "missing value or principal amount"})
            continue
        pct_of_par = r["value"] / r["sshPrnamt"] * 100
        if pct_of_par > PCT_OF_PAR_CEILING or pct_of_par < 0:
            status = "FAIL"
        elif pct_of_par < PCT_OF_PAR_FLOOR:
            status = "REVIEW_VALUE_SCALING"
        else:
            status = "PASS"
        results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                         "pctOfPar": round(pct_of_par, 2), "status": status})
    return results


def check_2b_filing_wide_value_scaling(rows):
    """Filing-wide companion to check 2 -- a population check, not a
    per-row one. Closes a real gap found by testing against a genuinely
    different fund (Bridgewater Associates, a historically-confirmed
    thousands reporter -- its 2006 13F states "Value Total: $476,707
    (thousands)" in the filing text itself): a filing-wide value-in-
    thousands error produces implied prices that are individually
    PLAUSIBLE (a real ~$650 SPY position reported in thousands implies
    $0.65 -- inside check 2's per-row $0.01-$10,000 floor/ceiling) but
    collectively wrong. Per-row check 2 cannot catch this by
    construction; it has to be a population check.

    Also closes a real gap in check 9: check 9 only runs on rows check
    4 flags, and a scaling error that is CONSISTENT across quarters
    never trips check 4 either -- the cross-quarter ratio looks stable
    even though both sides are wrong by the same factor. This check
    runs unconditionally, every single-quarter run, with no dependency
    on cross-quarter data or an external total (unlike check 1, which
    needs a third-party number this can run without).

    Population is COMMON plus fund-type long positions (broad-index,
    sector, fixed-income, commodity, regional funds) -- all of these
    have real per-share dollar prices in normal ranges, unlike
    warrants (legitimately sub-penny, excluded) or options (priced at
    underlying value, redundant with the underlying's own row).
    Restricting to COMMON alone was tried first and found, by testing,
    to leave too few rows for the check to have any statistical power
    on an ETF-heavy book -- exactly the fund type (Bridgewater-style
    macro) most likely to actually need this check: a 3-row test with
    SPY and IYW correctly classified out of COMMON left only 1 true
    COMMON row, below the minimum sample size, on the very filing this
    check exists to protect.

    Verified: correctly flags a constructed Bridgewater-shaped
    thousands-scaling test (median implied price $0.50, three real
    verified CUSIPs -- SPY, IYW, AMZN -- all understated exactly
    1000x) and correctly does not flag real Armistice Q1 2026 data
    (median well above $1). CONVERTIBLE_BOND is deliberately absent
    from priced_classes below -- a bond's value/principal ratio is
    price-as-fraction-of-par, not a per-share price, and mixing it
    into this population is what produced a near-miss false positive
    on real Ghisallo Capital Management data (median $1.0035, a hair
    above the <$1.0 threshold) before this exclusion existed."""
    priced_classes = {
        "COMMON", "ETF_INDEX", "SECTOR_ETF", "FIXED_INCOME_ETF",
        "COMMODITY_ETF", "INTL_REGIONAL_ETF", "FUND_UNVERIFIED",
    }
    prices = [
        r["value"] / r["sshPrnamt"]
        for r in rows
        if r["instrumentClass"] in priced_classes and r.get("sshPrnamt")
    ]
    if len(prices) < 3:
        return {"status": "NOT_APPLICABLE",
                "detail": "too few priced (non-warrant, non-option) rows to assess a population"}

    prices.sort()
    n = len(prices)
    median = (prices[n // 2] if n % 2
              else (prices[n // 2 - 1] + prices[n // 2]) / 2)

    if median < 1.0:
        return {
            "status": "REVIEW_VALUE_SCALING",
            "medianImpliedPrice": round(median, 4), "rowCount": n,
            "detail": (
                f"Median implied price across {n} priced rows is ${median:.4f} -- "
                f"below $1, suggesting the whole filing may be reported in "
                f"thousands and not yet corrected. Verify against the filing's "
                f"own value scale before trusting any implied price in this "
                f"dataset."
            ),
        }
    return {"status": "PASS", "medianImpliedPrice": round(median, 4), "rowCount": n}


def check_3_voting_authority(rows):
    """Derivative rows (by raw putCall, not instrumentClass) are exempt --
    labeled NOT_APPLICABLE, not REVIEW, since there's nothing to
    investigate about a rule that doesn't apply."""
    results = []
    for r in rows:
        if r["putCall"] is not None:
            results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                             "status": "NOT_APPLICABLE",
                             "detail": "derivative row; common-equity voting "
                                       "authority check does not apply"})
            continue
        if r["investmentDiscretion"] != "SOLE":
            results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                             "status": "NOT_APPLICABLE", "detail": "not sole discretion"})
            continue
        status = "PASS" if r["votingAuthoritySole"] == r["sshPrnamt"] else "FAIL"
        results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                         "status": status,
                         "sole": r["votingAuthoritySole"], "shares": r["sshPrnamt"]})
    return results


def check_4_price_continuity(rows_by_quarter):
    """rows_by_quarter: {report_date: [classified rows]}, at least 2 keys.
    Groups by CUSIP + instrumentClass across adjacent quarters. A >80%
    move is an ANOMALY TRIGGER, not a conclusion -- resolve via
    corporate_actions.py, which consumes this output."""
    quarters = sorted(rows_by_quarter.keys())
    results = []
    for i in range(1, len(quarters)):
        old_q, new_q = quarters[i - 1], quarters[i]
        old_by_key = {(r["cusip"], r["instrumentClass"]): r for r in rows_by_quarter[old_q]}
        new_by_key = {(r["cusip"], r["instrumentClass"]): r for r in rows_by_quarter[new_q]}
        for key in set(old_by_key) & set(new_by_key):
            old_r, new_r = old_by_key[key], new_by_key[key]
            if not old_r["sshPrnamt"] or not new_r["sshPrnamt"]:
                continue
            old_price = old_r["value"] / old_r["sshPrnamt"]
            new_price = new_r["value"] / new_r["sshPrnamt"]
            if old_price == 0:
                status, change_pct = "REVIEW_MARKET_DATA", None
            else:
                change_pct = (new_price - old_price) / old_price * 100
                status = "REVIEW_MARKET_DATA" if abs(change_pct) > PRICE_CONTINUITY_THRESHOLD_PCT else "PASS"
            results.append({
                "oldQuarter": old_q, "newQuarter": new_q, "cusip": key[0],
                "instrumentClass": key[1], "issuer": new_r["nameOfIssuer"],
                "oldImpliedPrice": round(old_price, 4), "newImpliedPrice": round(new_price, 4),
                "changePct": round(change_pct, 2) if change_pct is not None else None,
                "status": status,
            })
    return results


def run_check_4_multi_quarter(fund_name, quarter_specs):
    """CLI-facing wrapper: loads 'label:path' quarter files, runs
    check_4_price_continuity, resolves tickers via security_master.py
    (edgartools primary, Bloomberg PARSEKYABLE_DES fallback if
    data/market_data.json exists), and writes check4_price_continuity.csv
    in the exact schema price_verify.py and corporate_actions.py expect
    (PascalCase columns; Status literally "PASS" or "REVIEW", not the
    finer-grained REVIEW_MARKET_DATA -- those scripts inherit this
    two-value contract and translating it here, once, keeps both
    readers unchanged rather than special-casing them)."""
    import csv
    from pathlib import Path

    rows_by_quarter = {}
    for spec in quarter_specs:
        label, path = spec.split(":", 1)
        with open(path) as f:
            rows_by_quarter[label] = json.load(f)

    results = check_4_price_continuity(rows_by_quarter)

    all_cusips = sorted({r["cusip"] for r in results})
    ticker_map = {}
    try:
        from security_master import resolve_all
        sm_input = [{"cusip": c} for c in all_cusips]
        sm_result = resolve_all(sm_input)
        ticker_map = {c: v["ticker"] for c, v in sm_result.items()}
        bloomberg_resolved = sum(1 for v in sm_result.values() if v["source"] == "bloomberg")
        if bloomberg_resolved:
            print(f"  {bloomberg_resolved} ticker(s) resolved via Bloomberg fallback "
                  f"(edgartools missed these).")
    except ImportError:
        print("  WARNING: security_master.py not importable here -- Ticker column "
              "will be blank, price_verify.py cannot run on these rows "
              "until resolved (yfinance needs a ticker symbol, not a CUSIP).")

    output_rows = []
    for r in results:
        status = "PASS" if r["status"] == "PASS" else "REVIEW"
        output_rows.append({
            "OldQuarter": r["oldQuarter"], "NewQuarter": r["newQuarter"],
            "Ticker": ticker_map.get(r["cusip"]) or "",
            "Cusip": r["cusip"], "SecurityType": r["instrumentClass"],
            "OldImpliedPrice": r["oldImpliedPrice"], "NewImpliedPrice": r["newImpliedPrice"],
            "PriceChangePct": r["changePct"], "Status": status,
            "Reason": "" if status == "PASS" else
                      f"implied price moved {r['changePct']}% -- exceeds "
                      f"{PRICE_CONTINUITY_THRESHOLD_PCT}% threshold",
        })

    out_dir = Path(f"{fund_name}_integrity")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "check4_price_continuity.csv"
    fieldnames = ["OldQuarter", "NewQuarter", "Ticker", "Cusip", "SecurityType",
                  "OldImpliedPrice", "NewImpliedPrice", "PriceChangePct", "Status", "Reason"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    review_rows = [r for r in output_rows if r["Status"] == "REVIEW"]
    no_ticker_review = [r for r in review_rows if not r["Ticker"]]
    print(f"  {len(output_rows)} transitions, {len(review_rows)} flagged REVIEW")
    print(f"  Wrote {out_path}")
    if no_ticker_review:
        print(f"  WARNING: {len(no_ticker_review)} REVIEW row(s) have no resolved "
              f"ticker -- price_verify.py will fail on these specifically until "
              f"resolved manually:")
        for r in no_ticker_review:
            print(f"    {r['Cusip']}  {r['SecurityType']}")
    return output_rows


def check_5_options_price_consistency(rows):
    """Tolerance-based, not exact-match -- rounding in reported dollar
    values can produce trivially different implied prices for a
    genuinely consistent underlying. 1% spread, not equality."""
    by_cusip = defaultdict(list)
    for r in rows:
        if r["sshPrnamt"] and r["value"] is not None:
            by_cusip[r["cusip"]].append(r)

    results = []
    for cusip, group in by_cusip.items():
        has_option = any(r["putCall"] is not None for r in group)
        if not has_option:
            continue
        implied_prices = [r["value"] / r["sshPrnamt"] for r in group]
        min_p, max_p = min(implied_prices), max(implied_prices)
        if min_p == 0:
            status = "REVIEW_SECURITY_MAPPING"
        else:
            spread_pct = (max_p - min_p) / min_p * 100
            status = "PASS" if spread_pct <= TOLERANCE_PCT_OPTIONS_CONSISTENCY else "REVIEW_SECURITY_MAPPING"
        results.append({
            "cusip": cusip, "issuer": group[0]["nameOfIssuer"], "status": status,
            "rows": len(group), "implied_prices": [round(p, 4) for p in implied_prices]
        })
    return results


def check_6_shares_outstanding(rows, shares_outstanding_by_cusip=None):
    results = []
    for r in rows:
        so = (shares_outstanding_by_cusip or {}).get(r["cusip"])
        if so is None:
            results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                             "status": "PENDING_EXTERNAL_DATA",
                             "detail": "requires verified shares-outstanding data"})
            continue
        status = "FAIL" if (r["sshPrnamt"] or 0) > so else "PASS"
        results.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                         "shares": r["sshPrnamt"], "sharesOutstanding": so, "status": status})
    return results


def check_7_missing_fields(rows):
    required = ["nameOfIssuer", "titleOfClass", "cusip", "value", "sshPrnamt", "sshPrnamtType"]
    missing = []
    for r in rows:
        for field in required:
            if r.get(field) in (None, ""):
                missing.append({"row": r["raw_row_number"], "issuer": r["nameOfIssuer"],
                                 "field": field})
    return missing


def summarize_integrity_status(rows, fund_name, market_data=None):
    """Same hard-fail rule as this module's CLI (__main__), returned as
    a payload the dashboard can display. Does not invent a PASS that
    the checks did not produce. Check 1 remains PENDING_EXTERNAL_DATA
    unless a third-party total is supplied -- so a clean filing still
    reports PASS WITH REVIEW/PENDING ITEMS, never a hardcoded
    'SEC QA PASS'."""
    quarter = derive_quarter_label(rows)

    c1 = check_1_total_reconciliation(rows)
    c2 = apply_resolution_log(
        check_2_implied_price_sanity(rows), fund_name, quarter, "check2",
        id_fn=lambda item: f"row{item['row']}",
        review_statuses={"REVIEW_VALUE_SCALING", "REVIEW_SHARE_COUNT"},
    )
    c2b = check_2b_filing_wide_value_scaling(rows)
    c2c = apply_resolution_log(
        check_2c_convertible_bond_price_sanity(rows), fund_name, quarter, "check2c",
        id_fn=lambda item: f"row{item['row']}",
        review_statuses={"REVIEW_VALUE_SCALING", "REVIEW_SHARE_COUNT"},
    )
    c3 = check_3_voting_authority(rows)
    c5 = apply_resolution_log(
        check_5_options_price_consistency(rows), fund_name, quarter, "check5",
        id_fn=lambda item: item["cusip"],
        review_statuses={"REVIEW_SECURITY_MAPPING"},
    )

    shares_outstanding_by_cusip = {}
    if market_data:
        records = market_data.values() if isinstance(market_data, dict) else market_data
        for md in records:
            so = md.get("EQY_SH_OUT")
            if so is not None and md.get("EQY_SH_OUT_status") == "PASS" and so > 0:
                shares_outstanding_by_cusip[md["cusip"]] = so * 1_000_000
    c6 = check_6_shares_outstanding(rows, shares_outstanding_by_cusip) if shares_outstanding_by_cusip else []

    c7 = check_7_missing_fields(rows)
    c8_raw = check_8_duplicate_rows(rows)
    for d in c8_raw:
        d["status"] = "REVIEW_SECURITY_MAPPING"
        d["identifier"] = f"{d['cusip']}_row{min(d['row_numbers'])}"
    c8 = apply_resolution_log(
        c8_raw, fund_name, quarter, "check8",
        id_fn=lambda item: item["identifier"],
        review_statuses={"REVIEW_SECURITY_MAPPING"},
    )

    hard_fails = (
        [r for r in c2 if r["status"] == "FAIL"]
        + [r for r in c3 if r["status"] == "FAIL"]
        + [r for r in c6 if r["status"] == "FAIL"]
    )
    if hard_fails:
        status = "FAIL"
    else:
        status = "PASS WITH REVIEW/PENDING ITEMS"

    def _open_reviews(items):
        return [i for i in items
                if i.get("exception_id") and not i.get("human_resolution")]

    open_reviews = (
        _open_reviews(c2) + _open_reviews(c2c) + _open_reviews(c5) + _open_reviews(c8)
    )
    c2b_open = c2b.get("status") == "REVIEW_VALUE_SCALING"

    return {
        "status": status,
        "hardFailCount": len(hard_fails),
        "check1Status": c1.get("status"),
        "openReviewCount": len(open_reviews) + (1 if c2b_open else 0),
        "missingFieldCount": len(c7),
        "duplicateGroupCount": len(c8),
    }


def check_8_duplicate_rows(rows):
    """Audit only. Never auto-dedupe -- 13F discloses no strike or
    expiry, so identical-looking option rows can be genuinely distinct
    positions."""
    seen = defaultdict(list)
    for r in rows:
        key = (r["cusip"], r["value"], r["sshPrnamt"], r["putCall"],
               r["investmentDiscretion"], r["votingAuthoritySole"])
        seen[key].append(r)
    duplicates = []
    for key, group in seen.items():
        if len(group) > 1:
            duplicates.append({
                "cusip": key[0], "issuer": group[0]["nameOfIssuer"],
                "instrumentClass": group[0]["instrumentClass"],
                "row_numbers": [r["raw_row_number"] for r in group],
                "count": len(group),
                "note": "Duplicate-looking rows detected. No automatic deduplication "
                        "performed. Investigate whether rows represent separate "
                        "option positions or manager/security allocations.",
            })
    return duplicates


if __name__ == "__main__":
    import sys

    with open("data/classified_rows.json") as f:
        rows = json.load(f)

    FUND_NAME = sys.argv[1] if len(sys.argv) > 1 else "fund"
    QUARTER = derive_quarter_label(rows)

    print("=" * 70)
    print("CHECK 1: Total reconciliation")
    c1 = check_1_total_reconciliation(rows)
    print(f"  SEC reported total: ${c1['sec_reported_total']:,d}  -> {c1['status']}")

    print("\n" + "=" * 70)
    print("CHECK 2: Implied price sanity")
    c2 = check_2_implied_price_sanity(rows)
    c2 = apply_resolution_log(c2, FUND_NAME, QUARTER, "check2",
                               id_fn=lambda item: f"row{item['row']}",
                               review_statuses={"REVIEW_VALUE_SCALING", "REVIEW_SHARE_COUNT"})
    c2_open, c2_escalated, c2_closed = split_by_resolution(c2)
    for status in ("FAIL", "REVIEW_VALUE_SCALING", "REVIEW_SHARE_COUNT"):
        flagged = [r for r in c2_open if r["status"] == status]
        if flagged:
            print(f"  {status}: {len(flagged)}")
            for f in flagged[:10]:
                print(f"    ROW {f['row']:3d} {f['issuer']:30s} implied=${f.get('implied')}  "
                      f"[{f['exception_id']}]")
    if c2_closed:
        print(f"  {len(c2_closed)} previously resolved (APPROVE/CORRECT) -- not shown above")
    if c2_escalated:
        print(f"  {len(c2_escalated)} previously ESCALATED -- still open:")
        for f in c2_escalated:
            print(f"    ROW {f['row']:3d} {f['issuer']}: {f['human_resolution']}")
    passed = [r for r in c2 if r["status"] == "PASS"]
    print(f"  PASS: {len(passed)} / {len(c2)}")

    print("\nCHECK 2b: Filing-wide value-scaling sanity (population check, "
          "runs unconditionally)")
    c2b = check_2b_filing_wide_value_scaling(rows)
    c2b_resolution = None
    if c2b["status"] == "REVIEW_VALUE_SCALING":
        c2b_eid = make_exception_id(FUND_NAME, QUARTER, "check2b", "filing_wide")
        c2b_resolution_record = get_resolution(c2b_eid)
        c2b_resolution = (
            f"{c2b_resolution_record['decision']} by {c2b_resolution_record['reviewer']} "
            f"at {c2b_resolution_record['timestamp']}"
        ) if c2b_resolution_record else None
        if c2b_resolution:
            print(f"  REVIEW_VALUE_SCALING -- {c2b['detail']}")
            print(f"  Previously resolved: {c2b_resolution}  [{c2b_eid}]")
        else:
            print(f"  REVIEW_VALUE_SCALING -- {c2b['detail']}  [{c2b_eid}]")
    elif c2b["status"] == "PASS":
        print(f"  PASS -- median implied price ${c2b['medianImpliedPrice']} "
              f"across {c2b['rowCount']} priced rows")
    else:
        print(f"  {c2b['status']} -- {c2b.get('detail', '')}")

    print("\nCHECK 2c: Convertible bond price sanity (% of par, PRN-type rows)")
    c2c = check_2c_convertible_bond_price_sanity(rows)
    c2c = apply_resolution_log(c2c, FUND_NAME, QUARTER, "check2c",
                                id_fn=lambda item: f"row{item['row']}",
                                review_statuses={"REVIEW_VALUE_SCALING", "REVIEW_SHARE_COUNT"})
    if not c2c:
        print("  NOT_APPLICABLE -- no CONVERTIBLE_BOND rows in this filing")
    else:
        c2c_open, c2c_escalated, c2c_closed = split_by_resolution(c2c)
        for r in c2c:
            if r in c2c_closed:
                continue
            tag = f"  [{r['exception_id']}]" if r.get("exception_id") else ""
            print(f"    ROW {r['row']:3d} {r['issuer']:25s} "
                  f"{r.get('pctOfPar', '?')}% of par -> {r['status']}{tag}")
        if c2c_closed:
            print(f"  {len(c2c_closed)} previously resolved -- not shown above")

    print("\n" + "=" * 70)
    print("CHECK 3: Voting authority cross-check")
    c3 = check_3_voting_authority(rows)
    fails = [r for r in c3 if r["status"] == "FAIL"]
    na = [r for r in c3 if r["status"] == "NOT_APPLICABLE"]
    print(f"  {len(c3)} rows: {len(fails)} FAIL, {len(na)} NOT_APPLICABLE, "
          f"{len(c3) - len(fails) - len(na)} PASS")
    for f in fails:
        print(f"    ROW {f['row']:3d} {f['issuer']}: sole={f['sole']} shares={f['shares']}")

    print("\n" + "=" * 70)
    if len(sys.argv) > 2:
        # Multi-quarter mode: python integrity.py FUND_NAME
        #   2025-12-31:data/classified_rows_2025Q4.json
        #   2026-03-31:data/classified_rows_2026Q1.json  ...
        # Chronological order matters -- consecutive pairs become
        # transitions. Single-quarter checks above still ran against
        # data/classified_rows.json regardless; this is additive.
        print("CHECK 4: Cross-quarter price continuity")
        fund_name = sys.argv[1]
        quarter_specs = sys.argv[2:]
        run_check_4_multi_quarter(fund_name, quarter_specs)
    else:
        print("CHECK 4: Cross-quarter price continuity -- SKIPPED "
              "(pass FUND_NAME and 2+ 'label:path' quarter files to run)")

    print("\n" + "=" * 70)
    print("CHECK 5: Options price consistency (1% tolerance)")
    c5 = check_5_options_price_consistency(rows)
    c5 = apply_resolution_log(c5, FUND_NAME, QUARTER, "check5",
                               id_fn=lambda item: item["cusip"],
                               review_statuses={"REVIEW_SECURITY_MAPPING"})
    for r in c5:
        if r["status"] == "PASS":
            print(f"  [PASS] {r['issuer']:30s} cusip={r['cusip']} rows={r['rows']} "
                  f"implied={r['implied_prices']}")
        elif r.get("human_resolution"):
            print(f"  [REVIEW -- {r['human_resolution']}] {r['issuer']:30s} "
                  f"cusip={r['cusip']} rows={r['rows']} implied={r['implied_prices']}")
        else:
            print(f"  [REVIEW] {r['issuer']:30s} cusip={r['cusip']} rows={r['rows']} "
                  f"implied={r['implied_prices']}  [{r['exception_id']}]")

    print("\n" + "=" * 70)
    print("CHECK 6: Share-count magnitude")
    shares_outstanding_by_cusip = {}
    try:
        with open("data/market_data.json") as f:
            market_data = json.load(f)
        for md in market_data:
            so = md.get("EQY_SH_OUT")
            if so is not None and md.get("EQY_SH_OUT_status") == "PASS" and so > 0:
                # EQY_SH_OUT is Bloomberg-reported in millions -- verified
                # against real data (NVIDIA: EQY_SH_OUT=24100 x PX_LAST=
                # 228.45 = CUR_MKT_CAP exactly, from the same live pull).
                shares_outstanding_by_cusip[md["cusip"]] = so * 1_000_000
    except FileNotFoundError:
        pass

    if shares_outstanding_by_cusip:
        c6 = check_6_shares_outstanding(rows, shares_outstanding_by_cusip)
        fails = [r for r in c6 if r["status"] == "FAIL"]
        pending = [r for r in c6 if r["status"] == "PENDING_EXTERNAL_DATA"]
        passed = [r for r in c6 if r["status"] == "PASS"]
        print(f"  {len(c6)} rows: {len(fails)} FAIL, {len(pending)} PENDING_EXTERNAL_DATA "
              f"(no shares-outstanding data for that CUSIP), {len(passed)} PASS")
        for f in fails:
            print(f"    ROW {f['row']:3d} {f['issuer']}: shares={f['shares']:,d} "
                  f"exceeds sharesOutstanding={f['sharesOutstanding']:,d} -- impossible, investigate")
    else:
        c6 = []
        print("  PENDING_EXTERNAL_DATA (no data/market_data.json found, or no EQY_SH_OUT "
              "resolved -- run the Bloomberg export/import round trip first)")

    print("\n" + "=" * 70)
    print("CHECK 7: Missing required fields")
    c7 = check_7_missing_fields(rows)
    print(f"  {len(c7)} missing field(s) found")

    print("\n" + "=" * 70)
    print("CHECK 8: Duplicate-row detection (audit only)")
    c8 = check_8_duplicate_rows(rows)
    # Every check-8 entry is inherently a flag -- there's no PASS state,
    # audit-only by design (see docstring). Annotate all of them, keyed
    # on cusip + the first row number in the group for stability even
    # if two distinct duplicate groups happen to share a CUSIP.
    for d in c8:
        d["status"] = "REVIEW_SECURITY_MAPPING"
        d["identifier"] = f"{d['cusip']}_row{min(d['row_numbers'])}"
    c8 = apply_resolution_log(c8, FUND_NAME, QUARTER, "check8",
                               id_fn=lambda item: item["identifier"],
                               review_statuses={"REVIEW_SECURITY_MAPPING"})
    c8_open, c8_escalated, c8_closed = split_by_resolution(c8)
    print(f"  {len(c8)} duplicate group(s) found "
          f"({len(c8_closed)} previously resolved, {len(c8_escalated)} escalated)")
    for d in c8:
        if d in c8_closed:
            continue
        tag = f"  [{d['human_resolution']}]" if d.get("human_resolution") else f"  [{d['exception_id']}]"
        print(f"    {d['issuer']:30s} class={d['instrumentClass']:15s} "
              f"rows={d['row_numbers']} (x{d['count']}){tag}")

    hard_fails = ([r for r in c2 if r["status"] == "FAIL"] + [r for r in c3 if r["status"] == "FAIL"]
                  + [r for r in c6 if r["status"] == "FAIL"])
    if c2b["status"] == "REVIEW_VALUE_SCALING" and not c2b_resolution:
        print("\n  NOTE: check 2b flagged filing-wide value scaling -- this should "
              "be resolved before trusting downstream exposure/liquidity figures, "
              "even though it isn't in the hard-fail count above.")
    print("\n" + "=" * 70)
    if hard_fails:
        print(f"INTEGRITY STATUS: FAIL ({len(hard_fails)} hard failure(s)) "
              f"-- downstream analysis should stop.")
    else:
        print("INTEGRITY STATUS: PASS WITH REVIEW/PENDING ITEMS")
        print("No hard parser failures. External-data checks remain pending.")

    with open("data/integrity_results.json", "w") as f:
        json.dump({"check_1": c1, "check_2": c2, "check_2b": c2b, "check_2c": c2c, "check_3": c3, "check_5": c5,
                   "check_6": c6, "check_7": c7, "check_8": c8}, f, indent=2)
    print("\nWrote data/integrity_results.json")
