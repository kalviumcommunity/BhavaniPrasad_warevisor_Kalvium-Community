import pandas as pd

from scripts.rolling_metrics import build_time_series_metrics, save_rolling_plot, write_trend_report


def test_rolling_metrics_compute_resampling_rolling_and_trend(tmp_path):
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5, 6],
            "transaction_amount": [10, 20, 30, 40, 50, 60],
            "transaction_date": [
                "2025-01-01",
                "2025-01-02",
                "2025-01-08",
                "2025-01-15",
                "2025-02-01",
                "2025-02-10",
            ],
        }
    )

    metrics = build_time_series_metrics(df)

    assert "weekly" in metrics
    assert "monthly" in metrics
    assert "rolling_7" in metrics
    assert "rolling_30" in metrics
    assert "mom_change" in metrics
    assert metrics["trend_direction"] in {"up", "down", "flat"}
    assert isinstance(metrics["report"], str)

    plot_file = save_rolling_plot(metrics, tmp_path / "rolling_avg.png")
    report_file = write_trend_report(metrics["report"], tmp_path / "trend_analysis.txt")

    assert plot_file.exists()
    assert report_file.exists()
    assert "TREND ANALYSIS" in report_file.read_text(encoding="utf-8")