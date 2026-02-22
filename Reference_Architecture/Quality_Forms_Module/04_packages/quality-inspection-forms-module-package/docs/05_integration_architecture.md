# Deliverable 5: Integration Architecture

This document describes how the Inspection Forms module integrates with:
- Workflow (approval + status history)
- NCR (auto-create and linkage)
- Document system (attachments)
- Scheduling (due evaluation) without MES signals (v1)
- Audit/temporal retention

Endpoint examples use versioned API routes (`/v1/...`).

---

## Integration: Template → Approval → Publish

```mermaid
sequenceDiagram
  autonumber
  participant QE as Quality Engineer (App)
  participant API as sf-quality-api
  participant DB as Azure SQL (inspection SPs)
  participant WF as workflow.usp_TransitionState
  participant APR as workflow ApprovalChain

  QE->>API: POST /v1/inspection-templates (create draft)
  API->>DB: inspection.usp_CreateInspectionTemplateDraft(...)
  DB-->>API: NewTemplateId + summary
  API-->>QE: 201 Created

  QE->>API: PUT /v1/inspection-templates/{id} (save draft definition)
  API->>DB: inspection.usp_SaveInspectionTemplateDraftDefinition(...)
  DB-->>API: definition result sets
  API-->>QE: 200 OK

  QE->>API: POST /v1/inspection-templates/{id}/publish
  API->>DB: inspection.usp_PublishInspectionTemplate(...)
  DB->>WF: workflow.usp_TransitionState(EntityType='InspectionTemplate', ToStatus='INSP_TEMPLATE_ACTIVE')

  alt Approval required
    WF->>APR: Create approval records
    WF-->>DB: THROW 50414 (ApprovalRequired)
    DB-->>API: SQL error 50414
    API-->>QE: 202 Accepted (ApprovalRequired + approvalRecordId)
  else Approved / not gated
    WF-->>DB: StatusHistory written
    DB-->>API: publish success
    API-->>QE: 200 OK
  end
```

---

## Integration: Scheduling → Due Queue (v1 manual production run)

```mermaid
sequenceDiagram
  autonumber
  participant OP as Operator (App)
  participant API as sf-quality-api
  participant DB as Azure SQL

  OP->>API: POST /v1/production-runs (start run)
  API->>DB: inspection.usp_StartProductionRun(...)
  DB-->>API: ProductionRunId
  API-->>OP: 201 Created

  OP->>API: GET /v1/inspections/due?productionRunId=...
  API->>DB: inspection.usp_GetDueInspections(...)
  DB-->>API: due inspection candidates
  API-->>OP: 200 OK

  OP->>API: POST /v1/inspections/due/auto-create?productionRunId=...
  API->>DB: inspection.usp_AutoCreateDueInspections(...)
  DB-->>API: created inspection IDs
  API-->>OP: 201 Created
```

---

## Integration: Submit Inspection → Evaluate → Optional NCR auto-create

```mermaid
sequenceDiagram
  autonumber
  participant OP as Operator (App)
  participant API as sf-quality-api
  participant DB as Azure SQL
  participant NCR as quality.usp_CreateNcrQuick

  OP->>API: POST /v1/inspections/{id}/submit
  API->>DB: inspection.usp_SubmitInspection(...)

  DB->>DB: Evaluate responses vs criteria
  DB->>DB: Create findings + rollup result

  alt NCR trigger met
    DB->>NCR: quality.usp_CreateNcrQuick(...)
    NCR-->>DB: NewNcrId
    DB->>DB: Insert InspectionNcrLink + set Inspection.AutoNcrId
  end

  DB-->>API: inspection result summary
  API-->>OP: 200 OK
```

---

## Data Flow: Control Plan & Standard References

- A template revision is a controlled document:
  - `inspection.InspectionTemplate.DocumentId` (template document record)
- Field-level references:
  - `inspection.InspectionTemplateField.ControlPlanReferenceDocumentId`
  - `inspection.InspectionTemplateField.StandardReferenceDocumentId`

This avoids blocking on APQP/ControlPlan tables while still meeting document control expectations.

---

## Data Flow: Attachments / Photos

- Upload flow (recommended):
  1. Create `dbo.Document` metadata record (DB SP)
  2. API returns upload target (Blob SAS) and DocumentId
  3. Client uploads directly to Blob
  4. Finalize metadata (size/hash/content-type) with DB SP
  5. Link to inspection field via `inspection.InspectionResponseAttachment`

Database stores references; blob holds the bytes.

---

## Security Model (role intent)

Recommended permissions:
- Template authoring: create/edit/publish/retire
- Execution: fill/save/submit
- Review: approve/reject
- Analytics: view results, export SPC

Enforce permissions in SQL via existing `security.usp_EvaluatePolicy`.

---

## Audit & Retention

- Controlled document history: system-versioned temporal tables on template entities.
- Execution history: system-versioned temporal tables on inspections and responses.
- State transitions: immutable `workflow.StatusHistory` audit trail.

This supports “show me records for part X on line Y for last 6 months” queries without manual file chasing.
