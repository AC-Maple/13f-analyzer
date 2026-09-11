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
FIELD_COLUMNS = {
    "PX_LAST": (4, "numeric"),
    "EQY_SH_OUT": (5, "numeric"),
    "CUR_MKT_CAP": (6, "numeric"),
    "VOLUME_AVG_20D": (7, "numeric"),
    "VOLUME_AVG_3M": (8, "numeric"),
    "PARSEKYABLE_DES": (9, "string"),
    # Restored 2026-09-11 -- these two entries and the ws.cell()-based
    # row loop below (see the note there) were both silently dropped
    # when this file was rewritten for the liquidity_override feature,
    # reverting two already-shipped, already-verified fixes without
    # anyone deciding to. Found by testing against Melqart's real
    # refreshed workbook: it has real, populated GICS data for all 40
    # positions (confirmed by reading the raw cell values directly),
    # but zero of the 40 resulting market_data.json records carried a
    # GICS_INDUSTRY_NAME key at all until this was restored. GICS
    # mnemonics live-confirmed 2026-09-08 -- see SKILL.md's "Sector
    # classification field verification (GICS, live-tested)" section.
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
        if value == 0:
            # A genuine zero is implausible for every numeric field this
            # pipeline pulls (price, shares outstanding, market cap,
            # 20-day/3-month average volume) -- a real, currently-held
            # 13F position cannot have a $0 price or 0 shares outstanding,
            # and an actively-traded common stock cannot average literally
            # zero shares traded across an entire 20-day or 3-month window.
            # Found on real data (Melqart): Electronic Arts and Chart
            # Industries both showed VOLUME_AVG_20D=0 after a genuine,
            # deliberate live re-refresh (ruling out a stale/mid-calculation
            # read) -- while PX_LAST, PARSEKYABLE_DES, and other fields on
            # the same rows resolved correctly, so this wasn't a broader
            # identifier-resolution failure either. A 0 that PASSES here
            # was already silently distrusted downstream: compute_liquidity
            # (liquidity.py) has its own "adv <= 0" guard that treats it as
            # unusable regardless of this status -- meaning the status
            # field was claiming "trustworthy" for a value the rest of the
            # pipeline was already treating as worthless. That inconsistency
            # is the actual bug: a crash was never the risk (the downstream
            # guard already prevented one), a misleading PASS status was.
            return value, "REVIEW_MARKET_DATA"
        return value, "PASS"

    return None, "REVIEW_MARKET_DATA"


wb = load_workbook(INPUT_FILE, data_only=True)
ws = wb.active

results = []
for row_num in range(HEADER_ROW + 1, ws.max_row + 1):
    # Restored 2026-09-11 -- addressed by (row, column) via ws.cell(),
    # not by indexing into the row tuple from iter_rows(). That tuple
    # is only as wide as openpyxl thinks the sheet's used range is,
    # which can be narrower than max(FIELD_COLUMNS) on a workbook
    # exported before a newer column existed (e.g. a pre-GICS
    # bloomberg_template.xlsx re-run through a newer FIELD_COLUMNS).
    # ws.cell() on a column past the sheet's populated range just
    # returns an empty cell (value=None), which classify_cell already
    # treats as PENDING_EXTERNAL_DATA -- exactly the right outcome for
    # "this workbook predates this field," not a crash. This exact fix
    # was already shipped once (Pinnbrook session) and was silently
    # reverted when this file was rewritten for liquidity_override;
    # restoring it here rather than leaving the fragile version in
    # place now that the regression was found.
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

# Derive quarter the same way every other producer does -- from
# classified_rows.json's row metadata if it exists (it will, in the
# normal pipeline order: classify runs before this step). Falls back to
# a warned placeholder, never a silent guess.
try:
    with open("data/classified_rows.json") as f:
        classified_rows = json.load(f)
except FileNotFoundError:
    classified_rows = []
QUARTER = derive_quarter_label(classified_rows)

# Per-(cusip, field) exception IDs, covering EVERY field this pipeline
# pulls -- not just PX_LAST's "no coverage at all" case as before. The
# VOLUME_AVG_20D=0 fix above produces REVIEW_MARKET_DATA on individual
# fields (found on Melqart's real data: EA, Chart Industries, Catalyst
# Pharmaceuticals) that had no exception ID at all under the old,
# PX_LAST-only scope -- meaning there was no way to even attach a
# resolution to them. This replaces that narrower mechanism rather than
# running two parallel ones; PX_LAST is just one of the fields covered
# now, not a special case.
still_open = []
corrected_count = 0
already_resolved_no_value = []

for r in results:
    for field in FIELD_COLUMNS:
        status = r[f"{field}_status"]
        if status not in ("REVIEW_MARKET_DATA", "PENDING_EXTERNAL_DATA"):
            continue
        exception_id = make_exception_id(FUND_NAME, QUARTER, f"marketdata_{field}", r["cusip"])
        resolution = get_resolution(exception_id)

        if resolution and resolution["decision"] == "CORRECT" and resolution.get("correction") is not None:
            _, expected_type = FIELD_COLUMNS[field]
            raw_correction = resolution["correction"]
            if expected_type == "numeric":
                try:
                    corrected_value = float(raw_correction)
                except (TypeError, ValueError):
                    # A human recorded a CORRECT decision but the stored
                    # correction doesn't parse as a number for a numeric
                    # field -- never silently apply it. Surfaced as still
                    # open, same as no resolution at all, rather than
                    # guessing what was meant.
                    r[f"{field}_exception_id"] = exception_id
                    still_open.append((r, field, exception_id, None))
                    continue
            else:
                corrected_value = raw_correction
            r[field] = corrected_value
            r[f"{field}_status"] = "PASS_HUMAN_CORRECTED"
            r[f"{field}_correction_source"] = (
                f"CORRECT by {resolution['reviewer']} at {resolution['timestamp']}"
                + (f" -- {resolution['note']}" if resolution.get("note") else "")
            )
            corrected_count += 1
        elif resolution:
            # APPROVE or ESCALATE -- a human has looked at this, but
            # there's no replacement value to apply. Still flagged (the
            # underlying value is still whatever Bloomberg returned),
            # but shown as already-reviewed, not a fresh gap.
            r[f"{field}_exception_id"] = exception_id
            r[f"{field}_human_resolution"] = (
                f"{resolution['decision']} by {resolution['reviewer']} at {resolution['timestamp']}"
                + (f" -- {resolution['note']}" if resolution.get("note") else "")
            )
            already_resolved_no_value.append((r, field, exception_id, resolution))
        else:
            r[f"{field}_exception_id"] = exception_id
            still_open.append((r, field, exception_id, None))

    # Liquidity override -- separate from the per-field mechanism above
    # and checked unconditionally for every CUSIP, not just ones with a
    # flagged field. A resolved cash merger (Chart Industries / Baker
    # Hughes, $210.00/share all-cash, closed 7/16/2026) isn't a
    # correction to what Bloomberg's VOLUME_AVG_20D "really" is -- no
    # finite ADV number produces exactly 0 days to liquidate through the
    # normal shares/(adv*rate) formula, it only ever approaches zero.
    # Forcing this through the per-field correction mechanism would mean
    # inventing a fake trading volume for a security that no longer
    # trades at all. This is a distinct kind of fact -- "this position
    # is now a contractually guaranteed cash claim" -- so it gets its
    # own exception scope and bypasses the ADV math entirely in
    # liquidity.py, rather than feeding a fabricated number into it.
    liq_override_id = make_exception_id(FUND_NAME, QUARTER, "liquidity_override", r["cusip"])
    liq_resolution = get_resolution(liq_override_id)
    if liq_resolution and liq_resolution["decision"] == "CORRECT" and liq_resolution.get("correction"):
        r["liquidityOverride"] = liq_resolution["correction"]
        r["liquidityOverrideSource"] = (
            f"CORRECT by {liq_resolution['reviewer']} at {liq_resolution['timestamp']}"
            + (f" -- {liq_resolution['note']}" if liq_resolution.get("note") else "")
        )
    r["liquidity_override_exception_id"] = liq_override_id  # always recorded, whether resolved or not -- lets a human resolve it later without re-deriving the id

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"Read {len(results)} securities from {INPUT_FILE}")

all_statuses = [record[f"{field}_status"] for record in results for field in FIELD_COLUMNS]
pending = sum(1 for s in all_statuses if s == "PENDING_EXTERNAL_DATA")
review = sum(1 for s in all_statuses if s == "REVIEW_MARKET_DATA")
na = sum(1 for s in all_statuses if s == "NOT_APPLICABLE")
passed = sum(1 for s in all_statuses if s == "PASS")
corrected = sum(1 for s in all_statuses if s == "PASS_HUMAN_CORRECTED")
print(f"  {passed} field values PASS")
if corrected:
    print(f"  {corrected} PASS_HUMAN_CORRECTED (Bloomberg value replaced by a recorded human correction)")
print(f"  {pending} PENDING_EXTERNAL_DATA (Bloomberg error or blank -- no coverage or not yet refreshed)")
print(f"  {review} REVIEW_MARKET_DATA (unexpected value -- needs a look)")
print(f"  {na} NOT_APPLICABLE (warrant ADV, as expected)")

if still_open:
    print(f"\n{len(still_open)} field(s) need a decision:")
    for r, field, exception_id, _ in still_open:
        print(f"    {r['cusip']}  {r['issuer']:30s} {field:16s} [{exception_id}]")
    print(f"\n  python resolution_log.py resolve <exception_id> APPROVE <reviewer> [note]")
    print(f"  python resolution_log.py resolve <exception_id> ESCALATE <reviewer> [note]")
    print(f"  python resolution_log.py resolve <exception_id> CORRECT <reviewer> <correction_value> [note]")

if already_resolved_no_value:
    print(f"\n{len(already_resolved_no_value)} field(s) previously reviewed (APPROVE/ESCALATE, no replacement value) -- not fresh flags:")
    for r, field, exception_id, resolution in already_resolved_no_value:
        print(f"    {r['cusip']}  {r['issuer']:30s} {field:16s} -- {resolution['decision']} by {resolution['reviewer']}")

print(f"\nWrote {OUTPUT_FILE}")
