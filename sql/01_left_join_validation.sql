-- Task 1: LEFT JOIN with Row Count Validation
-- Purpose: Join all customers with their orders (some have multiple orders, some have none)
-- Validate row count changes, order counts per customer, and aggregate spending.

SELECT 
    c.customer_id,
    c.customer_type,
    COUNT(DISTINCT o.order_id) as order_count,
    SUM(o.order_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_type
ORDER BY total_spent DESC NULLS LAST;
