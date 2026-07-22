"""Funnel analysis and drop-off detection workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_PLOT_FILE = DEFAULT_OUTPUT_DIR / "funnel_chart.png"
DEFAULT_REPORT_FILE = DEFAULT_OUTPUT_DIR / "funnel_analysis.txt"
DEFAULT_DATA_FILE = Path("data/raw/funnel_data.csv")

STAGE_COLUMNS = [
    "signup_completed",
    "email_entered",
    "password_created",
    "email_verified",
    "payment_added",
    "first_purchase",
]

STAGE_LABELS = [
    "Sign Up",
    "Email Entered",
    "Password Created",
    "Email Verified",
    "Payment Added",
    "First Purchase",
]


@dataclass(frozen=True)
class FunnelArtifacts:
    """Container for pipeline outputs."""

    stages: dict[str, int]
    funnel_df: pd.DataFrame
    impact_df: pd.DataFrame
    recommendation: str


def generate_synthetic_funnel_data(
    stage_counts: list[int] | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    """Create a synthetic funnel dataset with monotonically decreasing stage counts."""
    del seed  # The synthetic funnel is deterministic by design.

    counts = stage_counts or [10000, 8000, 6000, 5000, 4000, 2000]
    if len(counts) != len(STAGE_COLUMNS):
        raise ValueError(f"Expected {len(STAGE_COLUMNS)} stage counts, received {len(counts)}.")

    if any(counts[index] < counts[index + 1] for index in range(len(counts) - 1)):
        raise ValueError("Stage counts must be non-increasing across the funnel.")

    total_users = counts[0]
    df = pd.DataFrame({"user_id": range(1, total_users + 1)})

    for index, column in enumerate(STAGE_COLUMNS):
        df[column] = (df["user_id"] <= counts[index]).astype(int)

    return df


def load_data(filepath: str | Path = DEFAULT_DATA_FILE) -> pd.DataFrame:
    """Load a funnel dataset or generate a synthetic one when no source file exists."""
    path = Path(filepath)
    if path.exists():
        return pd.read_csv(path)
    return generate_synthetic_funnel_data()


def count_funnel_stages(df: pd.DataFrame, stage_columns: list[str] | None = None) -> dict[str, int]:
    """Count how many users reach each funnel stage."""
    columns = stage_columns or STAGE_COLUMNS
    labels = STAGE_LABELS[: len(columns)]

    missing_columns = [column for column in columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required funnel columns: {missing_columns}")

    stages = {
        label: int(df[column].fillna(0).astype(int).sum())
        for label, column in zip(labels, columns, strict=True)
    }
    return stages


def compute_drop_off(stages: dict[str, int]) -> pd.DataFrame:
    """Compute users lost, completion rate, and drop rate between funnel stages."""
    stage_names = list(stages.keys())
    stage_values = list(stages.values())
    drop_rows: list[dict[str, object]] = []

    for index in range(len(stage_values) - 1):
        users_before = stage_values[index]
        users_after = stage_values[index + 1]
        users_lost = users_before - users_after
        completion_rate = (users_after / users_before) * 100 if users_before else 0.0
        drop_rate = (users_lost / users_before) * 100 if users_before else 0.0

        drop_rows.append(
            {
                "from_stage": stage_names[index],
                "to_stage": stage_names[index + 1],
                "users_before": users_before,
                "users_after": users_after,
                "users_lost": users_lost,
                "completion_rate": f"{completion_rate:.1f}%",
                "drop_rate": f"{drop_rate:.1f}%",
                "drop_rate_value": round(drop_rate, 2),
                "revenue_impact": users_lost * 100,
            }
        )

    return pd.DataFrame(drop_rows)


def rank_business_impact(funnel_df: pd.DataFrame, revenue_per_customer: int = 100) -> pd.DataFrame:
    """Calculate business impact of each drop-off and rank the bottlenecks."""
    impact_df = funnel_df.copy()
    impact_df["revenue_impact"] = impact_df["users_lost"] * revenue_per_customer
    impact_df["priority"] = impact_df["revenue_impact"].apply(lambda value: "HIGH" if value >= 100000 else "MEDIUM")
    return impact_df.sort_values(
        by=["revenue_impact", "drop_rate_value", "users_lost"],
        ascending=False,
        ignore_index=True,
    )


def save_funnel_chart(stages: dict[str, int], output_path: str | Path = DEFAULT_PLOT_FILE) -> Path:
    """Create and save a bar chart for funnel stage volumes."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
    bars = ax.bar(list(stages.keys()), list(stages.values()), color=colors[: len(stages)])

    ax.set_ylabel("Users", fontsize=12)
    ax.set_xlabel("Stage", fontsize=12)
    ax.set_title("Signup Funnel: Volume by Stage", fontsize=14)
    ax.set_ylim(0, max(stages.values()) * 1.15)
    ax.tick_params(axis="x", rotation=45)

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height):,}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)
    return path


def build_recommendation(funnel_df: pd.DataFrame, revenue_per_customer: int = 100) -> str:
    """Write a prioritized recommendation for the highest-impact bottleneck."""
    ranked = rank_business_impact(funnel_df, revenue_per_customer=revenue_per_customer)
    highest_impact = ranked.iloc[0]

    additional_conversions = int(highest_impact["users_lost"] * 0.10)
    additional_revenue = additional_conversions * revenue_per_customer

    return f"""FUNNEL OPTIMIZATION PRIORITY:

CRITICAL BOTTLENECK:
Stage: {highest_impact['from_stage']} -> {highest_impact['to_stage']}
Users Lost: {int(highest_impact['users_lost']):,}
Drop Rate: {highest_impact['drop_rate']}
Revenue Impact: ${int(highest_impact['revenue_impact']):,}

ROOT CAUSE INVESTIGATION NEEDED:
- Is step unclear? (Poor UX)
- Is step too complex? (Too many fields)
- Is step optional? (Should be required)
- Is step timing wrong? (Too early/late in funnel)

RECOMMENDED ACTION:
1. A/B test simplified version of step
2. Monitor drop rate before/after
3. Estimate revenue recovery
4. Roll out to 100% if improvement > 5%

EXPECTED IMPACT:
If we improve {highest_impact['from_stage']} -> {highest_impact['to_stage']} completion by 10%:
Additional conversions: {additional_conversions:,}
Additional revenue: ${additional_revenue:,}
"""


def save_report(artifacts: FunnelArtifacts, output_path: str | Path = DEFAULT_REPORT_FILE) -> Path:
    """Persist a text summary of the funnel analysis."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "FUNNEL ANALYSIS SUMMARY",
        "",
        "Stage counts:",
        str(artifacts.stages),
        "",
        "Drop-off table:",
        artifacts.funnel_df.to_string(index=False),
        "",
        "Business impact:",
        artifacts.impact_df.to_string(index=False),
        "",
        artifacts.recommendation.strip(),
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def run_pipeline() -> FunnelArtifacts:
    """Run the complete funnel analysis workflow."""
    df = load_data()
    stages = count_funnel_stages(df)
    funnel_df = compute_drop_off(stages)
    impact_df = rank_business_impact(funnel_df)
    recommendation = build_recommendation(funnel_df)

    save_funnel_chart(stages)
    save_report(FunnelArtifacts(stages=stages, funnel_df=funnel_df, impact_df=impact_df, recommendation=recommendation))

    return FunnelArtifacts(
        stages=stages,
        funnel_df=funnel_df,
        impact_df=impact_df,
        recommendation=recommendation,
    )


if __name__ == "__main__":
    artifacts = run_pipeline()
    print(artifacts.funnel_df.to_string(index=False))
    print()
    print(artifacts.impact_df.to_string(index=False))
    print()
    print(artifacts.recommendation)