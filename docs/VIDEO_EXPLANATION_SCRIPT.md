# Video Explanation Script

## 1. What a data dictionary is and why it matters
- Introduce the concept of a data dictionary as the business-facing map of each column in the dataset.
- Explain that it prevents confusion between technical column names and business meaning.
- Mention that it reduces errors in reporting, analytics, and model training by making definitions explicit.

## 2. Example of translating a raw column into business meaning
- Use the example of transaction_amount.
- Explain that the raw column name is technical, but the dictionary clarifies that it represents revenue from a single transaction in USD.
- Highlight that this ensures analysts interpret it consistently.

## 3. Walk through five columns
- customer_id: unique identifier for each customer, used for tracking and lifetime value analysis.
- customer_name: human-readable name used in reporting and support workflows.
- transaction_amount: revenue amount from a single transaction.
- transaction_date: date when the transaction occurred.
- flag_churn: binary churn indicator used for retention analysis.

## 4. Ambiguous columns and how to resolve them
- Explain that flag_churn is ambiguous because it could mean current churn or future churn.
- Describe the resolution: the dictionary defines it as a 90-day churn indicator after the transaction.
- Mention that this avoids misinterpretation by analysts and machine learning teams.

## 5. How to maintain the data dictionary over time
- Recommend that every new column be documented before it is used in dashboards or models.
- Suggest adding a review step in the data pipeline or intake process.
- Encourage version control and periodic updates whenever schemas change.
