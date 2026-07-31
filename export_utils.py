import os
from datetime import datetime
import pandas as pd
import markdown

def markdown_to_html(text):
    return markdown.markdown(text)

def export_analysis(df, summary_text, charts_dict, output_dir):
    """
    Export analysis in three formats: CSV, PDF, HTML.
    
    Args:
        df: Cleaned DataFrame with analysis results
        summary_text: Executive summary as markdown string
        charts_dict: Dict of {chart_name: plotly_figure}
        output_dir: Directory to save outputs
    """
    
    # Create timestamped output folder
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    report_dir = f"{output_dir}/{timestamp}_analysis"
    os.makedirs(report_dir, exist_ok=True)
    
    # 1. Export cleaned CSV
    csv_path = f"{report_dir}/cleaned_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ CSV exported: {csv_path}")
    
    # 2. Export PDF summary
    try:
        # Convert markdown to HTML, then to PDF
        pdf_path = f"{report_dir}/summary_report.pdf"
        html_content = markdown_to_html(summary_text)
        
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(pdf_path)
        print(f"✓ PDF exported: {pdf_path}")
    except Exception as e:
        print(f"✗ PDF export failed: {e}")
    
    # 3. Export HTML with embedded charts
    html_path = f"{report_dir}/interactive_report.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analysis Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .chart-container {{ margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>Analysis Report</h1>
        <div class="summary">{markdown_to_html(summary_text)}</div>
    """
    
    # Embed all charts
    for chart_name, fig in charts_dict.items():
        html_content += f"""
        <div class="chart-container">
            <h2>{chart_name}</h2>
            {fig.to_html(include_plotlyjs='cdn', div_id=chart_name)}
        </div>
        """
    
    html_content += "</body></html>"
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✓ HTML exported: {html_path}")
    
    # 4. Create metadata file
    metadata = {
        'Generated': datetime.now().isoformat(),
        'Records': len(df),
        'Columns': list(df.columns),
        'Data Range': f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else "N/A"
    }
    
    metadata_path = f"{report_dir}/README.md"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write("# Analysis Report\n\n")
        for key, value in metadata.items():
            f.write(f"- **{key}:** {value}\n")
    
    print(f"✓ Metadata created: {metadata_path}")
    
    return report_dir


def verify_exports(report_dir):
    """Verify all export files are present and readable."""
    
    required_files = ['cleaned_data.csv', 'summary_report.pdf', 'interactive_report.html', 'README.md']
    
    for filename in required_files:
        filepath = f"{report_dir}/{filename}"
        
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✓ {filename}: {file_size} bytes")
        else:
            print(f"✗ {filename}: MISSING")
    
    # Test CSV is readable
    try:
        df_test = pd.read_csv(f"{report_dir}/cleaned_data.csv")
        print(f"✓ CSV readable: {len(df_test)} rows, {len(df_test.columns)} columns")
    except Exception as e:
        print(f"✗ CSV read failed: {e}")
    
    # Test HTML opens in browser
    html_path = f"{report_dir}/interactive_report.html"
    print(f"\\nOpen in browser: file://{os.path.abspath(html_path)}")
