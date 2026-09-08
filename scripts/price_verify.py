import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
import time

# =========================================================
# 13F HISTORICAL PRICE VERIFICATION (fund-agnostic)
#
# Purpose:
#   Compare SEC 13F implied price:
#
#       reported_value / reported_shares
#
#   against an independent historical market close.
#
# Important:
#   - SEC data is never modified.
#   - Yahoo/yfinance is an independent validation source only.
#   - This is NOT yet the production market-data layer.
#   - Use raw "Close", not "Adj Close" (auto_adjust=False below).
#     13F implied price is unadjusted-as-of-report-date; an
#     adjusted close would disagree by the split factor for any
#     name with a split after the report date -- precisely the
#     population check 4 flags, which would make this layer
#     manufacture the anomalies it exists to resolve.
#
# Set FUND_NAME per run (or pass as sys.argv[1]). Everything else
# derives from it, so this script doesn't need per-fund edits.
# =========================================================

import sys

FUND_NAME = sys.argv[1] if len(sys.argv) > 1 else "fund"

INPUT_FILE = Path(
    f"{FUND_NAME}_integrity/check4_price_continuity.csv"
)

OUTPUT_DIR = Path(
    f"{FUND_NAME}_price_verify"
)

OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = (
    OUTPUT_DIR /
    f"{FUND_NAME}_price_verification.csv"
)

REVIEW_FILE = (
    OUTPUT_DIR /
    f"{FUND_NAME}_price_verification_review.csv"
)

# =========================================================
# CONFIGURATION
# =========================================================

# Maximum acceptable difference before manual review.
#
# A 1% tolerance is intentionally conservative.
# SEC reported values and historical market closes can differ
# slightly because of valuation methodology, rounding, timing,
# and data-provider conventions.
#
# We DO NOT automatically "fix" anything outside the tolerance.
TOLERANCE_PCT = 1.0

# Number of calendar days around the report date to request.
# 5 is sufficient for normal weekends/holidays.
LOOKAROUND_DAYS = 5

# Delay between symbols to be polite to the data provider.
REQUEST_DELAY_SECONDS = 0.5


# =========================================================
# LOAD INPUT
# =========================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Missing input file: {INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "OldQuarter",
    "NewQuarter",
    "Ticker",
    "Cusip",
    "SecurityType",
    "OldImpliedPrice",
    "NewImpliedPrice",
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        "Input file is missing required columns: "
        + ", ".join(missing_columns)
    )


# =========================================================
# BUILD VERIFICATION TASKS
#
# We verify BOTH sides of each flagged transition:
#
#   OldQuarter implied price → historical close
#   NewQuarter implied price → historical close
#
# This gives us an independent check on both observations.
# =========================================================

tasks = []

for _, row in df.iterrows():

    for quarter_type, date_column, price_column in [
        (
            "OLD",
            "OldQuarter",
            "OldImpliedPrice",
        ),
        (
            "NEW",
            "NewQuarter",
            "NewImpliedPrice",
        ),
    ]:

        tasks.append({
            "Transition": (
                f"{row['OldQuarter']}"
                f"_to_"
                f"{row['NewQuarter']}"
            ),
            "QuarterType": quarter_type,
            "ReportDate": row[date_column],
            "Ticker": str(row["Ticker"]).strip().upper(),
            "Cusip": str(row["Cusip"]).strip().upper(),
            "SecurityType": row["SecurityType"],
            "SEC_ImpliedPrice": row[price_column],
        })

tasks_df = pd.DataFrame(tasks)


# =========================================================
# HISTORICAL PRICE FUNCTION
# =========================================================

def get_historical_close(ticker, report_date):
    """
    Retrieve the historical market close nearest to the
    requested SEC reporting date.

    Uses yfinance historical daily data.

    Returns:
        {
            "MarketDate": ...,
            "Close": ...,
            "ExactDateMatch": ...,
            "Status": ...
        }
    """

    report_dt = pd.Timestamp(report_date)

    start = (
        report_dt
        - pd.Timedelta(days=LOOKAROUND_DAYS)
    )

    end = (
        report_dt
        + pd.Timedelta(days=LOOKAROUND_DAYS + 1)
    )

    try:

        history = yf.Ticker(ticker).history(
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            interval="1d",
            auto_adjust=False,
            actions=True,
            repair=True,
        )

    except Exception as exc:

        return {
            "MarketDate": None,
            "Close": None,
            "ExactDateMatch": False,
            "Status": (
                "MARKET_DATA_ERROR: "
                + str(exc)
            ),
        }

    if history.empty:

        return {
            "MarketDate": None,
            "Close": None,
            "ExactDateMatch": False,
            "Status": "NO_MARKET_DATA",
        }

    # -----------------------------------------------------
    # Normalize index
    # -----------------------------------------------------

    history = history.copy()

    if getattr(history.index, "tz", None) is not None:

        history.index = (
            history.index
            .tz_localize(None)
        )

    history.index = pd.to_datetime(
        history.index
    ).normalize()

    # -----------------------------------------------------
    # Find exact date if available
    # -----------------------------------------------------

    exact = history[
        history.index == report_dt.normalize()
    ]

    if not exact.empty:

        market_date = exact.index[0]
        close = exact["Close"].iloc[0]

        return {
            "MarketDate": market_date.date().isoformat(),
            "Close": float(close),
            "ExactDateMatch": True,
            "Status": "EXACT_DATE",
        }

    # -----------------------------------------------------
    # If date is not a trading day, use nearest prior
    # trading date.
    # -----------------------------------------------------

    prior = history[
        history.index < report_dt.normalize()
    ]

    if not prior.empty:

        market_date = prior.index[-1]
        close = history.loc[
            market_date,
            "Close"
        ]

        return {
            "MarketDate": market_date.date().isoformat(),
            "Close": float(close),
            "ExactDateMatch": False,
            "Status": "PRIOR_TRADING_DATE",
        }

    # -----------------------------------------------------
    # No prior date available; use nearest available date.
    # -----------------------------------------------------

    market_date = history.index[0]
    close = history.loc[
        market_date,
        "Close"
    ]

    return {
        "MarketDate": market_date.date().isoformat(),
        "Close": float(close),
        "ExactDateMatch": False,
        "Status": "NEAREST_AVAILABLE_DATE",
    }


# =========================================================
# VERIFY EACH TASK
# =========================================================

results = []

print("=" * 100)
print(f"{FUND_NAME.upper()} 13F HISTORICAL PRICE VERIFICATION")
print("=" * 100)

print(
    f"\nInput: {INPUT_FILE}"
)

print(
    f"Tolerance: ±{TOLERANCE_PCT:.2f}%"
)

print(
    "\nMarket-data source: Yahoo Finance via yfinance"
)

print(
    "Price field: Close (not Adj Close)"
)

print(
    "\nIMPORTANT: This is an independent validation layer, "
    "not the eventual production market-data source."
)

print("\n")


for number, task in enumerate(
    tasks,
    start=1
):

    ticker = task["Ticker"]
    report_date = task["ReportDate"]
    sec_price = task["SEC_ImpliedPrice"]

    print(
        f"[{number}/{len(tasks)}] "
        f"{ticker} | "
        f"{report_date} | "
        f"{task['QuarterType']}"
    )

    # -----------------------------------------------------
    # Validate SEC price
    # -----------------------------------------------------

    if (
        pd.isna(sec_price)
        or float(sec_price) <= 0
    ):

        results.append({
            **task,
            "MarketDate": None,
            "HistoricalClose": None,
            "ExactDateMatch": False,
            "DifferencePct": None,
            "Status": "REVIEW",
            "Resolution": (
                "Invalid or missing SEC implied price."
            ),
        })

        continue

    # -----------------------------------------------------
    # Skip warrants from this common-stock price test.
    # -----------------------------------------------------

    if task["SecurityType"] == "WARRANT":

        results.append({
            **task,
            "MarketDate": None,
            "HistoricalClose": None,
            "ExactDateMatch": False,
            "DifferencePct": None,
            "Status": "NOT_APPLICABLE",
            "Resolution": (
                "Warrant. Common-equity historical "
                "price verification does not apply."
            ),
        })

        continue

    # -----------------------------------------------------
    # Retrieve market close
    # -----------------------------------------------------

    market = get_historical_close(
        ticker,
        report_date
    )

    market_close = market["Close"]

    if (
        market_close is None
        or pd.isna(market_close)
    ):

        results.append({
            **task,
            "MarketDate": market["MarketDate"],
            "HistoricalClose": None,
            "ExactDateMatch": market["ExactDateMatch"],
            "DifferencePct": None,
            "Status": "REVIEW",
            "Resolution": market["Status"],
        })

        continue

    # -----------------------------------------------------
    # Calculate difference
    # -----------------------------------------------------

    difference_pct = (
        (
            float(sec_price)
            - float(market_close)
        )
        / float(market_close)
        * 100
    )

    absolute_difference_pct = abs(
        difference_pct
    )

    # -----------------------------------------------------
    # Resolve
    # -----------------------------------------------------

    if (
        absolute_difference_pct
        <= TOLERANCE_PCT
    ):

        status = "PASS"

        if market["ExactDateMatch"]:

            resolution = (
                "SEC implied price reconciles "
                "to exact reporting-date market close."
            )

        else:

            resolution = (
                "SEC implied price reconciles "
                "to prior trading-date market close."
            )

    else:

        status = "REVIEW"

        resolution = (
            "SEC implied price differs from "
            "independent historical close by more "
            f"than {TOLERANCE_PCT:.2f}%. "
            "Investigate corporate action, ticker mapping, "
            "value scaling, share count, timing, or "
            "market-data convention."
        )

    results.append({
        **task,
        "MarketDate": market["MarketDate"],
        "HistoricalClose": market_close,
        "ExactDateMatch": market["ExactDateMatch"],
        "DifferencePct": difference_pct,
        "Status": status,
        "Resolution": resolution,
    })

    time.sleep(
        REQUEST_DELAY_SECONDS
    )


# =========================================================
# RESULTS DATAFRAME
# =========================================================

results_df = pd.DataFrame(results)

# Sort for readability
results_df = results_df.sort_values(
    [
        "ReportDate",
        "Ticker",
        "QuarterType",
    ]
).reset_index(drop=True)


# =========================================================
# SAVE COMPLETE RESULTS
# =========================================================

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# SAVE REVIEW ITEMS
# =========================================================

review_df = results_df[
    results_df["Status"] == "REVIEW"
].copy()

review_df.to_csv(
    REVIEW_FILE,
    index=False
)


# =========================================================
# TERMINAL SUMMARY
# =========================================================

print("\n" + "=" * 100)
print("VERIFICATION SUMMARY")
print("=" * 100)

status_counts = (
    results_df["Status"]
    .value_counts()
)

for status, count in status_counts.items():

    print(
        f"{status:<20} {count}"
    )

print(
    f"\nTotal observations: {len(results_df)}"
)

print(
    f"Passed: "
    f"{(results_df['Status'] == 'PASS').sum()}"
)

print(
    f"Review: "
    f"{(results_df['Status'] == 'REVIEW').sum()}"
)

print(
    f"Not applicable: "
    f"{(results_df['Status'] == 'NOT_APPLICABLE').sum()}"
)


# =========================================================
# SHOW REVIEW ITEMS
# =========================================================

print("\n" + "=" * 100)
print("REVIEW ITEMS")
print("=" * 100)

if review_df.empty:

    print(
        "\nNo price-verification review items."
    )

else:

    display_columns = [
        "ReportDate",
        "Ticker",
        "Cusip",
        "QuarterType",
        "SecurityType",
        "SEC_ImpliedPrice",
        "MarketDate",
        "HistoricalClose",
        "DifferencePct",
        "Status",
        "Resolution",
    ]

    print(
        review_df[
            display_columns
        ].to_string(index=False)
    )


# =========================================================
# SHOW PASS ITEMS
# =========================================================

print("\n" + "=" * 100)
print("PASSED PRICE VERIFICATIONS")
print("=" * 100)

pass_df = results_df[
    results_df["Status"] == "PASS"
]

if pass_df.empty:

    print(
        "\nNo observations passed."
    )

else:

    display_columns = [
        "ReportDate",
        "Ticker",
        "Cusip",
        "QuarterType",
        "SEC_ImpliedPrice",
        "MarketDate",
        "HistoricalClose",
        "DifferencePct",
    ]

    print(
        pass_df[
            display_columns
        ].to_string(index=False)
    )


# =========================================================
# OUTPUT
# =========================================================

print("\n" + "=" * 100)
print("OUTPUT FILES")
print("=" * 100)

print(
    f"Complete results:\n{OUTPUT_FILE.resolve()}"
)

print(
    f"\nReview-only results:\n{REVIEW_FILE.resolve()}"
)

print("\nVerification complete.")