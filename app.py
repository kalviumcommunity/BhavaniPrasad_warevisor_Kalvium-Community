import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path

from scripts.db_connect import get_engine, authenticate_user, test_connection

# Configure Streamlit page layout
st.set_page_config(
    page_title="WareVisor - Warehouse & Retail Portal",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphism / Modern Styling for Manager & Product Sender Portal
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
    .badge-manager {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 12px;
    }
    .badge-sender {
        background: linear-gradient(90deg, #065f46, #10b981);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 12px;
    }
    .wh-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load data from PostgreSQL or local CSV fallback
@st.cache_data(ttl=60)
def load_sales_data():
    try:
        engine = get_engine()
        query = "SELECT record_id, year, month, supplier, item_code, item_description, item_type, retail_sales, retail_transfers, warehouse_sales FROM warehouse_retail_sales LIMIT 50000;"
        df = pd.read_sql(query, engine)
        if not df.empty:
            return df, "PostgreSQL Database (Supabase)"
    except Exception as e:
        pass

    # Fallback to cleaned CSV if database connection is offline
    csv_path = Path("data/processed/warehouse_retail_sales_cleaned.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path, nrows=50000)
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
        return df, "Local Cleaned CSV Dataset"

    return pd.DataFrame(), "No Data"

# Session State Initialization for Role-Based Login
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# Sidebar Authentication Section
st.sidebar.markdown("### 📦 WareVisor")
st.sidebar.caption("Enterprise Warehouse & Retail Management")
st.sidebar.divider()

if not st.session_state["authenticated"]:
    st.sidebar.subheader("🔑 Role-Based Login")
    login_tab1, login_tab2 = st.sidebar.tabs(["Quick Demo Login", "DB Credential Login"])

    with login_tab1:
        role_choice = st.radio("Select Role", ["Manager (Central Admin)", "Product Sender (Supplier)"])
        if st.button("Log In as Demo Role", use_container_width=True):
            if "Manager" in role_choice:
                st.session_state["authenticated"] = True
                st.session_state["user_role"] = "manager"
                st.session_state["user_name"] = "Central Warehouse Manager"
                st.session_state["username"] = "manager"
            else:
                st.session_state["authenticated"] = True
                st.session_state["user_role"] = "product_sender"
                st.session_state["user_name"] = "Product Dispatch Sender"
                st.session_state["username"] = "sender"
            st.rerun()

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
        period = st.selectbox("Select Filter", ["This Year", "This Quarter", "This Month"], key="period_sel")
        
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

elif page == "Trends":
    # Task 3: Visual Hierarchy - Page Title
    st.title("Trend Analysis")

    # Task 3: Headers, Subheaders, Dividers
    st.header("Revenue Trends")
    st.subheader("Monthly Revenue (Last 12 Months)")

    # Task 2: Columns layout for side-by-side comparison
    trend_col1, trend_col2 = st.columns(2)
    with trend_col1:
        st.subheader("Q1 - Q2 Revenue Performance")
        st.write("Steady upward trajectory driven by new product launches and increased demand.")
        st.metric("H1 Total Revenue", "$2.8M", "+14.2%")
    with trend_col2:
        st.subheader("Q3 - Q4 Projected Growth")
        st.write("Seasonal uptick anticipated with expanding enterprise partnerships.")
        st.metric("H2 Projected Revenue", "$3.1M", "+16.8%")

    st.divider()

    st.header("Customer Metrics")
    st.subheader("Active Customers Over Time")

    cust_col1, cust_col2 = st.columns(2)
    with cust_col1:
        st.metric("Monthly Active Users", "2,150", "+8.4%")
    with cust_col2:
        st.metric("Customer Acquisition Cost", "$120", "-5.1%", delta_color="inverse")

    st.divider()

    # Task 2: Expander for trend details
    with st.expander("Trend Analysis Methodology"):
        st.write(
            "Monthly revenue trends are compiled at the end of each billing cycle. "
            "Growth rates compare current period metrics against prior trailing twelve-month averages. "
            "Projections account for seasonal baseline variance."
        )

elif page == "Data Explorer":
    st.title("Data Explorer")
    st.write("Upload your dataset to explore, clean, and visualize the data automatically.")

    # Task 3: Apply @st.cache_data to Data Loading
    @st.cache_data
    def load_data(file_bytes, file_name):
        import io
        if file_name.endswith(".csv"):
            return pd.read_csv(io.BytesIO(file_bytes))
        elif file_name.endswith(".json"):
            return pd.read_json(io.BytesIO(file_bytes))
        return None

    # Task 1 & Task 4: File Upload and Error Handling
    uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "json"])

    if uploaded_file is not None:
        try:
            df = load_data(uploaded_file.getvalue(), uploaded_file.name)
            if df is None:
                st.error("Unsupported file type.")
                st.stop()

    st.title("📦 WareVisor Portal")
    st.info("Please log in from the sidebar using **Quick Demo Login** or **DB Credential Login**.")
    st.stop()

# Logged-In User Information in Sidebar
role_name = "Manager (Admin)" if st.session_state["user_role"] == "manager" else "Product Sender"
st.sidebar.success(f"Logged in as: **{st.session_state['user_name']}**\n\nRole: **{role_name}**")

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None
    st.rerun()

        # Task 4: Handle Empty Filtered Results
        if len(filtered_df) == 0:
            st.warning("No data matches current filters. Broaden your selection.")
            st.stop()

# Navigation per Role
if st.session_state["user_role"] == "manager":
    nav_options = [
        "📊 Manager Dashboard",
        "📦 All Inventory Items",
        "➕ Add/Update Items",
        "👥 Role & User Management",
        "⚙️ Database Settings"
    ]
else: # product_sender
    nav_options = [
        "🚚 Product Sender Portal",
        "📦 My Dispatched Items",
        "➕ Submit New Shipment Item",
        "⚙️ Settings"
    ]

page = st.sidebar.radio("Navigation", nav_options)

# Load dataset
df_sales, data_source = load_sales_data()
st.sidebar.caption(f"Data Source: **{data_source}**")

# ---------------------------------------------------------
# MANAGER ROLE PAGES
# ---------------------------------------------------------
if st.session_state["user_role"] == "manager":
    if page == "📊 Manager Dashboard":
        st.markdown('<span class="badge-manager">ROLE: MANAGER (CENTRAL ADMIN)</span>', unsafe_allow_html=True)
        st.title("Manager Analytics & Stock Overview")
        st.caption("Real-time oversight of warehouse sales, transfers, and inventory distribution")
        st.divider()

        # Task 5: Avoid Hardcoded Data
        # Dynamic mapping for required fields to avoid hardcoded column errors
        # Fallback to defaults if specific names aren't found
        cust_col = next((c for c in filtered_df.columns if 'customer' in c.lower()), filtered_df.columns[0])
        
        # Display Automatic Preview (wired to filtered_df)
        st.header("Dataset Preview")
        st.write(f"Showing **{len(filtered_df):,}** of **{len(df):,}** records")

        # Task 1: Display Five Reactive KPI Metrics
        total_revenue = filtered_df[num_col].sum() if num_col else 0
        avg_order = filtered_df[num_col].mean() if num_col else 0
        row_count = len(filtered_df)
        unique_customers = filtered_df[cust_col].nunique() if cust_col else 0
        null_pct = (filtered_df.isnull().sum().sum() / (filtered_df.shape[0] * filtered_df.shape[1]) * 100) if not filtered_df.empty else 0

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Revenue", f"${total_revenue:,.0f}")
        with col2:
            st.metric("Avg Order", f"${avg_order:,.0f}")
        with col3:
            st.metric("Records", f"{row_count:,}")
        with col4:
            st.metric("Customers", f"{unique_customers:,}")
        with col5:
            st.metric("Quality", f"{100 - null_pct:.1f}%")

        st.subheader("First 10 Rows")
        st.dataframe(filtered_df.head(10), use_container_width=True)

        st.divider()

        # Task 2: Include Three Chart Types
        st.header("Visualizations")
        
        # Chart 1: Line chart (trend)
        if date_col and num_col:
            st.subheader(f"{num_col.title()} Over Time")
            trend = filtered_df.groupby(date_col)[num_col].sum().reset_index()
            st.line_chart(trend.set_index(date_col))
        else:
            st.info("Date and Numeric columns required for Trend chart.")
            
        # Chart 2: Bar chart (comparison)
        if cat_col and num_col:
            st.subheader(f"{num_col.title()} by {cat_col.title()}")
            seg = filtered_df.groupby(cat_col)[num_col].sum().reset_index()
            st.bar_chart(seg.set_index(cat_col))
        else:
            st.info("Categorical and Numeric columns required for Bar chart.")
            
        # Chart 3: Plotly histogram (distribution)
        if num_col:
            st.subheader(f"{num_col.title()} Distribution")
            import plotly.express as px
            fig = px.histogram(filtered_df, x=num_col, nbins=30)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Numeric column required for Histogram.")

    else:
        st.info("Upload a CSV or JSON file to begin.")

elif page == "Workflow":
    st.title("Multi-Step Analysis Workflow")
    
    # Task 5: Document Session State Usage
    # "selected_segment" - stores the user's segment choice from Step 1
    # so it survives reruns when the user interacts with Step 2 widgets.
    
    # "workflow_step" - tracks which step the user has completed.
    # Prevents Step 2 from displaying before Step 1 is confirmed.
    
    # "analysis_result" - caches the computation from Step 2 so
    # it does not recompute when unrelated widgets are changed.

    # Task 1 & Task 2: Persist Three Values & Safely Initialise
    if "selected_segment" not in st.session_state:
        st.session_state["selected_segment"] = "All"
    if "workflow_step" not in st.session_state:
        st.session_state["workflow_step"] = 1
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None

    # Task 4: Implement Session State Reset
    if st.sidebar.button("Reset Workflow"):
        for key in ["selected_segment", "workflow_step", "analysis_result"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Task 3: Build a Multi-Step Workflow
    # Step 1
    st.header("Step 1: Select Segment")
    segment = st.selectbox("Segment", ["All", "Enterprise", "Mid-Market", "SMB"])
    if st.button("Confirm Segment"):
        st.session_state["selected_segment"] = segment
        st.session_state["workflow_step"] = 2
        st.rerun()

    # Step 2 (only if step 1 complete)
    if st.session_state["workflow_step"] >= 2:
        st.header("Step 2: Analysis")
        chosen = st.session_state["selected_segment"]
        st.write("Analysing: " + chosen)
        
        # Interactive widget to prove session state persistence
        analysis_type = st.radio("Select Analysis Type", ["Basic", "Deep Dive"])
        
        if st.button("Run Analysis"):
            # Compute and display results for chosen segment
            st.session_state["analysis_result"] = f"Completed {analysis_type} analysis for {chosen} segment."
            
        if st.session_state["analysis_result"]:
            st.success(st.session_state["analysis_result"])
