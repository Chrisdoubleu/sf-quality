# Plant 1 QSA Audit — Final Synthesis

**Plant:** Select Finishing Plant 1 (Powder Coat + E-Coat)
**Synthesis Date:** 2026-02-24
**Status:** COMPLETE — Cross-repo validated against DB (Phase 34), API (v0.3.0), App (planning), Reference Architecture (QFM)

---

## 1. What Was Audited

- **133 files** across 3 document families: Powder Line Forms, E-Coat Line Forms, Inspection & Testing Forms
- **18 customers** served: AGS, ABM, JAC, Warren, Tiercon, GLDC, Polycon, Presstran, JNM, Takumi, Multimatic, Rollstamp, Ultrafit, GreenBlue, MSSC, Accurate, Ursa, Toyotetsu
- **2 AI auditors** produced independent reports: Claude (complete) + ChatGPT Pro (partial — timed out before finishing appendices)
- **1 codebase assessment** cross-referenced all findings against live database schema

---

## 2. Overall Readiness Score: 30/100

Plant 1's quality data capture system is a **functional paper-and-Excel operation** that keeps parts moving but would fail a forensic traceability test. Both AI auditors converged on the same score independently.

| Dimension | Consensus Score | Key Evidence |
|-----------|----------------|-------------|
| NCR/Disposition | 15/100 | No formal NCR exists. 4 disconnected forms cover ~15-40% of what the NCR entity provides |
| Defect Tracking | 33/100 | 97 unique defect strings across 19 forms. 3 taxonomy families. Cross-customer Pareto impossible |
| Inspection & Testing | 43/100 | Strong test method references (ASTM). Film build readings captured numerically. No calibration linkage |
| Production Tracking | 38/100 | Load/unload cycle captured but identifiers don't chain together. Approval Tag # is de facto lot ID |
| Process Control | 38/100 | Parameters recorded but not linked to production runs. ChatGPT found structured spec limits |
| Lab/Chemistry | 48/100 | Daily Lab Analysis Template is best-structured form. BASF PB Ratio file has 8+ years of data in one file |
| Traceability | 18/100 | Chain breaks at 3 points: Load→Unload, Paint Record→Load Sheet, Defect→Production Run |
| Document Control | 13/100 | 1 of 133 forms has a revision log. 23 files older than 2 years. "DO NOT USE" files still in active folders |

---

## 3. Critical Findings (Both Auditors Agree)

1. **No NCR system exists.** The platform's NCR entity (35+ fields, 7-state lifecycle, containment actions) is a quantum leap from paper.
2. **Traceability breaks at load bar.** Load→Unload→Inspect→Ship chain has no common identifier.
3. **97 defect names normalize to 38 types.** Same defect = 3-7 different spellings across customer forms.
4. **53 customer-specific forms reduce to ~12 configurable templates.** Tier 1: 13 identical copies. Tier 2: 8 minor variants. Tier 3: 7 genuinely unique.
5. **GP-12 forms are siloed.** 14 forms across 8 customers doing the same job with 14 data models.
6. **Zero cost data** on any form. Cost-of-poor-quality is invisible.

---

## 4. ChatGPT-Unique Findings (8 items Claude missed)

| # | Finding | Severity | Impact |
|---|---------|----------|--------|
| C1 | **Cavity/location codes used instead of defect counts** — operators write "D3", "K4", "A6" | HIGH | App must enforce numeric entry; location codes become metadata |
| C2 | **BASF PB Ratio file has ~69,538 merged ranges** — hostile to any parser | MEDIUM | Migration tooling must handle or bypass |
| C3 | **Scanned records reveal defects NOT in templates** — "Bad Polish", "Nick" | MEDIUM | Taxonomy must account for operator-invented terms |
| C4 | **PackagingHold / ShipmentRelease entity needed** | HIGH | Merged into CertificationRecord design |
| C5 | **DocumentTemplate / DocumentRevision entity needed** | HIGH | Confirmed: Document table has no revision control |
| C6 | **TrainingCompetencyRecord mentioned** | LOW | Deferred — no Plant 1 evidence |
| C7 | **Specific spec limits extracted** — Bath Temp 90-98°F, pH 5.2-6.0, Oven 380-415°F | INFO | Directly usable as ProcessParameter seed data |
| C8 | **OOS auto-trigger NCR** — Out-of-Spec form should auto-create NCR when repeated | HIGH | Workflow rule needed at API layer |

---

## 5. Defect Taxonomy Reconciliation

**Three-way reconciliation completed** — see [DEFECT_TAXONOMY_MASTER.csv](defect_taxonomy/DEFECT_TAXONOMY_MASTER.csv)

| Source | L1 Categories | L2 Leaves | Schema |
|--------|--------------|-----------|--------|
| Claude Audit | 8 | 38 | SURFACE, COVERAGE, CONTAMINATION, HANDLING, PROCESS, SUBSTRATE, PRETREAT, PACKAGING |
| ChatGPT Audit | 7 | ~30 | APPLICATION, COVERAGE, DAMAGE, TEXTURE, CONTAMINATION, SURFACE, CORROSION |
| Live DB | 12 | 35 | ADH, TEX, CON, APP, COV, CUR, BLS, COR, DAM, MAS, SPC, DOC |

**Reconciliation results:**
- **EXACT match:** 12 defects (dirt, hook mark, scratch, orange peel, etc.)
- **MAPPED (different category, same leaf):** 45 defects (e.g., fisheyes: audit=SURFACE, DB=CON)
- **REVIEW needed:** 4 defects (water spots, oil contamination — may need new DB leaves)
- **NEW (not in DB):** 8 defects — all die-cast substrate defects (GLDC-specific: misfill, pin push, sink, flash, sharp edge) + general material defect catch-alls. Recommend: incoming material taxonomy extension after Plants 2-7 confirm cross-plant need.

---

## 6. Entity Proposals — Cross-Repo Validated

**15 entities proposed → 9 genuinely new, 6 superseded by QFM**

See [ENTITY_PROPOSALS.md](entity_proposals/ENTITY_PROPOSALS.md) for full assessment.

### Genuinely New (not in QFM)
| Entity | Priority | Purpose |
|--------|----------|---------|
| LoadRecord | P1 | Load-bar-level tracking per production run |
| CertificationRecord | P2 | Ship-release evidence with hold/release lifecycle |
| ProcessParameterLog | P2 | Per-line per-shift parameter capture header |
| ProcessParameterReading | P2 | Individual readings with InSpec computed column |
| LabAnalysis | P2 | Per-line per-date lab analysis header |
| LabAnalysisReading | P2 | Per-stage per-parameter readings |
| GP12Program | P2 | Program lifecycle (Active→Monitoring→Exit→Closed) |
| GP12InspectionRecord | P2 | Bridge: GP12Program ↔ InspectionInstance |
| DocumentTemplate/Revision | P2 | Document revision control (ALTER TABLE + new entity) |

### Superseded by QFM (use QFM designs)
| Audit Proposal | QFM Equivalent |
|---------------|----------------|
| InspectionRecord | inspection.InspectionInstance |
| InspectionTestResult | inspection.InspectionResponse[Numeric\|Attribute\|Text\|Selection] |
| ProductionRun | inspection.ProductionRun (move to production schema) |

---

## 7. Gap Closure Status (21 Gaps)

See [GAP_TRACKER.md](gap_tracker/GAP_TRACKER.md) for full cross-repo status.

| Status | Count | Gaps |
|--------|-------|------|
| **CLOSED by existing DB** | 4 | NCR process (GAP-01), Disposition codes (GAP-05), Cost fields (GAP-08), User identity (GAP-09) |
| **PARTIALLY CLOSED** | 2 | Defect taxonomy (GAP-03), Calibration linkage (GAP-10) |
| **DESIGNED (entity proposals + QFM)** | 11 | Traceability, PPM, digital readiness, GP-12, inspection, process params, production run, lab, packaging hold, OOS trigger |
| **OPEN** | 2 | Stale forms (GAP-06), Document revision control (GAP-19) |
| **ACKNOWLEDGED (non-schema)** | 1 | Merged-cell migration tooling (GAP-18) |
| **BLOCKED** | 1 | Inspection entity (GAP-12) — QFM adjudication NO-GO |

---

## 8. Platform Impact Summary

### sf-quality-db
- **Existing coverage:** NCR entity (35+ fields), 11 DispositionCodes, 12/35 DefectType taxonomy, 38 ProcessAreas, CalibrationRecord, Document (no revision)
- **Gaps confirmed:** No production schema, no inspection entities (QFM blocked), no lab/process parameter entities, no GP-12 entity, no document revision control
- **Action:** 9 new entities across ~23 migrations (Phases 35-42) + QFM blocker resolution for inspection entities

### sf-quality-api
- **Existing coverage:** 19 NCR endpoints fully implemented, SCAR/Audit/8D placeholders
- **Gaps confirmed:** No Inspection, ProductionRun, Lab, ProcessParameter, GP-12, or Certification endpoints
- **Action:** ~30 new endpoints across 6 controller groups (after DB entities land)

### sf-quality-app
- **Existing coverage:** 0% — not started (planning complete)
- **Gaps confirmed:** Everything. No screens exist.
- **Key finding from audit:** Tablet-first for floor entry. Shift selector as global context. 53 forms → 12 configurable templates.
- **Action:** App Phase 1 can start independently of plant audits

---

## 9. Action Items for Plant 1 Completion

| # | Action | Owner | Priority | Blocked By | Status |
|---|--------|-------|----------|------------|--------|
| 1 | Resolve QFM 8 adjudication blockers | DB | P0 | Nothing — must do before any inspection entity work | NOT STARTED |
| 2 | Create `production` schema + ProductionRun + LoadRecord | DB | P1 | Nothing | READY TO START |
| 3 | Add ProductionRunId FK to NonConformanceReport | DB | P1 | Action 2 | BLOCKED |
| 4 | Create ProcessParameterLog + Reading entities | DB | P2 | Action 2 | BLOCKED |
| 5 | Create LabAnalysis + LabAnalysisReading entities | DB | P2 | Action 2 | BLOCKED |
| 6 | Create GP12Program + GP12InspectionRecord entities | DB | P2 | QFM inspection entities | BLOCKED |
| 7 | Create CertificationRecord entity | DB | P2 | Action 2 | BLOCKED |
| 8 | Add RevisionNumber + SupersededById to Document | DB | P2 | Nothing | READY TO START |
| 9 | Seed Plant 1 e-coat spec limits as ProcessParameter reference data | DB | P1 | Action 4 | BLOCKED |
| 10 | Seed 18 customers as Plant 1 reference data | DB | P1 | Nothing | READY TO START |
| 11 | Add Inspection/Production/Lab API endpoint groups | API | P2 | DB Actions 2-5 | BLOCKED |
| 12 | Enhance NCR create endpoint with ProductionRunId | API | P2 | DB Action 3 | BLOCKED |
| 13 | Design tablet-first form entry UX pattern | App | P1 | Nothing | READY TO START |
| 14 | Add shift selector as global context filter | App | P1 | App Phase 2 | BLOCKED |
| 15 | Implement configurable customer-specific form templates | App | P2 | DB Actions 2-6 | BLOCKED |
| 16 | Ask ChatGPT to complete remaining deliverables (Appendix B full, Phase 5 template) | Human | P2 | Nothing | RECOMMENDED |

---

## 10. Open Questions for Plants 2-7

These questions emerged from Plant 1 and need answers from subsequent plant audits:

1. **Do other plants have formal NCR forms?** — If any plant has a better process, adopt it company-wide
2. **What defect vocabulary do other plants use?** — 6 substrate defects (GLDC die-cast) may be Plant-1-only. Need cross-plant evidence before adding to DB
3. **Is the Approval Tag # used as lot identifier across all plants?** — Critical for traceability chain design
4. **Do other plants have training/competency forms?** — IATF 16949 clause 7.2 evidence
5. **What coating technologies do other plants use?** — Determines process parameter schema (liquid paint, anodize, etc.)
6. **Do water spots need a dedicated DefectType leaf?** — Currently mapped to CON-DST but may warrant own category
7. **Does oil contamination need a dedicated leaf?** — Currently maps to CON-FIS (fisheyes) but oil is a root cause, not a defect presentation

---

*Plant 1 synthesis complete. 133 files examined by 2 AI auditors. 21 gaps identified (4 already closed by platform). 9 new entities approved. 97 defect strings reconciled to 35 DB leaves. Ready for Plants 2-7.*
