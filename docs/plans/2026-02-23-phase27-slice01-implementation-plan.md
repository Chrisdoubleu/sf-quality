# Phase 27 Slice 01 Timeout Contract Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver a DB-first approval-timeout contract surface for Phase 27 Slice 01 and update Phase 27 planning stubs into actionable state, with downstream changes only if required by producer contract deltas.

**Architecture:** Extend existing `workflow.ApprovalTimeoutQueue` infrastructure with producer-owned workflow stored procedures, then regenerate DB contract artifacts and validate via cycle checks. Keep API/App untouched unless a required producer snapshot propagation is necessary.

**Tech Stack:** Azure SQL migrations, PowerShell validation scripts, JSON contract manifests.

---

### Task 1: Create Isolated DB Workspace

**Files:**
- Create: global worktree path `~/.config/superpowers/worktrees/sf-quality-db/phase27-slice01-timeout-contract/`
- Verify: `database/migrations/`

**Step 1: Create feature worktree and branch**

Run:
```powershell
git -C C:/Dev/sf-quality-db worktree add C:/Users/chris/.config/superpowers/worktrees/sf-quality-db/phase27-slice01-timeout-contract -b phase27/slice01-timeout-contract
```
Expected: new worktree created and checked out on `phase27/slice01-timeout-contract`.

**Step 2: Baseline repo checks**

Run:
```powershell
pwsh -File scripts/Invoke-CycleChecks.ps1 -ChangedOnly
```
Expected: pass or skip with no failures before implementation.

**Step 3: Confirm clean baseline**

Run:
```powershell
git status --short
```
Expected: no local changes in DB worktree before edits.

### Task 2: Implement Timeout Queue Contract Surface (DB-first)

**Files:**
- Create: `database/migrations/139_phase27_timeout_contract_surface.sql`
- Modify: `.planning/contracts/db-contract-manifest.json`

**Step 1: RED check for new contract objects**

Run:
```powershell
rg -n "workflow\\.usp_EnqueueApprovalTimeouts|workflow\\.usp_GetApprovalTimeoutQueue" .planning/contracts/db-contract-manifest.json
```
Expected: no matches (objects absent before implementation).

**Step 2: Add migration with timeout queue procedures**

Create `database/migrations/139_phase27_timeout_contract_surface.sql` containing:
```sql
/*
    139_phase27_timeout_contract_surface.sql
    Phase 27 Slice 01: approval timeout contract surface.
*/

SET NOCOUNT ON;
GO

CREATE OR ALTER PROCEDURE workflow.usp_EnqueueApprovalTimeouts
    @CallerAzureOid UNIQUEIDENTIFIER
AS
BEGIN
    SET XACT_ABORT, NOCOUNT ON;
    EXEC dbo.usp_SetSessionContext @CallerAzureOid = @CallerAzureOid;

    ;WITH due_pending AS (
        SELECT
            pat.EntityType,
            pat.EntityId,
            DATEADD(HOUR, ac.TimeoutHours, pat.RequestedDate) AS TimeoutAtUtc,
            ac.TimeoutAction
        FROM workflow.PendingApprovalTransition pat
        INNER JOIN workflow.ApprovalChain ac
            ON ac.ApprovalChainId = pat.ApprovalChainId
        WHERE pat.Status = N'Pending'
          AND ac.IsActive = 1
          AND ac.TimeoutHours IS NOT NULL
          AND DATEADD(HOUR, ac.TimeoutHours, pat.RequestedDate) <= SYSUTCDATETIME()
    )
    INSERT INTO workflow.ApprovalTimeoutQueue
    (
        EntityType,
        EntityId,
        TimeoutAtUtc,
        TimeoutAction
    )
    SELECT d.EntityType, d.EntityId, d.TimeoutAtUtc, d.TimeoutAction
    FROM due_pending d
    WHERE NOT EXISTS (
        SELECT 1
        FROM workflow.ApprovalTimeoutQueue q
        WHERE q.EntityType = d.EntityType
          AND q.EntityId = d.EntityId
          AND q.TimeoutAtUtc = d.TimeoutAtUtc
    );

    SELECT @@ROWCOUNT AS EnqueuedCount;
END;
GO

CREATE OR ALTER PROCEDURE workflow.usp_GetApprovalTimeoutQueue
    @CallerAzureOid UNIQUEIDENTIFIER,
    @Top INT = 100
AS
BEGIN
    SET XACT_ABORT, NOCOUNT ON;
    EXEC dbo.usp_SetSessionContext @CallerAzureOid = @CallerAzureOid;

    IF @Top IS NULL OR @Top < 1 SET @Top = 100;
    IF @Top > 1000 SET @Top = 1000;

    SELECT TOP (@Top)
        q.ApprovalTimeoutQueueId,
        q.EntityType,
        q.EntityId,
        q.TimeoutAtUtc,
        q.TimeoutAction,
        q.ProcessedAtUtc,
        q.CreatedAtUtc
    FROM workflow.ApprovalTimeoutQueue q
    WHERE q.ProcessedAtUtc IS NULL
    ORDER BY q.TimeoutAtUtc ASC, q.ApprovalTimeoutQueueId ASC;
END;
GO
```

**Step 3: Static SQL validation**

Run:
```powershell
pwsh -File database/deploy/Test-SqlStaticRules.ps1 -RepoRoot (Get-Location)
```
Expected: pass with 0 violations.

**Step 4: Regenerate and validate DB contract manifest**

Run:
```powershell
pwsh -File database/deploy/Export-DbContractManifest.ps1 -RepoRoot (Get-Location)
pwsh -File database/deploy/Test-DbContractManifest.ps1 -RepoRoot (Get-Location)
rg -n "workflow\\.usp_EnqueueApprovalTimeouts|workflow\\.usp_GetApprovalTimeoutQueue" .planning/contracts/db-contract-manifest.json
```
Expected: manifest validation passes and both procedures are present.

### Task 3: Update Phase 27 Planning Stubs to Actionable State

**Files:**
- Modify: `.planning/phases/27-approval-lifecycle-timeout-processing/27-CONTEXT.md`
- Modify: `.planning/phases/27-approval-lifecycle-timeout-processing/27-RESEARCH.md`
- Modify: `.planning/phases/27-approval-lifecycle-timeout-processing/27-VERIFICATION.md`

**Step 1: Update context with slice map and Slice 01 scope**

Add concrete slice map (Slice 01 contract surface, Slice 02 processor apply semantics, Slice 03 downstream exposure and monitoring).

**Step 2: Update research with producer-first findings**

Record that migration `133` provided queue storage and Slice 01 adds executable contract SPs as minimal extension.

**Step 3: Update verification file status and evidence placeholders**

Set status to in-progress and add explicit command/output capture section for cycle checks.

**Step 4: Planning consistency validation**

Run:
```powershell
pwsh -File scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)
```
Expected: pass.

### Task 4: Downstream Producer-First Propagation Check

**Files:**
- Conditionally modify: `C:/Dev/sf-quality-api/.planning/contracts/db-contract-manifest.snapshot.json`
- Conditionally modify: `C:/Dev/sf-quality-api/.planning/contracts/api-openapi.publish.json`
- Conditionally modify: `C:/Dev/sf-quality-app/.planning/contracts/api-openapi.snapshot.json`

**Step 1: Determine required downstream delta**

Decision rule:
- If only DB-internal contract/procedure additions exist and no API usage is introduced in Slice 01, no API/App contract publication change is required.
- If API DB snapshot policy requires immediate sync for this delta, update API snapshot only; app changes still not required unless OpenAPI changes.

**Step 2: Apply only required changes**

Run downstream updates only if Step 1 requires them.

### Task 5: Verification and Handoff Output

**Files:**
- Modify: `.planning/phases/27-approval-lifecycle-timeout-processing/27-VERIFICATION.md` (append run evidence)

**Step 1: Run required verification commands**

Run in each touched repo:
```powershell
pwsh -File scripts/Invoke-CycleChecks.ps1 -ChangedOnly
```

If API runtime code changed:
```powershell
dotnet test
```

**Step 2: Record evidence**

Capture pass/fail by repo and drift findings in Phase 27 verification doc.

**Step 3: Prepare handoff output**

Provide:
1. findings first (bugs/risks/regressions),
2. implemented Slice 01 summary,
3. next-slice (Slice 02) prompt.
