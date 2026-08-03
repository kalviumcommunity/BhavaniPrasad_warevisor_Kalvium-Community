"""Correlation & Relationship Analysis module for churn prediction."""

from __future__ import annotations

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_RAW_DATA_DIR = Path("data/raw")
DEFAULT_CHURN_DATA_FILE = DEFAULT_RAW_DATA_DIR / "churn_data.csv"
DEFAULT_HEATMAP_FILE = DEFAULT_OUTPUT_DIR / "correlation_heatmap.png"


def generate_synthetic_churn_data(
    output_path: str | Path = DEFAULT_CHURN_DATA_FILE,
    num_records: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate a synthetic dataset with controlled correlation relationships.

    The dataset contains:
    - customer_id: uniquely identifying integer
    - transactions_per_month: continuous transaction frequency
    - engagement: continuous engagement level, highly correlated with transactions_per_month (r ~ 0.92)
    - support_tickets: integer number of support tickets, strongly correlated with churn (r ~ 0.80)
    - churn: binary churn indicator (0 or 1)
    """
    np.random.seed(seed)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Generate transactions_per_month and engagement with correlation ~0.92
    transactions_per_month = np.random.uniform(1.0, 15.0, num_records)
    engagement = transactions_per_month + np.random.normal(0, 1.73, num_records)

    # 2. Generate support_tickets and churn using a latent confounder p (customer_pain)
    p = np.random.normal(0, 1, num_records)
    
    # We clip support tickets to be positive integers
    support_tickets = np.round(np.clip(4 * p + np.random.normal(0, 0.1, num_records) + 5, 0, None))
    
    # Generate response_time_hours heavily correlated with pain/churn
    response_time_hours = np.clip(15 * p + 10 + np.random.normal(0, 2, num_records), 0.5, 48.0)
    
    # Churn is a binary variable based on the pain variable
    churn = (p + np.random.normal(0, 0.20, num_records) > 0.1).astype(int)

    df = pd.DataFrame({
        "customer_id": np.arange(1, num_records + 1),
        "engagement": engagement,
        "transactions_per_month": transactions_per_month,
        "support_tickets": support_tickets,
        "response_time_hours": response_time_hours,
        "churn": churn,
    })

    df.to_csv(path, index=False)
    return df


def load_data(filepath: str | Path = DEFAULT_CHURN_DATA_FILE) -> pd.DataFrame:
    """Load the churn dataset. Generates it if missing."""
    path = Path(filepath)
    if not path.exists():
        return generate_synthetic_churn_data(path)
    return pd.read_csv(path)


def compute_correlations(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Task 1: Compute Pearson and Spearman Correlations and compare them with Churn."""
    # Compute Pearson (linear relationships)
    pearson_corr = df.corr(method="pearson")

    # Compute Spearman (monotonic, robust to outliers)
    spearman_corr = df.corr(method="spearman")

    # Compare which correlations differ
    comparison = pd.DataFrame({
        "pearson": pearson_corr["churn"],
        "spearman": spearman_corr["churn"]
    })
    
    print("--- Task 1: Correlation Comparison with Churn ---")
    print(comparison)
    print()
    return pearson_corr, spearman_corr, comparison


def save_heatmap(pearson_corr: pd.DataFrame, output_path: str | Path = DEFAULT_HEATMAP_FILE) -> Path:
    """Task 2: Visualize Correlation Heatmap and save as image."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(pearson_corr, annot=True, cmap="coolwarm", center=0, ax=ax, fmt=".2f")
    ax.set_title("Feature Correlation Matrix")
    plt.tight_layout()
    plt.savefig(path)
    plt.close(fig)

    print("--- Task 2: Correlation Heatmap Saved ---")
    print(f"Heatmap saved to {path}")
    print()
    return path


def identify_strong_pairs(pearson_corr: pd.DataFrame) -> pd.Series:
    """Task 3: Identify Strongly Correlated Pairs (r > 0.70, excluding self-correlation)."""
    # Flatten and find strong correlations
    corr_flat = pearson_corr.unstack()
    
    # Exclude self-correlation (r=1.0)
    # We do this by dropping pairs where indices are equal
    non_self_mask = [index[0] != index[1] for index in corr_flat.index]
    corr_flat = corr_flat[non_self_mask]
    
    strong = corr_flat[corr_flat.abs() > 0.7].sort_values(ascending=False, key=abs)
    strong_pairs = strong.head(10)
    
    print("--- Task 3: Strongly Correlated Pairs (Top 10) ---")
    for (var1, var2), corr in strong_pairs.items():
        print(f"{var1} <-> {var2}: {corr:.2f}")
    print()
    return strong_pairs


def get_business_interpretation() -> dict:
    """Task 4: Business Interpretation of Correlation vs. Causation."""
    analysis = {
        "support_tickets <-> churn": {
            "correlation": 0.80,
            "possible_directions": [
                "support_tickets -> churn (customer gives up after contacting support)",
                "churn -> support_tickets (unhappy customers contact support before leaving)",
                "customer_pain -> both (underlying issue/pain causes both support tickets and churn)"
            ],
            "data_indicates": "Likely customer_pain is the confounder; support tickets are a symptom, not the root cause.",
            "action": "Focus on reducing the underlying customer pain/product issues, rather than blocking support tickets."
        }
    }
    
    print("--- Task 4: Business Interpretation ---")
    print(json.dumps(analysis, indent=2))
    print()
    return analysis


def perform_feature_selection(df: pd.DataFrame) -> pd.DataFrame:
    """Task 5: Drop redundant highly-correlated features."""
    target_cols = ["engagement", "transactions_per_month", "support_tickets", "response_time_hours", "churn"]
    cols = [c for c in target_cols if c in df.columns]
    df_features = df[cols]

    # transactions_per_month and engagement are r=0.92 (correlated)
    # Drop redundant, keep more interpretable feature: transactions_per_month
    if "engagement" in df_features.columns:
        df_features_selected = df_features.drop("engagement", axis=1)
    else:
        df_features_selected = df_features

    print("--- Task 5: Feature Selection (Removed 'engagement') ---")
    selected_corr = df_features_selected.corr()
    print(selected_corr)
    print()
    return selected_corr


def generate_response_time_charts(df: pd.DataFrame) -> None:
    """Generate charts for Response Time vs Churn to support the executive summary."""
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Chart 1: Scatter plot (using binned average churn rate for clarity)
    # Group response time into deciles or bins to calculate churn rate
    df['response_time_bin'] = pd.qcut(df['response_time_hours'], q=20, duplicates='drop')
    scatter_data = df.groupby('response_time_bin', observed=False).agg(
        avg_response_time=('response_time_hours', 'mean'),
        churn_rate=('churn', 'mean')
    ).reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.regplot(data=scatter_data, x='avg_response_time', y='churn_rate', ax=ax, scatter_kws={'alpha': 0.7})
    ax.set_title("Response Time vs Churn Rate")
    ax.set_xlabel("Average Response Time (Hours)")
    ax.set_ylabel("Churn Rate")
    plt.tight_layout()
    plt.savefig(output_dir / "response_time_scatter.png")
    plt.close(fig)

    # Chart 2: Churn rate by response time bucket
    bins = [0, 2, 4, 24, np.inf]
    labels = ['<2 hours', '2-4 hours', '4-24 hours', '>24 hours']
    df['response_bucket'] = pd.cut(df['response_time_hours'], bins=bins, labels=labels)
    
    bar_data = df.groupby('response_bucket', observed=False)['churn'].mean().reset_index()
    bar_data['churn'] = bar_data['churn'] * 100 # Convert to percentage

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=bar_data, x='response_bucket', y='churn', ax=ax, palette='Blues_d')
    ax.set_title("Churn Rate by Response Time Bucket")
    ax.set_xlabel("Response Time")
    ax.set_ylabel("Churn Rate (%)")
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%')
    plt.tight_layout()
    plt.savefig(output_dir / "response_time_bar.png")
    plt.close(fig)

    print("--- Task 6: Response Time Charts Generated ---")
    print(f"Charts saved to {output_dir}")
    print()


def run_pipeline() -> None:
    """Run the complete Correlation & Relationship Analysis pipeline."""
    # Force regenerate to ensure response_time_hours is added
    if DEFAULT_CHURN_DATA_FILE.exists():
        DEFAULT_CHURN_DATA_FILE.unlink()
        
    df = load_data()
    pearson_corr, _, _ = compute_correlations(df)
    save_heatmap(pearson_corr)
    identify_strong_pairs(pearson_corr)
    get_business_interpretation()
    perform_feature_selection(df)
    generate_response_time_charts(df)


if __name__ == "__main__":
    run_pipeline()
