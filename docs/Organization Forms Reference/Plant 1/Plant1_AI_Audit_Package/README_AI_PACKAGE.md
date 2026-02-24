# Plant 1 AI Audit Package

This package is prepared for uploading with the QSA audit prompt.

## Important
- The audit prompt file is intentionally NOT included.
- Paste the prompt separately in chat, then upload this package zip.

## Contents
- `forms/` — full copy of Plant 1 forms (originals untouched; temp/lock artifacts excluded)
- `ai_indexes/forms_manifest.csv` — master inventory
- `ai_indexes/sheet_index.csv` — workbook sheet discovery
- `ai_indexes/duplicate_revision_map.csv` — potential duplicate/superseded variants
- `ai_indexes/batch_order.csv` — recommended ingestion order
- `ai_extracted_text/` — extracted text sidecars for docx/pdf/images
- `ai_context/` — architecture/context files and output templates

## Upload Guidance
1. Upload prompt text directly in chat.
2. Upload this package zip.
3. If token limits are hit, submit files in `batch_order.csv` order.
