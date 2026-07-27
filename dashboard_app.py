import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime, timedelta

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

st.set_page_config(layout='wide', page_title='Business Performance Dashboard')
st.title('Business Performance Dashboard')

# Level 1: KPI Summary Cards
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

# Level 2: Trends
st.subheader("Performance Trends")
col_trend1, col_trend2, col_trend3 = st.columns(3)

# Chart 1: Revenue Trend (Line Chart)
months = pd.date_range('2024-01-01', periods=12, freq='ME')
revenue = [4.2, 4.5, 4.8, 4.6, 5.0, 5.1, 4.9, 4.7, 5.2, 5.4, 5.5, 5.2]

fig1, ax1 = plt.subplots(figsize=(8, 4))
ax1.plot(months, revenue, marker='o', linewidth=2, color='#1f77b4')
ax1.set_title('Monthly Revenue Trend (2024)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Month', fontsize=10)
ax1.set_ylabel('Revenue ($M)', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.axhline(y=5.0, color='#2ca02c', linestyle='--', linewidth=1.5, label='Target: $5M')
ax1.legend()
plt.tight_layout()
plt.savefig('output/revenue_trend.png', dpi=300)

with col_trend1:
    st.pyplot(fig1)

# Chart 2: Customer Metrics (Dual Line Chart)
active_customers = [2100, 2150, 2200, 2250, 2300, 2320, 2380, 2410, 2450, 2480, 2490, 2500]
churned_customers = [50, 45, 60, 55, 40, 42, 38, 35, 30, 25, 28, 20]

fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.plot(months, active_customers, marker='s', linewidth=2, color='#1f77b4', label='Active Customers')
ax2.set_title('Customer Growth vs Churn', fontsize=12, fontweight='bold')
ax2.set_xlabel('Month', fontsize=10)
ax2.set_ylabel('Active Customers', color='#1f77b4', fontsize=10)
ax2.tick_params(axis='y', labelcolor='#1f77b4')
ax2.grid(True, alpha=0.3)

ax2_twin = ax2.twinx()
ax2_twin.plot(months, churned_customers, marker='x', linewidth=2, color='#d62728', label='Churned Customers')
ax2_twin.set_ylabel('Churned Customers', color='#d62728', fontsize=10)
ax2_twin.tick_params(axis='y', labelcolor='#d62728')

# Reference line for acceptable churn limit
ax2_twin.axhline(y=40, color='#ff7f0e', linestyle=':', linewidth=1.5, label='Churn Alert Limit')
ax2_twin.legend(loc='upper right')

plt.tight_layout()
plt.savefig('output/customer_metrics.png', dpi=300)

with col_trend2:
    st.pyplot(fig2)

# Chart 3: Avg Order Value Trend
aov = [130, 132, 135, 134, 138, 140, 142, 141, 143, 144, 145, 145]
fig3, ax3 = plt.subplots(figsize=(8, 4))
ax3.plot(months, aov, marker='^', linewidth=2, color='#ff7f0e')
ax3.set_title('Average Order Value (AOV)', fontsize=12, fontweight='bold')
ax3.set_xlabel('Month', fontsize=10)
ax3.set_ylabel('AOV ($)', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.axhline(y=140, color='#2ca02c', linestyle='--', linewidth=1.5, label='AOV Target: $140')
ax3.legend()
plt.tight_layout()
plt.savefig('output/aov_trend.png', dpi=300)

with col_trend3:
    st.pyplot(fig3)

st.divider()

# Level 3: Segments
st.subheader("Segment Analysis")
col_seg1, col_seg2 = st.columns(2)

# Chart: Revenue by Segment (Bar Chart)
segments = ['Enterprise', 'Mid-Market', 'SMB', 'Starter']
segment_revenue = [2.1, 1.5, 1.0, 0.6]
segment_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

fig4, ax4 = plt.subplots(figsize=(8, 4))
bars = ax4.barh(segments, segment_revenue, color=segment_colors)
ax4.set_xlabel('Revenue ($M)', fontsize=10)
ax4.set_title('Revenue by Customer Segment', fontsize=12, fontweight='bold')

for bar, val in zip(bars, segment_revenue):
    ax4.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f'${val}M', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('output/revenue_by_segment.png', dpi=300)

with col_seg1:
    st.pyplot(fig4)

# Chart: Customer Count by Segment
segment_customers = [150, 450, 1100, 800]
fig5, ax5 = plt.subplots(figsize=(8, 4))
bars2 = ax5.barh(segments, segment_customers, color=segment_colors)
ax5.set_xlabel('Number of Customers', fontsize=10)
ax5.set_title('Customer Base by Segment', fontsize=12, fontweight='bold')

for bar, val in zip(bars2, segment_customers):
    ax5.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
            f'{val}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('output/customers_by_segment.png', dpi=300)

with col_seg2:
    st.pyplot(fig5)

st.divider()

# Level 4: Progressive Disclosure (Detail)
st.subheader('Detailed Data Explorer')

# Mock DataFrame for detail view
np.random.seed(42)
num_records = 500
mock_data = {
    'customer_id': [f'CUST-{i:04d}' for i in range(1, num_records + 1)],
    'segment': np.random.choice(segments, num_records, p=[0.06, 0.18, 0.44, 0.32]),
    'revenue': np.random.uniform(500, 15000, num_records).round(2),
    'last_activity': [datetime.today().date() - timedelta(days=int(d)) for d in np.random.randint(0, 60, num_records)],
    'churn_risk': np.random.choice(['Low', 'Medium', 'High'], num_records, p=[0.7, 0.2, 0.1])
}
df = pd.DataFrame(mock_data)

# Sidebar filters for drill-down
st.sidebar.header('Filters')
selected_segment = st.sidebar.selectbox('Customer Segment', ['All'] + segments)

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
csv = filtered_df.to_csv(index=False)
st.download_button(
    label='Download CSV',
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv'
)
