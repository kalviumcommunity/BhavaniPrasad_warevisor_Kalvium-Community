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
    
    print("--- Testing Ingestion Functions ---")
    
    # 1. Test Standard CSV
    print("\n1. Testing ingest_csv with standard comma file:")
    csv_path = os.path.join(base_dir, "sample_data.csv")
    df_csv = ingest_csv(csv_path)
    document_ingestion(df_csv, "sample_data.csv")
    
    # 2. Test Semicolon CSV
    print("\n2. Testing ingest_csv with semicolon file:")
    semi_path = os.path.join(base_dir, "semicolon_data.csv")
    df_semi = ingest_csv(semi_path, delimiter=";")
    document_ingestion(df_semi, "semicolon_data.csv")
    
    # 3. Test Nested JSON
    print("\n3. Testing ingest_json with nested data:")
    json_path = os.path.join(base_dir, "nested_data.json")
    df_json = ingest_json(json_path, is_nested=True)
    document_ingestion(df_json, "nested_data.json")
    
    # 4. Test Fallback CSV
    print("\n4. Testing ingest_csv_with_fallback:")
    df_fallback = ingest_csv_with_fallback(csv_path)
    document_ingestion(df_fallback, "sample_data.csv (fallback method)")
    
    print("\nAll tests passed successfully!")
