"""Refactor analytical SQL queries to demonstrate common optimization patterns.

This module builds a small SQLite demo database so the original and optimized
queries from the assignment can be executed locally. The workflow captures
result-size comparisons, lightweight timing data, and a markdown report that
summarizes the optimization choices.
"""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
import time
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"
DEFAULT_REPORT_PATH = DEFAULT_OUTPUT_DIR / "query_optimization_report.md"

TASK_1_ORIGINAL_QUERY = """
SELECT *
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE YEAR(t.transaction_date) = 2024
LIMIT 1000;
""".strip()

TASK_1_OPTIMIZED_QUERY = """
SELECT
    t.transaction_id,  -- Unique transaction ID for traceability in dashboards
    t.transaction_date,  -- Answers when the sale happened for trend analysis
    t.amount,  -- Measures revenue contribution for finance reporting
    t.customer_id,  -- Links the transaction back to the customer record
    c.customer_name,  -- Identifies the customer in operational reports
    c.country,  -- Supports regional analysis and segmentation
    c.account_type  -- Explains the account relationship in B2B/B2C reporting
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE YEAR(t.transaction_date) = 2024
LIMIT 1000;
""".strip()

TASK_2_ORIGINAL_QUERY = """
SELECT t.transaction_id, t.amount, c.customer_name, p.product_name
FROM transactions t
JOIN customers c ON t.customer_id = c.id
JOIN products p ON t.product_id = p.id
WHERE t.transaction_date >= '2024-01-01'
  AND t.amount > 100
  AND c.country = 'USA'
LIMIT 5000;
""".strip()

TASK_2_OPTIMIZED_QUERY = """
WITH filtered_transactions AS (
    SELECT transaction_id, customer_id, product_id, amount, transaction_date
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
      AND amount > 100
)
SELECT ft.transaction_id, ft.amount, c.customer_name, p.product_name
FROM filtered_transactions ft
JOIN customers c ON ft.customer_id = c.id
JOIN products p ON ft.product_id = p.id
WHERE c.country = 'USA'
LIMIT 5000;
""".strip()

TASK_3_ORIGINAL_QUERY = """
SELECT customer_segment, transaction_count, avg_transaction_value, total_revenue
FROM (
    SELECT
        c.customer_segment,
        AVG(t.amount) as avg_transaction_value,
        COUNT(DISTINCT t.transaction_id) as transaction_count,
        SUM(t.amount) as total_revenue
    FROM (
        SELECT t.transaction_id, t.amount, t.customer_id
        FROM transactions t
        WHERE t.transaction_date >= '2024-01-01'
    ) t
    JOIN customers c ON t.customer_id = c.id
    GROUP BY c.customer_segment
) grouped
ORDER BY avg_transaction_value DESC;
""".strip()

TASK_3_REFACTORED_QUERY = """
WITH recent_transactions AS (
    -- Step 1: Filter to recent transaction data before any join work begins.
    SELECT transaction_id, amount, customer_id
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
),
customer_with_segment AS (
    -- Step 2: Attach the customer segment to each recent transaction.
    SELECT
        rt.transaction_id,
        rt.amount,
        c.customer_segment
    FROM recent_transactions rt
    JOIN customers c ON rt.customer_id = c.id
),
segment_metrics AS (
    -- Step 3: Aggregate by segment to produce business-facing metrics.
    SELECT
        customer_segment,
        COUNT(DISTINCT transaction_id) as transaction_count,
        AVG(amount) as avg_transaction_value,
        SUM(amount) as total_revenue
    FROM customer_with_segment
    GROUP BY customer_segment
)
SELECT
    customer_segment,
    transaction_count,
    avg_transaction_value,
    total_revenue
FROM segment_metrics
ORDER BY avg_transaction_value DESC;
""".strip()


@dataclass(slots=True)
class QueryMetrics:
    """Capture timing and result-size information for a query run."""

    elapsed_ms: float
    rows: int
    columns: int
    memory_bytes: int


def _year(value: Any) -> int | None:
    """SQLite helper that mimics YEAR(date) for ISO date strings."""
    if value is None:
        return None
    text = str(value)
    return int(text[:4])


def create_demo_connection() -> sqlite3.Connection:
    """Create an in-memory SQLite database populated with demo analytical data."""
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.create_function("YEAR", 1, _year)
    build_demo_database(connection)
    return connection


def build_demo_database(connection: sqlite3.Connection) -> None:
    """Create tables and insert deterministic sample data for the assignment queries."""
    connection.executescript(
        """
        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS products;

        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            country TEXT NOT NULL,
            account_type TEXT NOT NULL,
            customer_segment TEXT NOT NULL
        );

        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL
        );

        CREATE TABLE transactions (
            transaction_id INTEGER PRIMARY KEY,
            transaction_date TEXT NOT NULL,
            amount REAL NOT NULL,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
        """
    )

    customers = pd.DataFrame(
        [
            (1, "Aster Retail", "USA", "Enterprise", "SMB"),
            (2, "Northwind Labs", "USA", "Growth", "Enterprise"),
            (3, "Blue Pine", "Canada", "Starter", "SMB"),
            (4, "Summit Goods", "USA", "Enterprise", "Mid-Market"),
            (5, "Orbit Commerce", "UK", "Growth", "Enterprise"),
            (6, "Harbor Group", "USA", "Starter", "SMB"),
        ],
        columns=["id", "customer_name", "country", "account_type", "customer_segment"],
    )

    products = pd.DataFrame(
        [
            (1, "Analytics Pro", "Software"),
            (2, "Support Plus", "Services"),
            (3, "Warehouse Sync", "Software"),
            (4, "Onboarding Pack", "Services"),
        ],
        columns=["id", "product_name", "category"],
    )

    transactions = pd.DataFrame(
        [
            (1, "2023-12-28", 95.0, 1, 1),
            (2, "2024-01-05", 120.0, 1, 2),
            (3, "2024-01-12", 240.0, 2, 1),
            (4, "2024-02-08", 80.0, 3, 3),
            (5, "2024-02-15", 310.0, 4, 1),
            (6, "2024-03-03", 150.0, 5, 4),
            (7, "2024-04-01", 180.0, 6, 2),
            (8, "2024-04-10", 75.0, 2, 3),
            (9, "2024-05-17", 410.0, 4, 4),
            (10, "2024-06-21", 220.0, 1, 1),
            (11, "2024-07-09", 160.0, 6, 3),
            (12, "2024-08-30", 340.0, 2, 2),
        ],
        columns=["transaction_id", "transaction_date", "amount", "customer_id", "product_id"],
    )

    customers.to_sql("customers", connection, if_exists="append", index=False)
    products.to_sql("products", connection, if_exists="append", index=False)
    transactions.to_sql("transactions", connection, if_exists="append", index=False)


def run_query(connection: sqlite3.Connection, query: str) -> pd.DataFrame:
    """Execute a SQL query with pandas and return the resulting DataFrame."""
    return pd.read_sql_query(query, connection)


def measure_query(connection: sqlite3.Connection, query: str) -> tuple[pd.DataFrame, QueryMetrics]:
    """Run a query and capture elapsed time and result memory usage."""
    start = time.perf_counter()
    result = run_query(connection, query)
    elapsed_ms = (time.perf_counter() - start) * 1000
    memory_bytes = int(result.memory_usage(deep=True).sum())
    metrics = QueryMetrics(
        elapsed_ms=elapsed_ms,
        rows=len(result),
        columns=len(result.columns),
        memory_bytes=memory_bytes,
    )
    return result, metrics


def format_bytes(value: int) -> str:
    """Format byte counts into a readable string."""
    if value < 1024:
        return f"{value} B"
    if value < 1024**2:
        return f"{value / 1024:.1f} KB"
    return f"{value / 1024**2:.1f} MB"


def build_summary_table(task_1: dict[str, Any], task_2: dict[str, Any], task_3: dict[str, Any]) -> pd.DataFrame:
    """Create a compact comparison table for the final assignment write-up."""
    return pd.DataFrame(
        {
            "Metric": [
                "Columns Selected",
                "Intermediate Rows",
                "Filters Applied Before Join",
                "Nesting Depth",
                "Readability Score",
            ],
            "Original": [
                f"{task_1['original_columns']} columns via SELECT *",
                f"{task_2['transactions_rows']:,} rows before filtering",
                "No",
                "3 levels",
                "Hard to follow",
            ],
            "Optimized": [
                f"{task_1['optimized_columns']} explicit columns",
                f"{task_2['filtered_rows']:,} rows before joining",
                "Yes",
                "1 level (CTEs)",
                "Clear steps",
            ],
        }
    )


def build_report(
    task_1: dict[str, Any],
    task_2: dict[str, Any],
    task_3: dict[str, Any],
    summary: pd.DataFrame,
) -> str:
    """Render a markdown report that documents the optimization work."""
    lines: list[str] = []
    lines.append("# Analytical SQL Query Optimisation Report")
    lines.append("")
    lines.append("## Summary Table")
    lines.append("")
    lines.append(summary.to_markdown(index=False))
    lines.append("")
    lines.append("## Task 1: Explicit Columns")
    lines.append("")
    lines.append("### Original")
    lines.append("")
    lines.append("```sql")
    lines.append(TASK_1_ORIGINAL_QUERY)
    lines.append("```")
    lines.append("")
    lines.append("### Optimized")
    lines.append("")
    lines.append("```sql")
    lines.append(TASK_1_OPTIMIZED_QUERY)
    lines.append("```")
    lines.append("")
    lines.append(
        f"Original query returned {task_1['original_metrics'].rows} rows and {task_1['original_metrics'].columns} columns in {task_1['original_metrics'].elapsed_ms:.2f} ms."
    )
    lines.append(
        f"Optimized query returned {task_1['optimized_metrics'].rows} rows and {task_1['optimized_metrics'].columns} columns in {task_1['optimized_metrics'].elapsed_ms:.2f} ms."
    )
    lines.append(
        f"The optimized result used {format_bytes(task_1['optimized_metrics'].memory_bytes)} versus {format_bytes(task_1['original_metrics'].memory_bytes)} for the full SELECT * result."
    )
    lines.append("")
    lines.append("## Task 2: Filter Before Join")
    lines.append("")
    lines.append("### Original")
    lines.append("")
    lines.append("```sql")
    lines.append(TASK_2_ORIGINAL_QUERY)
    lines.append("```")
    lines.append("")
    lines.append("### Optimized")
    lines.append("")
    lines.append("```sql")
    lines.append(TASK_2_OPTIMIZED_QUERY)
    lines.append("```")
    lines.append("")
    lines.append(f"Transactions table size: {task_2['transactions_rows']:,} rows.")
    lines.append(
        f"Filtered transactions before join: {task_2['filtered_rows']:,} rows ({task_2['filtered_ratio']:.1f}% of the base table)."
    )
    lines.append(
        f"Reduction factor before joining: {task_2['reduction_factor']:.2f}x smaller intermediate dataset."
    )
    lines.append("")
    lines.append("## Task 3: CTE Readability")
    lines.append("")
    lines.append("### Original")
    lines.append("")
    lines.append("```sql")
    lines.append(TASK_3_ORIGINAL_QUERY)
    lines.append("```")
    lines.append("")
    lines.append("### Refactored")
    lines.append("")
    lines.append("```sql")
    lines.append(TASK_3_REFACTORED_QUERY)
    lines.append("```")
    lines.append("")
    lines.append("## Follow-up Answers")
    lines.append("")
    lines.append("1. An index on a high-cardinality filter column helps the database find matching rows without scanning the full table, which reduces I/O and improves selective filters. The tradeoff is slower writes and extra storage because the index must be maintained on INSERT, UPDATE, and DELETE.")
    lines.append("")
    lines.append("2. CTE behavior depends on the database. In SQLite, a CTE may be inlined or materialized depending on the query planner, so repeated references are not guaranteed to be cached the same way everywhere. Some databases expose explicit MATERIALIZED or NOT MATERIALIZED control to make that behavior predictable.")
    lines.append("")
    lines.append("3. If the filtered dataset is still very large, partitioning, materialized views, pre-aggregated summary tables, and incremental rollups can reduce the amount of data scanned and joined.")
    return "\n".join(lines)


def run_query_optimization_workflow(output_dir: str | Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """Execute the three refactored queries and write the comparison report."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with create_demo_connection() as connection:
        original_task_1, original_task_1_metrics = measure_query(connection, TASK_1_ORIGINAL_QUERY)
        optimized_task_1, optimized_task_1_metrics = measure_query(connection, TASK_1_OPTIMIZED_QUERY)

        task_1_comparison_columns = [
            "transaction_id",
            "transaction_date",
            "amount",
            "customer_id",
            "customer_name",
            "country",
            "account_type",
        ]
        pd.testing.assert_frame_equal(
            original_task_1[task_1_comparison_columns].reset_index(drop=True),
            optimized_task_1.reset_index(drop=True),
        )

        transactions_rows = int(run_query(connection, "SELECT COUNT(*) AS count FROM transactions").iloc[0, 0])
        filtered_rows = int(
            run_query(
                connection,
                """
                SELECT COUNT(*) AS count
                FROM transactions
                WHERE transaction_date >= '2024-01-01'
                  AND amount > 100
                """.strip(),
            ).iloc[0, 0]
        )

        original_task_2, original_task_2_metrics = measure_query(connection, TASK_2_ORIGINAL_QUERY)
        optimized_task_2, optimized_task_2_metrics = measure_query(connection, TASK_2_OPTIMIZED_QUERY)
        pd.testing.assert_frame_equal(
            original_task_2.reset_index(drop=True),
            optimized_task_2.reset_index(drop=True),
        )

        original_task_3, original_task_3_metrics = measure_query(connection, TASK_3_ORIGINAL_QUERY)
        optimized_task_3, optimized_task_3_metrics = measure_query(connection, TASK_3_REFACTORED_QUERY)
        pd.testing.assert_frame_equal(
            original_task_3.reset_index(drop=True),
            optimized_task_3.reset_index(drop=True),
        )

    task_1 = {
        "original_metrics": original_task_1_metrics,
        "optimized_metrics": optimized_task_1_metrics,
        "original_columns": len(original_task_1.columns),
        "optimized_columns": len(optimized_task_1.columns),
    }
    task_2 = {
        "transactions_rows": transactions_rows,
        "filtered_rows": filtered_rows,
        "filtered_ratio": (filtered_rows / transactions_rows) * 100 if transactions_rows else 0.0,
        "reduction_factor": (transactions_rows / filtered_rows) if filtered_rows else float("inf"),
        "original_metrics": original_task_2_metrics,
        "optimized_metrics": optimized_task_2_metrics,
    }
    task_3 = {
        "original_metrics": original_task_3_metrics,
        "optimized_metrics": optimized_task_3_metrics,
    }

    summary = build_summary_table(task_1, task_2, task_3)
    report = build_report(task_1, task_2, task_3, summary)

    report_path = output_dir / "query_optimization_report.md"
    report_path.write_text(report, encoding="utf-8")

    return {
        "task_1": task_1,
        "task_2": task_2,
        "task_3": task_3,
        "summary": summary,
        "report_path": report_path,
    }


if __name__ == "__main__":
    results = run_query_optimization_workflow()
    print(results["summary"].to_string(index=False))
    print(f"Report written to {results['report_path']}")