-- Table: agg_daily_metrics
-- Purpose: Pre-aggregated summary table for high-performance dashboard querying
-- Business Grain: Daily summary by metric name
-- Updated: Periodically via batch refresh schedule (e.g. nightly ETL or hourly worker)
-- Used By: Executive Dashboards, Fast Historical Analysis, Streamlit Apps
-- 
-- Columns:
--   aggregation_date: Date of the aggregated metric snapshot
--   metric_name: Name identifier of business metric (e.g. 'total_revenue', 'completed_order_count')
--   metric_value: Summarized aggregate numerical metric value
--   row_count: Count of underlying transactions summarized in this row
--   updated_at: Timestamp when this aggregation record was computed

CREATE TABLE IF NOT EXISTS agg_daily_metrics (
    aggregation_date DATE,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    row_count INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populate table with daily aggregated revenue metrics
INSERT INTO agg_daily_metrics (aggregation_date, metric_name, metric_value, row_count, updated_at)
SELECT 
    DATE(o.order_date) AS aggregation_date,
    'total_revenue' AS metric_name,
    SUM(o.order_amount) AS metric_value,
    COUNT(*) AS row_count,
    CURRENT_TIMESTAMP AS updated_at
FROM orders o
WHERE o.order_status = 'completed'
GROUP BY DATE(o.order_date);
