-- Task 3: Compare Join Types
-- Purpose: Contrast INNER JOIN, LEFT JOIN, and FULL OUTER JOIN semantics and row counts.

-- 1. INNER JOIN (matched records only: excludes inactive customers AND orphaned orders)
SELECT c.customer_id, c.customer_type, o.order_id, o.order_amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;

-- 2. LEFT JOIN (all left customers preserved, matched with orders where available)
SELECT c.customer_id, c.customer_type, o.order_id, o.order_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- 3. FULL OUTER JOIN (all records from both customers and orders tables preserved)
SELECT c.customer_id, c.customer_type, o.order_id, o.order_amount
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;
