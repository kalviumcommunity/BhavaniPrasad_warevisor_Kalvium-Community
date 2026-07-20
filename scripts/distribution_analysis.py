"""Distribution analysis for business trend interpretation."""

from __future__ import annotations

from pathlib import Path
import json

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks


DEFAULT_INPUT_FILE = Path("data/raw/sample.csv")
DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_DISTRIBUTION_PLOT = DEFAULT_OUTPUT_DIR / "revenue_distribution.png"
DEFAULT_SEGMENT_PLOT = DEFAULT_OUTPUT_DIR / "revenue_segment_comparison.png"
DEFAULT_REPORT_FILE = DEFAULT_OUTPUT_DIR / "distribution_report.json"
VALUE_COLUMN_CANDIDATES = ("revenue", "transaction_amount", "amount")


def load_data(filepath: str | Path) -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() == ".json":
        return pd.read_json(path)

    raise ValueError(f"Unsupported file format: {path.suffix}")


def resolve_value_column(df: pd.DataFrame, preferred_column: str | None = None) -> str:
    candidate_columns: list[str] = []

    if preferred_column and preferred_column in df.columns:
        candidate_columns.append(preferred_column)

    for column in VALUE_COLUMN_CANDIDATES:
        if column in df.columns and column not in candidate_columns:
            candidate_columns.append(column)

    for column in df.select_dtypes(include=["number"]).columns:
        if column not in candidate_columns:
            candidate_columns.append(column)

    if not candidate_columns:
        raise ValueError("No numeric column available for distribution analysis.")

    return candidate_columns[0]


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if series.empty:
        raise ValueError(f"Column '{column}' does not contain numeric values.")
    return series


def _build_business_interpretation(skewness: float, kurtosis_value: float, high_value_mean: float, low_value_mean: float) -> str:
    skew_text = "highly right-skewed" if skewness > 1 else "approximately symmetric" if abs(skewness) <= 0.5 else "moderately skewed"
    kurtosis_text = "heavy-tailed with likely outliers" if kurtosis_value > 3 else "not strongly heavy-tailed"
    segment_text = "distinct high-value and low-value customer groups" if high_value_mean > low_value_mean * 3 else "a less pronounced segment split"

    return (
        f"The distribution is {skew_text}, so the median is a more representative business metric than the mean. "
        f"Kurtosis suggests the data is {kurtosis_text}. "
        f"Segment comparison points to {segment_text}, which means the business should avoid a single uniform strategy."
    )


def _save_distribution_plot(series: pd.Series, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(series, bins=50, edgecolor="black", color="#4c78a8")
    axes[0].set_title(f"{series.name} Distribution (Histogram)")
    axes[0].set_xlabel(series.name)
    axes[0].set_ylabel("Count")

    series.plot(kind="density", ax=axes[1], color="#f58518")
    axes[1].set_title(f"{series.name} Distribution (KDE)")
    axes[1].set_xlabel(series.name)

    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def _save_segment_plot(series: pd.Series, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lower_bound = series.quantile(0.25)
    upper_bound = series.quantile(0.75)
    low_value = series[series <= lower_bound]
    high_value = series[series >= upper_bound]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(low_value, bins=30, alpha=0.7, label="Low-Value", color="#72b7b2")
    ax.hist(high_value, bins=30, alpha=0.7, label="High-Value", color="#e45756")
    ax.set_title(f"{series.name}: High vs Low Value Customers")
    ax.set_xlabel(series.name)
    ax.set_ylabel("Count")
    ax.legend()

    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def analyze_distribution(
    df: pd.DataFrame,
    target_column: str | None = None,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict:
    column = resolve_value_column(df, target_column)
    series = _numeric_series(df, column)

    skewness = float(stats.skew(series, bias=False))
    kurtosis_value = float(stats.kurtosis(series, bias=False))

    percentiles = series.quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).round(2).to_dict()
    q1 = float(series.quantile(0.25))
    median = float(series.quantile(0.5))
    q3 = float(series.quantile(0.75))
    p90 = float(series.quantile(0.9))
    p99 = float(series.quantile(0.99))

    histogram_bins = min(20, max(5, int(np.sqrt(len(series)))))
    counts, _ = np.histogram(series, bins=histogram_bins)
    prominence = max(counts.max() * 0.1, 1) if len(counts) else 1
    peaks, _ = find_peaks(counts, prominence=prominence)

    abnormal_patterns: list[str] = []
    if abs(skewness) > 1:
        abnormal_patterns.append("Highly skewed distribution; the median is likely more representative than the mean.")
    if kurtosis_value > 3:
        abnormal_patterns.append("Heavy tails suggest extreme values and outliers are influencing the distribution.")
    if len(peaks) >= 2:
        abnormal_patterns.append("Histogram shape shows multiple peaks, which can indicate two or more customer segments.")
    if p90 - q3 > max(q3 - median, 1) * 3:
        abnormal_patterns.append("Large upper-tail jump suggests a separate high-value customer group.")

    low_value = series[series <= q1]
    high_value = series[series >= q3]

    distribution_plot = _save_distribution_plot(series.rename(column), Path(output_dir) / DEFAULT_DISTRIBUTION_PLOT.name)
    segment_plot = _save_segment_plot(series.rename(column), Path(output_dir) / DEFAULT_SEGMENT_PLOT.name)

    report = {
        "column": column,
        "record_count": int(series.shape[0]),
        "mean": round(float(series.mean()), 2),
        "median": round(float(median), 2),
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "skewness": round(skewness, 4),
        "kurtosis": round(kurtosis_value, 4),
        "percentiles": percentiles,
        "top_1_percent_threshold": round(p99, 2),
        "abnormal_patterns": abnormal_patterns,
        "segment_comparison": {
            "low_value_count": int(low_value.shape[0]),
            "high_value_count": int(high_value.shape[0]),
            "low_value_mean": round(float(low_value.mean()), 2) if not low_value.empty else None,
            "high_value_mean": round(float(high_value.mean()), 2) if not high_value.empty else None,
            "low_value_median": round(float(low_value.median()), 2) if not low_value.empty else None,
            "high_value_median": round(float(high_value.median()), 2) if not high_value.empty else None,
        },
        "plots": [str(distribution_plot), str(segment_plot)],
    }

    report["business_interpretation"] = _build_business_interpretation(
        skewness,
        kurtosis_value,
        report["segment_comparison"]["high_value_mean"] or 0.0,
        report["segment_comparison"]["low_value_mean"] or 0.0,
    )

    output_path = Path(output_dir) / DEFAULT_REPORT_FILE.name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(report, file_handle, indent=2, default=str)

    print(f"Analyzed {column} across {report['record_count']} records.")
    print(f"Skewness: {report['skewness']:.2f}")
    print(f"Kurtosis: {report['kurtosis']:.2f}")
    print(report["business_interpretation"])
    if abnormal_patterns:
        print("Abnormal patterns:")
        for pattern in abnormal_patterns:
            print(f"- {pattern}")
    print(f"Distribution plot saved to {distribution_plot}")
    print(f"Segment comparison plot saved to {segment_plot}")
    print(f"Report saved to {output_path}")

    return report


if __name__ == "__main__":
    data = load_data(DEFAULT_INPUT_FILE)
    analyze_distribution(data)