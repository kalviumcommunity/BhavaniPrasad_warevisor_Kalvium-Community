from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_FILE = BASE_DIR / "data/raw/untyped_data.csv"
TYPED_DATA_FILE = BASE_DIR / "data/processed/typed_data.csv"
TYPE_REPORT_FILE = BASE_DIR / "output/dtype_conversion_report.csv"
TYPE_LOG_FILE = BASE_DIR / "output/type_conversion_log.json"


def cast_columns_to_types(df, type_mapping):
    """
    Explicitly cast columns to correct dtypes.

    Args:
        df: Input DataFrame
        type_mapping: Dict of {column: target_dtype}

    Returns:
        DataFrame with corrected types and conversion log
    """
    df_typed = df.copy()
    conversion_log = {}

    for col, target_dtype in type_mapping.items():
        if col not in df.columns:
            print(f"Warning: Column {col} not found in DataFrame")
            continue

        original_dtype = df[col].dtype

        try:
            df_typed[col] = df_typed[col].astype(target_dtype)
            conversion_log[col] = {
                "from": str(original_dtype),
                "to": str(target_dtype),
                "status": "success",
            }
            print(f"✓ {col}: {original_dtype} → {target_dtype}")
        except Exception as exc:
            conversion_log[col] = {
                "from": str(original_dtype),
                "to": str(target_dtype),
                "status": "failed",
                "error": str(exc),
            }
            print(f"✗ {col}: Conversion failed - {exc}")
            raise

    return df_typed, conversion_log


def convert_string_dates_to_datetime(df, date_columns, date_format=None):
    """
    Convert string columns to datetime with explicit format.

    Args:
        df: Input DataFrame
        date_columns: List of column names containing dates
        date_format: Datetime format string (e.g., '%Y-%m-%d')

    Returns:
        DataFrame with datetime columns converted

    Note: ALWAYS specify format. "01-02-2025" is ambiguous without it.
    """
    df_typed = df.copy()

    for col in date_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue

        try:
            # Pandas infers format if not specified - risky!
            if date_format:
                df_typed[col] = pd.to_datetime(df_typed[col], format=date_format)
            else:
                # Only use inference if absolutely necessary
                df_typed[col] = pd.to_datetime(df_typed[col])

            print(f"✓ {col}: Converted to datetime")

        except Exception as exc:
            print(f"✗ {col}: Conversion failed - {exc}")
            print(f"  Sample values: {df[col].head(3).tolist()}")
            print(f"  Expected format: {date_format}")
            raise

    return df_typed


def convert_currency_to_float(df, currency_columns):
    """
    Strip currency symbols and convert to float.

    Example: '$150.50' → 150.50

    Args:
        df: Input DataFrame
        currency_columns: List of column names with currency

    Returns:
        DataFrame with clean numeric columns
    """
    df_typed = df.copy()

    for col in currency_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue

        try:
            # Remove common currency symbols and whitespace
            df_typed[col] = (
                df_typed[col]
                .astype(str)
                .str.replace("[$,]", "", regex=True)
                .str.strip()
            )

            # Convert to float - coerce errors to NaN
            df_typed[col] = pd.to_numeric(df_typed[col], errors="coerce")

            # Check for failed conversions
            failed_conversions = df_typed[col].isnull().sum() - df[col].isnull().sum()
            if failed_conversions > 0:
                print(f"⚠ {col}: {failed_conversions} values could not be converted to numeric")

            print(f"✓ {col}: Stripped symbols, converted to float")

        except Exception as exc:
            print(f"✗ {col}: Conversion failed - {exc}")
            raise

    return df_typed


def convert_integers_to_boolean(df, boolean_columns):
    """
    Convert 0/1 or yes/no columns to proper boolean type.

    Args:
        df: Input DataFrame
        boolean_columns: List of column names with binary values

    Returns:
        DataFrame with bool columns
    """
    df_typed = df.copy()

    for col in boolean_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue

        try:
            # First check what values exist
            unique_vals = df[col].unique()
            print(f"  {col} unique values: {unique_vals}")

            # Map different boolean representations
            if df[col].dtype == "object":
                mapping = {
                    "yes": True,
                    "no": False,
                    "y": True,
                    "n": False,
                    "true": True,
                    "false": False,
                    "1": True,
                    "0": False,
                    1: True,
                    0: False,
                    True: True,
                    False: False,
                }
                df_typed[col] = df_typed[col].map(mapping)
            else:
                df_typed[col] = df_typed[col].astype(bool)

            print(f"✓ {col}: Converted to boolean")

        except Exception as exc:
            print(f"✗ {col}: Conversion failed - {exc}")
            raise

    return df_typed


def compare_dtypes(df_original, df_typed):
    """
    Compare dtypes before and after conversion.

    Returns: Summary of all changes
    """
    comparison = pd.DataFrame(
        {
            "column": df_original.columns,
            "dtype_before": df_original.dtypes.values,
            "dtype_after": df_typed.dtypes.values,
            "changed": (df_original.dtypes != df_typed.dtypes).values,
        }
    )

    print("\n" + "=" * 70)
    print("DTYPE CONVERSION SUMMARY")
    print("=" * 70)
    print(comparison.to_string(index=False))

    TYPE_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(TYPE_REPORT_FILE, index=False)
    print(f"\nReport saved to {TYPE_REPORT_FILE.relative_to(BASE_DIR)}")
    print("=" * 70)

    return comparison


def save_conversion_log(conversion_log, output_file):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(conversion_log, indent=2, default=str))
    print(f"Conversion log saved to {output_file.relative_to(BASE_DIR)}")


def record_conversion(conversion_log, column, source_dtype, target_dtype, status, details=None):
    conversion_log[column] = {
        "from": str(source_dtype),
        "to": str(target_dtype),
        "status": status,
    }
    if details:
        conversion_log[column].update(details)


if __name__ == "__main__":
    # Load data
    df = pd.read_csv(RAW_DATA_FILE)

    print("=" * 70)
    print("BEFORE TYPE CONVERSION")
    print("=" * 70)
    print(df.dtypes)
    print("\nSample data:")
    print(df.head(3))

    # Define conversions
    df_typed = df.copy()
    conversion_log = {}

    # Convert dates with explicit format
    print("\n1. Converting date columns...")
    df_typed = convert_string_dates_to_datetime(
        df_typed,
        ["transaction_date", "signup_date"],
        date_format="%Y-%m-%d",
    )
    record_conversion(
        conversion_log,
        "transaction_date",
        df["transaction_date"].dtype,
        df_typed["transaction_date"].dtype,
        "success",
        {"transformation": "string date parsed with explicit format", "format": "%Y-%m-%d"},
    )
    record_conversion(
        conversion_log,
        "signup_date",
        df["signup_date"].dtype,
        df_typed["signup_date"].dtype,
        "success",
        {"transformation": "string date parsed with explicit format", "format": "%Y-%m-%d"},
    )

    # Convert currency
    print("\n2. Converting currency columns...")
    df_typed = convert_currency_to_float(
        df_typed,
        ["amount"],
    )
    record_conversion(
        conversion_log,
        "amount",
        df["amount"].dtype,
        df_typed["amount"].dtype,
        "success",
        {"transformation": "currency symbols stripped and converted to float"},
    )

    # Convert booleans
    print("\n3. Converting boolean columns...")
    df_typed = convert_integers_to_boolean(
        df_typed,
        ["is_active"],
    )
    record_conversion(
        conversion_log,
        "is_active",
        df["is_active"].dtype,
        df_typed["is_active"].dtype,
        "success",
        {"transformation": "0/1 values converted to boolean"},
    )

    # Compare
    print("\n4. Comparing before/after types...")
    print("=" * 70)
    print("AFTER TYPE CONVERSION")
    print("=" * 70)
    print(df_typed.dtypes)
    print("\nSample data:")
    print(df_typed.head(3))

    # Validation report
    compare_dtypes(df, df_typed)
    save_conversion_log(conversion_log, TYPE_LOG_FILE)

    # Save typed data
    TYPED_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_typed.to_csv(TYPED_DATA_FILE, index=False)
    print(f"\n✓ Typed data saved to {TYPED_DATA_FILE.relative_to(BASE_DIR)}")