PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS warehouse_retail_sales (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL CHECK (year BETWEEN 2017 AND 2020),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    supplier TEXT NOT NULL,
    item_code TEXT NOT NULL,
    item_description TEXT NOT NULL,
    item_type TEXT NOT NULL,
    retail_sales REAL NOT NULL DEFAULT 0,
    retail_transfers REAL NOT NULL DEFAULT 0,
    warehouse_sales REAL NOT NULL DEFAULT 0,
    CHECK (trim(supplier) <> ''),
    CHECK (trim(item_code) <> ''),
    CHECK (trim(item_description) <> ''),
    CHECK (trim(item_type) <> '')
);

CREATE INDEX IF NOT EXISTS idx_warehouse_retail_sales_year_month
    ON warehouse_retail_sales (year, month);

CREATE INDEX IF NOT EXISTS idx_warehouse_retail_sales_supplier
    ON warehouse_retail_sales (supplier);

CREATE INDEX IF NOT EXISTS idx_warehouse_retail_sales_item_type
    ON warehouse_retail_sales (item_type);