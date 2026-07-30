# Interactive Plotly Charts (Task 2.46)

This directory contains standalone interactive Plotly HTML chart files generated for assignment 2.46:

## Generated HTML Charts

1. **`chart1_revenue_trend.html`**:
   - **Daily Revenue Trend with Custom Hover**
   - Features `go.Scatter` with line+markers, unified hover template (`<b>%{x|%Y-%m-%d}</b><br>Revenue: $%{y:,.2f}<extra></extra>`), color `#1f77b4`, and `hovermode='x unified'`.

2. **`chart2_product_performance.html`**:
   - **Product Performance with Multi-Column Hover**
   - Features a bar chart showing top products by revenue with multi-metric tooltips revealing Revenue ($), Order Count, and Average Order Value ($).

3. **`chart3_metric_selector.html`**:
   - **Dropdown Filter to Toggle Views**
   - Features interactive `updatemenus` dropdown allowing client-side switching between Revenue, Profit, and Order Count without page reload.

4. **`chart4_interactive.html`**:
   - **Zoom, Pan, and Reset Interactions**
   - Multidimensional scatter plot with `dragmode='zoom'`, `hovermode='closest'`, height 600, box/lasso select, pan, and double-click reset.

5. **`date_range_slider_explanation.md`**:
   - Comprehensive answer and code example for Task 5 explaining `rangeselector` buttons, `rangeslider` drag-to-select, and comparative trade-offs.

---

## Generator Script

All HTML charts can be re-built using the python script:
```bash
python scripts/generate_plotly_charts.py
```
