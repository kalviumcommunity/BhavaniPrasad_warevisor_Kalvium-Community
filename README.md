# Sales Analytics Dashboard

Interactive analytics dashboard that ingests sales data, computes KPIs, detects threshold breaches, and delivers weekly reports. Built for the operations and sales teams.

## Getting Started

Run these commands to start the application from scratch:

```bash
git clone https://github.com/kalviumcommunity/BhavaniPrasad_warevisor_Kalvium-Community.git
cd BhavaniPrasad_warevisor_Kalvium-Community
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
streamlit run app.py
```

## Dataset

- **Source**: CSV upload or scheduled pipeline ingestion
- **Columns**: `customer_id`, `order_id`, `amount`, `date`, `segment`
- **Refresh**: Weekly via GitHub Actions pipeline

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kalviumcommunity/BhavaniPrasad_warevisor_Kalvium-Community.git
   cd BhavaniPrasad_warevisor_Kalvium-Community
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your SMTP credentials
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Usage

Upload a CSV file or let the pipeline load data automatically. Use sidebar filters to explore. Check KPI cards for status. Review alerts for threshold breaches. Send reports via email.

## Pipeline Architecture

```text
CSV Upload / Scheduled Ingest
        |
    Ingestion: Load raw CSV, validate file format
        |
    Cleaning: Drop nulls, cast types, filter invalid rows
        |
    Aggregation: Group by segment, compute revenue and order count
        |
    Output: Write cleaned.csv and aggregated.csv to output/
        |
    Dashboard: Load processed data, compute KPIs, render charts
        |
    Alerts: Check metrics against thresholds, display warnings
        |
    Reports: Generate summary, send via email
```

## Derived Features

| Column | Type | Description | Example |
| --- | --- | --- | --- |
| revenue_30d | float | Sum of order amounts last 30 days | 4523.50 |
| days_since_order | integer | Days since most recent order | 12 |
| churn_risk | string | Risk category based on activity | "high" |
| null_pct | float | Percentage of null values per column | 2.3 |

## Known Limitations

- Data refreshes weekly. Dashboard does not show real-time data.
- Revenue excludes refunded orders.
- Segment classification based on self-reported category field.
- Alert thresholds are static (no seasonal adjustment).
- Email delivery requires SMTP configuration in `.env` file.
- Pipeline assumes CSV with specific column names.

---

## Data Quality & Processing Workflows

### Duplicate Detection and Deduplication
- Script: `scripts/deduplicate_data.py`
- Run: `python scripts/deduplicate_data.py`
- Detects exact and near-duplicates using business keys (`customer_id`, `transaction_date`).
- Audit trail written to `output/removed_duplicates_audit.csv`.

### String Cleaning and Text Normalisation
- Script: `scripts/string_cleaning_pipeline.py`
- Run: `python scripts/string_cleaning_pipeline.py`
- Strips whitespace, normalizes casing, and standardizes categories.

### Merge Validation and Join Auditing
- Script: `scripts/merge_validation.py`
- Run: `python scripts/merge_validation.py`
- Validates row counts and unmatched keys when joining customer and order datasets.

### Feature Engineering for Business Meaning
- Script: `scripts/feature_engineering.py`
- Run: `python scripts/feature_engineering.py`
- Generates transaction rates, spend tiers, and RFM scores.

### Correlation & Relationship Analysis
- Script: `scripts/correlation_analysis.py`
- Run: `python scripts/correlation_analysis.py`
- Computes Pearson and Spearman correlations and exports heatmap to `output/correlation_heatmap.png`.

### SQL Joins & Multi-Table Analysis
- Database setup: `python scripts/setup_joins_db.py`
- Execution: `python sql/sql_joins_demo.py`
- Multi-table relational joins across SQLite tables (`customers`, `orders`, `order_items`, `products`).
