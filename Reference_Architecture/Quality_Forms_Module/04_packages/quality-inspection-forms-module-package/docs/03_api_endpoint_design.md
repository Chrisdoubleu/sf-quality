# Deliverable 3: API Endpoint Design

The API is a thin gateway:
- One endpoint → one stored procedure
- Dapper only (`CommandType.StoredProcedure`)
- No business logic in C# (SQL is authoritative)
- Versioned routes (`/v1/...`) aligned to API infrastructure hardening direction

---

## Endpoint Groups

### Inspection Templates

| Method | Path | Stored Procedure |
|---|---|---|
| POST | `/v1/inspection-templates` | `inspection.usp_CreateInspectionTemplateDraft` |
| GET | `/v1/inspection-templates` | `inspection.usp_ListInspectionTemplates` |
| GET | `/v1/inspection-templates/{id}` | `inspection.usp_GetInspectionTemplate` |
| PUT | `/v1/inspection-templates/{id}` | `inspection.usp_SaveInspectionTemplateDraftDefinition` |
| POST | `/v1/inspection-templates/{id}/new-revision` | `inspection.usp_CreateInspectionTemplateRevisionDraft` |
| POST | `/v1/inspection-templates/{id}/clone` | `inspection.usp_CloneInspectionTemplateToDraft` |
| POST | `/v1/inspection-templates/{id}/publish` | `inspection.usp_PublishInspectionTemplate` |
| POST | `/v1/inspection-templates/{id}/retire` | `inspection.usp_RetireInspectionTemplate` |

### Assignment Rules & Scheduling

| Method | Path | Stored Procedure |
|---|---|---|
| POST | `/v1/inspection-templates/families/{familyId}/assignment-rules` | `inspection.usp_CreateAssignmentRule` |
| PUT | `/v1/assignment-rules/{id}` | `inspection.usp_UpdateAssignmentRule` |
| DELETE | `/v1/assignment-rules/{id}` | `inspection.usp_DeactivateAssignmentRule` |
| PUT | `/v1/assignment-rules/{id}/schedule` | `inspection.usp_UpsertScheduleRule` |
| GET | `/v1/assignment-rules` | `inspection.usp_ListAssignmentRules` |

### Production Runs

| Method | Path | Stored Procedure |
|---|---|---|
| POST | `/v1/production-runs` | `inspection.usp_StartProductionRun` |
| POST | `/v1/production-runs/{id}/end` | `inspection.usp_EndProductionRun` |
| GET | `/v1/production-runs/active` | `inspection.usp_ListActiveProductionRuns` |

### Inspections (Instances)

| Method | Path | Stored Procedure |
|---|---|---|
| POST | `/v1/inspections` | `inspection.usp_CreateInspectionAdhoc` |
| GET | `/v1/inspections/{id}` | `inspection.usp_GetInspection` |
| PUT | `/v1/inspections/{id}/responses` | `inspection.usp_SaveInspectionResponses` |
| POST | `/v1/inspections/{id}/submit` | `inspection.usp_SubmitInspection` |
| POST | `/v1/inspections/{id}/approve` | `inspection.usp_ApproveInspection` |
| POST | `/v1/inspections/{id}/reject` | `inspection.usp_RejectInspection` |
| POST | `/v1/inspections/{id}/void` | `inspection.usp_VoidInspection` |

### Due Queue / Auto-create

| Method | Path | Stored Procedure |
|---|---|---|
| GET | `/v1/inspections/due` | `inspection.usp_GetDueInspections` |
| POST | `/v1/inspections/due/auto-create` | `inspection.usp_AutoCreateDueInspections` |

### Reporting & SPC

| Method | Path | Stored Procedure |
|---|---|---|
| GET | `/v1/inspections/search` | `inspection.usp_QueryInspections` |
| GET | `/v1/inspections/analytics/completion` | `inspection.usp_GetInspectionCompletionRates` |
| GET | `/v1/inspections/analytics/pass-fail` | `inspection.usp_GetInspectionPassFailRates` |
| GET | `/v1/spc/measurements` | `inspection.usp_GetSpcMeasurementExtract` |

---

## Request DTO Shapes (C# records)

### Create template draft

```csharp
public record CreateInspectionTemplateDraftRequest(
    int PlantId,
    string TemplateCode,
    string TemplateName,
    int TemplateTypeId,
    int? LineTypeId = null,
    string? Description = null,
    string? ChangeSummary = null);
```

### Save draft definition

```csharp
public record SaveInspectionTemplateDraftDefinitionRequest(string DefinitionJson);
```

### Create adhoc inspection

```csharp
public record CreateInspectionAdhocRequest(
    int PlantId,
    int InspectionTemplateId,
    int? ProductionLineId = null,
    int? LineStageId = null,
    int? EquipmentId = null,
    int? CustomerId = null,
    int? PartId = null,
    int? SupplierId = null,
    string? WorkOrderNumber = null,
    string? LotNumber = null);
```

### Save responses

```csharp
public record SaveInspectionResponsesRequest(string ResponsesJson);
```

### Gate-style transitions

```csharp
public record GateTransitionRequest(string? Comments = null);
public record RejectInspectionRequest(string ReasonComment, string? Comments = null);
public record VoidInspectionRequest(string ReasonComment, string? Comments = null);
```

---

## Status Codes & Error Mapping

- SQL business codes are mapped to HTTP via `SqlErrorMapper`.
- Add the 53xxx inspection module codes to the map (see `docs/02_stored_procedure_contracts.md`).
- Approval-required workflow outcomes (`50414`) should return `202 Accepted` with structured payload (not `403`).

---

## Notes for Implementers

- The API must always open DB connections via `DbConnectionFactory.CreateForUserAsync(...)` to ensure session context + RLS are active.
- Endpoints must not implement evaluation logic; they only pass through JSON payloads and return procedure result sets.
- Keep route grouping under `/v1` from initial implementation to avoid post-build route churn.
