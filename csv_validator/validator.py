from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from typing import Any


DEFAULT_ENCODINGS: tuple[str, ...] = ("utf-8", "utf-8-sig", "cp1252")


@dataclass(frozen=True)
class ValidationResult:
    total_rows: int
    avg_age: float | None
    errors: list[str]
    encoding_used: str


def read_csv_rows(path: Path, encodings: Iterable[str] = DEFAULT_ENCODINGS) -> tuple[list[dict[str, str]], str]:
    last_error: Exception | None = None
    for enc in encodings:
        try:
            with path.open(newline="", encoding=enc) as f:
                reader = csv.DictReader(f)
                return list(reader), enc
        except UnicodeDecodeError as ex:
            last_error = ex
            continue

    raise ValueError(f"Could not decode file using encodings: {tuple(encodings)}") from last_error


def validate_file_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")


def validate_columns(rows: list[dict[str, str]], expected_columns: set[str]) -> None:
    if not rows:
        raise ValueError("CSV has no rows")

    columns = set(rows[0].keys())
    missing = expected_columns - columns
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")


def validate_rows(rows: list[dict[str | None, Any]], age_column: str = "edad") -> list[str]:
    errors: list[str] = []

    for i, row in enumerate(rows, start=1):
        # Overflow: more values than headers
        if None in row and row[None]:
            errors.append(f"Row {i}: Too many columns (extra data: {row[None]})")
            continue

        # Underflow: fewer values than headers (DictReader fills missing with None)
        if any(v is None for k, v in row.items() if k is not None):
            errors.append(f"Row {i}: Missing columns")
            continue

        # Validate age
        value = (row.get(age_column) or "").strip()
        try:
            int(value)
        except ValueError:
            errors.append(f"Row {i}: invalid {age_column} -> {value!r}")

    return errors



def compute_summary(rows: list[dict[str, str]], age_column: str = "edad") -> tuple[int, float]:
    ages = [int((r.get(age_column) or "").strip()) for r in rows]
    total = len(rows)
    avg = sum(ages) / total
    return total, avg


def validate_csv(
    file_path: Path,
    expected_columns: set[str],
    age_column: str = "edad",
) -> ValidationResult:
    validate_file_exists(file_path)
    rows, enc = read_csv_rows(file_path)

    validate_columns(rows, expected_columns)
    errors = validate_rows(rows, age_column=age_column)

    if errors:
        return ValidationResult(
            total_rows=len(rows),
            avg_age=None,
            errors=errors,
            encoding_used=enc,
        )

    total, avg = compute_summary(rows, age_column=age_column)
    return ValidationResult(
        total_rows=total,
        avg_age=avg,
        errors=[],
        encoding_used=enc,
    )
