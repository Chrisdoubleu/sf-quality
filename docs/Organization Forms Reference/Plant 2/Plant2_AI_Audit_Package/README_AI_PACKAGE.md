# Plant 2 AI Audit Package

This package is prepared for uploading with the QSA audit prompt.

## Important
- The audit prompt file is intentionally NOT included.
- Paste the prompt separately in chat, then upload this package zip.

## Contents
- `forms/` — 81 current (non-obsolete) Plant 2 forms included in zip (temp/lock artifacts excluded)
- `ai_indexes/forms_manifest.csv` — master inventory of ALL 289 files (84 current, 205 obsolete) — the manifest documents everything even though obsolete files are excluded from the zip
- `ai_indexes/sheet_index.csv` — workbook sheet discovery (758 tabs)
- `ai_indexes/duplicate_revision_map.csv` — 58 duplicate/superseded clusters (150 rows)
- `ai_indexes/batch_order.csv` — recommended ingestion order
- `ai_extracted_text/` — note: Plant 2 has no non-Excel files in current folders
- `ai_context/` — architecture/context files, output templates, and **Plant 1 baseline**
- `ai_context/plant1_baseline.md` — Plant 1 audit scores, gaps, entity proposals for cross-plant comparison
- `ai_context/defect_taxonomy_reference_l1_l2.csv` — canonical 12 L1 / 35 L2 defect taxonomy reference for mapping

## Excluded from Zip (Documented in Manifest)
- **205 obsolete files** — in Obsolete/Review and Update folders. Documented in `forms_manifest.csv` and `duplicate_revision_map.csv` but excluded from the zip to keep upload size manageable.
- **3 oversized current files** (>500KB, embedded images) excluded from zip and required for full-current-file coverage:
  - `8.2.2.1.10 Daily Painter Line Up.xlsx` (3.3MB) — SCHEDULING / LABOR
  - `8.2.2.2.17 Approved Tag Tracking.xlsx` (3.3MB) — PACKAGING / SHIPPING
  - `8.2.2.4.20 Metelix Demand and Production Tracker Template.xlsx` (599KB) — PACKAGING / SHIPPING

  These files exist in the source folder and should be uploaded in a follow-up message during audit execution.

## Optional Obsolete Evidence Pack
- A targeted obsolete sample pack is provided separately at:
  - `docs/Organization Forms Reference/Plant 2/Plant2_Obsolete_Exemplar_Pack.zip`
- Use this only when the audit needs concrete obsolete-form content beyond manifest metadata.

## Key Differences from Plant 1 Package
- Plant 2 is **liquid paint** (Lines 101, 102, 103) — NOT powder/e-coat
- Has **post-paint operations** (sanding, buffing, deburring) not present in Plant 1
- Has dedicated **shipping forms** subfolder with per-customer pack slips
- Significantly more obsolete files (205 vs Plant 1's ~20) — heavier revision churn
- No Lab/Chemistry subfolder (no bath chemistry like e-coat)
- New categories not in Plant 1: WASTE MANAGEMENT, POST-PAINT OPERATIONS, SCHEDULING / LABOR

## Upload Guidance
1. Upload prompt text directly in chat.
2. Upload this package zip.
3. If token limits are hit, submit files in `batch_order.csv` order.
