"""
Builds data/classified_rows_prior.json -- a synthetic "prior quarter"
sharing most of the real position names from build_demo_data.py, with
share counts deliberately varied to exercise every QoQ status. This is
NOT real prior-quarter data (no such filing was fetched in this
session) -- it's purely to prove the wiring works correctly before
handing it to the user, the same testing discipline as everything else
in this build.
"""
import json
import hashlib

with open("data/classified_rows.json") as f:
    current_rows = json.load(f)

prior_rows = []
row_num = 1
skip_cusips = set()

for i, r in enumerate(current_rows):
    if r["instrumentClass"] != "COMMON":
        continue
    h = int(hashlib.md5((r["nameOfIssuer"] + "prior").encode()).hexdigest()[:8], 16)
    mod = h % 5

    if mod == 0:
        continue  # this position is NEW this quarter -- absent from prior
    elif mod == 1:
        skip_cusips.add(r["cusip"])  # this position was CLOSED this quarter -- present in prior, absent now
        shares = int(r["sshPrnamt"] * 1.4)
    elif mod == 2:
        shares = int(r["sshPrnamt"] * 0.6)  # will show as INCREASED this quarter
    elif mod == 3:
        shares = int(r["sshPrnamt"] * 1.8)  # will show as DECREASED this quarter
    else:
        shares = r["sshPrnamt"]  # UNCHANGED

    prior_rows.append({
        **{k: v for k, v in r.items() if k not in ("value", "sshPrnamt", "votingAuthoritySole", "raw_row_number")},
        "raw_row_number": row_num,
        "sshPrnamt": shares,
        "value": round(shares * (r["value"] / r["sshPrnamt"]) * 0.92),  # slightly different price, prior quarter
        "votingAuthoritySole": shares,
        "_source_period_of_report": "2026-03-31",
    })
    row_num += 1

with open("data/classified_rows_prior.json", "w") as f:
    json.dump(prior_rows, f, indent=2)

print(f"Wrote {len(prior_rows)} prior-quarter rows (synthetic, for wiring-test purposes only)")
print(f"{sum(1 for r in current_rows if r['instrumentClass']=='COMMON')} current COMMON positions, "
      f"expect a mix of NEW/CLOSED/INCREASED/DECREASED/UNCHANGED")
