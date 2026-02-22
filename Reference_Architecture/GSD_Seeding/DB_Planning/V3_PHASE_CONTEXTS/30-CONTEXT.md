# Phase 30 — SLA Enforcement and Background Jobs

**Milestone:** v3.0 Architectural Hardening and Platform Maturation
**Track:** Main dependency chain (gate: Phase 27 complete)
**Requirements:** ARCH-11, ARCH-12, ARCH-13
**Source patterns:** Pattern_Mapping.md #12, #17

---

## Reference Architecture Patterns

### Pattern #12 — SLA / CAPA Timeline Compliance
- **Gap:** `workflow.SlaConfiguration` table exists but is unseeded for CAPA use cases. `workflow.usp_EvaluateEscalationRules` exists but is not wired to CAPA entities. No dashboard view for SLA compliance reporting.
- **Scope:** Seed CAPA SLA thresholds; wire escalation rules for CAPA; add `quality.vw_CapaTimelineCompliance` dashboard view.

### Pattern #17 — Policy Resolution Engine / Background Job Processing
- **Gap:** No `security.vw_EffectivePolicyMap` view for policy scope resolution. No idempotency key pattern on batch procedures. The `workflow.usp_ProcessPendingApprovalTimeouts` proc from Phase 27 has no safe-retry infrastructure.
- **Scope (single-tenant):** Add policy resolution diagnostic view. Add `dbo.BackgroundJobRun` tracking table with idempotency keys on batch procedures. Full rules-engine policy graph is out of scope.

**Hidden Pattern Distillation — Policy Resolution Engine:**
The reference platform implements a generic algorithm: identify policy candidates → filter by scope → resolve conflicts by priority → return effective policy. For single-tenant scope, we achieve this via `security.vw_EffectivePolicyMap` — a diagnostic view over existing `workflow.SlaConfiguration` and `security.Permission` tables that surfaces "effective" policy per entity/scope, without a separate rules engine. The resolution algorithm is: most-specific scope wins (entity > role > global).

---

## Existing Artifacts

This phase builds on:
- `workflow.SlaConfiguration` (migration 046) — SLA config table, exists but unseeded for CAPA
- `workflow.usp_EvaluateEscalationRules` (migration 062) — escalation processor, exists but not wired to CAPA
- `security.Permission`, `security.RolePermission` (migration 091) — policy foundation
- `security.usp_EvaluatePolicy` (migration 096) — policy evaluation proc
- `workflow.usp_ProcessPendingApprovalTimeouts` (Phase 27 deliverable — background job needing idempotency)

---

## Recommended Approach (Distilled)

### Plan 30-01: CAPA SLA Configuration + Timeline View

**Seed `workflow.SlaConfiguration` for CAPA:**
```sql
-- SLA thresholds by severity (Critical/Major/Minor maps to days)
-- Insert seeds for CAPA entity type
INSERT INTO workflow.SlaConfiguration (EntityType, SeverityLevel, WarningDays, EscalationDays, ClosureDays)
VALUES
    ('CAPA', 'Critical', 15, 25, 30),
    ('CAPA', 'Major',    30, 50, 60),
    ('CAPA', 'Minor',    60, 80, 90);
```

Wire `workflow.usp_EvaluateEscalationRules` to CAPA entities:
- Modify the proc (or add CAPA-specific call) to evaluate CAPA open items against SLA thresholds
- Trigger: called by `dbo.BackgroundJobRun` scheduler or manual invocation

Create `quality.vw_CapaTimelineCompliance`:
```sql
-- Returns CAPA SLA compliance status per open CAPA
-- Columns: CapaId, OpenedDate, SeverityLevel, WarningDate, EscalationDate, ClosureDeadline,
--          DaysOpen, IsWarning, IsEscalated, IsOverdue, SlaStatus
SELECT
    c.CapaId,
    c.OpenedAtUtc,
    c.SeverityLevel,
    DATEADD(DAY, sla.WarningDays, c.OpenedAtUtc)    AS WarningDate,
    DATEADD(DAY, sla.EscalationDays, c.OpenedAtUtc) AS EscalationDate,
    DATEADD(DAY, sla.ClosureDays, c.OpenedAtUtc)    AS ClosureDeadline,
    DATEDIFF(DAY, c.OpenedAtUtc, SYSUTCDATETIME())  AS DaysOpen,
    CASE WHEN SYSUTCDATETIME() >= DATEADD(DAY, sla.WarningDays, c.OpenedAtUtc) THEN 1 ELSE 0 END AS IsWarning,
    CASE WHEN SYSUTCDATETIME() >= DATEADD(DAY, sla.EscalationDays, c.OpenedAtUtc) THEN 1 ELSE 0 END AS IsEscalated,
    CASE WHEN SYSUTCDATETIME() >= DATEADD(DAY, sla.ClosureDays, c.OpenedAtUtc) THEN 1 ELSE 0 END AS IsOverdue
FROM quality.Capa c  -- adjust table name to actual CAPA entity table
JOIN workflow.SlaConfiguration sla ON sla.EntityType = 'CAPA' AND sla.SeverityLevel = c.SeverityLevel
WHERE c.ClosedAtUtc IS NULL;
```

### Plan 30-02: Policy Map View + Background Job Infrastructure

**`security.vw_EffectivePolicyMap` diagnostic view:**
```sql
-- Policy resolution: most-specific scope wins (entity > role > global)
-- Surfaces effective policy per permission per scope context
CREATE VIEW security.vw_EffectivePolicyMap AS
SELECT
    r.RoleName,
    f.FeatureName,
    p.ActionName,
    CASE
        WHEN rp.ConstraintExpression IS NOT NULL THEN 'entity-scoped'
        WHEN rp.RoleId IS NOT NULL THEN 'role-scoped'
        ELSE 'global'
    END AS PolicyScope,
    rp.IsGranted,
    rp.ConstraintExpression
FROM security.RolePermission rp
JOIN dbo.Role r ON r.RoleId = rp.RoleId
JOIN security.Permission p ON p.PermissionId = rp.PermissionId
JOIN security.Feature f ON f.FeatureId = p.FeatureId;
```

**`dbo.BackgroundJobRun` table:**
```sql
CREATE TABLE dbo.BackgroundJobRun (
    BackgroundJobRunId  INT IDENTITY(1,1) PRIMARY KEY,
    JobName             NVARCHAR(100) NOT NULL,
    IdempotencyKey      NVARCHAR(200) NOT NULL,  -- e.g. 'timeout-processor-2026-02-22T10:00:00Z'
    StartedAtUtc        DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CompletedAtUtc      DATETIME2     NULL,
    Status              NVARCHAR(20)  NOT NULL DEFAULT 'Running',  -- Running, Completed, Failed
    ErrorMessage        NVARCHAR(MAX) NULL,
    RowsProcessed       INT           NULL
);

CREATE UNIQUE INDEX IX_BackgroundJobRun_IdempotencyKey ON dbo.BackgroundJobRun (IdempotencyKey);
```

Add `@IdempotencyKey NVARCHAR(200) = NULL` parameter to batch procedures (at minimum to `workflow.usp_ProcessPendingApprovalTimeouts`). Pattern: check for existing `BackgroundJobRun` row with same key before executing.

---

## Cross-Repo Dependencies

| Dependency | Direction | Details |
|-----------|-----------|---------|
| Phase 27 | DB → this phase | `usp_ProcessPendingApprovalTimeouts` (Phase 27) is the primary background job needing idempotency from this phase |
| `quality.vw_CapaTimelineCompliance` | DB → API Phase 9 | Dashboards endpoint will expose this view |
| `security.vw_EffectivePolicyMap` | DB → API Phase 7 | Feature-gating endpoint will reference this |

## Entry Criteria

- Phase 27 COMPLETE (timeout processor proc exists, background job pattern needed)

## Exit Criteria

1. `workflow.SlaConfiguration` seeded with CAPA thresholds (30/60/90-day by severity level)
2. `workflow.usp_EvaluateEscalationRules` callable and processes CAPA entities
3. `quality.vw_CapaTimelineCompliance` returns compliance data for open CAPA records
4. `security.vw_EffectivePolicyMap` returns policy scope data
5. `dbo.BackgroundJobRun` table exists with idempotency key unique index
6. `Invoke-CycleChecks.ps1` passes
