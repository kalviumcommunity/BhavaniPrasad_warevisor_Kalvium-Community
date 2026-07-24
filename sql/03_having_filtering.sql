-- Task 3: HAVING Filtering - Filter Groups After Aggregation
-- Purpose: Show only groups (aggregated results) that meet metric thresholds
-- Context: Find high-value customers with consistent purchase behavior

SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(amount) as annual_revenue,
    ROUND(AVG(amount), 2) as avg_order_value,
    MAX(transaction_date) as last_purchase_date
FROM transactions
WHERE transaction_date >= '2024-01-01'   -- WHERE: valid date range
  AND status = 'completed'
GROUP BY customer_id
HAVING SUM(amount) > 10000                -- HAVING: filter on aggregate metric
  AND COUNT(*) >= 5                       -- HAVING: minimum transaction count
  AND AVG(amount) > 500                   -- HAVING: high average order value
ORDER BY annual_revenue DESC;

/*
EXPLANATION:
- WHERE filters rows BEFORE grouping (only 2024, completed transactions)
- GROUP BY customer_id aggregates transactions per customer
- HAVING filters GROUPS after aggregation using:
  * SUM(amount) > 10000: total revenue threshold
  * COUNT(*) >= 5: minimum purchase frequency
  * AVG(amount) > 500: avg order value threshold
- These metrics CANNOT be in WHERE (they don't exist until after GROUP BY)
- Result: Only customers meeting business criteria (high-value, frequent, big orders)

KEY INSIGHT:
If you need to reference an aggregate function, it MUST go in HAVING, not WHERE.
*/
