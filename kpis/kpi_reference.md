# KPI Reference

This document formally defines key business KPIs, their formulas, data sources, targets, owners and update frequency. Use these definitions as the single source of truth for dashboards and reports.

---

KPI: Monthly Active Users (MAU)
Definition: Distinct customers with at least one transaction in the last 30 days
Formula: COUNT(DISTINCT customer_id) WHERE transaction_date >= (AS_OF_DATE - 30 days)
Data Source: transactions table (columns: customer_id, transaction_date)
Target Range: 5,000 - 6,000
Owner: Product Manager
Update Frequency: Daily
Notes: Use UTC dates. If definition changes, document the restatement for historical comparisons. Use `calculate_mau(df, days=30)` from kpi_functions.py.

---

KPI: Revenue per Customer (RPC)
Definition: Average revenue generated per unique customer over the measurement period (default last 30 days)
Formula: SUM(amount) / COUNT(DISTINCT customer_id) WHERE transaction_date in measurement window
Data Source: transactions table (columns: customer_id, amount, transaction_date)
Target Range: $90 - $110
Owner: Finance
Update Frequency: Daily
Notes: Exclude refunds and chargebacks or subtract them from amount. Use `calculate_revenue_per_customer(df)`.

---

KPI: Churn Rate (30-day)
Definition: Fraction of customers active in prior 30-day window who had no activity in the following 30-day window
Formula: (COUNT(customers active in days [-60,-31] and not active in days [-30,0])) / COUNT(customers active in days [-60,-31])
Data Source: transactions table (customer_id, transaction_date)
Target Range: 0% - 5% (0.00 - 0.05)
Owner: Customer Success
Update Frequency: Weekly
Notes: Use `calculate_churn_rate(df, period_days=30)`; if denominator is zero, churn rate = 0.

---

KPI: Payment Success Rate
Definition: Fraction of payment attempts that succeeded (successful payments / total payment attempts)
Formula: COUNT(payments where status in success_states) / COUNT(all payment attempts)
Data Source: payments table (payment_id, status, amount, customer_id, attempted_at)
Target Range: 95% - 100% (0.95 - 1.00)
Owner: Payments Team
Update Frequency: Hourly
Notes: Clearly specify which status values count as success (e.g., 'paid', 'completed'). Use `calculate_payment_success_rate(df, payment_status_col)`.

---

KPI: Customer Acquisition Cost (CAC)
Definition: Total acquisition spend over a period divided by number of new customers acquired in that period
Formula: SUM(marketing_spend) / COUNT(new_customers_acquired_in_period)
Data Source: marketing_spend table (date, campaign, cost) + customer acquisition timestamp (first transaction/first paid) in transactions table
Target Range: $0 - $50
Owner: Marketing
Update Frequency: Monthly
Notes: Define "new customer" consistently (e.g., first transaction_date in period). Use `calculate_cac(df, marketing_cost, days_acquisition)`.

---

KPI: MRR per Customer (optional)
Definition: Monthly recurring revenue normalized per active customer
Formula: (Sum of recurring subscription revenue for month) / COUNT(active_customers_in_month)
Data Source: subscriptions table (subscription_id, monthly_amount, customer_id, billing_status)
Target Range: Set per business model
Owner: Finance / Revenue Operations
Update Frequency: Monthly
Notes: Use for subscription products only. Use `calculate_mrr_per_customer(df_subscriptions)`.


# Change log
- 2026-07-23: Initial kpi_reference.md created. Any change to KPI definition must update this file and include a restatement note for historical data.
