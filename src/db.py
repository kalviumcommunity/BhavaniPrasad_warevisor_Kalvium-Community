"""Database access layer using PostgreSQL (Supabase) via SQLAlchemy."""

import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy import text

from scripts.db_connect import get_engine, authenticate_user, register_user, init_postgres_db, test_connection


def init_db():
    """Ensure PostgreSQL database tables are initialized."""
    init_postgres_db()


def load_products_df() -> pd.DataFrame:
    """Fetch products / retail sales data from PostgreSQL database with CSV fallback."""
    try:
        engine = get_engine()
        query = """
            SELECT record_id, year, month, supplier, item_code, item_description, item_type, retail_sales, retail_transfers, warehouse_sales
            FROM warehouse_retail_sales
            LIMIT 50000;
        """
        df = pd.read_sql(query, engine)
        if not df.empty:
            return df
    except Exception:
        pass

    csv_path = Path("data/processed/warehouse_retail_sales_cleaned.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path, nrows=50000)
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
        return df

    return pd.DataFrame()


def fetch_users_df() -> pd.DataFrame:
    """Fetch registered users from app_users PostgreSQL table."""
    try:
        engine = get_engine()
        query = "SELECT user_id, username, full_name, email, role, status, created_at FROM app_users ORDER BY user_id DESC;"
        return pd.read_sql(query, engine)
    except Exception as err:
        print(f"[DB ERROR] Error fetching users: {err}")
        return pd.DataFrame()


def add_product_record(
    item_code: str,
    item_description: str,
    supplier: str,
    item_type: str,
    retail_sales: float = 0.0,
    warehouse_sales: float = 0.0,
    year: int = 2026,
    month: int = 8
) -> bool:
    """Insert a new product record into PostgreSQL warehouse_retail_sales table."""
    try:
        engine = get_engine()
        with engine.begin() as conn:
            query = text("""
                INSERT INTO warehouse_retail_sales (year, month, supplier, item_code, item_description, item_type, retail_sales, retail_transfers, warehouse_sales)
                VALUES (:year, :month, :supplier, :item_code, :item_description, :item_type, :retail_sales, 0.0, :warehouse_sales);
            """)
            conn.execute(query, {
                "year": year,
                "month": month,
                "supplier": supplier,
                "item_code": item_code,
                "item_description": item_description,
                "item_type": item_type,
                "retail_sales": retail_sales,
                "warehouse_sales": warehouse_sales
            })
        return True
    except Exception as err:
        print(f"[DB ERROR] Error adding product: {err}")
        return False
