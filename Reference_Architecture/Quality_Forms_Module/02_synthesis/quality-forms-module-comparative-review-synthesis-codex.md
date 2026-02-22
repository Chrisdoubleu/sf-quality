# Quality Forms Module - Comparative Review Synthesis

## Executive Summary

Review B (Codex) is stronger on citation precision, count accuracy, and implementation-readiness framing; Review A (Claude Code) is stronger at surfacing hidden runtime risks in migrations/security/RLS. The most critical divergence is that Review B misses three breaking execution risks (`159_workflow_allow_entity_types_inspection.sql`, missing `security.Feature`/`security.Permission` seeds, and service-context RLS behavior), while Review A undercounts the implementation surface (27 vs actual 29 procedures) and is more permissive on readiness. Both reviews correctly identify that stored procedure contracts are incomplete and that phasing needs explicit cross-repo gates. Recommended course: use Review B as the structural baseline, then merge Review A's breaking runtime findings before any implementation phase starts.

## Part 1: Individual Review Assessment

### Review A (Claude Code)


| Section                            | Coverage                                              | Finding Quality                                                                                                                                             | Notable Gaps                                                                                                  |
| ---------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Architecture Constraint Violations | Partial (5 violations; not a full 8-constraint sweep) | Specific object names (`159_workflow_allow_entity_types_inspection.sql`, `usp_AutoCreateDueInspections`, permission codes), but fewer direct line citations | Does not classify contract-chain operationalization as a primary constraint failure in Section 1              |
| Naming & Schema Violations         | Broad                                                 | Concrete schema/proc references; includes rationale                                                                                                         | Misses `AttributePass` boolean naming drift and several abbreviated FK names flagged in Review B              |
| Cross-Repo Impact Map              | Medium                                                | Good dependency thinking across DB/API/App                                                                                                                  | Factual drift: reports 27 SPs and ~32 endpoints; package docs list 29 SPs and 29 endpoints                    |
| Phasing & Migration Sequencing     | Strong                                                | Identifies sequencing hazards and workflow integration dependency                                                                                           | Less precise than Review B on `Execution_Plan.md` prerequisite that DB Phases 23-24 complete before v3 starts |
| Domain Terminology Accuracy        | Strong depth                                          | Rich coating-domain corrections (MEK, adhesion, PPAP/FAI, pencil hardness)                                                                                  | Several assertions are external-standard based without tight linkage to provided reference files              |
| Design Question Completeness       | Full 8/8 assessed                                     | Clear per-question statuses                                                                                                                                 | Optimistic on Q3/Q5/Q8 completeness versus actual contract detail level                                       |
| Deliverable Completeness           | Full 6/6 assessed                                     | Clear blocker call for Deliverable 2                                                                                                                        | D3 and D6 are treated as non-blockers despite Success Criteria requiring implementation-ready specificity     |
| Practical Value Assessment         | Full                                                  | High practical/audit framing                                                                                                                                | Lacks explicit acceptance metrics for "ready to execute"                                                      |


**Unique findings not in Review B:**

- Breaking risk in `db/migrations/159_workflow_allow_entity_types_inspection.sql` hardcoding `CK_WorkflowProcess_EntityType`.
- Missing `security.Feature`/`security.Permission` seeding for permission codes referenced by `security.usp_EvaluatePolicy`.
- Service-path RLS risk from `DbConnectionFactory.CreateForServiceAsync` not setting session context.
- Dynamic `dbo.StatusCode` schema discovery risk in migrations 158/160 called out as deployment hazard.
- Shared-PK naming exception in `inspection.InspectionCriteria`* tables analyzed explicitly.

### Review B (Codex)


| Section                            | Coverage               | Finding Quality                                                             | Notable Gaps                                                                                                                           |
| ---------------------------------- | ---------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Architecture Constraint Violations | Partial (2 violations) | High citation quality (file:line references in package docs)                | Misses three execution-critical risks identified by Review A (migration 159 hardcoding, missing permission seeds, service-context RLS) |
| Naming & Schema Violations         | Strong                 | High specificity; exact migration/column/constraint references              | Does not discuss shared-PK convention exception in criteria detail tables                                                              |
| Cross-Repo Impact Map              | Very strong            | Most complete inventory (tables, 29 SPs, 29 endpoints, frontend components) | Limited prioritization of what is truly blocking versus informative                                                                    |
| Phasing & Migration Sequencing     | Strong                 | Anchored to `Execution_Plan.md` and artifact-chain gates                    | Does not include migration 159 CHECK-constraint regression risk                                                                        |
| Domain Terminology Accuracy        | Moderate               | Grounded in prompt references, focused on unit governance and labels        | Less coating-specific depth than Review A                                                                                              |
| Design Question Completeness       | Full 8/8 assessed      | Strong implementation-readiness lens; identifies under-specified logic      | Can be stricter than necessary at "question answered conceptually" level                                                               |
| Deliverable Completeness           | Full 6/6 assessed      | Best aligned to Success Criteria (implementation without guesswork)         | Some blocker calls depend on whether phased elaboration is acceptable                                                                  |
| Practical Value Assessment         | Full                   | Concise and useful                                                          | Less explicit than Review A on audit narrative detail                                                                                  |


**Unique findings not in Review A:**

- `inspection.InspectionResponseAttribute.AttributePass` violates `Is`* boolean convention.
- Additional abbreviated FK naming drifts (`FK_InspectionTemplate_Family`, `FK_InspectionTemplateSection_Template`, `FK_InspectionTemplateField_Section`, `FK_InspectionScheduleRule_AssignmentRule`).
- Explicit contract-chain artifact gate omissions in `docs/06_phasing_recommendation.md`.
- Corrected implementation counts (29 procedures, 29 endpoints) used in readiness assessment.
- Stronger blocker classification for Deliverables 3 and 6.

## Part 2: Agreement and Divergence Map

### Agreements (Substantive)


| Section                  | Finding                                                 | Both Reviews Agree That...                                                                    | Evidence Quality                                                    |
| ------------------------ | ------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Architecture Constraints | Core relational direction is correct                    | Typed model over EAV and SQL-first architecture are the right base approach                   | Substantive; both anchor to package design artifacts                |
| Architecture Constraints | Stored procedure contracts are not implementation-ready | Deliverable 2 needs deeper behavioral specification before coding                             | Substantive; both reference `docs/02_stored_procedure_contracts.md` |
| Naming & Schema          | NCR FK column naming drifts exist                       | `AutoNcrId` and `NcrId` should align to `NonConformanceReportId` convention                   | Substantive; same objects cited                                     |
| Cross-Repo Impact        | Work is inherently cross-repo                           | DB->API->App dependency chain must be enforced                                                | Substantive; both call out contract propagation dependencies        |
| Phasing                  | Migration numbering is provisional                      | 131-160 must be renumbered from live highest migration at execution time                      | Substantive; aligned with `CODEBASE_REFERENCE.md` migration context |
| Phasing                  | Workflow transition compatibility is a risk gate        | `workflow.usp_TransitionState` behavior for new entity types must be validated before rollout | Substantive; both identify this as high-risk integration            |
| Design Questions         | Attachment flow is only partially specified             | Blob/SAS initiation/finalization contracts need explicit definition                           | Substantive; same gap from different angles                         |
| Deliverables             | Deliverable 2 is a blocker                              | Current SP contract depth is insufficient for deterministic implementation                    | Substantive; explicit blocker status in both reviews                |


### Divergences


| Section                   | Issue                                          | Review A Position                                          | Review B Position                                          | Nature of Conflict                             |
| ------------------------- | ---------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------- |
| Architecture Constraints  | Migration 159 entity-type CHECK handling       | Breaking defect (V-01)                                     | Not addressed                                              | One-sided critical gap                         |
| Architecture Constraints  | Missing security permission seeds              | Breaking defect (V-02)                                     | Not addressed                                              | One-sided critical gap                         |
| Architecture Constraints  | Service-call RLS session context               | Breaking defect (V-03)                                     | Not addressed                                              | One-sided critical gap                         |
| Architecture Constraints  | Contract-chain failure classification          | Treated mainly in phasing/deliverables                     | ACV-01 primary violation                                   | Severity/classification difference             |
| Architecture/Deliverables | Procedure completeness scope                   | Focus on `usp_SubmitInspection` + selected reporting procs | 29 listed, only 8 fully specified (blocking)               | Irreconcilable on scope/completeness threshold |
| Naming & Schema           | `FK_Inspection_AutoNcr` naming validity        | Acceptable disambiguator                                   | Violates `FK_{Table}_{ReferencedTable}` convention         | Irreconcilable rules interpretation            |
| Naming & Schema           | Additional naming drift breadth                | Focuses on NCR + shared-PK + criteria FK shorthand         | Adds boolean and multiple abbreviated FK violations        | Breadth mismatch                               |
| Naming/Cross-Repo         | Views as required contract surface             | Flags absence of `inspection.vw_*` as schema/contract gap  | Does not treat as required                                 | Potential overreach vs optional pattern        |
| Cross-Repo Impact         | Inventory counts and contract scope            | 27 SPs, ~32 endpoints, table-manifest additions            | 29 SPs, 29 endpoints, contract focus on proc/view chain    | Irreconcilable factual conflict                |
| Phasing                   | Baseline prerequisite precision                | Mentions conflicts with phases 23-33 and milestone mapping | Explicitly enforces DB Phases 23-24 completion before v3   | Precision/severity conflict                    |
| Design Questions          | Q3/Q5/Q8 completeness                          | Marked fully/mostly addressed                              | Marked partially addressed due missing deterministic rules | Readiness-threshold conflict                   |
| Deliverables              | D3 and D6 blocker status                       | Non-blocking                                               | Blocking                                                   | Readiness-threshold conflict                   |
| Architecture/Phasing      | Dynamic `StatusCode` schema detection severity | Breaking migration risk (V-05)                             | Mentioned as complexity, not core blocker                  | Severity conflict                              |


### Coverage Gaps (One-Sided)


| Section                  | Issue                                                                     | Covered By | Missing From | Risk if Ignored                                                           |
| ------------------------ | ------------------------------------------------------------------------- | ---------- | ------------ | ------------------------------------------------------------------------- |
| Architecture Constraints | `CK_WorkflowProcess_EntityType` hardcoded reconstruction in migration 159 | Review A   | Review B     | Silent removal of pre-existing entity types in future phases              |
| Architecture Constraints | No seed for `security.Feature`/`security.Permission` inspection codes     | Review A   | Review B     | First policy check can fail at runtime for every protected proc           |
| Architecture Constraints | Service-path session context behavior (`CreateForServiceAsync`)           | Review A   | Review B     | RLS block-predicate failures for scheduler/autocreate operations          |
| Naming & Schema          | `AttributePass` boolean naming violation                                  | Review B   | Review A     | Convention drift and contract inconsistency in DTO/SP naming              |
| Naming & Schema          | Abbreviated FK violations beyond NCR tables                               | Review B   | Review A     | Repeated naming debt across generated migrations                          |
| Cross-Repo Impact        | Correct 29-proc / 29-endpoint counts                                      | Review B   | Review A     | Under-scoped implementation planning and effort estimates                 |
| Deliverables             | Deliverable 3 as execution blocker                                        | Review B   | Review A     | API implementation starts with ambiguous request/response/error contracts |
| Domain Terminology       | MEK double-rub, PPAP/FAI split, pencil-hardness semantics                 | Review A   | Review B     | Coating-domain semantics may be flattened in template criteria modeling   |


## Part 3: Decision Register

### D-1: Fix migration 159 CHECK-constraint reconstruction

- **Section**: Architecture Constraint Violations
- **Context**: `db/migrations/159_workflow_allow_entity_types_inspection.sql` drops and recreates `CK_WorkflowProcess_EntityType` with a static list. This can remove entity types introduced by other phases.
- **Review A says**: Breaking defect; dynamic append strategy or alternative model required.
- **Review B says**: Not addressed.
- **Recommendation**: **Accept A.** Rewrite migration 159 to preserve existing values and append `InspectionTemplate`/`Inspection` only when missing.
- **Priority**: Breaking

### D-2: Add inspection permission/feature seed migration

- **Section**: Architecture Constraint Violations
- **Context**: Procedure contracts reference permission codes (e.g., `INSPECTION_TEMPLATE_CREATE`) but no migration seeds matching `security.Feature`/`security.Permission` rows.
- **Review A says**: Breaking gap; add dedicated security seed migration.
- **Review B says**: Not addressed.
- **Recommendation**: **Accept A.** Add `161_seed_security_features_permissions_inspection.sql` and align code literals exactly to SP contract usage.
- **Priority**: Breaking

### D-3: Resolve service-path RLS session-context behavior

- **Section**: Architecture Constraint Violations
- **Context**: `DbConnectionFactory.CreateForServiceAsync` does not call `dbo.usp_SetSessionContext`, while RLS predicates require session-scoped plant context.
- **Review A says**: Scheduler/service calls can fail write predicates.
- **Review B says**: Not addressed.
- **Recommendation**: **Accept A with synthesis.** Define one pattern: either all service jobs use `CreateForUserAsync` with a service OID, or affected procs set context internally.
- **Priority**: High

### D-4: Make contract-chain artifact gates explicit in every phase

- **Section**: Architecture Constraint Violations
- **Context**: Phase plan states chain direction but does not operationalize artifact refresh tasks (`db-contract-manifest.json`, API snapshots, OpenAPI publish, app snapshot).
- **Review A says**: Identifies ordering gap mainly in phasing.
- **Review B says**: ACV-01; treats omission as core governance violation.
- **Recommendation**: **Synthesize (A+B), anchored on B.** Add explicit per-phase contract publication tasks and completion criteria.
- **Priority**: Breaking

### D-5: Normalize on 29 procedures and complete all contracts

- **Section**: Deliverable Completeness
- **Context**: `docs/02_stored_procedure_contracts.md` indexes 29 procedures but only 8 have full signature/behavior blocks.
- **Review A says**: Emphasizes `usp_SubmitInspection` and selected gaps; cross-repo map uses 27-proc count.
- **Review B says**: Treats 29->8 mismatch as blocking ACV and D2 defect.
- **Recommendation**: **Accept B.** Correct count to 29 everywhere and require full contracts for all 29 before API build.
- **Priority**: Breaking

### D-6: Enforce strict FK naming for NCR linkages

- **Section**: Naming & Schema Violations
- **Context**: Convention specifies `FK_{Table}_{ReferencedTable}`; current names include `FK_Inspection_AutoNcr` and `FK_InspectionNcrLink_Ncr`.
- **Review A says**: `FK_Inspection_AutoNcr` is acceptable disambiguation.
- **Review B says**: Both violate convention.
- **Recommendation**: **Accept B.** Rename to referenced-table tokens plus disambiguator where needed.
- **Priority**: Medium

### D-7: Apply full naming cleanup set (boolean + abbreviated FK names)

- **Section**: Naming & Schema Violations
- **Context**: Additional drift includes `AttributePass` and abbreviated FK names in migrations 133/134/135/144.
- **Review A says**: Does not include these issues.
- **Review B says**: Flags all with exact migration references.
- **Recommendation**: **Accept B.** Batch-rename these schema elements before downstream code generation.
- **Priority**: Medium

### D-8: Decide policy for shared-PK criteria detail tables

- **Section**: Naming & Schema Violations
- **Context**: `inspection.InspectionCriteriaNumeric/Attribute/Selection/Text` use `InspectionTemplateFieldCriteriaId` as both PK and FK, conflicting with strict `{TableName}Id` convention.
- **Review A says**: Treat as naming violation and recommends surrogate PK + unique FK.
- **Review B says**: Not addressed.
- **Recommendation**: **Synthesize.** Keep shared-PK only if formally approved as a documented exception; otherwise adopt surrogate PK + UQ FK pattern.
- **Priority**: Medium

### D-9: Correct cross-repo inventory and planning counts

- **Section**: Cross-Repo Impact Map
- **Context**: Review A reports 27 procedures and ~32 endpoints; package docs indicate 29 procedures and 29 endpoints.
- **Review A says**: 27 SPs / ~32 endpoints.
- **Review B says**: 29 SPs / 29 endpoints.
- **Recommendation**: **Accept B.** Update planning artifacts to 29/29 and re-estimate implementation scope.
- **Priority**: High

### D-10: Clarify contract manifest scope (procedures/views, not tables by default)

- **Section**: Cross-Repo Impact Map
- **Context**: Review A proposes adding new tables to `db-contract-manifest.json`; reference chain describes manifest primarily as procedures/views contract surface.
- **Review A says**: Add all 23 tables to manifest schema section.
- **Review B says**: Table changes are indirect contract impact; proc/view chain is primary artifact path.
- **Recommendation**: **Accept B.** Keep manifest scope aligned to existing contract chain unless schema-manifest extension is explicitly adopted.
- **Priority**: Medium

### D-11: Adopt phasing baseline from `Execution_Plan.md`

- **Section**: Phasing & Migration Sequencing
- **Context**: Baseline plan requires DB Phases 23-24 completion and manifest refresh before v3 work starts.
- **Review A says**: Notes broad conflict with phases 23-33 and milestone mapping options.
- **Review B says**: Enforces explicit prerequisite ordering with references to Step 0.
- **Recommendation**: **Accept B baseline**, then incorporate A's suggestion to split forms DB work into smaller migration batches.
- **Priority**: High

### D-12: Reclassify Q3/Q5/Q8 as conceptually answered but implementation-partial

- **Section**: Design Question Completeness
- **Context**: Key decisions answer the design intent, but deterministic rule details (tie-breaks, dedupe/cooldown, SPC extract contract) are not fully specified.
- **Review A says**: Mostly fully addressed.
- **Review B says**: Partially addressed due missing operational detail.
- **Recommendation**: **Synthesize.** Mark as "Conceptually answered; implementation details required" and add contract addenda.
- **Priority**: Medium

### D-13: Treat Deliverables 3 and 6 as blockers for execution start

- **Section**: Deliverable Completeness
- **Context**: Success criteria require enough specificity that agents can implement without guesswork; current API and phasing docs leave key ambiguities.
- **Review A says**: D3 and D6 are non-blocking.
- **Review B says**: D3 and D6 are blockers.
- **Recommendation**: **Accept B.** Block execution until API request/response/error contracts and phasing gate tasks are explicit.
- **Priority**: High

### D-14: Demote "missing views" from requirement to optional optimization

- **Section**: Naming & Schema Violations
- **Context**: Review A treats absence of `inspection.vw_`* as a required contract gap; constraints and deliverables do not explicitly require new views for this module.
- **Review A says**: Missing views is a substantive gap.
- **Review B says**: Does not require views; focuses on stored procedures.
- **Recommendation**: **Reject mandatory view requirement.** Keep as optional optimization if query-performance patterns justify it.
- **Priority**: Low

### D-15: Keep dynamic `StatusCode` discovery as high-risk preflight item

- **Section**: Architecture Constraint Violations
- **Context**: Migrations 158/160 use dynamic `dbo.StatusCode` column discovery and can `THROW 53000` on schema mismatch.
- **Review A says**: Breaking defect requiring direct-column contract before execution.
- **Review B says**: Notes complexity but does not elevate severity.
- **Recommendation**: **Synthesize.** Treat as high-priority preflight gate: validate live `dbo.StatusCode` schema before module rollout; replace dynamic logic if schema is stable.
- **Priority**: High

### D-16: Merge Review A's coating-domain nuance into final specification

- **Section**: Domain Terminology Accuracy
- **Context**: Review A adds coating-specific semantics (MEK double rubs, adhesion ordinal scale, PPAP/FAI distinction) not covered in Review B.
- **Review A says**: Adds deeper domain corrections and standards references.
- **Review B says**: Focuses on unit governance and labeling with less domain breadth.
- **Recommendation**: **Synthesize.** Keep B's implementation focus and import A's domain glossary where it affects data modeling/criteria validation.
- **Priority**: Medium

