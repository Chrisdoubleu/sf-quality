# Deliverable 2: Stored Procedure Contracts

The API is a thin HTTP-to-SQL gateway. **All business rules live in stored procedures.**

This document defines the required stored procedure surface for the Inspection Forms module.

---

## Standard Conventions

All procedures in this module:

- Set RLS session context using the caller’s Azure OID (directly or via shared helper):
  - `dbo.usp_SetSessionContext(@CallerAzureOid)`
- Accept:
  - `@CallerAzureOid UNIQUEIDENTIFIER`
  - `@CorrelationId NVARCHAR(100) = NULL` (where cross-system traceability matters)
- Use `THROW` with 5xxxx business rule codes (see Error Registry).
- Prefer result sets for queries; use OUTPUT only for new IDs.
- Do not embed business logic in the API layer.

---

## Procedure Index

| Area | Procedure | Purpose |
|---|---|---|
| Templates | `inspection.usp_CreateInspectionTemplateDraft` | Create family + initial draft revision |
| Templates | `inspection.usp_CreateInspectionTemplateRevisionDraft` | Create next draft revision from an existing revision |
| Templates | `inspection.usp_CloneInspectionTemplateToDraft` | Clone template family into a new family |
| Templates | `inspection.usp_SaveInspectionTemplateDraftDefinition` | Save header/sections/fields/options/criteria (draft-only) |
| Templates | `inspection.usp_PublishInspectionTemplate` | Publish draft revision (approval-gated via workflow) |
| Templates | `inspection.usp_RetireInspectionTemplate` | Retire an active revision |
| Templates | `inspection.usp_GetInspectionTemplate` | Get template revision + nested definition (multi result sets) |
| Templates | `inspection.usp_ListInspectionTemplates` | List families with current revision summary |
| Assignments | `inspection.usp_CreateAssignmentRule` | Create wildcardable assignment rule |
| Assignments | `inspection.usp_UpdateAssignmentRule` | Update rule (effective-dated) |
| Assignments | `inspection.usp_DeactivateAssignmentRule` | Soft-disable |
| Assignments | `inspection.usp_ListAssignmentRules` | List rules by family or filter |
| Scheduling | `inspection.usp_UpsertScheduleRule` | Upsert schedule rule for an assignment |
| Scheduling | `inspection.usp_GetDueInspections` | Evaluate “due now” (no creation) |
| Scheduling | `inspection.usp_AutoCreateDueInspections` | Idempotently create due inspections |
| Runs | `inspection.usp_StartProductionRun` | Start run (v1 manual anchor) |
| Runs | `inspection.usp_EndProductionRun` | End run |
| Runs | `inspection.usp_ListActiveProductionRuns` | List active runs |
| Instances | `inspection.usp_CreateInspectionAdhoc` | Create manual inspection instance |
| Instances | `inspection.usp_GetInspection` | Get inspection + template definition + responses |
| Instances | `inspection.usp_SaveInspectionResponses` | Save draft responses (typed tables) |
| Instances | `inspection.usp_SubmitInspection` | Validate + evaluate + findings + optional NCR + transition |
| Instances | `inspection.usp_ApproveInspection` | Supervisor approval |
| Instances | `inspection.usp_RejectInspection` | Supervisor rejection (requires reason) |
| Instances | `inspection.usp_VoidInspection` | Void instance (requires reason) |
| Reporting | `inspection.usp_QueryInspections` | Search/filter inspections |
| Reporting | `inspection.usp_GetInspectionCompletionRates` | Completion vs due |
| Reporting | `inspection.usp_GetInspectionPassFailRates` | Pass/fail + defect breakdown |
| SPC | `inspection.usp_GetSpcMeasurementExtract` | Numeric measurement extract for SPC tool |

---

## Template Management Procedures

### `inspection.usp_CreateInspectionTemplateDraft`

```sql
CREATE OR ALTER PROCEDURE inspection.usp_CreateInspectionTemplateDraft
    @CallerAzureOid UNIQUEIDENTIFIER,
    @PlantId INT,
    @TemplateCode NVARCHAR(50),
    @TemplateName NVARCHAR(200),
    @TemplateTypeId INT,
    @LineTypeId INT = NULL,
    @Description NVARCHAR(500) = NULL,
    @ChangeSummary NVARCHAR(500) = NULL,
    @CorrelationId NVARCHAR(100) = NULL,
    @NewInspectionTemplateFamilyId INT OUTPUT,
    @NewInspectionTemplateId INT OUTPUT
```

**Behavior**
1. Set session context.
2. Check permission: `INSPECTION_TEMPLATE_CREATE` (via `security.usp_EvaluatePolicy`).
3. Validate uniqueness of `(PlantId, TemplateCode)` in `inspection.InspectionTemplateFamily`.
4. Insert:
   - `inspection.InspectionTemplateFamily`
   - `inspection.InspectionTemplate` revision 1 as DRAFT
5. OUTPUT the new IDs.
6. Return 1-row summary for UI.

---

### `inspection.usp_CreateInspectionTemplateRevisionDraft`

```sql
CREATE OR ALTER PROCEDURE inspection.usp_CreateInspectionTemplateRevisionDraft
    @CallerAzureOid UNIQUEIDENTIFIER,
    @InspectionTemplateFamilyId INT,
    @SourceInspectionTemplateId INT,
    @ChangeSummary NVARCHAR(500),
    @CorrelationId NVARCHAR(100) = NULL,
    @NewInspectionTemplateId INT OUTPUT
```

**Behavior**
- Permission: `INSPECTION_TEMPLATE_EDIT_DRAFT`
- Create next revision as DRAFT; copy definition objects from source revision.
- Enforce **one draft at a time** per family (recommended).

---

### `inspection.usp_SaveInspectionTemplateDraftDefinition`

```sql
CREATE OR ALTER PROCEDURE inspection.usp_SaveInspectionTemplateDraftDefinition
    @CallerAzureOid UNIQUEIDENTIFIER,
    @InspectionTemplateId INT,
    @DefinitionJson NVARCHAR(MAX),
    @CorrelationId NVARCHAR(100) = NULL
```

**Behavior**
- Draft-only enforcement.
- Parse via `OPENJSON`.
- Upsert by natural keys (SectionCode, FieldCode, OptionCode).
- Soft-deactivate missing items instead of deleting.
- Return multi result sets (header, sections, fields, options, criteria).

---

### `inspection.usp_PublishInspectionTemplate`

```sql
CREATE OR ALTER PROCEDURE inspection.usp_PublishInspectionTemplate
    @CallerAzureOid UNIQUEIDENTIFIER,
    @InspectionTemplateId INT,
    @CorrelationId NVARCHAR(100) = NULL,
    @Comments NVARCHAR(500) = NULL
```

**Behavior**
- Validate completeness.
- Transition state via `workflow.usp_TransitionState` for entity type `InspectionTemplate`.
- On success:
  - Set `IsCurrentRevision = 1` for this revision, and clear on prior revisions.
  - Create `dbo.Document` record for controlled template if missing.

---

## Assignment & Scheduling Procedures

### `inspection.usp_GetDueInspections`

```sql
CREATE OR ALTER PROCEDURE inspection.usp_GetDueInspections
    @CallerAzureOid UNIQUEIDENTIFIER,
    @PlantId INT,
    @AsOfUtc DATETIME2(0),
    @ProductionLineId INT = NULL,
    @ProductionRunId INT = NULL,
    @CustomerId INT = NULL,
    @PartId INT = NULL,
    @SupplierId INT = NULL
```

**Behavior**
- Resolve matching assignment rules by wildcard match and `SpecificityScore`.
- Determine the active template revision for each family.
- Compute due windows based on schedule rule and last completed inspection.
- Return due candidates (without creating instances).

---

### `inspection.usp_AutoCreateDueInspections`

Same inputs as `GetDueInspections`. Inserts missing due inspections idempotently (unique index on schedule+run+due time) and returns created inspections.

---

## Inspection Instance Lifecycle Procedures

### `inspection.usp_SaveInspectionResponses`

```sql
CREATE OR ALTER PROCEDURE inspection.usp_SaveInspectionResponses
    @CallerAzureOid UNIQUEIDENTIFIER,
    @InspectionId INT,
    @ResponsesJson NVARCHAR(MAX),
    @CorrelationId NVARCHAR(100) = NULL
```

**Behavior**
- Editable status only.
- Parse JSON and upsert into typed response tables.
- Attachments are stored as DocumentId links (file upload handled outside the proc).

---

### `inspection.usp_SubmitInspection`

```sql
CREATE OR ALTER PROCEDURE inspection.usp_SubmitInspection
    @CallerAzureOid UNIQUEIDENTIFIER,
    @InspectionId INT,
    @CorrelationId NVARCHAR(100) = NULL,
    @Comments NVARCHAR(500) = NULL
```

**Behavior**
1. Validate completeness (required fields answered).
2. Evaluate responses against criteria; set PASS/FAIL/MARGINAL/NA.
3. Create `inspection.InspectionFinding` rows.
4. Roll up overall result and counts.
5. If NCR trigger conditions met, create NCR using `quality.usp_CreateNcrQuick` and link it.
6. Transition state via workflow to SUBMITTED.

---

## Error Code Registry (module-local)

| Code | Meaning | Typical HTTP |
|---:|---|---:|
| 53000 | Validation failed | 400 |
| 53004 | Not found | 404 |
| 53009 | Conflict / already exists | 409 |
| 53201 | Draft already exists | 409 |
| 53210 | Template not in DRAFT | 409 |
| 53211 | Template incomplete | 422 |
| 53410 | Inspection not editable | 409 |
| 53411 | Missing required responses | 422 |
| 53412 | Response type mismatch | 422 |
| 53501 | NCR trigger config invalid | 422 |

These codes must be added to the API’s `SqlErrorMapper`.

