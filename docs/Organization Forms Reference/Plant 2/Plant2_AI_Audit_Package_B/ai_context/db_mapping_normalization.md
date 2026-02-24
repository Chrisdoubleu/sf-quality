# DB Mapping Normalization (Use Before Any Field Mapping)

Use this file to normalize Part A assumptions before producing Part B field mappings and entity impacts.

## Canonical Mapping Rules

1. If a Part A artifact references `quality.NcrDisposition.*`, map to:
   - `quality.NonConformanceReport.DispositionCodeId`
   - `quality.NonConformanceReport.DispositionDate`
   - `quality.NonConformanceReport.DispositionJustification`
   - `quality.NonConformanceReport.DispositionApprovedById`

2. If a Part A artifact references `quality.NcrCostLedger.*`, map to:
   - `quality.NonConformanceReport.EstimatedCost`
   - `quality.NonConformanceReport.CostNotes`

3. If a Part A artifact references `quality.NcrExternalReference.*` or `quality.NcrNote.*`:
   - Treat as `NO CURRENT TABLE`
   - Mark mapping as `INFERRED` and include evidence

4. If Part A or templates reference non-canonical disposition labels:
   - `Customer-Deviation` / `Engineering-Deviation` -> `Deviate`
   - `Pending-Customer-Decision` -> `Hold` (until decision)
   - `Blend` -> `NO DIRECT MATCH` (flag as gap)

## Part B Output Rule

In Appendix B and any field mapping tables:
- Prefer canonical targets above.
- Do not emit `quality.NcrDisposition.*` or `quality.NcrCostLedger.*` as final targets.
- If uncertain, output `INFERRED` with exact evidence path.
