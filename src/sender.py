"""Product Sender Role portal screens and features as per the design layout."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db import load_products_df
from src.theme import apply_theme


def render_sender_portal():
    """Render full Product Sender Portal with Emerald Green Theme."""
    apply_theme("product_sender")

    # Sidebar & Brand Header
    st.sidebar.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
        <div style="width: 36px; height: 36px; background: #10b981; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; color: white;">🚚</div>
        <div>
            <div style="font-weight: 800; font-size: 16px; color: white;">Product Sender</div>
            <div style="font-size: 11px; color: #a7f3d0; text-transform: uppercase; letter-spacing: 0.5px;">Dispatch Portal</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_item = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Add Product",
            "My Products",
            "Send to Warehouse",
            "Sent History",
            "Profile"
        ],
        key="sender_nav"
    )

    st.sidebar.divider()
    st.sidebar.markdown(f"**{st.session_state.get('user_name', 'Supplier Sender')}**")
    st.sidebar.caption(f"Role: Product Sender (`{st.session_state.get('username', 'sender')}`)")

    if st.sidebar.button("🚪 Logout", use_container_width=True, key="sender_logout"):
        st.session_state["authenticated"] = False
        st.session_state["user_role"] = None
        st.session_state["user_name"] = None
        st.session_state["username"] = None
        st.rerun()

    df_products = load_products_df()

    if nav_item == "Dashboard":
        render_sender_dashboard()
    elif nav_item == "Add Product":
        render_sender_add_product()
    elif nav_item == "My Products":
        render_sender_my_products(df_products)
    elif nav_item == "Send to Warehouse":
        render_sender_send_warehouse()
    elif nav_item == "Sent History":
        render_sender_history()
    elif nav_item == "Profile":
        render_sender_profile()


def render_sender_dashboard():
    """1. Sender Dashboard."""
    st.markdown('<div class="header-banner">ROLE 2: PRODUCT SENDER – Add & Send Product Details</div>', unsafe_allow_html=True)
    st.title("1. Sender Dashboard")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Products Added", "56", "Total Products")
    with c2:
        st.metric("Pending In Sent", "12", "Not Yet Sent")
    with c3:
        st.metric("Products Sent", "44", "Successfully Sent")
    with c4:
        st.metric("Rejected", "3", "Needs Correction", delta_color="inverse")

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Recent Activity")
        st.markdown("""
        <div class="metric-card-box">
            <div style="padding: 8px 0; border-bottom: 1px solid #f1f5f9;">
                <b>Added new product Wireless Console</b><br>
                <small style="color: #64748b;">21 Dec 2026, 11:34 AM</small>
            </div>
            <div style="padding: 8px 0; border-bottom: 1px solid #f1f5f9;">
                <b>Sent 10 products to Central Warehouse</b><br>
                <small style="color: #64748b;">18 Jul 2026, 04:15 PM</small>
            </div>
            <div style="padding: 8px 0;">
                <b>Product Rejected: Travel Bag (Red)</b><br>
                <small style="color: #ef4444;">11 Jul 2026, 10:20 AM</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.subheader("Products Summary")
        sum_df = pd.DataFrame({
            "Category": ["Electronics", "Clothing", "Home & Kitchen", "Beauty", "Others"],
            "Share": [42, 28, 15, 10, 5]
        })
        fig = px.pie(sum_df, names="Category", values="Share", hole=0.5, color_discrete_sequence=px.colors.sequential.Emeral)
        fig.update_layout(template="plotly_white", height=300)
        st.plotly_chart(fig, use_container_width=True)


def render_sender_add_product():
    """2. Add Product."""
    st.title("2. Add Product")
    with st.form("sender_add_form"):
        p_name = st.text_input("Product Name *")
        sku = st.text_input("SKU *")
        cat = st.selectbox("Category *", ["Electronics", "Clothing", "Beauty", "Home & Kitchen"])
        brand = st.text_input("Brand")
        price = st.number_input("Unit Price ($) *", min_value=0.0, value=50.0)
        qty = st.number_input("Quantity *", min_value=1, value=100)
        desc = st.text_area("Description")
        submitted = st.form_submit_button("Send Product")
        if submitted:
            if not p_name or not sku:
                st.error("Please fill required fields.")
            else:
                st.success(f"✅ Product **{p_name}** added successfully!")


def render_sender_my_products(df: pd.DataFrame):
    """3. My Products."""
    st.title("3. My Products")
    st.dataframe(df.head(20), use_container_width=True)


def render_sender_send_warehouse():
    """4. Send To Warehouse."""
    st.title("4. Send To Warehouse")
    with st.form("sender_dispatch_form"):
        wh = st.selectbox("Select Warehouse *", ["Central Warehouse", "North Zone Warehouse", "South Zone Warehouse"])
        products = st.multiselect("Select Products *", ["Wireless Console", "Running Shoes", "Power Bank 10000mAh", "Steel Water Bottle"])
        qty = st.number_input("Dispatch Quantity", min_value=1, value=100)
        notes = st.text_area("Notes (Optional)")
        submitted = st.form_submit_button("Send Products")
        if submitted:
            st.success(f"✅ Dispatched {qty} units to {wh}!")


def render_sender_history():
    """5. Sent History."""
    st.title("5. Sent History")
    h_df = pd.DataFrame([
        {"Date": "18 Jul 2026", "Warehouse": "Central Warehouse", "Products": "Wireless Console, Power Bank", "Total Quantity": 45, "Status": "Delivered", "Ref No": "ORD-09823"},
        {"Date": "14 Jul 2026", "Warehouse": "North Warehouse", "Products": "Running Shoes", "Total Quantity": 12, "Status": "Delivered", "Ref No": "ORD-09824"},
        {"Date": "12 Jul 2026", "Warehouse": "South Warehouse", "Products": "Water Bottle Steel, T-Shirt", "Total Quantity": 85, "Status": "In Transit", "Ref No": "ORD-09825"},
        {"Date": "10 Jul 2026", "Warehouse": "Central Warehouse", "Products": "Keyboard K380", "Total Quantity": 20, "Status": "Rejected", "Ref No": "ORD-09826"},
    ])
    st.dataframe(h_df, use_container_width=True)


def render_sender_profile():
    """Profile."""
    st.title("Product Sender Profile")
    st.markdown(f"""
    **Full Name**: {st.session_state.get('user_name', 'Supplier Sender')}<br>
    **Role**: Product Sender<br>
    **Email**: {st.session_state.get('username', 'sender')}@warevisor.com
    """, unsafe_allow_html=True)
