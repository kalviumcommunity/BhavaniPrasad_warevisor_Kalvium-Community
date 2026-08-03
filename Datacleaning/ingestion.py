import pandas as pd
import json

def ingest_csv(filepath, delimiter=',', encoding='utf-8'):
    """Load CSV with explicit parameters."""
    try:
        df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
        return df
    except UnicodeDecodeError:
        print(f"Cannot decode with {encoding}. Try: latin-1, iso-8859-1, cp1252")
        raise

def ingest_json(filepath, is_nested=False):
    """Load JSON, optionally flattening nested structures."""
    if is_nested:
        # pd.json_normalize expects a dict or list of dicts
        with open(filepath, 'r') as f:
            data = json.load(f)
        df = pd.json_normalize(data)
        print("[OK] Flattened nested JSON")
    else:
        df = pd.read_json(filepath)
    return df

def ingest_csv_with_fallback(filepath):
    """Load CSV trying multiple encodings if the primary fails."""
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    for enc in encodings:
        try:
            return pd.read_csv(filepath, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not load file with any encoding")

def document_ingestion(df, source):
    """Create a permanent record of what was loaded."""
    print(f"\nINGESTION REPORT: {source}")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    print(f"\nColumn Types:")
    print(df.dtypes)
    print(f"\nFirst 3 rows:")
    print(df.head(3))
    print("-" * 40)

if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    warehouse_csv = os.path.join(base_dir, "..", "data", "raw", "Warehouse_and_Retail_Sales.csv")
    
    print("--- Testing Ingestion Functions ---")
    
    # 1. Test standard CSV ingestion using the warehouse sales dataset.
    print("\n1. Testing ingest_csv with warehouse sales file:")
    df_csv = ingest_csv(warehouse_csv)
    document_ingestion(df_csv, "Warehouse_and_Retail_Sales.csv")

    # 2. Test fallback CSV ingestion against the same warehouse sales dataset.
    print("\n2. Testing ingest_csv_with_fallback with warehouse sales file:")
    df_fallback = ingest_csv_with_fallback(warehouse_csv)
    document_ingestion(df_fallback, "Warehouse_and_Retail_Sales.csv (fallback method)")
    
    print("\nAll tests passed successfully!")
