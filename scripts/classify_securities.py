"""
classify_securities.py — Instrument classification. Fund-agnostic:
works on any 13F filing, not just the ones used to build it.

Per SKILL.md: every filing line item gets exactly one class before any
integrity check or aggregation runs.

ORDER MATTERS. Fund identity is checked BEFORE the options branch
returns. A put or call on a fund must be classified by what the fund
IS, not left as an undifferentiated PUT/CALL -- otherwise an SPY or
IWM put (the two rows an index-hedge-ratio calc depends on) gets
bucketed identically to a single-name put, and the hedge ratio is
silently wrong. This was found by inspecting a working integrity
script where the options branch returned first: SPY/IWM puts were
classified as plain "PUT" and never reached the fund-identity check
at all.
"""
import json
import re

WARRANT_PATTERN = re.compile(r"^\*W\b|^WT\b|^WTS\b|WARRANT|EXP\s+\d", re.IGNORECASE)

# Ticker-keyed fund taxonomy. Deliberately split into categories that
# matter for different signals:
#   BROAD_INDEX   -> feeds the index-hedge-ratio calc. Nothing else may.
#   SECTOR        -> long/short sector exposure, not a macro hedge.
#   FIXED_INCOME  -> a rates or credit hedge, not an equity-index hedge.
#   COMMODITY     -> not equity exposure at all.
#   INTL_REGIONAL -> regional/EM exposure, not a US broad-market hedge.
# Mixing any of these into "index hedge ratio" corrupts exactly the
# signal that ratio exists to isolate.
BROAD_INDEX_TICKERS = {"SPY", "QQQ", "IWM", "DIA", "VOO", "VTI", "IVV"}

SECTOR_ETF_TICKERS = {
    "XLK", "XLF", "XLE", "XLI", "XLV", "XLP", "XLY", "XLU", "XLC", "XLB",
    "XOP", "XBI", "XRT", "KRE", "XSD", "XME", "XHB", "VNQ",
}

FIXED_INCOME_ETF_TICKERS = {"TLT", "HYG", "LQD", "AGG", "BND", "SHY", "IEF"}

COMMODITY_ETF_TICKERS = {"GLD", "SLV", "USO", "UNG"}

INTL_REGIONAL_ETF_TICKERS = {"EEM", "EFA", "FXI", "EWJ"}

FUND_TICKER_MAP = {
    **{t: "ETF_INDEX" for t in BROAD_INDEX_TICKERS},
    **{t: "SECTOR_ETF" for t in SECTOR_ETF_TICKERS},
    **{t: "FIXED_INCOME_ETF" for t in FIXED_INCOME_ETF_TICKERS},
    **{t: "COMMODITY_ETF" for t in COMMODITY_ETF_TICKERS},
    **{t: "INTL_REGIONAL_ETF" for t in INTL_REGIONAL_ETF_TICKERS},
}

# CUSIP-keyed, for funds verified against a primary source (the filing's
# own titleOfClass, or an issuer factsheet) and confirmed correct as of
# this writing. CUSIP is always present in a 13F row; ticker usually
# isn't without a separate resolution step, so this table lets known
# funds resolve without waiting on one. Extend as new funds get verified
# -- never add a CUSIP here on inference from an abbreviated name alone.
FUND_CUSIP_MAP = {
    # Verified directly from the filing's own titleOfClass text
    # ("S&P 500 ETF" / "RUSSELL 2000 ETF") -- no external lookup needed.
    "78462F103": "ETF_INDEX",       # SPDR S&P 500 ETF Trust (SPY)
    "464287655": "ETF_INDEX",       # iShares Russell 2000 ETF (IWM)
    # Verified against State Street's own fact sheets, 2026-09-02.
    "81369Y506": "SECTOR_ETF",      # Energy Select Sector SPDR (XLE)
    "81369Y886": "SECTOR_ETF",      # Utilities Select Sector SPDR (XLU)
    "78468R556": "SECTOR_ETF",      # SPDR S&P Oil & Gas E&P (XOP)
    # Verified against iShares' own factsheet and cross-referenced ISIN,
    # 2026-09-03, while testing against Bridgewater Associates' holdings.
    "464287721": "SECTOR_ETF",      # iShares U.S. Technology ETF (IYW)
    # Verified against multiple independent sources (SEC 424B2 filings,
    # SSGA's own fund page), 2026-09-03, from Armistice's real Q2 2026
    # live filing -- found as FUND_UNVERIFIED before this entry existed.
    "78464A714": "SECTOR_ETF",      # SPDR S&P Retail ETF (XRT)
    # Verified directly from the filing's own titleOfClass text
    # ("SEMICONDUCTR ETF"), 2026-09-08, from Pinnbrook Capital
    # Management's real Q4 2025/Q1 2026 filings -- found as a silently
    # miscounted plain PUT before this entry existed, because "VANECK"
    # isn't in ETF_SPONSOR_PATTERN below. SECTOR_ETF, not ETF_INDEX --
    # semiconductor is an equity-sector play (same category as XSD
    # above), not a broad-market hedge.
    "92189F676": "SECTOR_ETF",      # VanEck Semiconductor ETF (SMH)
    # Verified directly from the filing's own titleOfClass text
    # ("SR LN ETF"), 2026-09-08, same Pinnbrook filings -- caught as
    # FUND_UNVERIFIED_PUT (not silently miscounted) since "INVESCO"
    # IS in ETF_SPONSOR_PATTERN, but not yet in any verified table.
    # FIXED_INCOME_ETF, not SECTOR_ETF -- a senior-loan/floating-rate
    # product is a credit/rates hedge, the same category as TLT/HYG,
    # not an equity-sector one.
    "46138G508": "FIXED_INCOME_ETF", # Invesco Senior Loan ETF (BKLN)
    # Verified directly from the filing's own titleOfClass text
    # ("GLOBAL X URANIUM"), 2026-09-10, from Melqart Asset Management's
    # real Q2 2026 filing -- found as silently miscounted plain COMMON
    # before this entry existed, because "GLOBAL X" isn't in
    # ETF_SPONSOR_PATTERN below (only this specific verified CUSIP
    # added, not the sponsor name -- same precedent as VANECK above:
    # any other Global X fund this or another filing holds still
    # correctly falls to FUND_UNVERIFIED for one-time human
    # confirmation, not auto-guessed). SECTOR_ETF, not COMMODITY_ETF --
    # Global X Uranium ETF (URA) holds equity of uranium mining/nuclear
    # fuel companies, not physical uranium, the same distinction that
    # already separates XLE/XOP (equity-sector) from GLD/SLV/USO/UNG
    # (physical-commodity) above.
    "37954Y871": "SECTOR_ETF",      # Global X Uranium ETF (URA)
}

# Fund-sponsor name pattern, checked against BOTH nameOfIssuer and
# titleOfClass. Catches fund-shaped rows whose ticker isn't (yet) in
# any list above -- e.g. a new sector SPDR, a thematic ETF, a filer
# using a share-class name instead of the trading ticker. This is a
# heuristic, not a closed list. A match here does NOT default to
# ETF_INDEX or COMMON -- it returns FUND_UNVERIFIED, a distinct class
# that must be resolved by a human before it enters any exposure
# calculation. Silently guessing is worse than flagging.
ETF_SPONSOR_PATTERN = re.compile(
    r"SPDR|ISHARES|VANGUARD|INVESCO|STATE STREET|SELECT SECTOR", re.IGNORECASE
)


def normalize_ticker(value):
    """Coerce a ticker to a string usable by FUND_TICKER_MAP.

    Invalid values become "" so classification never calls .strip() on
    None / NaN / non-strings. Empty ticker is a no-op for the map.
    Valid tickers are stripped but otherwise unchanged (case included).
    """
    if value is None:
        return ""
    if isinstance(value, str):
        text = value.strip()
        if not text or text.casefold() in ("nan", "none"):
            return ""
        return text
    try:
        if value != value:
            return ""
    except Exception:
        return ""
    return ""


def fund_class_of(row):
    """Returns a fund class string if this row is fund-shaped, else None.
    Checked independently of putCall so options branches can consult it.
    Checks CUSIP first (always present, verified list), then ticker
    (requires an upstream resolution step), then falls to the sponsor-
    name pattern as a last resort that flags rather than guesses."""
    cusip = row["cusip"]
    if cusip in FUND_CUSIP_MAP:
        return FUND_CUSIP_MAP[cusip]

    ticker = normalize_ticker(row.get("ticker")).upper()
    if ticker in FUND_TICKER_MAP:
        return FUND_TICKER_MAP[ticker]

    name = row["nameOfIssuer"]
    title = row["titleOfClass"]
    if ETF_SPONSOR_PATTERN.search(name) or ETF_SPONSOR_PATTERN.search(title):
        return "FUND_UNVERIFIED"

    return None


def classify_row(row):
    """
    Returns one of:
      COMMON, CALL, PUT, WARRANT, CONVERTIBLE_BOND,
      ETF_INDEX, ETF_INDEX_CALL, ETF_INDEX_PUT,
      SECTOR_ETF, SECTOR_ETF_CALL, SECTOR_ETF_PUT,
      FIXED_INCOME_ETF, FIXED_INCOME_ETF_CALL, FIXED_INCOME_ETF_PUT,
      COMMODITY_ETF, COMMODITY_ETF_CALL, COMMODITY_ETF_PUT,
      INTL_REGIONAL_ETF, INTL_REGIONAL_ETF_CALL, INTL_REGIONAL_ETF_PUT,
      FUND_UNVERIFIED, FUND_UNVERIFIED_CALL, FUND_UNVERIFIED_PUT,
      OTHER

    CONVERTIBLE_BOND is checked FIRST, ahead of fund identity and the
    options branch, keyed on sshPrnamtType == "PRN" -- the definitive
    SEC-schema signal for a principal-amount debt security, confirmed
    against real historical 13F filings (titleOfClass "DBCV", schema
    stable since well before 2013). This is deliberately NOT keyed on
    titleOfClass text: real convertible-bond class strings vary wildly
    ("DBCV", "05 04 31 CVT", "0.925 03 01 31 CVT PUT", coupon/maturity
    notation with no fixed pattern) in a way ordinary equity class
    strings don't, so titleOfClass pattern-matching would be fragile
    here in a way it isn't for warrants. sshPrnamtType is stable and
    load-bearing instead.

    Why this has to come before everything else: value / sshPrnamt for
    a PRN row is NOT a per-share price -- sshPrnamt is principal amount
    (face value in dollars), so the ratio is price-as-fraction-of-par
    (a bond near par gives ~1.0, regardless of the bond's real price
    level). Tested against real Ghisallo Capital Management holdings
    (CIK 1825214, Q1 2026): before this fix, 4 real convertible bonds
    classified as COMMON, and the filing-wide median (check 2b) landed
    at $1.0035 -- a hair above the <$1.0 threshold. A book with
    slightly more bonds priced at a discount to par would have tripped
    a FALSE thousands-scaling alarm on a completely healthy filing --
    a different failure mode from the Bridgewater case (which was a
    real error going undetected), and arguably more dangerous since it
    manufactures false alarms on ordinary, common institutional
    holdings rather than missing a real one.
    """
    if row.get("sshPrnamtType") == "PRN":
        return "CONVERTIBLE_BOND"

    put_call = row["putCall"]
    title = row["titleOfClass"]

    # Fund identity FIRST -- before the options branch can return.
    fclass = fund_class_of(row)
    if fclass is not None:
        if put_call == "Call":
            return f"{fclass}_CALL"
        if put_call == "Put":
            return f"{fclass}_PUT"
        return fclass

    # Single-name options
    if put_call == "Call":
        return "CALL"
    if put_call == "Put":
        return "PUT"

    # Warrants -- can carry sshPrnamtType=SH and blank putCall, so they
    # look like common stock unless titleOfClass is read.
    if WARRANT_PATTERN.search(title):
        return "WARRANT"

    return "COMMON"


def classify_all(rows):
    for row in rows:
        row["ticker"] = normalize_ticker(row.get("ticker"))
        row["instrumentClass"] = classify_row(row)
    return rows


if __name__ == "__main__":
    import sys
    # Optional input/output override -- python classify_securities.py
    # data/parsed_rows_2026-03-31.json data/classified_rows_2026-03-31.json
    # -- for classifying a historical quarter without touching the
    # default files everything else in the pipeline expects. Defaults
    # unchanged if no args given.
    input_path = sys.argv[1] if len(sys.argv) > 1 else "data/parsed_rows.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "data/classified_rows.json"

    with open(input_path) as f:
        rows = json.load(f)

    # Normalize ticker before classify. Missing / NaN / non-string values
    # become "" so FUND_TICKER_MAP is a no-op and only CUSIP / sponsor
    # patterns apply.
    classify_all(rows)

    from collections import Counter
    counts = Counter(r["instrumentClass"] for r in rows)
    print("Classification breakdown:")
    for cls, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {cls:20s} {n:4d} rows")
    print(f"\nTotal: {len(rows)} rows")

    print("\nRegression check -- SPY/IWM puts must classify as "
          "ETF_INDEX_PUT, not plain PUT:")
    for r in rows:
        if r["cusip"] in ("78462F103", "464287655"):
            print(f"  {r['nameOfIssuer']:35s} class={r['instrumentClass']}")

    print("\nSector/fund rows that would have silently fallen into COMMON "
          "or an undifferentiated ETF_INDEX bucket before this fix:")
    for r in rows:
        if r["instrumentClass"] in (
            "SECTOR_ETF", "FIXED_INCOME_ETF", "COMMODITY_ETF",
            "INTL_REGIONAL_ETF", "FUND_UNVERIFIED",
        ):
            print(f"  {r['nameOfIssuer']:35s} {r['titleOfClass']:20s} "
                  f"-> {r['instrumentClass']}")

    print("\nAll WARRANT rows:")
    for r in rows:
        if r["instrumentClass"] == "WARRANT":
            implied = r["value"] / r["sshPrnamt"] if r["sshPrnamt"] else None
            suffix = f"implied=${implied:.4f}" if implied else ""
            print(f"  {r['nameOfIssuer']:30s} {r['titleOfClass']!r:20s} {suffix}")

    with open(output_path, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"\nWrote {output_path}")
