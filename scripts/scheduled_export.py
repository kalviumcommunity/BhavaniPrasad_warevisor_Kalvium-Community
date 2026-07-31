import schedule
import time
import pandas as pd
from datetime import datetime
import sys
import os

# Ensure the parent directory is in the sys.path so we can import export_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from export_utils import export_analysis

def run_analysis():
    # Mock generating the analysis DataFrame
    print("Running analysis...")
    df = pd.DataFrame({
        'customer_id': [f'CUST-{i:04d}' for i in range(1, 100)],
        'segment': ['Enterprise'] * 50 + ['SMB'] * 49,
        'revenue': range(500, 14900, 100),
    })
    # Add a date column for metadata
    df['date'] = pd.date_range(start='2024-01-01', periods=len(df))
    return df

def generate_summary(df):
    return "## Analysis Report\nKey findings: Enterprise segment represents the majority of our high-value accounts."

def generate_charts(df):
    import plotly.express as px
    fig_revenue = px.histogram(df, x='revenue', title="Revenue Distribution")
    return {'Revenue Trend': fig_revenue}

def scheduled_export():
    """Run export on schedule."""
    df = run_analysis()  
    summary = generate_summary(df)
    charts = generate_charts(df)
    
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))
    os.makedirs(output_dir, exist_ok=True)
    report_dir = export_analysis(df, summary, charts, output_dir)
    print(f"[{datetime.now()}] Export complete: {report_dir}")

if __name__ == "__main__":
    print(f"[{datetime.now()}] Starting scheduled export service. Job runs daily at 17:00.")
    # Schedule to run daily at 5pm
    schedule.every().day.at("17:00").do(scheduled_export)
    
    # Run once immediately for demonstration (optional)
    # scheduled_export()

    while True:
        schedule.run_pending()
        time.sleep(60)
