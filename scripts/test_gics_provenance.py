"""Focused tests for historical GICS as-of provenance.

No network. Run from the repo root or scripts/:
  python scripts/test_gics_provenance.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from dashboard import (  # noqa: E402
    build_dashboard_data,
    historical_gics_as_of_available,
    period_of_report_from_rows,
)
from fund_io import (  # noqa: E402
    DATA_DIR,
    discover_prior_classified,
    load_classified,
    load_market_records,
    resolve_manager,
    resolve_market_path,
)
from liquidity import load_market_data  # noqa: E402

Q4_2025 = "2025-12-31"
Q1_2026 = "2026-03-31"
LIVE_PULL = "2026-09-14"


def test_period_of_report_from_rows_uses_canonical_field_not_filename():
    rows = [{"_source_period_of_report": Q4_2025, "_source_cik": "1107310"}]
    assert period_of_report_from_rows(rows) == Q4_2025
    assert period_of_report_from_rows([]) is None
    assert period_of_report_from_rows([{}]) is None


def test_historical_asof_matching_date_passes():
    assert historical_gics_as_of_available(
        {"gicsSourceType": "historical_asof", "gicsAsOfDate": Q4_2025},
        Q4_2025,
    ) is True


def test_historical_asof_wrong_date_fails():
    meta = {"gicsSourceType": "historical_asof", "gicsAsOfDate": Q1_2026}
    assert historical_gics_as_of_available(meta, Q4_2025) is False
    meta_pull = {"gicsSourceType": "historical_asof", "gicsAsOfDate": LIVE_PULL}
    assert historical_gics_as_of_available(meta_pull, Q4_2025) is False


def test_live_source_with_matching_date_fails():
    assert historical_gics_as_of_available(
        {"gicsSourceType": "live", "gicsAsOfDate": Q4_2025},
        Q4_2025,
    ) is False
    assert historical_gics_as_of_available(
        {"bloombergPulledAt": "2026-09-14T23:11:21Z", "gicsAsOfDate": Q4_2025},
        Q4_2025,
    ) is False


def test_missing_date_fails():
    assert historical_gics_as_of_available(
        {"gicsSourceType": "historical_asof"},
        Q4_2025,
    ) is False
    assert historical_gics_as_of_available(
        {"gicsSourceType": "historical_asof", "gicsAsOfDate": ""},
        Q4_2025,
    ) is False
    assert historical_gics_as_of_available(
        {"gicsSourceType": "historical_asof", "gicsAsOfDate": Q4_2025},
        None,
    ) is False


def test_file_presence_only_fails():
    assert historical_gics_as_of_available({}, Q4_2025) is False
    assert historical_gics_as_of_available(
        {"bloombergPulledAt": "2026-09-14T23:11:21Z"},
        Q4_2025,
    ) is False


def test_unparseable_or_timestamp_as_of_fails():
    bad = [
        "2025-12-31T00:00:00Z",
        "2025/12/31",
        "not-a-date",
        "2025-13-31",
    ]
    for value in bad:
        assert historical_gics_as_of_available(
            {"gicsSourceType": "historical_asof", "gicsAsOfDate": value},
            Q4_2025,
        ) is False, value


def _load_eminence():
    manager = resolve_manager("eminence")
    _, classified_rows = load_classified(manager, Q1_2026)
    market_path = resolve_market_path(manager, Q1_2026)
    load_market_records(market_path)
    priors = discover_prior_classified(manager, Q1_2026)
    prior_rows = [rows for _p, _path, rows in priors] or None
    market_data = load_market_data(str(market_path))
    return build_dashboard_data(manager.slug, classified_rows, market_data, prior_rows)


def _rotation_locked(data, extra=""):
    g = data["gicsRotation"]
    assert g.get("historicalProvenanceAvailable") is False, extra
    assert g.get("ranked") == [], extra
    assert g.get("currentHistoricalGicsAsOfAvailable") is False, extra


def _write_prior_market(meta):
    src = DATA_DIR / "market_data_1107310_2026-03-31.json"
    dest = DATA_DIR / "market_data_1107310_2025-12-31.json"
    raw = json.loads(src.read_text(encoding="utf-8"))
    records = raw["records"] if isinstance(raw, dict) else raw
    if meta:
        payload = {**meta, "records": records}
    else:
        payload = records
    dest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return dest


def test_synthetic_files_do_not_unlock_rotation_except_matching_prior_gate():
    prev = os.getcwd()
    os.chdir(SCRIPTS)
    dest = DATA_DIR / "market_data_1107310_2025-12-31.json"
    try:
        baseline = _load_eminence()
        br = next(
            s for s in baseline["sectorConcentration"]["industry"]["ranked"]
            if s["sector"] == "Broadline Retail"
        )
        assert br["trueLongExposure"] == 1059101968
        tickers = [
            x["ticker"]
            for x in baseline["exposures"]
            if x.get("gicsIndustry") == "Broadline Retail"
            and ((x.get("commonValue") or 0) + (x.get("callValue") or 0) > 0)
        ]
        assert tickers == ["SE", "AMZN", "CPNG", "BABA"]
        wk = next(r for r in baseline["changesBlotter"] if r.get("ticker") == "WK")
        assert wk["status"] == "DECREASED" and wk["dollarChange"] == -169394629
        liq = baseline["byBasis"]["common"]["0.15"]["liquidity"]
        mgrc = next(p for p in liq if p.get("ticker") == "MGRC")
        assert mgrc["daysToLiquidate_20d"] == 44.4
        assert mgrc["daysToLiquidate_3m"] == 31.0
        assert len(liq) == 33
        _rotation_locked(baseline, "baseline")
        q4 = next(q for q in baseline["trendsOverTime"] if q["quarter"] == Q4_2025)
        assert q4["historicalGicsAsOfAvailable"] is False

        shutil.copyfile(
            DATA_DIR / "market_data_1107310_2026-03-31.json", dest
        )
        live = _load_eminence()
        _rotation_locked(live, "live prior file")
        assert live["gicsRotation"]["priorHistoricalGicsAsOfAvailable"] is False
        q4_live = next(q for q in live["trendsOverTime"] if q["quarter"] == Q4_2025)
        assert q4_live["historicalGicsAsOfAvailable"] is False
        br_live = next(
            s for s in live["sectorConcentration"]["industry"]["ranked"]
            if s["sector"] == "Broadline Retail"
        )
        assert br_live["trueLongExposure"] == br["trueLongExposure"]

        _write_prior_market({
            "gicsSourceType": "historical_asof",
            "gicsAsOfDate": Q1_2026,
            "bloombergPulledAt": "2026-09-14T23:11:21Z",
        })
        wrong = _load_eminence()
        _rotation_locked(wrong, "wrong as-of date")
        assert wrong["gicsRotation"]["priorHistoricalGicsAsOfAvailable"] is False
        q4_wrong = next(q for q in wrong["trendsOverTime"] if q["quarter"] == Q4_2025)
        assert q4_wrong["historicalGicsAsOfAvailable"] is False

        _write_prior_market({
            "gicsSourceType": "historical_asof",
            "gicsAsOfDate": Q4_2025,
        })
        matching = _load_eminence()
        assert matching["gicsRotation"]["priorHistoricalGicsAsOfAvailable"] is True
        q4_ok = next(q for q in matching["trendsOverTime"] if q["quarter"] == Q4_2025)
        assert q4_ok["historicalGicsAsOfAvailable"] is True
        # Current quarter is still a live BDP pull, so rotation stays locked.
        _rotation_locked(matching, "matching prior only")
        assert matching["gicsRotation"]["currentHistoricalGicsAsOfAvailable"] is False
    finally:
        if dest.exists():
            dest.unlink()
        os.chdir(prev)


def test_armistice_and_pinnbrook_rotation_locked():
    prev = os.getcwd()
    os.chdir(SCRIPTS)
    try:
        a_manager = resolve_manager("armistice")
        _, a_rows = load_classified(a_manager, "2026-06-30")
        a_path = resolve_market_path(a_manager, "2026-06-30")
        load_market_records(a_path)
        a_priors = [rows for _p, _path, rows in discover_prior_classified(a_manager, "2026-06-30")] or None
        armistice = build_dashboard_data(
            a_manager.slug, a_rows, load_market_data(str(a_path)), a_priors
        )
        assert armistice["sectorConcentration"]["industry"]["ranked"]
        _rotation_locked(armistice, "armistice")

        p_manager = resolve_manager("pinnbrook")
        _, p_rows = load_classified(p_manager, Q1_2026)
        p_path = resolve_market_path(p_manager, Q1_2026)
        load_market_records(p_path)
        p_priors = [rows for _p, _path, rows in discover_prior_classified(p_manager, Q1_2026)] or None
        pinnbrook = build_dashboard_data(
            p_manager.slug, p_rows, load_market_data(str(p_path)), p_priors
        )
        assert pinnbrook["sectorConcentration"]["industry"]["ranked"]
        assert "common_plus_calls" in pinnbrook["byBasis"]
        _rotation_locked(pinnbrook, "pinnbrook")
    finally:
        os.chdir(prev)


def main():
    tests = [
        test_period_of_report_from_rows_uses_canonical_field_not_filename,
        test_historical_asof_matching_date_passes,
        test_historical_asof_wrong_date_fails,
        test_live_source_with_matching_date_fails,
        test_missing_date_fails,
        test_file_presence_only_fails,
        test_unparseable_or_timestamp_as_of_fails,
        test_synthetic_files_do_not_unlock_rotation_except_matching_prior_gate,
        test_armistice_and_pinnbrook_rotation_locked,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL  {test.__name__}: {exc}")
    if failed:
        print(f"\n{failed} test(s) failed")
        raise SystemExit(1)
    print(f"\n{len(tests)} tests passed")


if __name__ == "__main__":
    main()
