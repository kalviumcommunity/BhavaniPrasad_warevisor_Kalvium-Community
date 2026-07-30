# KPI Computation Sources & Data Lineage Documentation

This document specifies the data lineage, SQL views, directional logic, and validation details for all five executive KPI cards on the dashboard.

---

## 1. Executive KPI Specifications

### 📊 1. Total Revenue KPI
- **Business Question:** Are overall revenue sales growing compared to last month?
- **Data Source View:** `vw_monthly_kpis` (built upon `vw_daily_revenue` / `orders` table)
- **SQL Computation:**
  ```sql
  SELECT month, total_revenue
  FROM vw_monthly_kpis
  ORDER BY month DESC
  LIMIT 2;
  ```
- **Comparison Logic:** `((Current_Revenue - Prior_Revenue) / Prior_Revenue) * 100`
- **Directional Logic:** Standard (Up is Good `↑` Green, Down is Bad `↓` Red).

---

### 👥 2. Active Users KPI
- **Business Question:** How many unique customers engaged and placed orders this month versus last month?
- **Data Source View:** `vw_active_users` / `vw_monthly_kpis`
- **SQL Computation:**
  ```sql
  SELECT month, active_users
  FROM vw_monthly_kpis
  ORDER BY month DESC
  LIMIT 2;
  ```
- **Comparison Logic:** `((Current_Active_Users - Prior_Active_Users) / Prior_Active_Users) * 100`
- **Directional Logic:** Standard (Up is Good `↑` Green, Down is Bad `↓` Red).

---

### 💳 3. Average Order Value (AOV) KPI
- **Business Question:** Is the average order basket size increasing or decreasing?
- **Data Source View:** `vw_monthly_kpis`
- **SQL Computation:**
  ```sql
  SELECT month, avg_order_value
  FROM vw_monthly_kpis
  ORDER BY month DESC
  LIMIT 2;
  ```
- **Comparison Logic:** `((Current_AOV - Prior_AOV) / Prior_AOV) * 100`
- **Directional Logic:** Standard (Up is Good `↑` Green, Down is Bad `↓` Red).

---

### 🔄 4. Customer Churn Rate KPI
- **Business Question:** What percentage of last month's active customers did not return this month?
- **Data Source View:** `vw_churn_rate` / `vw_monthly_kpis`
- **SQL Computation:**
  ```sql
  SELECT month, churn_rate
  FROM vw_monthly_kpis
  ORDER BY month DESC
  LIMIT 2;
  ```
- **Comparison Logic:** `((Current_Churn - Prior_Churn) / Prior_Churn) * 100`
- **Directional Logic:** **Inverted Metric** (Down is Good `↓` Green `#10b981`, Up is Bad `↑` Red `#ef4444`, `delta_color='inverse'`).

---

### ⭐ 5. Customer Satisfaction (CSAT) KPI
- **Business Question:** Are customer satisfaction ratings remaining high and improving?
- **Data Source View:** `vw_customer_satisfaction` / `vw_monthly_kpis`
- **SQL Computation:**
  ```sql
  SELECT month, satisfaction_score
  FROM vw_monthly_kpis
  ORDER BY month DESC
  LIMIT 2;
  ```
- **Comparison Logic:** `((Current_CSAT - Prior_CSAT) / Prior_CSAT) * 100`
- **Directional Logic:** Standard (Up is Good `↑` Green, Down is Bad `↓` Red).

---

## 2. Follow-Up Question: Automated Data Updates

### Question
> When a new dataset is uploaded, the KPI values should automatically update without code changes. How would you design the KPI system to support this?

### Architectural Solution & Best Practices

1. **Decouple App Logic via Database Views:**
   - The application queries relational views (`vw_monthly_kpis`, `vw_daily_revenue`) rather than raw files or static date ranges.
   - Any newly appended rows in `orders` or `customers` are instantly grouped and aggregated by the underlying database engine.

2. **Dynamic Date Partitioning (Relative Date Queries):**
   - Use dynamic date functions (`strftime('%Y-%m', order_date)`) and relative ordering (`ORDER BY month DESC LIMIT 2`) rather than hardcoded string filters like `'2026-07'`.
   - When a new month of data arrives (e.g. `2026-08`), the query automatically selects `2026-08` as the current period and `2026-07` as the prior period.

3. **ETL Pipeline & Cache Invalidation:**
   - In Streamlit, utilize cache TTL parameters (`@st.cache_data(ttl=300)`) or trigger cache invalidation (`st.cache_data.clear()`) upon file upload.
   - When an automated batch job or user uploads a new dataset, an ingestion script updates `database/data_layer.db`, triggering instant, code-free metric updates on the dashboard.
