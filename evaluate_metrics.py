import pandas as pd
from sqlalchemy import create_engine

# Set up your database connection here
# engine = create_engine('postgresql://username:password@localhost:5432/your_database')
engine = create_engine('sqlite:///data/assignment.db') # Note: The SQL files use Postgres syntax, so you will need a Postgres engine to run them successfully.

def load_query(query_name):
    """Load SQL query from file."""
    with open(f'queries/{query_name}.sql', 'r') as f:
        return f.read()

# Load and execute
mau_query = load_query('monthly_active_users')
mau = pd.read_sql(mau_query, engine)
print("Monthly Active Users:")
print(mau)

revenue_query = load_query('revenue_by_segment')
revenue = pd.read_sql(revenue_query, engine)
print("\nRevenue by Segment:")
print(revenue)

funnel_query = load_query('conversion_funnel')
funnel = pd.read_sql(funnel_query, engine)
print("\nConversion Funnel:")
print(funnel)

def validate_metrics(mau_df, revenue_df, funnel_df):
    """Validate metric computation."""
    
    # Check for nulls
    assert mau_df.isnull().sum().sum() == 0, "MAU has nulls"
    assert revenue_df.isnull().sum().sum() == 0, "Revenue has nulls"
    
    # Check value ranges
    assert (revenue_df['monthly_revenue'] > 0).all(), "Revenue <= 0"
    assert (funnel_df['conversion_pct'] >= 0).all() and (funnel_df['conversion_pct'] <= 100).all(), "Conversion out of range"
    
    # Check consistency
    for idx, row in revenue_df.iterrows():
        assert row['order_count'] > 0, "Zero orders"
        assert row['monthly_revenue'] > 0, "Zero revenue"
    
    print("[OK] All metrics validated")
    return True

# Validate
validate_metrics(mau, revenue, funnel)
