# Clean Data Layer Naming Conventions

This document establishes team-wide standards for naming, defining, and organizing SQL views and pre-aggregated summary tables across all database schemas and reporting layers.

---

## Views
- **Prefix**: `vw_`
- **Pattern**: `vw_[business_entity]_[metric]`
- **Rule**: Every view must represent a single, focused business concept or metric family. Monolithic "everything" views are explicitly forbidden.
- **Examples**:
  - `vw_active_customers` - Single source of truth for rolling 30-day active customer metrics, activity frequency, and revenue.
  - `vw_product_performance` - Comprehensive sales volume, revenue breakdown, and order velocity per product and category.

---

## Pre-Aggregated Tables
- **Prefix**: `agg_`
- **Pattern**: `agg_[grain]_[subject]`
- **Rule**: Must pre-compute expensive aggregations at a specified time or entity grain (e.g., daily, hourly, customer-level) to serve dashboard queries with sub-millisecond response times.
- **Examples**:
  - `agg_daily_metrics` - Daily summarized business metrics (e.g., daily total revenue, order count).
  - `agg_hourly_metrics` - Real-time metrics refreshed on an hourly schedule.

---

## Columns in Aggregated Tables
All pre-aggregated tables (`agg_`) must conform to mandatory structural standards:
1. **Timestamp Audit Column**: Must include `updated_at` or `created_at` (`TIMESTAMP DEFAULT CURRENT_TIMESTAMP`) to inform consumers when data was pre-computed and detect stale data.
2. **Aggregation Grain Column**: Must explicitly declare the temporal or spatial grain (e.g., `aggregation_date`, `hour_timestamp`, `customer_id`).
3. **Row Count Audit**: Must include `row_count` (`INTEGER`) representing the count of raw transactions merged into the aggregated record for verification and reconciliation.

---

## Benefits of Clean Data Layer Architecture
- **Single Source of Truth**: Business definitions (such as "revenue" or "active customer") live in exactly one SQL view. Updating a definition updates every downstream dashboard automatically.
- **Zero Metric Drift**: Eliminates silent discrepancies where Sales, Operations, and Executive dashboards report conflicting figures.
- **Instant Dashboard Performance**: Pre-aggregating massive raw tables reduces dashboard query execution times from seconds/minutes to milliseconds.
- **Self-Documenting Codebase**: Developers, data analysts, and BI engineers immediately recognize object types (`vw_` vs `agg_` vs raw tables) from naming alone.

---

## Applied Conventions in Repository

| Object Name | Object Type | Naming Pattern | Description / Purpose |
| :--- | :--- | :--- | :--- |
| `vw_active_customers` | SQL View | `vw_[entity]_[metric]` | Identifies non-deleted customers active in the past 30 days. |
| `vw_product_performance` | SQL View | `vw_[entity]_[metric]` | Calculates revenue and units sold per product for completed orders. |
| `agg_daily_metrics` | Pre-Aggregated Table | `agg_[grain]_[subject]` | Daily pre-computed revenue and order counts with `updated_at` timestamp. |

---

## Python Integration Guidelines
- All database connections in python code (e.g., `assignment-33-python.py`) query views (`vw_`) and pre-aggregated tables (`agg_`), never raw transactional tables directly.
- Each Python query block must include clear comments explaining the object purpose and business context.
