"""Rebuild a fund/quarter dashboard from stamped inputs.

Does not read or write the shared working files data/classified_rows.json
or data/market_data.json. Bloomberg fetch/classify/import flags are not
in this cut -- those stay a later phase.

Usage (from the repo root, or from scripts/):
  python scripts/build_fund_dashboard.py --manager "Melqart Asset Management" --quarter 2026-06-30
  python scripts/build_fund_dashboard.py --all
"""
from __future__ import annotations

import argparse
import os
import sys
from contextlib import contextmanager
from pathlib import Path

from fund_io import (
    DATA_DIR,
    SCRIPTS_DIR,
    FundBuildError,
    accepted_managers,
    dashboard_output_path,
    discover_prior_classified,
    latest_buildable_quarter,
    load_classified,
    load_market_records,
    parse_quarter,
    resolve_manager,
    resolve_market_path,
)

from dashboard import (
    PARTICIPATION_RATES,
    MarketDataStampMismatch,
    render_and_write_dashboard,
)
from liquidity import load_market_data


@contextmanager
def _scripts_cwd():
    """Existing persist/load helpers write relative data/ paths.

    Keep that chdir inside the runner so the CLI still works from the
    repo root. Restore the caller's cwd afterward.
    """
    previous = Path.cwd()
    os.chdir(SCRIPTS_DIR)
    try:
        yield
    finally:
        os.chdir(previous)


def _die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def build_one(manager_query: str, quarter: str) -> Path:
    manager = resolve_manager(manager_query)
    period = parse_quarter(quarter)
    classified_path, classified_rows = load_classified(manager, period)
    market_path = resolve_market_path(manager, period)
    load_market_records(market_path)

    priors = discover_prior_classified(manager, period)
    prior_quarters_rows = [rows for _p, _path, rows in priors] or None
    output_path = dashboard_output_path(manager, period)

    print(f"Building {manager.full_name}  CIK {manager.cik}  period {period}")
    print(f"  classified: {classified_path}")
    print(f"  market:     {market_path}")
    if priors:
        shown = ", ".join(f"{p} ({path.name})" for p, path, _ in priors)
        print(f"  priors:     {shown}")
    else:
        print("  priors:     none -- QoQ unavailable")
    print(f"  output:     {output_path}")
    if DATA_DIR / "classified_rows.json" == classified_path:
        _die("internal error: refused to use shared classified_rows.json")
    if DATA_DIR / "market_data.json" == market_path:
        _die("internal error: refused to use shared market_data.json")

    print(f"Computing across {len(PARTICIPATION_RATES)} participation rates...")
    market_data = load_market_data(str(market_path))
    with _scripts_cwd():
        try:
            render_and_write_dashboard(
                manager.slug,
                classified_rows,
                market_data,
                prior_quarters_rows,
                str(output_path),
            )
        except MarketDataStampMismatch as exc:
            _die(str(exc))
    return output_path


def build_all() -> list[Path]:
    written = []
    errors = []
    for manager in accepted_managers():
        try:
            period = latest_buildable_quarter(manager)
            written.append(build_one(manager.registry_key, period))
        except (FundBuildError, MarketDataStampMismatch) as exc:
            errors.append(f"{manager.full_name}: {exc}")
            print(f"ERROR: {manager.full_name}: {exc}", file=sys.stderr)
    if errors:
        _die(
            f"--all finished with {len(errors)} failure(s):\n  "
            + "\n  ".join(errors)
        )
    return written


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild a 13F dashboard from fund/quarter-stamped inputs "
            "without swapping shared classified_rows.json / market_data.json."
        )
    )
    parser.add_argument(
        "--manager",
        help="Registry key, legal name, alias, or CIK",
    )
    parser.add_argument(
        "--quarter",
        help="Filing period YYYY-MM-DD (no silent fallback to another quarter)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="rebuild_all",
        help=(
            "Rebuild the accepted four-fund set. Each fund uses the latest "
            "period that has both classified rows and a market snapshot."
        ),
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    try:
        if args.rebuild_all:
            if args.manager or args.quarter:
                raise FundBuildError(
                    "Use --all alone, or --manager and --quarter together, not both."
                )
            paths = build_all()
            print(f"Rebuilt {len(paths)} dashboard(s).")
            return
        if not args.manager or not args.quarter:
            raise FundBuildError(
                "Provide --manager and --quarter, or --all. "
                "A manager without a quarter does not fall back to the latest filing."
            )
        build_one(args.manager, args.quarter)
    except FundBuildError as exc:
        _die(str(exc))


if __name__ == "__main__":
    main()
