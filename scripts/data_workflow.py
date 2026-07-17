"""Production-style data workflow with separated ingestion, processing, and output stages."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats

INPUT_FILE = "data/raw/sample.csv"
OUTPUT_FILE = "output/processed.csv"
OUTLIER_LOG_FILE = Path("output/cleaning_log.csv")
OUTLIER_CANDIDATE_COLUMNS = ("revenue", "amount", "transaction_amount")


def _resolve_outlier_column(df: pd.DataFrame, preferred_column: str | None = None) -> str:
    """Pick the most relevant numeric column for statistical outlier detection."""
    candidate_columns: list[str] = []

    if preferred_column and preferred_column in df.columns:
        candidate_columns.append(preferred_column)

    for column in OUTLIER_CANDIDATE_COLUMNS:
        if column in df.columns and column not in candidate_columns:
            candidate_columns.append(column)

    numeric_columns = list(df.select_dtypes(include=["number"]).columns)
    for column in numeric_columns:
        if column not in candidate_columns:
            candidate_columns.append(column)

    if not candidate_columns:
        raise ValueError("No numeric column available for outlier detection.")

    return candidate_columns[0]


def detect_zscore_outliers(series: pd.Series, threshold: float = 3.0) -> tuple[pd.Series, pd.Series]:
    """Return z-score values and a boolean outlier mask for a numeric series."""
    numeric_series = pd.to_numeric(series, errors="coerce")
    if numeric_series.dropna().nunique() <= 1:
        z_scores = pd.Series(0.0, index=series.index)
        return z_scores > threshold, z_scores

    z_values = np.abs(stats.zscore(numeric_series, nan_policy="omit"))
    z_scores = pd.Series(z_values, index=series.index).fillna(0.0)
    return z_scores > threshold, z_scores


def detect_iqr_outliers(series: pd.Series, multiplier: float = 1.5) -> tuple[pd.Series, float, float]:
    """Return an IQR outlier mask and the lower/upper bounds used for detection."""
    numeric_series = pd.to_numeric(series, errors="coerce")
    q1 = numeric_series.quantile(0.25)
    q3 = numeric_series.quantile(0.75)
    iqr = q3 - q1

    if pd.isna(iqr) or iqr == 0:
        lower_bound = q1
        upper_bound = q3
    else:
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

    outlier_mask = (numeric_series < lower_bound) | (numeric_series > upper_bound)
    return outlier_mask.fillna(False), float(lower_bound), float(upper_bound)


def apply_outlier_handling(
    df: pd.DataFrame,
    target_column: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Detect, cap, and flag outliers while creating an auditable cleaning log."""
    working_df = df.copy()
    column = _resolve_outlier_column(working_df, target_column)

    z_outliers, z_scores = detect_zscore_outliers(working_df[column])
    iqr_outliers, lower_bound, upper_bound = detect_iqr_outliers(working_df[column])
    capped_column = f"{column}_capped"

    working_df[f"{column}_zscore"] = z_scores
    working_df["is_outlier_iqr"] = iqr_outliers.astype(bool)
    working_df[capped_column] = pd.to_numeric(working_df[column], errors="coerce").clip(
        lower=lower_bound,
        upper=upper_bound,
    )
    working_df["is_outlier"] = (z_outliers | iqr_outliers).astype(bool)

    cleaning_log = pd.DataFrame(
        [
            {
                "column": column,
                "method": "Z-Score",
                "action": "flag",
                "threshold": 3.0,
                "affected_rows": int(z_outliers.sum()),
                "reasoning": "Values beyond three standard deviations are unusual and should be reviewed.",
            },
            {
                "column": column,
                "method": "IQR",
                "action": "cap",
                "threshold_lower": lower_bound,
                "threshold_upper": upper_bound,
                "affected_rows": int(iqr_outliers.sum()),
                "reasoning": "Values outside the 1.5 x IQR fence are capped to keep rows but limit distortion.",
            },
            {
                "column": column,
                "method": "Combined",
                "action": "flag",
                "threshold": "zscore_or_iqr",
                "affected_rows": int(working_df["is_outlier"].sum()),
                "reasoning": "A binary flag preserves all rows while exposing anomalous records to downstream analysis.",
            },
        ]
    )

    return working_df, cleaning_log


def write_cleaning_log(cleaning_log: pd.DataFrame, output_path: str | Path = OUTLIER_LOG_FILE) -> Path:
    """Persist the outlier cleaning log to CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cleaning_log.to_csv(path, index=False)
    return path


def ingest_data(filepath: str | Path) -> pd.DataFrame:
    """
    Load data from a CSV or JSON file into a pandas DataFrame.

    Args:
        filepath: Path to the source file. CSV and JSON formats are supported.

    Returns:
        A Pandas DataFrame containing the loaded records.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the file type is unsupported.
    """
    path = Path(filepath)

    # Read the file based on its extension so the script can support multiple inputs.
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() == ".json":
        df = pd.read_json(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")

    # Keep the ingestion function focused on reading data only.
    print(f"[OK] Ingested {len(df)} rows from {path}")
    return df


def process_data(df: pd.DataFrame, cleaning_log_path: str | Path = OUTLIER_LOG_FILE) -> pd.DataFrame:
    """
    Transform raw data into analysis-ready format.

    Input: A DataFrame containing raw records with at least a customer_id and amount column.
    Output: A cleaned DataFrame with duplicates removed, missing values filled, outliers
    handled statistically, and an additional high-value flag derived from purchase amount.
    """
    if df.empty:
        raise ValueError("Input DataFrame is empty. No data to process.")

    # Remove exact duplicates so each record is represented once.
    rows_before = len(df)
    df = df.drop_duplicates().copy()

    # Standardize the most important text field so downstream analysis is consistent.
    if "region" in df.columns:
        df["region"] = df["region"].astype(str).str.strip().str.title()

    # Fill numeric missing values using the median to reduce skew from outliers.
    for column in df.select_dtypes(include=["number"]).columns:
        df[column] = df[column].fillna(df[column].median())

    # Detect statistical outliers, cap them, and keep an auditable log of the decision.
    df, cleaning_log = apply_outlier_handling(df)
    write_cleaning_log(cleaning_log, cleaning_log_path)

    # Derive a simple business-friendly flag for downstream segmentation.
    if "amount" in df.columns:
        base_amount = df["amount_capped"] if "amount_capped" in df.columns else df["amount"]
        df["is_high_value"] = base_amount >= base_amount.median()
    elif "transaction_amount" in df.columns:
        base_amount = (
            df["transaction_amount_capped"] if "transaction_amount_capped" in df.columns else df["transaction_amount"]
        )
        df["is_high_value"] = base_amount >= base_amount.median()

    # Keep a light summary so the caller can see the impact of the cleaning step.
    rows_after = len(df)
    print(f"[OK] Processed rows: {rows_before} -> {rows_after}")
    print(f"[OK] Outlier log saved to {Path(cleaning_log_path)}")
    return df


def output_results(df: pd.DataFrame, output_path: str | Path) -> None:
    """
    Write the processed DataFrame to disk and print a confirmation summary.

    Args:
        df: The processed DataFrame to save.
        output_path: Destination file where the CSV data should be written.
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Write the final dataset so it can be consumed by later stages or humans.
    df.to_csv(output, index=False)

    # Print the confirmation messages requested by the assignment.
    print("[OK] Data successfully processed")
    print(f"[OK] Rows processed: {len(df)}")
    print(f"[OK] Output saved to {output}")


if __name__ == "__main__":
    try:
        data = ingest_data(INPUT_FILE)
        processed = process_data(data)
        output_results(processed, OUTPUT_FILE)
    except Exception as exc:  # pragma: no cover - defensive CLI handling
        print(f"Error: {exc}")
        sys.exit(1)
