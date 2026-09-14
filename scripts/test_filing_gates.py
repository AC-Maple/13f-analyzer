"""Focused tests for ticker normalization and the anomalous-13F gate.

No network. Run from the repo root or scripts/:
  python scripts/test_filing_gates.py
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from classify_securities import classify_all, classify_row, fund_class_of, normalize_ticker
from filing_anomaly import (
    ReviewRequired,
    assess_anomalous_13f,
    format_review_report,
    is_dummy_row,
)


def _common_row(**overrides):
    row = {
        "cusip": "23282W605",
        "ticker": "CYTK",
        "nameOfIssuer": "CYTOKINETICS INC",
        "titleOfClass": "COM",
        "putCall": None,
        "sshPrnamtType": "SH",
        "value": 50_390_700,
        "sshPrnamt": 764_538,
    }
    row.update(overrides)
    return row


def _spy_row(**overrides):
    row = {
        "cusip": "78462F103",
        "ticker": "SPY",
        "nameOfIssuer": "SPDR S&P 500 ETF TRUST",
        "titleOfClass": "S&P 500 ETF",
        "putCall": "Put",
        "sshPrnamtType": "SH",
        "value": 1_000_000,
        "sshPrnamt": 10_000,
    }
    row.update(overrides)
    return row


def _eminence_stub_row():
    return {
        "nameOfIssuer": "None",
        "titleOfClass": "0",
        "cusip": "000000000",
        "value": 0,
        "sshPrnamt": 0,
        "sshPrnamtType": "SH",
        "putCall": None,
        "ticker": float("nan"),
    }


def test_normalize_ticker():
    assert normalize_ticker(None) == ""
    assert normalize_ticker(float("nan")) == ""
    assert normalize_ticker(0.0) == ""
    assert normalize_ticker(123) == ""
    assert normalize_ticker("nan") == ""
    assert normalize_ticker("NaN") == ""
    assert normalize_ticker(" none ") == ""
    assert normalize_ticker("NONE") == ""
    assert normalize_ticker("") == ""
    assert normalize_ticker("  ") == ""
    assert normalize_ticker("SPY") == "SPY"
    assert normalize_ticker(" spy ") == "spy"
    try:
        import numpy as np
        assert normalize_ticker(np.float64("nan")) == ""
    except ImportError:
        pass


def test_empty_ticker_is_fund_map_noop():
    row = _common_row(ticker="", cusip="999999999")
    assert fund_class_of(row) is None
    row["ticker"] = float("nan")
    assert fund_class_of(row) is None
    classified = classify_all([_common_row(ticker=float("nan"), cusip="999999999")])
    assert classified[0]["ticker"] == ""
    assert classified[0]["instrumentClass"] == "COMMON"


def test_valid_tickers_unchanged():
    spy = classify_row(_spy_row())
    assert spy == "ETF_INDEX_PUT"
    spy_nan_ticker_but_cusip = classify_row(_spy_row(ticker=float("nan")))
    assert spy_nan_ticker_but_cusip == "ETF_INDEX_PUT"
    xrt = classify_row(_common_row(
        cusip="000000001",
        ticker="XRT",
        nameOfIssuer="SPDR S&P RETAIL ETF",
        titleOfClass="S&P RETAIL ETF",
        putCall=None,
    ))
    assert xrt == "SECTOR_ETF"


def test_classify_does_not_crash_on_nan_ticker():
    classify_row(_eminence_stub_row())


def test_dummy_row_detection():
    assert is_dummy_row(_eminence_stub_row())
    assert is_dummy_row(_eminence_stub_row() | {"nameOfIssuer": None})
    assert not is_dummy_row(_common_row())
    assert not is_dummy_row(_common_row(
        cusip="037833100",
        nameOfIssuer="APPLE INC",
        value=1,
        sshPrnamt=1,
    ))


def _priors():
    return [
        {"period": "2025-12-31", "row_count": 39, "value_total": 6_323_956_411,
         "filing_bytes": 25763, "infotable_bytes": 20000, "filing_date": "2026-02-17"},
        {"period": "2026-03-31", "row_count": 33, "value_total": 4_361_339_054,
         "filing_bytes": 22367, "infotable_bytes": 18000, "filing_date": "2026-05-15"},
    ]


def test_eminence_stub_is_review_required():
    decision = assess_anomalous_13f(
        manager_name="Eminence Capital, LP",
        cik="1107310",
        period="2026-06-30",
        accession="0000902664-26-003015",
        rows=[_eminence_stub_row()],
        table_entry_total=1,
        table_value_total=0,
        infotable_bytes=786,
        filing_bytes=4217,
        filing_date="2026-07-06",
        prior_quarters=_priors(),
    )
    assert decision.review_required
    assert decision.structural_dummy_table
    report = format_review_report(decision)
    assert "REVIEW REQUIRED — ANOMALOUS 13F FILING" in report
    assert "0000902664-26-003015" in report
    assert "dummy CUSIP 000000000" in report
    assert "missing issuer" in report
    assert "2026-03-31: 33 rows / $4.36B" in report
    assert "2025-12-31: 39 rows / $6.32B" in report
    assert report.index("2026-03-31: 33 rows / $4.36B") < report.index(
        "2025-12-31: 39 rows / $6.32B"
    )
    assert "STATUS: REVIEW REQUIRED" in report
    assert isinstance(ReviewRequired(report), ReviewRequired)


def test_dummy_table_blocks_without_priors():
    decision = assess_anomalous_13f(
        manager_name="Eminence Capital, LP",
        cik="1107310",
        period="2026-06-30",
        accession="0000902664-26-003015",
        rows=[_eminence_stub_row()],
        table_entry_total=1,
        table_value_total=0,
        infotable_bytes=786,
        filing_bytes=4217,
        filing_date="2026-07-06",
        prior_quarters=[],
    )
    assert decision.review_required
    assert decision.structural_dummy_table


def test_decline_alone_is_not_a_hard_stop():
    real_one_name = _common_row(
        nameOfIssuer="APPLE INC",
        cusip="037833100",
        value=100_000_000,
        sshPrnamt=500_000,
        ticker="AAPL",
    )
    decision = assess_anomalous_13f(
        manager_name="Test Manager",
        cik="1",
        period="2026-06-30",
        accession="0000000000-26-000001",
        rows=[real_one_name],
        table_entry_total=1,
        table_value_total=100_000_000,
        infotable_bytes=15000,
        filing_bytes=20000,
        filing_date="2026-07-06",
        prior_quarters=_priors(),
    )
    assert not decision.review_required
    assert "extreme collapse in row count" in decision.corroborating
    assert "unusually early filing date" in decision.corroborating


def test_early_date_alone_is_not_a_hard_stop():
    rows = [_common_row() for _ in range(33)]
    decision = assess_anomalous_13f(
        manager_name="Test Manager",
        cik="1",
        period="2026-06-30",
        accession="0000000000-26-000002",
        rows=rows,
        table_entry_total=33,
        table_value_total=4_000_000_000,
        infotable_bytes=18000,
        filing_bytes=22000,
        filing_date="2026-07-06",
        prior_quarters=_priors(),
    )
    assert not decision.review_required
    assert "unusually early filing date" in decision.corroborating


def main():
    tests = [
        test_normalize_ticker,
        test_empty_ticker_is_fund_map_noop,
        test_valid_tickers_unchanged,
        test_classify_does_not_crash_on_nan_ticker,
        test_dummy_row_detection,
        test_eminence_stub_is_review_required,
        test_dummy_table_blocks_without_priors,
        test_decline_alone_is_not_a_hard_stop,
        test_early_date_alone_is_not_a_hard_stop,
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
