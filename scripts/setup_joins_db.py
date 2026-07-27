"""Database setup for SQL Joins & Multi-Table Analysis.

Creates data/joins_analysis.db with 4 tables:
- customers (1,000 rows: 900 active, 100 inactive)
- orders (5,000 rows: 4,900 valid, 100 orphaned)
- order_items (8,000 rows: detailed line items)
- products (500 rows: product catalogue)
"""

from __future__ import annotations

import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def setup_joins_db(db_path: str = "data/joins_analysis.db") -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create tables
    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_type TEXT NOT NULL,
        signup_date TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT NOT NULL,
        order_amount REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)

    np.random.seed(42)
    start_date = datetime(2024, 1, 1)

    # 2. Populate Customers (1,000 rows)
    # customer_id: 1..1000
    # 1..900 will have orders; 901..1000 will have 0 orders.
    customer_types = ["Enterprise", "SMB", "Individual"]
    customers_data = []
    for cid in range(1, 1001):
        # 30% Enterprise, 50% SMB, 20% Individual
        ctype = np.random.choice(customer_types, p=[0.3, 0.5, 0.2])
        signup = start_date + timedelta(days=int(np.random.uniform(0, 180)))
        customers_data.append((cid, ctype, signup.strftime("%Y-%m-%d")))

    cursor.executemany(
        "INSERT INTO customers (customer_id, customer_type, signup_date) VALUES (?, ?, ?)",
        customers_data,
    )

    # 3. Populate Products (500 rows)
    categories = ["Hardware", "Software", "Cloud Services", "Consulting", "Peripherals"]
    products_data = []
    for pid in range(1, 501):
        cat = np.random.choice(categories)
        pname = f"{cat} Item-{pid}"
        price = round(float(np.random.uniform(15.0, 1200.0)), 2)
        products_data.append((pid, pname, cat, price))

    cursor.executemany(
        "INSERT INTO products (product_id, product_name, category, price) VALUES (?, ?, ?, ?)",
        products_data,
    )

    # 4. Populate Orders (5,000 rows total)
    # 4,900 orders matched to customer_ids 1..900
    # 100 orders orphaned with customer_ids 9001..9100 (non-existent in customers)
    orders_data = []

    # Matched orders (order_id 1001..5900)
    for oid in range(1001, 5901):
        cid = int(np.random.choice(range(1, 901)))  # active customers 1..900
        odate = start_date + timedelta(days=int(np.random.uniform(181, 365)))
        # Base amount placeholder (will update after generating items)
        orders_data.append((oid, cid, odate.strftime("%Y-%m-%d"), 0.0))

    # Orphaned orders (order_id 5901..6000) -> customer_id 9001..9100
    for oid in range(5901, 6001):
        cid = int(9000 + (oid - 5900))  # Invalid customer_id
        odate = start_date + timedelta(days=int(np.random.uniform(181, 365)))
        orders_data.append((oid, cid, odate.strftime("%Y-%m-%d"), 0.0))

    cursor.executemany(
        "INSERT INTO orders (order_id, customer_id, order_date, order_amount) VALUES (?, ?, ?, ?)",
        orders_data,
    )

    # 5. Populate Order Items (8,000 rows total across 5,000 orders)
    # Ensure every order (1001..6000) has at least 1 item.
    # The remaining 3,000 items are distributed randomly among orders.
    items_data = []
    order_totals = {oid: 0.0 for oid in range(1001, 6001)}

    # Guarantee 1 item per order
    for oid in range(1001, 6001):
        pid = int(np.random.choice(range(1, 501)))
        qty = int(np.random.randint(1, 6))
        uprice = float(products_data[pid - 1][3])
        item_total = qty * uprice
        order_totals[oid] += item_total
        items_data.append((oid, pid, qty, uprice))

    # Remaining 3,000 items
    extra_orders = np.random.choice(range(1001, 6001), 3000)
    for oid in extra_orders:
        oid = int(oid)
        pid = int(np.random.choice(range(1, 501)))
        qty = int(np.random.randint(1, 6))
        uprice = float(products_data[pid - 1][3])
        item_total = qty * uprice
        order_totals[oid] += item_total
        items_data.append((oid, pid, qty, uprice))

    cursor.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        items_data,
    )

    # Update orders.order_amount to match SUM(quantity * unit_price)
    for oid, total in order_totals.items():
        cursor.execute(
            "UPDATE orders SET order_amount = ? WHERE order_id = ?",
            (round(total, 2), oid),
        )

    conn.commit()
    conn.close()
    print(f"Database successfully setup at '{db_path}'!")


if __name__ == "__main__":
    setup_joins_db()
