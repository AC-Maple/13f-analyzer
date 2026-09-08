"""
import_bloomberg_data.py -- Reads the refreshed Bloomberg workbook back
in and produces a clean market-data file for price_verify.py / liquidity.py.

Read with load_workbook(data_only=True). This ONLY works on a file that
was actually opened and refreshed in real Excel with the Bloomberg
Add-in -- that's what leaves cached values behind for the formula cells.
A file passed through openpyxl/LibreOffice without ever touching a
Bloomberg session reads back as None everywhere (see xlsx skill notes on
data_only + recalc).

Bloomberg writes literal error TEXT into a cell when a lookup fails --
it does not leave the cell blank and does not raise. These strings must
be caught explicitly or they get treated as data:
  #N/A Invalid Security   -- identifier didn't resolve (bad CUSIP, no
                              Bloomberg coverage -- common for OTC
                              warrants and thinly-covered small caps)
  #N/A Field Not Applicable -- security exists but this field doesn't
                              apply to it (e.g. EQY_SH_OUT on some
                              structures)
  #N/A Requesting Data    -- the Add-in hadn't finished refreshing when
                              the file was saved; re-open and re-save
Never treat any of these as zero, blank, or "no position" -- they mean
"the market-data layer has nothing for this security," which is a
PENDING_EXTERNAL_DATA / REVIEW state, not a clean zero.

Cross-references resolution_log.py for the "no PX_LAST at all" case
specifically -- this is the one that fully excludes a security from
liquidity.py's ADV model, so it's the one worth a recorded human
decision, not every PENDING_EXTERNAL_DATA field individually (a
warrant's blank VOLUME_AVG_3M, for instance, is expected by design and
not worth a resolution-log entry). Without this, a name with genuinely
no Bloomberg coverage re-surfaces identically on every future import,
with no way to record "yes, checked, this one just isn't covered."
Usage: python import_bloomberg_data.py <refreshed_file.xlsx> [fund_name]
"""
import json
import re
import sys
from openpyxl import load_workbook

from resolution_log import make_exception_id, get_resolution, derive_quarter_label

INPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else "bloomberg_template.xlsx"
FUND_NAME = sys.argv[2] if len(sys.argv) > 2 else "fund"
OUTPUT_FILE = "data/market_data.json"

BLOOMBERG_ERROR_PATTERN = re.compile(r"^#N/A", re.IGNORECASE)

# (column, expected_type) -- PARSEKYABLE_DES is a string identifier
# ("NVDA US Equity"), not a number, and needs different validation than
# the five numeric market-data fields. Both /cusip/ identifiers and all
# six fields below are user-confirmed against a live Bloomberg session,
# 2026-09-02.
#
# GICS_INDUSTRY_NAME / GICS_SUB_INDUSTRY_NAME: string fields, same
# shape and same classify_cell() handling as PARSEKYABLE_DES -- a
# genuine GICS name ("Biotechnology") is expected valid text, so it
# can't be numerically sanity-checked the way PX_LAST is, but a blank
# cell or a Bloomberg error string ("#N/A Invalid Security", etc.)
# still runs through the same string branch below and comes back
# PENDING_EXTERNAL_DATA rather than being silently accepted as if it
# were a real sector name. Mnemonics live-confirmed against a real
# Bloomberg Terminal refresh, 2026-09-08 -- see SKILL.md's "Sector
# classification field verification (GICS, live-tested)" section.
# Not yet confirmed specifically through THIS script's per-CUSIP
# /cusip/ template at scale -- see SKILL.md's "Sector concentration
# wired into the pipeline" section for what that gap actually is and
# the bug it surfaced when tested with synthetic data in its place.
FIELD_COLUMNS = {
    "PX_LAST": (4, "numeric"),
    "EQY_SH_OUT": (5, "numeric"),
    "CUR_MKT_CAP": (6, "numeric"),
    "VOLUME_AVG_20D": (7, "numeric"),
    "VOLUME_AVG_3M": (8, "numeric"),
    "PARSEKYABLE_DES": (9, "string"),
    "GICS_INDUSTRY_NAME": (10, "string"),
    "GICS_SUB_INDUSTRY_NAME": (11, "string"),
}
HEADER_ROW = 4


def classify_cell(value, expected_type):
    """Returns (clean_value, status). status is PASS, PENDING_EXTERNAL_DATA
    (Bloomberg error or genuinely blank), NOT_APPLICABLE (warrant ADV,
    by design), or REVIEW_MARKET_DATA (a value that parsed but looks
    structurally wrong for its expected type)."""
    if value is None:
        return None, "PENDING_EXTERNAL_DATA"

    if isinstance(value, str):
        if BLOOMBERG_ERROR_PATTERN.match(value.strip()):
            return None, "PENDING_EXTERNAL_DATA"
        if value.strip().upper() in ("N/A -- WARRANT, NO ADV MODEL",):
            return None, "NOT_APPLICABLE"
        if expected_type == "string":
            # A real Bloomberg identifier, e.g. "NVDA US Equity" --
            # this is the expected, valid shape for this field.
            if value.strip():
                return value.strip(), "PASS"
            return None, "PENDING_EXTERNAL_DATA"
        # A stray string in a NUMERIC field is unexpected -- never
        # coerce it silently.
        return None, "REVIEW_MARKET_DATA"

    if isinstance(value, (int, float)):
        if expected_type == "string":
            # Bloomberg identifiers should never come back numeric.
            return None, "REVIEW_MARKET_DATA"
        if value < 0:
            return value, "REVIEW_MARKET_DATA"
        return value, "PASS"

    return None, "REVIEW_MARKET_DATA"


wb = load_workbook(INPUT_FILE, data_only=True)
ws = wb.active

results = []
for row_num in range(HEADER_ROW + 1, ws.max_row + 1):
    # Addressed by (row, column) via ws.cell(), not by indexing into the
    # row tuple from iter_rows() -- that tuple is only as wide as
    # openpyxl thinks the sheet's used range is, which can be narrower
    # than max(FIELD_COLUMNS) on a workbook exported before a new
    # column existed (e.g. a pre-GICS bloomberg_template.xlsx re-run
    # through a newer FIELD_COLUMNS). ws.cell() on a column past the
    # sheet's populated range just returns an empty cell (value=None),
    # which classify_cell already treats as PENDING_EXTERNAL_DATA --
    # exactly the right outcome for "this workbook predates this
    # field," not a crash.
    cusip_val = ws.cell(row=row_num, column=2).value
    if cusip_val in (None, ""):
        continue
    cusip = str(cusip_val).strip()
    issuer = ws.cell(row=row_num, column=1).value

    record = {"cusip": cusip, "issuer": issuer}
    for field, (col_idx, expected_type) in FIELD_COLUMNS.items():
        cell = ws.cell(row=row_num, column=col_idx)
        clean_value, status = classify_cell(cell.value, expected_type)
        record[field] = clean_value
        record[f"{field}_status"] = status
    results.append(record)

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"Read {len(results)} securities from {INPUT_FILE}")

all_statuses = [record[f"{field}_status"] for record in results for field in FIELD_COLUMNS]
pending = sum(1 for s in all_statuses if s == "PENDING_EXTERNAL_DATA")
review = sum(1 for s in all_statuses if s == "REVIEW_MARKET_DATA")
na = sum(1 for s in all_statuses if s == "NOT_APPLICABLE")
passed = sum(1 for s in all_statuses if s == "PASS")
print(f"  {passed} field values PASS")
print(f"  {pending} PENDING_EXTERNAL_DATA (Bloomberg error or blank -- no coverage or not yet refreshed)")
print(f"  {review} REVIEW_MARKET_DATA (unexpected value -- needs a look)")
print(f"  {na} NOT_APPLICABLE (warrant ADV, as expected)")

flagged = [r for r in results if any(
    r[f"{field}_status"] == "PENDING_EXTERNAL_DATA" for field in ("PX_LAST",)
)]

if flagged:
    # Derive quarter the same way every other producer does -- from
    # classified_rows.json's row metadata if it exists (it will, in the
    # normal pipeline order: classify runs before this step). Falls
    # back to a warned placeholder, never a silent guess.
    try:
        with open("data/classified_rows.json") as f:
            classified_rows = json.load(f)
    except FileNotFoundError:
        classified_rows = []
    QUARTER = derive_quarter_label(classified_rows)

    for r in flagged:
        r["exception_id"] = make_exception_id(FUND_NAME, QUARTER, "bloombergcoverage", r["cusip"])
        resolution = get_resolution(r["exception_id"])
        r["human_resolution"] = (
            f"{resolution['decision']} by {resolution['reviewer']} at {resolution['timestamp']}"
            + (f" -- {resolution['note']}" if resolution.get("note") else "")
        ) if resolution else None

    still_open = [r for r in flagged if not r["human_resolution"]]
    resolved = [r for r in flagged if r["human_resolution"]]

    print(f"\n{len(flagged)} securities have no PX_LAST at all -- likely no Bloomberg "
          f"coverage or the file wasn't refreshed before saving:")
    for r in still_open:
        print(f"    {r['cusip']}  {r['issuer']}  [{r['exception_id']}]")
    for r in resolved:
        print(f"    {r['cusip']}  {r['issuer']}  -- {r['human_resolution']}")
    if resolved:
        print(f"\n{len(resolved)} previously resolved -- not fresh flags.")
    if still_open:
        print(f"\n{len(still_open)} need a decision:")
        print(f"  python resolution_log.py resolve <exception_id> <APPROVE|CORRECT|ESCALATE> <your name> [\"note\"]")

print(f"\nWrote {OUTPUT_FILE}")
