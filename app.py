import streamlit as st
import pandas as pd

# Configure page layout
st.set_page_config(page_title="Analytics Dashboard", layout="wide")

# Task 1: Create Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Trends", "Data Explorer"]
)

# Task 5: Important Content Above the Fold
if page == "Overview":
    # Task 3: Visual Hierarchy - Page Title
    st.title("Business Overview")

    # Task 2 & 5: Top KPI row using st.columns (above the fold)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Revenue", "$5.2M", "+12.5%")
    with col2:
        st.metric("Users", "2,500", "+5.2%")
    with col3:
        st.metric("AOV", "$45", "+2.1%")
    with col4:
        st.metric("Churn", "5.2%", "-2.8%", delta_color="inverse")
    with col5:
        st.metric("NPS", "72", "+4")

    # Task 3: Dividers, Headers, and Subheaders
    st.divider()

    st.header("Executive Summary")
    st.subheader("Key Performance Highlights")

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write("• **Revenue Surge:** Enterprise subscriptions grew 18% YoY.")
        st.write("• **Customer Retention:** Churn reduced by 2.8% following onboarding updates.")
    with summary_col2:
        st.write("• **User Acquisition:** Active user base expanded past 2,500 accounts.")
        st.write("• **Customer Satisfaction:** NPS score reached an all-time high of 72.")

    st.divider()

    # Task 2: Progressive disclosure using st.expander
    with st.expander("About These Metrics"):
        st.write(
            "Revenue is calculated as sum of all order amounts for the current month. "
            "Churn is the percentage of customers who did not return within 30 days. "
            "AOV represents Average Order Value across all completed transactions."
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

    # Task 1 & Task 4: File Upload and Error Handling
    uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "json"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".json"):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            if len(df) == 0:
                st.warning("Uploaded file is empty.")
                st.stop()
        except Exception:
            st.error("Could not read this file. Check the format and try again.")
            st.stop()
            
        st.success(f"Loaded: {uploaded_file.name} ({len(df)} rows, {len(df.columns)} columns)")

        # Convert obvious date columns to datetime
        for c in df.columns:
            if 'date' in c.lower() or 'time' in c.lower():
                try:
                    df[c] = pd.to_datetime(df[c])
                except:
                    pass

        # Identify columns for filters dynamically
        date_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns.tolist()
        date_col = date_cols[0] if date_cols else None
        
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        cat_col = next((c for c in cat_cols if 'segment' in c.lower()), None) or \
                  next((c for c in cat_cols if 'region' in c.lower()), None) or \
                  (cat_cols[0] if cat_cols else None)

        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        num_col = next((c for c in num_cols if 'revenue' in c.lower()), None) or \
                  next((c for c in num_cols if 'amount' in c.lower()), None) or \
                  (num_cols[0] if num_cols else None)

        # Filters Sidebar
        st.sidebar.header("Filters")
        
        # Task 5: Implement Filter Reset
        if st.sidebar.button("Reset Filters"):
            st.rerun()

        filtered_df = df.copy()

        # Task 1 & 2 & 3: Widgets with Meaningful Defaults
        if date_col:
            min_date, max_date = filtered_df[date_col].min(), filtered_df[date_col].max()
            if pd.notnull(min_date) and pd.notnull(max_date):
                date_range = st.sidebar.date_input(
                    f"Date Range ({date_col})",
                    value=(min_date.date(), max_date.date())
                )
                if len(date_range) == 2:
                    filtered_df = filtered_df[
                        (filtered_df[date_col].dt.date >= date_range[0]) & 
                        (filtered_df[date_col].dt.date <= date_range[1])
                    ]

        if cat_col:
            all_segments = filtered_df[cat_col].dropna().unique().tolist()
            if all_segments:
                selected_segments = st.sidebar.multiselect(
                    f"Segments ({cat_col})", 
                    options=all_segments, 
                    default=all_segments
                )
                filtered_df = filtered_df[filtered_df[cat_col].isin(selected_segments)]

        if num_col:
            min_val, max_val = float(filtered_df[num_col].min()), float(filtered_df[num_col].max())
            if pd.notnull(min_val) and pd.notnull(max_val) and min_val < max_val:
                selected_range = st.sidebar.slider(
                    f"Value Range ({num_col})",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val)
                )
                filtered_df = filtered_df[
                    (filtered_df[num_col] >= selected_range[0]) & 
                    (filtered_df[num_col] <= selected_range[1])
                ]

        # Task 4: Handle Empty Filter Combinations
        if len(filtered_df) == 0:
            st.warning("No data matches the current filters. Try broadening your selection.")
            st.stop()

        st.divider()

        # Display Automatic Preview (wired to filtered_df)
        st.header("Dataset Preview")
        st.write(f"Showing **{len(filtered_df):,}** of **{len(df):,}** records")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{len(filtered_df):,}")
        with col2:
            st.metric("Columns", str(len(filtered_df.columns)))
        with col3:
            null_pct = (filtered_df.isnull().sum().sum() / (filtered_df.shape[0] * filtered_df.shape[1]) * 100) if not filtered_df.empty else 0
            st.metric("Null %", f"{null_pct:.1f}%")

        st.subheader("First 10 Rows")
        st.dataframe(filtered_df.head(10), use_container_width=True)

        st.subheader("Column Summary")
        summary = pd.DataFrame({
            "Column": filtered_df.columns,
            "Type": filtered_df.dtypes.astype(str).values,
            "Non-Null": filtered_df.notnull().sum().values,
            "Null Count": filtered_df.isnull().sum().values,
            "Null %": (filtered_df.isnull().sum() / len(filtered_df) * 100).round(1).values
        })
        st.dataframe(summary, use_container_width=True)

        st.divider()

        # Display Basic Statistics (wired to filtered_df)
        st.header("Descriptive Statistics")
        st.dataframe(filtered_df.describe(), use_container_width=True)

        st.divider()

        # Ensure Data Is Usable Downstream (Visualization, wired to filtered_df)
        st.header("Quick Exploration")
        numeric_cols_filt = filtered_df.select_dtypes(include="number").columns.tolist()
        if numeric_cols_filt:
            selected_col = st.selectbox("Select a numeric column to visualise distribution", numeric_cols_filt)
            st.bar_chart(filtered_df[selected_col].value_counts().head(20))
        else:
            st.info("No numeric columns available for visualization.")

    else:
        st.info("Upload a CSV or JSON file to begin.")
