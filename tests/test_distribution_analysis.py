from __future__ import annotations

import json

import pandas as pd

from scripts.distribution_analysis import analyze_distribution, resolve_value_column


def test_analyze_distribution_creates_reports_and_plots(tmp_path):
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "transaction_amount": [10, 11, 12, 13, 14, 15, 16, 1000],
            "transaction_date": pd.date_range("2025-01-01", periods=8),
        }
    )

    assert resolve_value_column(df) == "transaction_amount"

    report = analyze_distribution(df, output_dir=tmp_path)

    report_path = tmp_path / "distribution_report.json"
    distribution_plot = tmp_path / "revenue_distribution.png"
    segment_plot = tmp_path / "revenue_segment_comparison.png"

    assert report["column"] == "transaction_amount"
    assert report["skewness"] > 1
    assert report["kurtosis"] > 3
    assert report["segment_comparison"]["high_value_mean"] > report["segment_comparison"]["low_value_mean"]
    assert distribution_plot.exists()
    assert segment_plot.exists()
    assert report_path.exists()

    with open(report_path, "r", encoding="utf-8") as file_handle:
        saved_report = json.load(file_handle)

    assert saved_report["column"] == "transaction_amount"
    assert saved_report["abnormal_patterns"]