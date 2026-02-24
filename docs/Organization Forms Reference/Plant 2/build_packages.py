"""
Build Plant 2 AI Audit Packages A and B.

Package A: Line Operations & Process Control (8.2.2.1, 8.2.2.2, root-level 8.2.2.5-8.2.2.34)
Package B: Customer Inspection & Shipping (8.2.2.3, 8.2.2.4)
"""

import os
import sys
import csv
import json
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict

# Try to import Excel libraries
try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl not installed. Run: pip install openpyxl")
    sys.exit(1)
try:
    import xlrd
except ImportError:
    print("ERROR: xlrd not installed. Run: pip install xlrd")
    sys.exit(1)

# Paths
BASE = Path(r"c:/Dev/sf-quality/docs/Organization Forms Reference/Plant 2")
SOURCE = BASE / "Plant 2 Production Forms"
PKG_A = BASE / "Plant2_AI_Audit_Package_A"
PKG_B = BASE / "Plant2_AI_Audit_Package_B"

# Skip patterns
SKIP_PREFIXES = ("~$",)
SKIP_NAMES = ("Thumbs.db",)
SKIP_DIRS = ("Obsolete", "Review and Update")

# Classification: which top-level folders go to which package
PKG_A_FOLDERS = {"8.2.2.1 Line 101-103 Operating Forms", "8.2.2.2 Line 102 Operating Forms"}
PKG_B_FOLDERS = {"8.2.2.3 Production Forms by Customer", "8.2.2.4 Shipping Forms"}

# Form category classification for manifest
CATEGORIES = {
    "production_tracking": ["production tracking", "daily load sheet", "paint record", "load sheet", "tally sheet", "production report"],
    "process_control": ["temp log", "temperature", "oven verification", "paint mix", "batch verification", "recipe", "parameter", "pressure"],
    "scheduling": ["schedule template", "painter schedule", "painter line up", "daily painter"],
    "inspection": ["inspection", "gp12", "gp-12"],
    "maintenance": ["cleaning", "maintenance", "tpm", "filter change", "rack burn"],
    "defect_tracking": ["defect", "crash report", "fallout", "rejected", "hold tag", "hold for review", "rework"],
    "lab_chemistry": ["lab analysis", "basf", "pigment binder", "chemical addition", "solvent usage", "paint kitchen inventory"],
    "packaging_shipping": ["pack slip", "packslip", "shipping", "receiving log", "delivery performance", "monthly totals", "truck load", "tracker template"],
    "waste_management": ["waste", "booth sludge", "still bottoms", "empty"],
    "document_control": ["change tracker", "template", "programs"],
    "labels_tags": ["label", "tag", "certified", "use next", "sanded", "finished goods", "partial raw", "to be buffed", "to be sanded"],
    "post_paint": ["sanding", "buffing", "deburring", "buff inspection", "sander maintenance", "sanding booth"],
    "equipment": ["robot", "metering pump", "dustless sander"],
    "downtime": ["down time", "downtime"],
}


def should_skip(filepath):
    name = filepath.name
    if any(name.startswith(p) for p in SKIP_PREFIXES):
        return True
    if name in SKIP_NAMES:
        return True
    # Check if any parent directory is in SKIP_DIRS
    for part in filepath.parts:
        if part in SKIP_DIRS:
            return True
    return False


def classify_form(filename):
    """Classify a form by its filename into a category."""
    lower = filename.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in lower for kw in keywords):
            return cat
    return "other"


def get_file_extension(filepath):
    return filepath.suffix.lower()


def get_sheet_names(filepath):
    """Read worksheet/sheet names from an Excel file."""
    ext = filepath.suffix.lower()
    try:
        if ext in ('.xlsx', '.xlsm'):
            wb = openpyxl.load_workbook(str(filepath), read_only=True, data_only=True)
            names = wb.sheetnames
            wb.close()
            return names
        elif ext in ('.xls',):
            wb = xlrd.open_workbook(str(filepath))
            return wb.sheet_names()
    except Exception as e:
        return [f"ERROR: {str(e)[:80]}"]
    return []


def file_hash(filepath, block_size=65536):
    """MD5 hash for duplicate detection."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except Exception:
        return "error"


def assign_package(filepath):
    """Determine which package a file belongs to based on its relative path."""
    rel = filepath.relative_to(SOURCE)
    parts = rel.parts

    # Files directly in the root of "Plant 2 Production Forms/"
    if len(parts) == 1:
        return "A"  # Root-level forms go to Package A

    top_folder = parts[0]
    if top_folder in PKG_A_FOLDERS:
        return "A"
    elif top_folder in PKG_B_FOLDERS:
        return "B"
    else:
        return "A"  # Default to A for anything unmatched


def collect_forms():
    """Walk source and collect all non-skipped forms."""
    forms = {"A": [], "B": []}
    for filepath in sorted(SOURCE.rglob("*")):
        if not filepath.is_file():
            continue
        if should_skip(filepath):
            continue
        pkg = assign_package(filepath)
        forms[pkg].append(filepath)
    return forms


def copy_forms(forms, pkg_label, pkg_path):
    """Copy forms to package, preserving subfolder structure."""
    for filepath in forms:
        rel = filepath.relative_to(SOURCE)
        dest = pkg_path / "forms" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(filepath), str(dest))
    print(f"  Package {pkg_label}: copied {len(forms)} forms")


def build_forms_manifest(forms, pkg_path, source_base):
    """Generate forms_manifest.csv."""
    rows = []
    for filepath in forms:
        rel = filepath.relative_to(source_base)
        rel_in_pkg = filepath.relative_to(source_base)
        ext = get_file_extension(filepath)
        size_kb = round(filepath.stat().st_size / 1024, 1)
        category = classify_form(filepath.name)
        doc_number = filepath.stem.split(" ")[0] if filepath.stem[0].isdigit() else ""

        rows.append({
            "doc_number": doc_number,
            "filename": filepath.name,
            "relative_path": str(rel),
            "extension": ext,
            "size_kb": size_kb,
            "category": category,
            "has_macros": "yes" if ext == ".xlsm" else "no",
        })

    manifest_path = pkg_path / "ai_indexes" / "forms_manifest.csv"
    with open(manifest_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["doc_number", "filename", "relative_path", "extension", "size_kb", "category", "has_macros"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"  forms_manifest.csv: {len(rows)} entries")
    return rows


def build_sheet_index(forms, pkg_path):
    """Generate sheet_index.csv by reading all Excel workbook tabs."""
    rows = []
    excel_count = 0
    for filepath in forms:
        ext = get_file_extension(filepath)
        if ext not in ('.xlsx', '.xlsm', '.xls'):
            continue
        excel_count += 1
        sheets = get_sheet_names(filepath)
        for i, sheet_name in enumerate(sheets):
            rows.append({
                "filename": filepath.name,
                "sheet_index": i,
                "sheet_name": sheet_name,
            })

    index_path = pkg_path / "ai_indexes" / "sheet_index.csv"
    with open(index_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "sheet_index", "sheet_name"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"  sheet_index.csv: {len(rows)} sheets across {excel_count} workbooks")
    return rows


def build_duplicate_map(forms, pkg_path):
    """Identify potential duplicates by hash and by name similarity."""
    # Hash-based duplicates
    hash_groups = defaultdict(list)
    for filepath in forms:
        h = file_hash(filepath)
        hash_groups[h].append(filepath.name)

    # Name-based: strip version suffixes and compare
    name_groups = defaultdict(list)
    for filepath in forms:
        # Normalize: remove (v2), (Ver 2), -edit, etc.
        stem = filepath.stem
        for suffix in [" -edit", "-edit", " edit", "(v2)", "(v3)", "(Ver 2)", "(Ver 3)", "(Ver 4)"]:
            stem = stem.replace(suffix, "")
        stem = stem.strip()
        name_groups[stem].append(filepath.name)

    rows = []
    cluster_id = 0

    # Hash duplicates
    for h, files in hash_groups.items():
        if len(files) > 1:
            cluster_id += 1
            for fname in files:
                rows.append({
                    "cluster_id": cluster_id,
                    "detection_method": "hash_match",
                    "filename": fname,
                    "note": f"MD5: {h[:12]}..."
                })

    # Name duplicates (only if not already caught by hash)
    hash_dup_names = set()
    for files in hash_groups.values():
        if len(files) > 1:
            hash_dup_names.update(files)

    for stem, files in name_groups.items():
        if len(files) > 1:
            # Skip if all are already in hash duplicates
            new_files = [f for f in files if f not in hash_dup_names]
            if len(new_files) < len(files) and len(new_files) == 0:
                continue
            cluster_id += 1
            for fname in files:
                rows.append({
                    "cluster_id": cluster_id,
                    "detection_method": "name_similarity",
                    "filename": fname,
                    "note": f"Normalized stem: {stem}"
                })

    dup_path = pkg_path / "ai_indexes" / "duplicate_revision_map.csv"
    with open(dup_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["cluster_id", "detection_method", "filename", "note"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"  duplicate_revision_map.csv: {len(rows)} entries in {cluster_id} clusters")
    return rows


def build_batch_order(manifest_rows, pkg_path):
    """Create ingestion order prioritizing high-signal forms first."""
    priority = {
        "inspection": 1,
        "defect_tracking": 2,
        "process_control": 3,
        "production_tracking": 4,
        "lab_chemistry": 5,
        "maintenance": 6,
        "packaging_shipping": 7,
        "waste_management": 8,
        "post_paint": 9,
        "scheduling": 10,
        "labels_tags": 11,
        "equipment": 12,
        "document_control": 13,
        "downtime": 14,
        "other": 15,
    }

    sorted_rows = sorted(manifest_rows, key=lambda r: (priority.get(r["category"], 99), r["filename"]))

    rows = []
    for i, row in enumerate(sorted_rows, 1):
        rows.append({
            "batch_order": i,
            "filename": row["filename"],
            "category": row["category"],
            "size_kb": row["size_kb"],
        })

    batch_path = pkg_path / "ai_indexes" / "batch_order.csv"
    with open(batch_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["batch_order", "filename", "category", "size_kb"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"  batch_order.csv: {len(rows)} entries")


def build_package_manifest(forms, pkg_label, pkg_path, scope_desc):
    """Create package_manifest.json."""
    ext_counts = defaultdict(int)
    for f in forms:
        ext_counts[get_file_extension(f)] += 1

    manifest = {
        "package": f"Plant2_AI_Audit_Package_{pkg_label}",
        "plant": "Plant 2",
        "scope": scope_desc,
        "form_count": len(forms),
        "file_types": dict(ext_counts),
        "excluded": ["Obsolete/ subfolders", "Review and Update/ subfolders", "~$* temp files", "Thumbs.db"],
        "generated": "2026-02-24",
        "companion_package": f"Plant2_AI_Audit_Package_{'B' if pkg_label == 'A' else 'A'}",
    }

    manifest_path = pkg_path / "package_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f"  package_manifest.json written")


def main():
    print("=" * 60)
    print("Building Plant 2 AI Audit Packages")
    print("=" * 60)

    # Collect forms
    print("\n1. Collecting forms...")
    forms = collect_forms()
    print(f"   Package A: {len(forms['A'])} forms")
    print(f"   Package B: {len(forms['B'])} forms")
    print(f"   Total: {len(forms['A']) + len(forms['B'])} forms")

    # Copy forms
    print("\n2. Copying forms to packages...")
    copy_forms(forms["A"], "A", PKG_A)
    copy_forms(forms["B"], "B", PKG_B)

    # Build indexes for Package A
    print("\n3. Building Package A indexes...")
    manifest_a = build_forms_manifest(forms["A"], PKG_A, SOURCE)
    build_sheet_index(forms["A"], PKG_A)
    build_duplicate_map(forms["A"], PKG_A)
    build_batch_order(manifest_a, PKG_A)

    # Build indexes for Package B
    print("\n4. Building Package B indexes...")
    manifest_b = build_forms_manifest(forms["B"], PKG_B, SOURCE)
    build_sheet_index(forms["B"], PKG_B)
    build_duplicate_map(forms["B"], PKG_B)
    build_batch_order(manifest_b, PKG_B)

    # Package manifests
    print("\n5. Creating package manifests...")
    build_package_manifest(
        forms["A"], "A", PKG_A,
        "Line Operations & Process Control: 8.2.2.1 (Lines 101-103), 8.2.2.2 (Line 102), root-level forms (8.2.2.5-8.2.2.34)"
    )
    build_package_manifest(
        forms["B"], "B", PKG_B,
        "Customer Inspection & Shipping: 8.2.2.3 (Production Forms by Customer), 8.2.2.4 (Shipping Forms)"
    )

    print("\n" + "=" * 60)
    print("DONE. Next steps:")
    print("  - Copy ai_context/ files to both packages")
    print("  - Write README_AI_PACKAGE.md for each")
    print("  - Build the audit prompt (2 parts)")
    print("=" * 60)


if __name__ == "__main__":
    main()
