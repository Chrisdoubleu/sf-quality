"""
Plant 2 AI Audit Package Builder

Generates:
  - forms/          — clean copy of current forms (no temp files, Thumbs.db)
  - ai_indexes/forms_manifest.csv
  - ai_indexes/sheet_index.csv
  - ai_indexes/duplicate_revision_map.csv
  - ai_indexes/batch_order.csv
"""

import os
import sys
import shutil
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

# --- try imports ---
try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl not installed"); sys.exit(1)
try:
    import xlrd
except ImportError:
    xlrd = None
    print("WARNING: xlrd not available — .xls files will be marked LEGACY_XLS_NOT_PARSED")

# --- paths ---
SOURCE = Path(r"c:\Dev\sf-quality\docs\Organization Forms Reference\Plant 2\Plant 2 Production Forms")
PKG    = Path(r"c:\Dev\sf-quality\docs\Organization Forms Reference\Plant 2\Plant2_AI_Audit_Package")
FORMS  = PKG / "forms"
IDX    = PKG / "ai_indexes"

EXCLUDE_NAMES = {"Thumbs.db"}
EXCLUDE_PREFIXES = ("~$",)
MAX_FORM_FILE_SIZE = 500 * 1024  # Keep in sync with build_zip.py

GENERIC_NAME_TOKENS = {
    "line", "template", "forms", "form", "operating", "tracking", "daily", "sheet",
    "log", "checklist", "schedule", "paint", "plant", "production", "customer",
    "customers", "xlsx", "xls", "xlsm", "p2",
}

# --- category auto-classification rules ---
def classify_file(rel_path: str, filename: str) -> tuple[str, str]:
    """Return (category, line) based on path and filename heuristics."""
    low = filename.lower()
    rel_low = rel_path.lower()

    # Line assignment
    if "line 101" in rel_low or "101-103" in rel_low or "line 103" in rel_low:
        line = "Line 101-103"
    elif "line 102" in rel_low:
        line = "Line 102"
    elif "shipping" in rel_low:
        line = "General"
    elif "8.2.2.3 production forms by customer" in rel_low:
        # Check for specific customer
        for cust in ["rollstamp", "mytox", "laval", "metelix", "kb components", "polycon", "brp", "misc"]:
            if cust in rel_low:
                line = f"Customer-Specific"
                break
        else:
            line = "Customer-Specific"
    else:
        line = "General"

    # Category classification
    if "obsolete" in rel_low or "review and update" in rel_low:
        category = "DOCUMENT CONTROL"
    elif any(k in low for k in ["inspection", "inspect"]):
        if "buff" in low:
            category = "QUALITY INSPECTION"
        elif "gp12" in low or "gp-12" in low:
            category = "GP-12 / CONTAINMENT"
        else:
            category = "QUALITY INSPECTION"
    elif "gp12" in low or "gp-12" in low:
        category = "GP-12 / CONTAINMENT"
    elif any(k in low for k in ["tally sheet", "tally"]):
        category = "PRODUCTION TRACKING"
    elif any(k in low for k in ["defect", "reject", "fallout", "scrap"]):
        category = "DEFECT TRACKING"
    elif any(k in low for k in ["ncr", "nonconform", "out of spec", "crash report"]) or re.search(r"\brma\b", low):
        category = "NCR / DISPOSITION"
    elif any(k in low for k in ["hold tag", "hold for review"]):
        category = "NCR / DISPOSITION"
    elif any(k in low for k in ["packslip", "pack slip", "packing slip", "shipping report", "receiving log",
                                  "delivery performance", "monthly totals", "tracker template"]):
        category = "PACKAGING / SHIPPING"
    elif "shipping" in rel_low:
        category = "PACKAGING / SHIPPING"
    elif any(k in low for k in ["load sheet", "loaded parts", "production tracking", "production report",
                                  "paint tally", "schedule template", "daily schedule"]):
        category = "PRODUCTION TRACKING"
    elif any(k in low for k in ["paint mix", "colour verif", "color verif", "batch verif",
                                  "paint kitchen", "solvent", "paint inventory"]):
        category = "LAB / CHEMISTRY"
    elif any(k in low for k in ["clean", "maintenance", "booth clean", "burn off", "rack burn",
                                  "sander maintenance", "sanding booth"]):
        category = "MAINTENANCE / PM"
    elif any(k in low for k in ["oven verif", "temp log", "temperature", "tpm checklist",
                                  "operating form", "robot operator", "line speed",
                                  "pressure pot", "programs"]):
        category = "PROCESS CONTROL"
    elif any(k in low for k in ["down time", "downtime"]):
        category = "PRODUCTION TRACKING"
    elif any(k in low for k in ["painter line up", "painter schedule", "daily painter"]):
        category = "SCHEDULING / LABOR"
    elif any(k in low for k in ["waste", "sludge", "still bottom", "empty"]):
        category = "WASTE MANAGEMENT"
    elif any(k in low for k in ["sanding", "buffing", "deburring", "sanded", "to be buffed",
                                  "buff summary", "hummer sanding"]):
        category = "POST-PAINT OPERATIONS"
    elif any(k in low for k in ["finished good", "partial raw", "use next", "rework"]):
        category = "PRODUCTION TRACKING"
    elif any(k in low for k in ["change tracker"]):
        category = "DOCUMENT CONTROL"
    elif any(k in low for k in ["trial", "paint trial"]):
        category = "NCR / DISPOSITION"
    elif any(k in low for k in ["template"]) and "8.2.2.27" in low:
        category = "None/Reference"
    elif any(k in low for k in ["approved tag"]):
        category = "PACKAGING / SHIPPING"
    elif any(k in low for k in ["spoiler application", "hummer"]):
        category = "PRODUCTION TRACKING"
    elif "misc customers" in low:
        category = "QUALITY INSPECTION"
    else:
        category = "UNCATEGORIZED"

    return category, line


def extract_customer(rel_path: str) -> str:
    """Extract customer name from path if in customer subfolder."""
    rel_low = rel_path.lower()
    customer_map = {
        "rollstamp": "Rollstamp",
        "mytox": "Mytox",
        "laval tool": "Laval Tool",
        "metelix": "Metelix",
        "kb components": "KB Components",
        "polycon": "Polycon",
        "brp": "BRP",
        "misc": "Misc",
        "falcon lakeside": "Falcon Lakeside",
        "manterra": "Manterra",
        "mitchell": "Mitchell Plastics",
    }
    for key, name in customer_map.items():
        if key in rel_low:
            return name
    # Check filenames for customer hints
    if "tesla" in rel_low:
        return "Tesla (via Polycon/Rollstamp)"
    if "bmw" in rel_low:
        return "BMW (via Rollstamp)"
    return ""


def get_file_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    type_map = {
        ".xlsx": "xlsx", ".xls": "xls", ".xlsm": "xlsm",
        ".docx": "docx", ".doc": "doc",
        ".pdf": "pdf", ".jpg": "jpg", ".jpeg": "jpeg", ".png": "png",
    }
    return type_map.get(ext, ext.lstrip(".") if ext else "unknown")


def extract_doc_number(filename: str) -> str:
    """Try to extract document number like 8.2.2.1.5 from filename."""
    match = re.match(r"(8\.\d+\.\d+(?:\.\d+)*)", filename)
    if match:
        return match.group(1)
    # Also check for 8.5.2.* pattern
    match = re.match(r"(8\.\d+\.\d+(?:\.\d+)*)", filename)
    return match.group(1) if match else ""


def is_in_obsolete(rel_path: str) -> bool:
    return "obsolete" in rel_path.lower() or "review and update" in rel_path.lower()


def zip_inclusion_flags(rel_path: str, is_obsolete: bool, file_size_bytes: int) -> tuple[bool, bool]:
    """Return (included_in_zip, requires_separate_upload) for forms zip packaging."""
    rel_low = rel_path.lower().replace("\\", "/")
    if is_obsolete or "/obsolete/" in rel_low or "/review and update/" in rel_low:
        return False, False
    if file_size_bytes > MAX_FORM_FILE_SIZE:
        return False, True
    return True, False


def normalize_name_tokens(path: str) -> set[str]:
    """Tokenize filename for duplicate cluster confidence estimation."""
    low = path.replace("\\", "/").split("/")[-1].lower()
    low = re.sub(r"\.(xlsx|xlsm|xls|pdf|docx|doc)$", "", low)
    low = re.sub(r"^\d+(?:\.\d+)+\.?\d*\s*", "", low)
    low = re.sub(r"[^a-z0-9]+", " ", low)
    return {t for t in low.split() if t and t not in GENERIC_NAME_TOKENS and not t.isdigit()}


def cluster_confidence(paths: list[str]) -> str:
    """Estimate duplicate/revision cluster confidence from filename similarity."""
    if len(paths) <= 1:
        return "HIGH"
    token_sets = [normalize_name_tokens(p) for p in paths]
    max_sim = 0.0
    for i in range(len(token_sets)):
        for j in range(i + 1, len(token_sets)):
            union = token_sets[i] | token_sets[j]
            sim = (len(token_sets[i] & token_sets[j]) / len(union)) if union else 1.0
            if sim > max_sim:
                max_sim = sim
    if max_sim >= 0.50:
        return "HIGH"
    if max_sim >= 0.20:
        return "MEDIUM"
    return "LOW"


def get_sheet_names_xlsx(filepath: Path) -> list[str]:
    """Get sheet names from .xlsx/.xlsm without loading data."""
    try:
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        names = wb.sheetnames
        wb.close()
        return names
    except Exception as e:
        return [f"ERROR: {e}"]


def get_sheet_names_xls(filepath: Path) -> list[str]:
    """Get sheet names from .xls using xlrd."""
    if xlrd is None:
        return ["LEGACY_XLS_NOT_PARSED"]
    try:
        wb = xlrd.open_workbook(str(filepath))
        return wb.sheet_names()
    except Exception as e:
        return [f"ERROR: {e}"]


def main():
    print(f"Source: {SOURCE}")
    print(f"Package: {PKG}")

    # Ensure output dirs exist
    FORMS.mkdir(parents=True, exist_ok=True)
    IDX.mkdir(parents=True, exist_ok=True)

    # --- Phase 1: Discover all files ---
    all_files = []
    for root, dirs, files in os.walk(SOURCE):
        for fname in files:
            # Skip excluded
            if fname in EXCLUDE_NAMES:
                continue
            if any(fname.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            full = Path(root) / fname
            rel = full.relative_to(SOURCE)
            all_files.append((full, rel, fname))

    print(f"Discovered {len(all_files)} files (after excluding temp/Thumbs.db)")

    # --- Phase 2: Copy forms ---
    copied = 0
    for full, rel, fname in all_files:
        dest = FORMS / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(full), str(dest))
        copied += 1
    print(f"Copied {copied} files to forms/")

    # --- Phase 3: Build manifest + sheet index ---
    manifest_rows = []
    sheet_rows = []
    file_type_counts = {}

    for full, rel, fname in all_files:
        rel_str = str(rel).replace("\\", "/")
        ftype = get_file_type(fname)
        file_type_counts[ftype] = file_type_counts.get(ftype, 0) + 1

        doc_num = extract_doc_number(fname)
        category, line = classify_file(rel_str, fname)
        customer = extract_customer(rel_str)
        obsolete = is_in_obsolete(rel_str)

        # File metadata
        stat = full.stat()
        mod_time = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        size_kb = round(stat.st_size / 1024, 1)

        # Parse status + sheet names
        parse_status = "Readable"
        sheets = []

        if ftype in ("xlsx", "xlsm"):
            sheets = get_sheet_names_xlsx(full)
            if sheets and sheets[0].startswith("ERROR:"):
                parse_status = "Parse Error"
        elif ftype == "xls":
            sheets = get_sheet_names_xls(full)
            if sheets == ["LEGACY_XLS_NOT_PARSED"]:
                parse_status = "LEGACY_XLS_NOT_PARSED"
            elif sheets and sheets[0].startswith("ERROR:"):
                parse_status = "Parse Error"
        elif ftype in ("docx", "doc"):
            parse_status = "Readable"
        elif ftype == "pdf":
            parse_status = "Readable"
        elif ftype in ("jpg", "jpeg", "png"):
            parse_status = "Image"
        else:
            parse_status = "Unknown"

        # Stale check (older than 2 years from 2026-02-24)
        stale = stat.st_mtime < datetime(2024, 2, 24, tzinfo=timezone.utc).timestamp()
        included_in_zip, requires_separate_upload = zip_inclusion_flags(rel_str, obsolete, stat.st_size)

        manifest_rows.append({
            "relative_path": rel_str,
            "document_number": doc_num,
            "filename": fname,
            "category": category,
            "line": line,
            "customer": customer,
            "file_type": ftype,
            "parse_status": parse_status,
            "last_modified_utc": mod_time,
            "size_kb": size_kb,
            "sheet_count": len(sheets) if sheets and not sheets[0].startswith("ERROR:") and sheets != ["LEGACY_XLS_NOT_PARSED"] else 0,
            "is_obsolete": obsolete,
            "included_in_zip": included_in_zip,
            "requires_separate_upload": requires_separate_upload,
            "is_stale": stale,
            "platform_entity_map": "",
            "mapping_confidence": "",
        })

        # Sheet index rows
        for i, sname in enumerate(sheets):
            if sname.startswith("ERROR:") or sname == "LEGACY_XLS_NOT_PARSED":
                sheet_rows.append({
                    "relative_path": rel_str,
                    "document_number": doc_num,
                    "sheet_index": 0,
                    "sheet_name": sname,
                    "file_type": ftype,
                })
            else:
                sheet_rows.append({
                    "relative_path": rel_str,
                    "document_number": doc_num,
                    "sheet_index": i,
                    "sheet_name": sname,
                    "file_type": ftype,
                })

    # Write manifest
    manifest_path = IDX / "forms_manifest.csv"
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"Wrote forms_manifest.csv ({len(manifest_rows)} rows)")

    # Write sheet index
    if sheet_rows:
        sheet_path = IDX / "sheet_index.csv"
        with open(sheet_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(sheet_rows[0].keys()))
            writer.writeheader()
            writer.writerows(sheet_rows)
        print(f"Wrote sheet_index.csv ({len(sheet_rows)} rows)")

    # --- Phase 4: Duplicate/revision detection ---
    # Group by document number prefix (strip version suffixes)
    from collections import defaultdict
    doc_groups = defaultdict(list)
    for row in manifest_rows:
        dn = row["document_number"]
        if dn:
            doc_groups[dn].append(row)

    dup_rows = []
    dup_id = 0
    for dn, files in doc_groups.items():
        if len(files) > 1:
            dup_id += 1
            # Determine which is current vs obsolete
            current = [f for f in files if not f["is_obsolete"]]
            obsolete = [f for f in files if f["is_obsolete"]]
            confidence = cluster_confidence([f["relative_path"] for f in files])
            for f in files:
                dup_rows.append({
                    "cluster_id": dup_id,
                    "document_number": dn,
                    "relative_path": f["relative_path"],
                    "is_obsolete": f["is_obsolete"],
                    "last_modified_utc": f["last_modified_utc"],
                    "revision_note": "CURRENT" if not f["is_obsolete"] else "OBSOLETE/SUPERSEDED",
                    "cluster_confidence": confidence,
                })

    dup_path = IDX / "duplicate_revision_map.csv"
    with open(dup_path, "w", newline="", encoding="utf-8") as f:
        if dup_rows:
            writer = csv.DictWriter(f, fieldnames=list(dup_rows[0].keys()))
            writer.writeheader()
            writer.writerows(dup_rows)
        else:
            f.write("cluster_id,document_number,relative_path,is_obsolete,last_modified_utc,revision_note,cluster_confidence\n")
    print(f"Wrote duplicate_revision_map.csv ({len(dup_rows)} rows across {dup_id} clusters)")

    # --- Phase 5: Batch order ---
    # Priority: current non-obsolete first, then by category importance, then by doc number
    category_priority = {
        "QUALITY INSPECTION": 1,
        "DEFECT TRACKING": 2,
        "NCR / DISPOSITION": 3,
        "GP-12 / CONTAINMENT": 4,
        "PRODUCTION TRACKING": 5,
        "PROCESS CONTROL": 6,
        "LAB / CHEMISTRY": 7,
        "POST-PAINT OPERATIONS": 8,
        "PACKAGING / SHIPPING": 9,
        "SCHEDULING / LABOR": 10,
        "WASTE MANAGEMENT": 11,
        "MAINTENANCE / PM": 12,
        "DOCUMENT CONTROL": 13,
        "None/Reference": 14,
        "UNCATEGORIZED": 15,
    }

    batch_rows = []
    for i, row in enumerate(sorted(manifest_rows, key=lambda r: (
        r["is_obsolete"],  # current first
        category_priority.get(r["category"], 99),
        r["document_number"],
    ))):
        batch_rows.append({
            "batch_order": i + 1,
            "relative_path": row["relative_path"],
            "document_number": row["document_number"],
            "category": row["category"],
            "is_obsolete": row["is_obsolete"],
            "file_type": row["file_type"],
        })

    batch_path = IDX / "batch_order.csv"
    with open(batch_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(batch_rows[0].keys()))
        writer.writeheader()
        writer.writerows(batch_rows)
    print(f"Wrote batch_order.csv ({len(batch_rows)} rows)")

    # --- Summary ---
    total = len(manifest_rows)
    current = sum(1 for r in manifest_rows if not r["is_obsolete"])
    obsolete_count = total - current
    stale_count = sum(1 for r in manifest_rows if r["is_stale"])
    current_in_zip = sum(1 for r in manifest_rows if (not r["is_obsolete"]) and r["included_in_zip"])
    current_excluded = sum(1 for r in manifest_rows if (not r["is_obsolete"]) and r["requires_separate_upload"])
    obsolete_in_zip = sum(1 for r in manifest_rows if r["is_obsolete"] and r["included_in_zip"])

    print("\n=== PACKAGE SUMMARY ===")
    print(f"Total files: {total}")
    print(f"  Current: {current}")
    print(f"  Obsolete: {obsolete_count}")
    print(f"  Current included in zip: {current_in_zip}")
    print(f"  Current excluded from zip: {current_excluded}")
    print(f"  Stale (>2yr): {stale_count}")
    print(f"File types: {file_type_counts}")
    print(f"Sheet index rows: {len(sheet_rows)}")
    print(f"Duplicate clusters: {dup_id}")

    # Category breakdown
    cat_counts = defaultdict(int)
    for r in manifest_rows:
        if not r["is_obsolete"]:
            cat_counts[r["category"]] += 1
    print("\nCategory breakdown (current files only):")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Customer breakdown
    cust_counts = defaultdict(int)
    for r in manifest_rows:
        if r["customer"] and not r["is_obsolete"]:
            cust_counts[r["customer"]] += 1
    print("\nCustomer breakdown (current files only):")
    for cust, count in sorted(cust_counts.items(), key=lambda x: -x[1]):
        print(f"  {cust}: {count}")

    # Write package_manifest.json
    pkg_manifest = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_forms_path": str(SOURCE),
        "package_root": str(PKG),
        "prompt_included": False,
        "excluded_artifacts": ["Thumbs.db", "~$*"],
        "counts": {
            "total_files": total,
            "current_files": current,
            "obsolete_files": obsolete_count,
            "forms_manifest_rows": len(manifest_rows),
            "sheet_index_rows": len(sheet_rows),
            "duplicate_clusters": dup_id,
            "duplicate_revision_rows": len(dup_rows),
            "batch_rows": len(batch_rows),
            "stale_files": stale_count,
            "current_files_in_zip": current_in_zip,
            "current_files_excluded_from_zip": current_excluded,
            "obsolete_files_in_zip": obsolete_in_zip,
        },
        "file_type_distribution": file_type_counts,
        "category_distribution_current": dict(cat_counts),
        "customer_distribution_current": dict(cust_counts),
        "pdf_parser_available": False,
    }
    with open(PKG / "package_manifest.json", "w", encoding="utf-8") as f:
        json.dump(pkg_manifest, f, indent=2)
    print(f"\nWrote package_manifest.json")


if __name__ == "__main__":
    main()
