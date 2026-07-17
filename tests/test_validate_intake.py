import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_intake import (
    capture_dataset_stats,
    detect_encoding,
    generate_intake_report,
    validate_data_consistency,
    validate_file_exists,
    validate_file_format,
    validate_schema,
)


def test_validation_helpers_on_sample_csv():
    filepath = ROOT / "data" / "raw" / "sample.csv"

    file_exists, file_msg = validate_file_exists(filepath)
    assert file_exists is True
    assert "content" in file_msg

    format_valid, format_msg = validate_file_format(filepath)
    assert format_valid is True
    assert "csv" in format_msg

    import pandas as pd

    df = pd.read_csv(filepath)
    expected_columns = ["customer_id", "customer_name", "transaction_amount", "transaction_date"]
    schema_valid, schema_msg = validate_schema(df, expected_columns)
    assert schema_valid is False
    assert "Missing columns" in schema_msg

    encoding, encoding_msg = detect_encoding(filepath)
    assert encoding is not None
    assert "Detected" in encoding_msg

    stats = capture_dataset_stats(filepath, df)
    assert stats["rows"] == 7
    assert stats["columns"] == 5

    report = generate_intake_report(filepath, expected_columns)
    assert report["validations"]["file_exists"].startswith("File exists")
    assert report["validations"]["format"].startswith("Format valid")
    assert report["validations"]["schema"]
    assert report["statistics"]["rows"] == 7

    report_path = ROOT / "output" / "intake_report.json"
    assert report_path.exists()

    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    assert report_data["filepath"].endswith("data/raw/sample.csv")


def test_record_level_validation_rules_isolate_failures(tmp_path):
    import pandas as pd

    df = pd.DataFrame(
        [
            {
                "customer_id": 1,
                "age": 28,
                "price": 10.0,
                "birth_date": "1995-01-01",
                "email": "alice@example.com",
                "phone": "1234567890",
                "start_date": "2025-01-01",
                "end_date": "2025-01-10",
            },
            {
                "customer_id": None,
                "age": 200,
                "price": -5.0,
                "birth_date": "2050-01-01",
                "email": "invalid-email",
                "phone": "123",
                "start_date": "2025-02-10",
                "end_date": "2025-02-01",
            },
        ]
    )

    failures_path = tmp_path / "validation_failures.csv"
    report_path = tmp_path / "validation_report.json"

    result = validate_data_consistency(df, failures_output_path=failures_path, report_output_path=report_path)

    validated_df = result["validated_df"]
    failures = result["failures"]
    report = result["report"]

    assert "valid_age" in validated_df.columns
    assert "valid_price" in validated_df.columns
    assert "valid_birth_date" in validated_df.columns
    assert "valid_customer_id" in validated_df.columns
    assert "valid_email_format" in validated_df.columns
    assert "valid_phone" in validated_df.columns
    assert "valid_date_order" in validated_df.columns
    assert validated_df["passes_all_checks"].tolist() == [True, False]
    assert len(failures) == 1
    assert failures.iloc[0]["customer_id"] is None or pd.isna(failures.iloc[0]["customer_id"])
    assert failures_path.exists()
    assert report_path.exists()
    assert report["passed"] == 1
    assert report["failed"] == 1
    assert any(rule["rule"] == "valid_price" for rule in report["rule_summaries"])
