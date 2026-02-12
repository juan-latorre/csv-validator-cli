from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .validator import validate_csv


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="csv-validator",
        description="Validate a CSV file and compute basic stats (age average).",
    )
    p.add_argument("file", type=Path, help="Path to the CSV file")
    p.add_argument(
        "--columns",
        default="id,nombre,edad,ciudad",
        help="Comma-separated expected columns (default: id,nombre,edad,ciudad)",
    )
    p.add_argument(
        "--age-col",
        default="edad",
        help="Age column name (default: edad)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    expected = {c.strip() for c in args.columns.split(",") if c.strip()}

    try:
        result = validate_csv(args.file, expected_columns=expected, age_column=args.age_col)
    except Exception as ex:
        print(f"❌ Error: {ex}", file=sys.stderr)
        return 2

    print(f"✅ Encoding used: {result.encoding_used}")
    print(f"📄 Rows: {result.total_rows}")

    if result.errors:
        print("\nErrors found:")
        for e in result.errors:
            print(f" - {e}")
        return 1

    print(f"📊 Avg {args.age_col}: {result.avg_age:.1f}")
    print("✔️ No errors found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
