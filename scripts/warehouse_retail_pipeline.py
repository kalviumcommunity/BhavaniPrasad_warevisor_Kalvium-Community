from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "raw" / "Warehouse_and_Retail_Sales.csv"
DEFAULT_CLEANED_OUTPUT = REPO_ROOT / "data" / "processed" / "warehouse_retail_sales_cleaned.csv"
DEFAULT_REPORT_OUTPUT = REPO_ROOT / "output" / "warehouse_retail_cleaning_report.json"
DEFAULT_SCHEMA_OUTPUT = REPO_ROOT / "sql" / "warehouse_retail_sales_schema.sql"

COLUMN_RENAME_MAP = {
    "YEAR": "year",
    "MONTH": "month",
    "SUPPLIER": "supplier",
    "ITEM CODE": "item_code",
    "ITEM DESCRIPTION": "item_description",
    "ITEM TYPE": "item_type",
    "RETAIL SALES": "retail_sales",
    "RETAIL TRANSFERS": "retail_transfers",
    "WAREHOUSE SALES": "warehouse_sales",
}

TEXT_COLUMNS = ["supplier", "item_code", "item_description", "item_type"]
NUMERIC_COLUMNS = ["retail_sales", "retail_transfers", "warehouse_sales"]
KEY_COLUMNS = ["year", "month", "supplier", "item_code", "item_description", "item_type"]


def _resolve_input_path(source_path: str | Path | None = None) -> Path:
    candidates: list[Path] = []
    if source_path is not None:
        candidates.append(Path(source_path))
    candidates.append(DEFAULT_INPUT)
    candidates.append(Path("/home/tony/Downloads/archive/Warehouse_and_Retail_Sales.csv"))

    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Could not locate Warehouse_and_Retail_Sales.csv")


def load_retail_sales_data(source_path: str | Path | None = None, use_db_if_available: bool = True) -> pd.DataFrame:
    """Load retail sales dataset from PostgreSQL database (warehouse_retail_sales) or fallback to CSV."""
    if source_path is None and use_db_if_available:
        try:
            from scripts.db_connect import get_engine
            engine = get_engine()
            query = "SELECT year, month, supplier, item_code, item_description, item_type, retail_sales, retail_transfers, warehouse_sales FROM warehouse_retail_sales;"
            df = pd.read_sql(query, engine)
            if not df.empty:
                # Standardize uppercase column names if needed
                df.columns = [c.upper().replace("_", " ") if c in ["year", "month", "supplier", "item_code", "item_description", "item_type", "retail_sales", "retail_transfers", "warehouse_sales"] else c for c in df.columns]
                return df
        except Exception as err:
            pass

    path = _resolve_input_path(source_path)
    return pd.read_csv(path)



def _normalize_text_series(series: pd.Series, title_case: bool = False, upper_case: bool = False) -> pd.Series:
    cleaned = series.astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
    if title_case:
        cleaned = cleaned.str.title()
    if upper_case:
        cleaned = cleaned.str.upper()
    return cleaned


def _safe_mode(series: pd.Series, fallback: str) -> str:
    mode_values = series.dropna().mode()
    if mode_values.empty:
        return fallback
    value = mode_values.iloc[0]
    if pd.isna(value) or str(value).strip() == "":
        return fallback
    return str(value)


def analyze_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Return a missing-value summary for each column."""
    return pd.DataFrame(
        {
            "column": df.columns,
            "null_count": df.isna().sum().values,
            "null_percentage": (df.isna().sum() / len(df) * 100).round(4).values,
            "data_type": df.dtypes.astype(str).values,
        }
    )


def _build_validation_checks(df: pd.DataFrame) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def add_check(name: str, mask: pd.Series, description: str, severity: str = "error") -> None:
        normalized_mask = mask.fillna(False).astype(bool)
        failed = int((~normalized_mask).sum())
        checks.append(
            {
                "rule": name,
                "description": description,
                "severity": severity,
                "passed": int(normalized_mask.sum()),
                "failed": failed,
                "status": "passed" if failed == 0 else "failed",
            }
        )

    add_check("valid_year", df["year"].between(2017, 2020, inclusive="both"), "YEAR must fall between 2017 and 2020.")
    add_check("valid_month", df["month"].between(1, 12, inclusive="both"), "MONTH must be between 1 and 12.")
    add_check("supplier_present", df["supplier"].astype("string").str.strip().ne(""), "Supplier must be present.")
    add_check("item_code_present", df["item_code"].astype("string").str.strip().ne(""), "Item code must be present.")
    add_check(
        "item_description_present",
        df["item_description"].astype("string").str.strip().ne(""),
        "Item description must be present.",
    )
    add_check("item_type_present", df["item_type"].astype("string").str.strip().ne(""), "Item type must be present.")

    for column in NUMERIC_COLUMNS:
        add_check(
            f"{column}_numeric",
            pd.to_numeric(df[column], errors="coerce").notna(),
            f"{column} must be numeric.",
        )

    return checks


def clean_retail_sales_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean the retail sales dataset and return the cleaned data plus a report."""
    working = df.copy()
    working.columns = [column.strip() for column in working.columns]
    working = working.rename(columns=COLUMN_RENAME_MAP)

    missing_before = analyze_missing_values(working)
    original_row_count = len(working)
    exact_duplicates_before = int(working.duplicated().sum())

    text_missing_before = {column: int(working[column].isna().sum()) for column in TEXT_COLUMNS if column in working.columns}
    numeric_missing_before = {
        column: int(pd.to_numeric(working[column], errors="coerce").isna().sum())
        for column in NUMERIC_COLUMNS
        if column in working.columns
    }

    working = working.drop_duplicates().reset_index(drop=True)

    # Clean text fields first so the mode-based imputations use normalized labels.
    working["supplier"] = _normalize_text_series(working["supplier"], title_case=True)
    working["item_code"] = _normalize_text_series(working["item_code"])
    working["item_description"] = _normalize_text_series(working["item_description"], title_case=True)
    working["item_type"] = _normalize_text_series(working["item_type"], upper_case=True)

    imputation_log: dict[str, Any] = {}

    supplier_fill = _safe_mode(working["supplier"], "Unknown Supplier")
    supplier_nulls = int(working["supplier"].isna().sum())
    working["supplier"] = working["supplier"].fillna(supplier_fill)
    imputation_log["supplier"] = {"strategy": "mode", "fill_value": supplier_fill, "nulls_filled": supplier_nulls}

    item_type_fill = _safe_mode(working["item_type"], "UNKNOWN")
    item_type_nulls = int(working["item_type"].isna().sum())
    working["item_type"] = working["item_type"].fillna(item_type_fill).str.upper()
    imputation_log["item_type"] = {"strategy": "mode", "fill_value": item_type_fill, "nulls_filled": item_type_nulls}

    for column in NUMERIC_COLUMNS:
        numeric_series = pd.to_numeric(working[column], errors="coerce")
        fill_value = float(numeric_series.median()) if numeric_series.notna().any() else 0.0
        null_count = int(numeric_series.isna().sum())
        working[column] = numeric_series.fillna(fill_value)
        imputation_log[column] = {"strategy": "median", "fill_value": fill_value, "nulls_filled": null_count}

    working["year"] = pd.to_numeric(working["year"], errors="coerce").fillna(working["year"].mode(dropna=True).iloc[0]).astype(int)
    working["month"] = pd.to_numeric(working["month"], errors="coerce").fillna(working["month"].mode(dropna=True).iloc[0]).astype(int)

    # Re-apply text normalization after imputation so the inserted values match the style.
    working["supplier"] = _normalize_text_series(working["supplier"], title_case=True)
    working["item_description"] = _normalize_text_series(working["item_description"], title_case=True)
    working["item_type"] = _normalize_text_series(working["item_type"], upper_case=True)

    missing_after = analyze_missing_values(working)
    validation_checks = _build_validation_checks(working)

    negative_counts = {
        column: int((pd.to_numeric(working[column], errors="coerce") < 0).sum())
        for column in NUMERIC_COLUMNS
    }

    report = {
        "source_rows": original_row_count,
        "cleaned_rows": len(working),
        "exact_duplicates_before": exact_duplicates_before,
        "rows_removed_by_deduplication": original_row_count - len(working),
        "missing_before": missing_before.to_dict(orient="records"),
        "missing_after": missing_after.to_dict(orient="records"),
        "text_missing_before": text_missing_before,
        "numeric_missing_before": numeric_missing_before,
        "imputations": imputation_log,
        "validation_checks": validation_checks,
        "negative_value_counts": negative_counts,
        "schema_columns": KEY_COLUMNS + NUMERIC_COLUMNS,
    }

    return working, report


def prepare_retail_sales_dataset(
    source_path: str | Path | None = None,
    cleaned_output_path: str | Path = DEFAULT_CLEANED_OUTPUT,
    report_output_path: str | Path = DEFAULT_REPORT_OUTPUT,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load, clean, save, and report on the retail sales dataset."""
    raw_df = load_retail_sales_data(source_path)
    cleaned_df, report = clean_retail_sales_data(raw_df)

    cleaned_path = Path(cleaned_output_path)
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(cleaned_path, index=False)

    report_path = Path(report_output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    return cleaned_df, report


def build_schema_sql() -> str:
    """Return the SQLite schema that matches the cleaned retail sales dataset."""
    return """PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS warehouse_retail_sales (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL CHECK (year BETWEEN 2017 AND 2020),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    supplier TEXT NOT NULL,
    item_code TEXT NOT NULL,
    item_description TEXT NOT NULL,
    item_type TEXT NOT NULL,
    retail_sales REAL NOT NULL DEFAULT 0,
    retail_transfers REAL NOT NULL DEFAULT 0,
    warehouse_sales REAL NOT NULL DEFAULT 0,
    CHECK (trim(supplier) <> ''),
    CHECK (trim(item_code) <> ''),
    CHECK (trim(item_description) <> ''),
    CHECK (trim(item_type) <> '')
);

CREATE INDEX IF NOT EXISTS idx_warehouse_retail_sales_year_month
    ON warehouse_retail_sales (year, month);

CREATE INDEX IF NOT EXISTS idx_warehouse_retail_sales_supplier
    ON warehouse_retail_sales (supplier);

CREATE INDEX IF NOT EXISTS idx_warehouse_retail_sales_item_type
    ON warehouse_retail_sales (item_type);
"""


def write_schema_file(output_path: str | Path = DEFAULT_SCHEMA_OUTPUT) -> Path:
    """Persist the SQLite schema to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_schema_sql(), encoding="utf-8")
    return path
