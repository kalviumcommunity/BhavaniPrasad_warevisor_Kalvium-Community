import pandas as pd

from scripts.rolling_metrics import (
    build_anomaly_monitoring,
    build_time_series_metrics,
    check_thresholds,
    save_anomaly_log,
    save_anomaly_plot,
    save_rolling_plot,
    write_trend_report,
)


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


def test_anomaly_monitoring_thresholds_and_visualization(tmp_path):
    df = pd.DataFrame(
        {
            "customer_id": list(range(1, 36)),
            "transaction_amount": [100.0] * 29 + [400.0] + [100.0] * 5,
            "transaction_date": pd.date_range("2025-03-01", periods=35, freq="D").astype(str),
        }
    )

    metrics = build_time_series_metrics(df)

    rules = {
        "daily_revenue": {"min": 5000, "max": 50000},
        "transaction_count": {"min": 100, "max": 10000},
        "signup_rate": {"min": 10, "max": 500},
    }
    alerts = check_thresholds(
        {"daily_revenue": 2500, "transaction_count": 12000, "signup_rate": 50},
        rules,
    )
    assert len(alerts) == 2
    assert {alert["metric"] for alert in alerts} == {"daily_revenue", "transaction_count"}
    assert all("threshold" in alert for alert in alerts)

    anomaly_summary = build_anomaly_monitoring(metrics, threshold=2.0, lookback_days=30)

    assert len(anomaly_summary["anomalies"]) == 1
    assert anomaly_summary["anomaly_log"].shape[0] == 1
    assert anomaly_summary["anomaly_log"].iloc[0]["severity"] == "CRITICAL"
    assert anomaly_summary["high_severity_anomalies"].shape[0] == 1
    assert anomaly_summary["anomaly_log"].iloc[0]["status"] == "OPEN"
    assert anomaly_summary["z_scores"].max() > 2

    log_file = save_anomaly_log(anomaly_summary["anomaly_log"], tmp_path / "anomalies_log.csv")
    plot_file = save_anomaly_plot(metrics, anomaly_summary, tmp_path / "anomaly_detection.png")

    assert log_file.exists()
    assert plot_file.exists()

    log_df = pd.read_csv(log_file)
    assert list(log_df["metric"].unique()) == ["daily_revenue"]
    assert log_df["z_score"].iloc[0] > 2