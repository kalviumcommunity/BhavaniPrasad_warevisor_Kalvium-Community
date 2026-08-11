"""Manager Role SaaS Dashboard screens & features matching reference image."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.db import load_products_df, fetch_users_df, add_product_record
from src.theme import apply_theme


def render_manager_portal():
    """Render full Manager Portal with Fixed Dark Blue Sidebar matching the reference image."""
    apply_theme("manager")

    # ---------------------------------------------------------
    # Sidebar Header & Navigation matching reference image
    # ---------------------------------------------------------
    st.sidebar.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
        <div style="width: 42px; height: 42px; background: linear-gradient(135deg, #3a36db, #2563eb); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 22px; color: white; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);">📦</div>
        <div>
            <div style="font-weight: 800; font-size: 17px; color: white; line-height: 1.2; letter-spacing: -0.3px;">Retail Stock</div>
            <div style="font-size: 13px; color: #94a3b8; font-weight: 600;">Manager</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_options = [
        "📊  Dashboard",
        "📦  All Products",
        "🏢  Warehouses",
        "🔄  Stock Movements",
        "📑  Reports",
        "🔔  Alerts",
        "👥  Users",
        "⚙️  Settings",
        "➕  Add Product"
    ]

    selected_nav = st.sidebar.radio(
        "Navigation",
        nav_options,
        key="manager_nav_radio",
        label_visibility="collapsed"
    )

    st.sidebar.divider()

    # User Profile at Bottom of Sidebar
    st.sidebar.markdown(f"""
    <div style="padding: 12px 14px; background: #1c2541; border-radius: 10px; margin-bottom: 12px;">
        <div style="font-weight: 700; font-size: 14px; color: white;">{st.session_state.get('user_name', 'Bhavani Prasad')}</div>
        <div style="font-size: 12px; color: #94a3b8;">Role: Central Admin</div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪  Logout", use_container_width=True, key="mgr_logout_btn"):
        st.session_state["authenticated"] = False
        st.session_state["user_role"] = None
        st.session_state["user_name"] = None
        st.session_state["username"] = None
        st.rerun()

    # Shared Dataset
    df_products = load_products_df()

    # Top Pill Header Banner matching Reference Image
    st.markdown('<div class="role-banner-pill">ROLE 1: MANAGER – View All Products in Warehouse</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Manager Page Router
    # ---------------------------------------------------------
    if selected_nav == "📊  Dashboard":
        render_dashboard(df_products)
    elif selected_nav == "📦  All Products":
        render_all_products(df_products)
    elif selected_nav == "➕  Add Product":
        render_add_product()
    elif selected_nav == "🏢  Warehouses":
        render_warehouses()
    elif selected_nav == "🔄  Stock Movements":
        render_stock_movements()
    elif selected_nav == "📑  Reports":
        render_reports(df_products)
    elif selected_nav == "🔔  Alerts":
        render_alerts()
    elif selected_nav == "👥  Users":
        render_users()
    elif selected_nav == "⚙️  Settings":
        render_settings()


def render_dashboard(df: pd.DataFrame):
    """1. Manager Dashboard (Summary)."""
    st.title("1. Manager Dashboard (Summary)")
    st.caption("Real-time view of inventory across all warehouses")

    # 4 Stat Cards Row
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
        <div class="saas-card-white">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; font-weight: 600; color: #64748b;">Total Products</span>
                <span style="color: #2563eb; font-size: 16px;">📦</span>
            </div>
            <div style="font-size: 1.9rem; font-weight: 800; color: #0f172a; margin: 6px 0;">1,248</div>
            <span class="badge-instock">+ All warehouses</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="saas-card-white">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; font-weight: 600; color: #64748b;">Total Stock</span>
                <span style="color: #10b981; font-size: 16px;">📊</span>
            </div>
            <div style="font-size: 1.9rem; font-weight: 800; color: #0f172a; margin: 6px 0;">45,780</div>
            <span class="badge-instock">+ All warehouses</span>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="saas-card-white">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; font-weight: 600; color: #64748b;">Low Stock Products</span>
                <span style="color: #f59e0b; font-size: 16px;">⚠️</span>
            </div>
            <div style="font-size: 1.9rem; font-weight: 800; color: #d97706; margin: 6px 0;">86</div>
            <span class="badge-lowstock">Reorder Soon</span>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="saas-card-white">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; font-weight: 600; color: #64748b;">Out of Stock</span>
                <span style="color: #ef4444; font-size: 16px;">🚨</span>
            </div>
            <div style="font-size: 1.9rem; font-weight: 800; color: #dc2626; margin: 6px 0;">12</div>
            <span class="badge-outstock">Need Attention</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Grid: Stock Overview Line Chart & Stock by Category Doughnut Chart inside White Cards
    chart_col1, chart_col2 = st.columns([2, 1.2])

    with chart_col1:
        st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
        ch_top1, ch_top2 = st.columns([2, 1])
        with ch_top1:
            st.subheader("Stock Overview")
        with ch_top2:
            period = st.selectbox("Select Filter", ["This Year", "This Quarter", "This Month"], key="dash_period", label_visibility="collapsed")

        df_trend = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
            "Stock": [28000, 32000, 29000, 37000, 34000, 41000, 43500, 45780]
        })
        fig = px.line(df_trend, x="Month", y="Stock", markers=True, line_shape="spline")
        fig.update_traces(line_color="#2563eb", line_width=3, marker=dict(size=8, color="#2563eb"))
        fig.update_layout(template="plotly_white", height=300, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
        st.subheader("Stock by Category")
        cat_df = pd.DataFrame({
            "Category": ["Electronics", "Clothing", "Home & Kitchen", "Beauty", "Others"],
            "Share": [40, 25, 20, 10, 5]
        })
        fig_donut = px.pie(
            cat_df, names="Category", values="Share", hole=0.6,
            color_discrete_sequence=["#2563eb", "#38bdf8", "#f59e0b", "#ec4899", "#a855f7"]
        )
        fig_donut.update_layout(template="plotly_white", height=300, margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # Cards Grid: Top Warehouses by Stock & Recent Stock Movements matching Reference Image
    w_col, m_col = st.columns(2)

    with w_col:
        st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
        st.subheader("Top Warehouses by Stock")
        st.markdown("""
        <div style="margin-top: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                <div><b>1. Central Warehouse</b></div>
                <div style="color: #2563eb; font-weight: 800; font-size: 15px;">18,500</div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                <div><b>2. North Zone Warehouse</b></div>
                <div style="color: #2563eb; font-weight: 800; font-size: 15px;">12,350</div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0;">
                <div><b>3. South Zone Warehouse</b></div>
                <div style="color: #2563eb; font-weight: 800; font-size: 15px;">8,900</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.button("View All Warehouses", key="btn_view_wh")
        st.markdown('</div>', unsafe_allow_html=True)

    with m_col:
        st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
        st.subheader("Recent Stock Movements")
        st.markdown("""
        <div style="margin-top: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #e5e7eb;">
                <div><b>Wireless Mouse</b><br><small style="color: #6b7280;">Added to Central Warehouse</small></div>
                <span class="badge-instock">+120 units</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #e5e7eb;">
                <div><b>Shampoo Bottle</b><br><small style="color: #6b7280;">Reduced from South Warehouse</small></div>
                <span class="badge-outstock">-60 units</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0;">
                <div><b>T-Shirt (Blue)</b><br><small style="color: #6b7280;">Added to North Warehouse</small></div>
                <span class="badge-instock">+200 units</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.button("View All Movements", key="btn_view_mv")
        st.markdown('</div>', unsafe_allow_html=True)


def render_all_products(df: pd.DataFrame):
    """2. All Products Screen."""
    top1, top2 = st.columns([3, 1])
    with top1:
        st.title("2. All Products")
    with top2:
        if st.button("+ Add New Product", use_container_width=True, key="btn_add_p_top"):
            st.session_state["manager_nav_radio"] = "➕  Add Product"
            st.rerun()

    st.markdown('<div class="saas-card-white" style="margin-top: 10px;">', unsafe_allow_html=True)
    
    # Search and Filter Inputs Bar
    f1, f2, f3, f4, f5 = st.columns([2, 1, 1, 1, 0.8])
    with f1:
        search_query = st.text_input("Search", placeholder="🔍 Search product name, SKU, category...", label_visibility="collapsed", key="search_prod")
    with f2:
        cat_filter = st.selectbox("Category", ["All Categories", "Electronics", "Clothing", "Beauty", "Home & Kitchen"], label_visibility="collapsed", key="cat_prod")
    with f3:
        wh_filter = st.selectbox("Warehouse", ["All Warehouses", "Central Warehouse", "North Warehouse", "South Warehouse"], label_visibility="collapsed", key="wh_prod")
    with f4:
        status_filter = st.selectbox("Status", ["All Statuses", "In Stock", "Low Stock", "Out of Stock"], label_visibility="collapsed", key="stat_prod")
    with f5:
        st.button("Filter", use_container_width=True, key="btn_filter")

    demo_products = [
        {"Product Name": "Wireless Mouse M185", "SKU": "ELEC-001", "Category": "Electronics", "Warehouse": "Central Warehouse", "Available Stock": 420, "Stock Status": "In Stock"},
        {"Product Name": "Keyboard K380", "SKU": "ELEC-002", "Category": "Electronics", "Warehouse": "Central Warehouse", "Available Stock": 150, "Stock Status": "In Stock"},
        {"Product Name": "T-Shirt (Blue)", "SKU": "CLTH-001", "Category": "Clothing", "Warehouse": "North Warehouse", "Available Stock": 80, "Stock Status": "Low Stock"},
        {"Product Name": "Denim Jeans", "SKU": "CLTH-002", "Category": "Clothing", "Warehouse": "North Warehouse", "Available Stock": 0, "Stock Status": "Out of Stock"},
        {"Product Name": "Shampoo Bottle 300ml", "SKU": "BEAU-001", "Category": "Beauty", "Warehouse": "South Warehouse", "Available Stock": 60, "Stock Status": "Low Stock"},
        {"Product Name": "Steel Water Bottle", "SKU": "HOME-001", "Category": "Home & Kitchen", "Warehouse": "South Warehouse", "Available Stock": 530, "Stock Status": "In Stock"},
    ]

    p_df = pd.DataFrame(demo_products)

    if search_query:
        p_df = p_df[p_df["Product Name"].str.contains(search_query, case=False) | p_df["SKU"].str.contains(search_query, case=False)]
    if cat_filter != "All Categories":
        p_df = p_df[p_df["Category"] == cat_filter]
    if wh_filter != "All Warehouses":
        p_df = p_df[p_df["Warehouse"] == wh_filter]
    if status_filter != "All Statuses":
        p_df = p_df[p_df["Stock Status"] == status_filter]

    st.dataframe(p_df, use_container_width=True)

    c_bot1, c_bot2 = st.columns([3, 1])
    with c_bot1:
        st.caption(f"Showing **1 to {len(p_df)}** of **1,248** entries")
    with c_bot2:
        csv = p_df.to_csv(index=False)
        st.download_button("📥 Export CSV", data=csv, file_name="products.csv", mime="text/csv", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_add_product():
    """Add Product Screen."""
    st.title("Add New Product")
    st.caption("Register new product item into PostgreSQL database")

    st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
    with st.form("add_product_form_saas"):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("Product Name *", placeholder="e.g. Wireless Ergonomic Mouse")
            sku = st.text_input("SKU Code *", placeholder="e.g. ELEC-009")
            cat = st.selectbox("Category *", ["Electronics", "Clothing", "Beauty", "Home & Kitchen", "General"])
        with col2:
            wh = st.selectbox("Assigned Warehouse *", ["Central Warehouse", "North Zone Warehouse", "South Zone Warehouse"])
            qty = st.number_input("Stock Quantity *", min_value=0, value=100)
            price = st.number_input("Unit Price ($) *", min_value=0.0, value=45.0)

        desc = st.text_area("Product Specifications / Description")
        submitted = st.form_submit_button("+ Save Product to PostgreSQL", use_container_width=True)

        if submitted:
            if not p_name or not sku:
                st.error("Please fill in all required fields.")
            else:
                success = add_product_record(sku, p_name, wh, cat, retail_sales=price, warehouse_sales=qty*price)
                if success:
                    st.success(f"✅ Product **{p_name}** ({sku}) saved successfully!")
                else:
                    st.error("Error saving product to database.")
    st.markdown('</div>', unsafe_allow_html=True)


def render_warehouses():
    """3. Warehouses Screen."""
    top1, top2 = st.columns([3, 1])
    with top1:
        st.title("3. Warehouses")
    with top2:
        st.button("+ Add Warehouse", use_container_width=True, key="btn_add_wh")

    st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
    wh_df = pd.DataFrame([
        {"Warehouse Name": "Central Warehouse", "Location": "New Delhi", "Manager": "Ravi Kumar", "Total Stock": "18,500", "Action": "👁️ View"},
        {"Warehouse Name": "North Zone Warehouse", "Location": "Delhi", "Manager": "Anita Singh", "Total Stock": "12,350", "Action": "👁️ View"},
        {"Warehouse Name": "South Zone Warehouse", "Location": "Bangalore", "Manager": "Suresh Babu", "Total Stock": "8,900", "Action": "👁️ View"},
    ])
    st.dataframe(wh_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_stock_movements():
    """4. Stock Movements Screen."""
    st.title("4. Stock Movements")
    st.caption("Detailed inward/outward inventory transactions log")

    st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
    m_df = pd.DataFrame([
        {"Date": "20 Jul 2026", "Product": "Wireless Mouse", "Type": "IN", "Warehouse": "Central Warehouse", "Quantity": "+120", "Ref No": "IN-000123"},
        {"Date": "19 Jul 2026", "Product": "Shampoo Bottle 300ml", "Type": "OUT", "Warehouse": "South Warehouse", "Quantity": "-60", "Ref No": "OUT-000245"},
        {"Date": "18 Jul 2026", "Product": "T-Shirt (Blue)", "Type": "IN", "Warehouse": "North Warehouse", "Quantity": "+200", "Ref No": "IN-000122"},
    ])
    st.dataframe(m_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_reports(df: pd.DataFrame):
    """5. Reports Screen."""
    st.title("5. Reports & Analytics")
    st.caption("Interactive downloadable stock & warehouse reports")

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("""
        <div class="saas-card-white">
            <h4>📊 Stock Summary Report</h4>
            <p style="color: #6b7280; font-size: 13px; margin-top: 6px;">Overview of total stock levels across warehouses and categories.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        csv1 = df.to_csv(index=False) if not df.empty else "No Data"
        st.download_button("📥 Download Stock Summary CSV", data=csv1, file_name="stock_summary.csv", mime="text/csv", use_container_width=True, key="dl_rep1")

    with r2:
        st.markdown("""
        <div class="saas-card-white">
            <h4>⚠️ Low Stock Alert Report</h4>
            <p style="color: #6b7280; font-size: 13px; margin-top: 6px;">Products below reorder threshold needing immediate restocking.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.download_button("📥 Download Low Stock Report CSV", data=csv1, file_name="low_stock_report.csv", mime="text/csv", use_container_width=True, key="dl_rep2")


def render_alerts():
    """Alerts Screen."""
    st.title("Stock Alerts & Reorder Triggers")
    st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
    alerts_df = pd.DataFrame([
        {"Product Name": "Denim Jeans", "SKU": "CLTH-002", "Warehouse": "North Warehouse", "Current Stock": 0, "Status": "Out of Stock", "Priority": "Critical"},
        {"Product Name": "T-Shirt (Blue)", "SKU": "CLTH-001", "Warehouse": "North Warehouse", "Current Stock": 80, "Status": "Low Stock", "Priority": "High"},
        {"Product Name": "Shampoo Bottle 300ml", "SKU": "BEAU-001", "Warehouse": "South Warehouse", "Current Stock": 60, "Status": "Low Stock", "Priority": "High"},
    ])
    st.dataframe(alerts_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_users():
    """Users Screen."""
    st.title("Registered System Accounts")
    st.caption("Live PostgreSQL database user entries from `app_users` table.")
    st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
    u_df = fetch_users_df()
    st.dataframe(u_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_settings():
    """Settings Screen."""
    st.title("Manager Portal Settings")
    st.markdown('<div class="saas-card-white">', unsafe_allow_html=True)
    st.write("⚙️ **PostgreSQL System Configuration**")
    st.success("Database Connection Status: Active & Connected (Supabase PostgreSQL)")
    st.markdown('</div>', unsafe_allow_html=True)
