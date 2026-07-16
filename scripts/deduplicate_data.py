"""Detect and remove exact and near-duplicate records from the intake data."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "raw" / "data_with_dupes.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"
DEFAULT_PROCESSED_OUTPUT = REPO_ROOT / "data" / "processed" / "deduplicated_data.csv"
ROW_ID_COLUMN = "__row_id"


def detect_exact_duplicates(df: pd.DataFrame) -> tuple[int, pd.DataFrame]:
    """Find rows where all values are identical and return the duplicate rows."""
    if ROW_ID_COLUMN in df.columns:
        df_for_eval = df.drop(columns=[ROW_ID_COLUMN])
    else:
        df_for_eval = df
    exact_dups = int(df_for_eval.duplicated().sum())
    dup_rows = df[df_for_eval.duplicated(keep=False)].sort_values(by=df_for_eval.columns.tolist())

    print("\nEXACT DUPLICATE DETECTION")
    print("=" * 60)
    print(f"Exact duplicates found: {exact_dups}")
    print(f"Total duplicate rows (including originals): {len(dup_rows)}")

    if len(dup_rows) > 0:
        print("\nSample duplicate rows:")
        print(dup_rows.head(10).to_string())

    return exact_dups, dup_rows


def detect_near_duplicates(df: pd.DataFrame, key_columns: list[str]) -> pd.DataFrame:
    """Find rows with the same business key but different other fields."""
    duplicate_keys = df[df.duplicated(subset=key_columns, keep=False)]

    print("\nNEAR-DUPLICATE DETECTION")
    print("=" * 60)
    print(f"Records with duplicate keys: {len(duplicate_keys)}")
    print(f"Unique key combinations with duplicates: {len(duplicate_keys.groupby(key_columns))}")

    if len(duplicate_keys) > 0:
        print("\nSample groups with duplicate keys:")
        for keys, group in list(duplicate_keys.groupby(key_columns))[:3]:
            print(f"\n  Key: {keys}")
            print(f"  Records in group: {len(group)}")
            print(group.to_string())

    return duplicate_keys


def remove_exact_duplicates(df: pd.DataFrame, keep: str = "first") -> pd.DataFrame:
    """Remove exact duplicates and log the before/after row counts."""
    rows_before = len(df)
    subset_columns = [column for column in df.columns if column != ROW_ID_COLUMN]
    df_dedup = df.drop_duplicates(subset=subset_columns, keep=keep)

    rows_after = len(df_dedup)
    rows_removed = rows_before - rows_after
    removal_pct = (rows_removed / rows_before) * 100 if rows_before else 0.0

    print("\nEXACT DUPLICATE REMOVAL")
    print("=" * 60)
    print(f"Keep strategy: {keep}")
    print(f"Rows before: {rows_before:,}")
    print(f"Rows after:  {rows_after:,}")
    print(f"Rows removed: {rows_removed:,} ({removal_pct:.2f}%)")

    return df_dedup


def remove_near_duplicates(
    df: pd.DataFrame,
    key_columns: list[str],
    keep_strategy: str = "most_complete",
) -> pd.DataFrame:
    """Remove near-duplicates by preserving the best record per business key."""
    rows_before = len(df)

    if keep_strategy == "most_complete":
        kept_rows: list[pd.DataFrame] = []
        for _, group in df.groupby(key_columns, sort=False):
            null_counts = group.isnull().sum(axis=1)
            best_idx = null_counts.idxmin()
            kept_rows.append(group.loc[[best_idx]])
        df_dedup = pd.concat(kept_rows, axis=0)
    elif keep_strategy == "last":
        df_dedup = df.drop_duplicates(subset=key_columns, keep="last")
    else:
        df_dedup = df.drop_duplicates(subset=key_columns, keep="first")

    rows_after = len(df_dedup)
    rows_removed = rows_before - rows_after
    removal_pct = (rows_removed / rows_before) * 100 if rows_before else 0.0

    print("\nNEAR-DUPLICATE REMOVAL")
    print("=" * 60)
    print(f"Keep strategy: {keep_strategy}")
    print(f"Key columns: {key_columns}")
    print(f"Rows before: {rows_before:,}")
    print(f"Rows after:  {rows_after:,}")
    print(f"Rows removed: {rows_removed:,} ({removal_pct:.2f}%)")

    return df_dedup


def log_removed_duplicates(
    df_original: pd.DataFrame,
    df_dedup: pd.DataFrame,
    output_dir: str | Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Save removed rows to disk for audit and compliance purposes."""
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    original_ids = df_original[ROW_ID_COLUMN] if ROW_ID_COLUMN in df_original.columns else df_original.index
    dedup_ids = df_dedup[ROW_ID_COLUMN] if ROW_ID_COLUMN in df_dedup.columns else df_dedup.index
    removed_records = df_original[~original_ids.isin(dedup_ids)]

    print("\nAUDIT LOGGING")
    print("=" * 60)
    print(f"Total records removed: {len(removed_records)}")

    removed_records.to_csv(output_dir / "removed_duplicates_audit.csv", index=False)
    print("✓ Removed records saved to audit file")

    audit_path = output_dir / "removed_duplicates_audit.csv"
    try:
        audit_file = str(audit_path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        audit_file = str(audit_path)

    audit_summary = {
        "removal_timestamp": datetime.now().isoformat(),
        "total_removed": int(len(removed_records)),
        "reason": "Duplicate detection and deduplication",
        "audit_file": audit_file,
        "audit_note": "All removed records logged for compliance and recovery if needed",
    }

    with (output_dir / "dedup_audit_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(audit_summary, handle, indent=2, default=str)

    print("✓ Audit summary saved")
    print("=" * 60)

    return removed_records, audit_summary


def compare_before_after(
    df_original: pd.DataFrame,
    df_dedup: pd.DataFrame,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Create a before/after summary for deduplication impact."""
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    comparison = {
        "rows_before": len(df_original),
        "rows_after": len(df_dedup),
        "rows_removed": len(df_original) - len(df_dedup),
        "removal_percentage": round(((len(df_original) - len(df_dedup)) / len(df_original)) * 100, 2) if len(df_original) else 0.0,
        "columns": len(df_original.columns),
        "nulls_before": int(df_original.isnull().sum().sum()),
        "nulls_after": int(df_dedup.isnull().sum().sum()),
        "timestamp": datetime.now().isoformat(),
    }

    print("\n" + "=" * 70)
    print("DEDUPLICATION FINAL SUMMARY")
    print("=" * 70)
    print(f"Rows before: {comparison['rows_before']:,}")
    print(f"Rows after:  {comparison['rows_after']:,}")
    print(f"Removed:     {comparison['rows_removed']:,} ({comparison['removal_percentage']}%)")
    print(f"\nNulls before: {comparison['nulls_before']:,}")
    print(f"Nulls after:  {comparison['nulls_after']:,}")
    print(f"Null change:  {comparison['nulls_before'] - comparison['nulls_after']:,}")
    print("=" * 70)

    with (output_dir / "dedup_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(comparison, handle, indent=2)

    return comparison


def run_deduplication_workflow(
    input_file: str | Path = DEFAULT_INPUT,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    processed_output: str | Path = DEFAULT_PROCESSED_OUTPUT,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Execute the full deduplication workflow and save the outputs."""
    df = pd.read_csv(input_file)
    df[ROW_ID_COLUMN] = df.index
    df_original = df.copy()

    print("\n" + "=" * 70)
    print("STARTING DEDUPLICATION WORKFLOW")
    print("=" * 70)
    print(f"Initial record count: {len(df):,}")

    print("\n[Step 1/4] Detecting exact duplicates...")
    detect_exact_duplicates(df)

    print("\n[Step 2/4] Detecting near-duplicates by key...")
    detect_near_duplicates(df, key_columns=["customer_id", "transaction_date"])

    print("\n[Step 3/4] Removing exact duplicates (keeping first)...")
    df = remove_exact_duplicates(df, keep="first")

    print("\n[Step 4/4] Removing near-duplicates (keeping most complete)...")
    df = remove_near_duplicates(
        df,
        key_columns=["customer_id", "transaction_date"],
        keep_strategy="most_complete",
    )

    print("\n[Audit] Logging removed records for compliance...")
    log_removed_duplicates(df_original, df, output_dir=output_dir)

    comparison = compare_before_after(df_original, df, output_dir=output_dir)

    processed_path = Path(processed_output)
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df_without_id = df.drop(columns=[ROW_ID_COLUMN], errors=True)
    df_without_id.to_csv(processed_path, index=False)
    print(f"\n✓ Deduplicated data saved to {processed_path}")

    return df, comparison


if __name__ == "__main__":
    run_deduplication_workflow()
