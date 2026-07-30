import os
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="Executive KPI & Performance Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive KPI styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "database/data_layer.db"

def get_trend_indicator(change_pct, metric_name):
    """
    Return arrow and color based on metric direction.
    Up is good for: Revenue, Active Users, AOV, Customer Satisfaction.
    Down is good for: Churn Rate.
    """
    if metric_name == 'Churn Rate':
        if change_pct < -2:
            return '↓', '#10b981'  # Green (Decrease in churn is good)
        elif change_pct > 2:
            return '↑', '#ef4444'  # Red (Increase in churn is bad)
        else:
            return '→', '#f59e0b'  # Yellow (Flat)
    else:
        if change_pct > 2:
            return '↑', '#10b981'  # Green
        elif change_pct < -2:
            return '↓', '#ef4444'  # Red
        else:
            return '→', '#f59e0b'  # Yellow

@st.cache_data
def load_kpi_data():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        df_monthly = pd.read_sql("SELECT * FROM vw_monthly_kpis ORDER BY month DESC", conn)
        df_orders = pd.read_sql("SELECT * FROM orders", conn)
        conn.close()
        return df_monthly, df_orders
    else:
        # Fallback dataset if DB is not present
        df_monthly = pd.DataFrame([
            {"month": "2026-07", "total_revenue": 504750.04, "active_users": 41, "avg_order_value": 3912.79, "churn_rate": 9.52, "satisfaction_score": 4.4},
            {"month": "2026-06", "total_revenue": 530104.78, "active_users": 42, "avg_order_value": 4240.84, "churn_rate": 13.33, "satisfaction_score": 4.2}
        ])
        df_orders = pd.DataFrame()
        return df_monthly, df_orders

df_monthly, df_orders = load_kpi_data()

# Process Current vs Prior Period Metrics
if len(df_monthly) >= 2:
    current_row = df_monthly.iloc[0]
    prior_row = df_monthly.iloc[1]
else:
    current_row = df_monthly.iloc[0]
    prior_row = current_row

def calc_change(curr, prior):
    if prior == 0 or pd.isna(prior):
        return 0.0
    return ((curr - prior) / prior) * 100.0

rev_change = calc_change(current_row['total_revenue'], prior_row['total_revenue'])
users_change = calc_change(current_row['active_users'], prior_row['active_users'])
aov_change = calc_change(current_row['avg_order_value'], prior_row['avg_order_value'])
churn_change = calc_change(current_row['churn_rate'], prior_row['churn_rate'])
sat_change = calc_change(current_row['satisfaction_score'], prior_row['satisfaction_score'])

# Build KPI summary dataframe
kpis_df = pd.DataFrame({
    'Metric': ['Revenue', 'Active Users', 'AOV', 'Churn Rate', 'Satisfaction'],
    'Current': [current_row['total_revenue'], current_row['active_users'], current_row['avg_order_value'], current_row['churn_rate'], current_row['satisfaction_score']],
    'Prior': [prior_row['total_revenue'], prior_row['active_users'], prior_row['avg_order_value'], prior_row['churn_rate'], prior_row['satisfaction_score']],
    'Change_Pct': [rev_change, users_change, aov_change, churn_change, sat_change]
})

kpis_df['Trend_Tuple'] = kpis_df.apply(
    lambda r: get_trend_indicator(r['Change_Pct'], r['Metric']), axis=1
)
kpis_df['Arrow'] = kpis_df['Trend_Tuple'].apply(lambda x: x[0])
kpis_df['Color'] = kpis_df['Trend_Tuple'].apply(lambda x: x[1])
kpis_df['Change_Display'] = kpis_df['Change_Pct'].apply(lambda x: f"{x:+.1f}%" if x != 0 else "0%")

# Streamlit UI
st.title("🎯 Executive Sales & Performance KPI Dashboard")
st.caption(f"Comparing current period ({current_row['month']}) against prior period ({prior_row['month']})")

st.markdown("### Key Performance Indicators")

# Display 5 KPI Cards in 1 Row
col1, col2, col3, col4, col5 = st.columns(5)

kpi_list = [
    {
        'name': 'Revenue',
        'current': f"${current_row['total_revenue']:,.2f}",
        'change': f"{rev_change:+.1f}%",
        'delta_color': 'normal'
    },
    {
        'name': 'Active Users',
        'current': f"{int(current_row['active_users']):,}",
        'change': f"{users_change:+.1f}%",
        'delta_color': 'normal'
    },
    {
        'name': 'AOV',
        'current': f"${current_row['avg_order_value']:,.2f}",
        'change': f"{aov_change:+.1f}%",
        'delta_color': 'normal'
    },
    {
        'name': 'Churn Rate',
        'current': f"{current_row['churn_rate']:.2f}%",
        'change': f"{churn_change:+.1f}%",
        'delta_color': 'inverse'  # Negative is green for churn rate
    },
    {
        'name': 'Satisfaction',
        'current': f"{current_row['satisfaction_score']:.1f}/5.0",
        'change': f"{sat_change:+.1f}%",
        'delta_color': 'normal'
    }
]

cols = [col1, col2, col3, col4, col5]

for col, kpi in zip(cols, kpi_list):
    with col:
        st.metric(
            label=kpi['name'],
            value=kpi['current'],
            delta=kpi['change'],
            delta_color=kpi['delta_color']
        )

st.divider()

# Detailed Analytics Section Below KPI Cards
st.subheader("📊 Detailed Metric Analytics & Data Lineage")

tab1, tab2 = st.tabs(["Monthly Trend Comparison", "KPI Summary Table"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_monthly['month'],
        y=df_monthly['total_revenue'],
        mode='lines+markers',
        name='Revenue ($)',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        title="Monthly Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Total Revenue ($)",
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("#### Computed KPI DataFrame")
    st.dataframe(
        kpis_df[['Metric', 'Current', 'Prior', 'Change_Display', 'Arrow', 'Color']],
        use_container_width=True
    )
