# sf-quality Architecture Snapshot (for AI package)

_As of 2026-02-24. This is a condensed reference — the full briefing is in the prompt text._

## Platform Shape
- Contract-first 3-repo architecture: DB → API → App.
- DB owns business rules (stored-procedure contract).
- API is thin HTTP pass-through (Dapper, no ORM).
- App is planning-complete but source not started (Next.js 15 / React 19 / shadcn/ui).

## Published Contract State
- sf-quality-db: 151 migrations, 99 stored procedures, 38 views, 7 schemas.
- sf-quality-api OpenAPI: version 0.3.0, 30 operations, 29 paths.
- sf-quality-app: API snapshot pinned to 0.3.0.

## Key Existing Entities

### quality schema
- `NonConformanceReport` — NcrNumber, PlantId, StatusCodeId, PriorityLevelId, DefectTypeId, SeverityRatingId, DetectionProcessAreaId, QuantityAffected, QuantityRejected, QuantityInspected, DispositionCodeId, CustomerId, PartId, SupplierId, LotNumber, EstimatedCost, Description, ImmediateAction, CustomerApprovalRequired, CustomerApprovalReceived
  - Children: NcrContainmentAction, NcrDisposition, NcrCostEntry, NcrExternalReference, NcrNote
- `CorrectiveAction` (CAPA) — CapaNumber, SourceType, SourceRefId, OccurrenceRootCauseId, NonDetectionRootCauseId, SystemicRootCauseId, TargetCompletionDate, CompletedDate
  - Children: CapaAffectedPlant, CapaTeamMember, EffectivenessCheck
- `CustomerComplaint` — ComplaintNumber, CustomerId, ComplaintTypeId, QuantityAffected, CostClaim, ResponseDueDate, IsJustified
- `SupplierCar` (SCAR) — ScarNumber, SupplierId, PartId, DefectTypeId, QuantityRejected, CostChargedBack
- `QualityAudit` + `AuditFinding` — AuditNumber, AuditTypeId, FindingSeverityId, LinkedCapaId

### workflow schema
- `ActionItem` — ParentEntityType, ParentEntityId, AssignedToId, DueDate, CompletedById, VerifiedById (verifier ≠ completer)
- `StatusHistory` — EntityType, EntityId, FromStatusCodeId, ToStatusCodeId, DurationInState, SlaStatus

### rca schema
- EightDReport, FishboneDiagram, FiveWhysAnalysis, IsIsNotAnalysis, PfmeaHeader

### dbo schema (reference data)
- Plant, ProductionLine, Equipment, Shift, ProcessArea
- Customer, Supplier, Part, LineType
- DefectType (L1 category / L2 leaf, scoped to LineType via junction)
- StatusCode (39 codes, 5 entity types), PriorityLevel, SeverityRating, DispositionCode (11 codes)
- LookupValue (polymorphic), DocumentSequence

## NCR Lifecycle
```
DRAFT → OPEN → CONTAINED → INVESTIGATING → DISPOSED → PENDING_VERIFICATION → CLOSED
Special: VOID (any active), REOPEN (CLOSED → OPEN)
```

## Disposition Codes
USE-AS-IS, DEVIATE, REWORK, RECOAT, STRIP-RECOAT, REPROCESS, SCRAP, RETURN-CUST, RETURN-SUPP, SORT, HOLD

## Entities NOT Yet Built (Discovery Targets)
These are domains where the audit should propose new entity definitions:
- Inspection records (test results, measurements, pass/fail)
- Production runs / load tracking (load bar, rack, batch)
- Process parameters (temperatures, voltages, pressures, dwell times)
- Lab chemistry / bath analysis
- Maintenance / PM logs
- Document control / form revision tracking
- Packaging / shipping holds
- Training / competency records
- Calibration / MSA records

## Packaging Note
- Prompt file intentionally excluded from this package.
- Paste the prompt separately in chat, then upload this package zip.
