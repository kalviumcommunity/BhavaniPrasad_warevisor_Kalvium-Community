# Feature Engineering Summary

## Why the new features are better than raw columns
Raw counts like total transactions or total spent are hard to interpret on their own. A customer with 50 transactions over 5 years behaves very differently from a customer with 50 transactions in one month. The engineered features add business context by converting raw values into signals such as engagement rate, spend intensity, and customer value.

## 1. Ratio features
- transactions_per_month: shows how actively the customer engages over time.
- avg_spend_per_transaction: reflects purchase value per order.
- lifetime_value_per_month: captures customer value normalized by tenure.

These features are useful because they make comparisons fair across customers with different lengths of history.

## 2. Binning with pd.cut vs pd.qcut
- pd.cut uses fixed, business-defined thresholds. It is appropriate when the business already knows the ranges that matter, such as low/medium/high engagement.
- pd.qcut uses quantiles and is appropriate when the goal is to create balanced groups, such as quartiles for spend tiers.

## 3. Composite score construction
The RFM-style score combines:
- recency_score: how recently the customer bought
- frequency_score: how often the customer buys
- monetary_score: how much they spend

The final rfm_score is the sum of these component scores. This creates a single interpretable signal that can be used for segmentation or prioritization.

## 4. Most business-meaningful feature
The most useful feature in this workflow is transactions_per_month because it normalizes customer activity by time. It is far more actionable than raw transaction counts and helps distinguish engaged customers from occasional buyers.

## 5. Data leakage guardrails
To avoid leakage, features must be computed only from information available at the observation point. The workflow avoids using future purchase behavior and uses only the available historical customer metrics already present in the dataset.
