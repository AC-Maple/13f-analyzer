"""
security_master.py -- CUSIP -> ticker resolution.

Uses edgar.reference.get_ticker_from_cusip(), which reads from a bundled
dataset (no live network needed -- verified: resolves correctly with no
network access in this sandbox). Tested against 5 known CUSIPs from the
Armistice filing, including both broad-index ETF CUSIPs already in
classify_securities.py's FUND_CUSIP_MAP:

    023135106 -> AMZN   594918104 -> MSFT   23282W605 -> CYTK
    78462F103 -> SPY    464287655 -> IWM

Note the import path: `from edgar.reference import get_ticker_from_cusip`
-- it is NOT re-exported at the top-level `edgar` package namespace,
despite being documented there in some contexts. `from edgar import
get_ticker_from_cusip` raises ImportError.

This does not replace FUND_CUSIP_MAP / FUND_TICKER_MAP in
classify_securities.py -- those are hand-verified against primary
sources specifically because a wrong fund classification silently
corrupts the index-hedge-ratio calculation. This module is for the
lower-stakes case of getting *a* ticker to hand to yfinance or a
Bloomberg lookup; an occasional miss here means one security gets
PENDING_EXTERNAL_DATA, not a silently wrong exposure number.

Bloomberg fallback: for any CUSIP edgartools can't resolve, this falls
back to PARSEKYABLE_DES from data/market_data.json (produced by
import_bloomberg_data.py), if that file exists. User-confirmed live,
2026-09-02: /cusip/{cusip} Equity resolves via BDP, and PARSEKYABLE_DES
(field DS587) returns the full identifier ("NVDA US Equity") for it.
This is deliberately a fallback, not primary -- edgartools is free and
needs no Bloomberg session at all; reserve the Bloomberg round-trip for
names edgartools' bundled dataset actually misses (recent ticker
changes, thin small-caps). The ticker is parsed as the first
whitespace-delimited token of the identifier -- correct for the
ordinary "TICKER US Equity" case; a multi-part ticker (e.g. a share
class using a slash) would need a smarter split, not attempted here.
"""
import json
from pathlib import Path
from edgar.reference import get_ticker_from_cusip

INPUT_FILE = "data/classified_rows.json"
MARKET_DATA_FILE = "data/market_data.json"
OUTPUT_FILE = "data/security_master.json"


def resolve_all(rows):
    """Returns {cusip: {"ticker": ..., "source": "edgartools"|"bloomberg"|None}},
    one lookup per distinct CUSIP. Tries edgartools first (free, offline);
    falls back to a Bloomberg-derived market_data.json only for whatever
    edgartools couldn't resolve, and only if that file exists."""
    distinct_cusips = sorted({r["cusip"] for r in rows})
    result = {}
    for cusip in distinct_cusips:
        try:
            ticker = get_ticker_from_cusip(cusip)
        except Exception as e:
            print(f"WARNING: edgartools lookup failed for {cusip}: {e}")
            ticker = None
        result[cusip] = {"ticker": ticker, "source": "edgartools" if ticker else None}

    still_missing = [c for c, v in result.items() if v["ticker"] is None]
    if still_missing and Path(MARKET_DATA_FILE).exists():
        with open(MARKET_DATA_FILE) as f:
            market_data = json.load(f)
        bbg_by_cusip = {r["cusip"]: r for r in market_data}

        for cusip in still_missing:
            bbg_record = bbg_by_cusip.get(cusip)
            if not bbg_record:
                continue
            identifier = bbg_record.get("PARSEKYABLE_DES")
            if bbg_record.get("PARSEKYABLE_DES_status") != "PASS" or not identifier:
                continue
            ticker = identifier.split()[0]
            result[cusip] = {"ticker": ticker, "source": "bloomberg"}

    return result


if __name__ == "__main__":
    with open(INPUT_FILE) as f:
        rows = json.load(f)

    mapping = resolve_all(rows)

    from_edgartools = {c: v for c, v in mapping.items() if v["source"] == "edgartools"}
    from_bloomberg = {c: v for c, v in mapping.items() if v["source"] == "bloomberg"}
    unresolved = [c for c, v in mapping.items() if v["source"] is None]

    print(f"{len(mapping)} distinct CUSIPs: {len(from_edgartools)} via edgartools, "
          f"{len(from_bloomberg)} via Bloomberg fallback, {len(unresolved)} unresolved")
    if from_bloomberg:
        print("\nResolved via Bloomberg fallback (edgartools missed these):")
        for c, v in from_bloomberg.items():
            print(f"  {c}  -> {v['ticker']}")
    if unresolved:
        # Cross-reference against issuer name for anything unresolved,
        # so a human reviewing this doesn't have to go back to the raw
        # filing to know what CUSIP X even is.
        name_by_cusip = {r["cusip"]: r["nameOfIssuer"] for r in rows}
        print("\nUnresolved by either source (expected for non-US, delisted, "
              "or thinly covered securities -- e.g. many small warrants; "
              "run the Bloomberg export/import round trip first if you "
              "haven't, since that fallback only applies if "
              f"{MARKET_DATA_FILE} already exists):")
        for c in unresolved:
            print(f"  {c}  {name_by_cusip.get(c, '?')}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(mapping, f, indent=2)
    print(f"\nWrote {OUTPUT_FILE}")
