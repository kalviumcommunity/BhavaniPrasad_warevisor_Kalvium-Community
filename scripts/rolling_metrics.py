"""Time-series trend analysis with rolling metrics and resampling outputs."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_FILE = REPO_ROOT / "data" / "raw" / "sample.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"
DEFAULT_PLOT_FILE = DEFAULT_OUTPUT_DIR / "rolling_avg.png"
DEFAULT_REPORT_FILE = DEFAULT_OUTPUT_DIR / "trend_analysis.txt"

DATE_CANDIDATES = ("date", "transaction_date", "order_date", "timestamp")
VALUE_CANDIDATES = ("revenue", "transaction_amount", "amount", "sales")
COUNT_CANDIDATES = ("orders", "order_id", "customer_id")


def load_time_series_data(filepath: str | Path) -> pd.DataFrame:
    """Load a CSV or JSON file into a DataFrame."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() == ".json":
        return pd.read_json(path)

    raise ValueError(f"Unsupported file format: {path.suffix}")


def _resolve_column(df: pd.DataFrame, candidates: tuple[str, ...], kind: str) -> str:
    """Pick the first matching column from a list of candidates."""
    for column in candidates:
        if column in df.columns:
            return column
    available = ", ".join(df.columns)
    raise KeyError(f"Could not find a {kind} column. Available columns: {available}")


def _prepare_time_series(df: pd.DataFrame) -> tuple[pd.DataFrame, str, str, str]:
    """Normalize the input into a dated series with a numeric value column."""
    result = df.copy()
    date_column = _resolve_column(result, DATE_CANDIDATES, "date")
    value_column = _resolve_column(result, VALUE_CANDIDATES, "value")
    count_column = _resolve_column(result, COUNT_CANDIDATES, "count")

    result[date_column] = pd.to_datetime(result[date_column], errors="coerce")
    result = result.dropna(subset=[date_column]).sort_values(date_column)
    result[value_column] = pd.to_numeric(result[value_column], errors="coerce")
    result = result.dropna(subset=[value_column])

    return result, date_column, value_column, count_column


def build_time_series_metrics(df: pd.DataFrame) -> dict[str, object]:
    """Compute rolling averages, resampled views, change rates, and cumulative totals."""
    prepared, date_column, value_column, count_column = _prepare_time_series(df)
    time_indexed = prepared.set_index(date_column).sort_index()

    if time_indexed.empty:
        raise ValueError("No valid time-series rows available after parsing dates and values.")

    daily = time_indexed[value_column].resample("D").sum().asfreq("D", fill_value=0)
    weekly = daily.resample("W").agg(["sum", "count", "mean"])
    monthly = daily.resample("ME").agg(["sum", "count", "mean"])

    rolling_7 = daily.rolling(window=7, min_periods=1).mean()
    rolling_30 = daily.rolling(window=30, min_periods=1).mean()
    cumulative = daily.cumsum()
    mom_change = monthly["sum"].pct_change() * 100
    wow_change = weekly["sum"].pct_change() * 100

    recent_window = rolling_30.tail(min(30, len(rolling_30)))
    if len(recent_window) < 2:
        trend_direction = "flat"
        trend_magnitude = 0.0
    else:
        delta = recent_window.iloc[-1] - recent_window.iloc[0]
        baseline = recent_window.iloc[0]
        if baseline == 0:
            trend_magnitude = 0.0
        else:
            trend_magnitude = float((delta / baseline) * 100)
        if abs(trend_magnitude) < 1e-9:
            trend_direction = "flat"
        elif trend_magnitude > 0:
            trend_direction = "up"
        else:
            trend_direction = "down"

    last_mom_change = float(mom_change.dropna().iloc[-1]) if not mom_change.dropna().empty else 0.0
    volatility = float(daily.std()) if len(daily) > 1 else 0.0

    if trend_direction == "up":
        implication = "Accelerating growth - maintain the current strategy and watch for capacity constraints."
    elif trend_direction == "down":
        implication = "Declining momentum - investigate pricing, demand, and channel performance."
    else:
        implication = "Stable momentum - keep monitoring for a break in pattern before changing strategy."

    report = f"""TREND ANALYSIS

Rolling Average Trend: {trend_direction.upper()}
Change over last 30 days: {trend_magnitude:.1f}%
Month-over-month growth: {last_mom_change:.1f}%

Business Implications:
- {implication}
- Revenue volatility: {volatility:.0f} (measure of noise)
- Highest weekly revenue: {weekly['sum'].max():.0f}
- Highest monthly revenue: {monthly['sum'].max():.0f}

Growth Months:
{', '.join(monthly.index[mom_change > 0].strftime('%Y-%m').tolist()) or 'None'}

Decline Months:
{', '.join(monthly.index[mom_change < 0].strftime('%Y-%m').tolist()) or 'None'}
"""

    summary = {
        "prepared": prepared,
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
        "rolling_7": rolling_7,
        "rolling_30": rolling_30,
        "cumulative": cumulative,
        "mom_change": mom_change,
        "wow_change": wow_change,
        "trend_direction": trend_direction,
        "trend_magnitude": trend_magnitude,
        "report": report,
        "date_column": date_column,
        "value_column": value_column,
        "count_column": count_column,
    }
    return summary


def save_rolling_plot(metrics: dict[str, object], output_path: str | Path = DEFAULT_PLOT_FILE) -> Path:
    """Save the raw series and rolling averages as a comparison plot."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    daily = metrics["daily"]
    rolling_7 = metrics["rolling_7"]
    rolling_30 = metrics["rolling_30"]

    plt.figure(figsize=(12, 6))
    plt.plot(daily.index, daily.values, label="Raw", alpha=0.3, color="#444444")
    plt.plot(rolling_7.index, rolling_7.values, label="7-day MA", color="#2a6fdb")
    plt.plot(rolling_30.index, rolling_30.values, label="30-day MA", color="#d04e00")
    plt.title("Raw Revenue vs Rolling Averages")
    plt.xlabel("Date")
    plt.ylabel("Revenue")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()
    return output


def write_trend_report(report: str, output_path: str | Path = DEFAULT_REPORT_FILE) -> Path:
    """Persist the trend interpretation as plain text."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.strip() + "\n", encoding="utf-8")
    return output


def run_rolling_metrics_pipeline(
    filepath: str | Path = DEFAULT_INPUT_FILE,
    plot_path: str | Path = DEFAULT_PLOT_FILE,
    report_path: str | Path = DEFAULT_REPORT_FILE,
) -> dict[str, object]:
    """Run the full rolling-metrics workflow and write assignment deliverables."""
    df = load_time_series_data(filepath)
    metrics = build_time_series_metrics(df)
    plot_file = save_rolling_plot(metrics, plot_path)
    report_file = write_trend_report(metrics["report"], report_path)

    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Date column: {metrics['date_column']}")
    print(f"Value column: {metrics['value_column']}")
    print("Weekly aggregation:\n", metrics["weekly"])
    print("Monthly aggregation:\n", metrics["monthly"])
    print("Month-over-month change:\n", metrics["mom_change"])
    print(f"Rolling plot saved to {plot_file}")
    print(f"Trend report saved to {report_file}")

    return metrics


if __name__ == "__main__":
    try:
        run_rolling_metrics_pipeline()
    except Exception as exc:  # pragma: no cover - defensive CLI handling
        print(f"Error: {exc}")
        sys.exit(1)