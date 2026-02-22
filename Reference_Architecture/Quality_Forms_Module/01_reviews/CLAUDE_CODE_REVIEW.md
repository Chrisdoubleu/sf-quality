# Quality Forms Module — GPT Output Review
**Reviewed by:** Claude Code (claude-sonnet-4-6)
**Review Date:** 2026-02-22
**Package Path:** `Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/`
**Reference Material:** `Reference_Architecture/Quality_Forms_Module/00_ground_truth/CODEBASE_REFERENCE.md`, `Reference_Architecture/Quality_Forms_Module/00_ground_truth/PERSONA_PROMPT.md`, `Reference_Architecture/Execution_Plan.md`, DB migrations 125–130

---

## Executive Summary

The GPT-generated output is architecturally sound and substantially correct. The core design decisions — typed criteria tables over EAV, wildcardable specificity-scored assignment rules, `InspectionTemplateFamily`/`InspectionTemplate` revision split, and integration with the existing workflow engine — are all correct calls that a senior architect would make. The migration files are properly idempotent, the DDL follows naming conventions for the main tables, the RLS migration (155) comprehensively covers all 23 new tables, and the phasing is well-reasoned.

However, there are three breaking issues that must be resolved before execution: (1) Migration 159 hardcodes the `CK_WorkflowProcess_EntityType` constraint list and will silently drop entity types added by DB Phases 23-33 if those phases execute first; (2) the security feature/permission seed is entirely absent — procedures reference `INSPECTION_TEMPLATE_CREATE` and other permission codes that do not yet exist in `security.Feature`/`security.Permission`; (3) service-level calls to `usp_AutoCreateDueInspections` will fail RLS BLOCK predicates if run without session context. Beyond these, the FK naming convention is violated in two places, the typed criteria detail tables use a shared-PK pattern that violates `{TableName}Id` convention, and the stored procedure contracts for `usp_SubmitInspection` are underspecified — insufficient for a GSD agent to write the evaluation logic without guesswork.

**Recommended course of action:** Approve the overall architecture. Remediate the three breaking issues and the SP evaluation gap before handing to a GSD executor. The naming convention violations are mechanical fixes that can be applied directly.

---

## 1. Architecture Constraint Violations

| ID | GPT Statement / Artifact | Constraint Broken | Required Fix |
|----|--------------------------|-------------------|--------------|
| V-01 | Migration `159_workflow_allow_entity_types_inspection.sql` drops `CK_WorkflowProcess_EntityType` and reconstructs it with a hardcoded list of 8 entity types (`NCR`, `CAPA`, `CustomerComplaint`, `SupplierCAR`, `AuditFinding`, `EightDReport`, `InspectionTemplate`, `Inspection`) | Constraint #5 — Idempotent migrations / execution correctness | The hardcoded list will silently DROP entity types added by DB Phases 23-33 if those phases modify the same constraint or add new entity types. Remediation: parse the current constraint definition dynamically, tokenize the existing entity type list, append `InspectionTemplate` and `Inspection` only if absent, then rebuild. Never reconstruct a constraint from a static list when the existing list may have grown since the package was authored. |
| V-02 | `inspection.usp_CreateInspectionTemplateDraft` calls `security.usp_EvaluatePolicy` with permission code `INSPECTION_TEMPLATE_CREATE`; similarly `INSPECTION_TEMPLATE_EDIT_DRAFT`, `INSPECTION_FILL`, `INSPECTION_REVIEW`, `INSPECTION_APPROVE`, `INSPECTION_ANALYTICS` are referenced in SP contracts | Constraint #6 — Contract governance | No seed migration exists for `security.Feature` or `security.Permission` rows covering these codes. The SPs will throw a permission-not-found error on every call until the seeds are added. A migration `161_seed_security_features_permissions_inspection.sql` is required before any SP is callable in production. |
| V-03 | `inspection.usp_AutoCreateDueInspections` (and any service-level or scheduler-invoked procs) takes `@CallerAzureOid UNIQUEIDENTIFIER` and relies on the caller providing a valid OID | Constraint #7 — RLS via SESSION_CONTEXT | Background service calls made via `DbConnectionFactory.CreateForServiceAsync()` do not call `dbo.usp_SetSessionContext`. The RLS BLOCK predicate on `inspection.Inspection` will block all INSERT operations if session context is NULL (depending on predicate implementation). The SP contracts must explicitly document whether service-level procs are called via `CreateForUserAsync` (with a designated system service account OID) or must call `dbo.usp_SetSessionContext` internally. This is an unaddressed operational gap that will surface as a runtime RLS violation. |
| V-04 | `inspection.usp_SaveInspectionTemplateDraftDefinition` receives `@DefinitionJson NVARCHAR(MAX)` representing the complete section/field/option/criteria tree; `inspection.usp_SaveInspectionResponses` receives `@ResponsesJson NVARCHAR(MAX)` | Constraint #1 — Business logic in T-SQL only | Not a constraint violation in isolation — JSON is parsed via `OPENJSON` inside T-SQL. However, the JSON schema is an implicit API-DB contract that bypasses the normal typed-parameter pattern and is not published in `db-contract-manifest.json`. The exact JSON shape must be formally specified in the SP contract documents as a JSON schema literal. Without it, a GSD execution agent cannot write the `OPENJSON` parsing logic correctly. |
| V-05 | Migration `158_seed_status_codes_inspection.sql` and `160_seed_workflow_inspection.sql` use runtime dynamic SQL (`sys.sp_executesql`) to discover `dbo.StatusCode` column names and look up status IDs | Constraint #5 — Idempotent migrations | Dynamic schema detection is fragile and non-deterministic at plan time. If `dbo.StatusCode` has a column name not in the discovery list (`StatusCode`, `StatusCodeCode`, `Code`, `Status`, `StatusValue`), both migrations throw error 53000 and the entire deployment fails at migration 158/160. The actual `dbo.StatusCode` DDL is not in `CODEBASE_REFERENCE.md`, which is the documented gap. This must be resolved before execution: confirm the StatusCode column name and replace dynamic discovery with a direct reference. |

---

## 2. Naming & Schema Violations

| ID | GPT Proposed Name | Correct Name | Rule Violated |
|----|-------------------|--------------|---------------|
| N-01 | `inspection.InspectionNcrLink.NcrId` (column) | `NonConformanceReportId` | FK columns must match the referenced table's PK name (`quality.NonConformanceReport.NonConformanceReportId`). Per CODEBASE_REFERENCE: "Foreign Key: Referenced table's PK name." |
| N-02 | `inspection.Inspection.AutoNcrId` (column + FK `FK_Inspection_AutoNcr`) | Column: `AutoNonConformanceReportId`; Constraint: `FK_Inspection_AutoNcr` (constraint name acceptable as semantic disambiguator since multiple FKs to same table are conventional in this codebase) | Same FK column naming rule as N-01. `AutoNcrId` is not the PK of `quality.NonConformanceReport`. |
| N-03 | `inspection.InspectionCriteriaNumeric` PK column is `InspectionTemplateFieldCriteriaId` (shared-PK pattern); same for `InspectionCriteriaAttribute`, `InspectionCriteriaSelection`, `InspectionCriteriaText` | PK columns should be `InspectionCriteriaNumericId`, `InspectionCriteriaAttributeId`, etc. with the FK to parent named per convention | PK convention: `{TableName}Id`. The shared-PK (1:1 identifying relationship) pattern is architecturally valid for these typed detail tables but violates the naming convention. The constraint `PK_InspectionCriteriaNumeric` is correct but the column it covers must be `InspectionCriteriaNumericId` per convention, with a separate FK `InspectionTemplateFieldCriteriaId` on the same row. |
| N-04 | `FK_InspectionCriteriaNumeric_Criteria` | `FK_InspectionCriteriaNumeric_InspectionTemplateFieldCriteria` | FK constraint: `FK_{Table}_{ReferencedTable}`. "Criteria" is a shorthand, not the referenced table name. Same applies to `InspectionCriteriaAttribute`, `InspectionCriteriaSelection`, `InspectionCriteriaText`. |
| N-05 | `FK_InspectionTemplateField_ControlPlanDoc` | `FK_InspectionTemplateField_Document_ControlPlan` or `FK_InspectionTemplateField_ControlPlanReferenceDocument` | Multiple FKs to the same table (`dbo.Document`) require disambiguation but must reference the table name. Convention allows a disambiguating suffix when multiple FKs exist: `FK_{Table}_{ReferencedTable}_{Disambiguator}`. |
| N-06 | No views defined anywhere in the package | `inspection.vw_*` views required per codebase pattern | The existing system has 36 views in `db-contract-manifest.json`. The Forms module has no views — all querying deferred to SPs. This means `db-contract-manifest.json` will have 0 view entries for the inspection schema. Key query patterns (`vw_InspectionDueQueue`, `vw_InspectionCompletionSummary`, `vw_InspectionsByPartLine`) are missing. This is a gap against the codebase's view-based read pattern, not a naming violation per se, but its absence creates a contract surface hole. |
| N-07 | `inspection.ProductionRun` in the `inspection` schema | Consider `dbo.ProductionRun` | Schema assignment convention: dbo = infrastructure tier (Plant, Line, Customer, Part, Equipment). A production run is a manufacturing execution event, not an inspection-domain concept. Placing it in `inspection` creates coupling: a future Production Execution module cannot reference it without cross-schema dependency on an inspection table. This is a pragmatic v1 decision but should be explicitly called out as a deferred refactor. |

---

## 3. Cross-Repo Impact Map

| Artifact | Repo | Depends On | Contract Impact | RLS Impact |
|----------|------|-----------|----------------|------------|
| 23 new `inspection.*` tables (migrations 131–154) | sf-quality-db | `dbo.Plant`, `dbo.Customer`, `dbo.Part`, `dbo.ProductionLine`, `dbo.LineStage`, `dbo.LineType`, `dbo.Equipment`, `dbo.Supplier`, `dbo.LookupValue`, `dbo.DefectType`, `dbo.Document`, `dbo.AppUser`, `dbo.StatusCode`, `quality.NonConformanceReport`, `inspection.*` (sequential) | Add all 23 tables to `db-contract-manifest.json` (schema section) | All 23 tables get Filter + Block predicates in migration 155 |
| 27 new `inspection.*` stored procedures | sf-quality-db | All 23 new tables + `dbo.usp_SetSessionContext`, `security.usp_EvaluatePolicy`, `workflow.usp_TransitionState`, `quality.usp_CreateNcrQuick` | Add all 27 procedures to `db-contract-manifest.json` (procedures section) | Must call `dbo.usp_SetSessionContext` on every proc entry |
| 0 views (gap) | sf-quality-db | N/A | Missing from `db-contract-manifest.json` | N/A |
| `CK_WorkflowProcess_EntityType` constraint extension (migration 159) | sf-quality-db | `workflow.WorkflowProcess` (existing table) | No manifest impact (constraint not in manifest) | None |
| `security.Feature` + `security.Permission` seed (missing — V-02) | sf-quality-db | `security.Feature`, `security.Permission`, `security.RolePermission` (existing tables) | Add permission codes to `db-contract-manifest.json` permission catalog | None (security schema is not plant-scoped) |
| `dbo.LookupValue` seed (156) — 8 new categories, ~35 new values | sf-quality-db | `dbo.LookupCategory`, `dbo.LookupValue` | Existing tables; manifest update: new lookup categories (inspection module section) | None (dbo.LookupValue has no PlantId per CODEBASE_REFERENCE) |
| `dbo.DocumentType` seed (157) — `INSP_TEMPLATE`, `INSP_ATTACHMENT` | sf-quality-db | `dbo.DocumentType` | Existing table; manifest update | None |
| `dbo.StatusCode` seed (158) — 9 new status codes | sf-quality-db | `dbo.StatusCode` | Existing table; manifest update | None |
| `workflow.WorkflowProcess/State/Transition` seed (160) | sf-quality-db | `dbo.StatusCode` (seed 158 must run first), migration 159 must run first | Existing workflow tables | None |
| ~32 new API endpoints (6 groups) | sf-quality-api | All 27 inspection SPs must be in `db-contract-manifest.snapshot.json` before API phase executes | Add all endpoints to `api-openapi.publish.json`; bump API version | API must use `DbConnectionFactory.CreateForUserAsync()` on all endpoints |
| New `SqlErrorMapper` entries (53xxx range) | sf-quality-api | None | Part of `api-openapi.publish.json` error catalog | None |
| New C# records (DTOs) | sf-quality-api | API OpenAPI spec | Part of `api-openapi.publish.json` | None |
| Blob SAS generation endpoint (attachment upload helper) | sf-quality-api | Azure Blob Storage SDK + `dbo.Document` SP | New endpoint in `api-openapi.publish.json` — note: this is the ONLY API endpoint that calls Azure SDK (not just SQL), which is an architectural first for this codebase | None |
| New route groups + components (4 groups) | sf-quality-app | API endpoints must exist in `api-openapi.snapshot.json` | App must refresh snapshot after API publishes | None |

---

## 4. Phasing & Migration Sequencing Issues

**1. Migration numbers 131–160 are provisional and will conflict with DB Phases 23-33.**
The CODEBASE_REFERENCE states the current highest migration is 130. The Execution_Plan defines DB Phases 23-33 (9 phases, ~5 migrations each ≈ 45 migrations) that must execute before or concurrent with the Forms module. If those phases run first, the Forms module would start at approximately migration 175+. The GPT acknowledges this with the disclaimer "If your repository has advanced beyond migration 130, renumber these migrations sequentially" — this is correct guidance, but the phasing document must be updated to explicitly state: *do not schedule these migrations until the current highest migration number is confirmed from the live db-contract-manifest.json.*

**2. Migration 159 hardcodes the entity type list — the highest-risk sequencing dependency.**
If DB Phases 23-33 add any new entity type to `CK_WorkflowProcess_EntityType` (e.g., a future `ProductionOrder` or `MaintenanceRequest` entity type in Phase 31), migration 159 will drop and rebuild the constraint with only the 8 types it knows about, silently removing the newer entries. This is the most dangerous cross-phase dependency in the entire package. Fix required in migration 159 before execution (see Remediation Guide, R-01).

**3. Workflow seed (migration 160) has no `InspectionTemplate` REJECTED state.**
The seeded `InspectionTemplate` workflow has two transitions: DRAFT→ACTIVE and ACTIVE→RETIRED. If an approval chain rejects the publish request (workflow error 50414), the template is left in DRAFT status (correct behavior — workflow engine returns the entity to its prior state on approval rejection). However, there is no explicit "DRAFT (pending approval rejection)" state or re-editable path post-rejection. For the NCR workflow, a `REJECTED` state exists with a rework path. The template workflow should have: DRAFT→ACTIVE (Publish, approval-gated), ACTIVE→DRAFT (Revise), ACTIVE→RETIRED. This gap means a rejected template publish leaves the template in DRAFT with no workflow record of the rejection. IATF auditors will ask "why was this template revision rejected and by whom?" — this must be traceable.

**4. The Forms module phases 1–6 are not mapped to GSD milestone numbers.**
The phasing document describes phases as "Phase 1 — Foundations," "Phase 2 — Controlled Publish," etc. These must be mapped to a new GSD milestone (e.g., `v4.0 Quality Forms Module`) with specific GSD phase numbers before `gsd:plan-phase` can execute. The Execution_Plan defines v3.0 phases 25-33 for Architectural Hardening. The Forms module would be v4.0 (or extend v3.0 if timing aligns). This mapping must be resolved before any GSD executor is invoked.

**5. Phase 1 includes DB migrations 131-160 in a single sweep — this should be split.**
The recommended grouping from the Execution_Plan suggests ~2-5 migrations per GSD phase. Migrations 131-160 (30 files) in a single GSD phase is too large for a single focused session. Recommended split: DB Phase A (schema, migrations 131-155), DB Phase B (seeds + workflow extension, 156-160). This aligns with the GSD phase size guideline.

**6. Cross-repo ordering within the module phases is unspecified.**
The phasing document says "DB / API / App" per phase but does not define the gating explicitly. Before the Forms module API phase executes: the inspection SPs must be in `db-contract-manifest.json`, the manifest must be snapshotted into the API repo, and `api-openapi.publish.json` must be updated. This follows the existing contract chain protocol but needs to be stated explicitly in the phasing document.

**7. Phase 2 dependency on existing `workflow.usp_TransitionState`.**
If `workflow.usp_TransitionState` contains a hard-coded CASE statement that maps entity types to their status column (the highest-risk integration point per the open questions doc), extending it requires a DB modification inside the `workflow` schema. This cross-schema modification must be planned as part of Phase 2 DB work and must precede the API publish endpoint. The open questions doc flags this correctly as the single highest-risk integration detail.

---

## 5. Domain Terminology Corrections

| GPT Term | Correct Term / Unit | Standard Reference |
|----------|--------------------|--------------------|
| "MEK Rubs" (in field description context) | "MEK Double Rubs" — the measurement unit is the number of *double* rubs (one forward + one back = 1 double rub) | ASTM D5402 §3.2 |
| "Adhesion Rating" described as pass/fail attribute | Adhesion per ASTM D3359 (cross-hatch tape test) is a 6-point ordinal scale: 0B (worst) to 5B (best), where CQI-12 minimum is 4B. This is NOT a pass/fail binary — it is a categorical rating that should be modeled as a NUMERIC or SELECTION field type with min acceptable value = 4 (corresponding to 4B), not a simple ATTRIBUTE field | ASTM D3359 / CQI-12 §5.2.2 |
| DFT — no unit constraint in schema | DFT must be stored in mils or microns only. The `UnitOfMeasure` column is a free NVARCHAR(30) — acceptable as a design choice, but the unit values seeded for DFT fields must be constrained to `mils` or `µm` (microns). The system should never accept `mm` or `cm`. This should be enforced in a LookupValue seed for measurement units, not left as free text | CQI-12 §5.1 |
| "Color Delta E" (mentioned in PERSONA_PROMPT, not explicitly modeled) | ΔE (CIE L\*a\*b\* color difference, ASTM D2244). Modeled as a NUMERIC criteria type with MaxValue = customer-specified tolerance (typically < 1.0). The seed data does not include a specific measurement type code for ΔE. No violation in the DDL, but the seed should include a `DELTA_E` measurement type in a units lookup | ASTM D2244 |
| "IATF clause 7.5" — mentioned but not cited in design docs | Correct clause: IATF 16949:2016 §7.5 "Documented Information." Also relevant: §8.6 "Release of Products and Services" (final inspection sign-off), §9.1.1 "Monitoring, Measurement, Analysis and Evaluation" (in-process inspection frequency). These should be cited explicitly in the integration architecture document for audit-facing traceability | IATF 16949:2016 |
| "First Article / PPAP" — used interchangeably | PPAP (Production Part Approval Process) and FAI (First Article Inspection) are related but distinct. PPAP is the AIAG customer submission package. FAI is one element within a PPAP. The template type code `FIRST_ARTICLE` conflates both. The seed value name "First Article / PPAP" is acceptable for v1 as a combined template type, but implementers should be aware that a full PPAP submission involves elements beyond a single inspection form (dimensional data, material certifications, process capability studies) | AIAG PPAP Manual 4th Edition |
| "Pencil Hardness" — listed in PERSONA_PROMPT, no specific modeling | Pencil hardness per ASTM D3363 is an ordinal scale (6B through 9H, 15 values). This is a SELECTION field type, not a NUMERIC type. The acceptance criteria would be "minimum hardness" where the scale is ordered. The seed data does not include a specific pencil hardness selection lookup. Not a violation; should be added to measurement type seeds for completeness | ASTM D3363 |

---

## 6. Design Question Assessment

| # | Question | Status | Gap / Issue | Required Addition |
|---|----------|--------|-------------|-------------------|
| Q1 | Template versioning when form instances are in-progress | **Yes — Fully Addressed** | In-progress inspections complete under the old revision via `InspectionTemplateId` lock at creation. Correct per IATF controlled document requirements. | None |
| Q2 | Acceptance criteria complexity without EAV | **Yes — Fully Addressed** | Typed criteria tables (Numeric, Attribute, Selection, Text) + typed response tables. No EAV. Correct and compliant. | None |
| Q3 | Form assignment combinatorics | **Yes — Fully Addressed** | Wildcardable assignment rules with persisted `SpecificityScore` computed column + `RulePriority` + effective dating. Resolution logic is well-specified. | None |
| Q4 | Frequency enforcement without real-time production signals | **Yes — Addressed** | Manual `inspection.ProductionRun` as scheduling anchor in v1. Explicit acknowledgement that v2+ would replace the run creation source. Clean separation of concerns. | None |
| Q5 | NCR auto-creation threshold | **Yes — Fully Addressed** | Opt-in per field criteria (`IsNcrAutoCreateEnabled = 0` default). Two modes seeded: IMMEDIATE and FAIL_COUNT_WINDOW. `TriggerFailCount` + `TriggerWindowMinutes` configuration. `RemeasureAllowedCount` for re-measurement tolerance. | None |
| Q6 | Photo / attachment handling | **Partially Addressed** | Correctly routes to `dbo.Document` + `InspectionResponseAttachment`. SAS generation deferred to open questions. The key architectural concern: SAS generation requires the API to call Azure Blob SDK — this is the first API endpoint in sf-quality that would NOT be a thin SQL pass-through. This architectural deviation from Constraint #1 is not explicitly addressed. | Must add a specification for the upload helper endpoint that clarifies: (a) which Azure SDK is used, (b) where Blob container configuration lives, (c) whether a new `inspection.usp_InitiateAttachmentUpload` SP creates the Document record and returns a StoragePath, and (d) how the finalize step works. The API layer for SAS generation cannot be "thin SQL gateway" — this must be designed explicitly. |
| Q7 | Offline / disconnected operation | **Yes — Addressed** | Explicitly deferred with rationale. Draft saving and connectivity loss messaging in v1. Correct scope decision. | None |
| Q8 | SPC integration depth | **Yes — Addressed** | `inspection.usp_GetSpcMeasurementExtract` defined as a data export mechanism. No SPC engine built. Correct deferral. | None |

---

## 7. Deliverable Completeness Assessment

| # | Deliverable | Status | What's Missing | Blocker? |
|---|-------------|--------|---------------|----------|
| D1 | Database Schema Design | **Complete with defects** | (1) FK naming violations N-01, N-02; (2) shared-PK naming violation N-03; (3) no PlantId alignment constraint between parent criteria table and typed detail tables — if PlantId diverges between `InspectionTemplateFieldCriteria` and `InspectionCriteriaNumeric`, RLS will produce inconsistent results; (4) `dbo.StatusCode` schema unknown (open question #1, flags risk correctly); (5) no views defined | No — DDL is executable pending naming fixes. PlantId alignment gap is a data integrity risk but not a deployment blocker. |
| D2 | Stored Procedure Contracts | **Partially complete — blocker exists** | (1) `usp_SubmitInspection` evaluation logic underspecified: the 5-step behavior list does not specify HOW each criteria type is evaluated (e.g., for NUMERIC: is value < MinValue → FAIL, > WarningMaxValue → MARGINAL, etc.), which comparison operators are used, how MARGINAL is distinguished from FAIL, or how the overall rollup is computed (any FAIL → overall FAIL? or threshold?); (2) `usp_QueryInspections`, `usp_GetInspectionCompletionRates`, `usp_GetInspectionPassFailRates`, `usp_GetSpcMeasurementExtract` have no parameter lists or behavior specs; (3) `usp_SaveInspectionTemplateDraftDefinition` OPENJSON schema unspecified; (4) `usp_SaveInspectionResponses` JSON schema unspecified; (5) security permission seed missing (V-02) | **YES** — `usp_SubmitInspection` evaluation logic is the core of the entire module. A GSD executor cannot write this SP without the evaluation rules. |
| D3 | API Endpoint Design | **Substantially complete** | (1) Response shapes for GET endpoints not specified (only request DTOs); (2) no `/v1/` URL prefix per API Phase 3.5 plans in Execution_Plan.md (this prefix will need to be added when Phase 3.5 ships — either add it now or document the planned refactor); (3) SAS upload endpoint not specified (only flagged as open question); (4) query parameters for filter endpoints (`GET /inspections/search`, `GET /inspections/due`) not documented | No — sufficient to start implementation with caveat on response shapes |
| D4 | Frontend Form Builder Architecture | **Complete** | (1) TypeScript interface definitions for `InspectionTemplate`, `InspectionTemplateSection`, `InspectionTemplateField`, `Inspection`, and response union types not defined; (2) supervisor rejection flow page/components not specified; (3) how `INSP_TEMPLATE_APPROVED` state differs from `INSP_APPROVED` in the UI is not shown | No — sufficient for a frontend developer to start. Interface definitions are derivable from the API response shapes. |
| D5 | Integration Architecture | **Substantially complete** | (1) Missing sequence diagram for photo upload flow (described in text but no diagram); (2) missing sequence diagram for supervisor reject + rework flow; (3) missing sequence diagram for service-level `usp_AutoCreateDueInspections` (background scheduler pattern); (4) SPC extract flow not diagrammed | No — the three existing diagrams (template publish, due queue, submit/NCR) cover the critical paths for Phase 1 and Phase 2. |
| D6 | Phasing Recommendation | **Substantially complete** | (1) No GSD milestone number or version assigned (e.g., "v4.0 Quality Forms Module"); (2) explicit cross-repo ordering gates not stated (e.g., "DB Phase A must complete and manifest must be refreshed before API Phase begins"); (3) migration number conflicts with DB Phases 23-33 not addressed beyond a one-line disclaimer; (4) no mention of required `db-contract-manifest.json` refresh steps after each DB phase; (5) Phase 2 dependency on `workflow.usp_TransitionState` extensibility not treated as a hard gate | No — sufficient for planning, but the gaps must be resolved during the `gsd:discuss-phase` session before execution |

---

## 8. Practical Value Assessment

### What this module unlocks that doesn't exist today

Today, inspection records exist as paper forms, Excel spreadsheets, and scanned PDF files on shared drives. There is no programmatic way to answer the IATF auditor's baseline question: *"Show me all inspection records for part X on line Y for the last 6 months."* This module makes that query a `usp_QueryInspections` call. More concretely:

- **Controlled document chain**: IATF §7.5 requires inspection forms to be controlled documents with revision history and approval records. Today, Excel forms proliferate in uncontrolled copies. This module creates a system-versioned, approval-gated form template that produces an audit trail from draft through active to retired — exactly what §7.5 requires.
- **Inspection completion traceability**: The `usp_GetInspectionCompletionRates` capability will, for the first time, answer "were the required inspections actually performed?" vs "we have a paper that says they were." Audit findings repeatedly cite inadequate inspection records and non-compliance with Control Plan frequencies.
- **Automatic NCR creation pipeline**: The existing NCR lifecycle is mature (18 gate procedures, workflow engine, approval chains). Currently, a failed inspection requires a human to manually file an NCR — and this step is often delayed or skipped. The `IsNcrAutoCreateEnabled` + threshold-window configuration creates a direct, traceable link from inspection failure → NCR record without human intervention.

### Manual processes eliminated by role

| Role | Eliminated Manual Process |
|------|--------------------------|
| Operators | Paper form fill, submission to supervisor mailbox, manual NCR filing for failures |
| Quality Engineers | Excel form version distribution via email, spreadsheet-based completion rate tracking |
| Quality Managers | End-of-shift paper collection, manual pass/fail tallying for dashboards |
| Supervisors | Signed paper review copies, physical storage of inspection records |
| IATF Auditors | Manual search across paper/scanned files to construct inspection history for an audit finding |

### Downstream capabilities unlocked

- NCR auto-creation with embedded inspection context (lot number, line, part, template revision) improves root cause investigation quality
- `usp_GetSpcMeasurementExtract` provides a structured data feed for SPC tooling — Cp/Cpk calculations on DFT, adhesion, etc. become feasible without custom data extraction
- Inspection history becomes a queryable precursor to PPAP/First Article digital records
- Trend analysis (weekly pass/fail rates per line per customer) becomes a scheduled dashboard query rather than an Excel calculation

### What is the MVP that delivers measurable audit compliance value

**Phase 1 + Phase 2 together = minimum viable audit-grade compliance.** Phase 1 alone (templates + fill + submit) delivers forms that work but are not controlled documents. Phase 2 (approval workflow, controlled publish, status transitions) is what makes the forms IATF §7.5 compliant. Shipping Phase 1 without Phase 2 creates a gap: forms exist but any QE can publish them without approval. The MVP must include both phases before the next IATF surveillance audit.

Phase 3 (scheduling + due queue) is the next highest compliance value: it closes the "are inspections happening at the required frequency?" audit finding. This is a common repeat audit finding that Phase 3 directly addresses.

### Proposals that create more complexity than value

1. **`usp_SaveInspectionTemplateDraftDefinition` JSON-over-SP pattern**: Sending the entire form definition tree as a single `@DefinitionJson NVARCHAR(MAX)` blob is convenient for the form builder UI (one save call) but creates an implicit JSON schema contract that bypasses the typed-parameter governance of the rest of the system. Every `OPENJSON` parsing path in T-SQL is untestable without a live JSON payload. The alternative — fine-grained SPs (`usp_UpsertTemplateSection`, `usp_UpsertTemplateField`, `usp_UpsertTemplateFieldCriteria`) — is more verbose but each SP is independently callable and testable. This trade-off should be an explicit decision, not left implicit. **Recommendation: accept the JSON-over-SP pattern for v1 but formally specify the JSON schema in the SP contract document. This is not a blocker but needs to be addressed before GSD execution.**

2. **PlantId on every table including typed criteria detail tables**: The typed criteria tables (`InspectionCriteriaNumeric`, etc.) carry PlantId because RLS requires a `PlantId` column on every table covered by the isolation policy. This is architecturally correct but creates a data integrity gap: the `PlantId` in `InspectionCriteriaNumeric` must always match the `PlantId` in its parent `InspectionTemplateFieldCriteria` row, with no FK constraint or CHECK constraint enforcing this. If the stored procedures always derive PlantId from the parent row (rather than accepting it as a separate parameter), the risk is low. But it should be documented as a convention: "PlantId on typed criteria detail tables is always copied from the parent InspectionTemplateFieldCriteria row and never independently supplied by callers."

3. **Inspection.INSP_APPROVED is a Terminal state**: Based on migration 160's seeded workflow, once an inspection is APPROVED, no further transitions exist. This means: an approved inspection with an incorrectly entered measurement cannot be corrected. For IATF purposes, a corrected record would require a NEW inspection instance referencing the original — which is actually the correct audit-safe behavior. However, this should be explicitly stated in the design documents. An approved inspection is an immutable audit record; corrections create a superseding inspection.

---

## 9. Full Remediation Guide

| Issue ID | Severity | Exact Fix |
|----------|----------|-----------|
| R-01 (V-01) | **Breaking** | Rewrite migration 159. Replace the static list reconstruction with: (1) read current constraint definition text into `@CurrentDef`; (2) check `IF @CurrentDef NOT LIKE N'%InspectionTemplate%'`; (3) if modification needed, dynamically build the new constraint list by extracting all existing `N'...'` values from `@CurrentDef` via string parsing, appending `N'InspectionTemplate'` and `N'Inspection'` if absent, then rebuilding the constraint. Alternatively: drop the CHECK constraint and move to a FK-based validation table (`workflow.AllowedEntityType`) that is appendable without DDL changes — this is architecturally cleaner for a system that will continue adding entity types through phases 23-33 and beyond. |
| R-02 (V-02) | **Breaking** | Add migration `161_seed_security_features_permissions_inspection.sql`. Required entries: `security.Feature` rows for `INSPECTION_TEMPLATES` (Module), `INSPECTION_FILL` (Component), `INSPECTION_REVIEW` (Component), `INSPECTION_ANALYTICS` (Page). `security.Permission` rows for `INSPECTION_TEMPLATE_CREATE`, `INSPECTION_TEMPLATE_EDIT_DRAFT`, `INSPECTION_TEMPLATE_PUBLISH`, `INSPECTION_TEMPLATE_RETIRE`, `INSPECTION_FILL`, `INSPECTION_SUBMIT`, `INSPECTION_APPROVE`, `INSPECTION_REJECT`, `INSPECTION_VOID`, `INSPECTION_ANALYTICS_VIEW`, `INSPECTION_SPC_EXPORT`. These codes must match exactly what the SPs call via `security.usp_EvaluatePolicy`. |
| R-03 (V-03) | **Breaking** | In `usp_AutoCreateDueInspections` (and any other service-level invocation path): document explicitly in the SP contract whether: (a) the API always calls this via `CreateForUserAsync` with a designated system service account OID, requiring that service account to exist in `dbo.AppUser` with appropriate plant access; or (b) the SP internally calls `dbo.usp_SetSessionContext` using the provided `@CallerAzureOid`. Option (a) is consistent with the existing pattern (`quality.usp_CreateNcrQuick` takes `@CallerAzureOid`). If the scheduler is a background Timer trigger on App Service, it needs a managed identity OID or a designated service user OID. This must be explicitly resolved before Phase 3 (scheduling) executes. |
| R-04 (V-05) | **Breaking** | Before execution: confirm `dbo.StatusCode` DDL from the live database. Add the actual column name (likely `StatusCode`) to the `CODEBASE_REFERENCE.md` reference document. Replace the dynamic column discovery in migrations 158 and 160 with a direct reference to the confirmed column name. |
| R-05 (D2, SP evaluation gap) | **Significant** | Add a "Criteria Evaluation Rules" section to `docs/02_stored_procedure_contracts.md` specifying: for `InspectionCriteriaNumeric`: `MeasuredValue < MinValue OR MeasuredValue > MaxValue → FAIL`; `MeasuredValue < WarningMinValue OR MeasuredValue > WarningMaxValue (and not already FAIL) → MARGINAL`; `else → PASS`. For `InspectionCriteriaAttribute`: `IsPass = 0 → FAIL`, `IsPass = 1 → PASS`. For `InspectionCriteriaSelection`: response option must be in `InspectionCriteriaAllowedOption` → PASS, else → FAIL. For `InspectionCriteriaText`: always `PASS` unless SP has a "required non-empty" rule. Overall rollup: `any FAIL finding → overall FAIL`; `no FAIL but any MARGINAL → overall MARGINAL`; `all PASS or NA → PASS`. These rules must be explicit and machine-implementable. |
| R-06 (N-01) | **Significant** | Rename `inspection.InspectionNcrLink.NcrId` → `NonConformanceReportId`. Update FK constraint: `FK_InspectionNcrLink_Ncr` → `FK_InspectionNcrLink_NonConformanceReport`. Update all SPs, views, and API DTOs that reference this column. |
| R-07 (N-02) | **Significant** | Rename `inspection.Inspection.AutoNcrId` → `AutoNonConformanceReportId`. FK constraint name `FK_Inspection_AutoNcr` is acceptable as a semantic disambiguator (multiple FKs to same table). Update all SPs, API DTOs, and the sequence diagram in docs/05. |
| R-08 (N-03) | **Significant** | For each typed criteria detail table: add a surrogate PK column (`InspectionCriteriaNumericId INT IDENTITY(1,1)`, etc.), keep `InspectionTemplateFieldCriteriaId INT NOT NULL` as a separate FK column with a `UNIQUE` constraint (enforcing 1:1). Update constraint names: `PK_InspectionCriteriaNumeric` covers the new surrogate; `FK_InspectionCriteriaNumeric_InspectionTemplateFieldCriteria` is the FK. The unique constraint on `InspectionTemplateFieldCriteriaId` ensures the 1:1 relationship. |
| R-09 (N-04) | **Significant** | Rename FK constraints on typed criteria detail tables: `FK_InspectionCriteriaNumeric_Criteria` → `FK_InspectionCriteriaNumeric_InspectionTemplateFieldCriteria`; same pattern for Attribute, Selection, Text. |
| R-10 (PlantId alignment) | **Significant** | Add documentation convention to SP contracts: "PlantId on typed criteria detail tables (`InspectionCriteriaNumeric`, `InspectionCriteriaAttribute`, `InspectionCriteriaSelection`, `InspectionCriteriaText`) is always SET from the parent `InspectionTemplateFieldCriteria.PlantId` row during INSERT. Callers never provide PlantId independently on these tables." Add a stored procedure guard in `usp_SaveInspectionTemplateDraftDefinition` that asserts `@PlantId = (SELECT PlantId FROM inspection.InspectionTemplateFieldCriteria WHERE ...)` before inserting into detail tables. |
| R-11 (Missing views) | **Significant** | Add a minimum set of views to the DB phase: `inspection.vw_InspectionDueQueue` (due inspections with template and context info), `inspection.vw_InspectionSummary` (inspections with template name, line, part, customer, result), `inspection.vw_InspectionTemplateCatalog` (families with current active revision summary). These views should be referenced from `db-contract-manifest.json` and used by the API's GET list endpoints instead of SELECT * patterns. |
| R-12 (Phasing gap) | **Significant** | Update `docs/06_phasing_recommendation.md`: (a) assign a GSD milestone version (v4.0 recommended); (b) add explicit cross-repo ordering gates with manifest refresh steps; (c) state that migrations 131-160 are provisional and must be renumbered at execution time; (d) split DB Phase 1 into Phase 1a (schema, migrations 131-155) and Phase 1b (seeds + workflow extension, 156-161); (e) add a hard gate: "Phase 2 DB work must confirm `workflow.usp_TransitionState` is data-driven or extend it before the API publish endpoint is implemented." |
| R-13 (Template workflow rejection path) | **Significant** | Add to migration 160 workflow seeds: `INSP_TEMPLATE_DRAFT` → `INSP_TEMPLATE_ACTIVE` transition requires approval chain. On approval rejection, the workflow engine returns entity to DRAFT (this is the existing pattern). However, add an `InspectionTemplate` status code `INSP_TEMPLATE_REVIEW` (Normal state) and transitions: DRAFT→REVIEW (Submit for Approval), REVIEW→ACTIVE (Approve), REVIEW→DRAFT (Reject with reason). This provides a clear audit trail for rejected template submissions. |
| R-14 (OPENJSON schema) | **Significant** | Add a "DefinitionJson Schema" appendix to `docs/02_stored_procedure_contracts.md` showing the exact JSON shape expected by `usp_SaveInspectionTemplateDraftDefinition` with TypeScript-style interface definitions. Without this, the API developer cannot construct the correct payload and the SP developer cannot write the `OPENJSON` paths. |
| R-15 (Blob SAS architectural spec) | **Significant** | Add a dedicated section to `docs/05_integration_architecture.md` and `docs/03_api_endpoint_design.md` specifying: (a) new endpoint `POST /inspections/{id}/attachments/initiate` calls SP to create Document record and returns `{ documentId, storagePath }`; (b) API endpoint `GET /attachments/{documentId}/upload-url` calls Azure Blob Storage SDK (not SQL) to generate a time-limited SAS token — acknowledge this as the only non-SQL API call; (c) `POST /attachments/{documentId}/finalize` calls SP to update Document metadata (size, hash, content-type) and links to `InspectionResponseAttachment`. This three-step flow must be explicit. |
| R-16 (MEK units) | **Minor** | Correct "MEK Rubs" to "MEK Double Rubs" in all documentation and seed data descriptions. Update `InspectionFrequencyType` description if any MEK-specific language exists. |
| R-17 (IATF clause citations) | **Minor** | Add IATF 16949:2016 clause citations to `docs/05_integration_architecture.md` audit section: §7.5 for template controlled document requirements, §8.6 for final/release inspection requirements, §9.1.1 for in-process inspection frequency requirements. |
| R-18 (No `/v1/` prefix) | **Minor** | In `docs/03_api_endpoint_design.md`, add a note: "All inspection endpoints will receive the `/v1/` prefix when API Phase 3.5 (URL versioning) executes. Implementation of inspection endpoints should use the `/v1/inspection-templates`, `/v1/inspections` etc. paths from the start if Phase 3.5 has already shipped." |
| R-19 (ProductionRun schema) | **Minor** | Add a note in `docs/01_database_schema_design.md` under Schema Assignment Rationale: "`inspection.ProductionRun` is placed in the inspection schema for v1 as a pragmatic choice. If a future Production Execution module requires production run data, this table should be migrated to `dbo` or a dedicated `production` schema via a renaming migration. Until then, callers must reference `inspection.ProductionRun`." |
| R-20 (Adhesion modeling note) | **Minor** | Add to `docs/01_database_schema_design.md` a note under Coating Measurement Fields: "ASTM D3359 adhesion (0B–5B scale) should be modeled as a NUMERIC field with integer values 0-5, where `MinValue = 4` for CQI-12 compliance. Do not model as an ATTRIBUTE (pass/fail) field — the ordinal value is required for SPC trend analysis and for identifying gradual degradation (e.g., dropping from 5B to 4B over time)." |

---

## 10. Follow-Up Prompt (If Required)

The package has one area requiring targeted expansion before a GSD executor can write `usp_SubmitInspection` correctly. The following prompt should be sent to GPT (or used as a context document for the GSD planner) to obtain the missing specification:

---

**Follow-Up Prompt: usp_SubmitInspection Evaluation Logic Specification**

You are the same Principal Quality Systems Architect who authored the Quality Inspection Forms Module package. I need you to expand the stored procedure contract for `inspection.usp_SubmitInspection` with complete evaluation rules. A GSD agent will write this procedure and cannot make assumptions.

Specifically, provide:

**1. Per-Criteria-Type Evaluation Rules (T-SQL pseudocode acceptable):**
- `InspectionCriteriaNumeric`: exact comparison logic to determine PASS / FAIL / MARGINAL / NA. Specify: when is a value MARGINAL vs FAIL (is it when it's outside MinValue/MaxValue but inside WarningMinValue/WarningMaxValue, or is MARGINAL a separate concept)? What happens if MinValue or MaxValue is NULL?
- `InspectionCriteriaAttribute`: how is the stored IsPass bit evaluated?
- `InspectionCriteriaSelection`: how are allowed option checks performed when `AllowMultiple = true`?
- `InspectionCriteriaText`: is there any evaluation (required non-empty)? When is it NA vs PASS?

**2. Overall Inspection Result Rollup Logic:**
- If any field produces FAIL → overall result = FAIL
- If no FAIL but any MARGINAL → overall result = MARGINAL
- If all responses are PASS or NA → overall result = PASS
- Specify how overall `FailCount`, `MarginalCount`, `PassCount`, `NaCount` are computed

**3. NCR Auto-Creation Trigger Check:**
For each `InspectionTemplateFieldCriteria` where `IsNcrAutoCreateEnabled = 1`:
- `NcrTriggerType = IMMEDIATE`: create NCR if this single submission produced a FAIL for this criteria
- `NcrTriggerType = FAIL_COUNT_WINDOW`: query `inspection.InspectionFinding` for this plant + this `InspectionTemplateFieldCriteriaId` in the last `TriggerWindowMinutes` minutes; if count of FAIL findings ≥ `TriggerFailCount`, create NCR
- `RemeasureAllowedCount > 0`: if this attempt number ≤ `RemeasureAllowedCount`, do NOT evaluate NCR trigger yet; only evaluate on the final allowed attempt
- What is the NCR defect type when auto-created? Use `InspectionTemplateFieldCriteria.DefectTypeId` if set, else `InspectionTemplateField.DefaultDefectTypeId`, else NULL
- What quantity is passed to `quality.usp_CreateNcrQuick`? Use a configurable default (e.g., 1) or derive from lot size if available

**4. Required Fields Completeness Check:**
- Which fields with `IsRequired = 1` must have a response before submission is allowed?
- If a required PHOTO_ATTACHMENT field has no response, is it error 53411 (missing required) or a different code?
- Are fields with `FieldType = NA` or criteria with `IsActive = 0` excluded from the required check?

**5. State Transition:**
- What status code does a SUBMITTED inspection transition to: `INSP_SUBMITTED` if supervisor review is required, or directly to `INSP_APPROVED` if no approval chain is configured?
- Does the transition call `workflow.usp_TransitionState` with `EntityType = 'Inspection'`?

Return this as an addendum to the stored procedure contract document section for `inspection.usp_SubmitInspection`.

