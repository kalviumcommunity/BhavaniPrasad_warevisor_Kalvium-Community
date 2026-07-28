-- View: vw_active_customers
-- Purpose: Identify active customers with recent order activity (last 30 days)
-- Business Metric: Rolling 30-day active customer count, order count, and revenue per active customer
-- Updated: Evaluated dynamically on query execution (always returns fresh real-time data)
-- Used By: Customer Success Dashboard, Retention Analysis, Executive Overview
-- 
-- Columns:
--   customer_id: Unique customer identifier
--   customer_name: Display name of the customer
--   segment: Customer segment classification (e.g., Enterprise, SMB, Consumer)
--   order_count_30d: Total distinct orders placed in the last 30 days
--   revenue_30d: Total revenue generated from orders in the last 30 days
--   last_order_date: Date of the most recent order placed by customer
--   days_since_order: Days elapsed since customer's last order

CREATE VIEW IF NOT EXISTS vw_active_customers AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.segment,
    COUNT(DISTINCT o.order_id) AS order_count_30d,
    COALESCE(SUM(o.order_amount), 0.0) AS revenue_30d,
    MAX(o.order_date) AS last_order_date,
    CAST((JULIANDAY(CURRENT_DATE) - JULIANDAY(MAX(o.order_date))) AS INTEGER) AS days_since_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
    AND o.order_date >= DATE(CURRENT_DATE, '-30 days')
WHERE c.deleted_at IS NULL
GROUP BY c.customer_id, c.customer_name, c.segment;
