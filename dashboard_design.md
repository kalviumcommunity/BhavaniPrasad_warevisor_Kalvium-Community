# Dashboard Design Documentation

## Information Hierarchy Applied
- **Level 1 (Status)**: 5 KPI cards - what they are and why chosen
  - **Revenue**: Crucial for the CEO and Sales Director to monitor overall financial health.
  - **Active Customers**: Measures the current size of the user base, critical for long-term growth.
  - **Avg Order Value**: Shows how much value is derived per transaction, useful for sales strategy.
  - **Churn Rate**: Highlights the percentage of customers leaving; a leading indicator of problems.
  - **NPS Score**: Captures customer satisfaction and loyalty.
- **Level 2 (Trends)**: 2-3 trend charts - what patterns they reveal
  - **Monthly Revenue Trend**: Reveals seasonality and growth trajectory compared to the $5M target.
  - **Customer Growth vs Churn**: Shows the relationship between acquiring new customers and losing existing ones over time.
  - **Average Order Value (AOV)**: Tracks whether customers are spending more per transaction over time.
- **Level 3 (Segments)**: 1-2 comparison charts - which segments need attention
  - **Revenue by Customer Segment**: Identifies that 'Enterprise' and 'Mid-Market' drive most revenue, whereas 'SMB' and 'Starter' might need strategic attention or upselling.
  - **Customer Base by Segment**: Shows the volume distribution across segments.
- **Level 4 (Detail)**: Filters and data table - drill-down capability
  - Interactive sidebar filters for Customer Segment and Date Range allow analysts to isolate specific records in a detailed data table for deeper investigation, complete with CSV export.

## Design Principles Applied
1. **Progressive Disclosure**: Summary visible immediately at the top, trends below, and full detail hidden behind filters at the bottom.
2. **Spatial Organisation**: Most important metrics (Revenue, Customers) are positioned top-left for immediate visibility.
3. **Consistent Metaphor**: Green = good (targets, positive indicators), Red = bad (churn, negative indicators) across all visual elements.
4. **Context Over Numbers**: Every metric includes a comparison, such as a % change delta or a target reference line in charts.

## Colour Palette
- **Primary**: #1f77b4 (blue) - main metrics (e.g., active customers, enterprise revenue)
- **Secondary**: #ff7f0e (orange) - comparison metrics (e.g., AOV, alert limits)
- **Success**: #2ca02c (green) - positive indicators (e.g., targets)
- **Danger**: #d62728 (red) - negative indicators (e.g., churn)

## Target Audience
- **Primary**: VP of Sales (daily user, checks KPIs and trends to adjust short-term strategy)
- **Secondary**: CEO (weekly glance, reads KPI row only for an executive summary)
- **Tertiary**: Analysts (uses filters and exports for deeper investigation of anomalies)

## Data Sources
- **KPI values**: Computed from `vw_monthly_revenue` and `vw_active_customers` views.
- **Trend data**: Queried from `agg_daily_revenue` aggregated table.
- **Segment data**: Computed from `vw_customer_segments` view.
*(Note: For the Streamlit prototype, data is mocked using pandas to simulate these sources)*
