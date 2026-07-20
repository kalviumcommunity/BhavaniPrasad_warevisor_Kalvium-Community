"""Reusable feature engineering utilities for customer-level business features."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide two series safely, replacing zero denominators with NaN."""
    safe_denominator = denominator.replace(0, pd.NA)
    return numerator.div(safe_denominator, fill_value=pd.NA)


def _safe_qcut(series: pd.Series, q: int, labels: list[str] | list[int]) -> pd.Series:
    """Create quantile bins robustly when the dataset has few unique values."""
    if series.dropna().empty:
        return pd.Series([pd.NA] * len(series), index=series.index, dtype="object")

    valid = series.dropna()
    unique_count = int(valid.nunique(dropna=True))
    q_actual = min(q, unique_count)
    labels_actual = list(labels)[:q_actual]

    if q_actual < 2:
        return pd.Series([labels_actual[0]] * len(series), index=series.index, dtype="object")

    ranks = valid.rank(method="first")
    bins = pd.qcut(ranks, q=q_actual, labels=labels_actual, duplicates="drop")
    return pd.Series(bins, index=valid.index, dtype="object")


def _prepare_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure the input has the columns needed for the feature pipeline."""
    engineered = df.copy()

    if "total_transactions" not in engineered.columns:
        if "purchase_count" in engineered.columns:
            engineered["total_transactions"] = engineered["purchase_count"]
        else:
            engineered["total_transactions"] = 1

    if "days_as_customer" not in engineered.columns:
        engineered["days_as_customer"] = 30

    if "total_spent" not in engineered.columns:
        if "amount" in engineered.columns:
            engineered["total_spent"] = engineered["amount"]
        else:
            engineered["total_spent"] = 0

    if "purchase_count" not in engineered.columns:
        engineered["purchase_count"] = engineered["total_transactions"]

    if "days_since_last_purchase" not in engineered.columns:
        engineered["days_since_last_purchase"] = 30

    for column in ["total_transactions", "days_as_customer", "total_spent", "purchase_count", "days_since_last_purchase"]:
        engineered[column] = pd.to_numeric(engineered[column], errors="coerce")

    engineered["total_transactions"] = engineered["total_transactions"].fillna(1)
    engineered["days_as_customer"] = engineered["days_as_customer"].fillna(30)
    engineered["total_spent"] = engineered["total_spent"].fillna(0)
    engineered["purchase_count"] = engineered["purchase_count"].fillna(engineered["total_transactions"])
    engineered["days_since_last_purchase"] = engineered["days_since_last_purchase"].fillna(30)
    return engineered


def engineer_customer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create business-facing ratio, tiered, and composite features for customers."""
    if df.empty:
        raise ValueError("Input DataFrame is empty. No data to process.")

    engineered = _prepare_feature_columns(df)

    engineered["transactions_per_month"] = _safe_divide(
        engineered["total_transactions"],
        engineered["days_as_customer"] / 30,
    )
    engineered["avg_spend_per_transaction"] = _safe_divide(
        engineered["total_spent"],
        engineered["total_transactions"],
    )
    engineered["lifetime_value_per_month"] = _safe_divide(
        engineered["total_spent"],
        engineered["days_as_customer"] / 30,
    )

    engineered["engagement_tier"] = pd.cut(
        engineered["transactions_per_month"],
        bins=[0, 2, 10, float("inf")],
        labels=["low", "medium", "high"],
        include_lowest=True,
    )

    engineered["spend_quartile"] = _safe_qcut(
        engineered["total_spent"],
        q=4,
        labels=["Q1", "Q2", "Q3", "Q4"],
    )
    engineered["spend_quartile"] = engineered["spend_quartile"].fillna("Q1")

    engineered["recency_score"] = _safe_qcut(
        engineered["days_since_last_purchase"],
        q=5,
        labels=[5, 4, 3, 2, 1],
    )
    engineered["frequency_score"] = _safe_qcut(
        engineered["purchase_count"],
        q=5,
        labels=[1, 2, 3, 4, 5],
    )
    engineered["monetary_score"] = _safe_qcut(
        engineered["total_spent"],
        q=5,
        labels=[1, 2, 3, 4, 5],
    )

    for column in ["recency_score", "frequency_score", "monetary_score"]:
        engineered[column] = engineered[column].fillna(3)

    engineered["rfm_score"] = (
        engineered["recency_score"].astype(int)
        + engineered["frequency_score"].astype(int)
        + engineered["monetary_score"].astype(int)
    )

    return engineered


def validate_feature_ranges(df: pd.DataFrame) -> dict[str, Any]:
    """Return summary metrics for the engineered feature ranges and missingness."""
    validation = {
        "engagement_tier_distribution": df["engagement_tier"].value_counts(dropna=False).to_dict(),
        "rfm_score_range": {
            "min": int(df["rfm_score"].min()),
            "max": int(df["rfm_score"].max()),
        },
        "missing_values": {
            column: int(df[column].isna().sum())
            for column in ["engagement_tier", "spend_quartile", "rfm_score"]
        },
    }
    return validation


def run_feature_engineering(input_path: str | Path = "data/processed/merged_customers_orders.csv", output_path: str | Path = "output/feature_engineered.csv") -> dict[str, Any]:
    """Read a customer dataset, engineer features, and write the transformed output."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    df = pd.read_csv(input_file)
    engineered = engineer_customer_features(df)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    engineered.to_csv(output_file, index=False)

    validation = validate_feature_ranges(engineered)
    print(f"[OK] Wrote {len(engineered)} rows to {output_file}")
    print(validation)
    return validation


if __name__ == "__main__":
    run_feature_engineering()
