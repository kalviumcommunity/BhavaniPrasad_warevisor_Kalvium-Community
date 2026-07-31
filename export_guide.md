# Analysis Report Guide

## What's Included

### cleaned_data.csv
- **Purpose:** Raw analysis data for further exploration in Excel
- **Rows:** Filtered records based on dashboard or schedule state
- **Columns:** customer_id, segment, churn_risk, revenue, last_activity, etc.
- **Use Case:** Stakeholders can filter, sort, and build their own pivot tables
- **Refresh:** Updated daily at 5pm (if using schedule) or dynamically exported from dashboard.

### summary_report.pdf
- **Purpose:** Executive summary suitable for meetings and email
- **Content:** Key findings, business impact, recommendations
- **Length:** 1-2 pages
- **Use Case:** Share with leadership, embed in presentations
- **Format:** Professional PDF layout

### interactive_report.html
- **Purpose:** Full analysis with interactive charts
- **Content:** All findings, all visualizations, detailed metrics
- **Size:** Single file, no dependencies (except Plotly CDN)
- **Use Case:** Explore data in browser, zoom/pan/hover to see details
- **Sharing:** Email the HTML file to anyone - it opens in any browser

## How to Use These Files

1. **For Excel analysis:** Open `cleaned_data.csv` in Excel, build your own charts.
2. **For presentations:** Print or email `summary_report.pdf`.
3. **For exploration:** Open `interactive_report.html` in browser, hover for tooltips.
4. **For sharing:** Send `interactive_report.html` - no Python required to view.

## When Are These Files Updated?

- **Daily at 5pm:** Fresh exports with latest data via the scheduled script `scripts/scheduled_export.py`.
- **On-demand:** Click the "Export" button in the Streamlit dashboard sidebar for an immediate custom export.

## Questions?

- Data definitions: See the dynamically generated `README.md` inside each specific timestamped export folder.
