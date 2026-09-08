"""
fetch_edgar.py -- Step 1 + raw ingestion. Manager name + quarter -> CIK
-> correct filing -> parsed rows in the same schema classify_securities.py
already consumes (data/parsed_rows.json).

Requires network access to sec.gov -- CANNOT run in Claude's sandboxed
environment (see SKILL.md build constraint). Run this on your machine.

Every edgartools API used below (find_company, Company, get_filings,
Filing.accession_number/.filing_date/.period_of_report/.obj(),
ThirteenF.infotable, the exact column names it returns, and the fact
that .infotable already applies the thousands/dollars scaling fix) was
verified by reading the installed v5.55.0 source directly in this
session -- not recalled from memory, not guessed. What was NOT verified:
an actual live call, since this sandbox cannot reach sec.gov. On first
real run, read the printed diagnostics (columns, thousands-flag, row
count) before trusting the output.
"""
import sys
import os
import json
from pathlib import Path

try:
    from edgar import Company, set_identity
except ImportError:
    raise SystemExit("edgartools is not installed. Run: pip install edgartools")

REGISTRY_FILE = Path(__file__).resolve().parent.parent / "references" / "manager_registry.json"

# =========================================================
# CONFIGURATION
# =========================================================

MANAGER_NAME = sys.argv[1] if len(sys.argv) > 1 else "Armistice Capital"
# argv[2] is REGISTER_CIK ("" to skip -- keeps the existing 2-arg
# auto-register pattern working unchanged); argv[3] is FILING_INDEX,
# now a real CLI argument rather than a hand-edited constant -- this
# was the actual blocker to fetching a second quarter for QoQ position
# comparison, not a design choice worth leaving as friction.
REGISTER_CIK = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
FORM_TYPE = "13F-HR"
FILING_INDEX = int(sys.argv[3]) if len(sys.argv) > 3 else 0   # 0 = most recent, 1 = one quarter back, ...

# Identity: checked in this order so a future bug-fix download of this file
# never silently erases your setting. Prefer the EDGAR_IDENTITY environment
# variable (survives any file replacement); YOUR_IDENTITY below is a
# fallback for anyone who'd rather not use an env var, but it WILL be reset
# to the placeholder every time this file is replaced with a corrected copy.
YOUR_IDENTITY = "REPLACE ME your.email@example.com"   # SEC rejects requests without a real one

RAW_DIR = Path("data/raw_filings")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def load_registry():
    if not REGISTRY_FILE.exists():
        return {}
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def save_to_registry(name, cik, full_name=None):
    registry = load_registry()
    registry[name.strip().lower()] = {
        "cik": str(cik),
        "full_name": full_name or name,
        "verified_against": "manually supplied",
        "verified_date": "unset -- edit this entry to record how/when you confirmed it",
    }
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)
    print(f"Added '{name}' -> CIK {cik} to {REGISTRY_FILE}")


def resolve_manager(name_or_cik, register_as=None):
    """Step 1.1: manager name -> CIK.

    CIK is the primary, expected input -- a bare digit string resolves
    directly, no lookup involved. For a name, this checks a small
    hand-maintained local registry (references/manager_registry.json)
    ONLY. It deliberately does not fall back to edgartools'
    find_company(): that function searches get_company_tickers()'s
    ~10,365-entity dataset, scoped to entities that hold a public
    ticker. A 13F-only filer (any hedge fund, including Armistice) is
    structurally outside that dataset -- tested directly, it returned
    ARES CAPITAL, Alset Capital, FIRST CAPITAL, and Rithm Capital for
    "Armistice Capital", none of them correct. A confidently wrong CIK
    silently pulls the wrong fund's entire filing; no match at all is
    a much safer failure mode, so that path is not used here at all.

    Registry entries are added by looking the CIK up once (SEC's own
    company search, or a plain web search for "{name} 13F SEC EDGAR
    CIK" -- this is exactly how Armistice's CIK was found) and either
    editing manager_registry.json directly, or passing it as a second
    CLI argument to auto-register it for next time:
        python fetch_edgar.py "New Fund LLC" 1234567
    """
    if name_or_cik.strip().isdigit():
        if register_as:
            save_to_registry(register_as, name_or_cik.strip())
        return Company(name_or_cik.strip())

    registry = load_registry()
    key = name_or_cik.strip().lower()
    if key in registry:
        entry = registry[key]
        print(f"Registry match: '{name_or_cik}' -> CIK {entry['cik']} "
              f"({entry['full_name']}, verified {entry.get('verified_date', '?')})")
        return Company(entry["cik"])

    raise SystemExit(
        f"'{name_or_cik}' is not in {REGISTRY_FILE}.\n\n"
        f"Look up the CIK once -- SEC's own search or a plain web search for "
        f"'{name_or_cik} 13F SEC EDGAR CIK' finds it in seconds -- then either:\n"
        f"  1. Re-run with both name and CIK to auto-register it:\n"
        f"       python fetch_edgar.py \"{name_or_cik}\" <CIK>\n"
        f"  2. Or edit {REGISTRY_FILE.name} directly.\n\n"
        f"edgartools' find_company() is deliberately not used as a fallback here "
        f"-- it cannot resolve 13F-only filers (see resolve_manager()'s docstring) "
        f"and a wrong guess is worse than no guess."
    )


def select_filing(company):
    """Steps 1.2-1.4: enumerate filings, prefer 13F-HR/A over the
    original for the same period, detect 13F-NT (no infotable of its
    own -- holdings reported through another filer)."""
    filings = company.get_filings(form=FORM_TYPE)

    if len(filings) == 0:
        nt_filings = company.get_filings(form="13F-NT")
        if len(nt_filings) > 0:
            raise SystemExit(
                f"{company.name} has 13F-NT filings only -- holdings are "
                f"reported through another manager, not filed directly. "
                f"This pipeline has no position data for this CIK."
            )
        raise SystemExit(f"No {FORM_TYPE} filings found for {company.name} (CIK {company.cik}).")

    if FILING_INDEX >= len(filings):
        raise SystemExit(
            f"Only {len(filings)} {FORM_TYPE} filings available for "
            f"{company.name}; FILING_INDEX={FILING_INDEX} is out of range."
        )
    filing = filings[FILING_INDEX]

    # An amendment (13F-HR/A) for the SAME period supersedes the
    # original. Check for one and prefer it, recording both accession
    # numbers per SKILL.md step 1.4.
    amendments = company.get_filings(form="13F-HR/A")
    original_accession = filing.accession_number
    for amend in amendments:
        if amend.period_of_report == filing.period_of_report:
            print(
                f"Amendment found for period {filing.period_of_report}: "
                f"{amend.accession_number} supersedes {original_accession}. "
                f"Using the amendment."
            )
            filing = amend
            break

    return filing, original_accession


def main():
    identity = os.environ.get("EDGAR_IDENTITY") or YOUR_IDENTITY
    if "REPLACE ME" in identity:
        raise SystemExit(
            "No identity configured -- SEC rejects requests without one.\n\n"
            "Either:\n"
            "  1. Set it once as an environment variable (survives this file "
            "being replaced by a future update):\n"
            "       Windows (persists across sessions): "
            "setx EDGAR_IDENTITY \"Your Name your.email@example.com\"\n"
            "       Windows (this session only): "
            "set EDGAR_IDENTITY=Your Name your.email@example.com\n"
            "  2. Or edit YOUR_IDENTITY directly in this file -- note this "
            "resets every time you download a corrected copy of it."
        )
    set_identity(identity)

    if REGISTER_CIK:
        company = resolve_manager(REGISTER_CIK, register_as=MANAGER_NAME)
    else:
        company = resolve_manager(MANAGER_NAME)
    print(f"Resolved '{MANAGER_NAME}' -> CIK {company.cik}, {company.name}")

    filing, original_accession = select_filing(company)

    print(f"\nForm:           {filing.form}")
    print(f"Filing date:    {filing.filing_date}")
    print(f"Report period:  {filing.period_of_report}")
    print(f"Accession:      {filing.accession_number}"
          + (f"  (amends {original_accession})" if filing.accession_number != original_accession else ""))
    print(f"Source URL:     {filing.filing_url}")

    thirteenf = filing.obj()
    if thirteenf is None or not hasattr(thirteenf, "infotable"):
        raise SystemExit(
            f"filing.obj() did not return a ThirteenF for accession "
            f"{filing.accession_number} (form={filing.form}). Cannot proceed."
        )

    # Archive the raw XML -- immutable source of truth, data model layer 1.
    # This is the actual filed document, not a derived representation.
    raw_xml = getattr(thirteenf, "infotable_xml", None)
    if raw_xml:
        raw_path = RAW_DIR / f"{filing.accession_number}.xml"
        raw_path.write_text(raw_xml)
        print(f"Archived raw XML: {raw_path}")
    else:
        print("WARNING: no raw XML available (pre-2013 TXT-format filing?) -- "
              "nothing archived at the raw layer.")

    df = thirteenf.infotable
    if df is None or len(df) == 0:
        raise SystemExit(f"infotable is empty for accession {filing.accession_number}.")

    # Diagnostic: confirms whether this specific filing was detected as
    # thousands-scaled. .infotable already applied the correction if so
    # -- this print exists so a human can sanity-check that detection
    # against the values, not so the pipeline acts on it again.
    in_thousands = getattr(thirteenf, "_value_in_thousands_flag", "unknown")
    print(f"\nValue-in-thousands detected: {in_thousands} "
          f"(already corrected in the Value column if True)")
    print(f"Raw columns from edgartools: {list(df.columns)}")

    # Column mapping, verified against edgar/thirteenf/parsers/infotable_xml.py
    # in v5.55.0. edgartools' "Type" field is already normalized to
    # "Shares"/"Principal" -- reversed here back to the raw SEC codes
    # ("SH"/"PRN") this pipeline's schema and SKILL.md field reference
    # document, so downstream scripts see the same convention regardless
    # of whether data came through parse_13f.py or fetch_edgar.py.
    TYPE_REVERSE_MAP = {"Shares": "SH", "Principal": "PRN"}

    rows = []
    for i, record in enumerate(df.to_dict("records"), start=1):
        put_call = record.get("PutCall") or None          # "" -> None, matches parse_13f.py's convention
        other_manager = record.get("OtherManager") or None
        raw_type = record.get("Type")

        rows.append({
            "raw_row_number": i,
            "nameOfIssuer": record.get("Issuer"),
            "titleOfClass": record.get("Class"),
            "cusip": record.get("Cusip"),
            "figi": None,   # not extracted by this edgartools version's XML parser -- verified absent
            "ticker": record.get("Ticker") or "",   # edgartools DOES provide this -- feeds
                                                       # classify_securities.py's FUND_TICKER_MAP,
                                                       # which had nothing to match against before
                                                       # this field was captured (found on the first
                                                       # real fetch: XRT fell to FUND_UNVERIFIED
                                                       # despite already being a verified ticker,
                                                       # because no ticker ever reached the classifier)
            "value": record.get("Value"),
            "sshPrnamt": record.get("SharesPrnAmount"),
            "sshPrnamtType": TYPE_REVERSE_MAP.get(raw_type, raw_type),
            "putCall": put_call,
            "investmentDiscretion": record.get("InvestmentDiscretion"),
            "otherManager": other_manager,
            "votingAuthoritySole": record.get("SoleVoting"),
            "votingAuthorityShared": record.get("SharedVoting"),
            "votingAuthorityNone": record.get("NonVoting"),
            # Provenance -- carried through so every downstream number
            # traces back to this specific filing (SKILL.md step 1.6).
            "_source_cik": company.cik,
            "_source_accession": filing.accession_number,
            "_source_period_of_report": str(filing.period_of_report) if filing.period_of_report else None,
            "_source_filing_date": str(filing.filing_date) if filing.filing_date else None,
            "_source_url": filing.filing_url,
        })

    Path("data").mkdir(exist_ok=True)
    with open("data/parsed_rows.json", "w") as f:
        json.dump(rows, f, indent=2)

    # Period-stamped copy alongside the fixed-name file -- fetching a
    # second quarter overwrites data/parsed_rows.json (every downstream
    # script's default), but this copy persists, so a prior quarter is
    # still there to compare against for QoQ position status.
    period_label = filing.period_of_report or filing.accession_number
    stamped_path = Path(f"data/parsed_rows_{period_label}.json")
    with open(stamped_path, "w") as f:
        json.dump(rows, f, indent=2)

    print(f"\nWrote {len(rows)} rows to data/parsed_rows.json")
    print(f"Also wrote a period-stamped copy: {stamped_path} -- fetch another "
          f"quarter (FILING_INDEX=1, 2, ...) and both copies survive, for QoQ comparison.")
    print("Run classify_securities.py next -- no changes needed there, "
          "this output matches parse_13f.py's schema exactly.")


if __name__ == "__main__":
    main()
