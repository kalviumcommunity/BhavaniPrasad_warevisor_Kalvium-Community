-- Task 5: ORDER BY and Ranking - Surface Top/Bottom Performers
-- Purpose: Rank segments and customers by revenue, show top 20
-- Context: Board reporting - which segments drive revenue?

SELECT 
    c.customer_type as segment,
    c.industry,
    COUNT(DISTINCT t.customer_id) as segment_customers,
    SUM(t.amount) as total_revenue,
    ROUND(AVG(t.amount), 2) as avg_order,
    COUNT(*) as transaction_count,
    RANK() OVER (ORDER BY SUM(t.amount) DESC) as revenue_rank,
    DENSE_RANK() OVER (ORDER BY SUM(t.amount) DESC) as dense_revenue_rank,
    ROUND(
        100.0 * SUM(t.amount) / SUM(SUM(t.amount)) OVER (),
        2
    ) as pct_of_total
FROM transactions t
INNER JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= '2024-01-01'   -- WHERE: data quality
  AND t.status = 'completed'
  AND t.amount > 0
GROUP BY c.customer_type, c.industry
HAVING COUNT(DISTINCT t.customer_id) >= 10  -- HAVING: minimum viable segment
  AND SUM(t.amount) > 5000                   -- HAVING: material revenue
ORDER BY total_revenue DESC                  -- ORDER BY: sort descending
LIMIT 20;                                    -- Show only top 20

/*
EXPLANATION:

ORDER BY Clause:
  ORDER BY total_revenue DESC
  → Sorts results by highest revenue first (descending)
  → Result rows are presented in this order to stakeholders

RANK() vs DENSE_RANK():
  RANK() OVER (ORDER BY SUM(t.amount) DESC)
    → Assigns rank with gaps on ties (1, 2, 2, 4, 5, ...)
    → Use when you want to see how many rows precede this one
  
  DENSE_RANK() OVER (ORDER BY SUM(t.amount) DESC)
    → Assigns rank without gaps on ties (1, 2, 2, 3, 4, ...)
    → Use for cleaner reporting, no gaps

Percentage of Total (Window Function):
  SUM(SUM(t.amount)) OVER () as total
  → Computes grand total across all groups
  → Allows showing each segment's % contribution to overall revenue

LIMIT 20:
  → Only returns top 20 segments
  → Common for executive dashboards ("top 20 account segments")

Result: Board-ready report showing:
  - Rank 1-20 segments by revenue
  - Each segment's customer count, transaction count
  - % contribution to total company revenue
  - Ranking methodology visible for questions
*/
