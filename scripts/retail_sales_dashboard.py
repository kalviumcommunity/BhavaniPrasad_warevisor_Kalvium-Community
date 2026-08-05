from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from export_utils import export_analysis
from scripts.warehouse_retail_pipeline import (
    DEFAULT_CLEANED_OUTPUT,
    DEFAULT_REPORT_OUTPUT,
    build_schema_sql,
    prepare_retail_sales_dataset,
    write_schema_file,
)


@st.cache_data(show_spinner=True)
def load_dashboard_data() -> tuple[pd.DataFrame, dict]:
    """Load, clean, and cache the retail sales dataset for the dashboard."""
    return prepare_retail_sales_dataset(None, DEFAULT_CLEANED_OUTPUT, DEFAULT_REPORT_OUTPUT)


def _format_number(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value:,.0f}"
    return f"{value:,.2f}"


def _build_monthly_frame(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.assign(period=pd.to_datetime(dict(year=df["year"], month=df["month"], day=1)))
        .groupby("period", as_index=False)
        .agg(
            retail_sales=("retail_sales", "sum"),
            retail_transfers=("retail_transfers", "sum"),
            warehouse_sales=("warehouse_sales", "sum"),
        )
        .sort_values("period")
    )
    return monthly


def _build_summary_text(df: pd.DataFrame, report: dict) -> str:
    validation_checks = report.get("validation_checks", [])
    passed_checks = sum(1 for check in validation_checks if check["status"] == "passed")
    total_checks = len(validation_checks)

    return f"""## Warehouse and Retail Sales Cleaning Summary

- Rows loaded: {report.get('source_rows', len(df)):,}
- Rows after cleaning: {report.get('cleaned_rows', len(df)):,}
- Rows removed by deduplication: {report.get('rows_removed_by_deduplication', 0):,}
- Validation checks passed: {passed_checks}/{total_checks}
- Negative values flagged: {report.get('negative_value_counts', {})}

This dashboard now uses the cleaned warehouse retail dataset, with missing values imputed, exact duplicates removed, text fields normalized, and rule-based validation applied before analysis.
"""


def _apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    year_options = sorted(df["year"].dropna().astype(int).unique().tolist())
    selected_years = st.sidebar.multiselect("Year", year_options, default=year_options)

    item_type_options = ["All"] + sorted(df["item_type"].dropna().astype(str).unique().tolist())
    selected_item_type = st.sidebar.selectbox("Item Type", item_type_options)

    supplier_query = st.sidebar.text_input("Supplier contains", "")
    item_query = st.sidebar.text_input("Item description contains", "")

    filtered = df.copy()
    if selected_years:
        filtered = filtered[filtered["year"].isin(selected_years)]
    if selected_item_type != "All":
        filtered = filtered[filtered["item_type"] == selected_item_type]
    if supplier_query.strip():
        filtered = filtered[filtered["supplier"].str.contains(supplier_query.strip(), case=False, na=False)]
    if item_query.strip():
        filtered = filtered[filtered["item_description"].str.contains(item_query.strip(), case=False, na=False)]

    return filtered


def _build_trend_chart(df: pd.DataFrame) -> go.Figure:
    monthly = _build_monthly_frame(df)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["period"],
            y=monthly["retail_sales"],
            mode="lines+markers",
            name="Retail Sales",
            line=dict(color="#1f77b4", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["period"],
            y=monthly["retail_transfers"],
            mode="lines+markers",
            name="Retail Transfers",
            line=dict(color="#ff7f0e", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["period"],
            y=monthly["warehouse_sales"],
            mode="lines+markers",
            name="Warehouse Sales",
            line=dict(color="#2ca02c", width=2),
        )
    )
    fig.update_layout(
        title="Monthly Sales Movement",
        xaxis_title="Month",
        yaxis_title="Sales",
        hovermode="x unified",
        height=420,
        margin=dict(l=0, r=0, t=45, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig


def _build_supplier_chart(df: pd.DataFrame) -> go.Figure:
    supplier_frame = (
        df.groupby("supplier", as_index=False)
        .agg(warehouse_sales=("warehouse_sales", "sum"), retail_sales=("retail_sales", "sum"))
        .sort_values("warehouse_sales", ascending=False)
        .head(10)
        .sort_values("warehouse_sales", ascending=True)
    )

    fig = go.Figure(
        go.Bar(
            x=supplier_frame["warehouse_sales"],
            y=supplier_frame["supplier"],
            orientation="h",
            marker_color="#636efa",
            text=supplier_frame["warehouse_sales"].map(_format_number),
            textposition="outside",
            hovertemplate="%{y}<br>Warehouse Sales: %{x:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Top Suppliers by Warehouse Sales",
        xaxis_title="Warehouse Sales",
        yaxis_title="Supplier",
        height=500,
        margin=dict(l=0, r=0, t=45, b=0),
    )
    return fig


def _build_item_type_chart(df: pd.DataFrame) -> go.Figure:
    type_frame = (
        df.groupby("item_type", as_index=False)
        .agg(total_sales=("retail_sales", "sum"), warehouse_sales=("warehouse_sales", "sum"))
        .sort_values("total_sales", ascending=False)
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=type_frame["item_type"],
                values=type_frame["total_sales"],
                hole=0.45,
                textinfo="label+percent",
                marker=dict(line=dict(color="#ffffff", width=2)),
            )
        ]
    )
    fig.update_layout(title="Retail Sales Mix by Item Type", height=420, margin=dict(l=0, r=0, t=45, b=0))
    return fig


def main() -> None:
    st.set_page_config(layout="wide", page_title="Warehouse and Retail Sales Dashboard")
    st.title("Warehouse and Retail Sales Dashboard")
    st.caption("Cleaned retail sales data with missing-value imputation, deduplication, normalization, and validation.")

    cleaned_df, cleaning_report = load_dashboard_data()
    schema_path = write_schema_file()
    filtered_df = _apply_sidebar_filters(cleaned_df)

    validation_checks = cleaning_report.get("validation_checks", [])
    passed_checks = sum(1 for check in validation_checks if check["status"] == "passed")
    total_checks = max(len(validation_checks), 1)
    validation_rate = passed_checks / total_checks

    total_retail_sales = float(filtered_df["retail_sales"].sum()) if not filtered_df.empty else 0.0
    total_transfers = float(filtered_df["retail_transfers"].sum()) if not filtered_df.empty else 0.0
    total_warehouse_sales = float(filtered_df["warehouse_sales"].sum()) if not filtered_df.empty else 0.0
    top_supplier = filtered_df.groupby("supplier")["warehouse_sales"].sum().sort_values(ascending=False).index[0] if not filtered_df.empty else "N/A"

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Rows", f"{len(filtered_df):,}", delta=f"{len(filtered_df) - len(cleaned_df):,}")
    with col2:
        st.metric("Retail Sales", _format_number(total_retail_sales))
    with col3:
        st.metric("Warehouse Sales", _format_number(total_warehouse_sales))
    with col4:
        st.metric("Top Supplier", top_supplier)
    with col5:
        st.metric("Validation Pass Rate", f"{validation_rate:.0%}")

    st.divider()

    trend_chart = _build_trend_chart(filtered_df if not filtered_df.empty else cleaned_df)
    supplier_chart = _build_supplier_chart(filtered_df if not filtered_df.empty else cleaned_df)
    item_type_chart = _build_item_type_chart(filtered_df if not filtered_df.empty else cleaned_df)

    trend_col, supplier_col = st.columns([1.2, 1])
    with trend_col:
        st.plotly_chart(trend_chart, use_container_width=True)
    with supplier_col:
        st.plotly_chart(supplier_chart, use_container_width=True)

    st.plotly_chart(item_type_chart, use_container_width=True)

    st.divider()
    st.subheader("Data Explorer")
    st.write(f"Showing {len(filtered_df):,} rows from the cleaned dataset.")
    preview_columns = ["year", "month", "supplier", "item_code", "item_description", "item_type", "retail_sales", "retail_transfers", "warehouse_sales"]
    st.dataframe(filtered_df[preview_columns].head(2000), use_container_width=True, height=520)

    st.subheader("Cleaning Summary")
    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write("Missing values before cleaning")
        st.dataframe(pd.DataFrame(cleaning_report["missing_before"]), use_container_width=True)
        st.write("Missing values after cleaning")
        st.dataframe(pd.DataFrame(cleaning_report["missing_after"]), use_container_width=True)
    with summary_col2:
        st.write("Validation checks")
        st.dataframe(pd.DataFrame(validation_checks), use_container_width=True)
        st.write("Negative values flagged")
        st.json(cleaning_report.get("negative_value_counts", {}))

    st.sidebar.header("Export")
    summary_text = _build_summary_text(filtered_df, cleaning_report)
    charts = {
        "Monthly Sales Movement": trend_chart,
        "Top Suppliers": supplier_chart,
        "Item Type Mix": item_type_chart,
    }

    if st.sidebar.button("Export Analysis"):
        report_dir = export_analysis(filtered_df, summary_text, charts, "output")
        st.sidebar.success(f"Exported to {report_dir}")

    st.sidebar.download_button(
        label="Download Cleaned CSV",
        data=filtered_df.to_csv(index=False).encode(),
        file_name="warehouse_retail_sales_cleaned.csv",
        mime="text/csv",
    )
    st.sidebar.download_button(
        label="Download SQL Schema",
        data=build_schema_sql().encode(),
        file_name="warehouse_retail_sales_schema.sql",
        mime="text/sql",
    )
    st.sidebar.download_button(
        label="Download Cleaning Report",
        data=json.dumps(cleaning_report, indent=2, default=str).encode(),
        file_name="warehouse_retail_cleaning_report.json",
        mime="application/json",
    )

    st.sidebar.caption(f"Schema file saved at: {Path(schema_path)}")


if __name__ == "__main__":
    main()
