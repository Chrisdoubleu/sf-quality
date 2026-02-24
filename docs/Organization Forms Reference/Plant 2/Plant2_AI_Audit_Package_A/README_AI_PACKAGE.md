# Plant 2 AI Audit Package A — Line Operations & Process Control

## Scope
This is **Package A of 2** for the Plant 2 quality systems audit. It covers:

- **8.2.2.1** — Line 101-103 Operating Forms (shared across spray lines)
- **8.2.2.2** — Line 102 Operating Forms (robotic spray line-specific)
- **8.2.2.5–8.2.2.34** — Root-level forms (paint mix, waste, sanding/buffing tallies, labels/tags, templates)

**53 forms** total, **129 worksheet tabs**.

## Plant 2 Context
Plant 2 operates **3 conveyorized liquid spray paint lines** (Lines 101, 102, 103) with robotic application + manual touch-up, plus post-paint sanding, buffing, and deburring operations. This differs from Plant 1 (powder coat + e-coat).

Line types relevant: `LIQUID` (primary), `MECHFIN` (post-paint sanding/buffing/deburring).

## Upload Instructions
1. Upload this entire folder (with subfolders) to the AI conversation
2. Use the corresponding **QSA_Plant2_Audit_Prompt_Part_A.md** prompt
3. After completing Part A, start a new conversation with **Package B** and its prompt
4. The Part B prompt will instruct the AI to build on Part A findings

## Package Contents
```
Plant2_AI_Audit_Package_A/
├── forms/                          # 53 production forms (xlsx, xls, xlsm)
│   ├── 8.2.2.1 Line 101-103 Operating Forms/
│   ├── 8.2.2.2 Line 102 Operating Forms/
│   └── (root-level forms: 8.2.2.5–8.2.2.34)
├── ai_indexes/
│   ├── forms_manifest.csv          # Classified inventory of all 53 forms
│   ├── sheet_index.csv             # 129 worksheet tabs discovered
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
│   └── cross_plant_checklist_template.csv
├── ai_extracted_text/              # (empty — all forms are Excel)
├── package_manifest.json
└── README_AI_PACKAGE.md            # This file
```

## Companion Package
**Plant2_AI_Audit_Package_B** covers Customer Inspection (8.2.2.3) and Shipping (8.2.2.4) forms.
