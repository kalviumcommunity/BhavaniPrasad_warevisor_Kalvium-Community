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

    with login_tab2:
        uname_input = st.text_input("Username")
        pwd_input = st.text_input("Password", type="password")
        if st.button("Authenticate", use_container_width=True):
            user_info = authenticate_user(uname_input, pwd_input)
            if user_info:
                st.session_state["authenticated"] = True
                st.session_state["user_role"] = user_info["role"]
                st.session_state["user_name"] = user_info["full_name"]
                st.session_state["username"] = user_info["username"]
                st.sidebar.success(f"Welcome {user_info['full_name']}!")
                st.rerun()
            else:
                st.sidebar.error("Invalid username or password.")

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

st.sidebar.divider()

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

        # KPI Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        total_records = len(df_sales)
        total_retail = df_sales["retail_sales"].sum() if "retail_sales" in df_sales else 0
        total_wh_sales = df_sales["warehouse_sales"].sum() if "warehouse_sales" in df_sales else 0
        total_suppliers = df_sales["supplier"].nunique() if "supplier" in df_sales else 0

        with col1:
            st.metric("Total Items / Records", f"{total_records:,}")
        with col2:
            st.metric("Total Retail Sales ($)", f"${total_retail:,.2f}")
        with col3:
            st.metric("Total Warehouse Sales ($)", f"${total_wh_sales:,.2f}")
        with col4:
            st.metric("Unique Suppliers", f"{total_suppliers:,}")

        st.divider()

        # Charts Section
        chart_col1, chart_col2 = st.columns([2, 1])

        with chart_col1:
            st.subheader("Sales Performance by Item Type")
            if not df_sales.empty and "item_type" in df_sales:
                type_sales = df_sales.groupby("item_type")[["retail_sales", "warehouse_sales"]].sum().reset_index()
                fig_bar = px.bar(
                    type_sales, x="item_type", y=["retail_sales", "warehouse_sales"],
                    barmode="group", title="Retail vs Warehouse Sales by Item Category",
                    color_discrete_sequence=["#2563eb", "#10b981"]
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No sales data available for chart rendering.")

        with chart_col2:
            st.subheader("Top Suppliers Breakdown")
            if not df_sales.empty and "supplier" in df_sales:
                top_supp = df_sales.groupby("supplier")["warehouse_sales"].sum().nlargest(5).reset_index()
                fig_pie = px.pie(top_supp, names="supplier", values="warehouse_sales", hole=0.4, title="Top 5 Suppliers")
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No supplier data available.")

    elif page == "📦 All Inventory Items":
        st.markdown('<span class="badge-manager">ROLE: MANAGER</span>', unsafe_allow_html=True)
        st.title("Warehouse Item Storing Database")
        st.caption("Search, filter, and inspect warehouse item records in PostgreSQL")
        st.divider()

        if not df_sales.empty:
            # Filters
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                item_types = ["All"] + sorted(df_sales["item_type"].dropna().unique().tolist())
                sel_type = st.selectbox("Filter by Item Type", item_types)
            with f_col2:
                suppliers = ["All"] + sorted(df_sales["supplier"].dropna().unique().tolist())[:100]
                sel_supp = st.selectbox("Filter by Supplier", suppliers)
            with f_col3:
                search_kw = st.text_input("Search Description / Code")

            filtered_df = df_sales.copy()
            if sel_type != "All":
                filtered_df = filtered_df[filtered_df["item_type"] == sel_type]
            if sel_supp != "All":
                filtered_df = filtered_df[filtered_df["supplier"] == sel_supp]
            if search_kw:
                filtered_df = filtered_df[
                    filtered_df["item_description"].str.contains(search_kw, case=False, na=False) |
                    filtered_df["item_code"].str.contains(search_kw, case=False, na=False)
                ]

            st.write(f"Showing **{len(filtered_df):,}** matching items")
            st.dataframe(filtered_df.head(100), use_container_width=True)
        else:
            st.warning("No item records found in database.")

    elif page == "➕ Add/Update Items":
        st.markdown('<span class="badge-manager">ROLE: MANAGER</span>', unsafe_allow_html=True)
        st.title("Add New Item to PostgreSQL Schema")
        st.caption("Create new stock items or sales entries directly in PostgreSQL database")
        st.divider()

        with st.form("add_item_form"):
            col1, col2 = st.columns(2)
            with col1:
                year_in = st.number_input("Year", min_value=2017, max_value=2030, value=2020)
                month_in = st.number_input("Month", min_value=1, max_value=12, value=1)
                supplier_in = st.text_input("Supplier Name")
                item_code_in = st.text_input("Item Code")
            with col2:
                item_desc_in = st.text_input("Item Description")
                item_type_in = st.selectbox("Item Type", ["WINE", "BEER", "LIQUOR", "NON-ALCOHOL", "OTHER"])
                retail_sales_in = st.number_input("Retail Sales Amount ($)", min_value=0.0, value=0.0)
                wh_sales_in = st.number_input("Warehouse Sales Amount ($)", min_value=0.0, value=0.0)

            submitted = st.form_submit_button("Save Item to PostgreSQL")

            if submitted:
                if not supplier_in or not item_code_in or not item_desc_in:
                    st.error("Please fill in Supplier, Item Code, and Description.")
                else:
                    try:
                        engine = get_engine()
                        with engine.begin() as conn:
                            ins_query = text("""
                                INSERT INTO warehouse_retail_sales 
                                (year, month, supplier, item_code, item_description, item_type, retail_sales, warehouse_sales)
                                VALUES (:y, :m, :s, :code, :desc, :type, :rs, :ws)
                            """)
                            conn.execute(ins_query, {
                                "y": year_in, "m": month_in, "s": supplier_in,
                                "code": item_code_in, "desc": item_desc_in,
                                "type": item_type_in, "rs": retail_sales_in, "ws": wh_sales_in
                            })
                        st.success(f"[OK] Item '{item_code_in}' successfully saved to PostgreSQL database!")
                        st.cache_data.clear()
                    except Exception as err:
                        st.error(f"Error saving item to database: {err}")

    elif page == "👥 Role & User Management":
        st.markdown('<span class="badge-manager">ROLE: MANAGER</span>', unsafe_allow_html=True)
        st.title("Role-Based User Management")
        st.caption("View and manage app accounts for Manager and Product Sender roles")
        st.divider()

        try:
            engine = get_engine()
            users_df = pd.read_sql("SELECT user_id, username, full_name, email, role, status, created_at FROM app_users;", engine)
            st.subheader("Registered System Users")
            st.dataframe(users_df, use_container_width=True)
        except Exception:
            st.write("Default Demo Roles:")
            st.table([
                {"Username": "manager", "Role": "manager", "Full Name": "Central Warehouse Manager", "Access": "Full Admin (SELECT, INSERT, UPDATE, DELETE)"},
                {"Username": "sender", "Role": "product_sender", "Full Name": "Product Dispatch Sender", "Access": "Item Sender (SELECT, INSERT)"}
            ])

    elif page == "⚙️ Database Settings":
        st.markdown('<span class="badge-manager">ROLE: MANAGER</span>', unsafe_allow_html=True)
        st.title("Supabase PostgreSQL Database Settings")
        st.divider()

        is_connected = test_connection()
        if is_connected:
            st.success("Connected to PostgreSQL Database: db.pbnlrmcohihvmxxaqgmj.supabase.co:5432")
        else:
            st.warning("Not connected to PostgreSQL Database. Check POSTGRES_PASSWORD in .env or credentials.")

# ---------------------------------------------------------
# PRODUCT SENDER ROLE PAGES
# ---------------------------------------------------------
else:
    if page == "🚚 Product Sender Portal":
        st.markdown('<span class="badge-sender">ROLE: PRODUCT SENDER</span>', unsafe_allow_html=True)
        st.title("Product Sender & Dispatch Portal")
        st.caption("Submit stock items, send products to warehouse, and track dispatched shipments")
        st.divider()

        s_col1, s_col2 = st.columns(2)
        with s_col1:
            st.metric("Logged In Sender", st.session_state["user_name"])
        with s_col2:
            st.metric("Dispatched Items Total", f"{len(df_sales):,}" if not df_sales.empty else "0")

        st.divider()
        st.subheader("Quick Dispatched Inventory Overview")
        if not df_sales.empty:
            st.dataframe(df_sales.head(20), use_container_width=True)

    elif page == "📦 My Dispatched Items":
        st.markdown('<span class="badge-sender">ROLE: PRODUCT SENDER</span>', unsafe_allow_html=True)
        st.title("Dispatched Item Catalog")
        st.divider()
        if not df_sales.empty:
            search_sender = st.text_input("Filter Item Code or Description")
            if search_sender:
                res = df_sales[df_sales["item_description"].str.contains(search_sender, case=False, na=False)]
                st.dataframe(res, use_container_width=True)
            else:
                st.dataframe(df_sales.head(50), use_container_width=True)

    elif page == "➕ Submit New Shipment Item":
        st.markdown('<span class="badge-sender">ROLE: PRODUCT SENDER</span>', unsafe_allow_html=True)
        st.title("Submit New Shipment Entry")
        st.caption("Add stock shipment into PostgreSQL warehouse item database")
        st.divider()

        with st.form("sender_item_form"):
            s_supplier = st.text_input("Supplier / Sender Name", value=st.session_state["user_name"])
            s_code = st.text_input("Item Code (SKU)")
            s_desc = st.text_input("Item Description")
            s_type = st.selectbox("Item Category", ["WINE", "BEER", "LIQUOR", "NON-ALCOHOL", "OTHER"])
            s_qty = st.number_input("Warehouse Sales / Dispatch Quantity", min_value=1.0, value=10.0)

            s_submit = st.form_submit_button("Submit Product Shipment")

            if s_submit:
                if not s_code or not s_desc:
                    st.error("Item Code and Description are required.")
                else:
                    try:
                        engine = get_engine()
                        with engine.begin() as conn:
                            ins_stmt = text("""
                                INSERT INTO warehouse_retail_sales 
                                (year, month, supplier, item_code, item_description, item_type, retail_sales, warehouse_sales)
                                VALUES (2020, 8, :s, :code, :desc, :type, 0.0, :ws)
                            """)
                            conn.execute(ins_stmt, {
                                "s": s_supplier, "code": s_code,
                                "desc": s_desc, "type": s_type, "ws": s_qty
                            })
                        st.success(f"[OK] Shipment for '{s_desc}' ({s_code}) submitted successfully!")
                        st.cache_data.clear()
                    except Exception as err:
                        st.error(f"Failed to submit shipment: {err}")

    elif page == "⚙️ Settings":
        st.markdown('<span class="badge-sender">ROLE: PRODUCT SENDER</span>', unsafe_allow_html=True)
        st.title("Sender Account Settings")
        st.write(f"Logged in as **{st.session_state['user_name']}** ({st.session_state['username']})")
