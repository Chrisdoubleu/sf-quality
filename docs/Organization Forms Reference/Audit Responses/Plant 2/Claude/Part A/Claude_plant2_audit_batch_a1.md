# BATCH A1: Executive Summary + File Inventory Table

---

## Section 1: Executive Summary

**Plant 2 Digital Readiness Score: 28/100**

Here's the blunt assessment: Plant 2 is a mirror image of Plant 1's dysfunction, with a few unique problems of its own.

I've examined **53 forms** across **129 worksheet tabs** covering the entire operational core of a three-line liquid paint operation — and what I found is a data collection system that exists almost entirely for the sake of data collection. The fundamental question I came in with — *"If I were a quality engineer trying to trace a customer complaint back through this system, could I actually do it?"* — gets the same answer as Plant 1: **No. Not even close.**

### What's Broken, Specifically

**No NCR system exists.** Zero forms in this 53-form package constitute a formal nonconformance report. The Hold Tag (8.2.2.12) has checkbox options for REVIEW / REJECT / REINSPECT but captures no root cause, no corrective action, no cost data, no disposition chain. The "Approved Tag Tracking" form (8.2.2.2.17) is the closest thing to a quality event log — it records date, tag number, colour, part description, and quantity — but it has no defect type, no disposition code, and hasn't been updated since November 2018. This plant has been running three paint lines for years with no formal system for documenting what goes wrong.

**Traceability is fundamentally broken.** The chain from part → load → paint batch → spray parameters → oven cure → post-paint operations has at least three hard breaks:

1. The **Daily Load Sheet** (8.2.2.1.5) records part names by customer section but has no rack/carrier ID field, no batch cross-reference, and no timestamp.
2. The **Paint Production Tracking** form (8.2.2.2.1) captures spray parameters (fluid PSI, atomizing PSI, fan PSI, cup test) and references a "Starting Rack #" — but this only exists for Line 102. Lines 101 and 103 have no equivalent production tracking form.
3. **Post-paint tally sheets** (sanding, buffing, deburring) record part names and quantities with no link to the production run, paint batch, or defect that caused the rework.

**Process control data is being collected but never analyzed.** The Daily Paint Tally Sheet (8.2.2.1.18) records paint batch numbers, viscosity (raw and reduced), solvent amounts, and filter sizes — solid data points. But this data feeds nowhere. There's no statistical analysis, no trend charting, no correlation with quality outcomes. Same story with Oven Verification (8.2.2.1.16) — date and oven setting, period.

**The waste system is purely labeling.** The five waste "forms" (Booth Sludge, Still Bottoms, Waste Paint, Waste Zinc, Empty) are printable drum labels with zero data fields — no volumes, no dates, no tie to production. The Solvent Usage Tracking form (8.2.2.25) has the right fields (supplier, amount, batch, drum tracking) but no linkage to production volume or cost.

### Bright Spots (Relative to Plant 1)

- The **102 Line Operating Form** (8.2.2.2.7, xlsm) is a genuinely well-designed standardized work instruction with a production tracker that captures carrier number, time, temperature/humidity, spray parameters per stage (primer, base, clear), and supervisor sign-off. *This is the best form in either plant audit.*
- The **Buffing Summary Template** (8.2.2.30) has monthly and daily summary dashboards with FTQ calculations, return-to-buff rates, and per-person efficiency metrics. It's collecting data across 272 days.
- The **102 Schedule Template** (8.2.2.2.3) has master reference sheets for parts, cycle times, and robot job programs — real planning data.
- The **New Paint Batch Verification** (8.2.2.26) captures colorimetric data (L, a, b at 25°/45°/75° with ΔEcmc pass/fail) — actual lab-grade verification.
- **Revision logs** exist on 7+ forms (vs nearly zero in Plant 1), showing some document control discipline.

### Comparison to Plant 1 (30/100)

Plant 2 scores **28/100** — slightly worse overall despite a few better-designed forms. The main drag: Lines 101 and 103 have significantly less production tracking infrastructure than Line 102, the waste system is pure labeling with no data, and two critical process control forms (Oven Verification, Paint Kitchen Temp) haven't been modified since December 2016.

---

## Section 2: File Inventory Table

| # | Doc Number | File Name | Category | Line | Ext | Parse Status | Modified | Has Data? | Rev Evidence? | Platform Entity | Map Confidence |
|---|-----------|-----------|----------|------|-----|-------------|----------|-----------|---------------|----------------|----------------|
| 1 | 8.2.2.1.1 | 101-103 Weekly Rack Burn Off Tracker | MAINTENANCE / PM | 101-103 | .xlsx | Readable | 2024-10-16 | Yes (rack names, dates) | No | Maintenance | Medium |
| 2 | 8.2.2.1.2 | Paint Kitchen Temp Log | PROCESS CONTROL | 101-103 | .xls | Readable | 2016-12-16 ⚠️ | No (blank template) | No | ProcessControl | Medium |
| 3 | 8.2.2.1.3 | Daily Paint Booth Cleaning Schedule | MAINTENANCE / PM | 101/103 | .xlsx | Readable | 2023-09-18 | No (template) | No | Maintenance | High |
| 4 | 8.2.2.1.4 | Monthly Paint Booth Cleaning Schedule | MAINTENANCE / PM | 101/103 | .xlsx | Readable | 2025-11-10 | No (template) | Yes (Rev Log: 3 revisions, 2014-2023) | Maintenance | High |
| 5 | 8.2.2.1.5 | 101-103 Daily Load Sheet | PRODUCTION TRACKING | 101-103 | .xlsx | Readable | 2025-08-07 | Yes (part numbers, customer names) | No | ProductionRun | High |
| 6 | 8.2.2.1.6 | 101 Schedule Template | SCHEDULING / LABOR | 101 | .xlsx | Readable | 2025-12-12 | Yes (part schedules, paint usage, time matrix) | No | None/Reference | Low |
| 7 | 8.2.2.1.7 | Daily Painter Schedule | SCHEDULING / LABOR | 101 | .xlsx | Readable | 2024-11-06 | Yes (sample lineup data) | No | None/Reference | Low |
| 8 | 8.2.2.1.9 | Daily Down Time | SCHEDULING / LABOR | 101-103 | .xlsx | Readable | 2023-06-27 | No (template) | No | ProductionRun | Medium |
| 9 | 8.2.2.1.10 | Daily Painter Line Up | SCHEDULING / LABOR | 101-103 | .xlsx | Readable | 2024-10-31 | No (template) | No | None/Reference | Low |
| 10 | 8.2.2.1.11 | 103 Schedule Template | SCHEDULING / LABOR | 103 | .xlsx | Readable | 2025-11-04 | Yes (schedules, paint usage) | No | None/Reference | Low |
| 11 | 8.2.2.1.16 | Oven Verification Log | PROCESS CONTROL | 101/103 | .xls | Readable | 2016-12-16 ⚠️ | No (blank template) | No | ProcessControl | Medium |
| 12 | 8.2.2.1.18 | Daily Paint Tally Sheet | PAINT MIX / CHEMISTRY | 101-103 | .xls | Readable | 2024-03-15 | No (template) | No | PaintMix | High |
| 13 | 8.2.2.1.19 | Line 103 Paint Pot Lines Cleaning Chart | MAINTENANCE / PM | 103 | .xlsx | Readable | 2025-11-10 | No (template) | No | Maintenance | High |
| 14 | 8.2.2.1.20 | Line 101 Paint Pot Lines Cleaning Chart | MAINTENANCE / PM | 101 | .xlsx | Readable | 2025-11-10 | No (template) | No | Maintenance | High |
| 15 | 8.2.2.2.1 | 102 Line Paint Production Tracking | PRODUCTION TRACKING | 102 | .xlsx | Readable | 2024-06-25 | No (template) | No | ProductionRun | High |
| 16 | 8.2.2.2.3 | 102 Line Paint Schedule Template | SCHEDULING / LABOR | 102 | .xlsx | Readable | 2025-03-25 | Yes (ref sheets, job programs) | No | None/Reference | Low |
| 17 | 8.2.2.2.4 | 102 Line Loaded Parts Tracking | PRODUCTION TRACKING | 102 | .xlsx | Readable | 2024-01-08 | No (template) | No | ProductionRun | High |
| 18 | 8.2.2.2.6 | Line 102 Programs | PROCESS CONTROL | 102 | .xlsx | Readable | 2025-10-17 | Yes (job numbers, valve, presets) | No | ProcessControl | Medium |
| 19 | 8.2.2.2.7 | 102 Line Operating Form | PROCESS CONTROL | 102 | .xlsm | Readable | 2025-01-07 | Yes (SWI + tracker) | Yes (Created 2024-12-20, AP) | ProcessControl + ProductionRun | High |
| 20 | 8.2.2.2.8 | Line 102 Robot Operator Maintenance | MAINTENANCE / PM | 102 | .xlsx | Readable | 2025-12-10 | No (template) | No | Maintenance | High |
| 21 | 8.2.2.2.9 | 102 TPM Checklist | MAINTENANCE / PM | 102 | .xlsx | Readable | 2025-12-10 | No (template) | No | Maintenance | High |
| 22 | 8.2.2.2.10 | 102 Maintenance Log | MAINTENANCE / PM | 102 | .xlsx | Readable | 2025-12-10 | No (template) | No | Maintenance | High |
| 23 | 8.2.2.2.17 | Approved Tag Tracking | DEFECT TRACKING | 102 | .xlsx | Readable | 2018-11-30 ⚠️ | No (template) | No | NCR (INFERRED) | Low |
| 24 | 8.2.2.5 | Paint Kitchen Inventory | PAINT MIX / CHEMISTRY | General | .xlsx | Readable | 2025-01-17 | Yes (full inventory w/ costs) | Yes (Rev Log: 7 revisions, 2016-2024) | PaintMix | High |
| 25 | 8.2.2.6 | Change Tracker | DOCUMENT CONTROL | General | .xlsx | Readable | 2023-06-27 | No (template) | No | DocumentControl | Medium |
| 26 | 8.2.2.7 | Daily Sanding Tally Sheet | POST-PAINT OPERATIONS | General | .xlsx | Readable | 2026-02-05 | No (template w/ examples) | Yes (Rev Log: 4 revisions, 2016-2023) | PostPaintOps | High |
| 27 | 8.2.2.8 | Daily Buffing Tally Sheet | POST-PAINT OPERATIONS | General | .xlsx | Readable | 2026-02-05 | Yes (KANBAN: part list) | Yes (Rev Log: 4 revisions, 2016-2023) | PostPaintOps | High |
| 28 | 8.2.2.9 | Daily Deburring Tally Sheet | POST-PAINT OPERATIONS | General | .xlsx | Readable | 2023-07-24 | No (template) | Yes (Rev Log: 4 revisions, 2016-2023) | PostPaintOps | High |
| 29 | 8.2.2.10 | Sanded- Ready For Paint (Orange) | LABELS / TAGS | General | .xlsx | Readable | 2023-08-16 | No (tag template) | Yes (Created 05/05/17, Rev 07/28/23) | PackagingHold | Medium |
| 30 | 8.2.2.11 | Finished Goods/Partial | LABELS / TAGS | General | .xlsx | Readable | 2023-07-28 | No (tag template) | Yes (Created 05/05/17, Rev 07/28/23) | PackagingHold | Medium |
| 31 | 8.2.2.12 | Hold Tag | LABELS / TAGS | General | .xlsx | Readable | 2023-07-28 | No (tag template) | Yes (Created 05/05/17, Rev 07/28/23) | NCR (INFERRED) | Medium |
| 32 | 8.2.2.13 | Hold For Review | LABELS / TAGS | General | .xlsx | Readable | 2023-07-28 | No (tag template) | Yes (Created 05/05/17, Rev 07/28/23) | NCR (INFERRED) | Medium |
| 33 | 8.2.2.14 | Partial Raw | LABELS / TAGS | General | .xlsx | Readable | 2023-07-28 | No (tag template) | Yes (Created 05/05/17, Rev 07/28/23) | PackagingHold | Medium |
| 34 | 8.2.2.15 | Rework- To Be Sanded | LABELS / TAGS | General | .xlsx | Readable | 2023-07-28 | No (tag template) | Yes (Created 05/05/17, Rev 07/28/23) | NcrDisposition (INFERRED) | Medium |
| 35 | 8.2.2.16 | To Be Buffed | LABELS / TAGS | General | .xlsx | Readable | 2023-07-28 | No (tag template) | Yes (Created 05/05/17, Rev 07/28/23) | NcrDisposition (INFERRED) | Medium |
| 36 | 8.2.2.17 | Booth Sludge | WASTE MANAGEMENT | General | .xlsx | Readable | 2023-08-03 | No (drum label only) | Yes (Created 05/05/17, Rev 08/01/23) | WasteTracking (INFERRED) | Low |
| 37 | 8.2.2.18 | Empty | WASTE MANAGEMENT | General | .xlsx | Readable | 2023-08-03 | No (drum label only) | Yes (Created 05/05/17, Rev 08/01/23) | WasteTracking (INFERRED) | Low |
| 38 | 8.2.2.19 | Still Bottoms | WASTE MANAGEMENT | General | .xlsx | Readable | 2023-08-03 | No (drum label only) | Yes (Created 05/05/17, Rev 08/01/23) | WasteTracking (INFERRED) | Low |
| 39 | 8.2.2.20 | Waste Paint | WASTE MANAGEMENT | General | .xlsx | Readable | 2023-08-03 | No (drum label only) | Yes (Created 05/05/17, Rev 08/01/23) | WasteTracking (INFERRED) | Low |
| 40 | 8.2.2.21 | Waste Zinc | WASTE MANAGEMENT | General | .xlsx | Readable | 2023-08-03 | No (drum label only) | Yes (Created 05/05/17, Rev 08/01/23) | WasteTracking (INFERRED) | Low |
| 41 | 8.2.2.22 | Use Next | LABELS / TAGS | General | .xlsx | Readable | 2023-08-10 | No (label only) | Yes (Created 05/05/17, Rev 08/10/23) | None/Reference | Low |
| 42 | 8.2.2.23 | Paint Mix Information Sheet | PAINT MIX / CHEMISTRY | General | .xlsx | Readable | 2023-12-20 | No (template) | No | PaintMix | High |
| 43 | 8.2.2.24 | Pressure Pot Label | PAINT MIX / CHEMISTRY | General | .xlsx | Readable | 2023-08-17 | No (label template) | Yes (Created 08/15/23) | PaintMix | Medium |
| 44 | 8.2.2.25 | Solvent Usage Tracking | PAINT MIX / CHEMISTRY | General | .xlsx | Readable | 2023-10-31 | Yes (supplier/product list) | No | PaintMix + WasteTracking | High |
| 45 | 8.2.2.26 | New Paint Batch Verification | PAINT MIX / CHEMISTRY | General | .xlsx | Readable | 2024-06-28 | No (template) | No | PaintMix | High |
| 46 | 8.2.2.27 | Template | LABELS / TAGS | General | .xlsx | Readable | 2024-01-05 | No (blank ATT template) | No | None/Reference | Low |
| 47 | 8.2.2.28 | Down time Tracking Template | SCHEDULING / LABOR | 101/102/103 | .xlsx | Readable | 2024-01-05 | Yes (category structure) | No | ProductionRun | Medium |
| 48 | 8.2.2.29 | Daily Production Report Template | PRODUCTION TRACKING | 101/103 | .xlsx | Readable | 2024-01-05 | No (template) | No | ProductionRun | High |
| 49 | 8.2.2.30 | Buffing Summary Template | POST-PAINT OPERATIONS | General | .xlsx | Readable | 2024-01-22 | Yes (272 days of summary data) | No | PostPaintOps | High |
| 50 | 8.2.2.31 | Daily Hummer Sanding Tally Sheet | POST-PAINT OPERATIONS | General | .xlsx | Readable | 2024-11-13 | No (template) | Yes (Rev Log: 1 entry, 2023) | PostPaintOps | High |
| 51 | 8.2.2.32 | Dustless Sander Maintenance Check Sheet | MAINTENANCE / PM | General | .xlsx | Readable | 2025-05-12 | No (template) | No | Maintenance | High |
| 52 | 8.2.2.33 | Plant 2 Paint Trial Information Sheet | PROCESS CONTROL | General | .xlsx | Readable | 2025-12-16 | No (template) | No | ProcessControl + PaintMix | High |
| 53 | 8.2.2.34 | Sanding Booth Cleaning and Maintenance | MAINTENANCE / PM | General | .xlsx | Readable | 2025-11-10 | Yes (dates from May-Jun 2023) | No | Maintenance | High |

---

## Classification Corrections from Automated Manifest

| Doc Number | File Name | Changed From | Changed To | Reason |
|-----------|-----------|-------------|------------|--------|
| 8.2.2.12 | Hold Tag | defect_tracking | LABELS / TAGS | It's a printable tag, not a tracking form |
| 8.2.2.13 | Hold For Review | defect_tracking | LABELS / TAGS | — |
| 8.2.2.15 | Rework- To Be Sanded | defect_tracking | LABELS / TAGS | — |
| 8.2.2.1.18 | Daily Paint Tally Sheet | production_tracking | PAINT MIX / CHEMISTRY | Records paint mixing data, not production counts |
| 8.2.2.23 | Paint Mix Information Sheet | process_control | PAINT MIX / CHEMISTRY | — |
| 8.2.2.24 | Pressure Pot Label | process_control | PAINT MIX / CHEMISTRY | — |
| 8.2.2.25 | Solvent Usage Tracking | lab_chemistry | PAINT MIX / CHEMISTRY | — |
| 8.2.2.5 | Paint Kitchen Inventory | lab_chemistry | PAINT MIX / CHEMISTRY | — |
| 8.2.2.26 | New Paint Batch Verification | process_control | PAINT MIX / CHEMISTRY | — |
| 8.2.2.2.4 | 102 Line Loaded Parts Tracking | other | PRODUCTION TRACKING | — |
| 8.2.2.2.7 | 102 Line Operating Form | other | PROCESS CONTROL | — |
| 8.2.2.33 | Plant 2 Paint Trial Information Sheet | other | PROCESS CONTROL | — |
| 8.2.2.28 | Down time Tracking Template | document_control | SCHEDULING / LABOR | — |
| 8.2.2.30 | Buffing Summary Template | document_control | POST-PAINT OPERATIONS | — |
| 8.2.2.2.6 | Line 102 Programs | document_control | PROCESS CONTROL | — |
| 8.2.2.18 | Empty | waste_management | LABELS / TAGS | It's a container label, same template as other waste labels |

---

## Stale Form Flags (>2 Years Without Modification)

| Doc Number | File Name | Last Modified | Age |
|-----------|-----------|--------------|-----|
| 8.2.2.1.2 | Paint Kitchen Temp Log | 2016-12-16 | 8+ years old |
| 8.2.2.1.16 | Oven Verification Log | 2016-12-16 | 8+ years old |
| 8.2.2.2.17 | Approved Tag Tracking | 2018-11-30 | 6+ years old |
