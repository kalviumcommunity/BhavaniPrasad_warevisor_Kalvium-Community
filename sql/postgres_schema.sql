-- WareVisor PostgreSQL Database Schema
-- Role-based Access Control (Manager & Product Sender) and Warehouse Retail Sales Item Storing

-- 1. Create Application Users Table for Role-Based Login
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

-- Seed default initial logins for Manager and Product Sender
INSERT INTO app_users (username, password_hash, full_name, email, role)
VALUES 
    ('manager', 'manager123', 'Central Warehouse Manager', 'manager@warevisor.com', 'manager'),
    ('sender', 'sender123', 'Product Dispatch Sender', 'sender@warevisor.com', 'product_sender')
ON CONFLICT (username) DO UPDATE 
SET role = EXCLUDED.role, full_name = EXCLUDED.full_name, email = EXCLUDED.email;

-- 2. Create Warehouse Retail Sales Table (Schema for warehouse_retail_sales_cleaned.csv)
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

-- 3. Optimization Indexes for Querying Items and Metrics
CREATE INDEX IF NOT EXISTS idx_sales_year_month ON warehouse_retail_sales (year, month);
CREATE INDEX IF NOT EXISTS idx_sales_supplier ON warehouse_retail_sales (supplier);
CREATE INDEX IF NOT EXISTS idx_sales_item_code ON warehouse_retail_sales (item_code);
CREATE INDEX IF NOT EXISTS idx_sales_item_type ON warehouse_retail_sales (item_type);

-- 4. Role-based Grants & Security Configuration
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'manager_role') THEN
        CREATE ROLE manager_role;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'product_sender_role') THEN
        CREATE ROLE product_sender_role;
    END IF;
END
$$;

-- Grant Full Administrative Privileges to Manager Role
GRANT ALL PRIVILEGES ON TABLE warehouse_retail_sales TO manager_role;
GRANT ALL PRIVILEGES ON TABLE app_users TO manager_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO manager_role;

-- Grant Item Viewing & Entry Privileges to Product Sender Role
GRANT SELECT, INSERT ON TABLE warehouse_retail_sales TO product_sender_role;
GRANT SELECT ON TABLE app_users TO product_sender_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO product_sender_role;
