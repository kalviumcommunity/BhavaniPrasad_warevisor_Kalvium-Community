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
   # Edit .env with your SMTP & Supabase PostgreSQL credentials
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Usage

Upload a CSV file or let the pipeline load data automatically. Use sidebar filters to explore. Check KPI cards for status. Review alerts for threshold breaches. Send reports via email.

---

## Pipeline & System Architecture

### Data & Application Flow

```text
Product Sender
      │
      ▼
Add Product ────► Submit Product Details
                         │
                         ▼
CSV Ingestion ────► PostgreSQL Database (Supabase)
                         │
                         ▼
Cleaning & Aggregation ──► Manager Dashboard
                         │
                         ▼
               Inventory Analysis & Alerts ──► Weekly Reports & Email Delivery
```

### Detailed Pipeline Stages

```text
CSV Upload / Scheduled Ingest
        │
    Ingestion: Load raw CSV, validate file format
        │
    Cleaning: Drop nulls, cast types, filter invalid rows
        │
    Aggregation: Group by segment, compute revenue and order count
        │
    Output: Write cleaned.csv and aggregated.csv to data/processed/
        │
    Dashboard: Load processed data, compute KPIs, render charts
        │
    Alerts: Check metrics against thresholds, display warnings
        │
    Reports: Generate summary, send via email
```

---

## Database Architecture & Design (PostgreSQL Only)

PostgreSQL (Supabase / SQLAlchemy) powers the application database layer. The connection pool helper lives in [scripts/db_connect.py](scripts/db_connect.py) and schema definitions live in [sql/postgres_schema.sql](sql/postgres_schema.sql).

```sql
-- Application Users Table (Exclusively using app_users schema)
CREATE TABLE IF NOT EXISTS app_users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('manager', 'product_sender')),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Products Table referencing app_users
CREATE TABLE IF NOT EXISTS products (
    product_id BIGSERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    sku VARCHAR(100) NOT NULL UNIQUE,
    sender_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES app_users (user_id) ON DELETE CASCADE
);

-- Inventory Table referencing products
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL,
    warehouse VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
);

-- Shipments Table referencing app_users and products
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id BIGSERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    shipment_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES app_users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
);

-- Returns Table referencing products
CREATE TABLE IF NOT EXISTS returns (
    return_id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
);
```

---

## Data Processing Workflow

### Executing the Data Workflow Script

Run the automated data workflow from the repository root:

```bash
python scripts/data_workflow.py
```

This ingests the raw sales dataset, processes and standardizes the records, and writes cleaned output to `data/processed/warehouse_retail_sales_cleaned.csv`.

### Core Workflow Functions

- **`ingest_data(filepath)`**: Reads source CSV files into a pandas DataFrame and validates structure.
- **`process_data(df)`**: Removes exact and near-duplicates, fills missing numeric values, standardizes casing/strings, and flags high-value transactions.
- **`output_results(df, output_path)`**: Exports the processed DataFrame to disk and prints an execution audit summary.

### Adapting for New Datasets

1. Update the input path constants at the top of `scripts/data_workflow.py`.
2. Ensure the target file includes required schema columns or adjust transformation logic.
3. Re-run `python scripts/data_workflow.py` to produce a updated clean dataset.

---

## Derived Features

| Column | Type | Description | Example |
| --- | --- | --- | --- |
| revenue_30d | float | Sum of order amounts last 30 days | 4523.50 |
| days_since_order | integer | Days since most recent order | 12 |
| churn_risk | string | Risk category based on activity | "high" |
| null_pct | float | Percentage of null values per column | 2.3 |

---

## Data Quality & Processing Workflows

### Duplicate Detection and Deduplication
- **Script**: `scripts/deduplicate_data.py`
- **Run**: `python scripts/deduplicate_data.py`
- Detects exact and near-duplicates using business keys (`customer_id`, `transaction_date`).
- Writes audit log to `output/removed_duplicates_audit.csv`.

### String Cleaning and Text Normalization
- **Script**: `scripts/string_cleaning_pipeline.py`
- **Run**: `python scripts/string_cleaning_pipeline.py`
- Strips whitespace, normalizes casing, and standardizes text categories.

### Merge Validation and Join Auditing
- **Script**: `scripts/merge_validation.py`
- **Run**: `python scripts/merge_validation.py`
- Audits row counts and unmatched keys when merging customer and order datasets.

### Feature Engineering for Business Meaning
- **Script**: `scripts/feature_engineering.py`
- **Run**: `python scripts/feature_engineering.py`
- Generates transaction rates, spend tiers, and RFM scores.

### Correlation & Relationship Analysis
- **Script**: `scripts/correlation_analysis.py`
- **Run**: `python scripts/correlation_analysis.py`
- Computes Pearson and Spearman correlations and exports heatmap to `output/correlation_heatmap.png`.

---

## Known Limitations

- Data refreshes weekly. Dashboard does not show real-time streaming data.
- Revenue metrics exclude refunded orders.
- Segment classification is based on self-reported category fields.
- Alert thresholds are static (no dynamic seasonal adjustments).
- Email delivery requires valid SMTP configuration in `.env`.
- Pipeline assumes CSVs match expected schema column names.
