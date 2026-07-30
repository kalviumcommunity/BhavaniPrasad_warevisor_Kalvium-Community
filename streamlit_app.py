import os
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Configure Streamlit page layout
st.set_page_config(
    page_title="Interactive Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium look
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "database/data_layer.db"

@st.cache_data
def load_data():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        df_orders = pd.read_sql("SELECT * FROM orders", conn)
        df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
        
        df_details = pd.read_sql("""
            SELECT o.order_id, o.order_date, o.order_amount, o.customer_id, o.order_status,
                   p.product_name, p.category, oi.quantity, oi.unit_price,
                   (oi.quantity * oi.unit_price) as item_total
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
        """, conn)
        df_details['order_date'] = pd.to_datetime(df_details['order_date'])
        conn.close()
        return df_orders, df_details
    else:
        # Fallback dummy data if DB file not present
        dates = pd.date_range(start="2026-01-01", periods=200, freq="D")
        amounts = [150.0 + (i % 10)*45.0 for i in range(200)]
        df_orders = pd.DataFrame({
            "order_id": list(range(1, 201)),
            "customer_id": [(i % 50) + 100 for i in range(200)],
            "order_date": dates,
            "order_amount": amounts,
            "order_status": ["Completed" if i % 4 != 0 else "Pending" for i in range(200)]
        })
        df_details = df_orders.copy()
        df_details['product_name'] = ["Product " + chr(65 + (i % 5)) for i in range(200)]
        df_details['category'] = ["Electronics" if i % 2 == 0 else "Software" for i in range(200)]
        df_details['quantity'] = [(i % 3) + 1 for i in range(200)]
        df_details['unit_price'] = df_details['order_amount'] / df_details['quantity']
        df_details['item_total'] = df_details['order_amount']
        return df_orders, df_details

df_orders, df_details = load_data()

st.title("📊 Interactive Sales Analytics Dashboard")
st.markdown("Explore order trends, revenue metrics, and product performance using interactive Plotly visualisations.")

# Sidebar Controls & Filters
st.sidebar.header("Filter Controls")

# Date range filter
min_date_val = df_orders['order_date'].min().date()
max_date_val = df_orders['order_date'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=[min_date_val, max_date_val],
    min_value=min_date_val,
    max_value=max_date_val
)

# Minimum order amount filter
max_amount = float(df_orders['order_amount'].max())
min_amount = st.sidebar.slider(
    "Minimum Order Amount ($)",
    min_value=0.0,
    max_value=max_amount,
    value=0.0,
    step=50.0
)

# Status filter
status_options = ["All"] + sorted(df_orders['order_status'].dropna().unique().tolist())
selected_status = st.sidebar.selectbox("Order Status", status_options)

# Filter Dataframe
filtered_orders = df_orders[
    (df_orders['order_date'].dt.date >= start_date) &
    (df_orders['order_date'].dt.date <= end_date) &
    (df_orders['order_amount'] >= min_amount)
]

if selected_status != "All":
    filtered_orders = filtered_orders[filtered_orders['order_status'] == selected_status]

# Top KPI Summary Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_revenue = filtered_orders['order_amount'].sum()
total_orders = len(filtered_orders)
avg_order_val = filtered_orders['order_amount'].mean() if total_orders > 0 else 0
unique_cust = filtered_orders['customer_id'].nunique()

kpi1.metric("Total Revenue", f"${total_revenue:,.2f}")
kpi2.metric("Total Orders", f"{total_orders:,}")
kpi3.metric("Avg Order Value", f"${avg_order_val:,.2f}")
kpi4.metric("Unique Customers", f"{unique_cust:,}")

st.markdown("---")

# Main Interactive Plotly Section
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📈 Orders & Revenue Over Time")
    
    daily_df = filtered_orders.groupby(filtered_orders['order_date'].dt.date).agg(
        revenue=('order_amount', 'sum'),
        order_count=('order_id', 'count')
    ).reset_index()
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=daily_df['order_date'],
        y=daily_df['revenue'],
        mode='lines+markers',
        name='Revenue ($)',
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>',
        line=dict(color='#1f77b4', width=2.5),
        marker=dict(size=7)
    ))
    
    fig_line.update_layout(
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        height=450,
        template='plotly_white',
        margin=dict(l=40, r=20, t=30, b=40)
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.subheader("📊 Metric Switcher View")
    
    filtered_details = df_details[df_details['order_id'].isin(filtered_orders['order_id'])]
    prod_summary = filtered_details.groupby('product_name').agg(
        revenue=('item_total', 'sum'),
        orders=('order_id', 'nunique'),
        quantity=('quantity', 'sum')
    ).reset_index().sort_values(by='revenue', ascending=False).head(6)
    
    metric_choice = st.radio("Select View Metric:", ["Revenue ($)", "Order Count", "Units Sold"], horizontal=True)
    
    if metric_choice == "Revenue ($)":
        y_val = prod_summary['revenue']
        fmt = "$%{y:,.2f}"
        color = '#1f77b4'
    elif metric_choice == "Order Count":
        y_val = prod_summary['orders']
        fmt = "%{y:,} orders"
        color = '#ff7f0e'
    else:
        y_val = prod_summary['quantity']
        fmt = "%{y:,} units"
        color = '#2ca02c'
        
    fig_bar = go.Figure(data=go.Bar(
        x=prod_summary['product_name'],
        y=y_val,
        marker_color=color,
        hovertemplate='<b>%{x}</b><br>' + fmt + '<extra></extra>'
    ))
    fig_bar.update_layout(
        xaxis_title="Product",
        yaxis_title=metric_choice,
        height=400,
        template='plotly_white',
        margin=dict(l=40, r=20, t=30, b=100),
        xaxis=dict(tickangle=-30)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Filtered Data Table Section
st.subheader("📄 Order Transactions Data Table")
st.write(f"Showing {len(filtered_orders)} orders matching criteria (>= ${min_amount:,.2f})")
st.dataframe(
    filtered_orders[['order_id', 'order_date', 'customer_id', 'order_amount', 'order_status']],
    use_container_width=True
)
