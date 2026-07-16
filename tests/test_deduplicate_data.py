import pandas as pd

from scripts.deduplicate_data import (
    compare_before_after,
    detect_exact_duplicates,
    detect_near_duplicates,
    log_removed_duplicates,
    remove_exact_duplicates,
    remove_near_duplicates,
)


def test_deduplication_functions_workflow(tmp_path):
    df = pd.DataFrame(
        [
            {"customer_id": 1, "transaction_date": "2025-01-15", "amount": 100, "status": "completed"},
            {"customer_id": 1, "transaction_date": "2025-01-15", "amount": 100, "status": "completed"},
            {"customer_id": 2, "transaction_date": "2025-01-20", "amount": 250, "status": "pending"},
            {"customer_id": 2, "transaction_date": "2025-01-20", "amount": 250, "status": "pending"},
            {"customer_id": 3, "transaction_date": "2025-02-01", "amount": 150, "status": "completed"},
            {"customer_id": 4, "transaction_date": "2025-02-10", "amount": 180, "status": "completed"},
            {"customer_id": 4, "transaction_date": "2025-02-10", "amount": 200, "status": "completed"},
        ]
    )

    exact_count, exact_rows = detect_exact_duplicates(df)
    assert exact_count == 2
    assert len(exact_rows) == 4

    dedup_exact = remove_exact_duplicates(df, keep="first")
    assert len(dedup_exact) == 5

    near_rows = detect_near_duplicates(dedup_exact, key_columns=["customer_id", "transaction_date"])
    assert len(near_rows) == 2

    dedup_final = remove_near_duplicates(
        dedup_exact,
        key_columns=["customer_id", "transaction_date"],
        keep_strategy="most_complete",
    )
    assert len(dedup_final) == 4
    assert dedup_final.loc[dedup_final["customer_id"] == 4, "amount"].iloc[0] == 180

    removed_records, audit_summary = log_removed_duplicates(df, dedup_final, output_dir=tmp_path)
    assert len(removed_records) == 3
    assert audit_summary["total_removed"] == 3
    assert (tmp_path / "removed_duplicates_audit.csv").exists()

    comparison = compare_before_after(df, dedup_final, output_dir=tmp_path)
    assert comparison["rows_before"] == 7
    assert comparison["rows_after"] == 4
    assert comparison["rows_removed"] == 3
