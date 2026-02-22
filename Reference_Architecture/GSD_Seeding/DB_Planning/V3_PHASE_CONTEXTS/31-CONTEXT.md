# Phase 31 — Multi-Party Entity Lifecycle

**Milestone:** v3.0 Architectural Hardening and Platform Maturation
**Track:** Independent (no dependencies — execute in any order alongside main chain)
**Requirements:** ARCH-17, ARCH-18
**Source patterns:** Pattern_Mapping.md #19, #9

---

## Reference Architecture Patterns

### Pattern #19 — Multi-Party Entity Lifecycle Tracking
- **Gap:** `quality.SupplierCar` (SCAR) tracks a single overall status. There is no per-party status tracking — the customer response and supplier response are not independently tracked with their own status fields and history.
- **Scope:** Add `CustomerResponseStatus` and `SupplierResponseStatus` columns to `quality.SupplierCar`. Add `quality.ScarPartyStatusHistory` for audit trail of party status changes. Add `quality.vw_ScarPartyStatus` for dashboard reporting.

### Pattern #9 — Dual-Key Identity Pattern (Internal Surrogate + External Reference)
- **Gap:** `quality.NcrExternalReference` exists (migration 106) but lacks unique index enforcement for fast external-key lookups. Similar external reference patterns on other entities may not have index coverage.
- **Scope:** Add unique indexes on `quality.NcrExternalReference` and equivalent tables for deterministic external-key joins.

---

## Existing Artifacts

This phase builds on:
- `quality.SupplierCar` — SCAR entity table (verify column names from actual schema)
- `dbo.usp_GenerateDocumentNumber` (migration 008) — dual-key numbering
- `quality.NcrExternalReference` (migration 106) — NCR external key bridge table
- Existing SCAR workflow transitions (verify migrations for SCAR state machine)

---

## Recommended Approach (Distilled)

### Plan 31-01: SCAR Party Status Columns + History

```sql
-- ALTER quality.SupplierCar to add independent party status tracking
-- Note: Verify exact table name — may be quality.Scar, quality.SupplierCorrectiveActionRequest, etc.
ALTER TABLE quality.SupplierCar ADD
    CustomerResponseStatus  TINYINT NOT NULL DEFAULT 0,  -- 0=Pending,1=Acknowledged,2=Disputed,3=Accepted
    SupplierResponseStatus  TINYINT NOT NULL DEFAULT 0;  -- 0=Pending,1=InProgress,2=Submitted,3=Accepted

ALTER TABLE quality.SupplierCar ADD
    CONSTRAINT CHK_SupplierCar_CustomerResponseStatus CHECK (CustomerResponseStatus IN (0,1,2,3)),
    CONSTRAINT CHK_SupplierCar_SupplierResponseStatus CHECK (SupplierResponseStatus IN (0,1,2,3));
```

Create `quality.ScarPartyStatusHistory`:
```sql
CREATE TABLE quality.ScarPartyStatusHistory (
    ScarPartyStatusHistoryId INT IDENTITY(1,1) PRIMARY KEY,
    ScarId                   INT NOT NULL,  -- FK to quality.SupplierCar
    PartyType                NVARCHAR(20) NOT NULL,  -- 'Customer' or 'Supplier'
    PriorStatus              TINYINT NOT NULL,
    NewStatus                TINYINT NOT NULL,
    ChangedByUserId          INT NOT NULL,
    ChangedAtUtc             DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    ChangeReason             NVARCHAR(500) NULL
);

CREATE INDEX IX_ScarPartyStatusHistory_ScarId ON quality.ScarPartyStatusHistory (ScarId, ChangedAtUtc DESC);
```

Create `quality.vw_ScarPartyStatus`:
```sql
-- Dashboard view showing current party status per SCAR
CREATE VIEW quality.vw_ScarPartyStatus AS
SELECT
    s.ScarId,
    s.ScarNumber,
    s.CustomerResponseStatus,
    s.SupplierResponseStatus,
    -- Latest change timestamps from history
    (SELECT TOP 1 h.ChangedAtUtc FROM quality.ScarPartyStatusHistory h
     WHERE h.ScarId = s.ScarId AND h.PartyType = 'Customer'
     ORDER BY h.ChangedAtUtc DESC) AS CustomerStatusLastChangedAtUtc,
    (SELECT TOP 1 h.ChangedAtUtc FROM quality.ScarPartyStatusHistory h
     WHERE h.ScarId = s.ScarId AND h.PartyType = 'Supplier'
     ORDER BY h.ChangedAtUtc DESC) AS SupplierStatusLastChangedAtUtc
FROM quality.SupplierCar s;
```

### Plan 31-02: External Key Index Coverage

```sql
-- Enforce unique index on quality.NcrExternalReference for fast external-key lookups
-- Verify existing index coverage first
CREATE UNIQUE INDEX UIX_NcrExternalReference_ExternalKey
    ON quality.NcrExternalReference (ExternalSystemName, ExternalKey)
    WHERE ExternalKey IS NOT NULL;

-- Check other entities for external reference tables and add equivalent indexes
-- Pattern: any table with ExternalSystemName + ExternalKey or ExternalDocumentNumber columns
```

Add lookup proc for API:
```sql
-- quality.usp_GetScarPartyStatus(@ScarId INT)
-- Returns current party statuses + recent status change history
```

---

## Cross-Repo Dependencies

| Dependency | Direction | Details |
|-----------|-----------|---------|
| `CustomerResponseStatus` / `SupplierResponseStatus` columns | DB → API Phase 5 | **Hard gate:** API Phase 5 (SCAR/Audit endpoints) consumes these columns. Refresh `db-contract-manifest.json` after this phase. |
| `quality.vw_ScarPartyStatus` | DB → API Phase 5 | SCAR detail endpoint will expose this view |

**Important:** Refresh `db-contract-manifest.json` after completing this phase so API team can plan Phase 5 with accurate SCAR schema.

## Entry Criteria

- v3.0 milestone initialized; Phase 31 directory created
- Can execute in any order relative to Phases 25-30 and 33 (no dependencies)

## Exit Criteria (Gate for API Phase 5)

1. `quality.SupplierCar` has `CustomerResponseStatus` and `SupplierResponseStatus` TINYINT columns with CHECK constraints
2. `quality.ScarPartyStatusHistory` table exists
3. `quality.vw_ScarPartyStatus` returns party status dashboard data for all open SCARs
4. Unique index on `quality.NcrExternalReference` for external-key lookups
5. `db-contract-manifest.json` refreshed to include Phase 31 additions
6. `Invoke-CycleChecks.ps1` passes
