# Live DB Validation Notes (2026-02-22)

Source: User-provided direct Azure SQL metadata query results.
Environment: `sqldb-quality-core-dev` on `sql-sf-quality-0b1f-dev.database.windows.net`
Timestamp (UTC): 2026-02-22 16:43:43

## 1) dbo.StatusCode live physical schema

- `dbo.StatusCode` exists and is a `SYSTEM_VERSIONED_TEMPORAL_TABLE`.
- `StatusCodeId` int NOT NULL IDENTITY (PK)
- `StatusCode` nvarchar(60) NOT NULL
- `StatusName` nvarchar(200) NOT NULL
- `Description` nvarchar(1000) NULL
- `EntityType` nvarchar(60) NOT NULL
- `StatusCategory` nvarchar(40) NOT NULL
- `IsFinal` bit NOT NULL default ((0))
- `IsActive` bit NOT NULL default ((1))
- `ColorHex` nvarchar(14) NULL
- `SortOrder` int NOT NULL default ((0))
- `CreatedBy` int NULL
- `CreatedDate` datetime2 NULL default (sysutcdatetime())
- `ModifiedBy` int NULL
- `ModifiedDate` datetime2 NULL default (sysutcdatetime())
- `ValidFrom` datetime2 NOT NULL hidden, AS_ROW_START
- `ValidTo` datetime2 NOT NULL hidden, AS_ROW_END

Required explicit insert fields (non-null, no default, non-generated):
- `StatusCode`
- `StatusName`
- `EntityType`
- `StatusCategory`

## 2) workflow.usp_TransitionState behavior for new entity types

- `workflow.usp_TransitionState` is not fully data-driven; it is hard-coded for known tables/entity types.
- No dynamic SQL (`sp_executesql` / `EXEC(@...)`) detected.
- Hard-coded `@EntityType` dispatch literals currently present:
  - `NCR`
  - `CAPA`
  - `CustomerComplaint`
  - `SupplierCAR`
  - `AuditFinding`
  - `EightDReport`
- No `Inspection` or `InspectionTemplate` handling found.
- `dbo.EntityTypeRegistry` includes `ActionItem`, but procedure dispatch list does not include it for status load/update.

## 3) Cross-environment consistency

- Same procedure/schema signatures in `sqldb-quality-core-prod` at query time (hash match).
