-- Task 2: Detect Unmatched Keys
-- Purpose: Identify inactive customers with no orders and orphaned orders with no matching customer record.

-- 1. Customers with NO orders (Inactive customers)
SELECT 
    c.customer_id, 
    c.customer_type, 
    c.signup_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
ORDER BY c.signup_date;

-- 2. Orders with NO matching customer (Orphaned records)
SELECT 
    o.order_id, 
    o.customer_id, 
    o.order_date,
    o.order_amount
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
ORDER BY o.order_date;
