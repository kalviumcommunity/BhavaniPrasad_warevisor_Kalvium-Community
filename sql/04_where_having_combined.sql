-- Task 4: WHERE + HAVING Combined - Production-Grade Filtering
-- Purpose: Real-world query combining data quality (WHERE) and business logic (HAVING)
-- Context: Find Enterprise segment with significant revenue impact

SELECT 
    c.customer_type,
    COUNT(DISTINCT t.customer_id) as segment_customer_count,
    COUNT(*) as segment_transaction_count,
    SUM(t.amount) as segment_total_revenue,
    ROUND(AVG(t.amount), 2) as segment_avg_order_value,
    ROUND(
        100.0 * SUM(t.amount) / 
        SUM(SUM(t.amount)) OVER (),  -- % of grand total
        2
    ) as pct_of_total_revenue
FROM transactions t
INNER JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= '2024-01-01'      -- WHERE: valid date range
  AND t.transaction_date <= '2024-12-31'      -- WHERE: exclude future dates
  AND t.status = 'completed'                   -- WHERE: only successful txns
  AND t.amount > 0                             -- WHERE: exclude refunds
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 100   -- HAVING: minimum segment size
  AND SUM(t.amount) > 100000                   -- HAVING: significant revenue
  AND COUNT(*) >= 1000                         -- HAVING: volume threshold
ORDER BY segment_total_revenue DESC;

/*
EXPLANATION:

WHERE CLAUSE (Rows filtered BEFORE grouping):
  1. transaction_date >= '2024-01-01' and <= '2024-12-31'
     → Only transactions from calendar year 2024
  2. status = 'completed'
     → Exclude pending, failed, cancelled transactions
  3. amount > 0
     → Exclude refunds, credits, negative adjustments

GROUP BY:
  c.customer_type
  → Aggregate transactions into customer segments (Enterprise, SMB, Startup, etc.)

HAVING CLAUSE (Groups filtered AFTER aggregation):
  1. COUNT(DISTINCT t.customer_id) >= 100
     → Segment must have at least 100 unique customers
  2. SUM(t.amount) > 100000
     → Segment revenue must exceed $100k (business impact)
  3. COUNT(*) >= 1000
     → Segment must have significant transaction volume

PERFORMANCE NOTE:
WHERE eliminates ~80% of invalid rows BEFORE aggregation.
HAVING then filters aggregated groups, not individual rows.
This is much faster than alternatives.

Result: Segments that are:
  - From valid 2024 completed transactions
  - Large enough (100+ customers, 1000+ txns)
  - Significant revenue ($100k+)
*/
