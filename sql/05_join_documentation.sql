-- Task 5: Document Join Decisions
-- Purpose: Formal documentation of relational join design, row count lineage,
-- unmatched key policies, and aggregation grain rules.

/*
================================================================================
JOIN STRATEGY DOCUMENTATION
================================================================================

Table Inventory:
- customers: 1,000 rows (PK: customer_id)
- orders: 5,000 rows (PK: order_id, FK: customer_id)
- order_items: 8,000 rows (PK: item_id, FK: order_id, product_id)
- products: 500 rows (PK: product_id)

--------------------------------------------------------------------------------
Decision 1: customers LEFT JOIN orders
--------------------------------------------------------------------------------
- Purpose: Retain complete customer universe (all 1,000 customers) while incorporating order history.
- Row Count Trajectory: 1,000 customers -> 5,000 rows (4,900 matched customer-order rows + 100 inactive customer rows with NULL orders).
- Unmatched Key Policy: 100 customers have zero orders. They are retained with NULL order attributes for complete cohort analysis.
- Business Use: Customer lifetime value calculation, inactive customer segmentation, churn analysis.

--------------------------------------------------------------------------------
Decision 2: orders LEFT JOIN order_items
--------------------------------------------------------------------------------
- Purpose: Granular line-item breakdown of transactions.
- Row Count Trajectory: 5,000 orders -> 8,000 item rows (multiplied by items per order).
- Unmatched Key Policy: 0 orders without line items. Every order maps to at least 1 order_item.
- Business Use: Product basket analysis, item-level revenue attribution, cross-selling analysis.

--------------------------------------------------------------------------------
Decision 3: Full 4-Table Join (customers -> orders -> order_items -> products)
--------------------------------------------------------------------------------
- Purpose: Comprehensive lineage linking customer demographics to individual product categories and unit prices.
- Row Count Trajectory: 1,000 customers -> 8,100 total rows (8,000 item rows for active customers + 100 inactive customers with NULL order/item rows).
- Multiplicity Risk: Aggregating order_amount at the product/item level will double-count revenue if multiple items exist per order.
- Solution: Calculate line totals via (quantity * unit_price) or aggregate order metrics prior to joining line items.

--------------------------------------------------------------------------------
Validation & Integrity Verification
--------------------------------------------------------------------------------
- Row counts validated before and after every join operation.
- Orphaned orders (100 orders with customer_id not in customers) explicitly detected and audited.
- Line total sums equal sum of raw order_items, confirming zero artificial duplication.
================================================================================
*/
