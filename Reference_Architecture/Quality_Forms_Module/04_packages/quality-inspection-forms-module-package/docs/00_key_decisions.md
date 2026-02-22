# Key Decisions & Explicit Answers

This document answers the “Key Design Questions” explicitly and records the most important architectural decisions.

---

## 1) Template versioning model

**Decision:** When a template is revised, **in-progress inspections complete under the old revision**.

**Implementation detail:**
- `inspection.Inspection` stores `InspectionTemplateId` (revision lock) at creation time.
- The form “definition at time of use” is preserved, which is the controlled-document expectation for IATF audits.

**No migration of in-flight instances** is performed when a new revision is published.

---

## 2) Acceptance criteria complexity (numeric vs attribute vs text vs selection) without EAV

**Decision:** Use **typed criteria tables** + **typed response tables**, not a generic FieldName/FieldValue design.

- Criteria:
  - `inspection.InspectionTemplateFieldCriteria` (base)
  - `inspection.InspectionCriteriaNumeric`
  - `inspection.InspectionCriteriaAttribute`
  - `inspection.InspectionCriteriaSelection` + `inspection.InspectionCriteriaAllowedOption`
  - `inspection.InspectionCriteriaText`

- Responses:
  - `inspection.InspectionResponseNumeric`
  - `inspection.InspectionResponseAttribute`
  - `inspection.InspectionResponseText`
  - `inspection.InspectionResponseDateTime`
  - `inspection.InspectionResponseSelection`
  - `inspection.InspectionResponseAttachment`

This keeps responses queryable and supports SPC extracts without runtime casting.

---

## 3) Assignment rule combinatorics (global → customer → part → line → stage → equipment)

**Decision:** Use **wildcardable assignment rules** where `NULL = applies to all`, and resolve matches by:
1. Highest computed `SpecificityScore` (more specified dimensions wins)
2. Then `RulePriority` (explicit override)
3. Then effective dating

**Implementation detail:**
- `inspection.InspectionTemplateAssignmentRule` includes:
  - `CustomerId`, `PartId`, `LineTypeId`, `ProductionLineId`, `LineStageId`, `EquipmentId`, `SupplierId`
  - computed `SpecificityScore` persisted column
  - `RulePriority` integer

This avoids combinatorial explosion while still enabling “part X on line 3 only” type rules.

---

## 4) Frequency enforcement without MES/real-time production signals (v1)

**Decision (v1):** Use a **manual ProductionRun** signal:
- operator or supervisor starts a run (`inspection.ProductionRun`)
- scheduling logic treats a run as the anchor for “production is happening”

Later enhancement (v2+):
- integrate with MES/ERP run signals or production scheduling feed
- keep the same tables; only replace the run creation source

---

## 5) NCR auto-creation threshold

**Decision:** NCR auto-create is **opt-in** and **configurable per field criteria**.

Supported trigger behaviors (v1):
- **Remeasure allowed:** allow N attempts before counting failure
- **Threshold in window:** create NCR only if `TriggerFailCount` failures occur within `TriggerWindowMinutes`

**Default:** `IsNcrAutoCreateEnabled = 0` so you don’t accidentally spam NCR creation.

---

## 6) Photo / attachment handling

**Decision:** Use the existing document registry:
- store an attachment as a `dbo.Document`
- link it to a field response via `inspection.InspectionResponseAttachment(DocumentId)`

Binary content lives in Blob Storage; DB stores metadata and storage key/path.

---

## 7) Offline/disconnected operation

**Decision:** Not in v1.

Offline requires:
- local persistence
- conflict resolution
- replay/merge semantics
- UI state recovery

That is a separate project. v1 should instead provide clear “connection lost” messaging and safe draft saving.

---

## 8) SPC integration depth

**Decision:** Don’t build an SPC engine in v1.

Capture measurement data in a way that enables SPC:
- numeric responses are stored as decimals with units and context
- provide an extract procedure `inspection.usp_GetSpcMeasurementExtract`

Export to a dedicated SPC tool or analytics pipeline later.

---

## 9) Workflow engine integration

**Decision:** Reuse existing workflow infrastructure **for controlled publish and inspection review/approval**, but:

- You must add new entity types to the workflow system:
  - `InspectionTemplate`
  - `Inspection`

This requires:
- extending the `workflow.WorkflowProcess.EntityType` check constraint to allow these values
- seeding `workflow.WorkflowProcess`, `workflow.WorkflowState`, `workflow.WorkflowTransition` rows for those entity types

**Critical note:** The package includes a seed script for workflow records. If `workflow.usp_TransitionState` internally hard-codes supported entity types, it must be extended to support the two new entity types.

See `docs/07_open_questions_and_todos.md`.

