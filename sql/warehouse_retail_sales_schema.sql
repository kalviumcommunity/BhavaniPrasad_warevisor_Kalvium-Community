-- WareVisor PostgreSQL Table Schema for warehouse_retail_sales
CREATE TABLE IF NOT EXISTS warehouse_retail_sales (
    record_id BIGSERIAL PRIMARY KEY,
    year INT NOT NULL CHECK (year BETWEEN 2017 AND 2030),
    month INT NOT NULL CHECK (month BETWEEN 1 AND 12),
    supplier VARCHAR(255) NOT NULL,
    item_code VARCHAR(100) NOT NULL,
    item_description TEXT NOT NULL,
    item_type VARCHAR(100) NOT NULL,
    retail_sales NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    retail_transfers NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    warehouse_sales NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_warehouse_retail_sales_year_month
    ON warehouse_retail_sales (year, month);

CREATE INDEX IF NOT EXISTS idx_warehouse_retail_sales_supplier
    ON warehouse_retail_sales (supplier);

CREATE INDEX IF NOT EXISTS idx_warehouse_retail_sales_item_type
    ON warehouse_retail_sales (item_type);