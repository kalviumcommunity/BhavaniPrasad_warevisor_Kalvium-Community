import time
import numpy as np
import pandas as pd

def generate_mock_data(num_rows=1_000_000):
    """Generate a large dataset with a revenue column."""
    print(f"Generating mock data with {num_rows:,} rows...")
    np.random.seed(42)
    # Generate revenues between 100 and 100,000
    revenues = np.random.uniform(100.0, 100000.0, size=num_rows)
    return pd.DataFrame({'revenue': revenues})

def main():
    # Pre-requisite: Generate 1M row dataset
    df = generate_mock_data(1_000_000)
    print("-" * 50)
    
    # Task 1: Replace Loop with NumPy Vectorization
    print("Executing Task 1: Replace Loop with NumPy Vectorization")
    
    # SLOW: Loop
    normalized_loop = []
    # Note: min/max computed outside loop to avoid O(n^2) behavior, simulating typical loop logic
    min_rev = df['revenue'].min()
    max_rev = df['revenue'].max()
    for val in df['revenue']:
        normalized_loop.append((val - min_rev) / (max_rev - min_rev))
        
    # FAST: NumPy
    revenue_array = df['revenue'].values
    normalized_np = (revenue_array - revenue_array.min()) / (revenue_array.max() - revenue_array.min())
    
    print("-" * 50)
    
    # Task 2: Z-Score Normalization
    print("Executing Task 2: Z-Score Normalization")
    revenue_array = df['revenue'].values
    z_scores = (revenue_array - revenue_array.mean()) / revenue_array.std()
    
    print("-" * 50)
    
    # Task 3: Bulk Ranking/Scoring
    print("Executing Task 3: Bulk Ranking/Scoring")
    # Rank all customers by revenue
    revenue_array = df['revenue'].values
    rankings = np.argsort(-revenue_array)  # Negative for descending
    
    # Fixed pandas assignment to avoid SettingWithCopyWarning
    ranks = np.empty_like(rankings)
    ranks[rankings] = np.arange(1, len(rankings) + 1)
    
    print("-" * 50)
    
    # Task 4: Time Performance Comparison
    print("Executing Task 4: Time Performance Comparison")
    
    # Time loop version
    start = time.time()
    result_loop = []
    for val in df['revenue']:
        result_loop.append(val * 1.1)
    loop_time = time.time() - start

    # Time NumPy version
    start = time.time()
    result_np = df['revenue'].values * 1.1
    np_time = time.time() - start

    print(f"Loop: {loop_time:.4f}s")
    print(f"NumPy: {np_time:.4f}s")
    print(f"Speedup: {loop_time/np_time:.0f}x")
    
    print("-" * 50)
    
    # Task 5: Integrate Back to DataFrame
    print("Executing Task 5: Integrate Back to DataFrame")
    # All NumPy results go back to DataFrame as new columns
    df['revenue_normalized'] = normalized_np
    df['revenue_zscore'] = z_scores
    # Using the ranks calculated in Task 3
    df['revenue_rank'] = ranks

    # Verify types and shapes
    print(f"Shape: {df.shape}")
    print(f"Dtypes:\n{df.dtypes}")
    
    print("\nSample Output (First 5 rows):")
    print(df.head())

if __name__ == '__main__':
    main()
