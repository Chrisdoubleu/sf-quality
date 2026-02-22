# Phase 25 — Workflow Engine Foundation Hardening

**Milestone:** v3.0 Architectural Hardening and Platform Maturation
**Track:** Main dependency chain (foundation for Phases 26, 27, 28, 32)
**Requirements:** ARCH-01, ARCH-02, ARCH-03
**Source patterns:** Pattern_Mapping.md #2, #11

---

## Reference Architecture Patterns

### Pattern #2 — Workflow Orchestration Engine with Typed Node Concepts
- **Gap:** Reusable condition catalogs and notification-node semantics are implicit (embedded at transition rows). No `workflow.GuardDefinition` table.
- **Scope:** Introduce reusable guard definitions and explicit notification metadata. Enhance `rca.EightDStep` step state tracking.

### Pattern #11 — Guided Process Orchestration / Workflow Immutability
- **Gap:** The 8D step model uses `IsComplete BIT` — insufficient for tracking in-progress, skipped, or blocked steps. No per-step prerequisite configuration. No workflow process versioning.
- **Scope (single-tenant):** Per-step state machine on `rca.EightDStep` (replacing `IsComplete BIT`). `workflow.WorkflowProcessVersion` for activation window and immutable-after-activation. No separate orchestration tier needed — the hidden pattern's monitoring workflow concept is achieved via `rca.vw_EightDCompletionStatus`.

**Hidden Pattern Distillation — Guided Process Orchestration:**
The reference platform uses a two-tier orchestration model (guided process conductor above the workflow engine) for multi-step processes like 8D investigations. For single-tenant scope, we achieve the equivalent by enriching `rca.EightDStep` with a proper state machine — each step tracks its own state independently, and `rca.vw_EightDCompletionStatus` computes process-level metrics without a separate orchestration service.

---

## Existing Artifacts

This phase builds on:
- `workflow.WorkflowProcess`, `workflow.WorkflowState`, `workflow.WorkflowTransition` (migration 046)
- `workflow.ApprovalChain`, `workflow.ApprovalStep` (migration 051)
- `workflow.usp_TransitionState` (migration 098)
- `workflow.SlaConfiguration` (migration 046)
- Guard evaluation in `workflow.usp_TransitionState` and `072_harden_workflow_guard_parsing.sql`
- `rca.EightDReport`, `rca.EightDStep` with D0-D8 disciplines (migration 037) — current `IsComplete BIT` flag

---

## Recommended Approach (Distilled)

### Plan 25-01: `rca.EightDStep` Step State Machine

```sql
-- ALTER rca.EightDStep to replace IsComplete BIT with richer state tracking
ALTER TABLE rca.EightDStep ADD
    StepStatus            TINYINT      NOT NULL DEFAULT 0,  -- 0=NotStarted,1=InProgress,2=Complete,3=Skipped,4=Blocked
    IsSkippable           BIT          NOT NULL DEFAULT 0,
    SkippedReason         NVARCHAR(500) NULL,
    SkippedByUserId       INT           NULL REFERENCES dbo.[User](UserId),
    PrerequisiteStepNumber TINYINT      NULL;               -- advisory ordering gate

-- Add CHECK constraint for StepStatus values
ALTER TABLE rca.EightDStep
    ADD CONSTRAINT CHK_EightDStep_StepStatus
    CHECK (StepStatus IN (0,1,2,3,4));

-- Note: IsComplete BIT column should be kept for backwards compatibility in this migration
-- and aliased / deprecated in a follow-up, or dropped if no consumers reference it
```

Create `rca.vw_EightDCompletionStatus`:
```sql
-- Returns per-report step metrics for dashboard and SLA evaluation
SELECT
    r.EightDReportId,
    COUNT(*)                                          AS TotalSteps,
    SUM(CASE WHEN s.StepStatus = 2 THEN 1 ELSE 0 END) AS CompleteSteps,
    SUM(CASE WHEN s.StepStatus = 3 THEN 1 ELSE 0 END) AS SkippedSteps,
    SUM(CASE WHEN s.StepStatus = 1 THEN 1 ELSE 0 END) AS InProgressSteps,
    SUM(CASE WHEN s.StepStatus = 4 THEN 1 ELSE 0 END) AS BlockedSteps,
    SUM(CASE WHEN s.StepStatus = 0 THEN 1 ELSE 0 END) AS NotStartedSteps
FROM rca.EightDReport r
JOIN rca.EightDStep s ON s.EightDReportId = r.EightDReportId
GROUP BY r.EightDReportId;
```

### Plan 25-02: Reusable Guard Definitions + Workflow Versioning

**`workflow.GuardDefinition` table:**
```sql
CREATE TABLE workflow.GuardDefinition (
    GuardDefinitionId INT IDENTITY(1,1) PRIMARY KEY,
    GuardKey          NVARCHAR(100) NOT NULL UNIQUE,  -- e.g. 'has-open-ncr', 'severity-gt-2'
    Description       NVARCHAR(500) NOT NULL,
    EvaluationExpression NVARCHAR(MAX) NOT NULL,       -- T-SQL expression or stored proc name
    IsActive          BIT NOT NULL DEFAULT 1,
    CreatedAtUtc      DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
```

Add optional notification metadata columns to `workflow.WorkflowTransition`:
```sql
ALTER TABLE workflow.WorkflowTransition ADD
    NotificationTemplateKey  NVARCHAR(100) NULL,   -- references future notification template
    NotifyOnTransition       BIT NOT NULL DEFAULT 0;
```

**`workflow.WorkflowProcessVersion` table:**
```sql
CREATE TABLE workflow.WorkflowProcessVersion (
    ProcessVersionId   INT IDENTITY(1,1) PRIMARY KEY,
    WorkflowProcessId  INT NOT NULL REFERENCES workflow.WorkflowProcess(WorkflowProcessId),
    VersionNumber      NVARCHAR(20) NOT NULL,  -- e.g. '1.0', '2.0'
    ActivatedAtUtc     DATETIME2 NULL,
    DeactivatedAtUtc   DATETIME2 NULL,
    IsImmutable        BIT NOT NULL DEFAULT 0  -- set to 1 on activation; prevents further modifications
);
```

---

## Cross-Repo Dependencies

| Dependency | Direction | Details |
|-----------|-----------|---------|
| Phase 25 complete | DB → DB Phase 26 | Guard definitions must exist before Phase 26 adds `workflow.usp_ResolveApprovers` |
| Phase 25 complete | DB → DB Phase 27 | `IsPresave` flag and presave path in `usp_TransitionState` depends on stable transition model |
| Phase 25 complete | DB → DB Phase 32 | Validate-only changes to `usp_TransitionState` need stable workflow foundation |
| `rca.vw_EightDCompletionStatus` | DB → API Phase 6 | Phase 6 (RCA Tools) will expose this view via API |

## Entry Criteria

- v3.0 milestone initialized; Phase 25 directory created
- Phase 29 may execute in parallel (independent track)
- This CONTEXT file reviewed by planner

## Exit Criteria (Gate for Phase 26)

1. `workflow.GuardDefinition` table exists and is queryable with at least 1 seeded guard definition
2. `rca.EightDStep.StepStatus` column exists with CHECK constraint and non-zero default behavior
3. `rca.vw_EightDCompletionStatus` returns non-null aggregated results for any `EightDReportId`
4. `workflow.WorkflowProcessVersion` table exists with activation window columns
5. `Invoke-CycleChecks.ps1` passes
