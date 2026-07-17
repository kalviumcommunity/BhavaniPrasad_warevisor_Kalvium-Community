from __future__ import annotations

import pandas as pd

from scripts.data_workflow import detect_iqr_outliers, detect_zscore_outliers, process_data


def test_outlier_detection_and_logging(tmp_path):
    df = pd.DataFrame(
        [
            {"customer_id": 1, "customer_name": "Alice", "transaction_amount": 10.0, "transaction_date": "2025-01-01"},
            {"customer_id": 2, "customer_name": "Bob", "transaction_amount": 12.0, "transaction_date": "2025-01-02"},
            {"customer_id": 3, "customer_name": "Carol", "transaction_amount": 11.0, "transaction_date": "2025-01-03"},
            {"customer_id": 4, "customer_name": "Dave", "transaction_amount": 500.0, "transaction_date": "2025-01-04"},
        ]
    )

    z_mask, z_scores = detect_zscore_outliers(df["transaction_amount"])
    assert z_mask.sum() == 1
    assert z_scores.iloc[-1] > 3

    iqr_mask, lower_bound, upper_bound = detect_iqr_outliers(df["transaction_amount"])
    assert iqr_mask.sum() == 1
    assert lower_bound < upper_bound
    assert upper_bound < 500

    log_path = tmp_path / "cleaning_log.csv"
    processed = process_data(df, cleaning_log_path=log_path)

    assert "transaction_amount_zscore" in processed.columns
    assert "transaction_amount_capped" in processed.columns
    assert "is_outlier_iqr" in processed.columns
    assert "is_outlier" in processed.columns
    assert processed["is_outlier"].sum() == 1
    assert processed.loc[processed["customer_id"] == 4, "transaction_amount_capped"].iloc[0] < 500
    assert processed["is_high_value"].dtype == bool
    assert log_path.exists()

    log_df = pd.read_csv(log_path)
    assert set(log_df["method"]) == {"Z-Score", "IQR", "Combined"}
    assert set(log_df["action"]) == {"flag", "cap"}
