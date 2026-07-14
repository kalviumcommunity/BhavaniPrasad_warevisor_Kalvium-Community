"""Validate incoming datasets before they enter the processing pipeline."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd # type: ignore

try:
    import chardet # type: ignore
except ImportError:  # pragma: no cover - dependency is optional at runtime
    chardet = None

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "data" / "raw" / "sample.csv"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "intake_report.json"
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
    sys.exit(0 if report["status"] == "passed" else 1)
