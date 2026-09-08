"""
corporate_actions.py -- Resolves CHECK 4 (cross-quarter price continuity)
REVIEW flags using price_verify.py's independent historical-price checks.

This is the piece that was missing: check4_price_continuity.csv and
price_verification.csv both existed and were individually correct, but
nothing read the second to resolve the first. A >80% cross-quarter
implied-price move is an ANOMALY TRIGGER (check 4's job), not a
conclusion -- this script is the resolution (check 9's job).

Resolution logic:

    Both OLD and NEW sides independently verify (PASS in price_verify)
        -> PASS_CORPORATE_ACTION
        Both numbers are individually correct against their own
        period's market close. The divergence between them reflects
        a real market or corporate event (split, spinoff, etc.), not
        a parsing error.

    Either side fails to verify
        -> REVIEW_MARKET_DATA
        At least one side could not be independently confirmed. This
        may still be a parsing error, ticker mismatch, value-scaling
        issue, or genuine data gap. Needs a human.

    Either side is a warrant (NOT_APPLICABLE in price_verify)
        -> REVIEW_SECURITY_MAPPING
        Common-equity corporate-action resolution doesn't apply to
        warrants; review manually.

Never modifies an SEC-reported value. This only assigns a resolution
status to the existing check4 row, alongside the reasoning, so a human
reviewing the output sees both the anomaly and how it was investigated
-- not just a final verdict.

Cross-references resolution_log.py: any REVIEW_MARKET_DATA or
REVIEW_SECURITY_MAPPING row is checked against the resolution log
before being presented as needing attention. A prior APPROVE or
CORRECT closes it out of the "still needs review" list (though it
stays in the CSV output, tagged with HumanResolution, for audit).
A prior ESCALATE stays visible but is labeled as previously escalated,
not presented as a fresh flag no one has looked at.

Usage: python corporate_actions.py <fund_name>
Reads:  <fund_name>_integrity/check4_price_continuity.csv
        <fund_name>_price_verify/<fund_name>_price_verification.csv
        data/resolution_log.jsonl (if it exists)
Writes: <fund_name>_integrity/check4_resolved.csv
"""
import sys
import pandas as pd
from pathlib import Path

from resolution_log import make_exception_id, get_resolution

FUND_NAME = sys.argv[1] if len(sys.argv) > 1 else "fund"

CHECK4_FILE = Path(f"{FUND_NAME}_integrity/check4_price_continuity.csv")
PRICE_VERIFY_FILE = Path(f"{FUND_NAME}_price_verify/{FUND_NAME}_price_verification.csv")
OUTPUT_DIR = Path(f"{FUND_NAME}_integrity")
OUTPUT_FILE = OUTPUT_DIR / "check4_resolved.csv"

for path in (CHECK4_FILE, PRICE_VERIFY_FILE):
    if not path.exists():
        raise FileNotFoundError(
            f"Missing input file: {path}\n"
            f"Run integrity.py then price_verify.py for '{FUND_NAME}' first."
        )

check4 = pd.read_csv(CHECK4_FILE)
verify = pd.read_csv(PRICE_VERIFY_FILE)

# Only REVIEW rows need resolution -- rows that passed check 4 directly
# (no >80% move) already have everything downstream needs.
to_resolve = check4[check4["Status"] == "REVIEW"].copy()
already_passed = check4[check4["Status"] == "PASS"].copy()

resolved_rows = []

for _, row in to_resolve.iterrows():
    transition = f"{row['OldQuarter']}_to_{row['NewQuarter']}"
    cusip = row["Cusip"]

    match = verify[(verify["Transition"] == transition) & (verify["Cusip"] == cusip)]
    old_match = match[match["QuarterType"] == "OLD"]
    new_match = match[match["QuarterType"] == "NEW"]

    if old_match.empty or new_match.empty:
        resolved_status = "REVIEW_MARKET_DATA"
        reason = (
            "No matching price-verification record for one or both sides "
            "of this transition. Run price_verify.py against "
            "check4_price_continuity.csv first."
        )
    else:
        old_status = old_match.iloc[0]["Status"]
        new_status = new_match.iloc[0]["Status"]

        if old_status == "NOT_APPLICABLE" or new_status == "NOT_APPLICABLE":
            resolved_status = "REVIEW_SECURITY_MAPPING"
            reason = (
                "Warrant on one or both sides of this transition. "
                "Common-equity corporate-action resolution does not "
                "apply; review manually."
            )
        elif old_status == "PASS" and new_status == "PASS":
            resolved_status = "PASS_CORPORATE_ACTION"
            reason = (
                "Both OLD and NEW implied prices independently "
                "reconcile to their own period's historical close. "
                "The cross-quarter change reflects a real market or "
                "corporate event, not a parsing error."
            )
        else:
            failing_side = "OLD" if old_status != "PASS" else "NEW"
            resolved_status = "REVIEW_MARKET_DATA"
            reason = (
                f"{failing_side} side did not independently reconcile to "
                "its historical close. May still be a parsing error, "
                "ticker mismatch, value-scaling issue, or genuine data "
                "gap -- needs manual review."
            )

    resolved_rows.append({**row.to_dict(), "ResolvedStatus": resolved_status,
                           "ResolutionReason": reason})

# Cross-reference every REVIEW-type row against the resolution log --
# a human decision recorded on a prior run should never be presented
# as a fresh, unaddressed flag. Exception ID is transition + cusip,
# since that's what uniquely identifies a check-4 flag regardless of
# which run produced it.
for row in resolved_rows:
    if row["ResolvedStatus"] not in ("REVIEW_MARKET_DATA", "REVIEW_SECURITY_MAPPING"):
        row["ExceptionId"] = None
        row["HumanResolution"] = None
        continue
    transition = f"{row['OldQuarter']}_to_{row['NewQuarter']}"
    exception_id = make_exception_id(FUND_NAME, transition, "check4", row["Cusip"])
    row["ExceptionId"] = exception_id
    resolution = get_resolution(exception_id)
    row["HumanResolution"] = (
        f"{resolution['decision']} by {resolution['reviewer']} at {resolution['timestamp']}"
        + (f" -- {resolution['note']}" if resolution.get("note") else "")
    ) if resolution else None

resolved_df = pd.DataFrame(resolved_rows) if resolved_rows else pd.DataFrame(
    columns=list(check4.columns) + ["ResolvedStatus", "ResolutionReason"]
)

already_passed["ResolvedStatus"] = "PASS"
already_passed["ResolutionReason"] = (
    "Within cross-quarter continuity threshold; no resolution needed."
)
already_passed["ExceptionId"] = None
already_passed["HumanResolution"] = None

final_df = pd.concat([resolved_df, already_passed], ignore_index=True)
final_df.to_csv(OUTPUT_FILE, index=False)

print("=" * 80)
print(f"{FUND_NAME.upper()} CHECK 4 RESOLUTION (via independent price verification)")
print("=" * 80)
print(f"\n{len(check4)} total transitions")
print(f"{len(already_passed)} passed check 4 directly (no >80% move)")
print(f"{len(to_resolve)} required resolution")
print()
if not final_df.empty:
    print(final_df["ResolvedStatus"].value_counts().to_string())

review_type = final_df[final_df["ResolvedStatus"].isin(["REVIEW_MARKET_DATA", "REVIEW_SECURITY_MAPPING"])]
already_closed = review_type[review_type["HumanResolution"].notna()
                              & ~review_type["HumanResolution"].str.startswith("ESCALATE", na=False)]
still_open = review_type[review_type["HumanResolution"].isna()]
escalated = review_type[review_type["HumanResolution"].str.startswith("ESCALATE", na=False)]

if not already_closed.empty:
    print(f"\n{len(already_closed)} REVIEW item(s) already closed by a prior human "
          f"decision -- not re-surfaced below. See {OUTPUT_FILE.name} for the full "
          f"record, including HumanResolution.")

if not still_open.empty:
    print("\n" + "=" * 80)
    print("STILL NEEDS HUMAN REVIEW (independent verification could not confirm, "
          "no prior decision recorded)")
    print("=" * 80)
    cols = ["OldQuarter", "NewQuarter", "Ticker", "Cusip", "OldImpliedPrice",
            "NewImpliedPrice", "PriceChangePct", "ResolutionReason", "ExceptionId"]
    print(still_open[cols].to_string(index=False))
    print(f"\nTo record a decision: python resolution_log.py resolve <ExceptionId> "
          f"<APPROVE|CORRECT|ESCALATE> <your name> [\"note\"]")

if not escalated.empty:
    print("\n" + "=" * 80)
    print("PREVIOUSLY ESCALATED -- still open, not a fresh flag")
    print("=" * 80)
    for _, r in escalated.iterrows():
        print(f"  {r['Cusip']}  {r['OldQuarter']}->{r['NewQuarter']}: {r['HumanResolution']}")

print(f"\nOutput: {OUTPUT_FILE.resolve()}")
