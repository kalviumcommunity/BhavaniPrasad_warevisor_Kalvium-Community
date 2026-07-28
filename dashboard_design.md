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

---

## Follow-Up Question: Date Range Filtering in Plotly

**Question:** You have a time-series Plotly chart showing revenue by week. You want to add a date range slider so users can select which weeks to view (e.g., "show me only Q1 2024"). How would you implement this in Plotly?

**Answer:**
In Plotly, there are two primary ways to add date range filtering directly to a time-series chart without relying on external UI components (like Streamlit sidebars): **Rangeselector buttons** and the **Rangeslider**.

### 1. Rangeselector Buttons
These are clickable buttons overlaid on the chart (e.g., "1M", "6M", "YTD", "ALL") that instantly snap the x-axis to a predefined date range.

**When to use:** Better for executive dashboards where users want quick, predefined insights without having to manually scrub through dates. It saves time and is very mobile-friendly.

```python
fig.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(step="all")
        ])
    )
)
```

### 2. Rangeslider
This adds a miniature version of the chart below the main x-axis with draggable handles, allowing the user to seamlessly click and drag to define a custom time window.

**When to use:** Better for deep analytical tools where analysts need fine-grained control to isolate specific, non-standard periods (e.g., investigating a specific anomalous 3-week period).

```python
fig.update_xaxes(
    rangeslider_visible=True
)
```

For maximum flexibility, you can actually enable both at the same time:
```python
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)
```
