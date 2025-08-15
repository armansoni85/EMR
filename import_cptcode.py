#!/usr/bin/env python3
"""
insert_cpt_codes.py

Standalone script to insert CPT codes from Internal Medicine/Family Practice PDF into Django database.
"""

import os
import sys

# Configure Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emr.base_settings")
import django
django.setup()

# Import your CPT model
from superbills.models import CPTCode  # adjust if your app/model path differs

def insert_cpt_codes():
    """
    Insert all CPT codes from the Internal Medicine/Family Practice PDF into the database.
    """
    # List of CPT codes and their descriptions from the PDF
    cpt_codes = [
        ("99202", "Office visit, new patient, 15-29 min"),
        ("99203", "Office visit, new patient, 30-44 min"),
        ("99204", "Office visit, new patient, 45-59 min"),
        ("99205", "Office visit, new patient, 60+ min"),
        ("99211", "Office visit, established patient, minimal"),
        ("99212", "Office visit, established patient, 10-19 min"),
        ("99213", "Office visit, established patient, 20-29 min"),
        ("99214", "Office visit, established patient, 30-39 min"),
        ("99215", "Office visit, established patient, 40-54 min"),
        ("99381", "Initial preventive exam, new patient <1 year"),
        ("99382", "Initial preventive exam, new patient 1-4 years"),
        ("99383", "Initial preventive exam, new patient 5-11 years"),
        ("99384", "Initial preventive exam, new patient 12-17 years"),
        ("99385", "Initial preventive exam, new patient 18-39 years"),
        ("99386", "Initial preventive exam, new patient 40-64 years"),
        ("99387", "Initial preventive exam, new patient 65+ years"),
        ("99391", "Periodic preventive exam, established <1 year"),
        ("99392", "Periodic preventive exam, established 1-4 years"),
        ("99393", "Periodic preventive exam, established 5-11 years"),
        ("99394", "Periodic preventive exam, established 12-17 years"),
        ("99395", "Periodic preventive exam, established 18-39 years"),
        ("99396", "Periodic preventive exam, established 40-64 years"),
        ("99397", "Periodic preventive exam, established 65+ years"),
        ("99406", "Smoking cessation counseling, 3-10 min"),
        ("99407", "Smoking cessation counseling, >10 min"),
        ("99495", "Transitional care mgmt, moderate complexity"),
        ("99496", "Transitional care mgmt, high complexity"),
        ("G0438", "Medicare Annual Wellness Visit, initial"),
        ("G0439", "Medicare Annual Wellness Visit, subsequent"),
        ("99490", "Chronic care management, 20+ min/month"),
        ("99491", "Chronic care management by physician, 30+ min/month"),
    ]

    inserted = 0
    updated = 0

    for code, description in cpt_codes:
        # Use update_or_create to avoid duplicates
        obj, created = CPTCode.objects.update_or_create(
            code=code.strip(),
            defaults={'description': description.strip()}
        )
        if created:
            inserted += 1
        else:
            updated += 1

    print(f"CPT codes inserted: {inserted}")
    print(f"CPT codes updated: {updated}")
    print(f"Total CPT codes processed: {inserted + updated}")

if __name__ == "__main__":
    print("Starting CPT code import...")
    insert_cpt_codes()
    print("CPT code import completed!")
