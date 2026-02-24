# Required Audit Output Template

## 1. Executive Summary
- Readiness score (0-100)
- Top 10 blockers

## 2. File Inventory Table
Required columns:
- relative_path
- document_number
- category
- line
- customer
- file_type
- parse_status
- last_modified_utc
- platform_entity_map
- mapping_confidence

## 3. Detailed Analysis by Category
Include sections A-K per prompt.

## 4. Critical Gap Analysis
Include NCR, traceability, taxonomy consistency, quantification, disposition, temporal, digital readiness, cost, competency, calibration, shipping-release gaps.

Required add-on: Embedded Defect Capture Matrix (where defects are captured without dedicated defect-tracking forms).

## 5. Platform Impact Assessment
5a DB, 5b API, 5c UI.

## 6. Cross-Plant Normalization Assessment
Use checklist table format.

## Appendix A
Defect taxonomy mapping table + CSV block.

## Appendix B
Form-to-entity field mapping table + CSV block.

## Appendix C
Form consolidation matrix + CSV block.

## Appendix D
Proposed entities in SQL-style DDL + JSON object blocks.

## Delivery Batching
If the response nears limits, deliver in this order:
1. Sections 1-6
2. Appendix A-B
3. Appendix C-D
