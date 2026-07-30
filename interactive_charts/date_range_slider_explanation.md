# Task 5: Date Range Selection in Plotly Time-Series Charts

## Question
> You have a time-series Plotly chart showing revenue by week. You want to add a date range slider so users can select which weeks to view (e.g., "show me only Q1 2024"). How would you implement this in Plotly?

---

## Implementation Approach

To enable intuitive date filtering on time-series charts, Plotly provides two native x-axis interactive components:

1. **Date Range Selector Buttons (`rangeselector`)**: Quick preset buttons at the top of the chart that allow users to jump to predefined time windows (e.g., 1 Month, 3 Months, 6 Months, YTD, or All).
2. **Date Range Slider (`rangeslider`)**: A drag-and-drop mini slider rendered beneath the x-axis that allows users to select custom start and end dates visually.

---

## Code Example

```python
import plotly.graph_objects as go
import pandas as pd

# Sample weekly revenue dataset
df = pd.DataFrame({
    'week': pd.date_range(start='2024-01-01', periods=52, freq='W'),
    'revenue': [15000 + (i % 7) * 2000 + i * 300 for i in range(52)]
})

# Create weekly revenue time-series figure
fig = go.Figure(data=go.Scatter(
    x=df['week'],
    y=df['revenue'],
    mode='lines+markers',
    name='Weekly Revenue',
    hovertemplate='<b>Week of %{x|%Y-%m-%d}</b><br>Revenue: $%{y:,.2f}<extra></extra>',
    line=dict(color='#1f77b4', width=2.5),
    marker=dict(size=6)
))

# Enable range selector buttons AND drag-to-select range slider on x-axis
fig.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=1, label='1M', step='month', stepmode='backward'),
            dict(count=3, label='3M (Qtr)', step='month', stepmode='backward'),
            dict(count=6, label='6M', step='month', stepmode='backward'),
            dict(count=1, label='YTD', step='year', stepmode='todate'),
            dict(step='all', label='All')
        ]),
        bgcolor='#f4f4f9',
        activecolor='#1f77b4'
    ),
    rangeslider=dict(visible=True),
    type='date'
)

fig.update_layout(
    title='Weekly Revenue Trend with Date Range Controls',
    xaxis_title='Week',
    yaxis_title='Revenue ($)',
    hovermode='x unified',
    height=550,
    template='plotly_white'
)

# Export as standalone HTML
fig.write_html('weekly_revenue_range_slider.html')
```

---

## When Each Approach is Better

| Approach | Ideal Use Case | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **`rangeselector` Buttons** | Standard reporting & periodic reviews (e.g. Q1, YTD, 1M). | - 1-click instant navigation<br>- Consistent financial boundaries<br>- Clean UI | - Fixed predefined intervals<br>- Less flexible for arbitrary date ranges |
| **`rangeslider`** | Visual exploration & anomaly investigation across long time-series. | - Intuitive click-and-drag interface<br>- Full visibility of overall shape<br>- Arbitrary start/end selection | - Consumes additional vertical chart height<br>- Can feel cluttered on small screens |
| **Streamlit / Dashboard Filters (`st.date_input`)** | Multi-chart synchronized dashboards. | - Filters entire dashboard simultaneously<br>- Reduces client-side memory footprint | - Requires server/app re-render cycle |

---

## Summary Recommendation

For standalone interactive charts, **combining `rangeselector` buttons with a `rangeslider`** offers the best user experience. Executive stakeholders get quick single-click quarterly access, while data analysts enjoy granular drag-to-select capabilities.
