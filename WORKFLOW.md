# Data Workflow

## How to execute the script

Run the workflow from the repository root with:

```bash
python scripts/data_workflow.py
```

This command ingests the sample CSV file, processes the data, and writes the cleaned results to output/processed.csv.

## What each function does

- ingest_data(filepath): Reads the source file into a pandas DataFrame and returns it.
- process_data(df): Removes duplicates, fills missing numeric values, standardizes text, and adds a simple high-value flag.
- output_results(df, output_path): Saves the processed DataFrame to disk and prints a confirmation summary.

## How to modify it for new datasets

1. Replace the input path in the configuration constants at the top of scripts/data_workflow.py.
2. Ensure the new file has the required columns, or update the processing logic to match the new schema.
3. Re-run the script to generate a fresh output file.
