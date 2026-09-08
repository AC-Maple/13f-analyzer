"""
test_yfinance_fallback.py -- Standalone test, NOT part of the main
pipeline. Probes what yfinance can actually provide as a free fallback
for when Bloomberg isn't available -- price, shares outstanding, average
volume (both windows), market cap, and sector/industry -- against the
same 3 known-answer securities used for the Bloomberg GICS test, for
direct comparability.

Run this locally (wherever the rest of this pipeline runs) -- Yahoo
Finance's endpoints are not reachable from Claude's sandbox, confirmed
directly by trying: both yf.Ticker.info and yf.Ticker.history() route
through query1/query2.finance.yahoo.com, neither reachable from there.

Real, structural difference from Bloomberg worth remembering while
reading the output: yfinance has NO CUSIP lookup, ticker only. This
script uses tickers directly (CYTK, BSX, SBUX) because they're already
known -- a real fallback pipeline would need security_master.py's
CUSIP->ticker resolution to run FIRST, unconditionally, not as an
optional fallback the way it is today.

VOLUME METHODOLOGY -- deliberately does NOT trust yfinance's own
"averageVolume" / "averageVolume10days" fields at face value. Their
exact windowing (trading days vs calendar days, which end date) isn't
documented clearly enough to assume it matches Bloomberg's
VOLUME_AVG_20D / VOLUME_AVG_3M definitions. Instead, pulls raw daily
volume via .history() and computes genuine 20-trading-day and
63-trading-day (~3 calendar months of trading days) averages directly
-- same logic this pipeline already trusts, just computed by hand
instead of assumed from a pre-aggregated field. Both the raw .info
fields AND the manually-computed ones are printed, so the two can be
compared directly rather than guessing which is right.
"""
import json

try:
    import yfinance as yf
except ImportError:
    print("yfinance not installed. Run: pip install yfinance --break-system-packages")
    raise SystemExit(1)

TEST_SECURITIES = [
    ("CYTK", "CYTOKINETICS INC", "pure biotech"),
    ("BSX", "BOSTON SCIENTIFIC CORP", "diagnostics/med-device ambiguity"),
    ("SBUX", "STARBUCKS CORP", "restaurant"),
]

results = []

for ticker, name, note in TEST_SECURITIES:
    print(f"\n{'='*70}\n{name} ({ticker}) -- {note}\n{'='*70}")
    row = {"ticker": ticker, "name": name}

    t = yf.Ticker(ticker)

    # ---- .info dict: price, shares out, market cap, sector, industry,
    # and whatever pre-aggregated volume fields it happens to expose ----
    try:
        info = t.info
        fields_to_check = [
            "currentPrice", "regularMarketPrice",       # price -- yfinance has used both names across versions
            "sharesOutstanding", "marketCap",
            "averageVolume", "averageVolume10days", "averageDailyVolume10Day",  # exact set varies by version -- print whichever exist
            "sector", "industry",
        ]
        for f in fields_to_check:
            v = info.get(f)
            row[f"info.{f}"] = v
            print(f"  info.{f:30s} = {v}")
        if not any(info.get(f) for f in fields_to_check):
            print("  WARNING: .info returned no usable fields at all -- possible rate limit or blocked request")
    except Exception as e:
        print(f"  .info FAILED: {e}")
        row["info_error"] = str(e)

    # ---- Manually computed 20-day / 63-day average volume from raw
    # daily history, independent of whatever .info claims ----
    try:
        hist = t.history(period="4mo")  # comfortably more than 63 trading days
        if hist.empty:
            print("  history() returned no rows")
        else:
            # Exclude a possibly-partial current trading day before
            # computing anything -- if this runs while the market is
            # still open, the last row is volume-so-far, not a full
            # day's total, and would drag a short window down more
            # than a long one. A prior run showed exactly that pattern
            # (20-day average understated by 6-12%, 63-day only 0.5-3.5%)
            # -- this is the concrete hypothesis for why, being tested
            # directly rather than left unexplained.
            import datetime
            today = datetime.datetime.now().date()
            last_row_date = hist.index[-1].date()
            excluded_partial_day = False
            if last_row_date == today:
                hist = hist.iloc[:-1]
                excluded_partial_day = True

            vol = hist["Volume"]
            adv_20d = vol.tail(20).mean()
            adv_63d = vol.tail(63).mean()
            row["computed_adv_20d"] = round(adv_20d, 0)
            row["computed_adv_63d"] = round(adv_63d, 0)
            row["history_rows"] = len(hist)
            row["excluded_partial_current_day"] = excluded_partial_day
            row["last_close"] = round(hist["Close"].iloc[-1], 2)
            row["last_date"] = str(hist.index[-1].date())
            print(f"  excluded partial current-day row: {excluded_partial_day}")
            print(f"  computed 20-trading-day avg volume  = {adv_20d:,.0f}  (from {len(hist)} rows of history)")
            print(f"  computed 63-trading-day avg volume  = {adv_63d:,.0f}")
            print(f"  last close = ${hist['Close'].iloc[-1]:.2f}  as of {hist.index[-1].date()}")
    except Exception as e:
        print(f"  history() FAILED: {e}")
        row["history_error"] = str(e)

    results.append(row)

print(f"\n{'='*70}\nRAW JSON (for reporting back)\n{'='*70}")
print(json.dumps(results, indent=2, default=str))
