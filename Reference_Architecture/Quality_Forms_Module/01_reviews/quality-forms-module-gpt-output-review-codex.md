# Quality Forms Module — GPT Output Review

## Executive Summary
The package is strong on core relational modeling: it avoids EAV, keeps business logic in SQL contracts, uses idempotent migration guards, and includes RLS coverage for all 23 new `inspection.*` tables (`db/migrations/155_add_rls_predicates_inspection.sql`). The highest-risk gaps are governance and implementation readiness, not conceptual design. Specifically, contract-chain publication steps are asserted but not operationalized in phase tasks (`docs/06_phasing_recommendation.md:3-6`, `docs/06_phasing_recommendation.md:11-119`), and stored procedure contracts are incomplete (29 indexed, only 8 with full signatures/behavior blocks in `docs/02_stored_procedure_contracts.md:28-56`, `docs/02_stored_procedure_contracts.md:62-205`). There are also meaningful naming drifts around NCR foreign keys (`AutoNcrId`, `NcrId`) and one boolean naming violation (`AttributePass`) that should be corrected before code generation. Recommended course: accept the data-model direction, reject the current phasing/contract details as implementation-ready, and require the remediation set in Sections 9-10 before build starts.

## 1. Architecture Constraint Violations
| Violation | GPT Statement | Constraint Broken | Required Fix |
|---|---|---|---|
| ACV-01: Contract chain is declared but not executed in phase tasks | Declares chain: `docs/06_phasing_recommendation.md:3-6`; phase tasks omit explicit `db-contract-manifest.json` refresh, API publish, and app snapshot updates: `docs/06_phasing_recommendation.md:11-119` | Constraint #6 (contract-governed repos; PERSONA_PROMPT `:54`, CODEBASE_REFERENCE `:989-997`) | Add explicit phase gates: DB proc/view changes -> refresh `db-contract-manifest.json`; API changes -> refresh `db-contract-manifest.snapshot.json` and publish `api-openapi.publish.json`; app changes -> refresh `api-openapi.snapshot.json`. |
| ACV-02: Procedure surface incompleteness can force logic drift into API | 29 procedures listed (`docs/02_stored_procedure_contracts.md:28-56`), but only 8 have concrete signatures/behavior (`docs/02_stored_procedure_contracts.md:62-205`) | Constraint #1 (business logic in T-SQL) and #2 (thin Dapper API) from PERSONA_PROMPT `:49-50` | Fully specify all 29 procedure signatures/validation/error behavior before API implementation so C# remains transport-only. |

## 2. Naming & Schema Violations
| GPT Proposed Name | Correct Name | Rule Violated |
|---|---|---|
| `inspection.InspectionResponseAttribute.AttributePass` (`db/migrations/150_create_inspection_response_attribute.sql:25`) | `inspection.InspectionResponseAttribute.IsAttributePass` | Boolean columns must use `Is*` prefix (CODEBASE_REFERENCE `:36`) |
| `inspection.Inspection.AutoNcrId` (`db/migrations/146_create_inspection_instance.sql:74`) | `inspection.Inspection.AutoNonConformanceReportId` | FK column should align to referenced PK (`NonConformanceReportId`) (CODEBASE_REFERENCE `:35`) |
| `inspection.InspectionNcrLink.NcrId` (`db/migrations/148_create_inspection_ncr_link.sql:22`) | `inspection.InspectionNcrLink.NonConformanceReportId` | FK column naming alignment with referenced PK (CODEBASE_REFERENCE `:35`) |
| `FK_Inspection_AutoNcr` (`db/migrations/146_create_inspection_instance.sql:75`) | `FK_Inspection_NonConformanceReport` (or `FK_Inspection_AutoNonConformanceReport`) | FK constraint pattern drift (`FK_{Table}_{ReferencedTable}`; CODEBASE_REFERENCE `:38`) |
| `FK_InspectionNcrLink_Ncr` (`db/migrations/148_create_inspection_ncr_link.sql:23`) | `FK_InspectionNcrLink_NonConformanceReport` | FK constraint pattern drift (CODEBASE_REFERENCE `:38`) |
| `UQ_InspectionNcrLink_Inspection_Ncr` (`db/migrations/148_create_inspection_ncr_link.sql:31`) | `UQ_InspectionNcrLink_Inspection_NonConformanceReport` | Unique constraint naming column-token drift from canonical FK column name (CODEBASE_REFERENCE `:39`) |
| `IX_Inspection_AutoNcrId` (`db/migrations/146_create_inspection_instance.sql:113`) | `IX_Inspection_AutoNonConformanceReportId` | Index naming should track canonical column name (CODEBASE_REFERENCE `:42`) |
| `IX_InspectionNcrLink_NcrId` (`db/migrations/148_create_inspection_ncr_link.sql:34`) | `IX_InspectionNcrLink_NonConformanceReportId` | Index naming should track canonical column name (CODEBASE_REFERENCE `:42`) |
| `FK_InspectionTemplate_Family` (`db/migrations/133_create_inspection_template_revision.sql:18`) | `FK_InspectionTemplate_InspectionTemplateFamily` | FK suffix abbreviation vs referenced-table convention (CODEBASE_REFERENCE `:38`) |
| `FK_InspectionTemplateSection_Template` (`db/migrations/134_create_inspection_template_section.sql:18`) | `FK_InspectionTemplateSection_InspectionTemplate` | FK suffix abbreviation vs referenced-table convention (CODEBASE_REFERENCE `:38`) |
| `FK_InspectionTemplateField_Section` (`db/migrations/135_create_inspection_template_field.sql:18`) | `FK_InspectionTemplateField_InspectionTemplateSection` | FK suffix abbreviation vs referenced-table convention (CODEBASE_REFERENCE `:38`) |
| `FK_InspectionScheduleRule_AssignmentRule` (`db/migrations/144_create_inspection_schedule_rule.sql:20`) | `FK_InspectionScheduleRule_InspectionTemplateAssignmentRule` | FK suffix abbreviation vs referenced-table convention (CODEBASE_REFERENCE `:38`) |

## 3. Cross-Repo Impact Map
Source inventories:
- Tables: `db/migrations/132_*` through `db/migrations/154_*`
- Procedures: `docs/02_stored_procedure_contracts.md:28-56`
- Endpoints: `docs/03_api_endpoint_design.md:16-69`
- Frontend components: `docs/04_frontend_form_builder_architecture.md:39-55`, `docs/04_frontend_form_builder_architecture.md:98-116`

### 3.1 DB Tables
| Artifact | Repo | Depends On | Contract Impact | RLS Impact |
|---|---|---|---|---|
| `inspection.InspectionTemplateFamily` | db | `dbo.Plant`, `dbo.LookupValue`, `dbo.LineType` | None directly (schema only); downstream read/write procs must be in `db-contract-manifest.json` | `PlantId` table; must be on `security.PlantIsolationPolicy` (covered in migration 155) |
| `inspection.InspectionTemplate` | db | `inspection.InspectionTemplateFamily`, `dbo.StatusCode`, `dbo.Document`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionTemplateSection` | db | `inspection.InspectionTemplate`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionTemplateField` | db | `inspection.InspectionTemplateSection`, `dbo.LookupValue`, `dbo.Document`, `dbo.DefectType`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionTemplateFieldOption` | db | `inspection.InspectionTemplateField`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionTemplateFieldCriteria` | db | `inspection.InspectionTemplateField`, `dbo.LookupValue`, `dbo.DefectType`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionCriteriaNumeric` | db | `inspection.InspectionTemplateFieldCriteria`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionCriteriaAttribute` | db | `inspection.InspectionTemplateFieldCriteria`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionCriteriaSelection` | db | `inspection.InspectionTemplateFieldCriteria`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionCriteriaAllowedOption` | db | `inspection.InspectionTemplateFieldCriteria`, `inspection.InspectionTemplateFieldOption`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionCriteriaText` | db | `inspection.InspectionTemplateFieldCriteria`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionTemplateAssignmentRule` | db | `inspection.InspectionTemplateFamily`, `dbo.Customer`, `dbo.Part`, `dbo.LineType`, `dbo.ProductionLine`, `dbo.LineStage`, `dbo.Equipment`, `dbo.Supplier`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionScheduleRule` | db | `inspection.InspectionTemplateAssignmentRule`, `dbo.LookupValue`, `dbo.Plant` | Same as above | Same as above |
| `inspection.ProductionRun` | db | `dbo.Plant`, `dbo.ProductionLine`, `dbo.Customer`, `dbo.Part`, `dbo.Supplier`, `dbo.AppUser`, `dbo.StatusCode` | Same as above | Same as above |
| `inspection.Inspection` | db | `inspection.ProductionRun`, `inspection.InspectionTemplate`, `inspection.InspectionTemplateAssignmentRule`, `inspection.InspectionScheduleRule`, `quality.NonConformanceReport`, `dbo.* context tables` | Same as above | Same as above |
| `inspection.InspectionFinding` | db | `inspection.Inspection`, `inspection.InspectionTemplateField`, `inspection.InspectionTemplateFieldCriteria`, `dbo.LookupValue`, `dbo.DefectType`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionNcrLink` | db | `inspection.Inspection`, `quality.NonConformanceReport`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionResponseNumeric` | db | `inspection.Inspection`, `inspection.InspectionTemplateField`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionResponseAttribute` | db | `inspection.Inspection`, `inspection.InspectionTemplateField`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionResponseText` | db | `inspection.Inspection`, `inspection.InspectionTemplateField`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionResponseDateTime` | db | `inspection.Inspection`, `inspection.InspectionTemplateField`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionResponseSelection` | db | `inspection.Inspection`, `inspection.InspectionTemplateField`, `inspection.InspectionTemplateFieldOption`, `dbo.Plant` | Same as above | Same as above |
| `inspection.InspectionResponseAttachment` | db | `inspection.Inspection`, `inspection.InspectionTemplateField`, `dbo.Document`, `dbo.Plant` | Same as above | Same as above |

### 3.2 DB Stored Procedures
| Artifact | Repo | Depends On | Contract Impact | RLS Impact |
|---|---|---|---|---|
| `inspection.usp_CreateInspectionTemplateDraft` | db | `InspectionTemplateFamily`, `InspectionTemplate`, `security.usp_EvaluatePolicy` | Add proc to `db-contract-manifest.json`; API must refresh `db-contract-manifest.snapshot.json` | Must call `dbo.usp_SetSessionContext` |
| `inspection.usp_CreateInspectionTemplateRevisionDraft` | db | `InspectionTemplate*`, copy logic, policy checks | Same as above | Same as above |
| `inspection.usp_CloneInspectionTemplateToDraft` | db | `InspectionTemplateFamily`, `InspectionTemplate* children` | Same as above | Same as above |
| `inspection.usp_SaveInspectionTemplateDraftDefinition` | db | `InspectionTemplateSection`, `InspectionTemplateField`, options, criteria tables | Same as above | Same as above |
| `inspection.usp_PublishInspectionTemplate` | db | `InspectionTemplate`, `workflow.usp_TransitionState`, `dbo.Document` | Same as above | Same as above |
| `inspection.usp_RetireInspectionTemplate` | db | `InspectionTemplate`, workflow transition | Same as above | Same as above |
| `inspection.usp_GetInspectionTemplate` | db | Template family/revision/definition tables | Same as above | Same as above |
| `inspection.usp_ListInspectionTemplates` | db | `InspectionTemplateFamily`, `InspectionTemplate` | Same as above | Same as above |
| `inspection.usp_CreateAssignmentRule` | db | `InspectionTemplateAssignmentRule` + context refs | Same as above | Same as above |
| `inspection.usp_UpdateAssignmentRule` | db | `InspectionTemplateAssignmentRule` | Same as above | Same as above |
| `inspection.usp_DeactivateAssignmentRule` | db | `InspectionTemplateAssignmentRule` | Same as above | Same as above |
| `inspection.usp_ListAssignmentRules` | db | `InspectionTemplateAssignmentRule` | Same as above | Same as above |
| `inspection.usp_UpsertScheduleRule` | db | `InspectionScheduleRule`, lookup categories | Same as above | Same as above |
| `inspection.usp_GetDueInspections` | db | Assignment + schedule + template current revision + `ProductionRun` | Same as above | Same as above |
| `inspection.usp_AutoCreateDueInspections` | db | Due-evaluation logic + `Inspection` insert path | Same as above | Same as above |
| `inspection.usp_StartProductionRun` | db | `ProductionRun`, `StatusCode`, `AppUser` | Same as above | Same as above |
| `inspection.usp_EndProductionRun` | db | `ProductionRun`, `StatusCode` | Same as above | Same as above |
| `inspection.usp_ListActiveProductionRuns` | db | `ProductionRun` | Same as above | Same as above |
| `inspection.usp_CreateInspectionAdhoc` | db | `Inspection`, template refs, context snapshot tables | Same as above | Same as above |
| `inspection.usp_GetInspection` | db | `Inspection`, template definition, typed response tables | Same as above | Same as above |
| `inspection.usp_SaveInspectionResponses` | db | Typed response tables + attachment link table | Same as above | Same as above |
| `inspection.usp_SubmitInspection` | db | `Inspection`, criteria tables, finding tables, `quality.usp_CreateNcrQuick`, workflow transition | Same as above | Same as above |
| `inspection.usp_ApproveInspection` | db | `Inspection`, workflow transition, approval rules | Same as above | Same as above |
| `inspection.usp_RejectInspection` | db | `Inspection`, workflow transition | Same as above | Same as above |
| `inspection.usp_VoidInspection` | db | `Inspection`, workflow transition | Same as above | Same as above |
| `inspection.usp_QueryInspections` | db | `Inspection`, `InspectionFinding`, context filters | Same as above | Same as above |
| `inspection.usp_GetInspectionCompletionRates` | db | `Inspection`, due/effective windows | Same as above | Same as above |
| `inspection.usp_GetInspectionPassFailRates` | db | `Inspection`, `InspectionFinding`, result lookups | Same as above | Same as above |
| `inspection.usp_GetSpcMeasurementExtract` | db | `InspectionResponseNumeric`, template/part/line context | Same as above | Same as above |

### 3.3 API Endpoints
| Artifact | Repo | Depends On | Contract Impact | RLS Impact |
|---|---|---|---|---|
| `POST /inspection-templates` | api | `inspection.usp_CreateInspectionTemplateDraft` | Add operation to `api-openapi.publish.json`; app refreshes `api-openapi.snapshot.json` | Uses `DbConnectionFactory.CreateForUserAsync` + `dbo.usp_SetSessionContext` |
| `GET /inspection-templates` | api | `inspection.usp_ListInspectionTemplates` | Same as above | Same as above |
| `GET /inspection-templates/{id}` | api | `inspection.usp_GetInspectionTemplate` | Same as above | Same as above |
| `PUT /inspection-templates/{id}` | api | `inspection.usp_SaveInspectionTemplateDraftDefinition` | Same as above | Same as above |
| `POST /inspection-templates/{id}/new-revision` | api | `inspection.usp_CreateInspectionTemplateRevisionDraft` | Same as above | Same as above |
| `POST /inspection-templates/{id}/clone` | api | `inspection.usp_CloneInspectionTemplateToDraft` | Same as above | Same as above |
| `POST /inspection-templates/{id}/publish` | api | `inspection.usp_PublishInspectionTemplate` | Same as above | Same as above |
| `POST /inspection-templates/{id}/retire` | api | `inspection.usp_RetireInspectionTemplate` | Same as above | Same as above |
| `POST /inspection-templates/families/{familyId}/assignment-rules` | api | `inspection.usp_CreateAssignmentRule` | Same as above | Same as above |
| `PUT /assignment-rules/{id}` | api | `inspection.usp_UpdateAssignmentRule` | Same as above | Same as above |
| `DELETE /assignment-rules/{id}` | api | `inspection.usp_DeactivateAssignmentRule` | Same as above | Same as above |
| `PUT /assignment-rules/{id}/schedule` | api | `inspection.usp_UpsertScheduleRule` | Same as above | Same as above |
| `GET /assignment-rules` | api | `inspection.usp_ListAssignmentRules` | Same as above | Same as above |
| `POST /production-runs` | api | `inspection.usp_StartProductionRun` | Same as above | Same as above |
| `POST /production-runs/{id}/end` | api | `inspection.usp_EndProductionRun` | Same as above | Same as above |
| `GET /production-runs/active` | api | `inspection.usp_ListActiveProductionRuns` | Same as above | Same as above |
| `POST /inspections` | api | `inspection.usp_CreateInspectionAdhoc` | Same as above | Same as above |
| `GET /inspections/{id}` | api | `inspection.usp_GetInspection` | Same as above | Same as above |
| `PUT /inspections/{id}/responses` | api | `inspection.usp_SaveInspectionResponses` | Same as above | Same as above |
| `POST /inspections/{id}/submit` | api | `inspection.usp_SubmitInspection` | Same as above | Same as above |
| `POST /inspections/{id}/approve` | api | `inspection.usp_ApproveInspection` | Same as above | Same as above |
| `POST /inspections/{id}/reject` | api | `inspection.usp_RejectInspection` | Same as above | Same as above |
| `POST /inspections/{id}/void` | api | `inspection.usp_VoidInspection` | Same as above | Same as above |
| `GET /inspections/due` | api | `inspection.usp_GetDueInspections` | Same as above | Same as above |
| `POST /inspections/due/auto-create` | api | `inspection.usp_AutoCreateDueInspections` | Same as above | Same as above |
| `GET /inspections/search` | api | `inspection.usp_QueryInspections` | Same as above | Same as above |
| `GET /inspections/analytics/completion` | api | `inspection.usp_GetInspectionCompletionRates` | Same as above | Same as above |
| `GET /inspections/analytics/pass-fail` | api | `inspection.usp_GetInspectionPassFailRates` | Same as above | Same as above |
| `GET /spc/measurements` | api | `inspection.usp_GetSpcMeasurementExtract` | Same as above | Same as above |

### 3.4 Frontend Components
| Artifact | Repo | Depends On | Contract Impact | RLS Impact |
|---|---|---|---|---|
| `InspectionTemplateBuilderPage` | app | `GET/PUT /inspection-templates/{id}` | Consumes `api-openapi.snapshot.json`; refresh required when endpoint contracts change | Indirect through API session-context path |
| `TemplateHeaderForm` | app | `POST /inspection-templates`, `PUT /inspection-templates/{id}` | Same as above | Same as above |
| `BuilderWorkspace` | app | Template definition payload from `GET /inspection-templates/{id}` | Same as above | Same as above |
| `SectionNavigator` | app | Template sections in GET payload | Same as above | Same as above |
| `SectionCanvas` | app | Template sections/fields payload | Same as above | Same as above |
| `SectionCard` | app | Template sections payload | Same as above | Same as above |
| `FieldList` | app | Template fields payload | Same as above | Same as above |
| `FieldCard` | app | Template fields payload | Same as above | Same as above |
| `FieldPalette` | app | `InspectionFieldType` lookup values | Same as above | Same as above |
| `FieldEditorDrawer` | app | `PUT /inspection-templates/{id}` | Same as above | Same as above |
| `FieldBasicsTab` | app | Template field DTO contract | Same as above | Same as above |
| `CriteriaTab` | app | Criteria DTO contract + lookup values | Same as above | Same as above |
| `OptionsTab` | app | Options DTO contract | Same as above | Same as above |
| `AttachmentTab` | app | Attachment field config + `Document` linkage behavior | Same as above | Same as above |
| `ConditionalLogicTab` (v2) | app | Deferred (not in v1 backend contracts) | Future OpenAPI additions needed | Same as above |
| `TemplatePreviewPane` | app | Template definition payload | Same as above | Same as above |
| `PublishBar` | app | `POST /inspection-templates/{id}/publish` | Same as above | Same as above |
| `InspectionDueQueuePage` | app | `GET /inspections/due`, `POST /inspections/due/auto-create` | Same as above | Same as above |
| `ProductionRunSelector` | app | `GET /production-runs/active`, `POST /production-runs` | Same as above | Same as above |
| `DueInspectionTable` | app | Due queue payload contract | Same as above | Same as above |
| `StartInspectionDialog` | app | `POST /inspections` | Same as above | Same as above |
| `InspectionFillPage` | app | `GET /inspections/{id}`, `PUT /inspections/{id}/responses`, `POST /inspections/{id}/submit` | Same as above | Same as above |
| `InspectionContextHeader` | app | Inspection context payload | Same as above | Same as above |
| `InspectionFormRenderer` | app | Dynamic template/response schema | Same as above | Same as above |
| `SectionRenderer` | app | Dynamic section schema | Same as above | Same as above |
| `FieldRenderer` | app | Field-type registry + field payload | Same as above | Same as above |
| `NumericMeasurementField` | app | Numeric criteria and response contracts | Same as above | Same as above |
| `PassFailField` | app | Attribute criteria and response contracts | Same as above | Same as above |
| `TextField` | app | Text criteria and response contracts | Same as above | Same as above |
| `DateTimeField` | app | DateTime response contracts | Same as above | Same as above |
| `SelectField` | app | Selection options + response contracts | Same as above | Same as above |
| `MultiSelectField` | app | Selection options + response contracts | Same as above | Same as above |
| `PhotoAttachmentField` | app | Attachment upload/link flow (`DocumentId`) | Same as above | Same as above |
| `SubmitBar` | app | `PUT /inspections/{id}/responses`, `POST /inspections/{id}/submit` | Same as above | Same as above |

## 4. Phasing & Migration Sequencing Issues
1. The package phase plan starts at module Phase 1 immediately (`docs/06_phasing_recommendation.md:9-26`), but current planning baseline requires finishing DB Phase 23 and 24 first and only then starting v3 (`Execution_Plan.md:415-425`, `GSD_Seeding/PREPARATION_GUIDE.md:14-15`, `GSD_Seeding/PREPARATION_GUIDE.md:71-86`).
Corrected order: Finish DB Phases 23-24 -> refresh manifest -> archive v2.0 -> create v3 milestone -> place Forms module work in new milestone/phase set -> renumber migrations from actual live highest.

2. Migration numbering in the package assumes `130` as current top (`db/migrations/README.md:3-4`), while planning artifacts explicitly warn that numbering must continue from the live highest and v3 scaffolding is not yet created (`CODEBASE_REFERENCE.md:1016`, `GSD_Seeding/PREPARATION_GUIDE.md:15-21`).
Corrected order: reserve logical sequence only; at execution time renumber 131+ to current highest+1 after pulling latest DB migration history.

3. DB -> API -> App dependency order is stated globally (`Execution_Plan.md:40`) but not enforced in module phase steps.
Corrected order: DB schema and procedures land first; then refresh `db-contract-manifest.json`; then API snapshots DB contract and publishes `api-openapi.publish.json`; then app snapshots API OpenAPI and implements UI.

4. API Phase 1 implementation is described before complete DB procedure specs exist (`docs/06_phasing_recommendation.md:16-24` vs `docs/02_stored_procedure_contracts.md:28-56`, only 8 detailed in `docs/02_stored_procedure_contracts.md:62-205`).
Corrected order: complete DB procedure contracts and SQL behavior specs for all listed procs first, then API endpoint implementation.

## 5. Domain Terminology Corrections
| GPT Term | Correct Term/Unit | Standard Reference |
|---|---|---|
| `InspectionFieldType` value `ATTRIBUTE` labeled as `Pass / Fail` (`db/migrations/156_seed_lookup_inspection.sql:72`) | Label as `Attribute / Categorical` (still can include pass/fail) so it also covers ordinal ratings like adhesion `0B-5B` | ASTM D3359 adhesion rating scale; PERSONA_PROMPT coating fields `:343` |
| Free-text `Units NVARCHAR(30)` in criteria and responses (`db/migrations/138_create_inspection_criteria_numeric.sql:30`, `db/migrations/149_create_inspection_response_numeric.sql:26`, `db/migrations/147_create_inspection_finding.sql:41`) | Add canonical unit codes and validation set (`MIL`, `MICRON`, `GU`, `DELTA_E`, `HOUR`, `DOUBLE_RUB`, `B_RATING`) | PERSONA_PROMPT coating unit requirements `:342-348` |
| No explicit clause mapping fields/tags in template metadata or outputs | Add explicit traceability tags for IATF clauses 7.5, 8.6, 9.1.1 at template/header level | PERSONA_PROMPT compliance references `:12`, controlled forms context `:313-321` |

## 6. Design Question Assessment
| Question | Status | Gap/Issue | Required Addition |
|---|---|---|---|
| 1. Template versioning with in-progress forms | Yes | Decision is explicit and architecturally sound (`docs/00_key_decisions.md:7-15`) | Add guard spec in publish/revise procedures to block retroactive mutation of old revisions except controlled corrections. |
| 2. Acceptance criteria complexity without EAV | Yes | Typed criteria/response model is correct (`docs/00_key_decisions.md:19-38`) | Add explicit per-type validation contracts (units/method refs) in SP behavior for audit consistency. |
| 3. Assignment combinatorics hierarchy | Partially | Wildcard + `SpecificityScore` is good (`docs/00_key_decisions.md:42-55`, `db/migrations/143_create_inspection_assignment_rule.sql:46-54`) but overlap/tie conflict resolution is underspecified | Add deterministic SQL tie-break order and overlap-prevention constraints/indexed checks. |
| 4. Frequency enforcement and production signal integration | Yes | Manual `ProductionRun` anchor is reasonable for v1 (`docs/00_key_decisions.md:59-67`) | Add explicit behavior when no active run exists and timezone/shift boundary rules. |
| 5. NCR auto-creation threshold | Partially | Trigger knobs exist (`docs/00_key_decisions.md:71-80`, `db/migrations/137_create_inspection_field_criteria.sql:31-39`) but duplicate suppression/cooldown logic not defined | Define exact algorithm for duplicate prevention and remeasure exhaustion windows. |
| 6. Photo/attachment handling with Blob + Document | Partially | Architecture direction is correct (`docs/00_key_decisions.md:83-90`, `docs/05_integration_architecture.md:118-127`) | Add concrete SP contract set: create upload slot, finalize upload metadata, link attachment atomically. |
| 7. Offline/disconnected scope | Yes | Correctly deferred from v1 (`docs/00_key_decisions.md:93-104`) | Add explicit v1 guarantee statement: no offline submit; draft save requires round-trip success. |
| 8. SPC integration depth | Partially | Correctly avoids full SPC engine (`docs/00_key_decisions.md:107-115`) | Define `usp_GetSpcMeasurementExtract` output schema, filter params, cursor/pagination behavior. |

## 7. Deliverable Completeness Assessment
| Deliverable | Status | What's Missing | Blocker? Y/N |
|---|---|---|---|
| 1. Database Schema Design | Partially complete | DDL is present via migrations, but NCR naming drift and canonical unit governance gaps remain (`db/migrations/146_*`, `db/migrations/148_*`) | N (after rename fixes) |
| 2. Stored Procedure Contracts | Incomplete | 29 listed but only 8 with full signatures/behavior (`docs/02_stored_procedure_contracts.md:28-56`, `docs/02_stored_procedure_contracts.md:62-205`) | Y |
| 3. API Endpoint Design | Partially complete | Endpoint-to-proc mapping exists; per-endpoint request/response bodies, error codes, and status matrices are not fully specified (`docs/03_api_endpoint_design.md:14-69`, `docs/03_api_endpoint_design.md:126-129`) | Y |
| 4. Frontend Form Builder Architecture | Mostly complete | Strong component hierarchy and rendering approach; missing precise contract assumptions for attachment finalize and SPC/export UX | N |
| 5. Integration Architecture | Partially complete | Three Mermaid sequences provided, but attachment SAS flow and contract publication flow are prose-only (`docs/05_integration_architecture.md:118-127`) | N |
| 6. Phasing Recommendation | Incomplete | Not aligned to active DB milestone state and misses explicit contract-chain publication gates (`docs/06_phasing_recommendation.md:9-119`, `Execution_Plan.md:415-425`) | Y |

## 8. Practical Value Assessment
### What this module unlocks
- Controlled digital inspection templates with revision locking and history.
- Typed inspection response capture suitable for analytics/SPC feed.
- Formal linkage from inspection failures to NCR lifecycle entities.
- Plant-scoped queryability for auditor-style trace requests by part/line/date.

### Audit findings / IATF risks directly closed
- Controlled-document traceability for inspection forms (IATF clause 7.5) through template revision records and publish workflow.
- Release evidence and inspection execution traceability (IATF clause 8.6) via `inspection.Inspection` + typed responses + findings.
- Measurable monitoring data capture (IATF clause 9.1.1) through structured result/finding/response data.

### Manual processes eliminated by role
- Operators: paper forms and manual frequency tracking replaced by due queue + guided fill.
- Supervisors: manual review logbooks replaced by workflow-backed submit/approve/reject transitions.
- Quality engineers: spreadsheet collation for pass/fail and NCR triggers replaced by queryable SQL procedures.

### Downstream capabilities enabled
- NCR auto-creation from configurable failure patterns.
- SPC extraction pipeline from numeric response tables.
- Cross-entity traceability queries (inspection -> finding -> NCR -> workflow history).
- Future integration with MES production signals without schema replacement (manual `ProductionRun` is swappable anchor).

### MVP with measurable compliance value
- MVP should include: template draft/publish, manual inspection creation/fill/submit, typed response persistence, RLS enforcement, inspection/NCR linkage.
- Defer: offline sync engine, full attachment orchestration hardening, and advanced analytics/SPC UI.

### Complexity that likely exceeds immediate value
- Delivering 30 migrations before first auditable workflow use may delay value; split into strict MVP and expansions.
- Dynamic schema-detection seeding for `dbo.StatusCode` is defensive but adds runtime ambiguity; replace with explicit column contract once schema is confirmed.
- Workflow seed depth is high before confirming `workflow.usp_TransitionState` entity-type support in live code.

## 9. Full Remediation Guide
| Issue ID | Severity (Breaking/Significant/Minor) | Exact fix — complete DDL correction, procedure rename, endpoint path change, etc. |
|---|---|---|
| R-01 | Breaking | Update `docs/06_phasing_recommendation.md` to add explicit contract tasks in every phase: (a) DB changes -> refresh `db-contract-manifest.json`; (b) API changes -> refresh `db-contract-manifest.snapshot.json` and publish `api-openapi.publish.json`; (c) App changes -> refresh `api-openapi.snapshot.json`. |
| R-02 | Breaking | Expand `docs/02_stored_procedure_contracts.md` with full signature + behavior + error codes for missing 21 procs: `usp_CloneInspectionTemplateToDraft`, `usp_RetireInspectionTemplate`, `usp_GetInspectionTemplate`, `usp_ListInspectionTemplates`, `usp_CreateAssignmentRule`, `usp_UpdateAssignmentRule`, `usp_DeactivateAssignmentRule`, `usp_ListAssignmentRules`, `usp_UpsertScheduleRule`, `usp_StartProductionRun`, `usp_EndProductionRun`, `usp_ListActiveProductionRuns`, `usp_CreateInspectionAdhoc`, `usp_GetInspection`, `usp_ApproveInspection`, `usp_RejectInspection`, `usp_VoidInspection`, `usp_QueryInspections`, `usp_GetInspectionCompletionRates`, `usp_GetInspectionPassFailRates`, `usp_GetSpcMeasurementExtract`. |
| R-03 | Significant | In `db/migrations/150_create_inspection_response_attribute.sql`, change `AttributePass BIT NOT NULL` to `IsAttributePass BIT NOT NULL`; update all references and included-index columns accordingly. |
| R-04 | Significant | In `db/migrations/146_create_inspection_instance.sql`, rename `AutoNcrId` -> `AutoNonConformanceReportId`; rename `FK_Inspection_AutoNcr` -> `FK_Inspection_NonConformanceReport`; rename `IX_Inspection_AutoNcrId` -> `IX_Inspection_AutoNonConformanceReportId`; update all INCLUDE/WHERE references. |
| R-05 | Significant | In `db/migrations/148_create_inspection_ncr_link.sql`, rename `NcrId` -> `NonConformanceReportId`; rename `FK_InspectionNcrLink_Ncr` -> `FK_InspectionNcrLink_NonConformanceReport`; rename `UQ_InspectionNcrLink_Inspection_Ncr` -> `UQ_InspectionNcrLink_Inspection_NonConformanceReport`; rename `IX_InspectionNcrLink_NcrId` -> `IX_InspectionNcrLink_NonConformanceReportId`. |
| R-06 | Minor | Normalize abbreviated FK names to referenced-table naming in core files: `FK_InspectionTemplate_Family`, `FK_InspectionTemplateSection_Template`, `FK_InspectionTemplateField_Section`, `FK_InspectionScheduleRule_AssignmentRule` -> explicit referenced table tokens. |
| R-07 | Breaking | Rework `docs/06_phasing_recommendation.md` sequencing to align with live planning constraints: finish DB Phase 23/24 first (`Execution_Plan.md:415-425`), then place Forms work into a post-v2 milestone and renumber migrations from live highest. |
| R-08 | Significant | Add an explicit “DB procedures complete before API implementation” gate to phase plan; API endpoint work must not start from index-only SP names. |
| R-09 | Significant | Add assignment-rule conflict handling: enforce deterministic tie-break (`SpecificityScore DESC`, `RulePriority ASC`, `EffectiveFrom DESC`, `InspectionTemplateAssignmentRuleId DESC`) and add overlap-prevention checks in assignment-rule write procedures. |
| R-10 | Significant | Define NCR auto-create dedupe logic in `usp_SubmitInspection`: include cooldown window key (`InspectionTemplateFieldCriteriaId`, context dimensions, time bucket) to prevent repeated NCR creation from repeated submissions. |
| R-11 | Significant | Add attachment SP contracts: `inspection.usp_CreateInspectionAttachmentUpload`, `inspection.usp_FinalizeInspectionAttachmentUpload`, and link finalization behavior in `usp_SaveInspectionResponses` or dedicated link proc. |
| R-12 | Significant | Specify `inspection.usp_GetSpcMeasurementExtract` output contract: required columns, time filters, part/line/template filters, paging/cursor behavior, and null-handling for units. |
| R-13 | Minor | Introduce canonical measurement-unit governance: add lookup category for allowed units and validate in criteria/response save procedures; avoid free-form unit drift for DFT/Gloss/DeltaE/SaltSpray/MEK/Adhesion ratings. |
| R-14 | Significant | Expand `docs/03_api_endpoint_design.md` to include per-endpoint request schema, response schema, success/failure status codes, and mapped SQL error codes (including 53xxx additions) so OpenAPI publication can be generated without guesswork. |
| R-15 | Minor | Add explicit IATF clause tags at template level (`IatfClauseCode`, optional many-to-many mapping table if needed) and include in template retrieval contract for audit traceability narratives. |

## 10. Follow-Up Prompt (If Required)
```text
Revise the Quality Inspection Forms Module package for sf-quality using the existing files as baseline. Keep all core design decisions that are compliant (typed response model, RLS, SQL-first logic, Dapper thin API), but produce a corrected implementation-ready package with the following mandatory changes:

1) Contract-chain enforcement:
- Add explicit phase tasks for db-contract-manifest.json refresh, api db-contract-manifest snapshot refresh, api-openapi.publish.json publication, and app api-openapi.snapshot.json refresh.
- Reflect these steps in phasing docs and integration flow diagrams.

2) Stored procedure contract completion:
- For all 29 listed inspection procedures, provide full signatures, parameter definitions, result-set contracts, error codes, and step-by-step behavior.
- Ensure workflow, permission, and NCR integration behavior is explicit and SQL-authoritative.

3) Naming and DDL corrections:
- Rename AttributePass -> IsAttributePass.
- Rename AutoNcrId -> AutoNonConformanceReportId and NcrId -> NonConformanceReportId.
- Rename related FK/UQ/IX constraints accordingly.
- Normalize key FK naming to FK_{Table}_{ReferencedTable} where currently abbreviated.

4) Design question gaps:
- Add deterministic assignment-rule conflict/tie handling.
- Add NCR duplicate-suppression/cooldown logic.
- Add full attachment upload/finalize/link stored procedure contracts.
- Add explicit SPC extract schema and paging contract.

5) Domain terminology hardening:
- Replace ATTRIBUTE “Pass/Fail” label with Attribute/Categorical wording.
- Add canonical unit governance for DFT (mils/microns), Adhesion (0-5B), MEK rub count, Gloss (GU), Delta E, Salt Spray (hours), and related coating metrics.
- Add explicit IATF clause traceability tags (7.5, 8.6, 9.1.1).

6) Sequencing alignment:
- Align module rollout with current sf-quality planning baseline: DB Phase 23/24 completion before new milestone execution, and migration renumbering from live highest migration at execution time.

Output format:
- Keep the same 10-section package structure, but include line-level precision and implementation-ready contracts.
```
