"""Migration script to initialize PostgreSQL database schema and bulk import cleaned dataset."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# Add parent directory to sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.db_connect import get_engine, get_db_url, test_connection

SCHEMA_PATH = REPO_ROOT / "sql" / "postgres_schema.sql"
CLEANED_CSV_PATH = REPO_ROOT / "data" / "processed" / "warehouse_retail_sales_cleaned.csv"


def run_schema_migration(engine) -> None:
    """Execute DDL schema script to set up tables and roles."""
    print("--- 1. Applying PostgreSQL Schema & Role Setup ---")
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    
    with engine.begin() as conn:
        conn.execute(text(schema_sql))
    print("[OK] Schema, indexes, and roles applied successfully.")


def import_cleaned_csv(engine, csv_path: Path = CLEANED_CSV_PATH, chunksize: int = 2000) -> int:
    """Import warehouse_retail_sales_cleaned.csv into PostgreSQL table using COPY or chunked inserts."""
    import io

    print(f"--- 2. Importing Cleaned Sales Data from {csv_path.name} ---")
    if not csv_path.exists():
        raise FileNotFoundError(f"Cleaned CSV dataset not found at {csv_path}")

    # Read CSV
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"[DATA] Read {len(df):,} records from CSV.")

    # Lowercase column names to match PostgreSQL schema
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]

    # Map column names if needed
    col_mapping = {
        "item_code": "item_code",
        "item_description": "item_description",
        "item_type": "item_type",
        "retail_sales": "retail_sales",
        "retail_transfers": "retail_transfers",
        "warehouse_sales": "warehouse_sales"
    }
    df = df.rename(columns=col_mapping)

    # Clean text types
    df["supplier"] = df["supplier"].astype(str)
    df["item_code"] = df["item_code"].astype(str)
    df["item_description"] = df["item_description"].astype(str)
    df["item_type"] = df["item_type"].astype(str)

    target_cols = [
        "year", "month", "supplier", "item_code", "item_description",
        "item_type", "retail_sales", "retail_transfers", "warehouse_sales"
    ]
    df = df[target_cols]

    total_rows = len(df)

    with engine.begin() as conn:
        # Check if table already has data
        existing_count = conn.execute(text("SELECT COUNT(*) FROM warehouse_retail_sales;")).scalar() or 0
        if existing_count > 0:
            print(f"[INFO] Table already contains {existing_count:,} records. Truncating for fresh import...")
            conn.execute(text("TRUNCATE TABLE warehouse_retail_sales RESTART IDENTITY;"))

    # Try fast PostgreSQL COPY command first
    print(f"[IMPORT] Inserting {total_rows:,} records into PostgreSQL...")
    try:
        raw_conn = engine.raw_connection()
        try:
            buffer = io.StringIO()
            df.to_csv(buffer, index=False, header=False, sep="\t", na_rep="\\N")
            buffer.seek(0)

            with raw_conn.cursor() as cursor:
                copy_sql = (
                    "COPY warehouse_retail_sales ("
                    "year, month, supplier, item_code, item_description, "
                    "item_type, retail_sales, retail_transfers, warehouse_sales"
                    ") FROM STDIN WITH (FORMAT CSV, DELIMITER '\t', NULL '\\N')"
                )
                cursor.copy_expert(sql=copy_sql, file=buffer)
            raw_conn.commit()
            print("[IMPORT] Fast PostgreSQL COPY completed successfully.")
        finally:
            raw_conn.close()
    except Exception as err:
        print(f"[WARN] PostgreSQL COPY failed ({err}), falling back to chunked to_sql...")
        with engine.begin() as conn:
            df.to_sql(
                "warehouse_retail_sales",
                con=conn,
                if_exists="append",
                index=False,
                chunksize=chunksize,
                method=None
            )

    with engine.connect() as conn:
        inserted = conn.execute(text("SELECT COUNT(*) FROM warehouse_retail_sales;")).scalar() or 0

    print(f"[OK] Successfully imported {inserted:,} records into PostgreSQL database.")
    return inserted


def verify_database(engine) -> None:
    """Verify tables, user logins, and row counts."""
    print("--- 3. Database Verification ---")
    with engine.connect() as conn:
        user_count = conn.execute(text("SELECT COUNT(*) FROM app_users;")).scalar()
        sales_count = conn.execute(text("SELECT COUNT(*) FROM warehouse_retail_sales;")).scalar()
        users = conn.execute(text("SELECT username, role, full_name FROM app_users;")).mappings().all()

        print(f"[VERIFY] Total app_users: {user_count}")
        for user in users:
            print(f"  - User: '{user['username']}' | Role: '{user['role']}' | Name: '{user['full_name']}'")

        print(f"[VERIFY] Total warehouse_retail_sales rows: {sales_count:,}")


def main():
    parser = argparse.ArgumentParser(description="Migrate WareVisor database to Supabase PostgreSQL.")
    parser.add_argument("--password", type=str, help="PostgreSQL password for Supabase")
    parser.add_argument("--verify-only", action="store_true", help="Only verify database status")
    args = parser.parse_args()

    password = args.password or os.getenv("POSTGRES_PASSWORD", "")
    if password:
        os.environ["POSTGRES_PASSWORD"] = password

    engine = get_engine(password)

    if args.verify_only:
        verify_database(engine)
        return

    print(f"[INIT] Connecting to PostgreSQL database...")
    run_schema_migration(engine)
    import_cleaned_csv(engine)
    verify_database(engine)
    print("\n[SUCCESS] PostgreSQL migration & role-based setup complete!")


if __name__ == "__main__":
    main()
