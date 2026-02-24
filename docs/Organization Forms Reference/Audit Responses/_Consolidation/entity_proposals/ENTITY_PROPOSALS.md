# Entity Proposal Assessment — Cross-Repo Validated

**Assessment Date:** 2026-02-24
**Assessed By:** Claude Code (cross-repo validated)
**Sources:** Plant 1 QSA Audit (Claude — 12 entities), ChatGPT Partial (3 additional entities), Plant 2 QSA Audit (Claude Part A + Part B — 12 entities, ChatGPT 3 batches — 5 entities with full DDL), Quality Forms Module (QFM — 12+ entities pre-designed)
**Validation:** Cross-referenced against sf-quality-db (153 migrations, Phase 34), sf-quality-api (v0.3.0), Reference_Architecture

---

## Executive Summary

Plant 1 audits proposed **15 total entities** (12 from Claude + 3 from ChatGPT). Plant 2 audits propose **12 additional entities** (with 9 confirming/extending Plant 1 proposals). Cross-repo validation reveals that the Reference Architecture's **Quality Forms Module (QFM)** already pre-designs many inspection-domain entities in migrations 131-160 — but those are currently **NO-GO** due to 8 adjudication blockers.

**Key alignment finding:** The QFM's `inspection.*` schema overlaps with 6 of the 15 Plant 1 entities. The remaining 9 Plant 1 entities + 12 Plant 2 entities are genuinely new proposals not covered by QFM.

**Plant 2 impact:** Confirms all 9 Plant 1 entity proposals with liquid-paint extensions, and adds 12 genuinely new entities across 5 new schemas (postpaint, logistics, production extensions, labor, compliance).

---

## Alignment Matrix: Audit Proposals vs QFM vs Live DB

### Plant 1 Entities (Original 15)

| # | Proposed Entity | Source | QFM Equivalent | Live DB Status | Recommendation |
|---|----------------|--------|---------------|----------------|----------------|
| 1 | **ProductionRun** | Claude P1 | `inspection.ProductionRun` (QFM) | NOT IN DB | **MERGE** — Use QFM design but place in `production` schema. Plant 2 confirms: add LineType=LIQUID, ColorProgram, Booth/Robot mode |
| 2 | **LoadRecord** | Claude P1 | None | NOT IN DB | **APPROVE** — Genuinely new. Plant 2 confirms: add CarrierNumber + optional MoldingDate |
| 3 | **InspectionRecord** | Claude P1 | `inspection.InspectionInstance` (QFM) | NOT IN DB | **USE QFM** — QFM design is more mature. Plant 2 adds: need count-based InspectionDefectCount child table |
| 4 | **InspectionTestResult** | Claude P1 | `inspection.InspectionResponse[Numeric\|Attribute\|Text\|Selection]` (QFM) | NOT IN DB | **USE QFM** — Plant 2 adds: need InspectionDefectCount for routing-style inspection |
| 5 | **ProcessParameterLog** | Claude P2 | None | NOT IN DB | **APPROVE** — Plant 2 confirms: must support multi-coat parameter groups (primer/base/clear) |
| 6 | **ProcessParameterReading** | Claude P2 | None | NOT IN DB | **APPROVE** — Plant 2 adds: need SpecMin/SpecMax/TargetValue columns (GAP-26) |
| 7 | **LabAnalysis** | Claude P2 | None | NOT IN DB | **APPROVE** — Plant 2 adds: analysis types PaintMix, ColorVerification, SolventUsage, StorageTemp |
| 8 | **LabAnalysisReading** | Claude P2 | None | NOT IN DB | **APPROVE** — Plant 2 adds: structured colour fields (L*, a*, b*, delta-Ecmc at 25/45/75 degrees) |
| 9 | **MaintenanceLog** | Claude P3 | None | NOT IN DB | **APPROVE at P3** — Plant 2 confirms: add checklist-style frequency-based occurrences |
| 10 | **CertificationRecord** | Claude P2 | None | NOT IN DB | **APPROVE** — Plant 2 confirms: must link to Shipment/PackSlip + Inspection/Run |
| 11 | **GP12Program** | Claude P2 | None | NOT IN DB | **APPROVE** — Plant 2: Tesla GP-12 lacks all lifecycle elements; entity is 90% net-new design |
| 12 | **GP12InspectionRecord** | Claude P2 | None (links to QFM InspectionInstance) | NOT IN DB | **APPROVE** — Plant 2 confirms: add customer-program scoping + stage fields |
| 13 | **PackagingHold / ShipmentRelease** | ChatGPT | None | NOT IN DB | **MERGE into CertificationRecord** — Plant 2 confirms: Approved Tag Tracking abandoned since 2018 |
| 14 | **DocumentTemplate / DocumentRevision** | ChatGPT | None | Document exists (13 cols) but NO revision fields | **APPROVE** — Plant 2 confirms: only 2/31 inspection forms have revision tracking. 58 superseded clusters. |
| 15 | **TrainingCompetencyRecord** | ChatGPT | None | NOT IN DB | **DEFER** — Still no evidence at Plant 2. Wait for Plants 3-7. |

### Plant 2 New Entities (12 additional)

| # | Proposed Entity | Source | Schema | Confidence | Live DB Status | Recommendation |
|---|----------------|--------|--------|------------|----------------|----------------|
| 16 | **InspectionDefectCount** | Claude P2-B | quality | HIGH | NOT IN DB | **APPROVE** — Count-based child of InspectionRecord for routing inspection (Good/Buff/Repaint/Scrap). 8-20 rows per inspection. Distinct from QFM InspectionResponse (which is measurement-based). |
| 17 | **CustomerInspectionProfile** | Claude P2-B | quality | HIGH | NOT IN DB | **APPROVE** — Configuration entity for dynamic form rendering. Customer×Part→defect set with GateAlarmThreshold + SortOrder. ~180 rows. Drives which defect columns appear per customer. |
| 18 | **Gp12ContainmentEvent** | Claude P2-B | quality | HIGH | NOT IN DB | **APPROVE** — Full GP-12 lifecycle (entry/exit criteria, customer notification, inspection frequency, max duration, sample size). Links to NCR as triggering event. |
| 19 | **PostPaintReworkEvent** + **PostPaintReworkDefect** | ChatGPT P2 + Claude P2-A | postpaint | HIGH | NOT IN DB | **APPROVE** — Closes GAP-22 (post-paint rework black hole). Lifecycle: DRAFT→OPEN→COMPLETE→VERIFIED. RLS on PlantId. Constraint: QtyOut + QtyScrapped <= QtyIn. |
| 20 | **Shipment/PackSlip** + **ShipmentLine/PackSlipLineItem** | ChatGPT P2 + Claude P2-B | logistics | MEDIUM-HIGH | NOT IN DB | **APPROVE** — Replaces 7 pack slip templates. QualityReleaseStatus gate. CK_ShipmentLine_TraceToken constraint (at least one of ProductionRunId/LoadRecordId/LotNumber). |
| 21 | **ReceivingLogEntry** | Claude P2-B | logistics | MEDIUM | NOT IN DB | **APPROVE** — Structured incoming inspection with reject reason code + SCAR escalation FK. Currently binary Accept/Reject with no classification. |
| 22 | **ReturnMaterialAuthorization** + **RmaLineItem** | Claude P2-B | logistics | MEDIUM | NOT IN DB | **APPROVE** — Based on Metelix RMA pattern (only structured return tracking in organization). Part states: SANDED_RAW/UNSANDED_RAW/PAINTED. |
| 23 | **DowntimeEvent** | Claude P2-A + ChatGPT P2 | production | HIGH | NOT IN DB | **APPROVE** — 15-category taxonomy from Plant 2. Links to ProductionRun. Propose as cross-plant standard. |
| 24 | **ShiftStaffing** + **ShiftStaffingAssignment** | ChatGPT P2 | labor | MEDIUM-HIGH | NOT IN DB | **APPROVE at P3** — Operator-to-run-to-defect linkage. Wait for Plant 3-7 evidence on competency tracking before finalizing. |
| 25 | **PaintBatch** + **ColourVerification** | Claude P2-A | production | HIGH | NOT IN DB | **APPROVE** — Discrete batch model (fundamentally different from Plant 1 continuous bath). ColourVerification: L*/a*/b* at 25/45/75 degrees, delta-Ecmc, visual override flag. |
| 26 | **PaintTrial** + **PaintTrialBooth** | Claude P2-A | production | MEDIUM | NOT IN DB | **APPROVE at P3** — Trial lifecycle with per-booth parameters. Low urgency but addresses change management gap. |
| 27 | **WasteDisposalEvent** | ChatGPT P2 | compliance | LOW-MEDIUM | NOT IN DB | **DEFER** — Forms are blank drum labels with zero data. Scope decision needed. Only create if environmental compliance requirements confirmed. |

---

## QFM Overlap Detail

The Quality Forms Module (Reference_Architecture/Quality_Forms_Module/04_packages/) defines these inspection-domain entities in migrations 131-160:

| QFM Entity | Schema | Purpose | Audit Equivalent |
|------------|--------|---------|-----------------|
| `InspectionTemplateFamily` | inspection | Template versioning container | No equivalent — audit didn't propose template management |
| `InspectionTemplateRevision` | inspection | Template lifecycle (Draft/Review/Active) | No equivalent |
| `InspectionTemplateSection` | inspection | Form layout grouping | No equivalent |
| `InspectionTemplateField` | inspection | Individual form field definitions | No equivalent |
| `InspectionFieldCriteria` | inspection | Validation rules per field | No equivalent |
| `InspectionCriteria[Numeric\|Attribute\|Selection\|Text]` | inspection | Typed criterion details | No equivalent |
| `InspectionInstance` | inspection | Execution record | **InspectionRecord** (audit) |
| `InspectionFinding` | inspection | Defect findings | Part of **InspectionTestResult** (audit) |
| `InspectionAssignmentRule` | inspection | Routing rules | No equivalent |
| `InspectionScheduleRule` | inspection | Scheduling rules | No equivalent |
| `InspectionResponse[Numeric\|Attribute\|Text\|Selection\|Attachment]` | inspection | Typed response data | **InspectionTestResult** (audit) |
| `InspectionNcrLink` | inspection | Soft/hard NCR linking | Not in audit — audit assumed direct FK |
| `ProductionRun` | inspection | Production context | **ProductionRun** (audit) — same concept, different schema |

**Assessment:** QFM is significantly more mature than the audit proposals for inspection-domain entities. **However, Plant 2 reveals a gap in QFM:** the count-based routing inspection pattern (Good/Buff/Repaint/Scrap buckets) is not well-served by QFM's measurement-based InspectionResponse model. **Recommendation: Adopt QFM for measurement-based inspection; add InspectionDefectCount as a parallel child of InspectionInstance for count-based routing inspection.**

---

## Entities NOT Covered by QFM (Genuinely New — Combined Plant 1 + Plant 2)

### Group 1: Production Operations (P1 priority)
1. **LoadRecord** — Load-bar/carrier-level tracking (E-coat: single bar; Liquid: carrier number)
2. **CertificationRecord** — Ship-release evidence with hold/release lifecycle
3. **PaintBatch** + **ColourVerification** — Discrete paint batch tracking with lab-grade colour data (Plant 2)

### Group 2: Process & Lab (P1-P2 priority)
4. **ProcessParameterLog** — Header: per-line per-shift parameter capture (multi-coat support)
5. **ProcessParameterReading** — Child: individual readings with InSpec computed column + SpecMin/SpecMax/TargetValue
6. **LabAnalysis** — Header: per-line per-date lab analysis (bath sampling AND paint mix types)
7. **LabAnalysisReading** — Child: per-stage per-parameter readings (colour readings, viscosity, pH)

### Group 3: GP-12 Program (P2 priority)
8. **GP12Program** — Program lifecycle (Active→Monitoring→Exit→Closed)
9. **GP12InspectionRecord** — Bridge: GP12Program ↔ InspectionInstance
10. **Gp12ContainmentEvent** — Full containment lifecycle with customer notification (Plant 2)

### Group 4: Inspection Extensions (P1 priority, Plant 2-driven)
11. **InspectionDefectCount** — Count-based child of InspectionInstance for routing inspection
12. **CustomerInspectionProfile** — Dynamic form configuration with gate alarm thresholds

### Group 5: Logistics (P2 priority, Plant 2-driven)
13. **Shipment/PackSlip** + **ShipmentLine** — Outbound shipment with quality release gate
14. **ReceivingLogEntry** — Incoming inspection with structured reject + SCAR link
15. **ReturnMaterialAuthorization** + **RmaLineItem** — Customer return lifecycle

### Group 6: Post-Paint Operations (P1 priority, Plant 2-driven)
16. **PostPaintReworkEvent** + **PostPaintReworkDefect** — Rework lifecycle with defect/source linkage

### Group 7: Production Extensions (P2 priority, Plant 2-driven)
17. **DowntimeEvent** — Structured downtime with 15-category taxonomy
18. **PaintTrial** + **PaintTrialBooth** — Trial lifecycle with per-booth parameters

### Group 8: Supporting (P2-P3 priority)
19. **DocumentTemplate / DocumentRevision** — Form template management + revision control
20. **ShiftStaffing** + **ShiftStaffingAssignment** — Operator-to-run linkage

### Deferred
- **TrainingCompetencyRecord** — No evidence at Plant 1 or Plant 2; await Plants 3-7
- **WasteDisposalEvent** — Scope decision needed; Plant 2 forms are blank labels

---

## Proposed Migration Phasing (Revised for Plant 1 + Plant 2)

**Pre-condition:** QFM adjudication blockers (8 items) must be resolved before inspection entities can land. Non-inspection entities can proceed independently.

| Phase | Entities | Dependencies | Source | QFM Alignment |
|-------|----------|-------------|--------|---------------|
| **Phase 35** | `production.ProductionRun` + `production.LoadRecord` | None (uses existing ProductionLine, Shift, Equipment) | Plant 1 + Plant 2 confirm | ProductionRun replaces QFM `inspection.ProductionRun` — `production` schema |
| **Phase 36** | QFM Inspection entities + `quality.InspectionDefectCount` + `quality.CustomerInspectionProfile` | QFM adjudication resolved + Phase 35 | Plant 1 + Plant 2 | QFM-owned inspection + Plant 2 count-based extension |
| **Phase 37** | `production.ProcessParameterLog` + `ProcessParameterReading` (with SpecMin/Max/Target) | Phase 35 (optional FK to ProductionRun) | Plant 1 + Plant 2 confirm | Independent of QFM |
| **Phase 38** | `production.LabAnalysis` + `LabAnalysisReading` + `production.PaintBatch` + `production.ColourVerification` | Phase 35 (optional FK to ProductionRun) | Plant 1 + Plant 2 | Independent of QFM |
| **Phase 39** | `quality.GP12Program` + `GP12InspectionRecord` + `quality.Gp12ContainmentEvent` | Phase 36 (optional FK to InspectionInstance) | Plant 1 + Plant 2 | Links to QFM InspectionInstance |
| **Phase 40** | `quality.CertificationRecord` + `logistics.Shipment/PackSlip` + `logistics.ShipmentLine` | Phase 35 | Plant 1 + Plant 2 | Independent of QFM |
| **Phase 41** | `logistics.ReceivingLogEntry` + `logistics.ReturnMaterialAuthorization` + `logistics.RmaLineItem` | Phase 40 | Plant 2 | Independent of QFM |
| **Phase 42** | `postpaint.PostPaintReworkEvent` + `PostPaintReworkDefect` | Phase 35, Phase 36 | Plant 2 | Independent of QFM |
| **Phase 43** | `production.DowntimeEvent` | Phase 35 | Plant 2 | Independent of QFM |
| **Phase 44** | `dbo.MaintenanceLog` | None (uses existing Equipment) | Plant 1 + Plant 2 confirm | Independent of QFM |
| **Phase 45** | NCR enhancement (add ProductionRunId FK) + Document revision columns | Phase 35 | Plant 1 + Plant 2 confirm | Schema changes to existing tables |
| **Phase 46** | `production.PaintTrial` + `PaintTrialBooth` | Phase 38 | Plant 2 | Independent of QFM |
| **Phase 47** | `labor.ShiftStaffing` + `ShiftStaffingAssignment` | Phase 35 | Plant 2 | Independent of QFM |

**Note:** Phase numbers are illustrative — actual numbering depends on current migration state at execution time (currently at 150/Phase 34).

---

## Gap Closure Matrix (Updated for Plant 1 + Plant 2)

| Gap ID | Gap Name | Closed By | Fully Closed? |
|--------|----------|-----------|---------------|
| GAP-02 | Traceability chain breaks | ProductionRun + LoadRecord + Shipment | YES — enables load → coat → inspect → ship chain |
| GAP-04 | No PPM/yield calculation | QFM InspectionInstance + InspectionDefectCount + ProductionRun | YES — QuantityInspected + count-based defects per run |
| GAP-11 | No GP-12 exit gate | GP12Program + Gp12ContainmentEvent | YES — exit criteria + customer notification |
| GAP-12 | No dedicated Inspection entity | QFM InspectionInstance + InspectionDefectCount + CustomerInspectionProfile | YES — measurement-based AND count-based inspection |
| GAP-13 | Process params decoupled from quality | ProcessParameterLog + Reading (with Spec limits) | YES — links params to runs to NCRs with spec compliance |
| GAP-14 | No production run tracking | ProductionRun + LoadRecord | YES |
| GAP-15 | Lab chemistry not digitized | LabAnalysis + Reading + PaintBatch + ColourVerification | YES — covers both bath (Plant 1) and batch (Plant 2) |
| GAP-16 | GP-12 forms siloed per customer | GP12Program + QFM templates + CustomerInspectionProfile | YES — configurable per customer/part |
| GAP-17 | Cavity codes instead of counts | QFM InspectionFinding + LocationCode | YES |
| GAP-19 | No document revision control | DocumentRevision columns on Document | YES |
| GAP-20 | No packaging hold / shipment release | CertificationRecord + Shipment.QualityReleaseStatus | YES — dual mechanism |
| GAP-21 | OOS → NCR auto-trigger | ProcessParameterReading.InSpec + QFM InspectionNcrLink | PARTIAL — needs API workflow rule |
| GAP-22 | Post-paint rework black hole | PostPaintReworkEvent + PostPaintReworkDefect | YES — lifecycle tracking with source linkage |
| GAP-23 | Inspection-to-NCR disconnect | POST /v1/inspection/{id}/escalate + InspectionNcrLink | YES — bridges inspection to NCR |
| GAP-24 | Shipping-quality gate absent | Shipment.QualityReleaseStatus + CK_ShipmentLine_TraceToken | YES — database-enforced quality gate |
| GAP-26 | No spec limits on process params | ProcessParameterReading.SpecMin/SpecMax/TargetValue | YES — InSpec computed column |
| GAP-27 | Customer requirements not referenced | CustomerInspectionProfile.CustomerSpecReference | YES — spec reference per customer×part |

**17 of 28 gaps closed by entity proposals + QFM.** Remaining gaps are adoption (GAP-01, 05, 08, 09), calibration linkage (GAP-10), document control (GAP-06), line asymmetry (GAP-25), hidden customer (GAP-28), merged cells (GAP-18), and digital readiness (GAP-07).

---

## Status: APPROVED with QFM Alignment (Plant 1 + Plant 2)

All entity proposals are validated against cross-repo state:
- **6 entities** superseded by QFM (use QFM designs instead)
- **9 entities** genuinely new from Plant 1 (all confirmed by Plant 2 with extensions)
- **12 entities** genuinely new from Plant 2
- **1 entity** merged into another (PackagingHold → CertificationRecord)
- **2 entities** deferred (TrainingCompetencyRecord, WasteDisposalEvent)

**Combined total: ~27 new entities + 8 child entities across 7 schemas (quality, production, logistics, postpaint, labor, compliance, inspection/QFM)**

**Gate:** QFM adjudication blockers must be resolved before inspection-domain entities can land. Non-inspection entities (ProductionRun, LoadRecord, ProcessParameter, Lab, PaintBatch, GP12, Certification, Shipment, PostPaint, Downtime, Maintenance) can proceed immediately.
