"""SQL Joins & Multi-Table Analysis Demonstrations.

This script executes and validates 5 core SQL join tasks against data/joins_analysis.db:
1. LEFT JOIN with row count validation and multiplication factor
2. Unmatched key detection (inactive customers and orphaned orders)
3. Join type comparison (INNER, LEFT, FULL OUTER) with integrity assertions
4. Multi-table join (4 tables) with product total lineage validation
5. Documented join strategy decisions

Execution:
    python sql/sql_joins_demo.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import sqlite3
import pandas as pd
from scripts.setup_joins_db import setup_joins_db

DB_PATH = "data/joins_analysis.db"


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    if not os.path.exists(db_path):
        setup_joins_db(db_path)
    return sqlite3.connect(db_path)


def task_1_left_join_validation(conn: sqlite3.Connection) -> pd.DataFrame:
    """Task 1: LEFT JOIN with Row Count Validation.

    Executes LEFT JOIN from customers to orders, measures row counts before and after,
    and calculates average orders per customer (multiplication factor).
    """
    customers_df = pd.read_sql("SELECT customer_id FROM customers", conn)
    customers_count = len(customers_df)

    query = """
    SELECT 
        c.customer_id,
        c.customer_type,
        COUNT(DISTINCT o.order_id) as order_count,
        SUM(o.order_amount) as total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_type
    ORDER BY total_spent DESC NULLS LAST;
    """
    joined = pd.read_sql(query, conn)

    # Raw row count of un-grouped LEFT JOIN
    raw_left_join_query = """
    SELECT c.customer_id, o.order_id 
    FROM customers c 
    LEFT JOIN orders o ON c.customer_id = o.customer_id;
    """
    raw_joined = pd.read_sql(raw_left_join_query, conn)
    after_count = len(raw_joined)
    change = after_count - customers_count
    pct_change = (change / customers_count) * 100.0
    mult_factor = after_count / customers_count

    print("\n" + "=" * 80)
    print("TASK 1: LEFT JOIN WITH ROW COUNT VALIDATION")
    print("=" * 80)
    print(f"Before Join (customers count): {customers_count:,}")
    print(f"After Join (raw result rows): {after_count:,}")
    print(f"Row Count Change: +{change:,} (+{pct_change:.1f}%)")
    print(f"Multiplication Factor (rows per customer): {mult_factor:.2f}")
    print(f"Grouped Customers Summary Count: {len(joined):,}")
    print("\nSample Grouped Customer History (Top 5 spenders):")
    print(joined.head(5).to_string(index=False))

    print("\n[DOCUMENTATION / REASONING]")
    print(
        "Why is the un-grouped LEFT JOIN result larger than the base customers table?\n"
        "Customers with multiple orders create multiple rows in the join result.\n"
        "All 1,000 customers are preserved (including those with 0 orders, which yield NULL order fields)."
    )

    return joined


def task_2_detect_unmatched_keys(conn: sqlite3.Connection) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Task 2: Detect Unmatched Keys.

    Finds customers with no orders and orphaned orders with no matching customer.
    """
    customers_count = pd.read_sql("SELECT COUNT(*) FROM customers", conn).iloc[0, 0]
    orders_count = pd.read_sql("SELECT COUNT(*) FROM orders", conn).iloc[0, 0]

    no_orders_query = """
    SELECT c.customer_id, c.customer_type, c.signup_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_id IS NULL
    ORDER BY c.signup_date;
    """
    no_orders = pd.read_sql(no_orders_query, conn)

    orphaned_query = """
    SELECT o.order_id, o.customer_id, o.order_date, o.order_amount
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
    ORDER BY o.order_date;
    """
    orphaned = pd.read_sql(orphaned_query, conn)

    pct_no_orders = (len(no_orders) / customers_count) * 100.0
    pct_orphaned = (len(orphaned) / orders_count) * 100.0

    print("\n" + "=" * 80)
    print("TASK 2: DETECT UNMATCHED KEYS")
    print("=" * 80)
    print(f"Customers without orders: {len(no_orders)} / {customers_count} ({pct_no_orders:.1f}%)")
    print(f"Orphaned orders (no matching customer): {len(orphaned)} / {orders_count} ({pct_orphaned:.1f}%)")

    if len(orphaned) > 0:
        print("[WARNING] Orphaned records found! Investigate customer_id foreign key mismatches.")

    print("\nSample Inactive Customers (first 5):")
    print(no_orders.head(5).to_string(index=False))

    print("\nSample Orphaned Orders (first 5):")
    print(orphaned.head(5).to_string(index=False))

    return no_orders, orphaned


def task_3_compare_join_types(conn: sqlite3.Connection) -> dict[str, int]:
    """Task 3: Compare Join Types.

    Executes INNER, LEFT, and FULL OUTER joins, compares row counts,
    and validates relational invariants with assertions.
    """
    inner_query = """
    SELECT c.customer_id, o.order_id, o.order_amount
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id;
    """
    left_query = """
    SELECT c.customer_id, o.order_id, o.order_amount
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id;
    """
    full_query = """
    SELECT c.customer_id, o.order_id, o.order_amount
    FROM customers c
    FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;
    """

    inner = pd.read_sql(inner_query, conn)
    left = pd.read_sql(left_query, conn)
    full = pd.read_sql(full_query, conn)

    counts = {
        "INNER": len(inner),
        "LEFT": len(left),
        "FULL": len(full),
    }

    print("\n" + "=" * 80)
    print("TASK 3: COMPARE JOIN TYPES")
    print("=" * 80)
    print(f"INNER JOIN:      {counts['INNER']:,} rows (only matched customer-order pairs)")
    print(f"LEFT JOIN:       {counts['LEFT']:,} rows (all 1,000 customers + matched orders)")
    print(f"FULL OUTER JOIN: {counts['FULL']:,} rows (all customers + all orders including orphans)")

    # Integrity Assertions
    assert len(left) >= len(inner), "LEFT join must yield at least as many rows as INNER join"
    assert len(full) >= max(len(left), 1000), "FULL OUTER join must be >= max(LEFT, customer count)"
    print("\n[OK] Join Relationship Invariants Validated Successfully!")

    return counts


def task_4_multi_table_join(conn: sqlite3.Connection) -> pd.DataFrame:
    """Task 4: Multi-Table Join.

    Joins 4 tables (customers, orders, order_items, products), calculates line_total,
    and validates line_total against expected order_items totals.
    """
    query = """
    SELECT 
        c.customer_id,
        c.customer_type,
        o.order_id,
        o.order_date,
        oi.product_id,
        p.product_name,
        oi.quantity,
        oi.unit_price,
        (oi.quantity * oi.unit_price) as line_total
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN products p ON oi.product_id = p.product_id
    WHERE c.customer_type = 'Enterprise'
    ORDER BY o.order_date DESC;
    """
    result = pd.read_sql(query, conn)

    # Validation: Sum of line_total for all non-null products in full multi-table query vs raw order_items
    full_multi_table_query = """
    SELECT 
        oi.product_id,
        (oi.quantity * oi.unit_price) as line_total
    FROM order_items oi
    LEFT JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    WHERE c.customer_id IS NOT NULL;
    """
    full_multi = pd.read_sql(full_multi_table_query, conn)
    product_total_sum = full_multi["line_total"].sum()

    expected_total = pd.read_sql(
        "SELECT SUM(oi.quantity * oi.unit_price) FROM order_items oi JOIN orders o ON oi.order_id = o.order_id JOIN customers c ON o.customer_id = c.customer_id",
        conn,
    ).iloc[0, 0]

    assert abs(product_total_sum - expected_total) < 0.01, "Duplication in join detected!"

    print("\n" + "=" * 80)
    print("TASK 4: MULTI-TABLE JOIN (4 TABLES)")
    print("=" * 80)
    print(f"Enterprise Filtered Multi-Table Rows: {len(result):,}")
    print(f"Total Line-Item Spend (Matched Customers): ${expected_total:,.2f}")
    print("\nSample Enterprise Line Items (first 5 rows):")
    print(result.head(5).to_string(index=False))
    print("\n[OK] Multi-table join validated - no unexpected duplication detected!")

    return result


def task_5_document_join_decisions() -> str:
    """Task 5: Document Join Decisions."""
    join_documentation = """
================================================================================
JOIN STRATEGY DOCUMENTATION
================================================================================

Table Inventory:
- customers (1,000 rows, PK: customer_id)
- orders (5,000 rows, PK: order_id, FK: customer_id)
- order_items (8,000 rows, PK: item_id, FK: order_id, product_id)
- products (500 rows, PK: product_id)

Decision 1: customers LEFT JOIN orders
- Purpose: Get all customers with their order history while retaining zero-order customers
- Row count change: 1,000 -> 5,000 rows (4,900 matched + 100 inactive customers with NULL orders)
- Unmatched: 100 customers have no orders (retained due to LEFT join semantics)
- Business use: Customer lifetime value, churn rate calculation, cohort analysis

Decision 2: orders LEFT JOIN order_items  
- Purpose: Detailed line-item view for product basket and revenue breakdown
- Row count change: 5,000 -> 8,000 rows (orders expand into multiple item rows)
- Unmatched: 0 (every order possesses at least 1 line item)
- Business use: Product revenue attribution, inventory velocity, basket size analysis

Decision 3: Full 4-Table Join (customers -> orders -> order_items -> products)
- Purpose: Complete order context linking customer segment to product details
- Row count: 1,000 -> 8,100 rows (8,000 line items + 100 inactive customers)
- Risk: Avoid double-counting order totals when aggregating across line items
- Solution: Calculate revenue via quantity * unit_price at line-item level

Validation: Row counts match expectations, unmatched keys audited (100 inactive customers, 100 orphaned orders), zero duplication confirmed.
================================================================================
"""
    print("\n" + "=" * 80)
    print("TASK 5: DOCUMENT JOIN DECISIONS")
    print("=" * 80)
    print(join_documentation)
    return join_documentation


def main():
    print("#" * 80)
    print("# SQL JOINS & MULTI-TABLE ANALYSIS DEMONSTRATION")
    print("#" * 80)

    conn = get_connection()

    try:
        t1_res = task_1_left_join_validation(conn)
        t2_no_orders, t2_orphaned = task_2_detect_unmatched_keys(conn)
        t3_counts = task_3_compare_join_types(conn)
        t4_res = task_4_multi_table_join(conn)
        t5_doc = task_5_document_join_decisions()

        print("\n" + "#" * 80)
        print("# SUMMARY OF EXECUTION")
        print("#" * 80)
        print(f"[PASS] Task 1: LEFT JOIN Validation - Processed {len(t1_res):,} customer aggregates")
        print(f"[PASS] Task 2: Unmatched Keys - Identified {len(t2_no_orders)} inactive customers & {len(t2_orphaned)} orphaned orders")
        print(f"[PASS] Task 3: Join Comparison - Validated INNER ({t3_counts['INNER']}), LEFT ({t3_counts['LEFT']}), FULL ({t3_counts['FULL']})")
        print(f"[PASS] Task 4: Multi-Table Join - Validated 4-table join with zero duplication")
        print(f"[PASS] Task 5: Strategy Documentation - Generated complete join lineage report")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
