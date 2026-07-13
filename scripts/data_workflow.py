"""Production-style data workflow with separated ingestion, processing, and output stages."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

INPUT_FILE = "data/raw/sample.csv"
OUTPUT_FILE = "output/processed.csv"


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


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw data into analysis-ready format.

    Input: A DataFrame containing raw records with at least a customer_id and amount column.
    Output: A cleaned DataFrame with duplicates removed, missing values filled, and an
    additional high-value flag derived from purchase amount.
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

    # Derive a simple business-friendly flag for downstream segmentation.
    if "amount" in df.columns:
        df["is_high_value"] = df["amount"] >= df["amount"].median()

    # Keep a light summary so the caller can see the impact of the cleaning step.
    rows_after = len(df)
    print(f"[OK] Processed rows: {rows_before} -> {rows_after}")
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
