"""Manager Role SaaS Dashboard screens & features styled with Production-Ready Dark Navy Theme."""

import pandas as pd
import plotly.express as px
import streamlit as st
import math

from src.db import (
    fetch_dashboard_metrics,
    fetch_monthly_records_trend,
    fetch_suppliers_summary,
    fetch_recent_records,
    fetch_item_types_summary,
    fetch_records_count,
    fetch_records_page,
    fetch_users_df,
    add_product_record
)
from src.theme import apply_theme
from src.kpi_dashboard import render_executive_kpi_dashboard



def render_manager_portal():
    """Render full Manager Portal with Dark Navy Sidebar & Custom SaaS Navigation."""
    apply_theme("manager")

    if "manager_nav" not in st.session_state:
        st.session_state["manager_nav"] = "Dashboard"

    # Sidebar Header
    st.sidebar.markdown(
        '<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #1E293B;">'
        '<div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #2563eb, #1d4ed8); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; color: white;">📊</div>'
        '<div>'
        '<div style="font-weight: 800; font-size: 15px; color: #F8FAFC; line-height: 1.2;">WareVisor</div>'
        '<div style="font-size: 11px; color: #94A3B8; font-weight: 500;">Retail Data Platform</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    current_page = st.session_state["manager_nav"]
    if current_page == "Settings":
        current_page = "Dashboard"
        st.session_state["manager_nav"] = "Dashboard"

    # Navigation Section 1: MAIN
    st.sidebar.markdown('<div class="nav-section-title">MAIN</div>', unsafe_allow_html=True)
    main_items = [
        ("Dashboard", "📊  Dashboard"),
        ("Executive KPIs", "🎯  Executive KPIs"),
        ("Records", "📦  Records"),
        ("Suppliers", "🏬  Suppliers"),
        ("Item Types", "🏷️  Item Types"),
        ("Reports", "📑  Reports")
    ]
    for page_id, label in main_items:
        is_active = (current_page == page_id)
        if st.sidebar.button(
            label,
            key=f"mgr_btn_{page_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state["manager_nav"] = page_id
            st.rerun()

    # Navigation Section 2: ADMINISTRATION
    st.sidebar.markdown('<div class="nav-section-title">ADMINISTRATION</div>', unsafe_allow_html=True)
    admin_items = [
        ("Users", "👥  Users"),
        ("Add Record", "➕  Add Record")
    ]
    for page_id, label in admin_items:
        is_active = (current_page == page_id)
        if st.sidebar.button(
            label,
            key=f"mgr_btn_{page_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state["manager_nav"] = page_id
            st.rerun()

    st.sidebar.divider()

    # User Profile Card at Sidebar Bottom
    user_display_name = st.session_state.get('user_name', 'Bhavani Prasad')
    user_role_str = str(st.session_state.get('user_role', 'manager')).title()

    st.sidebar.markdown(
        f'<div style="padding: 12px; background-color: #0B172A; border: 1px solid #1E293B; border-radius: 10px; margin-bottom: 12px;">'
        f'<div style="font-weight: 700; font-size: 13px; color: #F8FAFC;">{user_display_name}</div>'
        f'<div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">{user_role_str}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if st.sidebar.button("🚪 Logout", use_container_width=True, key="mgr_logout_btn"):
        st.session_state["authenticated"] = False
        st.session_state["user_role"] = None
        st.session_state["user_name"] = None
        st.session_state["username"] = None
        st.session_state.pop("manager_nav", None)
        st.rerun()

    # Router
    if current_page == "Dashboard":
        render_dashboard()
    elif current_page == "Executive KPIs":
        render_executive_kpi_dashboard()
    elif current_page == "Records":
        render_records()
    elif current_page == "Suppliers":
        render_suppliers()
    elif current_page == "Item Types":
        render_item_types()
    elif current_page == "Reports":
        render_reports()
    elif current_page == "Users":
        render_users()
    elif current_page == "Add Record":
        render_add_record()


def render_dashboard():
    """1. Manager Dashboard in Production-Ready Dark Navy Theme."""
    
    user_display_name = st.session_state.get('user_name', 'Bhavani Prasad')
    user_role_str = str(st.session_state.get('user_role', 'manager')).title()

    h_left, h_right = st.columns([3, 1])
    with h_left:
        st.markdown(
            '<div>'
            '<div style="font-size: 10px; font-weight: 800; color: #3B82F6; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 4px;">MANAGER / OVERVIEW</div>'
            '<h1 style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 0 0 4px 0;">Manager Dashboard</h1>'
            '<p style="font-size: 13px; color: #94A3B8; margin: 0;">Overview of retail records and performance metrics.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    with h_right:
        st.markdown(
            '<div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; background-color: #0B172A; border: 1px solid #1E293B; border-radius: 12px; padding: 8px 14px; margin-top: 6px;">'
            '<div style="width: 32px; height: 32px; border-radius: 50%; background-color: #101D31; color: #3B82F6; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">👤</div>'
            '<div>'
            f'<div style="font-size: 12px; font-weight: 700; color: #F8FAFC; line-height: 1.2;">{user_display_name}</div>'
            f'<div style="font-size: 10px; color: #94A3B8; font-weight: 500;">{user_role_str}</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.write("")

    metrics = fetch_dashboard_metrics()

    # 4 Compact Dark Navy KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(
            '<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">'
            '<div style="display: flex; justify-content: space-between; align-items: center;">'
            '<span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.5px;">TOTAL RECORDS</span>'
            '<div style="width: 28px; height: 28px; border-radius: 8px; background-color: rgba(37, 99, 235, 0.2); color: #60A5FA; display: flex; align-items: center; justify-content: center; font-size: 14px;">📄</div>'
            '</div>'
            f'<div style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 8px 0 4px 0;">{metrics["total_records"]:,}</div>'
            '<span style="background-color: rgba(37, 99, 235, 0.15); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 10px; display: inline-block;">Total entries</span>'
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
            '<span style="background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 10px; display: inline-block;">Distinct item codes</span>'
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
            '<span style="background-color: rgba(168, 85, 247, 0.15); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 10px; display: inline-block;">Active suppliers</span>'
            '</div>',
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            '<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">'
            '<div style="display: flex; justify-content: space-between; align-items: center;">'
            '<span style="font-size: 10px; font-weight: 800; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.5px;">ITEM TYPES</span>'
            '<div style="width: 28px; height: 28px; border-radius: 8px; background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; display: flex; align-items: center; justify-content: center; font-size: 14px;">🏷️</div>'
            '</div>'
            f'<div style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 8px 0 4px 0;">{metrics["total_item_types"]:,}</div>'
            '<span style="background-color: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 10px; display: inline-block;">Distinct categories</span>'
            '</div>',
            unsafe_allow_html=True
        )

    st.write("")

    # Section Header: Analytics
    st.markdown('<div style="font-size: 16px; font-weight: 700; color: #F8FAFC; margin: 8px 0 12px 0;">Analytics</div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns([2, 1.3])

    with chart_col1:
        st.markdown('<div style="font-size: 14px; font-weight: 700; color: #F8FAFC; margin-bottom: 8px;">Records Volume Over Time</div>', unsafe_allow_html=True)
        trend_df = fetch_monthly_records_trend()
        if not trend_df.empty:
            fig = px.line(trend_df, x="period", y="record_count", markers=True, line_shape="spline")
            fig.update_traces(line_color="#3B82F6", line_width=2.5, marker=dict(size=6, color="#60A5FA"))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#101D31",
                plot_bgcolor="#101D31",
                height=270,
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(color="#CBD5E1", family="Inter, sans-serif"),
                xaxis=dict(title=dict(text="Period", font=dict(color="#94A3B8", size=11)), tickfont=dict(color="#94A3B8", size=10), gridcolor="#1E293B"),
                yaxis=dict(title=dict(text="Records", font=dict(color="#94A3B8", size=11)), tickfont=dict(color="#94A3B8", size=10), gridcolor="#1E293B")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No record trend data available.")

    with chart_col2:
        st.markdown('<div style="font-size: 14px; font-weight: 700; color: #F8FAFC; margin-bottom: 8px;">Records by Item Type</div>', unsafe_allow_html=True)
        cat_summary = fetch_item_types_summary()
        if not cat_summary.empty:
            fig_donut = px.pie(
                cat_summary, names="Item Type", values="Record Count", hole=0.6,
                color_discrete_sequence=["#2563EB", "#38BDF8", "#F59E0B", "#EC4899", "#A855F7", "#10B981", "#64748B"]
            )
            fig_donut.update_layout(
                template="plotly_dark",
                paper_bgcolor="#101D31",
                plot_bgcolor="#101D31",
                height=270,
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(color="#CBD5E1", family="Inter, sans-serif"),
                legend=dict(font=dict(color="#CBD5E1", size=10), orientation="v")
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No item type data available.")

    st.write("")

    # Section Header: Data Insights
    st.markdown('<div style="font-size: 16px; font-weight: 700; color: #F8FAFC; margin: 8px 0 12px 0;">Data Insights</div>', unsafe_allow_html=True)

    w_col, m_col = st.columns(2)

    # TOP SUPPLIERS CARD
    with w_col:
        st.markdown('<div style="font-size: 14px; font-weight: 700; color: #F8FAFC; margin-bottom: 8px;">Top Suppliers</div>', unsafe_allow_html=True)
        sup_df = fetch_suppliers_summary(limit=5)
        if not sup_df.empty:
            rows_list = []
            for rank, (_, row) in enumerate(sup_df.iterrows(), start=1):
                s_name = row['Supplier Name']
                s_recs = row['Total Records']
                rows_list.append(
                    f'<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #1E293B;">'
                    f'<div style="display: flex; align-items: center; gap: 10px;">'
                    f'<span style="background-color: rgba(37, 99, 235, 0.2); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); font-size: 11px; font-weight: 800; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">#{rank}</span>'
                    f'<div style="font-weight: 600; color: #F8FAFC; font-size: 13px;">{s_name}</div>'
                    f'</div>'
                    f'<div style="color: #38BDF8; font-weight: 800; font-size: 12px;">{s_recs:,} records</div>'
                    f'</div>'
                )
            
            sup_card_html = (
                f'<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 16px 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">'
                f'{"".join(rows_list)}'
                f'</div>'
            )
            st.markdown(sup_card_html, unsafe_allow_html=True)
        else:
            st.info("No supplier data available.")

    # RECENT RECORDS CARD
    with m_col:
        st.markdown('<div style="font-size: 14px; font-weight: 700; color: #F8FAFC; margin-bottom: 8px;">Recent Records</div>', unsafe_allow_html=True)
        rec_df = fetch_recent_records(limit=5)
        if not rec_df.empty:
            rec_rows_list = []
            for _, row in rec_df.iterrows():
                desc = row.get("item_description", "Item Record")
                it_type = row.get("item_type", "General")
                code = row.get("item_code", "N/A")
                supplier_name = row.get("supplier", "Supplier")
                rec_rows_list.append(
                    f'<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #1E293B;">'
                    f'<div>'
                    f'<div style="font-weight: 700; color: #F8FAFC; font-size: 13px;">{code} - {desc[:28]}</div>'
                    f'<div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">Type: {it_type} • Year: {row.get("year", "")}</div>'
                    f'</div>'
                    f'<span style="background-color: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 10px; font-weight: 600; padding: 3px 8px; border-radius: 8px; white-space: nowrap;">{supplier_name[:16]}</span>'
                    f'</div>'
                )
            
            rec_card_html = (
                f'<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 16px 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">'
                f'{"".join(rec_rows_list)}'
                f'</div>'
            )
            st.markdown(rec_card_html, unsafe_allow_html=True)
        else:
            st.info("No recent database records.")


def render_records():
    """2. Records Screen in Dark Navy Theme with Production Column Formatting."""
    top1, top2 = st.columns([3, 1])
    with top1:
        st.title("Records")
        st.caption("Manage and explore retail sales records")
    with top2:
        if st.button("+ Add New Record", use_container_width=True, key="btn_add_rec_top"):
            st.session_state["manager_nav"] = "Add Record"
            st.rerun()

    # Track Pagination State in session_state
    if "rec_page" not in st.session_state:
        st.session_state["rec_page"] = 1
    if "rec_page_size" not in st.session_state:
        st.session_state["rec_page_size"] = 10

    # Interactive Search & Filter Toolbar
    f1, f2, f3, f4, f5 = st.columns([2.2, 1, 1, 1.2, 1])
    with f1:
        search_q = st.text_input("Search records...", placeholder="Search code, description, supplier...", label_visibility="collapsed", key="rec_search_input")
    with f2:
        year_sel = st.selectbox("Year", ["All Years", "2020", "2019", "2018", "2017"], label_visibility="collapsed", key="rec_year_select")
    with f3:
        month_sel = st.selectbox("Month", ["All Months"] + [str(m) for m in range(1, 13)], label_visibility="collapsed", key="rec_month_select")
    with f4:
        type_sel = st.selectbox("Item Type", ["All Item Types", "WINE", "BEER", "LIQUOR", "STR SUPPLIES", "REF", "DUNNAGE"], label_visibility="collapsed", key="rec_type_select")
    with f5:
        page_size_options = [10, 25, 50, 100]
        cur_size_idx = page_size_options.index(st.session_state["rec_page_size"]) if st.session_state["rec_page_size"] in page_size_options else 0
        page_size_sel = st.selectbox(
            "Page Size",
            page_size_options,
            index=cur_size_idx,
            label_visibility="collapsed",
            key="rec_page_size_select"
        )
        if page_size_sel != st.session_state["rec_page_size"]:
            st.session_state["rec_page_size"] = page_size_sel
            st.session_state["rec_page"] = 1
            st.rerun()

    page_size = st.session_state["rec_page_size"]
    current_page = st.session_state["rec_page"]

    # 1. Server-side Count Query
    total_matching = fetch_records_count(
        search_query=search_q,
        year_filter=year_sel,
        month_filter=month_sel,
        item_type_filter=type_sel
    )

    total_pages = max(1, math.ceil(total_matching / page_size))
    if current_page > total_pages:
        current_page = total_pages
        st.session_state["rec_page"] = total_pages

    # 2. Server-side Page Data Query
    r_df = fetch_records_page(
        search_query=search_q,
        year_filter=year_sel,
        month_filter=month_sel,
        item_type_filter=type_sel,
        page=current_page,
        page_size=page_size
    )

    start_row = ((current_page - 1) * page_size) + 1 if total_matching > 0 else 0
    end_row = min(current_page * page_size, total_matching)

    # Render Data Table WITHOUT record_id column & with Production SaaS column headers
    if not r_df.empty:
        display_df = r_df.drop(columns=["record_id"], errors="ignore").rename(columns={
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
        st.info("No matching records found for the selected search filters.")

    # Bottom Pagination Bar
    p_col1, p_col2, p_col3, p_col4 = st.columns([2, 1, 1.2, 1])
    with p_col1:
        st.markdown(f"<div style='font-size: 13px; color: #94A3B8; padding-top: 6px;'>Showing <b style='color: #F8FAFC;'>{start_row:,}–{end_row:,}</b> of <b style='color: #F8FAFC;'>{total_matching:,}</b> records</div>", unsafe_allow_html=True)
    with p_col2:
        if st.button("← Previous", disabled=(current_page <= 1), use_container_width=True, key="btn_prev_page"):
            st.session_state["rec_page"] = max(1, current_page - 1)
            st.rerun()
    with p_col3:
        st.markdown(f"<div style='text-align: center; font-weight: 700; color: #F8FAFC; font-size: 13px; padding-top: 6px;'>Page {current_page:,} of {total_pages:,}</div>", unsafe_allow_html=True)
    with p_col4:
        if st.button("Next →", disabled=(current_page >= total_pages), use_container_width=True, key="btn_next_page"):
            st.session_state["rec_page"] = min(total_pages, current_page + 1)
            st.rerun()

    st.divider()

    # On-demand CSV Export
    if st.button("📥 Export Current Filtered Results (CSV)", key="btn_export_csv_action"):
        export_df = fetch_records_page(
            search_query=search_q,
            year_filter=year_sel,
            month_filter=month_sel,
            item_type_filter=type_sel,
            page=1,
            page_size=50000
        )
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            "Click to Download CSV File",
            data=csv_data,
            file_name="records_export.csv",
            mime="text/csv",
            key="dl_btn_ready"
        )


def render_suppliers():
    """3. Suppliers Page."""
    st.title("Suppliers")
    st.caption("Explore supplier activity across your records")

    sup_df = fetch_suppliers_summary(limit=50)
    st.dataframe(sup_df, use_container_width=True)


def render_item_types():
    """4. Item Types Page."""
    st.title("Item Types")
    st.caption("Explore item categories and sales distribution")

    cat_df = fetch_item_types_summary()
    st.dataframe(cat_df, use_container_width=True)


def render_add_record():
    """Add Record Screen with 2-Column Dark SaaS Layout."""
    st.markdown(
        '<div>'
        '<div style="font-size: 10px; font-weight: 800; color: #3B82F6; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 4px;">MANAGER / NEW ENTRY</div>'
        '<h1 style="font-size: 26px; font-weight: 800; color: #F8FAFC; margin: 0 0 4px 0;">Add New Record</h1>'
        '<p style="font-size: 13px; color: #94A3B8; margin: 0;">Insert a new product record entry into the system.</p>'
        '</div>',
        unsafe_allow_html=True
    )
    st.write("")

    with st.form("add_record_form_db"):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div style="font-size: 13px; font-weight: 700; color: #3B82F6; margin-bottom: 12px;">📦 ITEM DETAILS</div>', unsafe_allow_html=True)
            item_code = st.text_input("Item Code *", placeholder="e.g. 100009")
            item_desc = st.text_input("Item Description *", placeholder="e.g. BOOTLEG RED - 750ML")
            supplier = st.text_input("Supplier Name *", placeholder="e.g. REPUBLIC NATIONAL DISTRIBUTING CO")
            item_type = st.selectbox("Item Type *", ["WINE", "BEER", "LIQUOR", "STR SUPPLIES", "REF", "DUNNAGE"])
        with col2:
            st.markdown('<div style="font-size: 13px; font-weight: 700; color: #34D399; margin-bottom: 12px;">📊 PERIOD & SALES ($)</div>', unsafe_allow_html=True)
            year = st.number_input("Year *", min_value=2017, max_value=2030, value=2026)
            month = st.number_input("Month *", min_value=1, max_value=12, value=8)
            retail_sales = st.number_input("Retail Sales ($)", min_value=0.0, value=150.0)
            warehouse_sales = st.number_input("Warehouse Sales ($)", min_value=0.0, value=300.0)

        st.write("")
        submitted = st.form_submit_button("➕ Save Record Entry", use_container_width=True)

        if submitted:
            if not item_code or not item_desc or not supplier:
                st.error("Please fill in all required fields marked with *.")
            else:
                success = add_product_record(
                    item_code=item_code,
                    item_description=item_desc,
                    supplier=supplier,
                    item_type=item_type,
                    retail_sales=retail_sales,
                    warehouse_sales=warehouse_sales,
                    year=int(year),
                    month=int(month)
                )
                if success:
                    st.success(f"✅ Record for **{item_desc}** ({item_code}) saved successfully!")
                else:
                    st.error("Error saving record.")


def render_reports():
    """5. Reports Page."""
    st.title("Reports & Analytics")
    st.caption("Downloadable report datasets for business analytics")

    r1, r2 = st.columns(2)
    with r1:
        st.markdown(
            '<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 12px; padding: 16px; margin-bottom: 12px;">'
            '<h4 style="font-size: 14px; font-weight: 700; color: #F8FAFC; margin-bottom: 4px;">📊 Sales & Records Export</h4>'
            '<p style="font-size: 11px; color: #94A3B8; margin-bottom: 10px;">Export product and transaction records for system analysis.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("Generate Records Export CSV", key="gen_rep_rec"):
            df_all = fetch_records_page(page=1, page_size=50000)
            csv_all = df_all.to_csv(index=False) if not df_all.empty else "No Data"
            st.download_button("📥 Download Records CSV", data=csv_all, file_name="sales_records_full.csv", mime="text/csv", use_container_width=True, key="dl_rep_records")

    with r2:
        st.markdown(
            '<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 12px; padding: 16px; margin-bottom: 12px;">'
            '<h4 style="font-size: 14px; font-weight: 700; color: #F8FAFC; margin-bottom: 4px;">🏬 Supplier Analytics Export</h4>'
            '<p style="font-size: 11px; color: #94A3B8; margin-bottom: 10px;">Aggregated sales and volume breakdown by supplier.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("Generate Supplier Report CSV", key="gen_rep_sup"):
            sup_df = fetch_suppliers_summary(limit=50)
            csv_sup = sup_df.to_csv(index=False) if not sup_df.empty else "No Data"
            st.download_button("📥 Download Supplier Report CSV", data=csv_sup, file_name="supplier_analytics.csv", mime="text/csv", use_container_width=True, key="dl_rep_supplier")


def render_users():
    """Users Screen (displaying system user accounts with Production column formatting)."""
    st.title("Registered System Accounts")
    st.caption("Registered system user accounts and roles")

    u_df = fetch_users_df()
    if not u_df.empty:
        display_users = u_df.rename(columns={
            "user_id": "User ID",
            "username": "Username",
            "full_name": "Full Name",
            "email": "Email Address",
            "role": "Account Role",
            "status": "Account Status",
            "created_at": "Date Joined"
        })
        st.dataframe(display_users, use_container_width=True)
    else:
        st.info("No registered users found.")
