# BhavaniPrasad_warevisor_Kalvium-Community

## Duplicate Detection and Deduplication

The project now includes a reproducible deduplication workflow for handling exact and near-duplicate records.

### What is included
- A Python script at [scripts/deduplicate_data.py](scripts/deduplicate_data.py) that:
  - detects exact duplicates with pandas `.duplicated()`
  - detects near-duplicates using business keys such as `customer_id` and `transaction_date`
  - removes duplicates while keeping the most complete record
  - writes an audit trail to [output/removed_duplicates_audit.csv](output/removed_duplicates_audit.csv)
  - writes before/after metrics to [output/dedup_summary.json](output/dedup_summary.json)

### Generated artifacts
- Deduplicated dataset: [data/processed/deduplicated_data.csv](data/processed/deduplicated_data.csv)
- Audit summary: [output/dedup_audit_summary.json](output/dedup_audit_summary.json)
- Sample duplicate input: [data/raw/data_with_dupes.csv](data/raw/data_with_dupes.csv)

### Run it
```bash
python scripts/deduplicate_data.py
```

### Verification
The regression test at [tests/test_deduplicate_data.py](tests/test_deduplicate_data.py) confirms that exact duplicates are removed, near-duplicates are reduced to the best record, and the audit files are produced.

## String Cleaning and Text Normalisation

The project also includes a reusable string-cleaning pipeline for messy text fields.

### What is included
- A Python script at [scripts/string_cleaning_pipeline.py](scripts/string_cleaning_pipeline.py) that:
  - strips whitespace from string columns
  - normalizes casing to lowercase
  - removes special characters with regex
  - standardizes category labels using mapping dictionaries
  - exposes a reusable helper, [scripts/string_cleaning_pipeline.py](scripts/string_cleaning_pipeline.py), for any text column

### Generated artifacts
- Cleaned dataset: [data/processed/cleaned_strings.csv](data/processed/cleaned_strings.csv)
- Cleaning summary: [output/string_cleaning_summary.json](output/string_cleaning_summary.json)

### Run it
```bash
python scripts/string_cleaning_pipeline.py
```

### Verification
The regression test at [tests/test_string_cleaning_pipeline.py](tests/test_string_cleaning_pipeline.py) confirms that whitespace is stripped, casing is normalized, special characters are removed, and categories are standardized consistently.

## Merge Validation and Join Auditing

The project also includes a merge-validation workflow for joining customer and order data safely and transparently.

### What is included
- A Python script at [scripts/merge_validation.py](scripts/merge_validation.py) that:
  - performs explicit merges with a chosen join type
  - validates row counts before and after the join
  - detects unmatched keys on both sides of the merge
  - writes unmatched-key files and a join report for auditability

### Generated artifacts
- Merged dataset: [data/processed/merged_customers_orders.csv](data/processed/merged_customers_orders.csv)
- Unmatched customers: [output/unmatched_customers.csv](output/unmatched_customers.csv)
- Unmatched orders: [output/unmatched_orders.csv](output/unmatched_orders.csv)
- Join report: [output/join_validation_report.json](output/join_validation_report.json)

### Run it
```bash
python scripts/merge_validation.py
```

### Verification
The regression test at [tests/test_merge_validation.py](tests/test_merge_validation.py) confirms that left joins preserve customer rows, unmatched keys are detected, and join-type comparisons are reported correctly.

## Feature Engineering for Business Meaning

The project now includes a reusable feature-engineering workflow for turning raw customer metrics into interpretable business signals.

### What is included
- A reusable module at [scripts/feature_engineering.py](scripts/feature_engineering.py) that:
  - creates ratio features such as transactions per month, average spend per transaction, and lifetime value per month
  - bins engagement into low/medium/high tiers with `pd.cut`
  - creates quartile-based spend tiers with `pd.qcut`
  - builds an RFM-style composite score from recency, frequency, and monetary components
  - validates the engineered columns for sensible ranges and missingness

### Run it
```bash
python scripts/feature_engineering.py
```

### Verification
The regression test at [tests/test_feature_engineering.py](tests/test_feature_engineering.py) confirms that the engineered features are created and that the validation summaries are populated correctly.
