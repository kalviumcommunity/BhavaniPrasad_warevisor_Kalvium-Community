import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import numpy as np
from datetime import datetime, timedelta
from export_utils import export_analysis

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

st.set_page_config(layout='wide', page_title='Business Performance Dashboard')
st.title('Business Performance Dashboard')

# --- DATA INTEGRATION ---
# Level 2 (Trends) Data
months = pd.date_range('2024-01-01', periods=12, freq='ME')
trend_df = pd.DataFrame({
    'date': months,
    'revenue': [4.2, 4.5, 4.8, 4.6, 5.0, 5.1, 4.9, 4.7, 5.2, 5.4, 5.5, 5.2],
    'active_customers': [2100, 2150, 2200, 2250, 2300, 2320, 2380, 2410, 2450, 2480, 2490, 2500],
    'churned_customers': [50, 45, 60, 55, 40, 42, 38, 35, 30, 25, 28, 20],
    'aov': [130, 132, 135, 134, 138, 140, 142, 141, 143, 144, 145, 145]
})

# Level 3 (Segments) Data
segment_df = pd.DataFrame({
    'segment': ['Enterprise', 'Mid-Market', 'SMB', 'Starter'],
    'revenue': [2.1, 1.5, 1.0, 0.6],
    'profit': [0.8, 0.5, 0.2, -0.1],
    'customer_count': [150, 450, 1100, 800],
    'color': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
})

# --- LEVEL 1: KPI Summary Cards ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label='Revenue', value='$5.2M', delta='+12.5%')
with col2:
    st.metric(label='Active Customers', value='2,500', delta='+5.2%')
with col3:
    st.metric(label='Avg Order Value', value='$145', delta='+3.1%')
with col4:
    st.metric(label='Churn Rate', value='4.8%', delta='-1.2%', delta_color='inverse')
with col5:
    st.metric(label='NPS Score', value='72', delta='+4')

st.divider()

# --- LEVEL 2: Trends ---
st.subheader("Performance Trends")
col_trend1, col_trend2, col_trend3 = st.columns(3)

# Chart 1: Revenue Trend (Plotly Line Chart)
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=trend_df['date'],
    y=trend_df['revenue'],
    mode='lines+markers',
    name='Revenue',
    line=dict(color='#1f77b4', width=2),
    marker=dict(size=8),
    hovertemplate='<b>%{x|%b %Y}</b><br>' +
                  'Revenue: $%{y:.2f}M<br>' +
                  '<extra></extra>'
))
fig1.add_hline(y=5.0, line_dash="dash", line_color="#2ca02c", annotation_text="Target: $5M")
fig1.update_layout(
    title='Monthly Revenue Trend (2024)',
    xaxis_title='Month',
    yaxis_title='Revenue ($M)',
    hovermode='x unified',
    dragmode='zoom',
    height=400,
    margin=dict(l=0, r=0, t=40, b=0)
)
with col_trend1:
    st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Customer Metrics (Dual Line Chart)
fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(go.Scatter(
    x=trend_df['date'], y=trend_df['active_customers'],
    mode='lines+markers', name='Active Customers',
    line=dict(color='#1f77b4', width=2), marker=dict(symbol='square', size=8),
    hovertemplate='<b>%{x|%b %Y}</b><br>Active: %{y:,}<extra></extra>'
), secondary_y=False)

fig2.add_trace(go.Scatter(
    x=trend_df['date'], y=trend_df['churned_customers'],
    mode='lines+markers', name='Churned Customers',
    line=dict(color='#d62728', width=2), marker=dict(symbol='x', size=8),
    hovertemplate='<b>%{x|%b %Y}</b><br>Churned: %{y:,}<extra></extra>'
), secondary_y=True)

fig2.add_hline(y=40, line_dash="dot", line_color="#ff7f0e", annotation_text="Alert Limit", secondary_y=True)
fig2.update_layout(
    title='Customer Growth vs Churn',
    xaxis_title='Month',
    hovermode='x unified',
    dragmode='zoom',
    height=400,
    margin=dict(l=0, r=0, t=40, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig2.update_yaxes(title_text="Active Customers", color='#1f77b4', secondary_y=False)
fig2.update_yaxes(title_text="Churned Customers", color='#d62728', secondary_y=True)
with col_trend2:
    st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Avg Order Value Trend
fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=trend_df['date'],
    y=trend_df['aov'],
    mode='lines+markers',
    name='AOV',
    line=dict(color='#ff7f0e', width=2),
    marker=dict(symbol='triangle-up', size=10),
    hovertemplate='<b>%{x|%b %Y}</b><br>' +
                  'AOV: $%{y:.2f}<br>' +
                  '<extra></extra>'
))
fig3.add_hline(y=140, line_dash="dash", line_color="#2ca02c", annotation_text="Target: $140")
fig3.update_layout(
    title='Average Order Value (AOV)',
    xaxis_title='Month',
    yaxis_title='AOV ($)',
    hovermode='x unified',
    dragmode='zoom',
    height=400,
    margin=dict(l=0, r=0, t=40, b=0)
)
with col_trend3:
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --- LEVEL 3: Segments ---
st.subheader("Segment Analysis")

# Dynamic Dropdown Chart for Segments
fig4 = go.Figure()

# Add Traces
fig4.add_trace(go.Bar(
    x=segment_df['segment'], y=segment_df['revenue'], name='Revenue ($M)',
    marker_color=segment_df['color'], visible=True,
    text=segment_df['revenue'].apply(lambda x: f"${x}M"), textposition='auto',
    hovertemplate='<b>%{x}</b><br>Revenue: $%{y}M<extra></extra>'
))
fig4.add_trace(go.Bar(
    x=segment_df['segment'], y=segment_df['profit'], name='Profit ($M)',
    marker_color=segment_df['color'], visible=False,
    text=segment_df['profit'].apply(lambda x: f"${x}M"), textposition='auto',
    hovertemplate='<b>%{x}</b><br>Profit: $%{y}M<extra></extra>'
))
fig4.add_trace(go.Bar(
    x=segment_df['segment'], y=segment_df['customer_count'], name='Customer Count',
    marker_color=segment_df['color'], visible=False,
    text=segment_df['customer_count'].apply(lambda x: f"{x:,}"), textposition='auto',
    hovertemplate='<b>%{x}</b><br>Customers: %{y:,}<extra></extra>'
))

# Create dropdown menu
fig4.update_layout(
    updatemenus=[dict(
        active=0,
        x=0.0,
        xanchor='left',
        y=1.15,
        yanchor='top',
        buttons=[
            dict(label='Revenue', method='update',
                 args=[{'visible': [True, False, False]},
                       {'title': 'Revenue by Segment', 'yaxis.title.text': 'Revenue ($M)'}]),
            dict(label='Profit', method='update',
                 args=[{'visible': [False, True, False]},
                       {'title': 'Profit by Segment', 'yaxis.title.text': 'Profit ($M)'}]),
            dict(label='Customer Count', method='update',
                 args=[{'visible': [False, False, True]},
                       {'title': 'Customer Count by Segment', 'yaxis.title.text': 'Number of Customers'}])
        ]
    )],
    title='Segment Performance',
    xaxis_title='Segment',
    yaxis_title='Revenue ($M)',
    dragmode='zoom',
    height=500
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

# --- LEVEL 4: Progressive Disclosure (Detail) ---
st.subheader('Detailed Data Explorer')

# Mock DataFrame for detail view
np.random.seed(42)
num_records = 500
mock_data = {
    'customer_id': [f'CUST-{i:04d}' for i in range(1, num_records + 1)],
    'segment': np.random.choice(segment_df['segment'], num_records, p=[0.06, 0.18, 0.44, 0.32]),
    'revenue': np.random.uniform(500, 15000, num_records).round(2),
    'last_activity': [datetime.today().date() - timedelta(days=int(d)) for d in np.random.randint(0, 60, num_records)],
    'churn_risk': np.random.choice(['Low', 'Medium', 'High'], num_records, p=[0.7, 0.2, 0.1])
}
df = pd.DataFrame(mock_data)

# Sidebar filters for drill-down
st.sidebar.header('Filters')
selected_segment = st.sidebar.selectbox('Customer Segment', ['All'] + list(segment_df['segment']))

# Date range default: last 30 days
start_date = df['last_activity'].min()
end_date = df['last_activity'].max()
date_range = st.sidebar.date_input('Date Range', value=(start_date, end_date))

# Apply filters
filtered_df = df.copy()

if selected_segment != 'All':
    filtered_df = filtered_df[filtered_df['segment'] == selected_segment]

if len(date_range) == 2:
    d_start, d_end = date_range
    filtered_df = filtered_df[(filtered_df['last_activity'] >= d_start) & (filtered_df['last_activity'] <= d_end)]

# Display filtered data
st.write(f'Showing {len(filtered_df):,} records')
st.dataframe(filtered_df[['customer_id', 'segment', 'revenue', 'last_activity', 'churn_risk']], use_container_width=True)

# Export option
st.sidebar.header('Export')

if st.sidebar.button('📥 Export Analysis'):
    summary = "## Analysis Report\nKey findings..."
    charts = {'Revenue Trend': fig, 'Churn Drivers': fig3, 'Segment Performance': fig4}
    
    # Export
    report_dir = export_analysis(filtered_df, summary, charts, 'output')
    
    # Provide download links
    st.sidebar.success(f'✓ Analysis exported to: {report_dir}')
    
    # CSV download
    csv_bytes = filtered_df.to_csv(index=False).encode()
    st.sidebar.download_button(
        label='📊 Download Data (CSV)',
        data=csv_bytes,
        file_name='analysis_data.csv',
        mime='text/csv'
    )
    
    # HTML download
    with open(f'{report_dir}/interactive_report.html', 'r', encoding='utf-8') as f:
        html_bytes = f.read()
    st.sidebar.download_button(
        label='🌐 Download Report (HTML)',
        data=html_bytes,
        file_name='analysis_report.html',
        mime='text/html'
    )
    
    # PDF download
    try:
        with open(f'{report_dir}/summary_report.pdf', 'rb') as f:
            pdf_bytes = f.read()
        st.sidebar.download_button(
            label='📄 Download Report (PDF)',
            data=pdf_bytes,
            file_name='summary_report.pdf',
            mime='application/pdf'
        )
    except FileNotFoundError:
        pass

