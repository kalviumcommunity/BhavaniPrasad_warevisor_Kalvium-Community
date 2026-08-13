import smtplib
import os
import pandas as pd
from datetime import date
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_report(df, report_date):
    """Generate structured text report from analysis output."""
    revenue = df["revenue"].sum()
    customers = df["customer_id"].nunique()
    avg_order = df["revenue"].mean()

    lines = []
    lines.append("WEEKLY ANALYTICS REPORT")
    lines.append("Date: " + str(report_date))
    lines.append("")
    lines.append("== KPI SUMMARY ==")
    lines.append("Total Revenue: $" + f"{revenue:,.0f}")
    lines.append("Active Customers: " + f"{customers:,}")
    lines.append("Average Order: $" + f"{avg_order:,.0f}")
    lines.append("")
    lines.append("== KEY FINDING ==")
    top_seg = df.groupby("segment")["revenue"].sum().idxmax()
    lines.append("Top segment: " + top_seg)
    lines.append("")
    lines.append("== RECOMMENDED ACTION ==")
    lines.append("Allocate resources to high-growth segments.")
    return "\n".join(lines)

def send_report(report_text, recipient):
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASSWORD")
    if not sender or not password:
        print("Email not configured. Skipping.")
        return False

    msg = MIMEText(report_text)
    msg["Subject"] = "Weekly Analytics Report"
    msg["From"] = sender
    msg["To"] = recipient

    try:
        server = smtplib.SMTP(os.environ.get("SMTP_SERVER", "smtp.gmail.com"), int(os.environ.get("SMTP_PORT", 587)))
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"Successfully sent report to {recipient}")
        return True
    except Exception as e:
        print("Send failed: " + str(e))
        return False

if __name__ == "__main__":
    # Test Data for validation
    print("Testing report generation...")
    data = {
        "customer_id": [1, 2, 3, 4, 1],
        "revenue": [100.0, 250.0, 50.0, 300.0, 150.0],
        "segment": ["High Value", "Mid Value", "Low Value", "High Value", "High Value"]
    }
    df = pd.DataFrame(data)
    
    report = generate_report(df, date.today())
    print("\nGenerated Report:\n")
    print(report)
    print("\n--------------------------\n")
    
    print("Testing email delivery with current credentials...")
    send_report(report, "test-recipient@example.com")
