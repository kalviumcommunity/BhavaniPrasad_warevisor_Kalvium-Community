import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure page layout
st.set_page_config(
    page_title="WareVisor - Manager Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Manager Dashboard matching design system
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }
    .badge-banner {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 8px;
    }
    .wh-card {
        background-color: #f8fafc;
        border: 1px solid #f1f5f9;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation (Role 1: Manager)
st.sidebar.markdown("### 📦 WareVisor")
st.sidebar.caption("RetailStock Manager Portal")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📦 All Products",
        "➕ Add Product",
        "🚚 Stock Movements",
        "📈 Reports",
        "🔔 Alerts",
        "👥 Users",
        "⚙️ Settings"
    ]
)

st.sidebar.divider()
st.sidebar.info("Logged in as: **Manager** (Central Admin)")

if page == "📊 Dashboard":
    # Role Banner and Page Title
    st.markdown('<span class="badge-banner">ROLE 1: MANAGER</span>', unsafe_allow_html=True)
    st.title("1. Manager Dashboard (Summary)")
    st.caption("Real-time view of inventory across all warehouses")

    st.markdown("---")

    # 4 KPI Cards Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Products", value="1,248", delta="+4.2% MoM", help="All Warehouses")
    with col2:
        st.metric(label="Total Stock", value="45,780", delta="+12.5% MoM", help="All Warehouses")
    with col3:
        st.metric(label="Low Stock Products", value="86", delta="Reorder Soon", delta_color="inverse", help="Items needing reorder")
    with col4:
        st.metric(label="Out of Stock", value="12", delta="Action Required", delta_color="inverse", help="Critical alert")

    st.write("")

    # 2 Charts Grid
    chart_col1, chart_col2 = st.columns([2, 1.2])

    with chart_col1:
        st.subheader("Stock Overview")
        period = st.selectbox("Select Filter", ["This Year", "This Quarter", "This Month"], key="period_sel_st")
        
        # Stock overview line chart data
        if period == "This Year":
            df_trend = pd.DataFrame({
                "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
                "Stock": [28000, 32000, 29000, 37000, 34000, 41000, 43500, 45780]
            })
        elif period == "This Quarter":
            df_trend = pd.DataFrame({
                "Month": ["May", "Jun", "Jul", "Aug"],
                "Stock": [34000, 41000, 43500, 45780]
            })
        else:
            df_trend = pd.DataFrame({
                "Month": ["Week 1", "Week 2", "Week 3", "Week 4"],
                "Stock": [42000, 43200, 44800, 45780]
            })

        fig_line = px.line(
            df_trend, x="Month", y="Stock", markers=True,
            line_shape="spline", title=f"Stock Trend ({period})"
        )
        fig_line.update_traces(line_color="#3b82f6", line_width=3, fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)')
        fig_line.update_layout(template="plotly_white", height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_line, use_container_width=True)

    with chart_col2:
        st.subheader("Stock by Category")
        df_cat = pd.DataFrame({
            "Category": ["Electronics", "Clothing", "Home & Kitchen", "Beauty", "Others"],
            "Percentage": [41, 25, 18, 10, 6]
        })
        fig_donut = px.pie(
            df_cat, names="Category", values="Percentage", hole=0.6,
            color_discrete_sequence=["#3b82f6", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6"]
        )
        fig_donut.update_layout(template="plotly_white", height=320, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # Bottom Grid: Top Warehouses & Recent Movements
    bot_col1, bot_col2 = st.columns(2)

    with bot_col1:
        st.subheader("Top Warehouses by Stock")
        wh_data = [
            {"Name": "1. Central Warehouse", "Location": "New Delhi", "Manager": "Amit Sen", "Stock": "18,500 units", "Cap": "85%"},
            {"Name": "2. North Zone Warehouse", "Location": "Delhi", "Manager": "Simran Kaur", "Stock": "12,300 units", "Cap": "65%"},
            {"Name": "3. South Zone Warehouse", "Location": "Bangalore", "Manager": "Suresh Babu", "Stock": "8,850 units", "Cap": "45%"}
        ]
        for wh in wh_data:
            st.markdown(f"""
            <div class="wh-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 15px; color: #0f172a;">{wh['Name']}</strong><br>
                        <span style="font-size: 12px; color: #64748b;">{wh['Location']} • Manager: {wh['Manager']}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 16px; font-weight: 700; color: #2563eb;">{wh['Stock']}</span><br>
                        <span style="font-size: 11px; color: #94a3b8;">Cap: {wh['Cap']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with bot_col2:
        st.subheader("Recent Stock Movements")
        movements = [
            {"Title": "Wireless Mouse (WM-101)", "Meta": "Inbound to Central Warehouse • 15 Jul 2026", "Qty": "+150 units", "Color": "#10b981"},
            {"Title": "Workstation Chair (WC-502)", "Meta": "Outbound from South Warehouse • 15 Jul 2026", "Qty": "-45 units", "Color": "#ea580c"},
            {"Title": "T-Shirt (Blue - Size L)", "Meta": "Inbound to North Warehouse • 14 Jul 2026", "Qty": "+300 units", "Color": "#10b981"}
        ]
        for mv in movements:
            st.markdown(f"""
            <div class="wh-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 14px; color: #0f172a;">{mv['Title']}</strong><br>
                        <span style="font-size: 12px; color: #64748b;">{mv['Meta']}</span>
                    </div>
                    <div>
                        <span style="font-size: 15px; font-weight: 700; color: {mv['Color']};">{mv['Qty']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.title(f"WareVisor - {page}")
    st.info(f"The Manager Dashboard page is ready! Switch back to '📊 Dashboard' to view the complete Manager Dashboard.")
