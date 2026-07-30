import os
import sqlite3
import pandas as pd
import plotly.graph_objects as go

# Ensure output directory exists
os.makedirs("interactive_charts", exist_ok=True)
DB_PATH = "database/data_layer.db"

def get_db_connection():
    if os.path.exists(DB_PATH):
        return sqlite3.connect(DB_PATH)
    return None

def build_chart1():
    """Task 1 - Chart 1: Daily Revenue Trend with Custom Hover"""
    conn = get_db_connection()
    if conn:
        df = pd.read_sql("""
            SELECT DATE(order_date) as date, SUM(order_amount) as revenue, COUNT(*) as order_count
            FROM orders
            GROUP BY DATE(order_date)
            ORDER BY DATE(order_date)
        """, conn)
        conn.close()
    else:
        # Fallback dummy data if DB not accessible
        dates = pd.date_range(start="2026-01-01", periods=30, freq="D")
        revenue = [12000 + i*300 + (i%5)*1500 for i in range(30)]
        order_count = [15 + (i%7)*4 for i in range(30)]
        df = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "revenue": revenue, "order_count": order_count})

    fig = go.Figure(data=go.Scatter(
        x=df['date'],
        y=df['revenue'],
        mode='lines+markers',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>' +
                      'Revenue: $%{y:,.2f}<br>' +
                      '<extra></extra>',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8, color='#1f77b4')
    ))

    fig.update_layout(
        title='Daily Revenue Trend',
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        height=500,
        template='plotly_white',
        margin=dict(l=60, r=40, t=60, b=60)
    )

    output_path = 'interactive_charts/chart1_revenue_trend.html'
    fig.write_html(output_path)
    print(f"Chart 1 saved to {output_path}")

def build_chart2():
    """Task 1 - Chart 2: Product Performance with Multi-Column Hover"""
    conn = get_db_connection()
    if conn:
        df = pd.read_sql("""
            SELECT p.product_name, 
                   SUM(oi.quantity * oi.unit_price) as revenue,
                   COUNT(DISTINCT oi.order_id) as order_count,
                   AVG(oi.quantity * oi.unit_price) as avg_order_value
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_id, p.product_name
            ORDER BY revenue DESC
            LIMIT 10
        """, conn)
        conn.close()
    else:
        df = pd.DataFrame({
            "product_name": ["Product A", "Product B", "Product C", "Product D", "Product E"],
            "revenue": [120000, 95000, 75000, 50000, 35000],
            "order_count": [2500, 1800, 1500, 1000, 700],
            "avg_order_value": [48.00, 52.78, 50.00, 50.00, 50.00]
        })

    fig = go.Figure(data=go.Bar(
        x=df['product_name'],
        y=df['revenue'],
        customdata=list(zip(df['order_count'], df['avg_order_value'])),
        hovertemplate='<b>%{x}</b><br>' +
                      'Revenue: $%{y:,.2f}<br>' +
                      'Orders: %{customdata[0]:,}<br>' +
                      'Avg Order Value: $%{customdata[1]:,.2f}<br>' +
                      '<extra></extra>',
        marker=dict(
            color=df['revenue'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Revenue ($)")
        )
    ))

    fig.update_layout(
        title='Product Performance (Revenue & Order Metrics)',
        xaxis_title='Product Name',
        yaxis_title='Revenue ($)',
        height=500,
        template='plotly_white',
        margin=dict(l=60, r=40, t=60, b=120),
        xaxis=dict(tickangle=-30)
    )

    output_path = 'interactive_charts/chart2_product_performance.html'
    fig.write_html(output_path)
    print(f"Chart 2 saved to {output_path}")

def build_chart3():
    """Task 2: Create Dropdown Filter to Toggle Views"""
    conn = get_db_connection()
    if conn:
        df = pd.read_sql("""
            SELECT p.product_name, 
                   SUM(oi.quantity * oi.unit_price) as revenue,
                   SUM(oi.quantity * oi.unit_price * 0.35) as profit,
                   COUNT(DISTINCT oi.order_id) as order_count
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_id, p.product_name
            ORDER BY revenue DESC
            LIMIT 8
        """, conn)
        conn.close()
        products = df['product_name'].tolist()
        revenue_data = df['revenue'].tolist()
        profit_data = df['profit'].tolist()
        order_count = df['order_count'].tolist()
    else:
        products = ['Product A', 'Product B', 'Product C', 'Product D']
        revenue_data = [50000, 75000, 120000, 45000]
        profit_data = [15000, 22000, 35000, 10000]
        order_count = [1000, 1500, 2500, 800]

    fig = go.Figure()

    # Add all 3 traces, initially hidden except the first (Revenue)
    fig.add_trace(go.Bar(
        x=products,
        y=revenue_data,
        name='Revenue',
        marker=dict(color='#1f77b4'),
        visible=True,
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=products,
        y=profit_data,
        name='Profit',
        marker=dict(color='#ff7f0e'),
        visible=False,
        hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=products,
        y=order_count,
        name='Order Count',
        marker=dict(color='#2ca02c'),
        visible=False,
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
    ))

    # Add updatemenus dropdown
    fig.update_layout(
        updatemenus=[dict(
            active=0,
            x=0.0,
            xanchor='left',
            y=1.15,
            yanchor='top',
            buttons=[
                dict(label='Revenue', method='update',
                     args=[{'visible': [True, False, False]},
                           {'title': 'Revenue by Product', 'yaxis.title': 'Revenue ($)'}]),
                dict(label='Profit', method='update',
                     args=[{'visible': [False, True, False]},
                           {'title': 'Profit by Product', 'yaxis.title': 'Profit ($)'}]),
                dict(label='Order Count', method='update',
                     args=[{'visible': [False, False, True]},
                           {'title': 'Order Count by Product', 'yaxis.title': 'Orders'}])
            ]
        )],
        title='Product Performance Metric Selector',
        xaxis_title='Product',
        yaxis_title='Revenue ($)',
        height=500,
        template='plotly_white',
        margin=dict(l=60, r=40, t=80, b=100),
        xaxis=dict(tickangle=-25)
    )

    output_path = 'interactive_charts/chart3_metric_selector.html'
    fig.write_html(output_path)
    print(f"Chart 3 saved to {output_path}")

def build_chart4():
    """Task 3: Enable Zoom, Pan, and Reset Interactions"""
    conn = get_db_connection()
    if conn:
        df = pd.read_sql("""
            SELECT o.order_id, o.order_date, o.order_amount, o.customer_id,
                   COUNT(oi.item_id) as total_items,
                   SUM(oi.quantity) as total_quantity
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id
            LIMIT 500
        """, conn)
        conn.close()
        x_vals = df['total_quantity']
        y_vals = df['order_amount']
        hover_text = [
            f"Order ID: {row['order_id']}<br>Date: {row['order_date']}<br>Customer: {row['customer_id']}<br>Amount: ${row['order_amount']:,.2f}<br>Qty: {row['total_quantity']}"
            for _, row in df.iterrows()
        ]
    else:
        import numpy as np
        np.random.seed(42)
        x_vals = np.random.randint(1, 50, 100)
        y_vals = x_vals * np.random.uniform(20, 100, 100)
        hover_text = [f"Item {i}: Qty={x_vals[i]}, Amount=${y_vals[i]:,.2f}" for i in range(100)]

    fig = go.Figure(data=go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers',
        text=hover_text,
        hovertemplate='%{text}<extra></extra>',
        marker=dict(
            size=12,
            color=y_vals,
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title="Order Amount ($)"),
            opacity=0.8,
            line=dict(width=1, color='DarkSlateGrey')
        )
    ))

    fig.update_layout(
        title='Order Value vs. Quantity Purchased (Interactive Zoom & Pan)',
        xaxis_title='Total Quantity Purchased',
        yaxis_title='Order Amount ($)',
        dragmode='zoom',  # Options: 'zoom', 'pan', 'select', 'lasso'
        hovermode='closest',
        height=600,
        template='plotly_white'
    )

    output_path = 'interactive_charts/chart4_interactive.html'
    fig.write_html(output_path)
    print(f"Chart 4 saved to {output_path}")

if __name__ == '__main__':
    build_chart1()
    build_chart2()
    build_chart3()
    build_chart4()
