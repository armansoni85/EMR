#!/usr/bin/env python3
"""
import_codes.py

Standalone script to import ICD-10 and CPT codes from CSV files into the Django database.

Usage:
    # From your project’s root directory:
    python import_codes.py --icd_csv path/to/ValidICD10-Jan2024.csv \
                           --cpt_csv path/to/ValidCPT-Jan2024.csv
"""

import os
import sys
import csv
import argparse

# 1) Configure Django environment
# ────────────────────────────────────────────────────────────────────────────
# Adjust 'myproject.settings' to point at your settings module (replace accordingly).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emr.base_settings")
import django

django.setup()  # Now Django ORM is ready to use

# 2) Import your models
# ────────────────────────────────────────────────────────────────────────────
from superbills.models import ICDCode, CPTCode  # adjust if your app/model path differs


def import_icd_codes(csv_path):
    """
    Read the given CSV file of ICD-10 codes and insert them into the ICDCode model.
    Expected CSV columns (tab-delimited or comma-delimited):
      CODE    SHORT DESCRIPTION (VALID ICD-10 FY2024)    LONG DESCRIPTION (VALID ICD-10 FY2024)
    Only 'CODE' and one of the description fields are needed; we’ll load 'CODE' + LONG DESCRIPTION.
    """
    inserted = 0
    updated = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        # Detect delimiter: if it’s tab-delimited, use '\t'; else default to comma
        sample = f.read(1024)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters="\t,")
        reader = csv.DictReader(f, dialect=dialect)

        for row in reader:
            code = row.get("CODE") or row.get("Code") or row.get("code")
            long_desc = (
                row.get("LONG DESCRIPTION (VALID ICD-10 FY2024)")
                or row.get("Long Description")
                or row.get("long_description")
                or ""
            )
            if not code:
                continue

            obj, created = ICDCode.objects.update_or_create(
                code=code.strip(),
                defaults={"description": long_desc.strip()},
            )
            if created:
                inserted += 1
            else:
                updated += 1

    print(f"ICD: Inserted {inserted:,}, Updated {updated:,} entries.")


def import_cpt_codes(csv_path):
    """
    Read the given CSV file of CPT codes and insert them into the CPTCode model.
    You can adapt column names as needed, but typical CSV might have:
      CODE,CPT SHORT DESCRIPTION,CPT LONG DESCRIPTION
    We’ll read 'CODE' + LONG DESCRIPTION similarly.
    """
    inserted = 0
    updated = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        sample = f.read(1024)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters="\t,")
        reader = csv.DictReader(f, dialect=dialect)

        for row in reader:
            code = row.get("CODE") or row.get("Code") or row.get("code")
            long_desc = (
                row.get("LONG DESCRIPTION") or row.get("Long Description") or ""
            )
            if not code:
                continue

            obj, created = CPTCode.objects.update_or_create(
                code=code.strip(),
                defaults={"description": long_desc.strip()},
            )
            if created:
                inserted += 1
            else:
                updated += 1

    print(f"CPT: Inserted {inserted:,}, Updated {updated:,} entries.")


def main():
    parser = argparse.ArgumentParser(
        description="Import ICD-10 and/or CPT codes from CSV into Django models."
    )
    parser.add_argument(
        "--icd_csv",
        help="Path to your ICD-10 CSV file (e.g. ValidICD10-Jan2024.csv).",
        required=False,
    )
    parser.add_argument(
        "--cpt_csv",
        help="Path to your CPT CSV file (e.g. ValidCPT-Jan2024.csv).",
        required=False,
    )

    args = parser.parse_args()

    if not args.icd_csv and not args.cpt_csv:
        parser.error("At least one of --icd_csv or --cpt_csv must be provided.")

    if args.icd_csv:
        csv_path = os.path.abspath(args.icd_csv)
        if not os.path.exists(csv_path):
            print(f"ERROR: ICD CSV not found at: {csv_path}")
            sys.exit(1)
        print(f"Importing ICD codes from {csv_path} …")
        import_icd_codes(csv_path)

    if args.cpt_csv:
        csv_path = os.path.abspath(args.cpt_csv)
        if not os.path.exists(csv_path):
            print(f"ERROR: CPT CSV not found at: {csv_path}")
            sys.exit(1)
        print(f"Importing CPT codes from {csv_path} …")
        import_cpt_codes(csv_path)


if __name__ == "__main__":
    main()

