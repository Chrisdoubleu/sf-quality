# Phase 32 — Validate-Only and Reference Data

**Milestone:** v3.0 Architectural Hardening and Platform Maturation
**Track:** Independent with loose dependency on Phase 25
**Requirements:** ARCH-19, ARCH-20, ARCH-21
**Source patterns:** Pattern_Mapping.md #14, #10, #15

---

## Reference Architecture Patterns

### Pattern #14 — Validate-Only / Dry-Run Mode
- **Gap:** No write procedure accepts a dry-run / validate-only flag. Form preflight validation (App Phase 4+ requirement APP-FORM-03) depends on this pattern.
- **Scope:** Add `@IsValidateOnly BIT = 0` to 6+ write procedures using the transaction-rollback pattern.

**Hidden Pattern Distillation — Data Staging / Validate-Only Sub-Mode:**
The reference platform's Data Staging pattern includes a "validate-only" sub-mode where the system executes all validation logic but rolls back before committing. This is the correct approach for a SQL-first system — no staging schema needed, no additional tables, just a parameter flag + rollback pattern.

### Pattern #10 — Codebook Views and Reference Data Contract
- **Gap:** Lookup values (DefectType, Severity, Disposition, ProcessFamily, etc.) are queried via various ad-hoc mechanisms. There is no canonical codebook view surface that the API can depend on as a stable reference data contract.
- **Scope:** Create canonical lookup views/procs per domain as the authoritative reference data contract.

### Pattern #15 — Config Portability
- **Gap:** No configuration export/import mechanism exists. Moving configuration state between dev and prod environments requires manual script authoring.
- **Scope:** Create `security.usp_ExportConfiguration` / `security.usp_ImportConfiguration` with upsert semantics.

---

## Existing Artifacts

This phase builds on:
- `workflow.usp_TransitionState` (migration 098) — primary write proc for validate-only addition
- Various NCR/CAPA write procs — target for `@IsValidateOnly` parameter
- `dbo.DefectType`, `dbo.Severity`, `dbo.Disposition`, `quality.ProcessFamily` — codebook tables
- Existing lookup procs (verify which ones exist vs. are needed)
- `security.Permission`, `security.RolePermission`, `security.Feature` — config tables for export
- Phase 25 deliverable (`workflow.GuardDefinition`) — stable transition foundation before adding validate-only to transition procs

---

## Recommended Approach (Distilled)

### Plan 32-01: Validate-Only Pattern on Write Procs

**The validate-only pattern (apply to 6+ procs):**

```sql
-- Example: adding @IsValidateOnly to quality.usp_CreateNcr
ALTER PROCEDURE quality.usp_CreateNcr
    @NcrData    NVARCHAR(MAX),
    -- ... other params ...
    @IsValidateOnly BIT = 0  -- 0 = commit; 1 = validate and rollback
AS
BEGIN
    BEGIN TRANSACTION;

    -- All existing validation logic runs here (unchanged)
    -- ... validate NcrData, check constraints, evaluate workflow guards ...

    -- All write operations run here
    -- ... INSERT INTO quality.NonConformanceReport ... etc.

    IF @IsValidateOnly = 1
    BEGIN
        -- Rollback without error — return validation result as output
        ROLLBACK TRANSACTION;
        SELECT 'VALID' AS ValidationStatus, NULL AS ErrorCode, NULL AS ErrorMessage;
        RETURN;
    END

    COMMIT TRANSACTION;
    -- Normal success output
END
```

**Target procs for `@IsValidateOnly` addition (minimum 6):**
- `quality.usp_CreateNcr` (or equivalent NCR create proc)
- `quality.usp_UpdateNcr`
- `workflow.usp_TransitionState`
- `quality.usp_CreateCapa` (or CAPA write proc)
- `quality.usp_CreateScar` (or SCAR write proc)
- `quality.usp_RecordDisposition`

Verify actual proc names in the codebase before planning.

**Error output pattern on validation failure:**
```sql
-- When validation fails inside the transaction (before IsValidateOnly check):
-- Use RAISERROR or return a validation resultset, consistent with existing error patterns
SELECT 'INVALID' AS ValidationStatus, @ErrorCode AS ErrorCode, @ErrorMessage AS ErrorMessage;
```

### Plan 32-02: Canonical Lookup Views + Config Portability

**Canonical lookup views (reference data contract):**
```sql
-- One view per domain — naming pattern: domain.vw_[Domain]Lookup
CREATE VIEW quality.vw_DefectTypeLookup AS
    SELECT DefectTypeId, DefectCode, DefectName, ProcessFamilyId, IsActive FROM dbo.DefectType WHERE IsActive = 1;

CREATE VIEW quality.vw_SeverityLookup AS
    SELECT SeverityId, SeverityCode, SeverityName, SeverityLevel FROM dbo.Severity WHERE IsActive = 1;

CREATE VIEW quality.vw_DispositionLookup AS
    SELECT DispositionId, DispositionCode, DispositionName, IsActive FROM dbo.Disposition WHERE IsActive = 1;

-- Add ProcessFamily, PlantType, etc. as needed
```

**`security.usp_ExportConfiguration`:**
```sql
-- Exports current configuration state as a structured resultset
-- Covers: Roles, Permissions, Features, SlaConfiguration, workflow.GuardDefinition
-- Output: one resultset per config domain, each row serializable as JSON
-- Intended for: dev→prod bootstrap, backup before upgrades
CREATE PROCEDURE security.usp_ExportConfiguration AS
BEGIN
    SELECT 'Role' AS ConfigType, * FROM dbo.Role;
    SELECT 'Permission' AS ConfigType, * FROM security.Permission;
    SELECT 'Feature' AS ConfigType, * FROM security.Feature;
    SELECT 'SlaConfig' AS ConfigType, * FROM workflow.SlaConfiguration;
    SELECT 'GuardDefinition' AS ConfigType, * FROM workflow.GuardDefinition;
END
```

**`security.usp_ImportConfiguration`:**
```sql
-- Accepts config records and UPSERTs into target tables
-- Use MERGE pattern for idempotent import
-- Parameters: @ConfigType NVARCHAR(50), @ConfigJson NVARCHAR(MAX) (or TVP approach)
```

---

## Cross-Repo Dependencies

| Dependency | Direction | Details |
|-----------|-----------|---------|
| Phase 25 (loose) | DB → this phase | Stable `workflow.WorkflowTransition` and `GuardDefinition` ensure validate-only on transition proc is stable |
| `@IsValidateOnly` write procs | DB → API Phase 7 | **Hard gate:** API Phase 7 adds `?isValidateOnly=true` passthrough. Must have at least 3 procs with validate-only before API Phase 7 can execute. |
| `@IsValidateOnly` write procs | DB → App Phase 4+ | Form preflight (APP-FORM-03) depends on this pattern via API Phase 7 |
| Canonical lookup views | DB → API Phase 4 | Reference data endpoints in API Phase 4 will expose these views |

**Important:** Refresh `db-contract-manifest.json` after completing this phase so API team can plan Phase 7 with validate-only proc names.

## Entry Criteria

- Phase 25 COMPLETE (stable workflow foundation)
- Can execute in parallel with Phases 26-30 and 31, 33

## Exit Criteria (Gate for API Phase 7)

1. At least 6 write procs accept `@IsValidateOnly BIT = 0` and return `ValidationStatus` / `ErrorCode` / `ErrorMessage` resultset on rollback
2. Canonical lookup views exist: `quality.vw_DefectTypeLookup`, `quality.vw_SeverityLookup`, `quality.vw_DispositionLookup` (minimum 3 domains)
3. `security.usp_ExportConfiguration` produces a structured resultset covering all 5 config domains
4. `security.usp_ImportConfiguration` callable with upsert semantics
5. `db-contract-manifest.json` refreshed to include Phase 32 proc additions
6. `Invoke-CycleChecks.ps1` passes
