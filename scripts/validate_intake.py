"""Validate incoming datasets before they enter the processing pipeline."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd # type: ignore

try:
    import chardet # type: ignore
except ImportError:  # pragma: no cover - dependency is optional at runtime
    chardet = None

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "raw" / "sample.csv"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "intake_report.json"
DEFAULT_VALIDATION_OUTPUT = REPO_ROOT / "output" / "validation_report.json"
DEFAULT_FAILURES_OUTPUT = REPO_ROOT / "output" / "validation_failures.csv"
DEFAULT_EXPECTED_COLUMNS = [
    "customer_id",
    "customer_name",
    "transaction_amount",
    "transaction_date",
]


def _to_repo_relative_path(filepath: str | Path) -> str:
    """Return a workspace-relative path when possible."""
    path = Path(filepath)
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(path)


def validate_file_exists(filepath: str | Path) -> tuple[bool, str]:
    """Check if the file exists and is non-empty."""
    path = Path(filepath)
    if not path.exists():
        return False, f"File does not exist: {path}"

    if path.stat().st_size == 0:
        return False, f"File is empty: {path}"

    return True, "File exists and has content"


def validate_file_format(filepath: str | Path, allowed_formats: list[str] | None = None) -> tuple[bool, str]:
    """Check whether the file extension is supported."""
    if allowed_formats is None:
        allowed_formats = ["csv", "json", "xlsx"]

    extension = Path(filepath).suffix.lower().lstrip(".")
    if extension not in allowed_formats:
        return False, f"Unsupported format: {extension}. Allowed: {allowed_formats}"

    return True, f"Format valid: {extension}"


def validate_schema(df: pd.DataFrame, expected_columns: list[str]) -> tuple[bool, str]:
    """Validate that the DataFrame contains the required schema."""
    missing = sorted(set(expected_columns) - set(df.columns))
    extra = sorted(set(df.columns) - set(expected_columns))

    issues: list[str] = []
    if missing:
        issues.append(f"Missing columns: {missing}")
    if extra:
        issues.append(f"Unexpected columns: {extra}")

    if not issues:
        return True, f"Schema valid: {len(df.columns)} columns present"
    return False, " | ".join(issues)


def detect_encoding(filepath: str | Path) -> tuple[str, str]:
    """Detect file encoding with confidence."""
    path = Path(filepath)
    with path.open("rb") as handle:
        raw = handle.read(10000)

    if chardet is not None:
        result = chardet.detect(raw) or {}
        encoding = result.get("encoding") or "utf-8"
        confidence = result.get("confidence", 0) or 0.0
    else:
        encoding = "utf-8"
        confidence = 1.0

    return encoding, f"Detected: {encoding} (confidence: {confidence:.1%})"


def capture_dataset_stats(filepath: str | Path, df: pd.DataFrame) -> dict[str, Any]:
    """Capture row count and file size metrics."""
    path = Path(filepath)
    file_size_bytes = path.stat().st_size
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "file_size_mb": file_size_mb,
        "bytes": file_size_bytes,
    }


def _to_datetime_series(series: pd.Series) -> pd.Series:
    """Convert a series to datetime values while preserving missing values."""
    return pd.to_datetime(series, errors="coerce")


def _to_numeric_series(series: pd.Series) -> pd.Series:
    """Convert a series to numeric values while preserving missing values."""
    return pd.to_numeric(series, errors="coerce")


def _select_first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    """Return the first column from candidates that exists in the DataFrame."""
    for column in candidates:
        if column in df.columns:
            return column
    return None


def validate_data_consistency(
    df: pd.DataFrame,
    reference_values: dict[str, Iterable[Any]] | None = None,
    failures_output_path: str | Path = DEFAULT_FAILURES_OUTPUT,
    report_output_path: str | Path = DEFAULT_VALIDATION_OUTPUT,
) -> dict[str, Any]:
    """Apply record-level validation rules, isolate failures, and write a structured report."""
    working_df = df.copy()
    reference_values = reference_values or {}
    validation_columns: list[str] = []
    rule_summaries: list[dict[str, Any]] = []

    def add_rule(rule_name: str, mask: pd.Series | None, description: str, columns: list[str], skipped: bool = False) -> None:
        nonlocal working_df, validation_columns, rule_summaries

        if skipped or mask is None:
            rule_summaries.append(
                {
                    "rule": rule_name,
                    "description": description,
                    "columns": columns,
                    "status": "skipped",
                    "passed": 0,
                    "failed": 0,
                }
            )
            return

        mask = mask.fillna(False).astype(bool)
        working_df[rule_name] = mask
        validation_columns.append(rule_name)
        passed_count = int(mask.sum())
        failed_count = int((~mask).sum())
        rule_summaries.append(
            {
                "rule": rule_name,
                "description": description,
                "columns": columns,
                "status": "passed" if failed_count == 0 else "failed",
                "passed": passed_count,
                "failed": failed_count,
            }
        )

    age_column = _select_first_existing_column(working_df, ["age"])
    if age_column:
        age_values = _to_numeric_series(working_df[age_column])
        add_rule(
            "valid_age",
            age_values.between(0, 150, inclusive="both"),
            "Age must be between 0 and 150.",
            [age_column],
        )

    price_column = _select_first_existing_column(working_df, ["price", "transaction_amount", "amount", "revenue"])
    if price_column:
        price_values = _to_numeric_series(working_df[price_column])
        add_rule(
            "valid_price",
            price_values >= 0,
            "Price or amount must be non-negative.",
            [price_column],
        )

    birth_date_column = _select_first_existing_column(working_df, ["birth_date"])
    if birth_date_column:
        birth_dates = _to_datetime_series(working_df[birth_date_column])
        today = pd.Timestamp.now().normalize()
        add_rule(
            "valid_birth_date",
            birth_dates.between(pd.Timestamp("1920-01-01"), today, inclusive="both"),
            "Birth dates must be between 1920-01-01 and today.",
            [birth_date_column],
        )

    customer_id_column = _select_first_existing_column(working_df, ["customer_id"])
    if customer_id_column:
        add_rule(
            "valid_customer_id",
            working_df[customer_id_column].notna() & working_df[customer_id_column].astype(str).str.strip().ne(""),
            "Customer ID must be present.",
            [customer_id_column],
        )

    email_column = _select_first_existing_column(working_df, ["email"])
    if email_column:
        email_values = working_df[email_column].astype(str).str.strip()
        add_rule(
            "valid_email",
            working_df[email_column].notna() & email_values.ne(""),
            "Email must be present.",
            [email_column],
        )
        add_rule(
            "valid_email_format",
            working_df[email_column].notna() & email_values.str.contains(r"@", regex=True, na=False),
            "Email must contain @.",
            [email_column],
        )

    phone_column = _select_first_existing_column(working_df, ["phone"])
    if phone_column:
        phone_values = working_df[phone_column].astype(str).str.strip()
        add_rule(
            "valid_phone",
            working_df[phone_column].notna() & phone_values.str.match(r"^\d{10}$", na=False),
            "Phone must be exactly 10 digits.",
            [phone_column],
        )

    start_date_column = _select_first_existing_column(working_df, ["start_date", "campaign_start_date"])
    end_date_column = _select_first_existing_column(working_df, ["end_date", "campaign_end_date"])
    if start_date_column and end_date_column:
        start_dates = _to_datetime_series(working_df[start_date_column])
        end_dates = _to_datetime_series(working_df[end_date_column])
        add_rule(
            "valid_date_order",
            start_dates.notna() & end_dates.notna() & (end_dates >= start_dates),
            "End date must be on or after start date.",
            [start_date_column, end_date_column],
        )

    referential_column = _select_first_existing_column(working_df, list(reference_values.keys()))
    if referential_column:
        allowed_values = set(reference_values[referential_column])
        add_rule(
            "valid_referential_integrity",
            working_df[referential_column].isin(allowed_values),
            "Referenced values must exist in the allowed lookup set.",
            [referential_column],
        )

    if validation_columns:
        working_df["passes_all_checks"] = working_df[validation_columns].all(axis=1)
    else:
        working_df["passes_all_checks"] = True

    failures = working_df[~working_df["passes_all_checks"]].copy()

    failures_path = Path(failures_output_path)
    failures_path.parent.mkdir(parents=True, exist_ok=True)
    failures.to_csv(failures_path, index=False)

    report = {
        "timestamp": datetime.now().isoformat(),
        "rows": len(working_df),
        "passed": int(working_df["passes_all_checks"].sum()),
        "failed": int((~working_df["passes_all_checks"]).sum()),
        "validation_columns": validation_columns,
        "rule_summaries": rule_summaries,
        "failures_output": _to_repo_relative_path(failures_path),
        "report_output": _to_repo_relative_path(report_output_path),
    }

    report_path = Path(report_output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    working_df.attrs["validation_report"] = report
    working_df.attrs["validation_failures"] = failures

    return {
        "validated_df": working_df,
        "failures": failures,
        "report": report,
    }


def write_report(report: dict[str, Any], output_path: str | Path) -> None:
    """Persist the validation report to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")


def generate_intake_report(
    filepath: str | Path,
    expected_columns: list[str] | None = None,
    output_path: str | Path = DEFAULT_OUTPUT,
    allowed_formats: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a complete intake validation report."""
    path = Path(filepath)
    expected_columns = expected_columns or DEFAULT_EXPECTED_COLUMNS

    report: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "filepath": _to_repo_relative_path(path),
        "validations": {},
        "validation_statuses": {},
        "status": "passed",
    }

    file_exists, file_message = validate_file_exists(path)
    report["validations"]["file_exists"] = file_message
    report["validation_statuses"]["file_exists"] = "passed" if file_exists else "failed"
    if not file_exists:
        report["status"] = "failed"
        write_report(report, output_path)
        return report

    format_valid, format_message = validate_file_format(path, allowed_formats)
    report["validations"]["format"] = format_message
    report["validation_statuses"]["format"] = "passed" if format_valid else "failed"
    if not format_valid:
        report["status"] = "failed"
        write_report(report, output_path)
        return report

    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        elif path.suffix.lower() == ".json":
            df = pd.read_json(path)
        else:
            df = pd.read_excel(path)
    except Exception as exc:  # pragma: no cover - defensive CLI handling
        report["validations"]["dataset_load"] = f"Unable to load dataset: {exc}"
        report["validation_statuses"]["dataset_load"] = "failed"
        report["status"] = "failed"
        write_report(report, output_path)
        return report

    schema_valid, schema_message = validate_schema(df, expected_columns)
    report["validations"]["schema"] = schema_message
    report["validation_statuses"]["schema"] = "passed" if schema_valid else "failed"
    if not schema_valid:
        report["status"] = "failed"

    encoding, encoding_message = detect_encoding(path)
    report["validations"]["encoding"] = encoding_message
    report["validation_statuses"]["encoding"] = "passed" if encoding else "failed"

    report["statistics"] = capture_dataset_stats(path, df)
    write_report(report, output_path)
    return report


if __name__ == "__main__":
    report = generate_intake_report(DEFAULT_INPUT, DEFAULT_EXPECTED_COLUMNS)
    print(json.dumps(report, indent=2))

    if report["status"] == "passed":
        if DEFAULT_INPUT.suffix.lower() == ".csv":
            dataset = pd.read_csv(DEFAULT_INPUT)
        elif DEFAULT_INPUT.suffix.lower() == ".json":
            dataset = pd.read_json(DEFAULT_INPUT)
        else:
            dataset = pd.read_excel(DEFAULT_INPUT)

        validation_result = validate_data_consistency(dataset)
        print(json.dumps(validation_result["report"], indent=2, default=str))

    sys.exit(0 if report["status"] == "passed" else 1)
