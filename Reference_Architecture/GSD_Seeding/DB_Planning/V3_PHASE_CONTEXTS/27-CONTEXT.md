# Phase 27 — Approval Lifecycle and Timeout Processing

**Milestone:** v3.0 Architectural Hardening and Platform Maturation
**Track:** Main dependency chain (gate: Phases 25 + 26 complete)
**Requirements:** ARCH-04, ARCH-05
**Source patterns:** Pattern_Mapping.md #3, #20

---

## Reference Architecture Patterns

### Pattern #3 — Approval Timeout and Auto-Resolution
- **Gap:** `workflow.ApprovalChain.TimeoutAction` and `TimeoutHours` columns capture intent, but `workflow.PendingApprovalTransition` rows are not automatically evaluated or resolved when they expire.
- **Scope:** Add expiry timestamps to pending-approval rows and create a scheduled processor that applies the chain timeout policy deterministically.

### Pattern #20 — Optimistic Commit Mode for Safety-Critical Transitions
- **Gap:** All workflow transitions currently wait for approval completion before committing entity state changes. No presave/optimistic-commit path exists.
- **Scope:** Add `IsPresave BIT` to `workflow.WorkflowTransition`. On presave transitions, the entity state is committed immediately and a pending approval is created in parallel. If the approval is rejected, a compensating transition reverts the entity state.

**Hidden Pattern Distillation — Data Staging / Edit Mode Architecture:**
The reference platform's Data Staging pattern supports two commit modes: "presave" (immediate commit, approval in background) and "approved" (normal gate). This maps directly to the `IsPresave` flag approach. The "validate-only" sub-mode of this pattern is handled in Phase 32 (transaction rollback pattern), not here.

---

## Existing Artifacts

This phase builds on:
- `workflow.PendingApprovalTransition` with `Expired` status (migration 097) — has status but no expiry timestamp
- `workflow.ApprovalChain.TimeoutAction`, `TimeoutHours` (migration 051) — chain-level intent
- `workflow.usp_TransitionState` (migration 098) — transition orchestration proc to extend with presave path
- `workflow.usp_ProcessApprovalStep` (migration 099) — approval processing
- `workflow.usp_EnforceSeparationOfDuties` (Phase 26 deliverable — must exist)
- `workflow.usp_ResolveApprovers` (Phase 26 deliverable — must exist)

---

## Recommended Approach (Distilled)

### Plan 27-01: Approval Expiry Timestamps

```sql
-- ALTER workflow.PendingApprovalTransition to add expiry tracking
ALTER TABLE workflow.PendingApprovalTransition ADD
    ExpiresAtUtc          DATETIME2 NULL,       -- computed on creation from ApprovalChain.TimeoutHours
    TimeoutActionApplied  NVARCHAR(50) NULL;    -- 'AUTO-APPROVE', 'AUTO-REJECT', 'ESCALATE'

-- Populate ExpiresAtUtc for existing rows (if any are still pending):
-- ExpiresAtUtc = CreatedAtUtc + (TimeoutHours from ApprovalChain)
```

Create `workflow.usp_ProcessPendingApprovalTimeouts`:
```sql
-- workflow.usp_ProcessPendingApprovalTimeouts
-- Intended for scheduled execution (e.g., SQL Agent or Azure Functions timer)
-- For each expired PendingApprovalTransition (ExpiresAtUtc < SYSUTCDATETIME() AND TimeoutActionApplied IS NULL):
--   1. Look up ApprovalChain.TimeoutAction
--   2. Apply action: AUTO-APPROVE → call usp_ProcessApprovalStep(Approved); AUTO-REJECT → Reject; ESCALATE → escalate per EscalationRule
--   3. Set TimeoutActionApplied
--   4. Log to dbo.BackgroundJobRun (Phase 30 will create this table; use placeholder pattern here)
-- Returns: count of timeouts processed
```

### Plan 27-02: Presave (Optimistic Commit) Mode

```sql
-- ALTER workflow.WorkflowTransition to add presave flag
ALTER TABLE workflow.WorkflowTransition ADD
    IsPresave BIT NOT NULL DEFAULT 0;  -- 0 = normal gate; 1 = optimistic commit
```

**Presave path in `workflow.usp_TransitionState`:**

When processing a transition with `IsPresave = 1`:
1. **Immediately commit** entity state change (write to entity table, create `workflow.StatusHistory` row)
2. **Create** `workflow.PendingApprovalTransition` row for background approval
3. **Return** success to caller (entity is already in new state)

When the presave approval is **rejected**:
1. Create a **compensating transition** reverting the entity to its prior state
2. Record compensated status on the original `PendingApprovalTransition`
3. Notify originating user of rejection (write to `workflow.NotificationQueue` if Phase 28 is already deployed, otherwise use placeholder)

```sql
-- Add to workflow.WorkflowTransition or workflow.StatusHistory:
ALTER TABLE workflow.PendingApprovalTransition ADD
    IsPresaveCompensated  BIT NOT NULL DEFAULT 0,  -- 1 = compensating reversal was applied
    CompensatingTransitionId INT NULL;             -- FK to the reversal StatusHistory row
```

---

## Cross-Repo Dependencies

| Dependency | Direction | Details |
|-----------|-----------|---------|
| Phase 25 | DB → this phase | Stable `usp_TransitionState` foundation required for presave path addition |
| Phase 26 | DB → this phase | `usp_ResolveApprovers` and `usp_EnforceSeparationOfDuties` needed in timeout processor |
| This phase → Phase 28 | DB → DB | Phase 28's notification queue receives writes from presave rejection path |
| This phase → Phase 30 | DB → DB | `usp_ProcessPendingApprovalTimeouts` is a background job; Phase 30 adds `dbo.BackgroundJobRun` idempotency |

## Entry Criteria

- Phase 25 COMPLETE
- Phase 26 COMPLETE (usp_ResolveApprovers, usp_EnforceSeparationOfDuties exist)

## Exit Criteria (Gate for Phase 28)

1. `workflow.PendingApprovalTransition` has `ExpiresAtUtc` and `TimeoutActionApplied` columns
2. `workflow.usp_ProcessPendingApprovalTimeouts` callable — processes at least one synthetic expired row in a test migration
3. Presave transitions on `IsPresave=1` commit entity state immediately and create pending approval row
4. Rejected presave creates compensating transition reverting entity to prior state
5. `workflow.WorkflowTransition.IsPresave` column exists with DEFAULT 0
6. `Invoke-CycleChecks.ps1` passes
