"""Verify all prompt references exist in the zip package."""
import zipfile

z = zipfile.ZipFile(r"c:\Dev\sf-quality\docs\Organization Forms Reference\Plant 2\Plant2_AI_Audit_Package.zip")
files_in_zip = set(f.replace("\\", "/") for f in z.namelist() if not f.endswith("/"))

# Paths referenced in the prompt that MUST exist in the zip
required = [
    "ai_indexes/forms_manifest.csv",
    "ai_indexes/sheet_index.csv",
    "ai_indexes/duplicate_revision_map.csv",
    "ai_indexes/batch_order.csv",
    "ai_context/lookup_codes.csv",
    "ai_context/api_surface_summary.csv",
    "ai_context/defect_taxonomy_reference_l1_l2.csv",
    "ai_context/defect_taxonomy_mapping_template.csv",
    "ai_context/cross_plant_checklist_template.csv",
    "ai_context/plant1_baseline.md",
    "ai_context/architecture_snapshot.md",
    "ai_context/evidence_rules.md",
    "ai_context/glossary.md",
    "ai_context/output_template.md",
    "README_AI_PACKAGE.md",
    "package_manifest.json",
]

# Specific forms referenced by name in the prompt
form_refs = [
    ("8.2.2.2.7", "102 Line Operating Form.xlsm"),
    ("8.2.2.28", "Down time Tracking Template"),
    ("8.2.2.30", "Buffing Summary Template"),
]

print("=== Required context/index files ===")
all_ok = True
for r in required:
    status = "OK" if r in files_in_zip else "MISSING"
    if status == "MISSING":
        all_ok = False
    print(f"  [{status}] {r}")

print()
print("=== Specific form references from prompt ===")
for doc_num, name_fragment in form_refs:
    found = [f for f in files_in_zip if name_fragment in f]
    if found:
        print(f"  [OK] {doc_num} {name_fragment} -> {found[0]}")
    else:
        all_ok = False
        print(f"  [MISSING] {doc_num} {name_fragment}")

# Check the 3 excluded oversized files are NOT in the zip
excluded = [
    "8.2.2.1.10 Daily Painter Line Up.xlsx",
    "8.2.2.2.17 Approved Tag Tracking.xlsx",
    "8.2.2.4.20 Metelix Demand and Production Tracker Template.xlsx",
]
print()
print("=== Correctly excluded oversized files ===")
for ex in excluded:
    found = [f for f in files_in_zip if ex in f]
    if found:
        all_ok = False
        print(f"  [ERROR - SHOULD BE EXCLUDED] {ex}")
    else:
        print(f"  [OK - excluded] {ex}")

# Check no obsolete files leaked in
obsolete_in_zip = [f for f in files_in_zip if "/obsolete/" in f.lower() or "/review and update/" in f.lower()]
print()
print(f"=== Obsolete files in zip: {len(obsolete_in_zip)} ===")
if obsolete_in_zip:
    all_ok = False
    for o in obsolete_in_zip[:5]:
        print(f"  [LEAK] {o}")
else:
    print("  [OK] No obsolete files in zip")

# Count forms in zip
form_files = [f for f in files_in_zip if f.startswith("forms/")]
print(f"\n=== Form files in zip: {len(form_files)} ===")

# Verify manifest row count matches prompt claim
import csv
import io
manifest_data = z.read("ai_indexes/forms_manifest.csv").decode("utf-8")
reader = csv.DictReader(io.StringIO(manifest_data))
rows = list(reader)
current_in_manifest = sum(1 for r in rows if r["is_obsolete"] == "False")
obsolete_in_manifest = sum(1 for r in rows if r["is_obsolete"] == "True")
print(f"\n=== Manifest counts ===")
print(f"  Total rows: {len(rows)} (prompt says 289)")
print(f"  Current: {current_in_manifest} (prompt says 84)")
print(f"  Obsolete: {obsolete_in_manifest} (prompt says 205)")
count_ok = len(rows) == 289 and current_in_manifest == 84 and obsolete_in_manifest == 205
if count_ok:
    print("  [OK] Counts match prompt")
else:
    all_ok = False
    print("  [MISMATCH] Counts don't match prompt!")

# Check sheet_index row count
sheet_data = z.read("ai_indexes/sheet_index.csv").decode("utf-8")
sheet_rows = len(sheet_data.strip().split("\n")) - 1  # minus header
print(f"\n=== Sheet index rows: {sheet_rows} (prompt says 758) ===")
if sheet_rows == 758:
    print("  [OK]")
else:
    all_ok = False
    print("  [MISMATCH]")

# Check duplicate map
dup_data = z.read("ai_indexes/duplicate_revision_map.csv").decode("utf-8")
dup_reader = csv.DictReader(io.StringIO(dup_data))
dup_rows = list(dup_reader)
cluster_ids = set(r["cluster_id"] for r in dup_rows)
print(f"\n=== Duplicate map: {len(dup_rows)} rows, {len(cluster_ids)} clusters (prompt says 150/58) ===")
if len(dup_rows) == 150 and len(cluster_ids) == 58:
    print("  [OK]")
else:
    all_ok = False
    print("  [MISMATCH]")

print(f"\n{'=' * 40}")
if all_ok:
    print("ALL CHECKS PASSED")
else:
    print("SOME CHECKS FAILED — review above")
