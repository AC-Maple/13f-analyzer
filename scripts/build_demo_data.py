"""
Reconstructs a demo dataset from the REAL liquidity.py output the user
pasted (issuer, shares, daysToLiquidate_20d/3m, volume trend -- all real,
transcribed directly). ADV is back-solved to be CONSISTENT with those
real days-to-liquidate figures at 15% participation (the rate the user
actually ran): adv = shares / (days * participation_rate). So the
dashboard's own compute_liquidity() reproduces the same real
days-to-liquidate numbers exactly, given the same 0.15 rate -- this
isn't independently invented ADV, it's back-derived from real output.
Only the absolute price LEVEL (and therefore dollar value, EQY_SH_OUT)
is illustrative, deterministic per-name so re-running this script gives
the same demo every time, not random.
"""
import json
import hashlib

REAL_POSITIONS = [
    ("ESTRELLA IMMUNOPHARMA INC", 3975220, 1055.3, 684.4, -35.1),
    ("CITIUS ONCOLOGY INC", 8705589, 767.7, 731.7, -4.7),
    ("DOGWOOD THERAPEUTICS INC", 3132486, 276.9, 263.2, -4.9),
    ("KYNTRA BIO INC", 400000, 143.5, 129.2, -9.9),
    ("TREACE MED CONCEPTS INC", 6364000, 108.3, 64.8, -40.2),
    ("RAPID MICRO BIOSYSTEMS INC", 3328000, 87.1, 106.9, 22.8),
    ("BICYCLE THERAPEUTICS PLC", 3398000, 79.6, 53.9, -32.3),
    ("ORTHOFIX MED INC", 3264000, 66.5, 57.1, -14.1),
    ("MACROGENICS INC", 5006752, 65.8, 39.4, -40.1),
    ("ACCURAY INC DEL", 5736000, 57.6, 26.8, -53.5),
    ("GRIFOLS S A", 2936000, 53.7, 31.6, -41.1),
    ("VOYAGER THERAPEUTICS INC", 3436000, 53.6, 38.7, -27.8),
    ("IRONWOOD PHARMACEUTICALS INC", 13932000, 50.5, 41.7, -17.4),
    ("BRIDGEBIO ONCOLOGY THERAPEUT", 1764000, 45.1, 31.8, -29.5),
    ("ANGIODYNAMICS INC", 2198000, 41.8, 33.5, -19.8),
    ("INUVO INC", 1622307, 41.8, 41.7, -0.2),
    ("RTB DIGITAL INC", 350000, 40.7, 17.2, -57.7),
    ("RIGEL PHARMACEUTICALS INC", 1672000, 35.3, 31.7, -10.0),
    ("AUTOLUS THERAPEUTICS LTD", 15000000, 35.2, 52.6, 49.6),
    ("SOLID BIOSCIENCES INC", 4278000, 33.2, 18.0, -45.7),
    ("INOGEN INC", 1096000, 28.6, 28.0, -2.1),
    ("SUPERNUS PHARMACEUTICALS", 2646201, 27.9, 20.9, -25.0),
    ("NEUROPACE INC", 692000, 27.6, 24.5, -11.2),
    ("NEXTTRIP INC", 402081, 27.3, 15.1, -44.8),
    ("ARVINAS INC", 2796000, 25.6, 24.0, -6.5),
    ("REEDS INC", 486936, 25.4, 59.3, 133.4),
    ("VERRICA PHARMACEUTICALS INC", 426304, 24.8, 47.0, 89.5),
    ("IMMUNOCORE HLDGS PLC", 1428000, 24.6, 18.4, -25.2),
    ("VERASTEM INC", 7024000, 22.7, 18.7, -17.4),
    ("OLB GROUP INC", 1531152, 21.7, 34.9, 61.1),
    ("IMUNON INC", 144767, 18.2, 7.9, -56.7),
    ("AGIOS PHARMACEUTICALS INC", 2400000, 16.4, 14.1, -14.0),
    ("HARMONY BIOSCIENCES HLDGS IN", 1564000, 16.1, 12.8, -20.4),
    ("VSEE HEALTH INC", 4079129, 16.1, 3.3, -79.4),
    ("MINERALYS THERAPEUTICS INC", 1736000, 13.4, 8.9, -33.9),
    ("DYNE THERAPEUTICS INC", 3087226, 12.1, 9.3, -23.1),
    ("ALTO NEUROSCIENCE INC", 864000, 12.0, 10.7, -11.5),
    ("4D MOLECULAR THERAPEUTICS IN", 2000000, 11.9, 14.0, 17.0),
    ("CONDUENT INC", 1692000, 11.6, 10.5, -9.8),
    ("CENTRAL GARDEN & PET CO", 536000, 10.6, 10.4, -1.9),
    ("KURA ONCOLOGY INC", 3678000, 10.6, 13.3, 26.4),
    ("IMMUNOVANT INC", 1736000, 9.8, 9.0, -7.8),
    ("NEKTAR THERAPEUTICS", 724000, 9.0, 5.5, -39.2),
    ("PTC THERAPEUTICS INC", 1071395, 8.7, 4.4, -50.1),
    ("EVOLUS INC", 1436000, 8.0, 10.7, 34.4),
    ("XERIS BIOPHARMA HOLDINGS INC", 1958702, 7.9, 7.1, -10.4),
    ("TRAVERE THERAPEUTICS INC", 1572539, 7.8, 5.9, -24.3),
    ("MADRIGAL PHARMACEUTICALS INC", 288000, 7.5, 5.5, -26.7),
    ("FRESHPET INC", 1260702, 7.2, 6.1, -15.8),
    ("AXOGEN INC", 775000, 6.3, 4.2, -32.5),
    ("DENTSPLY SIRONA INC", 3672000, 5.8, 4.8, -17.5),
    ("FIVE9 INC", 1536000, 4.7, 3.8, -19.7),
    ("INCYTE CORP", 900005, 4.6, 3.3, -28.9),
    ("CYTOKINETICS INC", 1201342, 4.1, 3.9, -5.5),
    ("INTELLIA THERAPEUTICS INC", 1500000, 3.1, 2.1, -30.9),
    ("SANOFI SA", 1064000, 3.0, 2.2, -26.6),
    ("APPIAN CORP", 300000, 2.4, 2.3, -4.3),
    ("NUVATION BIO INC", 2000000, 2.4, 2.0, -17.9),
    ("PENN ENTERTAINMENT INC", 672000, 1.8, 1.4, -18.2),
    ("BLACKLINE INC", 278000, 1.7, 1.7, -0.7),
    ("STITCH FIX INC", 352776, 1.6, 1.3, -20.0),
    ("ALIGN TECHNOLOGY INC", 180286, 1.5, 1.2, -17.4),
    ("GITLAB INC", 1074141, 1.2, 1.3, 8.1),
    ("SENTINELONE INC", 1205661, 1.0, 1.1, 12.1),
    ("BOSTON SCIENTIFIC CORP", 265201, 0.4, 0.4, -5.4),
    ("NVIDIA CORPORATION", 41700, 0.2, 0.2, -8.9),
    ("MICROSOFT CORP", 80581, 0.2, 0.2, -35.0),
    ("ALPHABET INC", 126494, 0.2, 0.2, -28.9),
]

WARRANTS = [
    "BIMERGEN ENERGY CORP", "BIOVIE INC", "BRIACELL THERAPEUTICS CORP",
    "ERNEXA THERAPEUTICS INC", "EXYN TECHNOLOGIES INC", "FGI INDUSTRIES LTD",
    "GREENLAND ENERGY CO", "HEARTBEAM INC", "IVEDA SOLUTIONS INC",
    "LOCAFY LIMITED", "MARIS TECH LTD", "MEDICUS PHARMA LTD", "NEXGEL INC",
    "ONFOLIO HOLDINGS INC", "PASITHEA THERAPEUTICS CORP", "PRESIDIO PPTY TR INC",
    "STRAN & COMPANY INC", "TENON MEDICAL INC",
]
CALL_ISSUERS = {"AGIOS PHARMACEUTICALS INC", "CYTOKINETICS INC", "GITLAB INC",
                 "IMMUNOVANT INC", "MINERALYS THERAPEUTICS INC",
                 "PTC THERAPEUTICS INC", "SENTINELONE INC", "TRAVERE THERAPEUTICS INC"}

PARTICIPATION_RATE_USED = 0.15


def deterministic_price(name):
    h = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    if any(w in name for w in ("NVIDIA", "MICROSOFT", "ALPHABET", "BOSTON SCIENTIFIC")):
        return 40 + (h % 400)
    return 1 + (h % 60) / 2


rows = []
row_num = 1
cusip_seq = 700000000
days_by_name = {}

for name, shares, d20, d3m, voltrend in REAL_POSITIONS:
    price = round(deterministic_price(name), 2)
    value = round(shares * price)
    cusip = f"{cusip_seq:09d}"
    cusip_seq += 1000
    days_by_name[name] = (d20, d3m)

    rows.append({
        "raw_row_number": row_num, "nameOfIssuer": name, "titleOfClass": "COM",
        "cusip": cusip, "figi": None, "value": value, "sshPrnamt": shares,
        "sshPrnamtType": "SH", "putCall": None, "investmentDiscretion": "SOLE",
        "otherManager": None, "votingAuthoritySole": shares,
        "votingAuthorityShared": 0, "votingAuthorityNone": 0,
        "instrumentClass": "COMMON",
        "_source_period_of_report": "2026-06-30",
    })
    row_num += 1

    if name in CALL_ISSUERS:
        call_shares = int(shares * 0.3)
        rows.append({
            "raw_row_number": row_num, "nameOfIssuer": name, "titleOfClass": "COM",
            "cusip": cusip, "figi": None,
            "value": round(call_shares * price * 1.05), "sshPrnamt": call_shares,
            "sshPrnamtType": "SH", "putCall": "Call", "investmentDiscretion": "SOLE",
            "otherManager": None, "votingAuthoritySole": call_shares,
            "votingAuthorityShared": 0, "votingAuthorityNone": 0,
            "instrumentClass": "CALL",
            "_source_period_of_report": "2026-06-30",
        })
        row_num += 1

market_data = []
for r in rows:
    if r["instrumentClass"] != "COMMON":
        continue
    price = r["value"] / r["sshPrnamt"]
    d20, d3m = days_by_name[r["nameOfIssuer"]]
    adv_20d = max(1, round(r["sshPrnamt"] / (d20 * PARTICIPATION_RATE_USED))) if d20 > 0 else 50_000_000
    adv_3m = max(1, round(r["sshPrnamt"] / (d3m * PARTICIPATION_RATE_USED))) if d3m > 0 else 50_000_000

    h = int(hashlib.md5(r["nameOfIssuer"].encode()).hexdigest()[8:16], 16)
    so_millions = 20 + (h % 400)
    if r["nameOfIssuer"] == "KYNTRA BIO INC":
        so_millions = round(r["sshPrnamt"] / 1_000_000 / 0.048, 2)
    if r["nameOfIssuer"] == "IMUNON INC":
        so_millions = round(r["sshPrnamt"] / 1_000_000 / 0.095, 2)

    market_data.append({
        "cusip": r["cusip"], "issuer": r["nameOfIssuer"],
        "PX_LAST": round(price, 2), "PX_LAST_status": "PASS",
        "EQY_SH_OUT": so_millions, "EQY_SH_OUT_status": "PASS",
        "CUR_MKT_CAP": round(so_millions * 1_000_000 * price), "CUR_MKT_CAP_status": "PASS",
        "VOLUME_AVG_20D": adv_20d, "VOLUME_AVG_20D_status": "PASS",
        "VOLUME_AVG_3M": adv_3m, "VOLUME_AVG_3M_status": "PASS",
    })

long_book_est = sum(md["PX_LAST"] * next(r["sshPrnamt"] for r in rows if r["cusip"] == md["cusip"]) for md in market_data)
for name, cusip in [("STATE STR SPDR S&P 500 ETF T", "078462F103"), ("ISHARES TR", "046428765")]:
    put_notional = round(long_book_est * 0.40)
    rows.append({
        "raw_row_number": row_num, "nameOfIssuer": name, "titleOfClass": "TR UNIT",
        "cusip": cusip, "figi": None, "value": put_notional, "sshPrnamt": round(put_notional / 650),
        "sshPrnamtType": "SH", "putCall": "Put", "investmentDiscretion": "SOLE",
        "otherManager": None, "votingAuthoritySole": round(put_notional / 650),
        "votingAuthorityShared": 0, "votingAuthorityNone": 0,
        "instrumentClass": "ETF_INDEX_PUT",
        "_source_period_of_report": "2026-06-30",
    })
    row_num += 1

for name in WARRANTS:
    rows.append({
        "raw_row_number": row_num, "nameOfIssuer": name, "titleOfClass": "*W EXP 12/12/203",
        "cusip": f"{cusip_seq:09d}", "figi": None, "value": 50000, "sshPrnamt": 200000,
        "sshPrnamtType": "SH", "putCall": None, "investmentDiscretion": "SOLE",
        "otherManager": None, "votingAuthoritySole": 200000,
        "votingAuthorityShared": 0, "votingAuthorityNone": 0,
        "instrumentClass": "WARRANT",
        "_source_period_of_report": "2026-06-30",
    })
    cusip_seq += 1000
    row_num += 1

with open("data/classified_rows.json", "w") as f:
    json.dump(rows, f, indent=2)
with open("data/market_data.json", "w") as f:
    json.dump(market_data, f, indent=2)

print(f"Wrote {len(rows)} rows to data/classified_rows.json")
print(f"Wrote {len(market_data)} market data records to data/market_data.json")
