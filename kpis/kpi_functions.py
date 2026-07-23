"""Reusable KPI computation functions.

Each function accepts a pandas DataFrame (or parameters) and returns a dict with numeric "value" and a human-friendly "formatted" string.

Usage:
    from kpis.kpi_functions import calculate_mau, calculate_revenue_per_customer

    kpi = calculate_mau(df)
    print(kpi['value'], kpi['formatted'])
"""

from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np


def _to_datetime_safe(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_datetime(df[col], errors='coerce')


def calculate_mau(
    df: pd.DataFrame,
    transaction_date_col: str = "transaction_date",
    customer_col: str = "customer_id",
    days: int = 30,
    as_of: Optional[pd.Timestamp] = None,
) -> Dict[str, Any]:
    """Monthly Active Users: distinct customers active in last N days.

    Returns: {'value': int, 'formatted': 'X users'}
    """
    if as_of is None:
        as_of = pd.Timestamp.now()
    if transaction_date_col not in df.columns:
        raise ValueError(f"Missing column {transaction_date_col}")

    dates = _to_datetime_safe(df, transaction_date_col)
    cutoff = as_of - pd.Timedelta(days=days)
    active = df.loc[dates >= cutoff, customer_col].nunique()
    return {"value": int(active), "formatted": f"{int(active):,} users"}


def calculate_revenue_per_customer(
    df: pd.DataFrame,
    amount_col: str = "amount",
    customer_col: str = "customer_id",
) -> Dict[str, Any]:
    """Average revenue per unique customer. Returns numeric value and formatted currency string."""
    if amount_col not in df.columns:
        raise ValueError(f"Missing column {amount_col}")
    total_revenue = df[amount_col].sum()
    unique_customers = df[customer_col].nunique() if customer_col in df.columns else 0
    value = float(total_revenue / unique_customers) if unique_customers > 0 else 0.0
    return {"value": value, "formatted": f"${value:,.2f}"}


def calculate_churn_rate(
    df: pd.DataFrame,
    transaction_date_col: str = "transaction_date",
    customer_col: str = "customer_id",
    period_days: int = 30,
    as_of: Optional[pd.Timestamp] = None,
) -> Dict[str, Any]:
    """Churn rate over two consecutive periods of length period_days.

    Example: With period_days=30 and as_of=now:
      Period1 = (now - 60, now - 30]
      Period2 = (now - 30, now]

    Returns: {'value': 0.05, 'formatted': '5.00%'}
    """
    if transaction_date_col not in df.columns:
        raise ValueError(f"Missing column {transaction_date_col}")
    if as_of is None:
        as_of = pd.Timestamp.now()

    dates = _to_datetime_safe(df, transaction_date_col)
    p2_end = as_of
    p2_start = as_of - pd.Timedelta(days=period_days)
    p1_end = p2_start
    p1_start = p1_end - pd.Timedelta(days=period_days)

    mask_p1 = (dates > p1_start) & (dates <= p1_end)
    mask_p2 = (dates > p2_start) & (dates <= p2_end)

    active_p1 = set(df.loc[mask_p1, customer_col].dropna().unique())
    active_p2 = set(df.loc[mask_p2, customer_col].dropna().unique())

    denom = len(active_p1)
    churned = len([c for c in active_p1 if c not in active_p2])
    value = float(churned / denom) if denom > 0 else 0.0
    return {"value": value, "formatted": f"{value:.2%}"}


def calculate_payment_success_rate(
    df: pd.DataFrame,
    payment_status_col: str = "payment_status",
    success_states: Tuple[str, ...] = ("paid", "completed", "success"),
) -> Dict[str, Any]:
    """Payment success rate: successful payments / total attempts.

    Requires a column indicating payment status. Case-insensitive match against success_states.
    Returns: {'value': 0.98, 'formatted': '98.00%'}
    """
    if payment_status_col not in df.columns:
        raise ValueError(f"Missing column {payment_status_col}")
    statuses = df[payment_status_col].astype(str).str.lower()
    successes = statuses.isin([s.lower() for s in success_states]).sum()
    total = len(statuses)
    value = float(successes / total) if total > 0 else 0.0
    return {"value": value, "formatted": f"{value:.2%}"}


def calculate_cac(
    df: pd.DataFrame,
    marketing_cost: float,
    transaction_date_col: str = "transaction_date",
    customer_col: str = "customer_id",
    days_acquisition: int = 30,
    as_of: Optional[pd.Timestamp] = None,
) -> Dict[str, Any]:
    """Customer Acquisition Cost (CAC).

    marketing_cost: total spend in the acquisition window (currency)
    New customers are those whose first transaction falls within the acquisition window.

    Returns: {'value': 35.0, 'formatted': '$35.00'}
    """
    if as_of is None:
        as_of = pd.Timestamp.now()
    if transaction_date_col not in df.columns:
        raise ValueError(f"Missing column {transaction_date_col}")
    dates = _to_datetime_safe(df, transaction_date_col)

    window_start = as_of - pd.Timedelta(days=days_acquisition)
    # First transaction per customer
    grouped = df.assign(_dt=dates).sort_values(transaction_date_col).groupby(customer_col, as_index=False).first()
    new_customers = grouped.loc[pd.to_datetime(grouped[transaction_date_col]) >= window_start, customer_col].nunique()
    value = float(marketing_cost / new_customers) if new_customers > 0 else float('inf')
    formatted = f"${value:,.2f}" if np.isfinite(value) else "N/A (no new customers)"
    return {"value": value, "formatted": formatted}


def calculate_mrr_per_customer(
    df: pd.DataFrame,
    amount_col: str = "amount",
    customer_col: str = "customer_id",
) -> Dict[str, Any]:
    """MRR per customer: sum of recurring amounts divided by number of active customers.

    This function treats 'amount' as monthly recurring amount for subscriptions.
    """
    total = df[amount_col].sum() if amount_col in df.columns else 0.0
    customers = df[customer_col].nunique() if customer_col in df.columns else 0
    value = float(total / customers) if customers > 0 else 0.0
    return {"value": value, "formatted": f"${value:,.2f}"}


def validate_kpis(kpis: Dict[str, Dict[str, Any]], targets: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """Compare computed KPIs against target ranges.

    kpis: mapping of kpi_name -> {'value': numeric, 'formatted': str}
    targets: mapping of kpi_name -> {'min': x, 'max': y}

    Returns: pandas.DataFrame with columns: kpi, actual, target_min, target_max, status
    """
    rows = []
    for kpi_name, target in targets.items():
        actual = float(kpis.get(kpi_name, {}).get("value", 0.0))
        tmin = float(target.get("min", float("-inf")))
        tmax = float(target.get("max", float("inf")))
        status = "PASS" if (tmin <= actual <= tmax) else "ALERT"
        rows.append({
            "kpi": kpi_name,
            "actual": actual,
            "target_min": tmin,
            "target_max": tmax,
            "status": status,
        })
    return pd.DataFrame(rows)


def decompose_revenue(
    df: pd.DataFrame,
    amount_col: str = "amount",
    segment_col: str = "customer_type",
    product_col: str = "product",
) -> Dict[str, Any]:
    """Decompose total revenue into segment and product breakdowns.

    Returns dict with 'total', 'by_segment' (dict), 'by_product' (pandas.Series)
    """
    total = float(df[amount_col].sum()) if amount_col in df.columns else 0.0
    by_segment = df.groupby(segment_col)[amount_col].sum().to_dict() if segment_col in df.columns else {}
    by_product = df.groupby(product_col)[amount_col].sum() if product_col in df.columns else pd.Series(dtype=float)
    return {"total": total, "by_segment": by_segment, "by_product": by_product}


def load_targets(path: str | Path) -> Dict[str, Dict[str, float]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Targets file not found: {p}")
    return json.loads(p.read_text())


if __name__ == "__main__":
    # Example run: attempt to load sample dataset in repo if present
    repo_root = Path(__file__).resolve().parents[1]
    sample = repo_root / "data" / "raw" / "sample.csv"
    if sample.exists():
        df = pd.read_csv(sample)
        try:
            mau = calculate_mau(df)
            rpc = calculate_revenue_per_customer(df)
            churn = calculate_churn_rate(df)
            print(mau, rpc, churn)
        except Exception as e:
            print("Example run failed:", e)
    else:
        print("No sample data found. Import functions and call them with your DataFrame.")
