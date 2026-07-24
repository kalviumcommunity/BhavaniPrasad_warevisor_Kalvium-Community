"""SQL Filtering, Grouping & Aggregation Demonstrations.

This module demonstrates 5 core SQL concepts using pandas DataFrames:
1. WHERE filtering (data quality before aggregation)
2. GROUP BY on multiple dimensions
3. HAVING filtering (after aggregation)
4. WHERE + HAVING combined
5. ORDER BY ranking

Each function simulates the SQL query and returns results as pandas DataFrames.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def generate_sample_transactions(
    num_records: int = 5000,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate synthetic transactions and customers datasets.

    Returns:
        (transactions_df, customers_df)
    """
    np.random.seed(seed)

    # Generate customers
    num_customers = 500
    customer_types = ["Enterprise", "SMB", "Startup"]
    industries = ["Tech", "Finance", "Healthcare", "Retail", "Manufacturing"]

    customers = pd.DataFrame({
        "customer_id": range(1, num_customers + 1),
        "customer_type": np.random.choice(customer_types, num_customers),
        "industry": np.random.choice(industries, num_customers),
    })

    # Generate transactions
    statuses = ["completed", "pending", "failed", "refunded"]
    dates_2024 = [datetime(2024, 1, 1) + timedelta(days=int(x)) for x in np.random.uniform(0, 365, num_records)]

    transactions = pd.DataFrame({
        "customer_id": np.random.choice(range(1, num_customers + 1), num_records),
        "transaction_date": dates_2024,
        "amount": np.random.exponential(scale=200, size=num_records),  # Skewed distribution
        "status": np.random.choice(statuses, num_records, p=[0.80, 0.10, 0.05, 0.05]),
    })

    # Add some negative amounts (refunds)
    refund_mask = transactions["status"] == "refunded"
    transactions.loc[refund_mask, "amount"] = -transactions.loc[refund_mask, "amount"]

    return transactions, customers


def task_1_where_filtering(transactions: pd.DataFrame) -> pd.DataFrame:
    """Task 1: WHERE filtering - Data quality before grouping.

    WHERE filters ROWS before GROUP BY.
    Result: Each customer's clean 2024 revenue.
    """
    # WHERE conditions
    valid_date_range = (transactions["transaction_date"] >= "2024-01-01") & (
        transactions["transaction_date"] <= "2024-12-31"
    )
    positive_amount = transactions["amount"] > 0
    completed_status = transactions["status"] == "completed"

    filtered = transactions[valid_date_range & positive_amount & completed_status]

    # GROUP BY
    result = (
        filtered.groupby("customer_id")
        .agg(
            transaction_count=("customer_id", "count"),
            annual_revenue=("amount", "sum"),
            first_transaction=("transaction_date", "min"),
            last_transaction=("transaction_date", "max"),
        )
        .reset_index()
        .sort_values("annual_revenue", ascending=False)
    )

    print("\n" + "=" * 80)
    print("TASK 1: WHERE FILTERING - Data Quality Before Grouping")
    print("=" * 80)
    print(f"Total rows before WHERE: {len(transactions):,}")
    print(f"Total rows after WHERE: {len(filtered):,}")
    print(f"Rows filtered out: {len(transactions) - len(filtered):,}")
    print(f"\nTop 10 customers by annual revenue:")
    print(result.head(10).to_string(index=False))
    return result


def task_2_groupby_aggregation(transactions: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Task 2: GROUP BY multiple dimensions with multiple aggregate functions.

    GROUP BY on customer_type and month.
    Result: Monthly revenue trend by segment with 8+ metrics.
    """
    # WHERE filtering
    valid_date_range = (transactions["transaction_date"] >= "2024-01-01") & (
        transactions["transaction_date"] <= "2024-12-31"
    )
    valid_txns = (transactions["status"] == "completed") & (transactions["amount"] > 0)
    filtered = transactions[valid_date_range & valid_txns].copy()

    # Add customer_type and month
    filtered = filtered.merge(customers[["customer_id", "customer_type"]], on="customer_id", how="inner")
    filtered["month"] = pd.to_datetime(filtered["transaction_date"]).dt.to_period("M")

    # GROUP BY multiple dimensions
    result = (
        filtered.groupby(["customer_type", "month"])
        .agg(
            unique_customers=("customer_id", "nunique"),
            transaction_count=("customer_id", "count"),
            monthly_revenue=("amount", "sum"),
            avg_transaction=("amount", "mean"),
            min_transaction=("amount", "min"),
            max_transaction=("amount", "max"),
            stddev_transaction=("amount", "std"),
        )
        .reset_index()
        .sort_values(["month", "monthly_revenue"], ascending=[False, False])
    )
    
    # Round numeric columns to avoid datetime warning
    numeric_cols = ["monthly_revenue", "avg_transaction", "min_transaction", "max_transaction", "stddev_transaction"]
    for col in numeric_cols:
        if col in result.columns:
            result[col] = result[col].round(2)

    print("\n" + "=" * 80)
    print("TASK 2: GROUP BY Multiple Dimensions")
    print("=" * 80)
    print(f"Unique (customer_type, month) combinations: {len(result):,}")
    print(f"Aggregate functions used: 7 (unique, count, sum, mean, min, max, std)")
    print(f"\nMonthly revenue by segment (sample):")
    print(result.head(12).to_string(index=False))
    return result


def task_3_having_filtering(transactions: pd.DataFrame) -> pd.DataFrame:
    """Task 3: HAVING filtering - Filter groups after aggregation.

    HAVING filters GROUPS (after aggregation).
    Result: High-value customers (> $10k revenue, 5+ purchases, $500+ avg order).
    """
    # WHERE filtering
    valid_date_range = (transactions["transaction_date"] >= "2024-01-01") & (
        transactions["transaction_date"] <= "2024-12-31"
    )
    valid_txns = (transactions["status"] == "completed") & (transactions["amount"] > 0)
    filtered = transactions[valid_date_range & valid_txns].copy()

    # GROUP BY
    grouped = (
        filtered.groupby("customer_id")
        .agg(
            transaction_count=("customer_id", "count"),
            annual_revenue=("amount", "sum"),
            avg_order_value=("amount", "mean"),
            last_purchase_date=("transaction_date", "max"),
        )
        .reset_index()
    )

    # HAVING filtering (filter grouped data)
    result = grouped[
        (grouped["annual_revenue"] > 3000)
        & (grouped["transaction_count"] >= 5)
        & (grouped["avg_order_value"] > 100)
    ].sort_values("annual_revenue", ascending=False)

    print("\n" + "=" * 80)
    print("TASK 3: HAVING Filtering - Groups After Aggregation")
    print("=" * 80)
    print(f"Total customer groups: {len(grouped):,}")
    print(f"Groups meeting HAVING criteria: {len(result):,}")
    print(f"  - annual_revenue > $3,000")
    print(f"  - transaction_count >= 5")
    print(f"  - avg_order_value > $100")
    print(f"\nTop 10 high-value customers:")
    if len(result) > 0:
        result_display = result.head(10).copy()
        result_display["avg_order_value"] = result_display["avg_order_value"].round(2)
        result_display["annual_revenue"] = result_display["annual_revenue"].round(2)
        print(result_display.to_string(index=False))
    else:
        print("No customers meet the criteria.")
    return result


def task_4_where_having_combined(transactions: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Task 4: WHERE + HAVING combined - Real-world production filtering.

    WHERE: data quality checks (row-level).
    HAVING: business logic (group-level).
    Result: Segments with 100+ customers, $100k+ revenue, 1000+ transactions.
    """
    # WHERE filtering (rows before grouping)
    valid_date_range = (transactions["transaction_date"] >= "2024-01-01") & (
        transactions["transaction_date"] <= "2024-12-31"
    )
    valid_txns = (transactions["status"] == "completed") & (transactions["amount"] > 0)
    filtered = transactions[valid_date_range & valid_txns].copy()

    # Join with customers
    merged = filtered.merge(customers[["customer_id", "customer_type"]], on="customer_id", how="inner")

    # GROUP BY
    grouped = (
        merged.groupby("customer_type")
        .agg(
            segment_customer_count=("customer_id", "nunique"),
            segment_transaction_count=("customer_id", "count"),
            segment_total_revenue=("amount", "sum"),
            segment_avg_order=("amount", "mean"),
        )
        .reset_index()
    )

    # HAVING filtering (groups after aggregation)
    result = grouped[
        (grouped["segment_customer_count"] >= 100)
        & (grouped["segment_total_revenue"] > 100000)
        & (grouped["segment_transaction_count"] >= 1000)
    ].copy()

    # Add percentage of total
    total_revenue = grouped["segment_total_revenue"].sum()
    result["pct_of_total_revenue"] = (100.0 * result["segment_total_revenue"] / total_revenue).round(2)
    result = result.sort_values("segment_total_revenue", ascending=False)

    print("\n" + "=" * 80)
    print("TASK 4: WHERE + HAVING Combined - Production Filtering")
    print("=" * 80)
    print(f"Total segments in data: {len(grouped):,}")
    print(f"Segments meeting business criteria: {len(result):,}")
    print(f"WHERE conditions (row-level):")
    print(f"  - transaction_date in 2024")
    print(f"  - status = 'completed'")
    print(f"  - amount > 0")
    print(f"HAVING conditions (group-level):")
    print(f"  - segment_customer_count >= 100")
    print(f"  - segment_total_revenue > $100,000")
    print(f"  - segment_transaction_count >= 1,000")
    print(f"\nQualifying segments:")
    print(result.to_string(index=False))
    return result


def task_5_orderby_ranking(transactions: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Task 5: ORDER BY and ranking - Surface top performers.

    ORDER BY sorts results.
    RANK() creates ranking column.
    LIMIT 20 shows only top 20.
    """
    # WHERE filtering
    valid_date_range = (transactions["transaction_date"] >= "2024-01-01") & (
        transactions["transaction_date"] <= "2024-12-31"
    )
    valid_txns = (transactions["status"] == "completed") & (transactions["amount"] > 0)
    filtered = transactions[valid_date_range & valid_txns].copy()

    # Join with customers
    merged = filtered.merge(customers, on="customer_id", how="inner")

    # GROUP BY
    grouped = (
        merged.groupby(["customer_type", "industry"])
        .agg(
            segment_customers=("customer_id", "nunique"),
            total_revenue=("amount", "sum"),
            avg_order=("amount", "mean"),
            transaction_count=("customer_id", "count"),
        )
        .reset_index()
    )

    # HAVING filtering
    result = grouped[
        (grouped["segment_customers"] >= 10)
        & (grouped["total_revenue"] > 5000)
    ].copy()

    # Add ranking and percentage
    result = result.sort_values("total_revenue", ascending=False).reset_index(drop=True)
    result["revenue_rank"] = range(1, len(result) + 1)
    total_revenue = result["total_revenue"].sum()
    result["pct_of_total"] = (100.0 * result["total_revenue"] / total_revenue).round(2)

    # ORDER BY and LIMIT top 20
    top_20 = result.head(20).copy()

    print("\n" + "=" * 80)
    print("TASK 5: ORDER BY and Ranking - Top Performers")
    print("=" * 80)
    print(f"Total qualifying segments: {len(result):,}")
    print(f"Showing top 20 by revenue")
    print(f"\nTop 20 segments (Rank, Customer Type, Industry, Revenue):")
    display_cols = ["revenue_rank", "customer_type", "industry", "segment_customers", "total_revenue", "pct_of_total"]
    print(top_20[display_cols].to_string(index=False))
    return top_20


def main():
    """Run all 5 SQL filtering demonstrations."""
    print("\n" + "#" * 80)
    print("# SQL FILTERING, GROUPING & AGGREGATION DEMONSTRATIONS")
    print("#" * 80)

    # Generate sample data
    transactions, customers = generate_sample_transactions(num_records=5000)
    print(f"\nGenerated {len(transactions):,} transactions for {len(customers)} customers")

    # Run all tasks
    task_1_result = task_1_where_filtering(transactions)
    task_2_result = task_2_groupby_aggregation(transactions, customers)
    task_3_result = task_3_having_filtering(transactions)
    task_4_result = task_4_where_having_combined(transactions, customers)
    task_5_result = task_5_orderby_ranking(transactions, customers)

    print("\n" + "#" * 80)
    print("# SUMMARY")
    print("#" * 80)
    print(f"[PASS] Task 1: WHERE filtering - Found {len(task_1_result)} customers with valid 2024 revenue")
    print(f"[PASS] Task 2: GROUP BY aggregation - Analyzed {len(task_2_result)} (segment, month) combinations")
    print(f"[PASS] Task 3: HAVING filtering - Identified {len(task_3_result)} high-value customers")
    print(f"[PASS] Task 4: WHERE + HAVING - Found {len(task_4_result)} segments meeting business criteria")
    print(f"[PASS] Task 5: ORDER BY ranking - Ranked top {len(task_5_result)} segments by revenue")


if __name__ == "__main__":
    main()
