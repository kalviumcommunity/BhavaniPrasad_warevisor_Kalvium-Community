import pandas as pd
import numpy as np

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

# Generate Revenue (Enterprise 70% of total revenue)
# Let's say total revenue is 1,000,000. 
# Enterprise = 700,000 (avg 14,000 per customer)
# Others = 300,000 (avg 315 per customer)
revenue = np.concatenate([
    np.random.normal(14000, 2000, n_enterprise),
    np.random.normal(400, 100, n_smb),
    np.random.normal(250, 50, n_startup)
])
revenue = np.maximum(revenue, 0) # Ensure no negative revenue

# Generate Products
products = np.concatenate([
    np.random.choice(['Premium', 'Enterprise Suite'], size=n_enterprise),
    np.random.choice(['Basic', 'Pro'], size=n_smb),
    np.random.choice(['Starter', 'Basic'], size=n_startup)
])

# Generate Support Tickets
support_tickets = np.concatenate([
    np.random.poisson(lam=5, size=n_enterprise),
    np.random.poisson(lam=3, size=n_smb),
    np.random.poisson(lam=2, size=n_startup)
])

# Create DataFrame
df = pd.DataFrame({
    'customer_id': customer_ids,
    'customer_type': customer_types,
    'churn': churn,
    'revenue': revenue,
    'product': products,
    'support_tickets': support_tickets
})

print("--- Mock Data Generated ---")
print(f"Overall Churn Rate: {df['churn'].mean():.2%}\n")

# --- USER ASSIGNMENT CODE START ---

# Task 1: Single-Level GroupBy with Multiple Aggregations (1 mark)
print("--- Task 1: Single-Level GroupBy ---")
segment_metrics = df.groupby('customer_type').agg({
    'churn': 'mean',
    'revenue': 'sum',
    'customer_id': 'count',
    'support_tickets': 'mean'
})

segment_metrics.columns = ['churn_rate', 'total_revenue', 'customer_count', 'avg_support_tickets']

print(segment_metrics)
print("\n")

# Task 2: Multi-Level GroupBy (1 mark)
print("--- Task 2: Multi-Level GroupBy ---")
# Two dimensions simultaneously
product_segment = df.groupby(['customer_type', 'product']).agg({
    'revenue': 'sum',
    'customer_id': 'count'
})

product_segment.columns = ['total_revenue', 'customer_count']

# Unstack for cleaner view
product_segment_pivot = product_segment.unstack()
print(product_segment_pivot)
print("\n")

# Task 3: Pivot Table (1 mark)
print("--- Task 3: Pivot Table ---")
# Two-dimensional view: customer_type rows, product columns
pivot = pd.pivot_table(
    df,
    values='revenue',
    index='customer_type',
    columns='product',
    aggfunc='sum'
)

print(pivot)
print("\n")

# Task 4: Rank and Identify Top/Bottom Performers (1 mark)
print("--- Task 4: Rank Performers ---")
# Rank segments by churn
segment_metrics['churn_rank'] = segment_metrics['churn_rate'].rank()

# Sort to see worst first
worst_first = segment_metrics.sort_values('churn_rate', ascending=False)
print(worst_first)

# Profit/revenue ranking
segment_metrics['revenue_contribution'] = (segment_metrics['total_revenue'] / segment_metrics['total_revenue'].sum() * 100)
print(segment_metrics[['revenue_contribution', 'churn_rate']])
print("\n")

# Task 5: Surface Actionable Segment Insights (1 mark)
print("--- Task 5: Surface Actionable Insights ---")
# Create insight summary
insights = []

for segment in segment_metrics.index:
    row = segment_metrics.loc[segment]
    
    insight = {
        'segment': segment,
        'customer_count': int(row['customer_count']),
        'churn_rate': f"{row['churn_rate']:.1%}",
        'total_revenue': f"${row['total_revenue']:.0f}",
        'revenue_contribution': f"{row['revenue_contribution']:.1f}%",
        'action': ''
    }
    
    # Action based on metrics
    if row['churn_rate'] > 0.10:
        insight['action'] = 'HIGH PRIORITY: Churn above 10%. Investigate pain points.'
    elif row['churn_rate'] < 0.02:
        insight['action'] = 'Healthy. Maintain current service level.'
    else:
        insight['action'] = 'Monitor. No immediate action needed.'
    
    insights.append(insight)

insights_df = pd.DataFrame(insights)
print(insights_df.to_string(index=False))
insights_df.to_csv('output/segment_insights.csv', index=False)
print("\nSaved insights to output/segment_insights.csv")
