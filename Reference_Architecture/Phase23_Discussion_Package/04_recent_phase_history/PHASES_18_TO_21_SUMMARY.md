# Phases 18–21.1 Summary: What Was Built (v2.0 Knowledge Layer)

**Purpose:** Context for external AI — this is what Phase 23 must govern, document, and deploy correctly.

---

## Phase 18: Knowledge Schema Foundation (migration 125) — COMPLETE 2026-02-18

**What was built:** 9-table defect knowledge schema in `dbo` schema.

| Table | Purpose |
|-------|---------|
| `dbo.DefectTypeRootCause` | Root causes per defect code. Columns: DefectTypeId (FK), LineTypeId FK (NULL = universal), IshikawaCategoryId FK, CauseLevelId FK, RootCauseCode (natural key), CauseDescription, SortOrder, IsActive |
| `dbo.DefectTypeInvestigationStep` | Step-by-step investigation guidance. InvestigationCode, StepDescription, StepOrder |
| `dbo.DefectTypeTestMethod` | Test methods with method codes and descriptions. TestMethodCode |
| `dbo.DefectTypeDispositionGuidance` | Disposition decision guidance. DispositionCode |
| `dbo.DefectTypeContainmentGuidance` | Immediate containment actions. ContainmentCode |
| `dbo.DefectTypeConfusionPair` | Easily confused defect pairs. PairCode, ConfusedWithDefectTypeId FK |
| `dbo.DefectTypeParameterCheck` | Process parameter checks. ParameterCode |
| `dbo.DefectTypeStandardReference` | Standards cited (CQI-12, ASTM). StandardCode |
| `dbo.DefectTypeControlPoint` | Control points in the process. ControlCode |

**All 9 tables share:**
- IDENTITY PKs, DefectTypeId + LineTypeId FKs
- Natural key UNIQUE constraints (DefectTypeId + LineTypeId + XxxCode)
- Governance columns: IsVerified BIT, VerifiedBy INT, VerifiedDate DATE, ContentSource NVARCHAR(50) (values: CLAUDE, CHATGPT, QE_AUTHORED, PRODUCTION_DATA)
- Filtered indexes: ON IsActive=1
- Audit triggers via `dbo.usp_CreateAuditTrigger` pattern
- CHECK constraints on enum columns

**Key architecture rule:** Knowledge tables have NO RLS enrollment. PlantId = NULL on all rows. They are reference data, not plant-scoped transactional data.

**Verification:** 92/92 structural checks passed.

---

## Phase 19: E-coat and Powder Seed Data (migrations 126a, 126b) — COMPLETE 2026-02-18

**What was built:** Knowledge rows for 41 defect codes.

- Migration 126a: 18 e-coat codes, ~462 rows. Dimension pre-reqs included:
  - `dbo.IshikawaCategory`: MOTHER_NATURE → ENVIRONMENT rename
  - `dbo.CauseLevel`: NODETECT + SYSTEMIC values added
- Migration 126b: 23 powder codes, ~645 rows. 23 NODETECT retrofits + 7 SYSTEMIC rows.

**Total after Phase 19:** 1,103 knowledge rows.

**Naming conventions:**
- RootCause codes: RC-[DEFECTCODE]-[SUFFIX] (e.g., RC-FISHEYE-CONTAM)
- InvestigationStep codes: INV-[DEFECTCODE]-[SUFFIX]
- TestMethod codes: TM-[DEFECTCODE]-[SUFFIX]
- DispositionGuidance codes: DG-[DEFECTCODE]-[SUFFIX]
- ContainmentGuidance codes: CG-[DEFECTCODE]-[SUFFIX]
- ConfusionPair codes: CP-[DEFECTCODE]-[CONFUSEDWITH] (dual-use with ControlPoint CP- prefix)
- ParameterCheck codes: PC-[DEFECTCODE]-[SUFFIX]
- StandardReference codes: SR-[DEFECTCODE]-[SUFFIX]
- ControlPoint codes: CP-[DEFECTCODE]-[SUFFIX]

**Key decisions locked:**
- NODETECT/SYSTEMIC rows use CauseLevelCode=ROOT (not native NODETECT/SYSTEMIC values) — identified by IshikawaCategoryCode + naming suffix
- No -PW- infix on powder codes (KNOW-13 naming convention remains partially deferred to PLAT-02)

---

## Phase 20: Liquid and Cross-Process (migrations 126c, 126d, 127a) — COMPLETE 2026-02-18

**What was built:**
- Migration 126c: 27 SURF/COLOR codes, ~785 rows (universal foundation + liquid overlay)
- Migration 126d: 6 reverse confusion pair rows (e-coat bidirectionality fix — V05 BLOCKER)
- Migration 127 Section A: 99 containment guidance rows for 27 SURF/COLOR codes

**Architecture enforced:** Universal rows (LineTypeId=NULL) are process-agnostic — they serve ALL process families. Process-specific rows add mechanism-specific detail. This is the foundation of PLAT-01 documentation.

**Total after Phase 20:** 1,894 knowledge rows across 68 defect codes (18 e-coat + 23 powder + 27 SURF/COLOR).

**Verification:** V01-V14 all PASS including V05 (bidirectionality BLOCKER), V12 (line-type leakage), V13 (scope leakage), V14 (string domain validation).

**Open concerns for Phase 23:**
- RC-CURMEK-CONTAM: "Powder chemistry" in universal row — forward-fix candidate (change to "Coating chemistry")
- ConfusionPair exception allowlist (V02B): 8 codes pre-Phase-21.1, may need review after taxonomy cleanup

---

## Phase 21: Knowledge Retrieval Layer (migrations 128, 129) — COMPLETE 2026-02-19

**What was built:**

**Migration 128** — 9 knowledge views + advisory SP + queue view enhancement:
- 9 UNFILTERED knowledge views (include IsActive=0 rows for analytics/admin):
  - `dbo.vw_DefectKnowledge_RootCauses`
  - `dbo.vw_DefectKnowledge_InvestigationSteps`
  - `dbo.vw_DefectKnowledge_TestMethods`
  - `dbo.vw_DefectKnowledge_DispositionGuidance`
  - `dbo.vw_DefectKnowledge_ContainmentGuidance`
  - `dbo.vw_DefectKnowledge_ConfusionPairs`
  - `dbo.vw_DefectKnowledge_ParameterChecks`
  - `dbo.vw_DefectKnowledge_StandardReferences`
  - `dbo.vw_DefectKnowledge_ControlPoints`
- `quality.usp_GetDefectKnowledge` — advisory SP:
  - Parameters: @DefectTypeId INT, @LineTypeId INT NULL, @Sections NVARCHAR(200) NULL (CSV from 9-item allowlist), @SeverityRatingId INT NULL, @NcrId INT NULL, @CallerAzureOid NVARCHAR(128) NULL
  - Returns: up to 9 result sets, process-specific rows before universal rows, merged without duplicates
  - @NcrId path: auto-resolves DetectionLineStageId → ProductionLine → LineType (requires @CallerAzureOid for RLS session)
- `quality.vw_NcrOperationalQueue` enhanced: DefectCode, DefectName, DefectCategoryName, ProcessZoneName columns added

**Migration 129** — CHECK expansion + pre-population SP:
- `dbo.RootCause.HypothesisSource` CHECK expanded to include `N'DefectTypeRootCause'`
- `quality.usp_PrePopulateRootCauses` — returns candidate hypotheses for CAPA root cause entry:
  - Parameters: @DefectTypeId, @LineTypeId, @RootCauseTypeId
  - Returns rows with IshikawaCategoryId and CauseLevelId resolved (NOT an INSERT — returns data only)

**Gate SP knowledge mapping document:** `21-GATE-KNOWLEDGE-MAPPING.md` — all 18 gates mapped to @Sections CSV strings. Gate SPs themselves were NOT modified.

**Verification:** V01-V13 (12 PASS, 1 SKIP — V06 NcrId path untested in zero-NCR dev environment).

---

## Phase 21.1: Defect Taxonomy v3 Migration (migration 130) — COMPLETE 2026-02-20

**What was built:**

- **Goal:** Clean 112+ leaf codes to 82 observable-defect-only codes. Remove cause/test/crutch codes.
- **FK remap:** All knowledge table rows remapped from merge-source codes to survivor codes. Zero data loss.
- **New codes:** SURF-OVERSPRAY, SURF-MASKFAIL, THICK-PLUG (3 gap-closure codes, seeded with knowledge)
- **Deactivated:** EQUIP and CONTAM categories (and all children), GEN-UNDEF, v1 legacy codes from migration 020
- **Severity rebaseline:** All DefaultSeverityId values updated to AIAG-VDA 1-10 scale for 82 active codes
- **ConfusionPair remap:** Requires NOCHECK/CHECK choreography for `CK_DefectTypeConfusionPair_NotSelf`
- **Static validation:** 0 violations across 133 migration files

**Result:** 82 active leaf codes, 12 active categories, 1,894 knowledge rows preserved.

---

## What Phase 22 Was Supposed to Add (DEFERRED)

Phase 22 was going to create:
- `analytics` schema
- 7 cross-process analytics views (DefectPareto, RootCauseDistribution, ProcessZoneConcentration, RecurrenceTracking, EffectivenessTrending, ControlPointGapAnalysis, v1.0 KPI assessment)
- Security grants for all v2.0 objects

**Why it was deferred:** Schema still evolving, no API/app consumers exist, role architecture not finalized, dev has zero NCR data to validate analytics views.

**Impact on Phase 23:** SEC-01 (security grants) moved inline to Phase 23. Analytics views remain not built.

---

## The DB Object Surface Phase 23 Must Govern

**Procedures added in v2.0 (Phases 18-21.1) that need grant assessment:**
- `quality.usp_GetDefectKnowledge`
- `quality.usp_PrePopulateRootCauses`

**Views added in v2.0 (Phase 21) that need grant assessment:**
- `dbo.vw_DefectKnowledge_RootCauses`
- `dbo.vw_DefectKnowledge_InvestigationSteps`
- `dbo.vw_DefectKnowledge_TestMethods`
- `dbo.vw_DefectKnowledge_DispositionGuidance`
- `dbo.vw_DefectKnowledge_ContainmentGuidance`
- `dbo.vw_DefectKnowledge_ConfusionPairs`
- `dbo.vw_DefectKnowledge_ParameterChecks`
- `dbo.vw_DefectKnowledge_StandardReferences`
- `dbo.vw_DefectKnowledge_ControlPoints`

**Enhanced view (Phase 21) that may already have grants:**
- `quality.vw_NcrOperationalQueue` (existing, enhanced — existing grants should still apply)

**Note:** The `db-contract-manifest.json` already lists all of the above. The grant question is whether `EXECUTE`/`SELECT` grants exist for these objects in the DB roles from migration 123.
