# Data Dictionary

## Dataset Overview
This dataset contains customer transaction records used for revenue analysis, customer segmentation, and churn modeling. The current sample data is sourced from the repository's raw intake files and is updated as new batches arrive.

- Last Updated: 2025-05-21
- Maintained By: Data Engineering Team
- Source System: CRM transaction feed

## Columns

### customer_id
- **Type**: Integer
- **Business Meaning**: Unique customer identifier from the CRM system
- **Example**: 12456
- **Null Handling**: Never null (primary key)
- **Related KPI**: Customer tracking, lifetime value calculation
- **Updates**: Assigned when the customer is created in CRM

### customer_name
- **Type**: String
- **Business Meaning**: Human-readable customer name used in reporting and support workflows
- **Example**: Alice Smith
- **Null Handling**: Rarely null; should be investigated if missing
- **Related KPI**: Customer experience, manual account review
- **Updates**: Maintained in CRM customer master data

### transaction_amount
- **Type**: Float
- **Business Meaning**: Revenue from a single transaction
- **Example**: 150.50
- **Unit**: USD
- **Null Handling**: Very rare; investigate if present
- **Related KPI**: Monthly revenue, average transaction value, customer lifetime value
- **Updates**: Set when a transaction is completed

### transaction_date
- **Type**: Datetime
- **Business Meaning**: Date the transaction occurred or was completed
- **Example**: 2025-01-15
- **Null Handling**: Should not be null for completed transactions
- **Related KPI**: Sales velocity, monthly revenue trend
- **Updates**: Populated at transaction time

### cust_segment
- **Type**: String
- **Business Meaning**: Customer market segment (B2B, B2C, SMB)
- **Valid Values**: B2B, B2C, SMB
- **Example**: SMB
- **Null Handling**: If null, classify as UNKNOWN
- **Related KPI**: Segment revenue, segment churn rate
- **Updates**: Monthly from CRM classification

### flag_churn
- **Type**: Integer
- **Business Meaning**: Binary indicator of whether the customer churned within 90 days
- **Example**: 0
- **Null Handling**: Should be populated; nulls require investigation
- **Related KPI**: Churn rate prediction, retention analysis
- **Updates**: Derived after the retention window closes

## Column to KPI Mapping

### Monthly Revenue
- **Formula**: SUM(transaction_amount)
- **Related Columns**: transaction_amount, transaction_date
- **Why It Matters**: Tracks total company revenue over time
- **Update Frequency**: Daily

### Sales Velocity
- **Formula**: COUNT(transactions) / days
- **Related Columns**: transaction_date
- **Why It Matters**: Measures how quickly revenue is being generated
- **Update Frequency**: Weekly

### Segment Revenue
- **Formula**: SUM(transaction_amount) grouped by cust_segment
- **Related Columns**: transaction_amount, cust_segment
- **Why It Matters**: Identifies the most profitable market segments
- **Update Frequency**: Monthly

### Churn Rate
- **Formula**: SUM(flag_churn) / total_customers
- **Related Columns**: flag_churn, customer_id
- **Why It Matters**: Critical retention metric for growth planning
- **Update Frequency**: Quarterly

### Customer Lifetime Value
- **Formula**: SUM(transaction_amount) grouped by customer_id
- **Related Columns**: customer_id, transaction_amount
- **Why It Matters**: Helps prioritize high-value customers for retention and upsell
- **Update Frequency**: Monthly

## Ambiguous Columns & Resolutions

### Column: flag_churn
- **Original Ambiguity**: Does it mean the customer is currently churned or will churn in future?
- **Resolved Meaning**: Binary indicator of whether a customer churned within 90 days after the transaction
- **Business Interpretation**: Historical churn flag used for retention model training
- **Proposed Rename**: has_churned_90d
- **Risk If Misunderstood**: Models trained on the wrong definition will produce unreliable predictions

### Column: cust_segment
- **Original Ambiguity**: Does it refer to market segment, customer segment, product segment, or geography?
- **Resolved Meaning**: Customer market segment used in go-to-market planning
- **Business Interpretation**: Informs pricing strategy and sales approach
- **Proposed Rename**: market_segment
- **Risk If Misunderstood**: Revenue analysis by the wrong dimension will mislead segmentation decisions

## Column Relationships

### Revenue per Customer
- **Definition**: SUM(transaction_amount) grouped by customer_id
- **How It Matters**: Identifies high-value customers for retention focus and upsell opportunities
- **Example**: Top 10% of customers may generate a disproportionate share of revenue
- **Related Columns**: customer_id, transaction_amount

### Churn by Segment
- **Definition**: SUM(flag_churn) / SUM(all customers) grouped by cust_segment
- **How It Matters**: Reveals which segments carry the highest churn risk and need intervention
- **Example**: SMB customers may show higher churn than B2B customers
- **Related Columns**: flag_churn, cust_segment, customer_id

### Revenue Velocity
- **Definition**: Rolling sum of transaction_amount over 30-day windows
- **How It Matters**: Tracks monthly sales momentum and growth rate trends
- **Example**: Revenue velocity trending upward quarter over quarter signals improving business momentum
- **Related Columns**: transaction_amount, transaction_date

## Governance Notes
- Any new column should be added to this dictionary before it is used by analysts or models.
- Proposed rename suggestions should be reviewed with business stakeholders and data engineering before implementation.
- Updates should be versioned so downstream reports remain traceable.
