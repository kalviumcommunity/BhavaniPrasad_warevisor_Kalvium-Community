"""Reusable string cleaning pipeline for messy text fields."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "raw" / "string_cleaning_sample.csv"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "processed" / "cleaned_strings.csv"
DEFAULT_SUMMARY = REPO_ROOT / "output" / "string_cleaning_summary.json"


def strip_all_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from all string columns and report the consolidation effect."""
    string_cols = df.select_dtypes(include=["object"]).columns
    whitespace_fix_count = 0

    for col in string_cols:
        before = df[col].nunique(dropna=True)
        df[col] = df[col].astype("string").str.strip()
        after = df[col].nunique(dropna=True)
        whitespace_fix_count += max(0, before - after)
        print(f"{col}: {before} → {after} unique values")

    print(f"Total whitespace issues fixed: {whitespace_fix_count}")
    return df


def normalize_casing(df: pd.DataFrame, columns_to_lower: list[str]) -> pd.DataFrame:
    """Normalize casing for selected columns to lowercase."""
    for col in columns_to_lower:
        if col in df.columns:
            df[col] = df[col].astype("string").str.lower()
            print(f"Normalized {col} to lowercase")
    return df


def remove_special_characters(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Remove special characters from selected columns using a regex pattern."""
    pattern = r"[^a-zA-Z0-9 ]"
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype("string").str.replace(pattern, "", regex=True)
            df[col] = df[col].astype("string").str.lower()
            print(f"Removed special characters from {col}")
    return df


def standardize_categories(df: pd.DataFrame, mapping_by_column: dict[str, dict[str, str]]) -> pd.DataFrame:
    """Standardize categorical labels using a column-wise mapping dictionary."""
    for col, mapping in mapping_by_column.items():
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().str.lower().map(mapping).str.lower()
            print(f"Standardized values in {col} using mapping")
    return df


def clean_text_column(
    series: pd.Series,
    lowercase: bool = True,
    strip: bool = True,
    remove_special: bool = False,
    mapping: dict[str, str] | None = None,
) -> pd.Series:
    """Reusable helper that cleans a single string column."""
    result = series.copy()

    if result.isna().any():
        print(f"Warning: {result.isna().sum()} null values in column")

    if strip:
        result = result.astype("string").str.strip()

    if lowercase:
        result = result.astype("string").str.lower()

    if remove_special:
        result = result.astype("string").str.replace(r"[^a-zA-Z0-9 ]", "", regex=True)

    if mapping:
        result = result.map(mapping)

    return result


def build_cleaning_report(df_before: pd.DataFrame, df_after: pd.DataFrame) -> dict[str, Any]:
    """Create a summary describing the string-cleaning impact."""
    comparisons: dict[str, Any] = {}
    for col in df_before.columns:
        before_values = set(df_before[col].dropna().astype(str).tolist())
        after_values = set(df_after[col].dropna().astype(str).tolist())
        comparisons[col] = {
            "unique_before": len(before_values),
            "unique_after": len(after_values),
            "reduced": len(before_values) - len(after_values),
        }
    return comparisons


def run_string_cleaning_pipeline(
    input_file: str | Path = DEFAULT_INPUT,
    output_file: str | Path = DEFAULT_OUTPUT,
    summary_file: str | Path = DEFAULT_SUMMARY,
) -> pd.DataFrame:
    """Load a messy dataset, clean the text fields, and save the cleaned output."""
    path = Path(input_file)
    if not path.exists():
        df = pd.DataFrame(
            {
                "customer_name": [" John ", "john", "JOHN", None],
                "product_category": [" Electronics ", "electronics", "ELECTRONICS", ""],
                "customer_segment": ["B2B", "b 2 b", "business-to-business", "sme"],
                "city": ["São Paulo", "Montréal", "New York", "São Paulo"],
            }
        )
    else:
        df = pd.read_csv(path)

    df_before = df.copy()

    print("\nSTRIP WHITESPACE")
    df = strip_all_strings(df)

    print("\nNORMALIZE CASING")
    df = normalize_casing(df, ["customer_name", "product_category", "customer_segment"])

    print("\nREMOVE SPECIAL CHARACTERS")
    df = remove_special_characters(df, ["city"])

    print("\nSTANDARDIZE CATEGORIES")
    segment_map = {
        "b2b": "B2B",
        "b 2 b": "B2B",
        "business-to-business": "B2B",
        "sme": "SMB",
        "small medium enterprise": "SMB",
        "enterprise": "Enterprise",
    }
    df = standardize_categories(df, {"customer_segment": segment_map})

    print("\nAPPLY REUSABLE CLEANER")
    df["customer_name"] = clean_text_column(df["customer_name"], lowercase=True, strip=True)
    df["product_category"] = clean_text_column(df["product_category"], lowercase=True, strip=True)
    df["city"] = clean_text_column(df["city"], lowercase=True, strip=True, remove_special=True)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    summary = build_cleaning_report(df_before, df)
    summary_path = Path(summary_file)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(str(summary), encoding="utf-8")

    print(f"\nCleaned data saved to {output_path}")
    print(f"Summary saved to {summary_path}")
    return df


if __name__ == "__main__":
    run_string_cleaning_pipeline()
