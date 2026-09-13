"""Retrieve the latest 3 or 4 13F quarters into stamped fund/quarter files.

Does not read or write the shared working files data/parsed_rows.json,
data/classified_rows.json, or data/market_data.json. Does not render a
dashboard and does not create market-data snapshots -- those stay on
build_fund_dashboard.py after a human Bloomberg refresh.

Usage:
  python scripts/build_fund_history.py --manager "Pinnbrook Capital Management" --quarters 3
  python scripts/build_fund_history.py --manager armistice --quarters 4
"""
from __future__ import annotations

import argparse
import os
import sys
from contextlib import contextmanager
from pathlib import Path

from fund_io import (
    SCRIPTS_DIR,
    FundBuildError,
    bloomberg_template_path,
    classified_write_path,
    parsed_path,
    raw_filings_dir,
    resolve_manager,
    shared_working_files,
    validate_classified,
    validate_parsed,
)

from classify_securities import classify_all
from export_bloomberg_template import export_template
from fetch_edgar import (
    Company,
    FilingSelectionError,
    apply_amendment_overlay,
    archive_raw_xml,
    configure_identity,
    list_original_13f_filings,
    load_thirteenf,
    period_label_of,
    print_filing_header,
    rows_from_filing,
    write_json,
)

ALLOWED_QUARTERS = frozenset({3, 4})
SHARED_NAMES = ("parsed_rows.json", "classified_rows.json", "market_data.json")


@contextmanager
def _scripts_cwd():
    previous = Path.cwd()
    os.chdir(SCRIPTS_DIR)
    try:
        yield
    finally:
        os.chdir(previous)


def _die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def collect_unique_period_filings(filings, amendments, n_quarters, company_name=""):
    """Walk original 13F-HR filings in list order, apply the same-period
    /A overlay, skip duplicate period_of_report values, and return N
    unique quarters oldest-first.

    Does not substitute a different quarter to fill N. Exhausting the
    original list before N unique periods is a hard failure.
    """
    if n_quarters not in ALLOWED_QUARTERS:
        raise FundBuildError(
            f"--quarters must be 3 or 4, not {n_quarters}."
        )
    selected = []
    seen = set()
    skipped = []
    index = 0
    while len(selected) < n_quarters:
        if index >= len(filings):
            got = ", ".join(p for _f, _o, p in selected) or "(none)"
            raise FundBuildError(
                f"Requested {n_quarters} unique 13F periods for {company_name or 'this manager'} "
                f"but only {len(selected)} distinct period_of_report value(s) were available: {got}. "
                f"Refusing to substitute another quarter."
            )
        try:
            filing, original_accession = apply_amendment_overlay(
                filings[index], amendments
            )
            period = period_label_of(filing)
        except FilingSelectionError as exc:
            raise FundBuildError(str(exc)) from exc
        index += 1
        if period in seen:
            skipped.append((period, filing.accession_number, original_accession))
            print(
                f"Skipping duplicate period {period} "
                f"(accession {filing.accession_number}; already have this quarter). "
                f"Not counting toward --quarters {n_quarters}."
            )
            continue
        seen.add(period)
        selected.append((filing, original_accession, period))

    selected.sort(key=lambda item: item[2])
    return selected, skipped


def _assert_not_shared(path: Path) -> None:
    if path.name in SHARED_NAMES:
        raise FundBuildError(
            f"internal error: refused to write shared working file {path}"
        )


def persist_quarter(manager, filing, original_accession, period, company) -> dict:
    """Fetch infotable, classify, and write stamped parse/classify/template."""
    parsed_out = parsed_path(manager, period)
    classified_out = classified_write_path(manager, period)
    template_out = bloomberg_template_path(manager, period)
    for path in (parsed_out, classified_out, template_out):
        _assert_not_shared(path)

    print_filing_header(filing, original_accession)
    thirteenf = load_thirteenf(filing)
    archive_raw_xml(thirteenf, filing, raw_dir=raw_filings_dir())
    rows = rows_from_filing(company, filing, thirteenf)
    validate_parsed(rows, manager.cik, period, parsed_out)

    write_json(parsed_out, rows)
    print(f"Wrote {len(rows)} parsed rows: {parsed_out}")

    for row in rows:
        row.setdefault("ticker", "")
    classified = classify_all(rows)
    validate_classified(classified, manager.cik, period, classified_out)
    if not any(r.get("instrumentClass") for r in classified):
        raise FundBuildError(f"{classified_out}: classification produced no instrumentClass")
    write_json(classified_out, classified)
    print(f"Wrote {len(classified)} classified rows: {classified_out}")

    export_template(classified, template_out)

    return {
        "period": period,
        "accession": filing.accession_number,
        "original_accession": original_accession,
        "form": filing.form,
        "row_count": len(classified),
        "parsed": parsed_out,
        "classified": classified_out,
        "template": template_out,
    }


def build_history(manager_query: str, n_quarters: int) -> list[dict]:
    if n_quarters not in ALLOWED_QUARTERS:
        raise FundBuildError(
            f"--quarters must be 3 or 4, not {n_quarters}."
        )
    manager = resolve_manager(manager_query)
    configure_identity()
    company = Company(manager.cik)
    print(f"Resolved '{manager_query}' -> {manager.full_name}  "
          f"CIK {manager.cik}  ({company.name})")

    try:
        filings = list_original_13f_filings(company)
        amendments = company.get_filings(form="13F-HR/A") or []
    except FilingSelectionError as exc:
        raise FundBuildError(str(exc)) from exc

    print(
        f"Original 13F-HR filings available: {len(filings)} "
        f"(amendments listed separately: {len(amendments)})"
    )
    selected, _skipped = collect_unique_period_filings(
        filings, amendments, n_quarters, company_name=manager.full_name
    )

    results = []
    for filing, original_accession, period in selected:
        print(f"\n=== {manager.full_name}  period {period} ===")
        results.append(
            persist_quarter(manager, filing, original_accession, period, company)
        )

    print(f"\nWrote {len(results)} stamped quarters for {manager.full_name} "
          f"(CIK {manager.cik}):")
    for item in results:
        amended = (
            f"  (amends {item['original_accession']})"
            if item["accession"] != item["original_accession"]
            else ""
        )
        print(f"  {item['period']}  {item['accession']}  "
              f"{item['row_count']} rows{amended}")
        print(f"    parsed:     {item['parsed']}")
        print(f"    classified: {item['classified']}")
        print(f"    template:   {item['template']}")

    latest = results[-1]["period"]
    print(
        "\nRefresh each bloomberg_template_{cik}_{period}.xlsx on a "
        "Bloomberg Terminal machine."
    )
    print(
        "Import each to data/market_data_{cik}_{period}.json "
        "(not market_data.json)."
    )
    print(
        "Then: "
        f"python scripts/build_fund_dashboard.py --manager \"{manager.full_name}\" "
        f"--quarter {latest}"
    )
    parsed_shared, classified_shared, market_shared = shared_working_files()
    print(
        "Shared working files were not used: "
        f"{parsed_shared.name}, {classified_shared.name}, {market_shared.name}."
    )
    return results


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Retrieve the latest 3 or 4 valid 13F quarters into stamped "
            "parsed/classified files and quarter-specific Bloomberg templates. "
            "Does not rebuild dashboards or write shared working files."
        )
    )
    parser.add_argument(
        "--manager",
        required=True,
        help="Registry key, legal name, alias, or CIK",
    )
    parser.add_argument(
        "--quarters",
        type=int,
        required=True,
        help="Number of unique 13F periods to retrieve (3 or 4)",
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    try:
        with _scripts_cwd():
            build_history(args.manager, args.quarters)
    except FundBuildError as exc:
        _die(str(exc))


if __name__ == "__main__":
    main()
