"""Build datetime features and time-based aggregations from transaction data."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_FILE = REPO_ROOT / "data" / "raw" / "untyped_data.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"
DEFAULT_OUTPUT_FILE = DEFAULT_OUTPUT_DIR / "datetime_features.csv"
DEFAULT_REPORT_FILE = DEFAULT_OUTPUT_DIR / "datetime_feature_report.json"
DEFAULT_HOUR_PLOT_FILE = DEFAULT_OUTPUT_DIR / "hour_distribution.png"

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def load_transaction_data(filepath: str | Path) -> pd.DataFrame:
    """Load transaction data from CSV or JSON."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() == ".json":
        return pd.read_json(path)

    raise ValueError(f"Unsupported file format: {path.suffix}")


def _normalize_timestamp_strings(series: pd.Series) -> pd.Series:
    """Normalize timestamp strings so they can be parsed with a strict format."""
    values = series.astype(str).str.strip()
    date_only_mask = values.str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    values = values.where(~date_only_mask, values + " 00:00:00")
    return values


def parse_transaction_dates(df: pd.DataFrame, column: str = "transaction_date") -> pd.DataFrame:
    """Convert raw timestamp strings to datetime using an explicit format."""
    if column not in df.columns:
        raise KeyError(f"Missing required column: {column}")

    result = df.copy()
    normalized = _normalize_timestamp_strings(result[column])
    result[column] = pd.to_datetime(normalized, format=TIMESTAMP_FORMAT)
    return result


def add_time_features(df: pd.DataFrame, column: str = "transaction_date") -> pd.DataFrame:
    """Extract common datetime features for analysis."""
    if column not in df.columns:
        raise KeyError(f"Missing required column: {column}")

    result = df.copy()
    result["day_of_week"] = result[column].dt.day_name()
    result["hour"] = result[column].dt.hour
    result["week_num"] = result[column].dt.isocalendar().week.astype(int)
    result["month"] = result[column].dt.month
    result["quarter"] = result[column].dt.quarter
    return result


def compute_recency_metrics(df: pd.DataFrame, customer_column: str = "customer_id", date_column: str = "transaction_date") -> pd.DataFrame:
    """Compute days since last purchase per customer and attach it back to the rows."""
    if customer_column not in df.columns:
        raise KeyError(f"Missing required column: {customer_column}")
    if date_column not in df.columns:
        raise KeyError(f"Missing required column: {date_column}")

    result = df.copy()
    today = pd.Timestamp.now()
    last_purchase = result.groupby(customer_column)[date_column].transform("max")
    result["days_since_last_purchase"] = (today - last_purchase).dt.days
    return result


def build_time_indexed_aggregation(df: pd.DataFrame, date_column: str = "transaction_date", amount_column: str = "amount") -> dict[str, pd.DataFrame | pd.Series]:
    """Create grouped and resampled time-based views of the dataset."""
    if date_column not in df.columns:
        raise KeyError(f"Missing required column: {date_column}")
    if amount_column not in df.columns:
        raise KeyError(f"Missing required column: {amount_column}")

    time_indexed = df.set_index(date_column).sort_index()
    weekly = time_indexed[amount_column].resample("W").agg(["sum", "count", "mean"])
    hourly_daily = df.groupby(["day_of_week", "hour"]).agg({amount_column: ["sum", "count", "mean"]})
    pivot_table = pd.pivot_table(df, values=amount_column, index="hour", columns="day_of_week", aggfunc="sum")

    return {
        "weekly": weekly,
        "hourly_daily": hourly_daily,
        "pivot_table": pivot_table,
    }


def save_hour_distribution_plot(df: pd.DataFrame, output_path: str | Path) -> None:
    """Save a histogram-style plot of the transaction hour distribution."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 5))
    df["hour"].value_counts().sort_index().plot(kind="bar", color="#2a6fdb")
    plt.title("Transaction Volume by Hour")
    plt.xlabel("Hour of Day")
    plt.ylabel("Transaction Count")
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()


def build_feature_pipeline(filepath: str | Path = DEFAULT_INPUT_FILE) -> dict[str, object]:
    """Run the full datetime feature engineering pipeline."""
    df = load_transaction_data(filepath)
    df = parse_transaction_dates(df)
    df = add_time_features(df)
    df = compute_recency_metrics(df)

    aggregations = build_time_indexed_aggregation(df)
    save_hour_distribution_plot(df, DEFAULT_HOUR_PLOT_FILE)

    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DEFAULT_OUTPUT_FILE, index=False)

    report = {
        "filepath": str(Path(filepath).resolve()),
        "timestamp_dtype": str(df["transaction_date"].dtype),
        "min_date": df["transaction_date"].min().isoformat(),
        "max_date": df["transaction_date"].max().isoformat(),
        "days_in_dataset": int((df["transaction_date"].max() - df["transaction_date"].min()).days),
        "hours_with_data": sorted(int(value) for value in pd.Series(df["hour"].unique()).dropna().tolist()),
        "weeks_in_dataset": int(df["week_num"].nunique()),
        "min_days_since_purchase": int(df["days_since_last_purchase"].min()),
        "max_days_since_purchase": int(df["days_since_last_purchase"].max()),
        "day_of_week_counts": df["day_of_week"].value_counts().to_dict(),
        "weekly_metrics": aggregations["weekly"].reset_index().to_dict(orient="records"),
    }

    DEFAULT_REPORT_FILE.write_text(pd.Series(report).to_json(indent=2, default_handler=str), encoding="utf-8")

    print(f"transaction_date dtype: {df['transaction_date'].dtype}")
    print(f"Min date: {df['transaction_date'].min()}")
    print(f"Max date: {df['transaction_date'].max()}")
    print(f"Days in dataset: {(df['transaction_date'].max() - df['transaction_date'].min()).days}")
    print(f"Hours with data: {sorted(df['hour'].unique().tolist())}")
    print(f"Weeks in dataset: {df['week_num'].nunique()}")
    print(f"Min days since purchase: {df['days_since_last_purchase'].min()}")
    print(f"Max days since purchase: {df['days_since_last_purchase'].max()}")
    print("Weekly aggregation:\n", aggregations["weekly"])
    print("Hour/day pivot:\n", aggregations["pivot_table"])

    return {
        "data": df,
        "aggregations": aggregations,
        "report": report,
    }


if __name__ == "__main__":
    try:
        build_feature_pipeline()
    except Exception as exc:  # pragma: no cover - defensive CLI handling
        print(f"Error: {exc}")
        sys.exit(1)