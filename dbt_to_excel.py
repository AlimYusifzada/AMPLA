#!/usr/bin/env python3
"""
dbt_to_excel.py

Searches directories recursively for *.dbt files (space-separated text),
creates an Excel spreadsheet, and populates each .dbt file's data into its
own tab (worksheet) named after the file.
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    openpyxl = None


def sanitize_sheet_name(name: str, existing_names: set) -> str:
    """
    Sanitizes sheet name according to Excel restrictions:
    - Maximum 31 characters.
    - Cannot contain: \\ / ? * : [ ]
    - Must be unique within the workbook.
    """
    # Remove prohibited characters
    cleaned = re.sub(r"[\\/*?:\[\]]", "_", name)
    # Trim to 31 chars
    cleaned = cleaned[:31].strip() or "Sheet"

    # Ensure uniqueness
    candidate = cleaned
    counter = 1
    while candidate.lower() in existing_names:
        suffix = f"_{counter}"
        candidate = f"{cleaned[:31 - len(suffix)]}{suffix}"
        counter += 1

    existing_names.add(candidate.lower())
    return candidate


def parse_value(val: str):
    """Attempts to cast strings to int or float; falls back to str."""
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val


def process_dbt_files(search_dir: Path, output_file: Path, convert_numbers: bool = True):
    if openpyxl is None:
        print("Error: 'openpyxl' is required. Install it using: pip install openpyxl", file=sys.stderr)
        sys.exit(1)

    # Find all *.dbt files recursively
    dbt_files = sorted(search_dir.rglob("*.dbt"))

    if not dbt_files:
        print(f"No .dbt files found in '{search_dir}'.")
        return

    print(f"Found {len(dbt_files)} .dbt file(s) in '{search_dir}'. Processing...")

    # Use write_only mode to reduce memory overhead and speed up large workbook creation.
    wb = openpyxl.Workbook(write_only=True)
    existing_sheet_names = set()
    sheets_created = 0

    for file_path in dbt_files:
        # Base tab name on the file name without extension
        raw_name = file_path.stem
        sheet_title = sanitize_sheet_name(raw_name, existing_sheet_names)

        ws = wb.create_sheet(title=sheet_title)
        sheets_created += 1

        row_count = 0
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    tokens = line.split()
                    if not tokens:
                        continue

                    row_data = [parse_value(t) for t in tokens] if convert_numbers else tokens
                    ws.append(row_data)
                    row_count += 1

            print(f"  [+] Tab '{sheet_title}' <- {file_path.name} ({row_count} rows)")
        except Exception as e:
            print(f"  [!] Failed to read {file_path}: {e}", file=sys.stderr)

    # Save spreadsheet
    output_file.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_file)
    print(f"\nDone! Successfully created '{output_file}' with {sheets_created} tab(s).")


def main():
    parser = argparse.ArgumentParser(
        description="Search directories for *.dbt files and consolidate into an Excel workbook with one tab per file."
    )
    parser.add_argument(
        "-d", "--dir",
        type=str,
        default=".",
        help="Root directory to search for *.dbt files (default: current directory)."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="dbt_summary.xlsx",
        help="Path to output Excel file (default: dbt_summary.xlsx)."
    )
    parser.add_argument(
        "--raw-text",
        action="store_true",
        help="Do not auto-convert numeric values to int/float (keep everything as text)."
    )

    args = parser.parse_args()
    search_path = Path(args.dir).resolve()
    output_path = Path(args.output).resolve()

    process_dbt_files(
        search_dir=search_path,
        output_file=output_path,
        convert_numbers=not args.raw_text
    )

if __name__ == "__main__":
    main()
