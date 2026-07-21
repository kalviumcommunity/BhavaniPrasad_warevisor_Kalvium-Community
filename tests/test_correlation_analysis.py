"""Tests for correlation and relationship analysis module."""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from scripts.correlation_analysis import (
    generate_synthetic_churn_data,
    compute_correlations,
    save_heatmap,
    identify_strong_pairs,
    perform_feature_selection,
    DEFAULT_HEATMAP_FILE,
)


def test_generate_synthetic_churn_data(tmp_path):
    output_file = tmp_path / "test_churn_data.csv"
    df = generate_synthetic_churn_data(output_file, num_records=200, seed=42)

    assert output_file.exists()
    assert len(df) == 200
    assert list(df.columns) == ["customer_id", "engagement", "transactions_per_month", "support_tickets", "churn"]

    # Check correlations
    corr = df.corr()
    assert 0.85 < corr.loc["transactions_per_month", "engagement"] < 0.98
    assert 0.70 < corr.loc["support_tickets", "churn"] < 0.90


def test_compute_correlations():
    # Construct a simple dataframe
    df = pd.DataFrame({
        "engagement": [1, 2, 3, 4, 5],
        "transactions_per_month": [1.1, 2.1, 3.0, 4.2, 4.9],
        "support_tickets": [0, 1, 0, 4, 5],
        "churn": [0, 0, 0, 1, 1]
    })

    pearson_corr, spearman_corr, comparison = compute_correlations(df)

    assert isinstance(pearson_corr, pd.DataFrame)
    assert isinstance(spearman_corr, pd.DataFrame)
    assert isinstance(comparison, pd.DataFrame)

    assert "pearson" in comparison.columns
    assert "spearman" in comparison.columns
    assert comparison.index.isin(df.columns).all()


def test_save_heatmap(tmp_path):
    df = pd.DataFrame({
        "engagement": [1, 2, 3],
        "transactions_per_month": [1, 2, 3],
        "support_tickets": [1, 2, 3],
        "churn": [0, 0, 1]
    })
    corr = df.corr()
    output_plot = tmp_path / "test_heatmap.png"

    saved_path = save_heatmap(corr, output_path=output_plot)

    assert saved_path.exists()
    assert saved_path == output_plot


def test_identify_strong_pairs():
    df = pd.DataFrame({
        "A": [1, 2, 3, 4],
        "B": [1.1, 1.9, 3.1, 4.0],  # highly correlated with A
        "C": [4, 3, 2, 1],          # anti-correlated with A
        "D": [1, 3, 2, 4]           # weakly correlated
    })
    corr = df.corr()
    strong = identify_strong_pairs(corr)

    assert isinstance(strong, pd.Series)
    # A and B are highly correlated (~0.99)
    assert ("A", "B") in strong.index or ("B", "A") in strong.index
    # A and C are highly anti-correlated (~ -1.0)
    assert ("A", "C") in strong.index or ("C", "A") in strong.index


def test_perform_feature_selection():
    df = pd.DataFrame({
        "engagement": [1, 2, 3],
        "transactions_per_month": [1, 2, 3],
        "support_tickets": [1, 2, 3],
        "churn": [0, 0, 1]
    })

    selected_corr = perform_feature_selection(df)

    assert isinstance(selected_corr, pd.DataFrame)
    assert "engagement" not in selected_corr.columns
    assert "transactions_per_month" in selected_corr.columns
    assert "support_tickets" in selected_corr.columns
    assert "churn" in selected_corr.columns
