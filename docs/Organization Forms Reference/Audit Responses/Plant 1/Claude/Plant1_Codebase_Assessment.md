# Plant 1 QSA Audit — Codebase-Informed Assessment

**Assessment Date:** 2026-02-24
**Assessed By:** Claude Code (with live codebase access)
**Source Report:** Plant1_QSA_Audit_Report_Claude.md (QSA persona, no codebase access)

---

## Purpose

The QSA audit was performed by an AI with no access to the sf-quality codebase. This assessment cross-references every major claim against the actual database migrations, API contracts, and app planning docs to produce a verified, engineering-actionable synthesis.

---

## 1. Audit Quality Grade: A-

The report is thorough, well-structured, and correctly identifies the major gaps. The form-by-form analysis is detailed and the entity proposals are reasonable. Deductions:

- **Defect taxonomy proposal is superseded** — the live DB already has a more mature 12-category / 35-leaf taxonomy (vs. audit's 8/38). The audit's mapping is still valuable as a reconciliation input, but shouldn't be used as-is for seed data.
- **3 of 5 claimed NCR child entities don't exist** — NcrDisposition, NcrCostLedger, NcrExternalReference, NcrNote were cited as existing but aren't separate tables. The DB uses denormalized fields on NonConformanceReport instead. Only NcrContainmentAction exists as a child table.
- **DispositionCode count is slightly off** — the DB has 11 codes but they're not the exact same 11 names the audit listed. The DB has `Reprocess` and `Return to Customer` which the audit didn't mention, and doesn't have `Blend` or `Customer-Deviation` / `Engineering-Deviation` as separate codes (it uses `Deviate` as a single code).

These are understandable given the audit had only a prompt briefing, not live schema access.

---

## 2. Verified Findings (Confirmed Against Codebase)

### 2a. NCR Entity — 100% Field Coverage Confirmed

Every NCR field the audit referenced exists in migration `028_ncr_tables.sql`. The NCR entity is production-ready with 35+ fields including:
- All identification fields (NcrNumber, PlantId, CustomerId, PartId, SupplierId, LotNumber)
- All quality fields (DefectTypeId, SeverityRatingId, DetectionProcessAreaId, QuantityAffected/Rejected/Inspected)
- All disposition fields (DispositionCodeId, DispositionApprovedById, DispositionDate, DispositionJustification)
- All customer notification fields (CustomerNotified, CustomerNotifiedDate, NotificationMethod)
- All cost fields (EstimatedCost, CostNotes)
- All lifecycle fields (ReportedById, ReportedDate, ClosedDate, ClosedById)
- Temporal versioning with 7-year retention

**Assessment:** The audit's claim that the paper forms cover only 15-40% of what the NCR entity handles is CORRECT. The platform is vastly more capable than any paper form in the package.

### 2b. DispositionCode — 11 Codes Verified (with naming differences)

Migration `018_seed_quality_reference.sql` seeds 11 disposition codes. They cover the same functional space the audit described but with some naming differences:

| Audit Name | Actual Code Name | Status |
|-----------|-----------------|--------|
| Scrap | Scrap | EXACT |
| Rework | Rework | EXACT |
| Use-As-Is | Use As Is | EXACT |
| Recoat | Recoat | EXACT |
| Strip-and-Recoat | Strip and Recoat | EXACT |
| Return-to-Supplier | Return to Supplier | EXACT |
| Sort | Sort | EXACT |
| Hold | Hold | EXACT |
| Customer-Deviation + Engineering-Deviation | Deviate (single code) | MERGED |
| Pending-Customer-Decision | — | NOT PRESENT (Hold covers this) |
| Blend | — | NOT PRESENT |
| — | Reprocess | ADDITIONAL |
| — | Return to Customer | ADDITIONAL |

**Assessment:** The audit's finding that only 3 of 11 disposition codes are actively used on paper forms (Scrap, Rework, Recoat) is likely accurate and represents an adoption gap, not a schema gap.

### 2c. ProcessArea — 38 Rows Seeded

Migration `022_seed_process_areas.sql` seeds 38 process areas across 6 categories. The audit's request for "E-Coat Stage 1 through Stage 12" granularity is partially covered — the DB uses functional names (E-Coat Application, Zinc Phosphate Conversion, etc.) rather than stage numbers. Plant-specific stage numbering could be added as reference data.

### 2d. Production Infrastructure Tables — Schema Only

Equipment, Customer, Supplier, Part tables all exist with full schema but NO seed data. This is by design — plant teams populate via the application. The audit correctly flagged 18 customers as reference data gaps, but these are operational data, not seed data.

---

## 3. Corrections Required

### 3a. Defect Taxonomy — Audit Proposal is Superseded

**What the audit proposed:** 8 L1 categories, 38 L2 leaves
**What the DB has:** 12 L1 categories, 35 L2 leaves (migration 020)

The DB taxonomy is organized differently:
- ADH (Adhesion): 3 leaves — covers audit's PROCESS-ADHESION
- TEX (Surface Texture): 3 leaves — covers audit's SURFACE-ORANGEPEEL, SURFACE-RUNS
- CON (Contamination): 3 leaves — covers audit's CONTAM-DIRT, SURFACE-FISHEYE
- APP (Color & Appearance): 3 leaves — covers audit's CONTAM-DISCOLOR
- COV (Coverage & Film Build): 3 leaves — covers audit's COVERAGE-LIGHT, COVERAGE-HEAVY, COVERAGE-BARE
- CUR (Cure & Film Formation): 3 leaves — audit proposed but didn't categorize cure defects
- BLS (Blistering & Porosity): 3 leaves — covers audit's SURFACE-BUBBLE, SURFACE-PINHOLE
- COR (Corrosion): 3 leaves — covers audit's PRETREAT-RUST
- DAM (Damage & Substrate): 3 leaves — covers audit's HANDLING-SCRATCH, SUBSTRATE-* categories
- MAS (Masking & Dimensional): 3 leaves — not in audit (new discovery)
- SPC (Specialty Finishing): 3 leaves — not in audit (new discovery)
- DOC (Identification & Documentation): 2 leaves — not in audit

**Action Required:** The audit's Appendix A defect taxonomy mapping table should be reconciled against the live DB taxonomy, NOT imported directly. A reconciliation file is needed (see defect_taxonomy/ folder).

### 3b. NCR Child Entities — Design Differs from Audit Assumption

The audit assumed separate child tables for NcrDisposition, NcrCostLedger, NcrExternalReference, and NcrNote. In reality:
- **NcrContainmentAction** — EXISTS as a child table (confirmed)
- **NcrDisposition** — DOES NOT EXIST. Disposition is denormalized on NonConformanceReport (DispositionCodeId, DispositionDate, DispositionJustification, DispositionApprovedById)
- **NcrCostLedger** — DOES NOT EXIST. Cost is denormalized (EstimatedCost, CostNotes)
- **NcrExternalReference** — DOES NOT EXIST in any migration
- **NcrNote** — DOES NOT EXIST in any migration

**Impact:** The audit's entity coverage scores for NCR/Disposition (15-40%) are still directionally correct — the paper forms lack most of what the NCR entity provides. But field-level mapping in Appendix B should use `quality.NonConformanceReport.DispositionCodeId` not `quality.NcrDisposition.*`.

### 3c. TestMethod Entity — Confirmed Missing

The audit correctly identified that test methods (ASTM D3359, ASTM D4752, etc.) need reference data. No TestMethod table exists in any migration. This is a genuine schema gap that should be addressed as part of the InspectionRecord entity proposal.

---

## 4. New Entity Proposals — Assessment

The audit proposed 12 new entities. None exist in the codebase. Here's my assessment of each:

| Entity | Audit Priority | Codebase Assessment | Recommendation |
|--------|---------------|--------------------|-----------------|
| **ProductionRun** | P1 | No `production` schema exists. This is genuinely needed — the load/unload/coat cycle has no digital representation. | APPROVE — create `production` schema + entity |
| **LoadRecord** | P1 | Same — nothing exists. The audit's field list (LoadBarNumber, QuantityLoaded/AtUnload/Rejected/Packed, ApprovalTagNumber) is well-grounded in form evidence. | APPROVE |
| **InspectionRecord** | P1 | Nothing exists. The audit's proposal (InspectionTypeId, OverallResult, child TestResult table) is sound. Should FK to ProductionRun and LoadRecord. | APPROVE |
| **InspectionTestResult** | P1 | Nothing exists. The split between PASS_FAIL and NUMERIC result types matches what the forms actually capture. | APPROVE |
| **ProcessParameterLog** | P2 | Nothing exists. The audit's design (header + reading child table, per-line per-shift) matches the temperature log / daily checklist pattern. | APPROVE |
| **ProcessParameterReading** | P2 | The InSpec computed column is a nice touch. EquipmentId FK is correct. | APPROVE |
| **LabAnalysis** | P2 | Nothing exists. The BASF Process Database failure confirms the need. The audit's per-stage-per-parameter design matches the Daily Lab Analysis Template structure. | APPROVE |
| **LabAnalysisReading** | P2 | StageNumber field is e-coat-specific — needs generalization for other coating lines in plants 2-7. | APPROVE with generalization note |
| **MaintenanceLog** | P3 | Nothing exists. Lower priority — maintenance forms are the least structured in the package. | APPROVE at P3 |
| **CertificationRecord** | P2 | Nothing exists. The audit correctly identified the cert label/log pattern as ship-release evidence. | APPROVE |
| **GP12Program** | P2 | Nothing exists. The program-level tracking (start date, planned exit, required clean shipments) is a genuine gap — GP-12 is currently form-per-customer-per-part with no lifecycle. | APPROVE |
| **GP12InspectionRecord** | P2 | Links GP12Program to InspectionRecord. Sensible. | APPROVE |

**Overall: All 12 proposals are grounded in real form evidence and fill genuine schema gaps.** The `production` schema creation is a prerequisite for 6 of them.

---

## 5. API Impact — Assessment

The audit's endpoint proposals are reasonable but should be sequenced after the DB entities are built. Key observations:

- **NCR endpoint enhancements** (adding productionRunId, loadBarNumber, paintBatchLot to POST /v1/ncr/full) are valid but require DB schema changes first (new FK columns on NonConformanceReport).
- **Reporting endpoints** (/v1/reports/defect-pareto?groupBy=customer, yield, chemistry-trend) align with planned Phase 9 dashboard endpoints but need the underlying views built first.
- The audit correctly identified that Inspection, Production Run, and Lab Chemistry endpoints are entirely missing and would constitute new API phases.

---

## 6. UI Impact — Assessment

The audit's screen inventory and consolidation analysis are the **most immediately actionable** outputs for the app team:

- **53 forms → ~12 configurable templates** is a strong finding. The Tier 1/2/3 classification is well-evidenced.
- **Tablet-first for floor entry** is a critical design constraint that should be captured in app Phase 2 (Design System).
- **Shift-based batching** as a global context filter (alongside plant scope) is a new UX pattern not yet in the app planning docs.

---

## 7. Summary of Actions

| # | Action | Target Repo | Priority | Blocked By |
|---|--------|-------------|----------|------------|
| 1 | Reconcile audit defect taxonomy (8 L1 / 38 L2) against live DB taxonomy (12 L1 / 35 L2) | DB | P1 | Nothing |
| 2 | Create `production` schema | DB | P1 | Nothing |
| 3 | Create ProductionRun + LoadRecord entities | DB | P1 | Action 2 |
| 4 | Create InspectionRecord + InspectionTestResult entities | DB | P1 | Action 2 |
| 5 | Create TestMethod reference table | DB | P1 | Nothing |
| 6 | Add ProductionRunId FK to NonConformanceReport | DB | P1 | Action 3 |
| 7 | Create LabAnalysis + LabAnalysisReading entities | DB | P2 | Action 2 |
| 8 | Create ProcessParameterLog + Reading entities | DB | P2 | Action 2 |
| 9 | Create GP12Program + GP12InspectionRecord entities | DB | P2 | Action 4 |
| 10 | Create CertificationRecord entity | DB | P2 | Action 3 |
| 11 | Seed 18 customers as Plant 1 reference data | DB | P1 | Nothing |
| 12 | Seed Plant 1 equipment (guns, ovens, tanks, booths) | DB | P1 | Nothing |
| 13 | Add Inspection/Production/Lab API endpoint groups | API | P2 | Actions 3-8 |
| 14 | Enhance NCR create endpoint with production run linkage | API | P2 | Action 6 |
| 15 | Design tablet-first form entry UX pattern | App | P1 | Nothing |
| 16 | Add shift selector as global context filter | App | P1 | Nothing |
| 17 | Implement configurable customer-specific form templates | App | P2 | Actions 3-4 |
| 18 | Wait for Plants 2-7 audits before finalizing defect seed data | All | GATE | Plants 2-7 audits |
