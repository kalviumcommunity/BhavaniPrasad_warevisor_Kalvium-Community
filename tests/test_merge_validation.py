import pandas as pd

from scripts.merge_validation import (
    build_join_report,
    compare_join_types,
    detect_unmatched_keys,
    validate_merge,
)


def test_merge_validation_workflow():
    customers = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "customer_name": ["Alice", "Bob", "Carol"],
        }
    )
    orders = pd.DataFrame(
        {
            "customer_id": [1, 1, 4],
            "order_id": [101, 102, 103],
            "amount": [100, 150, 50],
        }
    )

    merged = validate_merge(customers, orders, on="customer_id", how="left")
    assert len(merged) == 4

    unmatched_customers, unmatched_orders = detect_unmatched_keys(customers, orders, on="customer_id")
    assert len(unmatched_customers) == 2
    assert len(unmatched_orders) == 1

    summary = compare_join_types(customers, orders, on="customer_id")
    assert summary["inner"]["rows"] == 2
    assert summary["left"]["rows"] == 4
    assert summary["outer"]["rows"] == 5

    report = build_join_report(customers, orders, merged, unmatched_customers, unmatched_orders, how="left")
    assert report["join_type"] == "left"
    assert report["result_rows"] == 4
    assert report["unmatched_left"] == 2
    assert report["unmatched_right"] == 1
