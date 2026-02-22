# Quality Forms Module — Comparative Review Synthesis

**Produced by:** Claude Code (claude-opus-4-6)
**Date:** 2026-02-22
**Inputs:**

- Review A: `Reference_Architecture/Quality_Forms_Module/01_reviews/CLAUDE_CODE_REVIEW.md` (Claude Code / claude-sonnet-4-6)
- Review B: `Reference_Architecture/Quality_Forms_Module/01_reviews/quality-forms-module-gpt-output-review-codex.md` (Codex)
- Ground Truth: `Reference_Architecture/Quality_Forms_Module/00_ground_truth/CODEBASE_REFERENCE.md`, `Reference_Architecture/Quality_Forms_Module/00_ground_truth/PERSONA_PROMPT.md`, GPT package in `Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/`

---

## Executive Summary

Review A (Claude Code) is the stronger review for identifying hidden runtime and deployment risks — it surfaces three breaking issues (migration 159 entity-type hardcoding, missing security permission seeds, service-path RLS failures) that Review B entirely misses. Review B (Codex) is the stronger review for citation precision, inventory accuracy, and implementation-readiness gating — it correctly counts 29 procedures and 29 endpoints where Review A reports 27 and ~32, and it correctly flags Deliverables 3 and 6 as execution blockers where Review A is too permissive. The most dangerous divergence is Review B's complete silence on the three breaking runtime defects; the most consequential readiness divergence is Review A's willingness to start API work before stored procedure contracts and phasing gates are fully specified. The recommended course is: adopt Review B's structural baseline and readiness threshold, merge all of Review A's breaking runtime findings, apply Review B's naming corrections in full, and treat both D3 and D6 as blockers before any GSD executor is invoked.

---

## Part 1: Individual Review Assessment

### Review A (Claude Code)


| Section                     | Coverage                                    | Finding Quality                                                                                                                                         | Notable Gaps                                                                                                                                                                                   |
| --------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Architecture Constraints | 5 violations identified (V-01 through V-05) | Specific artifact references (`159_workflow_allow_entity_types_inspection.sql`, permission codes, `CreateForServiceAsync`); no file:line citations      | Does not classify contract-chain operationalization as a primary constraint violation (defers to phasing section)                                                                              |
| 2. Naming & Schema          | 7 items (N-01 through N-07)                 | Correct on NCR column naming and shared-PK analysis; includes schema-assignment rationale for `ProductionRun`                                           | Misses `AttributePass` boolean convention violation (confirmed at migration 150:25); misses 4 abbreviated FK naming drifts in migrations 133/134/135/144                                       |
| 3. Cross-Repo Impact        | Single consolidated table                   | Good dependency chain thinking; identifies blob SAS as architectural first                                                                              | **Factual error**: reports "27 stored procedures" and "~32 API endpoints" — verified count is 29 SPs (`02_stored_procedure_contracts.md` index) and 29 endpoints (`03_api_endpoint_design.md`) |
| 4. Phasing & Migration      | 7 items with depth                          | Identifies migration 159 as highest-risk cross-phase dependency; correctly flags workflow rejection state gap and GSD milestone mapping                 | Less precise than Review B on `Execution_Plan.md` prerequisite chain (DB Phases 23-24 must complete before v3)                                                                                 |
| 5. Domain Terminology       | 7 entries with ASTM/CQI-12/IATF citations   | Richest domain content of either review — MEK double rubs, adhesion ordinal scale, pencil hardness, DFT unit constraints, Delta E, PPAP/FAI distinction | Some assertions are external-standard based without tight coupling to specific GPT package lines                                                                                               |
| 6. Design Questions         | All 8 assessed (Q1-Q8)                      | Clear per-question verdicts                                                                                                                             | Overly optimistic on Q3 (fully addressed), Q5 (fully addressed), Q8 (addressed) — the actual SP contracts lack deterministic tie-break, dedupe/cooldown, and SPC extract schema                |
| 7. Deliverable Completeness | All 6 assessed (D1-D6)                      | Correctly identifies D2 as a blocker; rich gap analysis per deliverable                                                                                 | **D3 and D6 classified as non-blocking** despite success criteria requiring implementation-ready specificity (PERSONA_PROMPT lines 427-432)                                                    |
| 8. Practical Value          | Full section with role-based analysis       | Strongest audit narrative of either review; clear MVP definition (Phase 1+2 = minimum audit-grade)                                                      | Lacks quantified acceptance criteria for "ready to execute"                                                                                                                                    |


**Unique findings not in Review B:**

- V-01: Migration 159 drops and rebuilds `CK_WorkflowProcess_EntityType` with a hardcoded 8-value list — verified at migration 159:42-57. This will silently remove entity types added by DB Phases 23-33.
- V-02: No seed migration exists for `security.Feature`/`security.Permission` rows covering inspection permission codes (`INSPECTION_TEMPLATE_CREATE`, etc.) referenced by SP contracts.
- V-03: `DbConnectionFactory.CreateForServiceAsync()` does not call `dbo.usp_SetSessionContext` — service-level invocations of `usp_AutoCreateDueInspections` will fail RLS BLOCK predicates.
- V-05: Dynamic `dbo.StatusCode` column discovery in migrations 158/160 can THROW 53000 on schema mismatch — verified at migration 158:36-62.
- N-03: Shared-PK pattern in `InspectionCriteria`* tables (PK column is `InspectionTemplateFieldCriteriaId` instead of `{TableName}Id`) — verified at migration 138:15-17.
- N-06: Absence of `inspection.vw_`* views as a contract surface gap against the codebase's 36-view pattern.
- N-07: `inspection.ProductionRun` schema assignment questioned (should be `dbo` for reusability).
- Template workflow rejection path gap: no DRAFT→REVIEW→ACTIVE states; rejected publish leaves no audit trail of the rejection.
- `usp_SubmitInspection` evaluation logic underspecified for GSD execution (criteria comparison operators, rollup rules, MARGINAL vs FAIL threshold).
- Blob SAS endpoint as the first non-SQL API call in the codebase — architectural deviation from Constraint #1.
- PlantId alignment gap between parent criteria and typed detail tables (no FK or CHECK enforcing match).

### Review B (Codex)


| Section                     | Coverage                                                     | Finding Quality                                                                                                                                                                           | Notable Gaps                                                                                                                 |
| --------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1. Architecture Constraints | 2 violations (ACV-01, ACV-02)                                | High citation precision with file:line references (`docs/06_phasing_recommendation.md:3-6`, `docs/02_stored_procedure_contracts.md:28-56`)                                                | **Misses three breaking runtime defects**: migration 159 hardcoding, missing security permission seeds, service-path RLS gap |
| 2. Naming & Schema          | 12 items                                                     | Best coverage of either review — includes `AttributePass` boolean violation (150:25), all 4 abbreviated FK drifts (133:18, 134:18, 135:18, 144:20), plus NCR naming with index/UQ cascade | Does not analyze shared-PK convention exception in criteria detail tables                                                    |
| 3. Cross-Repo Impact        | 4 sub-sections (tables, SPs, endpoints, frontend components) | Most comprehensive inventory; **correct counts**: 29 SPs, 29 endpoints; individual frontend component mapping                                                                             | Limited prioritization of what blocks vs. what is informational                                                              |
| 4. Phasing & Migration      | 4 items                                                      | Anchored to `Execution_Plan.md` with line references; correct prerequisite chain (DB Phases 23-24 → v3 milestone → then Forms)                                                            | Does not flag migration 159 CHECK-constraint regression risk; does not flag migration 158/160 dynamic discovery risk         |
| 5. Domain Terminology       | 3 entries                                                    | Focused and grounded in prompt references; `ATTRIBUTE` label correction and canonical unit governance proposal are actionable                                                             | Less coating-domain depth than Review A — no MEK double-rub, pencil hardness, Delta E, or PPAP/FAI distinction               |
| 6. Design Questions         | All 8 assessed                                               | Stronger implementation-readiness lens; correctly marks Q3, Q5, Q8 as partially addressed                                                                                                 | Some partial ratings could be seen as overly strict on conceptual completeness                                               |
| 7. Deliverable Completeness | All 6 assessed                                               | Correctly classifies **D3 and D6 as blockers** alongside D2; aligned with PERSONA_PROMPT success criteria                                                                                 | Some blocker calls depend on whether phased elaboration is an acceptable pattern                                             |
| 8. Practical Value          | Full section                                                 | Concise and well-structured; maps IATF clauses to specific system capabilities                                                                                                            | Less explicit audit narrative and role-based process elimination detail than Review A                                        |


**Unique findings not in Review A:**

- `AttributePass` boolean naming violation at migration 150:25 — verified; should be `IsAttributePass` per CODEBASE_REFERENCE:36.
- 4 additional abbreviated FK naming drifts: `FK_InspectionTemplate_Family` (133:18), `FK_InspectionTemplateSection_Template` (134:18), `FK_InspectionTemplateField_Section` (135:18), `FK_InspectionScheduleRule_AssignmentRule` (144:20) — all verified against actual DDL.
- `UQ_InspectionNcrLink_Inspection_Ncr` unique constraint naming drift (148:31) and `IX_Inspection_AutoNcrId` / `IX_InspectionNcrLink_NcrId` index naming cascade.
- Correct 29/29 procedure/endpoint counts vs Review A's 27/~32.
- D3 and D6 explicitly classified as execution blockers.
- Contract-chain operationalization classified as primary architecture constraint violation (ACV-01) rather than deferred to phasing.
- NCR auto-create duplicate suppression/cooldown gap (R-10).
- Assignment-rule tie-break determinism gap with explicit indexed-check recommendation (R-09).
- Explicit `Execution_Plan.md` Step 0 prerequisite enforcement for phase sequencing.

---

## Part 2: Agreement and Divergence Map

### Agreements (Substantive)


| Section                  | Finding                                          | Both Reviews Agree That...                                                                                 | Evidence Quality                                                                        |
| ------------------------ | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Architecture Constraints | Core data-model direction is sound               | Typed criteria tables over EAV, SQL-first logic, and RLS coverage on all 23 tables are correct calls       | Substantive — both anchor to GPT package design artifacts and CODEBASE_REFERENCE        |
| Architecture Constraints | SP contracts are insufficient for implementation | `docs/02_stored_procedure_contracts.md` has a 29-procedure index but only ~8 with full signatures/behavior | Substantive — both reference the same document; Review B has precise line citations     |
| Naming & Schema          | NCR FK column naming drifts                      | `AutoNcrId` → `AutoNonConformanceReportId` and `NcrId` → `NonConformanceReportId`                          | Substantive — both cite the same objects; verified against migrations 146:74 and 148:22 |
| Cross-Repo Impact        | Work is inherently cross-repo                    | DB→API→App dependency chain must be enforced with manifest refresh gates                                   | Substantive — both call out contract propagation dependencies                           |
| Phasing                  | Migration numbering is provisional               | 131-160 must be renumbered from live highest migration at execution time                                   | Substantive — aligned with CODEBASE_REFERENCE:1016                                      |
| Phasing                  | Workflow transition compatibility is a risk gate | `workflow.usp_TransitionState` behavior for new entity types must be validated before rollout              | Substantive — both identify this as the highest-risk integration point                  |
| Design Questions         | Attachment flow is partially specified           | Blob/SAS upload initiation, finalization, and linking contracts need explicit specification                | Substantive — same gap identified from different angles                                 |
| Deliverables             | D2 (SP Contracts) is a blocker                   | Current procedure contract depth is insufficient for deterministic implementation by a GSD agent           | Substantive — explicit blocker status in both reviews                                   |
| Domain Terminology       | Unit governance needs hardening                  | Free-text `Units NVARCHAR(30)` should have constrained values for DFT, Gloss, etc.                         | Substantive — both flag, though with different specificity                              |


### Divergences


| Section                  | Issue                                      | Review A Position                                                           | Review B Position                                                                         | Nature of Conflict                                                                                                                                |
| ------------------------ | ------------------------------------------ | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Architecture Constraints | Migration 159 entity-type CHECK handling   | Breaking defect (V-01); hardcoded list will drop future entity types        | Not addressed                                                                             | **One-sided critical gap** — Review B misses a verified breaking risk                                                                             |
| Architecture Constraints | Missing security permission seeds          | Breaking defect (V-02); all inspection SPs will throw permission-not-found  | Not addressed                                                                             | **One-sided critical gap** — Review B misses a verified breaking risk                                                                             |
| Architecture Constraints | Service-call RLS session context           | Breaking defect (V-03); `CreateForServiceAsync` doesn't set session context | Not addressed                                                                             | **One-sided critical gap** — Review B misses a runtime deployment risk                                                                            |
| Architecture Constraints | Dynamic StatusCode schema discovery        | Breaking defect (V-05); migrations 158/160 can THROW 53000                  | Mentioned as complexity (not elevated to breaking)                                        | Severity disagreement                                                                                                                             |
| Architecture Constraints | Contract-chain failure classification      | Treated in phasing/deliverables (not Section 1)                             | ACV-01 — primary constraint violation                                                     | Classification disagreement (both recognize the issue)                                                                                            |
| Naming & Schema          | `AttributePass` boolean convention         | Not addressed                                                               | Violation of `Is`* prefix (migration 150:25)                                              | **One-sided gap** — Review A misses a verified naming violation                                                                                   |
| Naming & Schema          | Abbreviated FK naming breadth              | Focuses on NCR columns + criteria FK shorthand (N-04)                       | Flags 4 additional abbreviated FKs (133/134/135/144)                                      | Breadth mismatch — Review B has fuller coverage                                                                                                   |
| Naming & Schema          | `FK_Inspection_AutoNcr` naming             | Acceptable semantic disambiguator                                           | Violates `FK_{Table}_{ReferencedTable}` convention                                        | **Irreconcilable** — only one FK from Inspection to NonConformanceReport exists, so no disambiguation needed. Review B is correct per convention. |
| Naming & Schema          | Views as required contract surface         | Missing views is a substantive gap (N-06)                                   | Does not treat views as required                                                          | Disagreement on whether existing view pattern is mandatory for new modules                                                                        |
| Cross-Repo Impact        | Procedure/endpoint counts                  | 27 SPs / ~32 endpoints                                                      | 29 SPs / 29 endpoints                                                                     | **Irreconcilable factual conflict** — verified count is 29/29. Review B is correct.                                                               |
| Phasing                  | Baseline prerequisite precision            | Mentions conflicts with phases 23-33 broadly; suggests v3.0 or v4.0         | Explicitly enforces DB Phases 23-24 completion before v3 with Execution_Plan.md citations | Precision difference — Review B is more operationally specific                                                                                    |
| Design Questions         | Q3 (assignment combinatorics)              | Fully addressed                                                             | Partially addressed — tie-break/overlap prevention underspecified                         | **Readiness-threshold conflict** — verified: no deterministic tie-break order in SP contracts                                                     |
| Design Questions         | Q5 (NCR auto-creation threshold)           | Fully addressed                                                             | Partially addressed — duplicate suppression/cooldown not defined                          | **Readiness-threshold conflict** — verified: no dedupe logic specified in `usp_SubmitInspection` contract                                         |
| Design Questions         | Q8 (SPC integration depth)                 | Addressed                                                                   | Partially addressed — output schema/filters/paging not defined                            | **Readiness-threshold conflict** — verified: `usp_GetSpcMeasurementExtract` has no output contract                                                |
| Deliverables             | D3 (API Endpoint Design) blocker status    | Non-blocking — "sufficient to start implementation"                         | Blocking — per-endpoint request/response/error contracts not specified                    | Readiness-threshold conflict                                                                                                                      |
| Deliverables             | D6 (Phasing Recommendation) blocker status | Non-blocking — "sufficient for planning"                                    | Blocking — not aligned to active DB milestone state                                       | Readiness-threshold conflict                                                                                                                      |


### Coverage Gaps (One-Sided)


| Section                  | Issue                                                                          | Covered By          | Missing From                                           | Risk if Ignored                                                                                  |
| ------------------------ | ------------------------------------------------------------------------------ | ------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| Architecture Constraints | `CK_WorkflowProcess_EntityType` hardcoded reconstruction (migration 159:42-57) | Review A (V-01)     | Review B                                               | **Critical**: silent removal of entity types added by concurrent DB phases; data corruption risk |
| Architecture Constraints | No seed for `security.Feature`/`security.Permission` inspection codes          | Review A (V-02)     | Review B                                               | **Critical**: every policy-checked SP call will fail at runtime with permission-not-found        |
| Architecture Constraints | Service-path session context (`CreateForServiceAsync`) RLS behavior            | Review A (V-03)     | Review B                                               | **High**: scheduler/autocreate operations will fail BLOCK predicates in production               |
| Architecture Constraints | Dynamic StatusCode column discovery (migrations 158/160)                       | Review A (V-05)     | Review B (noted as complexity, not breaking)           | **High**: migration 158 can halt deployment with THROW 53000                                     |
| Naming & Schema          | `AttributePass` boolean naming violation (150:25)                              | Review B            | Review A                                               | **Medium**: convention drift in DTO/SP naming; audit of naming consistency                       |
| Naming & Schema          | 4 abbreviated FK naming drifts (133:18, 134:18, 135:18, 144:20)                | Review B            | Review A                                               | **Medium**: repeated naming debt across generated migrations                                     |
| Naming & Schema          | Index/UQ naming cascade from NCR column renames                                | Review B            | Review A                                               | **Low**: cosmetic if columns are renamed; auto-corrected during rename                           |
| Naming & Schema          | Shared-PK convention exception in criteria detail tables                       | Review A (N-03)     | Review B                                               | **Medium**: convention violation creates ambiguity about identity columns in downstream code     |
| Naming & Schema          | `ProductionRun` schema assignment (should be `dbo`?)                           | Review A (N-07)     | Review B                                               | **Low**: pragmatic v1 decision; document as deferred refactor                                    |
| Cross-Repo Impact        | Correct 29/29 procedure/endpoint counts                                        | Review B            | Review A (reports 27/~32)                              | **High**: under-scoped implementation planning and effort estimates                              |
| Phasing                  | Template workflow rejection state gap                                          | Review A            | Review B                                               | **Medium**: no audit trail for rejected template publish requests (IATF §7.5 traceability)       |
| Phasing                  | GSD milestone version assignment                                               | Review A            | Review B                                               | **Medium**: GSD executor cannot be invoked without milestone/phase mapping                       |
| Domain Terminology       | MEK double-rub, adhesion ordinal scale, pencil hardness, PPAP/FAI, Delta E     | Review A            | Review B                                               | **Medium**: coating-domain semantics may be flattened in criteria modeling; affects SPC accuracy |
| Design Questions         | `usp_SubmitInspection` evaluation rules underspecified                         | Review A (D2, R-05) | Review B (noted generally but no specific remediation) | **High**: core evaluation SP cannot be written without explicit comparison logic                 |
| Practical Value          | Blob SAS as first non-SQL API call                                             | Review A            | Review B                                               | **Medium**: architectural deviation from Constraint #1 must be explicitly acknowledged           |
| Practical Value          | PlantId alignment gap on typed criteria detail tables                          | Review A (R-10)     | Review B                                               | **Low**: data integrity risk mitigated by SP convention                                          |
| Deliverables             | D3 and D6 as execution blockers                                                | Review B            | Review A                                               | **High**: starting API/phase work without contracts causes implementation drift                  |


---

## Part 3: Decision Register

### D-1: Fix migration 159 CHECK-constraint reconstruction

- **Section**: Architecture Constraint Violations
- **Context**: Migration `159_workflow_allow_entity_types_inspection.sql` reads the current constraint definition but then drops it and recreates with a static 8-value list (159:42-57). Any entity types added by DB Phases 23-33 would be silently removed.
- **Review A says**: Breaking defect (V-01). Recommends dynamic append or migration to a FK-based validation table.
- **Review B says**: Not addressed.
- **Recommendation**: **Accept A.** Rewrite migration 159 to extract existing entity type values from `@Def` via string parsing and append `InspectionTemplate`/`Inspection` only if absent. The FK-based validation table alternative is architecturally cleaner but a larger change; the dynamic-append fix is sufficient for now.
- **Priority**: Breaking

### D-2: Add inspection security permission/feature seed migration

- **Section**: Architecture Constraint Violations
- **Context**: SP contracts reference permission codes (`INSPECTION_TEMPLATE_CREATE`, `INSPECTION_TEMPLATE_EDIT_DRAFT`, `INSPECTION_FILL`, etc.) via `security.usp_EvaluatePolicy`, but no migration seeds these into `security.Feature`/`security.Permission`.
- **Review A says**: Breaking gap (V-02). Requires migration `161_seed_security_features_permissions_inspection.sql`.
- **Review B says**: Not addressed.
- **Recommendation**: **Accept A.** Add the seed migration with exact permission codes matching SP contract usage. This is a deployment-blocking absence.
- **Priority**: Breaking

### D-3: Resolve service-path RLS session-context behavior

- **Section**: Architecture Constraint Violations
- **Context**: `DbConnectionFactory.CreateForServiceAsync()` opens a connection without calling `dbo.usp_SetSessionContext`. Any SP invoked via this path (e.g., `usp_AutoCreateDueInspections` from a scheduler) will encounter RLS BLOCK predicates on INSERT.
- **Review A says**: Breaking defect (V-03). Must document whether service jobs use `CreateForUserAsync` with a service OID or internally call session context.
- **Review B says**: Not addressed.
- **Recommendation**: **Accept A with synthesis.** Define the canonical pattern: all service-level invocations use `CreateForUserAsync` with a designated system service account OID that has appropriate plant access. Document this in the SP contract for `usp_AutoCreateDueInspections` and any future service-path SPs. This aligns with the existing pattern where all SPs accept `@CallerAzureOid`.
- **Priority**: High (Phase 3 blocker — not Phase 1/2 blocker since scheduling is Phase 3)

### D-4: Validate StatusCode schema before execution

- **Section**: Architecture Constraint Violations
- **Context**: Migrations 158 and 160 use dynamic schema discovery to locate `dbo.StatusCode` column names and will THROW 53000 if the column name isn't in the discovery list (158:36-62).
- **Review A says**: Breaking defect (V-05). Replace dynamic discovery with direct column reference once schema is confirmed.
- **Review B says**: Notes as complexity; does not elevate to breaking.
- **Recommendation**: **Accept A's severity, implement as preflight gate.** Before module rollout: confirm `dbo.StatusCode` DDL from the live database, add the actual column name to CODEBASE_REFERENCE.md, and replace the dynamic discovery in migrations 158/160 with direct references. This is a deployment-sequence risk, not an architectural design flaw.
- **Priority**: High (preflight gate — must be resolved before first DB migration executes)

### D-5: Make contract-chain artifact gates explicit in every phase

- **Section**: Architecture Constraint Violations / Phasing
- **Context**: `docs/06_phasing_recommendation.md` states the chain direction (lines 3-5) but does not include artifact refresh tasks as explicit phase steps.
- **Review A says**: Identifies as phasing gap; recommends explicit cross-repo ordering gates.
- **Review B says**: ACV-01 — classifies as primary architecture constraint violation with file:line citations.
- **Recommendation**: **Synthesize, anchored on B's classification.** This is both a phasing deficiency and a Constraint #6 violation. Add explicit tasks per phase: DB changes → refresh `db-contract-manifest.json`; API changes → refresh `db-contract-manifest.snapshot.json` + publish `api-openapi.publish.json`; App changes → refresh `api-openapi.snapshot.json`.
- **Priority**: Breaking

### D-6: Correct procedure and endpoint counts to 29/29

- **Section**: Cross-Repo Impact Map
- **Context**: Review A reports 27 SPs and ~32 endpoints. The actual procedure index (`02_stored_procedure_contracts.md:28-56`) lists exactly 29 procedures, and 29 API endpoints are defined.
- **Review A says**: 27 SPs / ~32 endpoints.
- **Review B says**: 29 SPs / 29 endpoints.
- **Recommendation**: **Accept B.** Verified against source documents. Update all planning artifacts to the correct 29/29 counts.
- **Priority**: High (affects implementation scope estimates)

### D-7: Complete all 29 stored procedure contracts before API build

- **Section**: Deliverable Completeness (D2)
- **Context**: Both reviews agree D2 is a blocker. Review A focuses remediation on `usp_SubmitInspection` evaluation logic specifically; Review B frames it as all 21 unspecified procedures.
- **Review A says**: Follow-up prompt for `usp_SubmitInspection` evaluation rules; other gaps noted but not individually remediated.
- **Review B says**: All 29 must have full signatures/behavior/error codes before API implementation (R-02); lists all 21 missing procedures by name.
- **Recommendation**: **Synthesize.** Both are correct at different granularities. The 21 unspecified procedures must have at minimum: full parameter lists, behavior summary, error codes, and result set contracts. `usp_SubmitInspection` additionally requires the detailed evaluation rules Review A specifies (per-criteria-type comparison logic, rollup rules, NCR trigger algorithm). Use Review A's follow-up prompt (Section 10) for the evaluation logic gap specifically, and Review B's R-02 scope for the remaining 20 procedures.
- **Priority**: Breaking

### D-8: Treat D3 (API Endpoint Design) and D6 (Phasing) as blockers

- **Section**: Deliverable Completeness
- **Context**: PERSONA_PROMPT success criteria (lines 427-432) state that a GSD agent should be able to write API endpoints "without ambiguity" and that phasing should be "realistic" and "account for cross-repo dependencies." Current D3 lacks per-endpoint request/response schemas and error code mappings; D6 lacks explicit cross-repo gates and milestone alignment.
- **Review A says**: D3 and D6 are non-blocking — "sufficient to start implementation" / "sufficient for planning."
- **Review B says**: D3 and D6 are blockers.
- **Recommendation**: **Accept B.** The success criteria are explicit: implementation without guesswork. API endpoints without response schemas and phasing without contract gates do not meet that bar. Block execution on both until remediated.
- **Priority**: High

### D-9: Rename `AttributePass` to `IsAttributePass`

- **Section**: Naming & Schema Violations
- **Context**: `inspection.InspectionResponseAttribute.AttributePass` (migration 150:25) violates the `Is`* boolean prefix convention defined in CODEBASE_REFERENCE:36.
- **Review A says**: Not addressed.
- **Review B says**: Clear violation; exact fix specified (R-03).
- **Recommendation**: **Accept B.** Rename column and update all references (SP contracts, API DTOs, index INCLUDE lists at 150:52).
- **Priority**: Medium

### D-10: Apply full abbreviated FK naming cleanup

- **Section**: Naming & Schema Violations
- **Context**: Four FK constraints use abbreviated referenced-table names: `FK_InspectionTemplate_Family` (133:18), `FK_InspectionTemplateSection_Template` (134:18), `FK_InspectionTemplateField_Section` (135:18), `FK_InspectionScheduleRule_AssignmentRule` (144:20). Convention requires `FK_{Table}_{ReferencedTable}` with full table name.
- **Review A says**: Only addresses `FK_InspectionCriteriaNumeric_Criteria` (N-04); misses the other four.
- **Review B says**: Flags all with exact migration:line references (R-06).
- **Recommendation**: **Accept B.** Batch-rename all abbreviated FK constraints to use full referenced-table names. Combine with N-04 from Review A for the criteria table FKs.
- **Priority**: Medium

### D-11: Rename `FK_Inspection_AutoNcr` per convention

- **Section**: Naming & Schema Violations
- **Context**: There is only one FK from `inspection.Inspection` to `quality.NonConformanceReport` (the `AutoNcrId` column). Review A argues the abbreviated constraint name is an acceptable disambiguator; Review B says it violates convention.
- **Review A says**: Acceptable semantic disambiguator since "multiple FKs to same table are conventional in this codebase."
- **Review B says**: Violates `FK_{Table}_{ReferencedTable}` convention; rename to `FK_Inspection_NonConformanceReport`.
- **Recommendation**: **Accept B.** Verified: only one FK exists from `Inspection` to `NonConformanceReport`, so no disambiguation is needed. The column rename to `AutoNonConformanceReportId` (which both reviews agree on) naturally leads to `FK_Inspection_NonConformanceReport` or `FK_Inspection_AutoNonConformanceReport` if a future second FK is anticipated. Use `FK_Inspection_AutoNonConformanceReport` for semantic clarity about the column's purpose.
- **Priority**: Medium

### D-12: Decide policy for shared-PK criteria detail tables

- **Section**: Naming & Schema Violations
- **Context**: `InspectionCriteriaNumeric`, `InspectionCriteriaAttribute`, `InspectionCriteriaSelection`, `InspectionCriteriaText` use `InspectionTemplateFieldCriteriaId` as both PK and FK (migration 138:15-17). This is a valid 1:1 identifying relationship pattern but violates the `{TableName}Id` PK naming convention.
- **Review A says**: Naming violation (N-03). Recommends surrogate PK + unique FK to maintain convention.
- **Review B says**: Not addressed.
- **Recommendation**: **Synthesize.** The shared-PK pattern is architecturally valid for 1:1 typed detail tables and is a recognized SQL pattern. Adding a surrogate PK adds a column and index to each of four tables with no functional benefit. **Accept as a documented exception** to the `{TableName}Id` convention, but require a note in the schema design document explaining why. If the team prefers strict convention adherence, adopt Review A's surrogate PK approach.
- **Priority**: Low

### D-13: Adopt phasing baseline from Execution_Plan.md

- **Section**: Phasing & Migration Sequencing
- **Context**: The Execution Plan defines DB Phases 23-24 as prerequisites before v3 work starts. The Forms module must be placed in a post-v2 milestone with renumbered migrations.
- **Review A says**: Mentions broad conflicts with phases 23-33; suggests v3.0 or v4.0 milestone.
- **Review B says**: Explicitly enforces DB Phases 23-24 completion with `Execution_Plan.md` line citations; requires renumbering from live highest.
- **Recommendation**: **Accept B's baseline, incorporate A's implementation suggestions.** Correct sequencing: finish DB Phases 23-24 → archive v2.0 → create new milestone → place Forms work → renumber migrations from live highest. Also adopt Review A's recommendation to split 30 migrations into two DB sub-phases (schema 131-155, seeds 156-161).
- **Priority**: High

### D-14: Reclassify Q3, Q5, Q8 as partially addressed

- **Section**: Design Question Completeness
- **Context**: All three questions are answered at a conceptual/decision level in `docs/00_key_decisions.md`. However, the SP contracts lack the deterministic implementation details needed for a GSD executor: Q3 has no tie-break order for assignment rule overlaps; Q5 has no duplicate-suppression/cooldown logic for NCR auto-creation; Q8 has no output schema for SPC extract.
- **Review A says**: Q3 fully addressed, Q5 fully addressed, Q8 addressed.
- **Review B says**: Q3 partially, Q5 partially, Q8 partially — due to missing operational detail.
- **Recommendation**: **Accept B's assessment.** The questions are conceptually answered (correct design direction) but implementation-partial (a GSD agent cannot write deterministic SQL without the missing details). Mark as "Conceptually answered; implementation contracts required" and add as prerequisites for the relevant phase.
- **Priority**: Medium

### D-15: Add template workflow rejection state for IATF traceability

- **Section**: Phasing & Migration Sequencing
- **Context**: Migration 160 seeds template workflow with DRAFT→ACTIVE and ACTIVE→RETIRED transitions only. If a template publish is rejection-gated via approval chain, the rejection is handled by the workflow engine returning to DRAFT, but no explicit REVIEW state captures the approval-pending window.
- **Review A says**: Add `INSP_TEMPLATE_REVIEW` state with DRAFT→REVIEW→ACTIVE and REVIEW→DRAFT (Reject) transitions for audit traceability.
- **Review B says**: Not addressed.
- **Recommendation**: **Accept A with nuance.** The existing workflow engine already handles approval-rejection by returning the entity to its prior state (DRAFT). Adding an explicit REVIEW state improves auditability (IATF §7.5 — "why was this template revision rejected?"). However, migration 158 already seeds `INSP_TEMPLATE_DRAFT`, `INSP_TEMPLATE_ACTIVE`, `INSP_TEMPLATE_RETIRED` without a REVIEW code. Add `INSP_TEMPLATE_REVIEW` to the status seed and add DRAFT→REVIEW and REVIEW→ACTIVE/REVIEW→DRAFT transitions to migration 160.
- **Priority**: Medium

### D-16: Demote mandatory views to optional optimization

- **Section**: Naming & Schema Violations / Deliverable Completeness
- **Context**: Review A identifies the absence of `inspection.vw`_* views as a contract surface gap, citing the codebase's 36 existing views. The deliverable requirements and constraints do not explicitly require views for new modules.
- **Review A says**: Missing views is a substantive gap (N-06, R-11). Recommends minimum set: `vw_InspectionDueQueue`, `vw_InspectionSummary`, `vw_InspectionTemplateCatalog`.
- **Review B says**: Does not treat views as required; focuses on stored procedures.
- **Recommendation**: **Accept B's classification with A's suggestion as a future optimization.** Views are not required by the architecture constraints or deliverable specifications. The existing NCR module uses views extensively for dashboards, but the inspection module's read patterns can be served by stored procedures (which already exist in the design). Add views in a later phase if query performance or reporting patterns justify them.
- **Priority**: Low

### D-17: Merge Review A's coating-domain terminology into specification

- **Section**: Domain Terminology Accuracy
- **Context**: Review A surfaces 7 domain-specific corrections (MEK double rubs, adhesion ordinal scale, pencil hardness modeling, DFT unit constraints, Delta E, IATF clause citations, PPAP/FAI distinction). Review B covers 3 (ATTRIBUTE label, unit governance, IATF clause tags). Review A's corrections are more granular and directly affect criteria modeling and seed data.
- **Review A says**: Detailed corrections with ASTM/CQI-12 references.
- **Review B says**: Focused on label correction and unit governance framework.
- **Recommendation**: **Synthesize.** Adopt Review B's implementation framework (canonical unit governance via lookup category + validation in save procedures) and import Review A's domain-specific corrections as the values seeded into that framework. Specifically: "MEK Double Rubs" (not "MEK Rubs"), adhesion as NUMERIC 0-5 (not ATTRIBUTE pass/fail), DFT units constrained to `mils`/`µm`, pencil hardness as SELECTION field type, Delta E as NUMERIC with customer-specified MaxValue.
- **Priority**: Medium

### D-18: Specify blob/SAS upload architecture explicitly

- **Section**: Design Question Completeness (Q6)
- **Context**: Both reviews agree the attachment flow is partially specified. The blob SAS endpoint is the first API endpoint in sf-quality that would call Azure SDK directly rather than being a thin SQL pass-through.
- **Review A says**: Identifies as architectural first for Constraint #1 deviation; proposes 3-step flow (initiate→SAS token→finalize) with explicit SP contracts.
- **Review B says**: Notes direction is correct; recommends concrete SP contracts (R-11).
- **Recommendation**: **Synthesize.** Accept Review A's 3-step flow design as the specification. Add explicit SP contracts per Review B's recommendation: `inspection.usp_CreateInspectionAttachmentUpload` (creates Document record, returns StoragePath), API-side SAS generation (acknowledged as only non-SQL API call), `inspection.usp_FinalizeInspectionAttachmentUpload` (updates Document metadata, links to response). Document this as a formal Constraint #1 exception in the integration architecture doc.
- **Priority**: Medium (Phase 5 item — not blocking Phases 1-4)
