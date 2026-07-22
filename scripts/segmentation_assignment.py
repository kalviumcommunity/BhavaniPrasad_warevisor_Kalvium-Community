import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Generate Mock Data
np.random.seed(42)

# Total customers
total_customers = 1000

# Segment base percentages
n_enterprise = int(total_customers * 0.05)
n_smb = int(total_customers * 0.40)
n_startup = int(total_customers * 0.55)

# Generate IDs
customer_ids = np.arange(1, total_customers + 1)

# Generate Customer Types
customer_types = (['Enterprise'] * n_enterprise + 
                  ['SMB'] * n_smb + 
                  ['Startup'] * n_startup)

# Generate Churn (Enterprise 1%, SMB 12%, Startup 8%)
churn = np.concatenate([
    np.random.choice([0, 1], size=n_enterprise, p=[0.99, 0.01]),
    np.random.choice([0, 1], size=n_smb, p=[0.88, 0.12]),
    np.random.choice([0, 1], size=n_startup, p=[0.92, 0.08])
])

# Generate Lifetime Value
lifetime_value = np.concatenate([
    np.random.normal(150000, 20000, n_enterprise), # 150k
    np.random.normal(8000, 1000, n_smb),          # 8k
    np.random.normal(2000, 500, n_startup)         # 2k
])
lifetime_value = np.maximum(lifetime_value, 0)

# Generate Support Tickets
support_tickets = np.concatenate([
    np.random.poisson(lam=5, size=n_enterprise),
    np.random.poisson(lam=3, size=n_smb),
    np.random.poisson(lam=2, size=n_startup)
])

# Generate Retention Days
retention_days = np.concatenate([
    np.random.normal(1500, 200, n_enterprise),
    np.random.normal(800, 100, n_smb),
    np.random.normal(300, 50, n_startup)
])
retention_days = np.maximum(retention_days, 1)

# Create DataFrame
df = pd.DataFrame({
    'customer_id': customer_ids,
    'customer_type': customer_types,
    'churn': churn,
    'lifetime_value': lifetime_value,
    'support_tickets': support_tickets,
    'retention_days': retention_days
})

print("--- Mock Data Generated ---")
print(f"Overall Churn Rate: {df['churn'].mean():.2%}\n")

# Make sure output dir exists
os.makedirs('output', exist_ok=True)

# Task 1: Define Segments and Compute Metrics (1 mark)
print("--- Task 1: Segment Metrics ---")
segment_metrics = df.groupby('customer_type').agg({
    'lifetime_value': 'mean',
    'churn': 'mean',
    'support_tickets': 'mean',
    'retention_days': 'mean',
    'customer_id': 'count'
})

segment_metrics.columns = ['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention', 'count']
print(segment_metrics)
print("\n")

# Task 2: Summary Statistics Table (1 mark)
print("--- Task 2: Summary Statistics Table ---")
segment_summary = segment_metrics.copy()
segment_summary['ltv_rank'] = segment_summary['avg_ltv'].rank(ascending=False)
segment_summary['churn_rank'] = segment_summary['churn_rate'].rank(ascending=True)

print(segment_summary[['avg_ltv', 'ltv_rank', 'churn_rate', 'churn_rank']])
print("\n")

# Task 3: Visual Comparison (1 mark)
print("--- Task 3: Visual Comparison (Heatmap) ---")
# Heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(segment_metrics[['avg_ltv', 'churn_rate', 'avg_tickets']], 
            annot=True, cmap='RdYlGn', cbar_kws={'label': 'Value'})
plt.title('Segment Comparison Heatmap')
plt.tight_layout()
plt.savefig('output/segment_heatmap.png')
print("Saved heatmap to output/segment_heatmap.png")
print("\n")

# Task 4: Top and Bottom Performer Analysis (1 mark)
print("--- Task 4: Top and Bottom Performer Analysis ---")
# Highest value segment
top_segment = segment_metrics['avg_ltv'].idxmax()
top_value = segment_metrics.loc[top_segment, 'avg_ltv']

# Highest churn segment
high_churn = segment_metrics['churn_rate'].idxmax()

insights = f"""
HIGHEST VALUE: {top_segment} = ${top_value:,.0f}
HIGHEST CHURN: {high_churn} = {segment_metrics.loc[high_churn, 'churn_rate']:.1%}
BEST RETENTION: {segment_metrics['avg_retention'].idxmax()}
"""

print(insights.strip())
print("\n")

# Task 5: Business-Facing Insights (1 mark)
print("--- Task 5: Business-Facing Insights ---")
business_summary = """
SEGMENT STRATEGY SUMMARY:

Enterprise (5% of base, $150k LTV, 1% churn):
- Highest value, lowest churn
- Action: Maintain premium support, retention focus

SMB (40% of base, $8k LTV, 12% churn):
- Middle value, high churn risk
- Action: Improve onboarding, cheaper support tier

Startup (55% of base, $2k LTV, 8% churn):
- Lowest value, moderate churn
- Action: Self-service, education-focused
"""

print(business_summary.strip())
