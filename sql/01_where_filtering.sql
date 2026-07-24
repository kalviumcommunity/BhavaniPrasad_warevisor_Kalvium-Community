-- Task 1: WHERE Filtering - Data Quality Before Grouping
-- Purpose: Filter invalid/incomplete records BEFORE aggregation
-- Context: Remove refunds, invalid statuses, future dates, etc.

SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(amount) as annual_revenue,
    MIN(transaction_date) as first_transaction,
    MAX(transaction_date) as last_transaction
FROM transactions
WHERE transaction_date >= '2024-01-01'      -- Date range: valid period
  AND transaction_date <= '2024-12-31'      -- Exclude future-dated transactions
  AND amount > 0                             -- Remove refunds/credits (negative)
  AND status = 'completed'                   -- Only successfully completed transactions
GROUP BY customer_id
ORDER BY annual_revenue DESC;

/*
EXPLANATION:
- All WHERE conditions filter ROWS before GROUP BY aggregation
- This ensures we only count valid, completed transactions from 2024
- Much faster than filtering AFTER aggregation
- Result: Each customer's clean annual revenue with transaction count
*/
