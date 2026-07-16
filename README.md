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
