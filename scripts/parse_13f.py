"""
parse_13f.py — Filing line item parser.

Per SKILL.md: preserve every SEC information-table row exactly as reported.
No deduplication, no aggregation. One record per row.
"""
import csv
import re


def parse_number(s):
    """SEC numeric fields come comma-formatted; blank means field absent, not zero."""
    s = s.strip()
    if s == "":
        return None
    return int(s.replace(",", ""))


def parse_raw_table(path):
    """
    Parse the pipe-delimited 13F information table.
    Columns: nameOfIssuer | titleOfClass | cusip | figi | value | sshPrnamt |
             sshPrnamtType | putCall | investmentDiscretion | otherManager |
             votingAuthority(Sole) | votingAuthority(Shared) | votingAuthority(None)
    """
    rows = []
    with open(path) as f:
        for line_num, line in enumerate(f, start=1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 13:
                raise ValueError(
                    f"Line {line_num}: expected 13 fields, got {len(parts)}: {line!r}"
                )
            (name, title_of_class, cusip, figi, value, shares, sh_prn_type,
             put_call, discretion, other_manager, sole, shared, none_) = parts

            rows.append({
                "raw_row_number": line_num,
                "nameOfIssuer": name,
                "titleOfClass": title_of_class,
                "cusip": cusip,
                "figi": figi if figi else None,
                "value": parse_number(value),
                "sshPrnamt": parse_number(shares),
                "sshPrnamtType": sh_prn_type,
                "putCall": put_call if put_call else None,
                "investmentDiscretion": discretion,
                "otherManager": other_manager if other_manager else None,
                "votingAuthoritySole": parse_number(sole),
                "votingAuthorityShared": parse_number(shared),
                "votingAuthorityNone": parse_number(none_),
            })
    return rows


if __name__ == "__main__":
    import sys
    import json

    path = sys.argv[1] if len(sys.argv) > 1 else "data/armistice_q1_2026_raw.txt"
    rows = parse_raw_table(path)
    print(f"Parsed {len(rows)} filing line items from {path}")

    # Sanity spot-check: does CYTOKINETICS come through as 4 distinct rows?
    cytk_rows = [r for r in rows if r["cusip"] == "23282W605"]
    print(f"\nCYTOKINETICS (CUSIP 23282W605): {len(cytk_rows)} rows")
    for r in cytk_rows:
        print(f"  putCall={r['putCall'] or 'None (common)':15s} "
              f"shares={r['sshPrnamt']:>10,d}  value=${r['value']:>14,d}")

    with open("data/parsed_rows.json", "w") as f:
        json.dump(rows, f, indent=2)
    print(f"\nWrote data/parsed_rows.json ({len(rows)} records)")
