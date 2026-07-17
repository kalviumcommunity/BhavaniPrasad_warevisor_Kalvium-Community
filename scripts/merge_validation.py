"""Validate merges between customer and order-like datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CUSTOMERS = REPO_ROOT / "data" / "raw" / "customers.csv"
DEFAULT_ORDERS = REPO_ROOT / "data" / "raw" / "orders.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"
DEFAULT_MERGED_OUTPUT = REPO_ROOT / "data" / "processed" / "merged_customers_orders.csv"


def validate_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: str,
    how: str = "left",
) -> pd.DataFrame:
    """Perform an explicit merge and print row-count validation details."""
    print(f"Left rows: {len(left)}")
    print(f"Right rows: {len(right)}")

    merged = pd.merge(left, right, on=on, how=how)

    print(f"Merged rows: {len(merged)}")
    print(f"Row change: {len(merged) - len(left)}")
    return merged


def detect_unmatched_keys(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Find keys that exist on one side but not the other."""
    unmatched_left = left[~left[on].isin(right[on])]
    unmatched_right = right[~right[on].isin(left[on])]

    print(f"Unmatched left rows: {len(unmatched_left)}")
    print(f"Unmatched right rows: {len(unmatched_right)}")
    return unmatched_left, unmatched_right


def compare_join_types(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: str,
) -> dict[str, dict[str, Any]]:
    """Compare row counts for inner, left, and outer joins."""
    joins = {
        "inner": pd.merge(left, right, on=on, how="inner"),
        "left": pd.merge(left, right, on=on, how="left"),
        "right": pd.merge(left, right, on=on, how="right"),
        "outer": pd.merge(left, right, on=on, how="outer"),
    }

    summary: dict[str, dict[str, Any]] = {}
    for name, frame in joins.items():
        summary[name] = {"rows": len(frame), "columns": len(frame.columns)}

    return summary


def build_join_report(
    left: pd.DataFrame,
    right: pd.DataFrame,
    merged: pd.DataFrame,
    unmatched_left: pd.DataFrame,
    unmatched_right: pd.DataFrame,
    how: str,
) -> dict[str, Any]:
    """Create a human-readable join-validation report."""
    report = {
        "join_type": how,
        "left_table": "customers",
        "right_table": "orders",
        "join_key": "customer_id",
        "left_rows": len(left),
        "right_rows": len(right),
        "result_rows": len(merged),
        "unmatched_left": len(unmatched_left),
        "unmatched_right": len(unmatched_right),
        "reasoning": "Left join preserves all customers while still attaching matching orders; unmatched customers are expected if they have no orders.",
    }
    return report


def save_outputs(
    merged: pd.DataFrame,
    unmatched_left: pd.DataFrame,
    unmatched_right: pd.DataFrame,
    report: dict[str, Any],
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    merged_output: str | Path = DEFAULT_MERGED_OUTPUT,
) -> None:
    """Persist merge outputs and validation artifacts to disk."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    merged.to_csv(merged_output, index=False)
    unmatched_left.to_csv(output_dir / "unmatched_customers.csv", index=False)
    unmatched_right.to_csv(output_dir / "unmatched_orders.csv", index=False)

    with (output_dir / "join_validation_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)


def run_merge_validation_workflow(
    customers_path: str | Path = DEFAULT_CUSTOMERS,
    orders_path: str | Path = DEFAULT_ORDERS,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    merged_output: str | Path = DEFAULT_MERGED_OUTPUT,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load two sample datasets, validate a left join, and save outputs."""
    if not Path(customers_path).exists() or not Path(orders_path).exists():
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
    else:
        customers = pd.read_csv(customers_path)
        orders = pd.read_csv(orders_path)

    merged = validate_merge(customers, orders, on="customer_id", how="left")
    unmatched_left, unmatched_right = detect_unmatched_keys(customers, orders, on="customer_id")
    report = build_join_report(customers, orders, merged, unmatched_left, unmatched_right, how="left")
    save_outputs(merged, unmatched_left, unmatched_right, report, output_dir=output_dir, merged_output=merged_output)
    return merged, report


if __name__ == "__main__":
    run_merge_validation_workflow()
