-- Task 2: GROUP BY on Multiple Dimensions with Multiple Aggregate Functions
-- Purpose: Slice data by customer_type and month, computing 5+ metrics
-- Context: Monthly revenue trend by customer segment

SELECT 
    c.customer_type,
    DATE_TRUNC('month', t.transaction_date)::DATE as month,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    COUNT(*) as transaction_count,
    SUM(t.amount) as monthly_revenue,
    ROUND(AVG(t.amount), 2) as avg_transaction_value,
    MIN(t.amount) as min_transaction,
    MAX(t.amount) as max_transaction,
    ROUND(STDDEV(t.amount), 2) as stddev_transaction
FROM transactions t
INNER JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= '2024-01-01'   -- WHERE: data quality first
  AND t.status = 'completed'
  AND t.amount > 0
GROUP BY c.customer_type, DATE_TRUNC('month', t.transaction_date)
ORDER BY month DESC, monthly_revenue DESC;

/*
EXPLANATION:
- GROUP BY on 2 dimensions: customer_type and month
- WHERE filters rows BEFORE grouping (only valid 2024 transactions)
- 9 aggregate functions: COUNT(DISTINCT), COUNT(*), SUM, AVG, MIN, MAX, STDDEV
- Result: Each (customer_type, month) combo shows revenue trends and volatility
- ORDER BY shows most recent months first, then by revenue within each month
*/
