# Roadmap: Select Finishing Quality Management Database

## Milestones

- 🚧 **v2.0 Quality Intelligence Platform** — Phases 18-24 (in progress)
- ✅ **v1.1 NCR Disposition Operationalization** — Phases 12-17 (shipped 2026-02-17, GO WITH ACCEPTED WARNINGS)
- ✅ **v1.0 Quality System Backend** — Phases 1-11 (shipped 2026-02-15)

## Phases

### 🚧 v2.0 Quality Intelligence Platform (In Progress)

**Milestone Goal:** Transform the workflow enforcement system into a quality intelligence platform — structured knowledge that actively guides every decision in the quality lifecycle through a six-layer cascade: Taxonomy, Classification, Knowledge, Decision Support, Transactions, Analytics.

**Architecture:** Six-layer cascade with strict advisory/authoritative separation. Knowledge retrieval is a companion to gate SPs, never embedded in them. Humans make the final decision.

**Migration range:** 125-130+
**Requirement areas:** KNOW-01..16, INTEL-01..06, ANALYTICS-01..07, PLAT-01..06, SEC-01, DEPLOY-01 (37 total)

- [x] **Phase 18: Knowledge Schema Foundation** - Deploy 9-table defect knowledge schema with audit triggers, constraints, and structural verification — completed 2026-02-18
- [x] **Phase 19: Seed Data -- E-coat and Powder** - Deploy seed data for 41 codes (18 e-coat + 23 powder) with NODETECT/SYSTEMIC retrofit and V01-V13 verification — completed 2026-02-18
- [x] **Phase 20: Seed Data -- Liquid Synthesis and Cross-Process Verification** - Synthesized and deployed liquid seed data (27 codes, 785 rows) plus 99 containment guidance rows, verified unified knowledge across all 68 codes (1894 rows, V01-V14 PASS) -- completed 2026-02-18
- [x] **Phase 21: Knowledge Retrieval Layer** - Advisory SP, 9 knowledge views, operational view enhancement, root cause pre-population, gate SP integration documentation -- completed 2026-02-19
- [x] **Phase 21.1: Defect taxonomy v3 migration** (INSERTED) -- completed 2026-02-20
- [ ] **Phase 22: Analytics Foundation and Security** - DEFERRED (schema still evolving, no consumers, role architecture not locked). See `22-DEFERRAL.md`. SEC-01 grant closure is handled in Phase 23.
- [ ] **Phase 23: Platform Governance, Documentation, and Deployment** - Cascade pattern documentation, onboarding template, extension model, content maintenance model, feedback loop, deploy orchestration
- [ ] **Phase 24: Incoming Substrate and NCR Integration** - IncomingSubstrateDefectReason lookup table, NCR FK for substrate sub-categorization, temporal ALTER choreography, frontend integration contract

## Execution Notes

- Every future phase plan/research cycle must include explicit cross-repo checks in both `sf-quality-api` and `sf-quality-app`.
- After each execute wave, run `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` and include the result in the wave summary.

## Phase Details

### Phase 18: Knowledge Schema Foundation
**Goal**: The 9-table defect knowledge schema exists in the migration chain with all constraints, indexes, and audit triggers -- ready to receive seed data
**Depends on**: Phase 17 (v1.1 complete, migration 123 is baseline)
**Requirements**: KNOW-01
**Success Criteria** (what must be TRUE):
  1. Migration 125 deploys cleanly to dev -- 9 knowledge tables exist in dbo schema with IDENTITY PKs, DefectTypeId + LineTypeId FKs, and natural key UNIQUE constraints
  2. Audit triggers fire on all 9 tables (verified via test INSERT/UPDATE/DELETE producing audit.AuditLog rows with @PlantIdColumn=NULL)
  3. Zero knowledge tables appear in sys.security_predicates (no accidental RLS enrollment)
  4. CHECK constraints on enum columns reject invalid values; filtered indexes exist on active rows
  5. Migration is idempotent -- re-running 125 produces no errors and no duplicate objects
**Plans:** 2 plans

Plans:
- [x] 18-01-PLAN.md — Create and deploy migration 125 (9 knowledge tables with governance columns, constraints, indexes, audit triggers) — completed 2026-02-18
- [x] 18-02-PLAN.md — Write and run Verify-Phase18.sql structural verification against deployed schema — completed 2026-02-18

### Phase 19: Seed Data -- E-coat and Powder
**Goal**: 41 of 68 defect codes have complete knowledge (root causes, investigation steps, test methods, disposition guidance, containment guidance, parameter checks, control points, standard references) deployed and verified against V01-V13
**Depends on**: Phase 18 (knowledge tables must exist for MERGE inserts)
**Requirements**: KNOW-03, KNOW-04, KNOW-05, KNOW-06, KNOW-07, KNOW-08, KNOW-12, KNOW-13
**Assumptions**: Finalized in `19-ASSUMPTIONS-FINAL.md` (2026-02-18)
**Content audit**: `19-CONTENT-QUALITY-AUDIT-MATRIX.md` — 41 codes, 29 missing NODETECT, 7 SYSTEMIC candidates, 6 MOTHER_NATURE corrections, 7 ConfusionPair gaps accepted
**Success Criteria** (what must be TRUE):
  1. Migration 126a deploys 18 e-coat codes (~462+ rows incl. 6 NODETECT retrofit) with pre-flight DefectCode/LineType existence validation that fails loudly on missing targets; dimension pre-reqs (IshikawaCategory ENVIRONMENT rename, CauseLevel NODETECT/SYSTEMIC expansion) execute first
  2. Migration 126b deploys 23 powder codes (~645+ rows incl. 23 NODETECT + ~7 SYSTEMIC retrofit) with pre-flight validation; NODETECT/SYSTEMIC rows use CauseLevelCode=ROOT per phase contract
  3. E-coat verification passes V01-V13 (upgraded from V1-V5), including V12 line-type leakage and V13 scope leakage checks
  4. Powder verification passes V01-V13, including V12/V13, with NODETECT/SYSTEMIC retrofit rows validated
  5. Verify-Phase19.sql passes with V02A (8-table mandatory coverage, all 41 codes) and V02B (ConfusionPair exception allowlist = exactly 7 codes: GEN-DOCERR, GEN-UNDEF, CURE-CHEM, CURE-GELTIME, EQUIP-FILTER, EQUIP-PUMP, THICK-LAYERIMB)
**Locked governance decisions:**
  - GOV-01: Core8 hard gate, ConfusionPair conditional advisory (V02A/V02B split)
  - GOV-02: No -PW- infix in Phase 19, no mixed-style renaming for retrofit rows
  - GOV-03: Strip dbo.DefectType.Description MERGE from 126a/126b (knowledge tables + dimension pre-reqs only)
**Plans:** 3 plans

Plans:
- [x] 19-01-PLAN.md — Author retrofit content draft (36 statements) + e-coat migration 126a with dimension pre-reqs, corrections, and 6 NODETECT retrofits — completed 2026-02-18
- [x] 19-02-PLAN.md — Author powder migration 126b with 23 NODETECT + 7 SYSTEMIC retrofits + deploy 126a/126b to dev — completed 2026-02-18
- [x] 19-03-PLAN.md — Author and run Verify-Phase19.sql (V01-V13) + Apply-Phase19.ps1 + planning closeout — completed 2026-02-18

### Phase 20: SURF/COLOR Knowledge Foundation + Liquid Overlay + Cross-Process Verification
**Goal**: Build the universal knowledge platform for all 27 SURF/COLOR defect codes (the foundation that every process family inherits) plus the liquid-specific overlay — completing the knowledge layer for v2.0 with 68 codes across 3 process families deployed, harmonized, and verified
**Depends on**: Phase 19 (e-coat/powder deployed; universal row ownership established for ADHES/PRETR/CONTAM/GEN/THICK/CURE/EQUIP; MERGE patterns validated)
**Requirements**: KNOW-02, KNOW-06, KNOW-09, KNOW-10, KNOW-11, KNOW-14
**Architectural intent**: Universal knowledge is the platform; process-specific knowledge is the overlay. Universal rows (LineTypeId=NULL) must be written process-agnostically — they serve ALL process families, not just liquid. See `20-ASSUMPTIONS-FINAL.md` Section 1A.
**Assumptions**: Finalized in `20-ASSUMPTIONS-FINAL.md` (2026-02-18) — architectural review with governance decisions locked, Codex assessment reconciled
**Success Criteria** (what must be TRUE):
  1. Migration 126c deploys universal foundation + liquid overlay for 27 SURF/COLOR codes (~700-900 rows, ~70% universal / ~30% LIQUID-specific) — universal content is process-agnostic, descriptions included (GOV-05), ContentSource/IsVerified populated
  2. Migration 126d forward-fixes 6 one-way e-coat confusion pairs from 126a — V05 bidirectionality becomes a BLOCKER across all 68 codes
  3. Migration 127 Section A deploys 99 containment guidance rows for 27 SURF/COLOR codes — all universal, CG- prefix, 10-increment SortOrder
  4. Cross-process V01-V14 verification passes across all 68 codes using reusable Verify-Phase20.sql — zero orphan FKs, zero duplicate natural keys, confusion pair bidirectionality complete, no line-type or scope leakage, string domain validation (DispositionCode, ContainmentCode, ProcessZoneCode)
  5. Knowledge harmonization audit documents cross-process consistency — includes universal content language review of 126a/126b for process-specific language leakage, naming convention inventory, knowledge ownership registry
  6. IsVerified/VerifiedBy/VerifiedDate columns documented as optional tracking metadata for content reviewed by the project owner
**Plans**: 3 plans

Plans:
- [x] 20-01-PLAN.md — Synthesize FINAL SQL: universal foundation + liquid overlay for 27 SURF/COLOR codes (~733 rows) + summary markdown -- completed 2026-02-18
- [x] 20-02-PLAN.md — Promote to migrations (126c + 126d + 127 Section A), author Apply-Phase20.ps1, deploy to dev (785 + 6 + 99 rows) -- completed 2026-02-18
- [x] 20-03-PLAN.md — Reusable V01-V14 verification (68 codes, all PASS), harmonization audit, content quality audit, planning closeout -- completed 2026-02-18

### Phase 21: Knowledge Retrieval Layer
**Goal**: Quality engineers, inspectors, and operators can retrieve structured defect knowledge through an advisory SP and views -- knowledge surfaces in the triage queue and is documented for gate SP companion use
**Depends on**: Phase 20 (seed data complete; advisory SP needs populated tables to return meaningful results and for smoke testing)
**Requirements**: INTEL-01, INTEL-02, INTEL-03, INTEL-04, INTEL-05
**Assumptions**: Finalized in `21-ASSUMPTIONS-FINAL.md` (2026-02-18) — 16 sections, 11 decisions (D21-01..D21-11), 13 verification checks (V01-V13)
**Migrations**: 128 (retrieval layer: 9 views + advisory SP + queue view ALTER), 129 (temporal choreography: CHECK expansion + pre-population SP)
**Success Criteria** (what must be TRUE):
  1. `quality.usp_GetDefectKnowledge` accepts @DefectTypeId, @LineTypeId, @Sections (tokenized CSV from 9-item allowlist), @SeverityRatingId, @NcrId, @CallerAzureOid and returns up to 9 result sets with process-specific rows before universal rows; @NcrId auto-resolves via DetectionLineStageId → ProductionLine → LineType derivation chain with RLS session context
  2. 9 per-table knowledge views (dbo.vw_DefectKnowledge_RootCauses, _InvestigationSteps, _TestMethods, etc.) return human-readable UNFILTERED output joining DefectType + LineType names (includes IsActive=0 rows for analytics/admin use)
  3. `quality.vw_NcrOperationalQueue` shows DefectCode, DefectName, DefectCategoryName, TypicalProcessZoneId, and ProcessZoneName -- operators see defect classification in the triage queue
  4. Gate SP integration is documented gate-by-gate (which knowledge sections surface at each of 18 gate transitions) using companion advisory pattern -- existing gate SPs are NOT modified
  5. `quality.usp_PrePopulateRootCauses` returns candidate hypotheses with IshikawaCategoryCode→IshikawaCategoryId and CauseLevelCode→CauseLevelId resolved; `dbo.RootCause.HypothesisSource` CHECK expanded to include `N'DefectTypeRootCause'` via temporal OFF/ALTER/ON choreography
**Plans:** 3 plans

Plans:
- [x] 21-01-PLAN.md — Author migration 128: 9 knowledge views (INTEL-02) + advisory SP quality.usp_GetDefectKnowledge (INTEL-01) + queue view enhancement (INTEL-03) -- completed 2026-02-19
- [x] 21-02-PLAN.md — Author migration 129: CHECK expansion + pre-population SP (INTEL-05) + gate SP knowledge mapping documentation (INTEL-04) -- completed 2026-02-18
- [x] 21-03-PLAN.md — Author Apply-Phase21.ps1 + Verify-Phase21.sql (V01-V13), deploy to dev, verify, planning closeout -- completed 2026-02-19

### Phase 21.1: Defect Taxonomy v3 Migration (INSERTED)
**Goal**: The v2 taxonomy is cleaned to remove cause/test/crutch codes, consolidate redundant leaves via FK remap, add 3 missing gap-closure codes, and rebaseline all DefaultSeverityId values to AIAG-VDA 1-10 — resulting in ~82 observable, trainable leaf codes with preserved knowledge investment
**Depends on**: Phase 21 (knowledge retrieval layer complete; migration 130 remaps knowledge FKs that were seeded in Phases 19-20)
**Requirements**: KNOW-02 (taxonomy quality)
**Migration**: 130_defect_taxonomy_v3_cleanup.sql
**Success Criteria** (what must be TRUE):
  1. Migration 130 deploys to dev without errors — 112+ leaf codes consolidated to ~82 observable-defect-only codes
  2. All 1,894 knowledge rows preserved via FK remap across 11 tables (zero data loss)
  3. 3 new gap-closure codes active (SURF-OVERSPRAY, SURF-MASKFAIL, THICK-PLUG) with AIAG-VDA severity
  4. EQUIP and CONTAM categories deactivated with zero active children; GEN-UNDEF deactivated
  5. All DefaultSeverityId values rebaselined to AIAG-VDA 1-10 scale for ~82 active codes
  6. Verification suite passes all 12 THROW checks with zero errors
  7. v1 legacy codes from migration 020 deactivated
**Plans:** 2 plans

Plans:
- [x] 21.1-01-PLAN.md — Promote migration 130 + verification SQL, create Apply-Phase21-1.ps1 deploy script, deploy to dev, verify -- completed 2026-02-20
- [x] 21.1-02-PLAN.md — Planning closeout (STATE.md, ROADMAP.md, PROJECT.md, REQUIREMENTS.md, CONCERNS.md) + rev2 file cleanup -- completed 2026-02-20

### Phase 22: Analytics Foundation and Security — DEFERRED
**Goal**: Leadership and quality managers can see cross-process analytics (Pareto, root cause distribution, recurrence, effectiveness) through dedicated views with appropriate security grants for all v2.0 objects
**Status**: DEFERRED (2026-02-21). See `22-DEFERRAL.md` for full rationale.
**Deferral reason**: Schema still evolving (views create column dependencies that break on schema changes), no API/app consumers exist, role architecture not finalized. SEC-01 grant closure moved to Phase 23.
**Depends on**: Phase 21 (retrieval layer stable; analytics views reference knowledge tables whose column names must be finalized; security grants cover retrieval + analytics objects together)
**Requirements**: ANALYTICS-01, ANALYTICS-02, ANALYTICS-03, ANALYTICS-04, ANALYTICS-05, ANALYTICS-06, ANALYTICS-07, INTEL-06
**Preconditions to revisit**: (1) schema stable, (2) real consumers exist, (3) role architecture locked, (4) transactional data available
**Plans**: None — deferred

### Phase 23: Platform Governance, Documentation, and Deployment
**Goal**: The quality intelligence platform is deployable as a verified unit with documented extension patterns, governance controls, and a repeatable onboarding model for future process families and knowledge domains
**Depends on**: Phase 21.1 (all deployed database objects through migration 130; Phase 22 deferred — documentation covers what's deployed today, not analytics views)
**Requirements**: PLAT-01, PLAT-02, PLAT-03, PLAT-04, PLAT-05, PLAT-06, DEPLOY-01, SEC-01, KNOW-13 (closure via PLAT-02)
**Success Criteria** (what must be TRUE):
  1. DB contract manifest is refreshed to current migration surface (through migration 130) and cross-repo snapshot alignment notes are documented
  2. Six-layer cascade pattern is documented as a repeatable model with layer contracts, retrieval precedence, and universal/process-specific layering rules
  3. Process family onboarding template exists -- step-by-step for adding a new process family (e.g., ANODIZE) with bridge table rows, seed file template, V01-V13 verification, no schema changes needed
  4. IsVerified governance columns documented as optional content tracking (not a gate or blocker); update-via-migration workflow for content corrections documented
  5. Internal data feedback loop is documented -- how production NCR patterns improve knowledge base over time (likelihood ranking updates, gap identification from unmatched root causes, coverage expansion triggers)
  6. Security grant coverage for deployed v2.0 objects is verified and updated inline as needed
  7. Core planning documents and codebase mapping docs are updated with no conflicting phase pointers or stale migration counts
**Plans**: 2-3 plans

Plans:
- [ ] 23-01: Contract manifest refresh + security grant closure + cross-repo artifact drift notes
- [ ] 23-02: Platform governance documentation closure (PLAT-01..06, KNOW-13 finalization path)
- [ ] 23-03: Deploy and planning governance closure (DEPLOY-01 + planning/codebase metadata reconciliation)

### Phase 24: Incoming Substrate and NCR Integration
**Goal**: Incoming substrate defects (DMG-SUB) have a controlled sub-reason picklist deployed to the database with NCR FK integration -- inspectors can categorize the specific incoming defect type when writing NCRs against DMG-SUB
**Depends on**: Phase 18 (knowledge schema exists), Phase 20 (liquid seed data deployed -- migration 127 Section A containment rows use DefectTypeContainmentGuidance from migration 125)
**Requirements**: KNOW-15, KNOW-16
**Success Criteria** (what must be TRUE):
  1. Migration 127 Section B creates `dbo.IncomingSubstrateDefectReason` with 10 seed values (SUB-SPLAY through SUB-SEAL), SubstrateType column (MOLDED/FORMED/MACHINED/UNIVERSAL), standard audit columns, and audit trigger
  2. Migration 127 Section C adds nullable `IncomingSubstrateDefectReasonId` FK to `quality.NonConformanceReport` with temporal ALTER choreography (versioning off, ALTER both base + history, versioning on)
  3. Lookup table is process-agnostic -- SubstrateType filtering enables any process family (e-coat metal stampings, powder metal parts, liquid molded plastics) to use the same table with relevant seed rows
  4. Frontend integration contract documented: conditional dropdown visibility when DMG-SUB selected, required in that context
  5. Sub-reason picklist pattern documented as extensibility template -- if other defect codes (DMG-HANDLING, equipment-related) need sub-reasons in the future, Phase 24's architecture is the repeatable model
**Plans**: 2 plans (Plan 01: DDL + seed + NCR FK; Plan 02: Verify + integration contract documentation)

Plans:
- [ ] 24-01: Deploy IncomingSubstrateDefectReason table, seed data, and NCR FK (migration 127 Sections B+C)
- [ ] 24-02: Verify deployment, document frontend integration contract and sub-reason extensibility pattern

---

<details>
<summary>✅ v1.0 Quality System Backend (Phases 1-11) — SHIPPED 2026-02-15</summary>

- [x] Phase 1: Infrastructure & Security Foundation (3/3 plans) — completed 2026-02-11
- [x] Phase 2: Reference Data & Dimension Tables (3/3 plans) — completed 2026-02-11
- [x] Phase 3: Core Quality Event Entities (5/5 plans) — completed 2026-02-12
- [x] Phase 4: RCA Methodology Tables (5/5 plans) — completed 2026-02-12
- [x] Phase 5: Workflow Engine & Task Management (4/4 plans) — completed 2026-02-12
- [x] Phase 6: Codebase Hardening & Application Layer (5/5 plans) — completed 2026-02-12
- [x] Phase 7: Optimization & Integration Testing (1/4 plans, 3 deferred) — 07-01 verified 2026-02-13
- [x] Phase 8: Production Topology Expansion (6/6 plans) — completed 2026-02-14
- [x] Phase 9: Defect Taxonomy & Quality Integration (2/2 plans) — completed 2026-02-15
- [x] Phase 10: Domain Enrichment & Cutover Hardening (4/4 plans) — completed 2026-02-15
- [x] Phase 11: Production Deployment (3/3 plans) — completed 2026-02-15

Full details: [milestones/v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md)

</details>

<details>
<summary>✅ v1.1 NCR Disposition Operationalization (Phases 12-17) — SHIPPED 2026-02-17</summary>

- [x] Phase 12: Reconciliation and Baseline (3/3 plans) — completed 2026-02-15
- [x] Phase 13: Schema Foundation (3/3 plans) — completed 2026-02-15
- [x] Phase 14: Authority and Workflow Alignment (5/5 plans) — completed 2026-02-16
- [x] Phase 15: Gate Stored Procedures (6/6 plans) — completed 2026-02-16
- [x] Phase 16: Views, Outbox, and Security Grants (4/4 plans) — completed 2026-02-17
- [x] Phase 17: Deploy Validation and Cutover Readiness (4/4 plans) — completed 2026-02-17

Full details: [milestones/v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md)

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Infrastructure & Security Foundation | v1.0 | 3/3 | Complete | 2026-02-11 |
| 2. Reference Data & Dimension Tables | v1.0 | 3/3 | Complete | 2026-02-11 |
| 3. Core Quality Event Entities | v1.0 | 5/5 | Complete | 2026-02-12 |
| 4. RCA Methodology Tables | v1.0 | 5/5 | Complete | 2026-02-12 |
| 5. Workflow Engine & Task Management | v1.0 | 4/4 | Complete | 2026-02-12 |
| 6. Codebase Hardening & Application Layer | v1.0 | 5/5 | Complete | 2026-02-12 |
| 7. Optimization & Integration Testing | v1.0 | 1/4 | Partial (3 deferred) | 2026-02-13 |
| 8. Production Topology Expansion | v1.0 | 6/6 | Complete | 2026-02-14 |
| 9. Defect Taxonomy & Quality Integration | v1.0 | 2/2 | Complete | 2026-02-15 |
| 10. Domain Enrichment & Cutover Hardening | v1.0 | 4/4 | Complete | 2026-02-15 |
| 11. Production Deployment | v1.0 | 3/3 | Complete | 2026-02-15 |
| 12. Reconciliation and Baseline | v1.1 | 3/3 | Complete | 2026-02-15 |
| 13. Schema Foundation | v1.1 | 3/3 | Complete | 2026-02-15 |
| 14. Authority and Workflow Alignment | v1.1 | 5/5 | Complete | 2026-02-16 |
| 15. Gate Stored Procedures | v1.1 | 6/6 | Complete | 2026-02-16 |
| 16. Views, Outbox, and Security Grants | v1.1 | 4/4 | Complete | 2026-02-17 |
| 17. Deploy Validation and Cutover Readiness | v1.1 | 4/4 | Complete | 2026-02-17 |
| 18. Knowledge Schema Foundation | v2.0 | 2/2 | Complete | 2026-02-18 |
| 19. Seed Data -- E-coat and Powder | v2.0 | 3/3 | Complete | 2026-02-18 |
| 20. Seed Data -- Liquid Synthesis and Cross-Process Verification | v2.0 | 3/3 | Complete | 2026-02-18 |
| 21. Knowledge Retrieval Layer | v2.0 | 3/3 | Complete | 2026-02-19 |
| 21.1. Defect taxonomy v3 migration | v2.0 | 2/2 | Complete | 2026-02-20 |
| 22. Analytics Foundation and Security | v2.0 | 0/TBD | Deferred | - |
| 23. Platform Governance, Documentation, and Deployment | v2.0 | 0/TBD | Not started | - |
| 24. Incoming Substrate and NCR Integration | v2.0 | 0/2 | Not started | - |

---
*Updated: 2026-02-22 — Phase 23 packet prepared (assumptions/context/research/verification), requirements and success criteria aligned to deferred Phase 22 reality.*
