from __future__ import annotations

import pandas as pd

from scripts.funnel_analysis import (
    FunnelArtifacts,
    build_recommendation,
    compute_drop_off,
    count_funnel_stages,
    generate_synthetic_funnel_data,
    rank_business_impact,
    save_funnel_chart,
    save_report,
)


def test_generate_synthetic_funnel_data():
    df = generate_synthetic_funnel_data()

    assert len(df) == 10000
    assert list(df.columns) == ["user_id", "signup_completed", "email_entered", "password_created", "email_verified", "payment_added", "first_purchase"]
    assert df["signup_completed"].sum() == 10000
    assert df["email_entered"].sum() == 8000
    assert df["first_purchase"].sum() == 2000


def test_funnel_metrics_and_business_rank(tmp_path):
    df = pd.DataFrame(
        {
            "signup_completed": [1, 1, 1, 1],
            "email_entered": [1, 1, 1, 0],
            "password_created": [1, 1, 0, 0],
            "email_verified": [1, 0, 0, 0],
            "payment_added": [1, 0, 0, 0],
            "first_purchase": [0, 0, 0, 0],
        }
    )

    stages = count_funnel_stages(df)
    assert stages["Sign Up"] == 4
    assert stages["Email Entered"] == 3
    assert stages["Password Created"] == 2

    funnel_df = compute_drop_off(stages)
    assert list(funnel_df.columns) == [
        "from_stage",
        "to_stage",
        "users_before",
        "users_after",
        "users_lost",
        "completion_rate",
        "drop_rate",
        "drop_rate_value",
        "revenue_impact",
    ]
    assert funnel_df.iloc[0]["users_lost"] == 1

    impact_df = rank_business_impact(funnel_df, revenue_per_customer=100)
    assert impact_df.iloc[0]["revenue_impact"] >= impact_df.iloc[-1]["revenue_impact"]
    assert set(impact_df["priority"]) <= {"HIGH", "MEDIUM"}

    plot_path = tmp_path / "funnel_chart.png"
    report_path = tmp_path / "funnel_analysis.txt"
    assert save_funnel_chart(stages, plot_path).exists()

    artifacts = FunnelArtifacts(
        stages=stages,
        funnel_df=funnel_df,
        impact_df=impact_df,
        recommendation=build_recommendation(funnel_df),
    )
    assert save_report(artifacts, report_path).exists()


def test_recommendation_mentions_priority():
    stages = {
        "Sign Up": 10000,
        "Email Entered": 8000,
        "Password Created": 6000,
        "Email Verified": 5000,
        "Payment Added": 4000,
        "First Purchase": 2000,
    }
    funnel_df = compute_drop_off(stages)
    recommendation = build_recommendation(funnel_df)

    assert "FUNNEL OPTIMIZATION PRIORITY" in recommendation
    assert "First Purchase" in recommendation
    assert "Additional revenue" in recommendation