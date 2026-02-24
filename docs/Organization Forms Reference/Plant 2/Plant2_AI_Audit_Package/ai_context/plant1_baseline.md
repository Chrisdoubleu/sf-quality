# Plant 1 Audit Baseline (for Cross-Plant Comparison)

_Reference data from the Plant 1 QSA Audit completed 2026-02-24._

## Plant 1 Profile
- **Coating Lines:** Powder coat (inline conveyorized + offline batch booth) + E-coat (full electrodeposition with pre-treat)
- **Document Prefix:** 8.2.1.*
- **Total Files:** 133 (116 Excel, 6 Word, 2 PDF, 9 JPEG)
- **Customers:** 15+ (AGS, ABM, Tiercon, GLDC, Warren, and others)

## Digital Migration Readiness Scores (Plant 1)

| Dimension | Score | Key Finding |
|-----------|-------|-------------|
| NCR/Disposition | 15/100 | No formal NCR exists. Disposition captured on 2 disconnected forms. |
| Defect Tracking | 35/100 | 97 unique defect strings → 38 types. Quantitative counts exist. Taxonomy fragmented. |
| Inspection & Testing | 45/100 | Strong ASTM references. Film build captured numerically. No digital entity yet. |
| Production Tracking | 40/100 | Load/unload cycle captured but identifiers don't chain together. |
| Process Control | 30/100 | Parameters recorded but not linked to production runs. No SPC. |
| Lab/Chemistry | 50/100 | Daily lab analysis is strongest form. Specs documented. BASF DB abandoned. |
| Traceability | 20/100 | Serial number traceability concept exists but not systematically adopted. |
| Document Control | 10/100 | One form has revision log. Rest have no version control. |
| **Overall** | **30/100** | Data captured at every stage but in disconnected silos. |

## Gaps Identified in Plant 1

| Gap ID | Gap Name | Severity |
|--------|----------|----------|
| GAP-01 | No formal NCR process | CRITICAL |
| GAP-02 | Traceability chain breaks (load→unload→inspect) | CRITICAL |
| GAP-03 | Defect taxonomy fragmented (97 strings → 38 types) | HIGH |
| GAP-04 | No PPM/yield calculation possible (missing denominators) | HIGH |
| GAP-05 | Disposition decisions not formally captured (3 of 11 codes used) | HIGH |
| GAP-06 | Stale forms in circulation (2016-2022 vintage) | MEDIUM |
| GAP-07 | Digital readiness (free-text, merged cells, no IDs) | HIGH |
| GAP-08 | Zero cost data on any form | HIGH |
| GAP-09 | Operators identified by initials only (no employee linkage) | MEDIUM |
| GAP-10 | No calibration references on any inspection form | MEDIUM |
| GAP-11 | No GP-12 exit gate | MEDIUM |
| GAP-12 | No dedicated Inspection entity | HIGH |
| GAP-13 | Process parameters decoupled from quality outcomes | HIGH |
| GAP-14 | No production run / load record tracking entity | CRITICAL |
| GAP-15 | Lab chemistry not digitized (despite strong paper forms) | MEDIUM |
| GAP-16 | GP-12 forms siloed per customer (14 forms, 14 data models) | HIGH |

## Entity Proposals from Plant 1 (All Approved)

12 new entities proposed: ProductionRun, LoadRecord, InspectionRecord, InspectionTestResult, ProcessParameterLog, ProcessParameterReading, LabAnalysis, LabAnalysisReading, MaintenanceLog, CertificationRecord, GP12Program, GP12InspectionRecord.

## Plant 1 Category Distribution

| Category | Count | % |
|----------|-------|---|
| QUALITY INSPECTION | 31 | 23% |
| DEFECT TRACKING | 19 | 14% |
| GP-12 / CONTAINMENT | 14 | 11% |
| PROCESS CONTROL | 13 | 10% |
| PRODUCTION TRACKING | 10 | 8% |
| LAB / CHEMISTRY | 10 | 8% |
| MAINTENANCE / PM | 9 | 7% |
| NCR / DISPOSITION | 4 | 3% |
| PACKAGING / SHIPPING | 4 | 3% |
| DOCUMENT CONTROL | 3 | 2% |

## Defect Types Found in Plant 1

38 normalized defect types across 8 L1 categories:
- COVERAGE: Light Coverage, Heavy Coverage/Build-Up, Bare Metal/No Coat, Dry Spray
- SURFACE: Orange Peel, Runs/Sags, Fisheyes, Pinholes, Bubbles
- PROCESS: Back Ionization, Missing Texture, Paint in Threads, Adhesion Failure, General Paint Defect
- PRETREAT: Rust/Corrosion, Water Marks/Spots
- CONTAMINATION: Dirt/Debris, General Contamination, Oil Contamination, Fiber/Foreign Material, Discoloration/Off Color
- HANDLING: Hook Mark, Hit Mark/Impact, Touch Mark, Scratch/Damage, Dropped/Dent, Stuck Parts, Tight Clip/Fitment
- SUBSTRATE: Belt Mark, Misfill/Short Shot, Pin Push, Sink Mark, Flash, Tool Marks, General Material Defect

## Cross-Plant Comparison Targets

When auditing Plant 2, specifically compare:
1. Does Plant 2 have a formal NCR process or the same gap?
2. How does the traceability chain compare (liquid paint lines vs powder/e-coat)?
3. What defect types are specific to liquid paint vs what overlaps with powder/e-coat?
4. Is the customer-specific form fragmentation pattern the same?
5. How does GP-12 coverage compare (Plant 1 had 14 GP-12 forms)?
6. Does Plant 2 capture cost/scrap data that Plant 1 doesn't?
7. Are there sanding/buffing/deburring quality forms (new to Plant 2)?
8. How does document control maturity compare (Plant 1 had 133 files, 23 stale)?
