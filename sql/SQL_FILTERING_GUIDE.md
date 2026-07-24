# SQL Filtering, Grouping & Aggregation Guide

## Core Concepts

### WHERE vs HAVING

| Clause | When it Runs | Purpose | Example |
|--------|--------------|---------|---------|
| **WHERE** | **Before** GROUP BY | Data quality & row-level filtering | `WHERE amount > 0 AND status = 'completed'` |
| **HAVING** | **After** GROUP BY & aggregation | Filtered aggregated metric thresholds | `HAVING SUM(amount) > 10000 AND COUNT(*) >= 5` |

---

## Key Principles

### Principle 1: WHERE Filters Rows BEFORE Aggregation

```sql
-- This filters transactions BEFORE grouping
-- Only transactions from 2024 with positive amount are included
SELECT 
    customer_id,
    SUM(amount) as annual_revenue
FROM transactions
WHERE transaction_date >= '2024-01-01'
  AND amount > 0
GROUP BY customer_id;
```

**Why:** Data quality checks belong in WHERE. Exclude garbage before counting.

---

### Principle 2: HAVING Filters GROUPS AFTER Aggregation

```sql
-- This filters GROUPS AFTER summing
-- Groups where total revenue < $10k are excluded
SELECT 
    customer_id,
    SUM(amount) as annual_revenue,
    COUNT(*) as transaction_count
FROM transactions
GROUP BY customer_id
HAVING SUM(amount) > 10000
  AND COUNT(*) >= 5;
```

**Why:** Thresholds on metrics (SUM, COUNT, AVG) go in HAVING. They require aggregation first.

---

### Principle 3: WHERE + HAVING Together

```sql
-- WHERE: exclude invalid rows first
-- Then GROUP BY and aggregate
-- Then HAVING: filter groups by aggregate thresholds
SELECT 
    customer_type,
    COUNT(DISTINCT customer_id) as segment_size,
    SUM(amount) as segment_revenue
FROM transactions
WHERE transaction_date >= '2024-01-01'    -- WHERE: data quality
  AND amount > 0
  AND status = 'completed'
GROUP BY customer_type
HAVING COUNT(DISTINCT customer_id) >= 100  -- HAVING: metric threshold
  AND SUM(amount) > 100000;
```

**Why:** This is production-grade filtering. Quality first (WHERE), then business logic (HAVING).

---

### Principle 4: GROUP BY Multiple Dimensions

Grouping by more than one column slices the data into finer buckets:

```sql
SELECT 
    customer_type,
    DATE_TRUNC('month', transaction_date)::DATE as month,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(amount) as monthly_revenue
FROM transactions
WHERE transaction_date >= '2024-01-01'
GROUP BY customer_type, DATE_TRUNC('month', transaction_date)
ORDER BY month DESC, monthly_revenue DESC;
```

Result: Each row = one (customer_type, month) pair with aggregated metrics.

---

### Principle 5: ORDER BY and RANK() for Rankings

```sql
SELECT 
    customer_type,
    SUM(amount) as total_revenue,
    RANK() OVER (ORDER BY SUM(amount) DESC) as revenue_rank
FROM transactions
WHERE transaction_date >= '2024-01-01'
GROUP BY customer_type
ORDER BY total_revenue DESC;
```

**Why:** ORDER BY sorts final results. RANK() creates a ranking column (handles ties correctly).

---

## Performance Considerations

### ⚡ WHERE is Faster Than HAVING for Row Filtering

```sql
-- ❌ SLOW: Aggregates first, then filters
SELECT customer_id, SUM(amount)
FROM transactions
GROUP BY customer_id
HAVING transaction_date >= '2024-01-01';  -- Wrong! Filters groups, not rows

-- ✅ FAST: Filters rows first, then aggregates
SELECT customer_id, SUM(amount)
FROM transactions
WHERE transaction_date >= '2024-01-01'    -- Correct! Filters rows before GROUP BY
GROUP BY customer_id;
```

**Rule:** If it's a row-level condition, use WHERE. It eliminates rows before aggregation.

---

## Common Patterns

### Pattern 1: Top N Performers

```sql
SELECT TOP 10
    customer_id,
    SUM(amount) as total_revenue
FROM transactions
WHERE transaction_date >= '2024-01-01'
GROUP BY customer_id
HAVING SUM(amount) > 1000
ORDER BY total_revenue DESC;
```

### Pattern 2: Segment Analysis

```sql
SELECT 
    customer_type as segment,
    COUNT(DISTINCT customer_id) as customer_count,
    SUM(amount) as segment_revenue,
    ROUND(AVG(amount), 2) as avg_order_value,
    MIN(amount) as smallest_order,
    MAX(amount) as largest_order
FROM transactions
WHERE transaction_date >= '2024-01-01'
  AND amount > 0
GROUP BY customer_type
HAVING COUNT(DISTINCT customer_id) >= 50
ORDER BY segment_revenue DESC;
```

### Pattern 3: Time Series Aggregation

```sql
SELECT 
    DATE_TRUNC('day', transaction_date)::DATE as day,
    COUNT(*) as transaction_count,
    SUM(amount) as daily_revenue,
    COUNT(DISTINCT customer_id) as unique_customers
FROM transactions
WHERE transaction_date >= '2024-01-01'
GROUP BY DATE_TRUNC('day', transaction_date)
ORDER BY day DESC;
```

### Pattern 4: Percentage Share Within Group

```sql
SELECT 
    customer_type,
    product_category,
    SUM(amount) as category_revenue,
    ROUND(
        100.0 * SUM(amount) / 
        SUM(SUM(amount)) OVER (PARTITION BY customer_type),
        2
    ) as pct_of_segment
FROM transactions
WHERE transaction_date >= '2024-01-01'
GROUP BY customer_type, product_category
ORDER BY customer_type, category_revenue DESC;
```

---

## Testing Your Understanding

### Question 1
**You want to show revenue > $10,000 for Enterprise customers. WHERE or HAVING?**
- Answer: Both. WHERE customer_type = 'Enterprise' (row filter), HAVING SUM(amount) > 10000 (group filter).

### Question 2
**You want to exclude transactions dated before 2024. WHERE or HAVING?**
- Answer: WHERE. Row-level condition, must happen before grouping.

### Question 3
**You want to exclude customer groups with fewer than 5 transactions. WHERE or HAVING?**
- Answer: HAVING. It's a condition on COUNT(*), which is an aggregate.

---

## Common Mistakes

### ❌ Mistake 1: Using aggregate function in WHERE
```sql
-- ERROR: WHERE cannot use aggregates
SELECT customer_id, SUM(amount)
FROM transactions
WHERE SUM(amount) > 1000  -- INVALID!
GROUP BY customer_id;
```
**Fix:** Use HAVING instead.

### ❌ Mistake 2: Filtering rows in HAVING
```sql
-- WRONG: Inefficient (aggregates first, then filters)
SELECT customer_id, SUM(amount)
FROM transactions
GROUP BY customer_id
HAVING transaction_date >= '2024-01-01';  -- VALID but slow and wrong logic
```
**Fix:** Use WHERE for row-level conditions.

### ❌ Mistake 3: Forgetting all non-aggregated columns in GROUP BY
```sql
-- ERROR (MySQL/PostgreSQL strict mode)
SELECT customer_type, customer_id, SUM(amount)
FROM transactions
GROUP BY customer_id;  -- Missing customer_type in GROUP BY
```
**Fix:** All non-aggregated columns must be in GROUP BY.

---

## Summary

| Task | Use This | Reason |
|------|----------|--------|
| Remove invalid rows before grouping | WHERE | Faster, cleaner logic |
| Filter rows by specific values | WHERE | Row-level condition |
| Filter rows by date range | WHERE | Row-level condition |
| Filter groups by aggregated metric | HAVING | Aggregate function required |
| Sort results | ORDER BY | Final result ordering |
| Rank results | RANK() OVER | Create ranking column |

