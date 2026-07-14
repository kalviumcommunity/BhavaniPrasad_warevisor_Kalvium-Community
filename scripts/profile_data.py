"""Profile raw data quality before cleaning."""

from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd


NUMERIC_STRING_PATTERN = r"^-?\d+(\.\d+)?$"


DEFAULT_INPUT_FILE = Path("data/raw/quality_test.csv")
DEFAULT_OUTPUT_FILE = Path("output/profile_report.json")


def profile_nulls_and_duplicates(df: pd.DataFrame) -> dict:
    """
    Compute null percentage and duplicate counts per column.

    Returns: Dictionary with null analysis by column
    """
    profile = {
        "null_counts": {},
        "null_percentages": {},
        "exact_duplicate_count": 0,
    }

    row_count = len(df)

    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = (null_count / row_count) * 100 if row_count else 0
        profile["null_counts"][col] = int(null_count)
        profile["null_percentages"][col] = round(null_pct, 2)

    exact_duplicate_count = int(df.duplicated().sum())
    profile["exact_duplicate_count"] = exact_duplicate_count
    profile["duplicate_percentage"] = round((exact_duplicate_count / row_count) * 100, 2) if row_count else 0

    return profile


def profile_numerical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarise numerical columns with statistical measures.

    Returns: DataFrame with min, max, mean, median, std
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns

    stats = {}
    for col in numerical_cols:
        stats[col] = {
            "min": round(df[col].min(), 2),
            "max": round(df[col].max(), 2),
            "mean": round(df[col].mean(), 2),
            "median": round(df[col].median(), 2),
            "std": round(df[col].std(), 2),
            "null_count": int(df[col].isnull().sum()),
        }

    return pd.DataFrame(stats).T


def profile_categorical_columns(df: pd.DataFrame, top_n: int = 5) -> dict:
    """
    Summarise categorical columns with value distributions.

    Returns: Dictionary with unique counts and top values
    """
    categorical_cols = df.select_dtypes(include=["object", "string"]).columns

    profile = {}
    for col in categorical_cols:
        profile[col] = {
            "unique_count": int(df[col].nunique()),
            "top_values": df[col].value_counts().head(top_n).to_dict(),
            "null_count": int(df[col].isnull().sum()),
        }

    return profile


def identify_quality_issues(df: pd.DataFrame, null_threshold: float = 30, duplicate_threshold: float = 5) -> list:
    """
    Identify data quality problems based on thresholds.

    Returns: List of issues found with severity and recommendations
    """
    issues = []

    null_pcts = (df.isnull().sum() / len(df)) * 100 if len(df) else pd.Series(dtype=float)
    for col, pct in null_pcts.items():
        if pct > null_threshold:
            issues.append(
                {
                    "type": "High nulls",
                    "column": col,
                    "severity": "HIGH",
                    "value": f"{pct:.1f}% missing",
                    "recommendation": "Consider imputation or column exclusion",
                }
            )

    dup_count = int(df.duplicated().sum())
    dup_pct = (dup_count / len(df)) * 100 if len(df) else 0
    if dup_pct > duplicate_threshold:
        issues.append(
            {
                "type": "High duplicates",
                "column": "Full row",
                "severity": "HIGH",
                "value": f"{dup_pct:.1f}% duplicated",
                "recommendation": "Deduplication required before analysis",
            }
        )

    id_like_cols = [col for col in df.columns if "id" in col.lower()]
    comparison_cols = [col for col in df.columns if col not in id_like_cols]
    if comparison_cols:
        near_dup_count = int(df.duplicated(subset=comparison_cols).sum())
        near_dup_pct = (near_dup_count / len(df)) * 100 if len(df) else 0
        if near_dup_count > 0:
            issues.append(
                {
                    "type": "Potential duplicate entities",
                    "column": ", ".join(comparison_cols),
                    "severity": "MEDIUM",
                    "value": f"{near_dup_count} repeated records across non-ID fields ({near_dup_pct:.1f}%)",
                    "recommendation": "Review records for entity-level duplicates before cleaning",
                }
            )

    for col in df.select_dtypes(include=[np.number]).columns:
        if (df[col] < 0).any() and "amount" in col.lower():
            issues.append(
                {
                    "type": "Invalid range",
                    "column": col,
                    "severity": "MEDIUM",
                    "value": "Contains negative values",
                    "recommendation": "Investigate negative entries",
                }
            )

    for col in df.select_dtypes(include=["object", "string"]).columns:
        series = df[col].dropna().astype(str)
        numeric_like_values = series[series.str.match(NUMERIC_STRING_PATTERN)]
        if not numeric_like_values.empty and len(numeric_like_values) < len(series):
            issues.append(
                {
                    "type": "Corrupted categorical values",
                    "column": col,
                    "severity": "MEDIUM",
                    "value": f"Found numeric-like entries such as {numeric_like_values.iloc[0]!r}",
                    "recommendation": "Inspect the column for shifted rows or invalid category values",
                }
            )

    return issues


def generate_profile_report(df: pd.DataFrame, filepath: str | Path) -> dict:
    """
    Generate complete data quality report and save to JSON.

    Returns: Complete profile report dictionary
    """
    report = {
        "dataset": str(filepath),
        "record_count": len(df),
        "column_count": len(df.columns),
        "nulls_and_duplicates": profile_nulls_and_duplicates(df),
        "numerical_stats": profile_numerical_columns(df).to_dict(),
        "categorical_stats": profile_categorical_columns(df),
        "quality_issues": identify_quality_issues(df),
    }

    DEFAULT_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print(f"DATA QUALITY PROFILE: {filepath}")
    print(f"{'=' * 60}")
    print(f"Records: {report['record_count']}")
    print(f"Columns: {report['column_count']}")
    print(f"\nQuality Issues Found: {len(report['quality_issues'])}")
    for issue in report["quality_issues"]:
        print(f"  [{issue['severity']}] {issue['type']} in {issue['column']}")
        print(f"    Value: {issue['value']} → {issue['recommendation']}")
    print(f"{'=' * 60}\n")

    return report


def load_data(filepath: str | Path) -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() == ".json":
        return pd.read_json(path)

    raise ValueError(f"Unsupported file format: {path.suffix}")


if __name__ == "__main__":
    data = load_data(DEFAULT_INPUT_FILE)
    generate_profile_report(data, DEFAULT_INPUT_FILE)