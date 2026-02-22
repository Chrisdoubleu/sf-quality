# Phase 33 — Data Lifecycle and Bulk Operations

**Milestone:** v3.0 Architectural Hardening and Platform Maturation
**Track:** Independent (no dependencies — execute in any order)
**Requirements:** ARCH-22, ARCH-23
**Source patterns:** Pattern_Mapping.md #16, #24

---

## Reference Architecture Patterns

### Pattern #16 — Retention and Purging (Data Lifecycle)
- **Gap:** `dbo.RecordRetentionPolicy` table exists (migration 024) but no archival or purge procedure evaluates it. Closed records accumulate indefinitely. Audit logs have no purge boundary.
- **Scope:** Create `dbo.usp_ArchiveClosedRecords`, `audit.usp_PurgeAuditBeyondRetention`, and `dbo.ArchivePurgeLog` tracking table.

### Pattern #24 — Bulk Import
- **Gap:** No bulk import procedures exist. Bootstrapping seed data (lookup values, defect types, knowledge entries) requires manual migration script authoring per dataset.
- **Scope:** Create `dbo.usp_BulkImportLookupValues`, `dbo.usp_BulkImportDefectTypes`, `dbo.usp_BulkImportKnowledgeEntries` as reusable bulk import procs.

---

## Existing Artifacts

This phase builds on:
- `dbo.RecordRetentionPolicy` (migration 024) — retention policy table (verify structure: EntityType, RetentionDays, ArchiveAfterDays, etc.)
- `audit.AuditLog` (migration 003) — entity mutation log to be purge-bounded
- Seed migration patterns from Phases 19-21 (knowledge entries bulk-seeded via INSERT) — bulk import follows similar patterns but as reusable procs
- `dbo.usp_BulkImportLookupValues` may partially exist (check existing migrations)

---

## Recommended Approach (Distilled)

### Plan 33-01: Archive and Purge Infrastructure

Create `dbo.ArchivePurgeLog` tracking table:
```sql
CREATE TABLE dbo.ArchivePurgeLog (
    ArchivePurgeLogId  INT IDENTITY(1,1) PRIMARY KEY,
    OperationType      NVARCHAR(20)  NOT NULL,  -- 'Archive' or 'Purge'
    EntityType         NVARCHAR(50)  NOT NULL,
    RowsAffected       INT           NOT NULL,
    CutoffDate         DATETIME2     NOT NULL,
    ExecutedAtUtc      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    ExecutedByJobRef   NVARCHAR(200) NULL,      -- BackgroundJobRun.IdempotencyKey reference
    Notes              NVARCHAR(500) NULL
);
```

Create `dbo.usp_ArchiveClosedRecords`:
```sql
-- Evaluates dbo.RecordRetentionPolicy for each entity type
-- For records that are closed/resolved AND past their ArchiveAfterDays:
--   - Mark as archived (IsArchived BIT flag if present, or soft-delete pattern)
--   - Log to dbo.ArchivePurgeLog
-- Parameters: @EntityType NVARCHAR(50) = NULL (NULL = all types), @DryRun BIT = 0
-- Returns: count of records archived
CREATE PROCEDURE dbo.usp_ArchiveClosedRecords
    @EntityType NVARCHAR(50) = NULL,
    @DryRun     BIT = 0,
    @IdempotencyKey NVARCHAR(200) = NULL  -- from dbo.BackgroundJobRun
AS BEGIN
    -- Check idempotency key if provided (Phase 30 dbo.BackgroundJobRun pattern)
    -- Evaluate RecordRetentionPolicy
    -- Archive qualifying records
    -- Log to ArchivePurgeLog
END
```

Create `audit.usp_PurgeAuditBeyondRetention`:
```sql
-- Purges audit.AuditLog rows older than retention threshold
-- Parameters: @RetentionDays INT = 2555 (7 years default), @DryRun BIT = 0
-- Returns: count of rows purged
-- Safety: never purges rows from last 30 days regardless of policy
-- Logs to dbo.ArchivePurgeLog
```

### Plan 33-02: Bulk Import Procedures

**`dbo.usp_BulkImportLookupValues`:**
```sql
-- Accepts JSON array of lookup value records (Code, Name, IsActive, etc.)
-- MERGE pattern: upsert by Code
-- Parameters: @TableTarget NVARCHAR(100), @LookupJson NVARCHAR(MAX)
-- Returns: rows inserted / updated / skipped counts
```

**`dbo.usp_BulkImportDefectTypes`:**
```sql
-- Accepts JSON array of defect type records
-- MERGE into dbo.DefectType by DefectCode
-- Handles ProcessFamilyId lookup by name if provided as string
-- Parameters: @DefectJson NVARCHAR(MAX), @DryRun BIT = 0
-- Returns: validation result (on DryRun) or row counts (on commit)
```

**`dbo.usp_BulkImportKnowledgeEntries`:**
```sql
-- Accepts JSON array of knowledge entry records
-- MERGE into appropriate knowledge table (RootCause, InvestigationStep, etc.) based on @TableTarget
-- Parameters: @TableTarget NVARCHAR(100), @KnowledgeJson NVARCHAR(MAX), @DryRun BIT = 0
-- Returns: rows inserted / updated counts
-- Note: follows same seed pattern as Phase 19-21 migrations but as a reusable proc
```

---

## Cross-Repo Dependencies

| Dependency | Direction | Details |
|-----------|-----------|---------|
| `dbo.BackgroundJobRun` (Phase 30) | DB → this phase | Archive proc's `@IdempotencyKey` parameter references Phase 30's background job table. If Phase 30 is not yet complete, implement without idempotency key and add it in a later migration. |
| Bulk import procs | DB → internal tooling | These procs are used for bootstrapping and migrations; no direct API consumer. App team may call them for test data seeding. |

## Entry Criteria

- v3.0 milestone initialized; Phase 33 directory created
- Can execute in any order — no hard dependencies

## Exit Criteria

1. `dbo.ArchivePurgeLog` table exists
2. `dbo.usp_ArchiveClosedRecords` callable with `@DryRun = 1` mode — returns count of qualifying records without committing
3. `audit.usp_PurgeAuditBeyondRetention` callable with `@DryRun = 1` mode
4. `dbo.usp_BulkImportLookupValues` callable and produces correct upsert counts on test data
5. `dbo.usp_BulkImportDefectTypes` callable
6. `dbo.usp_BulkImportKnowledgeEntries` callable
7. `Invoke-CycleChecks.ps1` passes
