"""Database access layer using PostgreSQL (Supabase) via SQLAlchemy with server-side pagination, caching, and parameterized queries."""

import logging
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import streamlit as st
from sqlalchemy import text, Engine

from scripts.db_connect import get_engine, authenticate_user, register_user, init_postgres_db, test_connection

# Configure server-side logger
logger = logging.getLogger("warevisor.db")


@st.cache_resource(show_spinner=False)
def get_cached_engine() -> Engine:
    """Reusable cached SQLAlchemy Engine pool."""
    return get_engine()


def init_db():
    """Ensure PostgreSQL database tables are initialized."""
    init_postgres_db(get_cached_engine())


# Whitelist allowed sorting columns to prevent SQL injection
ALLOWED_SORT_COLUMNS = {
    "record_id": "record_id",
    "year": "year",
    "month": "month",
    "supplier": "supplier",
    "item_code": "item_code",
    "item_type": "item_type",
    "retail_sales": "retail_sales"
}


@st.cache_data(ttl=60, show_spinner=False)
def fetch_records_count(
    search_query: str = "",
    year_filter: str = "All Years",
    month_filter: str = "All Months",
    item_type_filter: str = "All Item Types",
    supplier_filter: str = "All Suppliers"
) -> int:
    """Fetch total count of matching records from PostgreSQL (Cached 60s, silent spinner)."""
    try:
        engine = get_cached_engine()
        where_clauses = ["1=1"]
        params = {}

        if search_query and search_query.strip():
            where_clauses.append("(LOWER(item_code) LIKE :q OR LOWER(item_description) LIKE :q OR LOWER(supplier) LIKE :q)")
            params["q"] = f"%{search_query.strip().lower()}%"

        if year_filter and year_filter != "All Years":
            where_clauses.append("year = :year")
            params["year"] = int(year_filter)

        if month_filter and month_filter != "All Months":
            where_clauses.append("month = :month")
            params["month"] = int(month_filter)

        if item_type_filter and item_type_filter != "All Item Types":
            where_clauses.append("item_type = :item_type")
            params["item_type"] = item_type_filter

        if supplier_filter and supplier_filter != "All Suppliers":
            where_clauses.append("LOWER(supplier) LIKE :supplier")
            params["supplier"] = f"%{supplier_filter.strip().lower()}%"

        query_str = f"SELECT COUNT(record_id) FROM warehouse_retail_sales WHERE {' AND '.join(where_clauses)};"
        with engine.connect() as conn:
            return conn.execute(text(query_str), params).scalar() or 0
    except Exception as err:
        logger.warning(f"Count query failed: {err}")
        return 0


def fetch_records_page(
    search_query: str = "",
    year_filter: str = "All Years",
    month_filter: str = "All Months",
    item_type_filter: str = "All Item Types",
    supplier_filter: str = "All Suppliers",
    page: int = 1,
    page_size: int = 10,
    sort_column: str = "record_id",
    sort_order: str = "DESC"
) -> pd.DataFrame:
    """Fetch ONLY single page of records using server-side SQL LIMIT & OFFSET."""
    try:
        engine = get_cached_engine()
        where_clauses = ["1=1"]
        params = {}

        if search_query and search_query.strip():
            where_clauses.append("(LOWER(item_code) LIKE :q OR LOWER(item_description) LIKE :q OR LOWER(supplier) LIKE :q)")
            params["q"] = f"%{search_query.strip().lower()}%"

        if year_filter and year_filter != "All Years":
            where_clauses.append("year = :year")
            params["year"] = int(year_filter)

        if month_filter and month_filter != "All Months":
            where_clauses.append("month = :month")
            params["month"] = int(month_filter)

        if item_type_filter and item_type_filter != "All Item Types":
            where_clauses.append("item_type = :item_type")
            params["item_type"] = item_type_filter

        if supplier_filter and supplier_filter != "All Suppliers":
            where_clauses.append("LOWER(supplier) LIKE :supplier")
            params["supplier"] = f"%{supplier_filter.strip().lower()}%"

        # Enforce whitelisted sorting column and order
        safe_sort_col = ALLOWED_SORT_COLUMNS.get(sort_column, "record_id")
        safe_sort_order = "DESC" if sort_order.upper() == "DESC" else "ASC"

        offset = (max(1, page) - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        query_str = f"""
            SELECT record_id, year, month, supplier, item_code, item_description, item_type, retail_sales, warehouse_sales
            FROM warehouse_retail_sales
            WHERE {" AND ".join(where_clauses)}
            ORDER BY {safe_sort_col} {safe_sort_order}
            LIMIT :limit OFFSET :offset;
        """
        df = pd.read_sql(text(query_str), engine, params=params)
        if not df.empty:
            return df
    except Exception as err:
        logger.warning(f"Server-side page query failed: {err}")

    return pd.DataFrame()


def load_records_df(limit: int = 50) -> pd.DataFrame:
    """Fetch small subset of records for general fallback."""
    return fetch_records_page(page=1, page_size=limit)


def load_products_df() -> pd.DataFrame:
    """Alias for load_records_df to preserve backward compatibility."""
    return load_records_df()


@st.cache_data(ttl=60, show_spinner=False)
def fetch_dashboard_metrics() -> Dict[str, Any]:
    """Calculate dashboard KPI metrics directly from PostgreSQL database (Cached 60s, silent spinner)."""
    try:
        engine = get_cached_engine()
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT 
                    COUNT(record_id) AS total_records,
                    COUNT(DISTINCT item_code) AS unique_items,
                    COUNT(DISTINCT supplier) AS total_suppliers,
                    COUNT(DISTINCT item_type) AS total_item_types,
                    COALESCE(SUM(retail_sales), 0) AS total_retail_sales,
                    COALESCE(SUM(warehouse_sales), 0) AS total_warehouse_sales
                FROM warehouse_retail_sales;
            """)).mappings().first()
            if row:
                return dict(row)
    except Exception as err:
        logger.warning(f"Failed to compute metrics via SQL: {err}")

    return {
        "total_records": 0,
        "unique_items": 0,
        "total_suppliers": 0,
        "total_item_types": 0,
        "total_retail_sales": 0.0,
        "total_warehouse_sales": 0.0
    }


@st.cache_data(ttl=60, show_spinner=False)
def fetch_sender_metrics(supplier_name: str = "") -> Dict[str, Any]:
    """Calculate KPI metrics specifically for a single logged-in sender/supplier from database."""
    try:
        if supplier_name and supplier_name.strip():
            engine = get_cached_engine()
            query_str = """
                SELECT 
                    COUNT(record_id) AS total_records,
                    COUNT(DISTINCT item_code) AS unique_items,
                    COUNT(DISTINCT supplier) AS total_suppliers,
                    COUNT(DISTINCT item_type) AS total_item_types,
                    COALESCE(SUM(retail_sales), 0) AS total_retail_sales,
                    COALESCE(SUM(warehouse_sales), 0) AS total_warehouse_sales
                FROM warehouse_retail_sales
                WHERE LOWER(supplier) LIKE :sup;
            """
            with engine.connect() as conn:
                row = conn.execute(text(query_str), {"sup": f"%{supplier_name.strip().lower()}%"}).mappings().first()
                if row and row["total_records"] > 0:
                    return dict(row)
    except Exception as err:
        logger.warning(f"Failed sender metrics query: {err}")

    return fetch_dashboard_metrics()


@st.cache_data(ttl=60, show_spinner=False)
def fetch_monthly_records_trend() -> pd.DataFrame:
    """Fetch monthly records count aggregated chronologically by year and month (Cached 60s, silent spinner)."""
    try:
        engine = get_cached_engine()
        query = """
            SELECT year, month, COUNT(record_id) AS record_count
            FROM warehouse_retail_sales
            GROUP BY year, month
            ORDER BY year ASC, month ASC;
        """
        df = pd.read_sql(text(query), engine)
        if not df.empty:
            df["period"] = df["year"].astype(str) + "-M" + df["month"].astype(str).str.zfill(2)
            return df
    except Exception as err:
        logger.warning(f"Failed monthly trend query: {err}")

    return pd.DataFrame()


@st.cache_data(ttl=60, show_spinner=False)
def fetch_suppliers_summary(limit: int = 5) -> pd.DataFrame:
    """Group records by Supplier to display top suppliers overview (Cached 60s, silent spinner)."""
    try:
        engine = get_cached_engine()
        query = f"""
            SELECT 
                supplier AS "Supplier Name",
                COUNT(record_id) AS "Total Records",
                COUNT(DISTINCT item_type) AS "Item Types Handled",
                ROUND(SUM(retail_sales)::numeric, 2) AS "Total Retail Sales ($)",
                ROUND(SUM(warehouse_sales)::numeric, 2) AS "Total Warehouse Sales ($)"
            FROM warehouse_retail_sales
            GROUP BY supplier
            ORDER BY COUNT(record_id) DESC
            LIMIT {limit};
        """
        return pd.read_sql(text(query), engine)
    except Exception as err:
        logger.warning(f"Failed supplier summary query: {err}")
        return pd.DataFrame()


@st.cache_data(ttl=60, show_spinner=False)
def fetch_recent_records(limit: int = 5) -> pd.DataFrame:
    """Fetch recent inserted records from warehouse_retail_sales (Cached 60s, silent spinner)."""
    try:
        engine = get_cached_engine()
        query = f"""
            SELECT record_id, item_code, item_description, supplier, item_type, year, month
            FROM warehouse_retail_sales
            ORDER BY record_id DESC
            LIMIT {limit};
        """
        return pd.read_sql(text(query), engine)
    except Exception as err:
        logger.warning(f"Failed recent records query: {err}")
        return pd.DataFrame()


@st.cache_data(ttl=60, show_spinner=False)
def fetch_item_types_summary() -> pd.DataFrame:
    """Group records by Item Type to display item type overview (Cached 60s, silent spinner)."""
    try:
        engine = get_cached_engine()
        query = """
            SELECT 
                item_type AS "Item Type",
                COUNT(record_id) AS "Record Count",
                COUNT(DISTINCT item_code) AS "Distinct Items",
                COUNT(DISTINCT supplier) AS "Suppliers Offering",
                ROUND(SUM(retail_sales)::numeric, 2) AS "Total Retail Sales ($)"
            FROM warehouse_retail_sales
            GROUP BY item_type
            ORDER BY COUNT(record_id) DESC;
        """
        return pd.read_sql(text(query), engine)
    except Exception as err:
        logger.warning(f"Failed item type summary query: {err}")
        return pd.DataFrame()


@st.cache_data(ttl=60, show_spinner=False)
def fetch_users_df() -> pd.DataFrame:
    """Fetch registered users from app_users PostgreSQL table (password_hash is excluded, Cached 60s, silent spinner)."""
    try:
        engine = get_cached_engine()
        query = "SELECT user_id, username, full_name, email, role, status, created_at FROM app_users ORDER BY user_id DESC;"
        return pd.read_sql(query, engine)
    except Exception as err:
        logger.error(f"Error fetching users: {err}")
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
    """Insert a new product record into PostgreSQL warehouse_retail_sales table and clear query caches."""
    try:
        engine = get_cached_engine()
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

        # Invalidate Streamlit query caches after new record insertion
        st.cache_data.clear()
        return True
    except Exception as err:
        logger.error(f"Error adding record: {err}")
        return False
