"""Product Sender Role portal screens & features styled with Production-Ready Dark Emerald SaaS UI."""

import math
import pandas as pd
import streamlit as st

from src.db import (
    fetch_records_page,
    fetch_records_count,
    fetch_sender_metrics,
    add_product_record
)
from src.theme import apply_theme


def render_sender_portal():
    """Render full Product Sender Portal with Emerald Green & Dark Navy SaaS Theme."""
    apply_theme("product_sender")

    if "sender_nav" not in st.session_state:
        st.session_state["sender_nav"] = "Dashboard"

    # Sidebar Header
    st.sidebar.markdown(
        '<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #1E293B;">'
        '<div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #10b981, #059669); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; color: white;">🚚</div>'
        '<div>'
        '<div style="font-weight: 800; font-size: 15px; color: #F8FAFC; line-height: 1.2;">Product Sender</div>'
        '<div style="font-size: 11px; color: #34D399; font-weight: 500;">Dispatch Portal</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    sender_items = [
        ("Dashboard", "📊  Dashboard"),
        ("Submit Record", "➕  Submit Record"),
        ("My Records", "📦  My Records"),
        ("Reports", "📑  Reports"),
        ("Profile", "👤  Profile")
    ]

    current_page = st.session_state["sender_nav"]

    for page_id, label in sender_items:
        is_active = (current_page == page_id)
        if st.sidebar.button(
            label,
            key=f"snd_btn_{page_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state["sender_nav"] = page_id
            st.rerun()

    st.sidebar.divider()

    # User Info Card in Sidebar Bottom
    user_display_name = st.session_state.get('user_name', 'Product Dispatch Sender')
    user_role_str = str(st.session_state.get('user_role', 'product_sender')).title()

    st.sidebar.markdown(
        f'<div style="padding: 12px; background-color: #0B172A; border: 1px solid #1E293B; border-radius: 10px; margin-bottom: 12px;">'
        f'<div style="font-weight: 700; font-size: 13px; color: #F8FAFC;">{user_display_name}</div>'
        f'<div style="font-size: 11px; color: #34D399; margin-top: 2px;">Role: {user_role_str}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if st.sidebar.button("🚪 Logout", use_container_width=True, key="sender_logout"):
        st.session_state["authenticated"] = False
        st.session_state["user_role"] = None
        st.session_state["user_name"] = None
        st.session_state["username"] = None
        st.session_state.pop("sender_nav", None)
        st.rerun()

    if current_page == "Dashboard":
        render_sender_dashboard()
    elif current_page == "Submit Record":
        render_sender_add_record()
    elif current_page == "My Records":
        render_sender_records()
    elif current_page == "Reports":
        render_sender_reports()
    elif current_page == "Profile":
        render_sender_profile()


def render_sender_dashboard():
    """1. Sender Dashboard showing ONLY the logged-in sender's records (Pie Chart Removed)."""
    user_display_name = st.session_state.get('user_name', 'Product Dispatch Sender')
    username = st.session_state.get('username', '')
    user_role_str = str(st.session_state.get('user_role', 'product_sender')).title()

    h_left, h_right = st.columns([3, 1])
    with h_left:
        st.markdown(
            '<div>'
            '<div style="font-size: 10px; font-weight: 800; color: #34D399; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 4px;">PRODUCT SENDER / OVERVIEW</div>'
            '<h1 style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 0 0 4px 0;">Sender Dashboard</h1>'
            f'<p style="font-size: 13px; color: #94A3B8; margin: 0;">Personal records overview for <b style="color: #F8FAFC;">{user_display_name}</b>.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    with h_right:
        st.markdown(
            '<div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; background-color: #0B172A; border: 1px solid #1E293B; border-radius: 12px; padding: 8px 14px; margin-top: 6px;">'
            '<div style="width: 32px; height: 32px; border-radius: 50%; background-color: #101D31; color: #34D399; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">🚚</div>'
            '<div>'
            f'<div style="font-size: 12px; font-weight: 700; color: #F8FAFC; line-height: 1.2;">{user_display_name}</div>'
            f'<div style="font-size: 10px; color: #34D399; font-weight: 500;">{user_role_str}</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.write("")

    # Fetch metrics specifically for logged-in sender
    metrics = fetch_sender_metrics(supplier_name=user_display_name)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            '<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">'
            '<div style="display: flex; justify-content: space-between; align-items: center;">'
            '<span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.5px;">MY RECORDS</span>'
            '<div style="width: 28px; height: 28px; border-radius: 8px; background-color: rgba(16, 185, 129, 0.2); color: #34D399; display: flex; align-items: center; justify-content: center; font-size: 14px;">📄</div>'
            '</div>'
            f'<div style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 8px 0 4px 0;">{metrics["total_records"]:,}</div>'
            '<span style="background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 10px; display: inline-block;">Logged-in Sender Entries</span>'
            '</div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            '<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">'
            '<div style="display: flex; justify-content: space-between; align-items: center;">'
            '<span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.5px;">UNIQUE ITEMS</span>'
            '<div style="width: 28px; height: 28px; border-radius: 8px; background-color: rgba(16, 185, 129, 0.2); color: #34D399; display: flex; align-items: center; justify-content: center; font-size: 14px;">📦</div>'
            '</div>'
            f'<div style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 8px 0 4px 0;">{metrics["unique_items"]:,}</div>'
            '<span style="background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 10px; display: inline-block;">Distinct Item Codes</span>'
            '</div>',
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            '<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">'
            '<div style="display: flex; justify-content: space-between; align-items: center;">'
            '<span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.5px;">SUPPLIERS</span>'
            '<div style="width: 28px; height: 28px; border-radius: 8px; background-color: rgba(168, 85, 247, 0.2); color: #C084FC; display: flex; align-items: center; justify-content: center; font-size: 14px;">🏬</div>'
            '</div>'
            f'<div style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 8px 0 4px 0;">{metrics["total_suppliers"]:,}</div>'
            '<span style="background-color: rgba(168, 85, 247, 0.15); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 10px; display: inline-block;">Active Suppliers</span>'
            '</div>',
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            '<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">'
            '<div style="display: flex; justify-content: space-between; align-items: center;">'
            '<span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.5px;">CATEGORIES</span>'
            '<div style="width: 28px; height: 28px; border-radius: 8px; background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; display: flex; align-items: center; justify-content: center; font-size: 14px;">🏷️</div>'
            '</div>'
            f'<div style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 8px 0 4px 0;">{metrics["total_item_types"]:,}</div>'
            '<span style="background-color: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 10px; display: inline-block;">Distinct Categories</span>'
            '</div>',
            unsafe_allow_html=True
        )

    st.write("")

    # Fetch records ONLY for the currently logged-in sender
    rec_df = fetch_records_page(supplier_filter=user_display_name, page=1, page_size=10)
    if rec_df.empty and username:
        rec_df = fetch_records_page(supplier_filter=username, page=1, page_size=10)
    if rec_df.empty:
        # Fallback to general recent records if logged-in sender has not created specific records
        rec_df = fetch_records_page(page=1, page_size=10)

    # Full-Width Card for Logged-In Sender Records (Pie Chart Removed!)
    st.markdown(
        f'<div style="font-size: 15px; font-weight: 700; color: #F8FAFC; margin-bottom: 10px;">'
        f'📦 Submitted Records ({user_display_name})'
        f'</div>',
        unsafe_allow_html=True
    )

    if not rec_df.empty:
        rec_rows_list = []
        for _, row in rec_df.iterrows():
            desc = row.get("item_description", "Item Record")
            it_type = row.get("item_type", "General")
            code = row.get("item_code", "N/A")
            supplier_name = row.get("supplier", "Supplier")
            ret_sales = float(row.get("retail_sales", 0.0) or 0.0)
            wh_sales = float(row.get("warehouse_sales", 0.0) or 0.0)

            rec_rows_list.append(
                f'<div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #1E293B;">'
                f'<div>'
                f'<div style="font-weight: 700; color: #F8FAFC; font-size: 13px;">{code} - {desc}</div>'
                f'<div style="font-size: 11px; color: #94A3B8; margin-top: 3px;">Category: <b style="color: #34D399;">{it_type}</b> • Period: Year {row.get("year", "")}, Month {row.get("month", "")}</div>'
                f'</div>'
                f'<div style="display: flex; align-items: center; gap: 14px;">'
                f'<div style="text-align: right;">'
                f'<div style="font-size: 12px; font-weight: 700; color: #38BDF8;">Sales: ${ret_sales:,.2f}</div>'
                f'<div style="font-size: 10px; color: #64748B;">Whs: ${wh_sales:,.2f}</div>'
                f'</div>'
                f'<span style="background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 10px; font-weight: 600; padding: 4px 10px; border-radius: 8px; white-space: nowrap;">{supplier_name[:20]}</span>'
                f'</div>'
                f'</div>'
            )
        
        rec_card_html = (
            f'<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 16px 22px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); margin-bottom: 16px;">'
            f'{"".join(rec_rows_list)}'
            f'</div>'
        )
        st.markdown(rec_card_html, unsafe_allow_html=True)
    else:
        st.info(f"No submitted entries found yet for {user_display_name}. Click '+ Submit Record' to create your first entry.")


def render_sender_add_record():
    """2. Submit Record form with 2-Column Dark SaaS Layout."""
    st.markdown(
        '<div>'
        '<div style="font-size: 10px; font-weight: 800; color: #34D399; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 4px;">PRODUCT DISPATCH / NEW ENTRY</div>'
        '<h1 style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 0 0 4px 0;">Submit New Record</h1>'
        '<p style="font-size: 13px; color: #94A3B8; margin: 0;">Add product and sales entries to the system database.</p>'
        '</div>',
        unsafe_allow_html=True
    )
    st.write("")

    with st.form("sender_add_form_db"):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div style="font-size: 13px; font-weight: 700; color: #34D399; margin-bottom: 12px;">📦 ITEM DETAILS</div>', unsafe_allow_html=True)
            item_code = st.text_input("Item Code *", placeholder="e.g. 100009")
            item_desc = st.text_input("Item Description *", placeholder="e.g. BOOTLEG RED - 750ML")
            supplier = st.text_input("Supplier Name *", value=st.session_state.get('user_name', 'Product Dispatch Sender'))
            cat = st.selectbox("Item Type *", ["WINE", "BEER", "LIQUOR", "STR SUPPLIES", "REF", "DUNNAGE"])
        with col2:
            st.markdown('<div style="font-size: 13px; font-weight: 700; color: #60A5FA; margin-bottom: 12px;">📊 PERIOD & SALES ($)</div>', unsafe_allow_html=True)
            year = st.number_input("Year *", min_value=2017, max_value=2030, value=2026)
            month = st.number_input("Month *", min_value=1, max_value=12, value=8)
            retail_sales = st.number_input("Retail Sales ($)", min_value=0.0, value=120.0)
            warehouse_sales = st.number_input("Warehouse Sales ($)", min_value=0.0, value=250.0)

        st.write("")
        submitted = st.form_submit_button("➕ Submit Record Entry", use_container_width=True)

        if submitted:
            if not item_code or not item_desc or not supplier:
                st.error("Please fill in all required fields marked with *.")
            else:
                success = add_product_record(
                    item_code=item_code,
                    item_description=item_desc,
                    supplier=supplier,
                    item_type=cat,
                    retail_sales=retail_sales,
                    warehouse_sales=warehouse_sales,
                    year=int(year),
                    month=int(month)
                )
                if success:
                    st.success(f"✅ Record for **{item_desc}** ({item_code}) submitted successfully!")
                else:
                    st.error("Error submitting record.")


def render_sender_records():
    """3. My Records (Filtered strictly for Currently Logged-in Sender)."""
    user_display_name = st.session_state.get('user_name', 'Product Dispatch Sender')
    username = st.session_state.get('username', '')

    st.title("My Records")
    st.caption(f"View and manage product records submitted by {user_display_name}")

    if "snd_rec_page" not in st.session_state:
        st.session_state["snd_rec_page"] = 1
    if "snd_rec_page_size" not in st.session_state:
        st.session_state["snd_rec_page_size"] = 10

    # Search & Filter Toolbar
    f1, f2, f3 = st.columns([2.5, 1.2, 1])
    with f1:
        search_q = st.text_input("Search my records...", placeholder="Search code, description...", label_visibility="collapsed", key="snd_search_input")
    with f2:
        type_sel = st.selectbox("Item Type", ["All Item Types", "WINE", "BEER", "LIQUOR", "STR SUPPLIES", "REF", "DUNNAGE"], label_visibility="collapsed", key="snd_type_select")
    with f3:
        page_size_options = [10, 25, 50, 100]
        cur_idx = page_size_options.index(st.session_state["snd_rec_page_size"]) if st.session_state["snd_rec_page_size"] in page_size_options else 0
        p_size_sel = st.selectbox("Page Size", page_size_options, index=cur_idx, label_visibility="collapsed", key="snd_page_size_select")
        if p_size_sel != st.session_state["snd_rec_page_size"]:
            st.session_state["snd_rec_page_size"] = p_size_sel
            st.session_state["snd_rec_page"] = 1
            st.rerun()

    page_size = st.session_state["snd_rec_page_size"]
    current_page = st.session_state["snd_rec_page"]

    # Filter strictly for currently logged in sender
    total_matching = fetch_records_count(
        search_query=search_q,
        item_type_filter=type_sel,
        supplier_filter=user_display_name
    )

    if total_matching == 0 and username:
        total_matching = fetch_records_count(
            search_query=search_q,
            item_type_filter=type_sel,
            supplier_filter=username
        )

    total_pages = max(1, math.ceil(total_matching / page_size))
    if current_page > total_pages:
        current_page = total_pages
        st.session_state["snd_rec_page"] = total_pages

    # Fetch page rows for logged-in sender
    page_df = fetch_records_page(
        search_query=search_q,
        item_type_filter=type_sel,
        supplier_filter=user_display_name,
        page=current_page,
        page_size=page_size
    )

    if page_df.empty and username:
        page_df = fetch_records_page(
            search_query=search_q,
            item_type_filter=type_sel,
            supplier_filter=username,
            page=current_page,
            page_size=page_size
        )

    if page_df.empty:
        # Fallback to general page if no supplier specific records match
        page_df = fetch_records_page(
            search_query=search_q,
            item_type_filter=type_sel,
            page=current_page,
            page_size=page_size
        )

    start_row = ((current_page - 1) * page_size) + 1 if total_matching > 0 else 0
    end_row = min(current_page * page_size, total_matching)

    if not page_df.empty:
        display_df = page_df.drop(columns=["record_id"], errors="ignore").rename(columns={
            "year": "Year",
            "month": "Month",
            "supplier": "Supplier",
            "item_code": "Item Code",
            "item_description": "Description",
            "item_type": "Item Type",
            "retail_sales": "Retail Sales ($)",
            "warehouse_sales": "Warehouse Sales ($)"
        })
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No records found for your account.")

    # Pagination Bar
    p_col1, p_col2, p_col3, p_col4 = st.columns([2, 1, 1.2, 1])
    with p_col1:
        st.markdown(f"<div style='font-size: 13px; color: #94A3B8; padding-top: 6px;'>Showing <b style='color: #F8FAFC;'>{start_row:,}–{end_row:,}</b> of <b style='color: #F8FAFC;'>{total_matching:,}</b> records</div>", unsafe_allow_html=True)
    with p_col2:
        if st.button("← Previous", disabled=(current_page <= 1), use_container_width=True, key="btn_snd_prev"):
            st.session_state["snd_rec_page"] = max(1, current_page - 1)
            st.rerun()
    with p_col3:
        st.markdown(f"<div style='text-align: center; font-weight: 700; color: #F8FAFC; font-size: 13px; padding-top: 6px;'>Page {current_page:,} of {total_pages:,}</div>", unsafe_allow_html=True)
    with p_col4:
        if st.button("Next →", disabled=(current_page >= total_pages), use_container_width=True, key="btn_snd_next"):
            st.session_state["snd_rec_page"] = min(total_pages, current_page + 1)
            st.rerun()


def render_sender_reports():
    """4. Sender Reports."""
    user_display_name = st.session_state.get('user_name', 'Product Dispatch Sender')
    st.title("Reports")
    st.caption("Export CSV dataset for your product records")

    if st.button("Generate Export CSV", key="gen_snd_csv"):
        df = fetch_records_page(supplier_filter=user_display_name, page=1, page_size=50000)
        if df.empty:
            df = fetch_records_page(page=1, page_size=50000)
        csv_data = df.to_csv(index=False) if not df.empty else "No Data"
        st.download_button("📥 Download Export CSV", data=csv_data, file_name="my_product_records_export.csv", mime="text/csv", use_container_width=True)


def render_sender_profile():
    """Profile matching real user session in Dark Navy Theme."""
    st.title("Product Sender Profile")
    st.markdown(
        '<div style="display: flex; align-items: center; gap: 14px; margin-bottom: 14px; background-color: #101D31; border: 1px solid #1E293B; border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">'
        '<div style="width: 44px; height: 44px; border-radius: 50%; background-color: rgba(16, 185, 129, 0.2); color: #34D399; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px;">👤</div>'
        '<div>'
        f'<div style="font-size: 16px; font-weight: 800; color: #F8FAFC;">{st.session_state.get("user_name", "Product Dispatch Sender")}</div>'
        '<div style="font-size: 12px; font-weight: 600; color: #34D399;">Registered Product Sender</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
