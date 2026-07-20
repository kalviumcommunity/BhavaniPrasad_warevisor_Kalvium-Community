import pandas as pd

from scripts.feature_engineering import engineer_customer_features, validate_feature_ranges


def test_feature_engineering_creates_business_features_and_validates_ranges():
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4],
            "total_transactions": [5, 15, 1, 40],
            "days_as_customer": [60, 180, 30, 365],
            "total_spent": [100, 900, 30, 4000],
            "purchase_count": [5, 15, 1, 40],
            "days_since_last_purchase": [10, 90, 20, 5],
        }
    )

    engineered = engineer_customer_features(df)

    assert "transactions_per_month" in engineered.columns
    assert "avg_spend_per_transaction" in engineered.columns
    assert "lifetime_value_per_month" in engineered.columns
    assert "engagement_tier" in engineered.columns
    assert "spend_quartile" in engineered.columns
    assert "rfm_score" in engineered.columns

    assert engineered["transactions_per_month"].notna().all()
    assert engineered["engagement_tier"].notna().all()
    assert engineered["spend_quartile"].notna().all()
    assert engineered["rfm_score"].notna().all()

    validation = validate_feature_ranges(engineered)
    assert validation["engagement_tier_distribution"]["low"] >= 0
    assert validation["rfm_score_range"]["min"] <= validation["rfm_score_range"]["max"]
    assert validation["missing_values"]["engagement_tier"] == 0
    assert validation["missing_values"]["spend_quartile"] == 0
    assert validation["missing_values"]["rfm_score"] == 0
