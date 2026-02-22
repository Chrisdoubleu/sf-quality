# Phase 23 and 24 CONTEXT Enrichments

**Apply to:** `sf-quality-db/.planning/phases/23-*/23-CONTEXT.md` and `24-*/24-CONTEXT.md`
**When:** Before running `/gsd:plan-phase 23` and `/gsd:plan-phase 24` respectively
**Source:** Execution_Plan.md Step 0, Pattern_Mapping.md v4

---

## Instructions

These are enrichment additions to the existing generic CONTEXT stubs. The stubs already contain cross-repo review requirements and entry/exit criteria. **Merge** this content in — do not replace the existing stub content.

Specifically, add these sections to each CONTEXT file after the existing "Required Cross-Repo Inputs" section.

---

## Phase 23: Platform Governance, Documentation, and Deployment

### Specific Scope for This Phase

This phase closes out v2.0 by ensuring the platform is in a deployable, governed, and documented state. It is the last phase before v2.0 is archived and v3.0 begins.

**Key deliverable:** DB contract manifest refresh is the primary production-gate deliverable of this phase.

#### 1. DB Contract Manifest Refresh (CRITICAL)

The `db-contract-manifest.json` is currently v1.0.0 and reflects the state before Phase 21. It is missing:
- 9 knowledge retrieval views added in Phase 21 (migrations 122-130):
  - `quality.vw_DefectKnowledge`
  - `quality.vw_RootCauseGuidance`
  - `quality.vw_InvestigationSteps`
  - `quality.vw_TestMethodGuidance`
  - `quality.vw_DispositionGuidance`
  - `quality.vw_ContainmentGuidance`
  - `quality.vw_ParameterCheckGuidance`
  - `quality.vw_ControlPointGuidance`
  - `quality.vw_ConfusionPairWarnings`
- 1 advisory procedure: `quality.usp_GetDefectKnowledge` (or equivalent advisory SP)
- Any new objects added in Phase 21.1 (taxonomy v3 migration 130)

**Action:** Update manifest to reflect actual state (v1.1.0 or increment as appropriate), then confirm API-side snapshot is aligned.

#### 2. Security Grants Closure (SEC-01)

If any v2.0 objects (knowledge views, advisory procs, any Phase 23-specific objects) require grants to the API application identity, add them here. Follow the existing grant pattern from `database/security/grants/`.

#### 3. Deployment Orchestration Script

Verify the deployment orchestration script covers migrations 001 through current (130+). Ensure:
- All apply scripts are in order
- Verify and smoke scripts are included
- Phase-level validation gates are present

#### 4. Documentation Closure

- Update `ARCHITECTURE.md` to reflect the knowledge schema and retrieval layer (Phase 18-21)
- Confirm `INTEGRATIONS.md` accurately describes the API consumer surface for v2.0 additions
- Confirm `CONCERNS.md` captures any known limitations of the Phase 22 deferral impact

**Plans suggested:** 2–3 (manifest refresh + grants + deployment verification + doc updates)

---

## Phase 24: Incoming Substrate and NCR Integration

### Specific Scope for This Phase

This phase adds the DB-side infrastructure for incoming substrate (raw material) tracking and its integration point with the NCR lifecycle. This establishes the substrate data model that the App quality forms will need in later phases.

**Key decision already made:** The substrate lookup model follows the universal knowledge pattern — substrate types and grades are reference data, not hardcoded enums.

#### 1. Incoming Substrate Reference Data Tables

Create or confirm the following substrate reference tables (following existing ReferenceData pattern):
- `quality.SubstrateType` (substrate material categories)
- `quality.SubstrateGrade` (FK to SubstrateType, specific grades/specs)

Seed with representative substrate types (e.g., primer, topcoat, e-coat bath chemicals) if applicable to Select Finishing's incoming material types.

#### 2. NCR-Substrate Linking

Extend `quality.NonConformanceReport` (or equivalent NCR entity) to capture incoming substrate reference:
- `SubstrateTypeId INT NULL FK → quality.SubstrateType`
- `SubstrateGradeId INT NULL FK → quality.SubstrateGrade`
- `BatchLotNumber NVARCHAR(100) NULL`

#### 3. Substrate Lookup Procedures

Add DB-facing procs for the API to call:
- `quality.usp_GetSubstrateTypes` (lookup list)
- `quality.usp_GetSubstrateGrades` (optionally filtered by SubstrateTypeId)
- Update NCR CRUD procs to include substrate FK columns where appropriate

#### 4. Contract Manifest Update

After this phase, refresh `db-contract-manifest.json` again to include new substrate procs/views before starting v3.0.

**Plans suggested:** 2 (substrate schema + NCR extension + procs, then verify/deploy)

**Cross-repo impact:** The API's NCR endpoints will need updated DTO models in a future phase to expose the substrate fields. Flag this in the 24-CONTEXT.md under "Cross-Repo Dependencies."
