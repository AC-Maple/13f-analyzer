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

from classify_securities import normalize_ticker

REGISTRY_FILE = Path(__file__).resolve().parent.parent / "references" / "manager_registry.json"
SCRIPTS_DIR = Path(__file__).resolve().parent

# =========================================================
# CONFIGURATION
# =========================================================

FORM_TYPE = "13F-HR"

# Identity: checked in this order so a future bug-fix download of this file
# never silently erases your setting. Prefer the EDGAR_IDENTITY environment
# variable (survives any file replacement); YOUR_IDENTITY below is a
# fallback for anyone who'd rather not use an env var, but it WILL be reset
# to the placeholder every time this file is replaced with a corrected copy.
YOUR_IDENTITY = "REPLACE ME your.email@example.com"   # SEC rejects requests without a real one

RAW_DIR = Path("data/raw_filings")

# Column mapping, verified against edgar/thirteenf/parsers/infotable_xml.py
# in v5.55.0. edgartools' "Type" field is already normalized to
# "Shares"/"Principal" -- reversed here back to the raw SEC codes
# ("SH"/"PRN") this pipeline's schema and SKILL.md field reference
# document, so downstream scripts see the same convention regardless
# of whether data came through parse_13f.py or fetch_edgar.py.
TYPE_REVERSE_MAP = {"Shares": "SH", "Principal": "PRN"}


class FilingSelectionError(Exception):
    """No usable 13F-HR for this CIK / index -- not a crash."""


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


def configure_identity():
    """SEC rejects requests without a real User-Agent identity."""
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
    return identity


def list_original_13f_filings(company):
    """Enumerate original 13F-HR filings only (amendments=False).

    edgartools' get_filings(form='13F-HR') defaults to amendments=True,
    which interleaves 13F-HR/A into the same list so FILING_INDEX no
    longer means 'Nth original holdings report'. The same-period /A
    overlay in apply_amendment_overlay is the documented way to prefer
    an amendment; it is applied after this list is built.
    """
    filings = company.get_filings(form=FORM_TYPE, amendments=False)

    if len(filings) == 0:
        nt_filings = company.get_filings(form="13F-NT")
        if len(nt_filings) > 0:
            raise FilingSelectionError(
                f"{company.name} has 13F-NT filings only -- holdings are "
                f"reported through another manager, not filed directly. "
                f"This pipeline has no position data for this CIK."
            )
        raise FilingSelectionError(
            f"No {FORM_TYPE} filings found for {company.name} (CIK {company.cik})."
        )
    return filings


def apply_amendment_overlay(filing, amendments):
    """Prefer a same-period 13F-HR/A over the original. First match wins.

    Returns (filing_to_use, original_accession).
    """
    original_accession = filing.accession_number
    if amendments is None:
        return filing, original_accession
    for amend in amendments:
        if amend.period_of_report == filing.period_of_report:
            if amend.accession_number != original_accession:
                print(
                    f"Amendment found for period {filing.period_of_report}: "
                    f"{amend.accession_number} supersedes {original_accession}. "
                    f"Using the amendment."
                )
            return amend, original_accession
    return filing, original_accession


def select_filing(company, filing_index=0, filings=None, amendments=None):
    """Steps 1.2-1.4: enumerate original 13F-HR filings, prefer 13F-HR/A
    over the original for the same period, detect 13F-NT (no infotable of
    its own -- holdings reported through another filer)."""
    if filings is None:
        filings = list_original_13f_filings(company)

    if filing_index >= len(filings):
        who = getattr(company, "name", None) or "this manager"
        raise FilingSelectionError(
            f"Only {len(filings)} {FORM_TYPE} filings available for "
            f"{who}; FILING_INDEX={filing_index} is out of range."
        )
    filing = filings[filing_index]

    # An amendment (13F-HR/A) for the SAME period supersedes the
    # original. Check for one and prefer it, recording both accession
    # numbers per SKILL.md step 1.4.
    if amendments is None:
        amendments = company.get_filings(form="13F-HR/A")
    return apply_amendment_overlay(filing, amendments)


def period_label_of(filing):
    period = filing.period_of_report
    if period is None or str(period).strip() == "":
        raise FilingSelectionError(
            f"Filing {filing.accession_number} has no period_of_report; "
            f"refusing to guess a quarter."
        )
    return str(period)


def archive_raw_xml(thirteenf, filing, raw_dir=None):
    """Archive the raw XML -- immutable source of truth, data model layer 1."""
    dest = Path(raw_dir) if raw_dir is not None else RAW_DIR
    dest.mkdir(parents=True, exist_ok=True)
    raw_xml = getattr(thirteenf, "infotable_xml", None)
    if raw_xml:
        raw_path = dest / f"{filing.accession_number}.xml"
        raw_path.write_text(raw_xml)
        print(f"Archived raw XML: {raw_path}")
        return raw_path
    print("WARNING: no raw XML available (pre-2013 TXT-format filing?) -- "
          "nothing archived at the raw layer.")
    return None


def load_thirteenf(filing):
    thirteenf = filing.obj()
    if thirteenf is None or not hasattr(thirteenf, "infotable"):
        raise FilingSelectionError(
            f"filing.obj() did not return a ThirteenF for accession "
            f"{filing.accession_number} (form={filing.form}). Cannot proceed."
        )
    return thirteenf


def rows_from_filing(company, filing, thirteenf=None):
    """Parse a ThirteenF infotable into this pipeline's row schema."""
    if thirteenf is None:
        thirteenf = load_thirteenf(filing)

    df = thirteenf.infotable
    if df is None or len(df) == 0:
        raise FilingSelectionError(
            f"infotable is empty for accession {filing.accession_number}."
        )

    # Diagnostic: confirms whether this specific filing was detected as
    # thousands-scaled. .infotable already applied the correction if so
    # -- this print exists so a human can sanity-check that detection
    # against the values, not so the pipeline acts on it again.
    in_thousands = getattr(thirteenf, "_value_in_thousands_flag", "unknown")
    print(f"\nValue-in-thousands detected: {in_thousands} "
          f"(already corrected in the Value column if True)")
    print(f"Raw columns from edgartools: {list(df.columns)}")

    period = period_label_of(filing)
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
            "ticker": normalize_ticker(record.get("Ticker")),
            # edgartools adds Ticker via CUSIP lookup; official 13F XML
            # has no ticker field. Missing lookups arrive as pandas NaN.
            # normalize_ticker turns None / NaN / non-strings / "nan" into
            # "" so FUND_TICKER_MAP is a no-op rather than a crash.
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
            "_source_period_of_report": period,
            "_source_filing_date": str(filing.filing_date) if filing.filing_date else None,
            "_source_url": filing.filing_url,
        })
    return rows


def write_json(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(rows, f, indent=2)
    return path


def print_filing_header(filing, original_accession):
    print(f"\nForm:           {filing.form}")
    print(f"Filing date:    {filing.filing_date}")
    print(f"Report period:  {filing.period_of_report}")
    print(f"Accession:      {filing.accession_number}"
          + (f"  (amends {original_accession})" if filing.accession_number != original_accession else ""))
    print(f"Source URL:     {filing.filing_url}")


def main(argv=None):
    argv = argv if argv is not None else sys.argv
    # argv[1] manager; argv[2] is REGISTER_CIK ("" to skip -- keeps the
    # existing 2-arg auto-register pattern working unchanged); argv[3]
    # is FILING_INDEX, 0 = most recent original 13F-HR.
    manager_name = argv[1] if len(argv) > 1 else "Armistice Capital"
    register_cik = argv[2] if len(argv) > 2 and argv[2] else None
    filing_index = int(argv[3]) if len(argv) > 3 else 0

    configure_identity()

    if register_cik:
        company = resolve_manager(register_cik, register_as=manager_name)
    else:
        company = resolve_manager(manager_name)
    print(f"Resolved '{manager_name}' -> CIK {company.cik}, {company.name}")

    try:
        filing, original_accession = select_filing(company, filing_index=filing_index)
        print_filing_header(filing, original_accession)
        thirteenf = load_thirteenf(filing)
        archive_raw_xml(thirteenf, filing)
        rows = rows_from_filing(company, filing, thirteenf)
    except FilingSelectionError as exc:
        raise SystemExit(str(exc)) from exc

    Path("data").mkdir(exist_ok=True)
    with open("data/parsed_rows.json", "w") as f:
        json.dump(rows, f, indent=2)

    # Period-stamped copy alongside the fixed-name file -- fetching a
    # second quarter overwrites data/parsed_rows.json (every downstream
    # script's default), but this copy persists, so a prior quarter is
    # still there to compare against for QoQ position status.
    #
    # CIK-qualified, not period-alone: found by testing against a real
    # second fund in the same session (Pinnbrook, CIK 1856103) -- most
    # 13F filers report on standard calendar-quarter boundaries, so two
    # unrelated funds' filings routinely share the exact same
    # period_of_report string. A period-only filename silently
    # overwrote Armistice's (CIK 1601086) saved Q4 2025/Q1 2026 files
    # with Pinnbrook's data of the same period labels the moment a
    # second fund was fetched in this project -- confirmed directly:
    # every "Armistice" period-stamped file read back with
    # _source_cik=1856103 after the collision. dashboard.py's own
    # output filename was already fund-qualified for exactly this
    # reason (SKILL.md: "so different funds and different quarters of
    # the same fund can never silently overwrite one another") --
    # fetch_edgar.py's period-stamped copy never got the same
    # treatment until this bug actually manifested and destroyed real
    # saved data. CIK, not fund name, since it's already a stable,
    # unambiguous per-fund identifier with no normalization edge cases.
    period_label = period_label_of(filing)
    stamped_path = Path(f"data/parsed_rows_{company.cik}_{period_label}.json")
    with open(stamped_path, "w") as f:
        json.dump(rows, f, indent=2)

    print(f"\nWrote {len(rows)} rows to data/parsed_rows.json")
    print(f"Also wrote a period-stamped copy: {stamped_path} -- fetch another "
          f"quarter (FILING_INDEX=1, 2, ...) and both copies survive, for QoQ comparison.")
    print("Run classify_securities.py next -- no changes needed there, "
          "this output matches parse_13f.py's schema exactly.")


if __name__ == "__main__":
    main()
