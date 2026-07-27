# SQL Joins & Multi-Table Analysis Guide

## Core Concepts

Joining tables allows analysts to combine relational datasets using foreign keys. Misunderstanding join mechanics or failing to validate row counts is the primary cause of corrupted analytical reporting and double-counting errors.

### The Three Fundamental Join Types

| Join Type | Included Left Rows | Included Right Rows | Output Row Count Bound | Use Case |
|---|---|---|---|---|
| **INNER JOIN** | Matched only | Matched only | `0 ≤ Rows ≤ min(L × R)` | Strict relationships where both sides must exist (e.g., active orders with valid products). |
| **LEFT JOIN** | All rows | Matched only | `L ≤ Rows ≤ L × R` | Cohort retention, keeping full baseline dataset regardless of secondary activity. |
| **FULL OUTER JOIN** | All rows | All rows | `max(L, R) ≤ Rows ≤ L + R + (matches)` | Reconciling systems, auditing missing records across both tables. |

---

## 1. Join Semantics & Concrete Examples

Given two tables:
- **`customers`** (1,000 rows): `customer_id` 1 to 1000.
- **`orders`** (5,000 rows): 4,900 orders belonging to customers 1..900; 100 orphaned orders belonging to non-existent `customer_id` 9001..9100.

```
customers (1000 rows)                     orders (5000 rows)
+-------------------+                    +-------------------+
| 900 active custs  | <--- MATCHED ----> | 4900 valid orders |
| 100 inactive custs|                    | 100 orphan orders |
+-------------------+                    +-------------------+
```

### Row Count Behavior Across Join Types

1. **INNER JOIN (`customers` ⋈ `orders`)**:
   - Matches only where `c.customer_id = o.customer_id`.
   - **Result**: 4,900 rows. Inactive customers (100) and orphaned orders (100) are excluded.

2. **LEFT JOIN (`customers` ⟕ `orders`)**:
   - Preserves all 1,000 customers.
   - **Result**: 5,000 rows (4,900 matched customer-order rows + 100 inactive customer rows with `NULL` order attributes).

3. **FULL OUTER JOIN (`customers` ⟗ `orders`)**:
   - Preserves all 1,000 customers AND all 5,000 orders.
   - **Result**: 5,100 rows (4,900 matched + 100 inactive customers with `NULL` orders + 100 orphaned orders with `NULL` customer details).

---

## 2. Row Count Validation & Preventing Multiplicity Fan-Out

### Why Validate Row Counts?

A common failure mode in database analysis is **unexpected row multiplication** (fan-out). If a `LEFT JOIN` increases row count beyond expectations, one-to-many relationships are expanding the result set.

### Multiplication Factor Formula

$$\text{Multiplication Factor} = \frac{\text{Post-Join Rows}}{\text{Distinct Left Keys}}$$

- If **Factor = 1.0**: Perfect 1-to-1 or 1-to-0/1 relationship.
- If **Factor > 1.0**: One-to-many relationship exists. This is expected when joining customers to orders, but MUST be documented.

---

## 3. Detecting Unmatched Keys & Orphaned Records

Unmatched keys point to potential data quality defects or inactive user segments.

### SQL Query Patterns

```sql
-- 1. Customers with NO orders (Inactive cohort)
SELECT c.customer_id, c.customer_type, c.signup_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- 2. Orders with NO matching customer (Orphaned records / Broken FKs)
SELECT o.order_id, o.customer_id, o.order_date
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

---

## 4. Multi-Table Joins & Data Lineage

Joining across 3+ tables (e.g., `customers` -> `orders` -> `order_items` -> `products`) creates multi-level fan-out.

### Data Lineage Chain
$$\text{customers (1,000)} \xrightarrow{\text{LEFT JOIN}} \text{orders (5,000)} \xrightarrow{\text{LEFT JOIN}} \text{order\_items (8,000)} \xrightarrow{\text{LEFT JOIN}} \text{products (500)}$$

### Preventing Double-Counting in Aggregations
When joining `orders` (5,000) to `order_items` (8,000), summing `o.order_amount` on the 8,000-row result set will **double-count** revenue for orders with multiple items!

**Rule**: Sum line-item revenue via `(quantity * unit_price)` at the line-item grain, OR aggregate order amounts *before* joining to line items.

---

## 5. Join Strategy Documentation (Task 5)

```text
JOIN STRATEGY DOCUMENTATION

Table Inventory:
- customers: 1,000 rows (PK: customer_id)
- orders: 5,000 rows (PK: order_id, FK: customer_id)
- order_items: 8,000 rows (PK: item_id, FK: order_id, product_id)
- products: 500 rows (PK: product_id)

Decision 1: customers LEFT JOIN orders
- Purpose: Get all customers with their order history while preserving zero-order customers.
- Row count change: 1,000 → 5,000 rows (4,900 matched + 100 inactive customers with NULL orders).
- Unmatched: 100 customers have no orders (retained due to LEFT).
- Business use: Customer lifetime value, churn analysis, segmentation.

Decision 2: orders LEFT JOIN order_items  
- Purpose: Detailed line-item view for basket and revenue analysis.
- Row count change: 5,000 → 8,000 rows (orders with multiple items expand into multiple rows).
- Unmatched: 0 (all orders have at least 1 line item).
- Business use: Product revenue, item volume analysis, category performance.

Decision 3: Full 4-Table Join
- Purpose: Complete order context linking customer segment to product details.
- Row count: 1,000 → 8,100 rows (8,000 line item rows + 100 inactive customers).
- Risk: Avoid double-counting order totals when aggregating across line items.
- Solution: Compute line-item revenue via quantity * unit_price.

Validation: Row counts match expectations, unmatched keys audited (100 inactive customers, 100 orphaned orders), zero duplication confirmed.
```
