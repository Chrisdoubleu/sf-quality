# Plant 2 AI Audit Package B — Customer Inspection & Shipping

## Scope
This is **Package B of 2** for the Plant 2 quality systems audit. It covers:

- **8.2.2.3** — Production Forms by Customer (6 active customers + Misc)
  - 8.2.2.3.2 Rollstamp (BMW/Tesla)
  - 8.2.2.3.3 Mytox
  - 8.2.2.3.4 Laval Tool
  - 8.2.2.3.5 Metelix
  - 8.2.2.3.6 KB Components
  - 8.2.2.3.7 Polycon
- **8.2.2.4** — Shipping Forms (pack slips, receiving logs, delivery performance, trackers)

**31 forms** total, **89 worksheet tabs**.

## Plant 2 Context
Plant 2 operates **3 conveyorized liquid spray paint lines** (Lines 101, 102, 103). This package focuses on the customer-facing quality inspection forms and shipping/logistics documentation.

## Upload Instructions
1. **Complete Package A audit first** — Part B builds on Part A findings
2. Upload this entire folder (with subfolders) to a **new** AI conversation
3. Use the corresponding **QSA_Plant2_Audit_Prompt_Part_B.md** prompt
4. Preferred: let the AI load Part A artifacts from `ai_context/` (no manual paste needed)
5. Fallback: paste the Part A handoff text manually if files are unavailable

## Package Contents
```
Plant2_AI_Audit_Package_B/
├── forms/                          # 31 production forms (xlsx, xls)
│   ├── 8.2.2.3 Production Forms by Customer/
│   │   ├── 8.2.2.3.2 Rollstamp/
│   │   ├── 8.2.2.3.3 Mytox/
│   │   ├── 8.2.2.3.4 Laval Tool/
│   │   ├── 8.2.2.3.5 Metelix/
│   │   ├── 8.2.2.3.6 KB Components/
│   │   ├── 8.2.2.3.7 Polycon/
│   │   └── Misc/
│   └── 8.2.2.4 Shipping Forms/
├── ai_indexes/
│   ├── forms_manifest.csv          # Classified inventory of all 31 forms
│   ├── sheet_index.csv             # 89 worksheet tabs discovered
│   ├── duplicate_revision_map.csv  # Duplicate/superseded form clusters
│   └── batch_order.csv             # Recommended ingestion order
├── ai_context/
│   ├── architecture_snapshot.md    # sf-quality platform architecture
│   ├── api_surface_summary.csv     # 30 API endpoints
│   ├── lookup_codes.csv            # LineType + DispositionCode reference
│   ├── evidence_rules.md           # Confidence/evidence standards
│   ├── glossary.md                 # Term definitions
│   ├── output_template.md          # Required output structure
│   ├── defect_taxonomy_mapping_template.csv
│   ├── cross_plant_checklist_template.csv
│   ├── part_a_handoff.md           # Canonical Part A summary for Part B
│   ├── part_a_defect_seed_partial.csv
│   ├── part_a_form_entity_map.csv
│   ├── part_a_entity_proposals.json
│   └── db_mapping_normalization.md # Canonical schema/field normalization rules
├── ai_extracted_text/              # (empty — all forms are Excel)
├── package_manifest.json
└── README_AI_PACKAGE.md            # This file
```

## Companion Package
**Plant2_AI_Audit_Package_A** covers Line Operations (8.2.2.1, 8.2.2.2) and Process Control (root-level 8.2.2.5–8.2.2.34) forms.
