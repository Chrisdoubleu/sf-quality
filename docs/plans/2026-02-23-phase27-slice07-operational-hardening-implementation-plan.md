# Phase 27 Slice 07 Operational Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close Phase 27 Slice 06 operational residuals by hardening processor-adoption controls and formalizing timeout alert thresholds, while keeping producer-first DB-only scope unless downstream evidence requires propagation.

**Architecture:** Add one producer migration to codify wrapper-first processor execution and operational alert thresholds, then update Phase 27 planning/handoff docs with findings protocol carry-forward coverage and verification evidence.

**Tech Stack:** Azure SQL migrations, PowerShell verification scripts, markdown planning artifacts.

---

### Task 1: Baseline and RED checks

**Files:**
- Verify: `database/migrations/`
- Verify: `.planning/contracts/db-contract-manifest.json`

**Step 1: Confirm clean baseline and anchor**

Run:
```powershell
git rev-parse HEAD
git status --short --branch
```
Expected: `2c13db6fbd81a2ce822e90182fe41c064f681f11` on `main` and clean working tree.

**Step 2: RED check for new operational alert contract**

Run:
```powershell
rg -n "workflow\\.usp_GetApprovalTimeoutOperationalAlerts" .planning/contracts/db-contract-manifest.json
```
Expected: no match (contract absent before Slice 07 implementation).

**Step 3: RED check for wrapper-adoption bootstrap guard**

Run:
```powershell
rg -n "DirectBypassExecute:workflow\\.usp_ApplyApprovalTimeoutQueueItem|DirectBypassExecute:workflow\\.usp_AcknowledgeApprovalTimeoutQueueItem" database/migrations/*.sql
```
Expected: no match (guard absent before Slice 07 implementation).

### Task 2: Implement Slice 07 DB hardening migration

**Files:**
- Create: `database/migrations/144_phase27_timeout_operational_hardening_contract.sql`

**Step 1: Add wrapper-adoption enforcement**

Implement:
- revoke direct `EXECUTE` on:
  - `workflow.usp_ApplyApprovalTimeoutQueueItem`
  - `workflow.usp_AcknowledgeApprovalTimeoutQueueItem`
- target role:
  - `dbrole_ncr_integration`
- preserve `workflow.usp_ProcessApprovalTimeoutQueueItem` as processor runtime path.

**Step 2: Add operational threshold contract**

Implement:
- `workflow.usp_GetApprovalTimeoutOperationalAlerts` with threshold parameters for:
  - ack-missed age (`ApplyAckDueAtUtc`)
  - dead-letter age (`ScopeDeadLetteredAtUtc`)
- output severity (`Info`/`Warning`/`Critical`) and summary counts.

**Step 3: Update bootstrap contract for wrapper adoption**

Implement:
- `workflow.usp_CheckApprovalTimeoutProcessorBootstrap` checks:
  - required timeout permissions active, no deny, plant-scoped allow.
  - required execute coverage for wrapper and operational observability procedures.
  - direct bypass execute checks on apply/ack procedures (must be absent for processor principal).

### Task 3: Refresh DB planning artifacts

**Files:**
- Modify: `.planning/phases/27-approval-lifecycle-timeout-processing/27-CONTEXT.md`
- Modify: `.planning/phases/27-approval-lifecycle-timeout-processing/27-RESEARCH.md`
- Modify: `.planning/phases/27-approval-lifecycle-timeout-processing/27-VERIFICATION.md`
- Modify: `.planning/contracts/db-contract-manifest.json`

**Step 1: Regenerate contract manifest**

Run:
```powershell
pwsh -File database/deploy/Export-DbContractManifest.ps1 -RepoRoot (Get-Location)
```
Expected: migration count and procedure list include Slice 07 artifacts.

**Step 2: Update planning docs**

Add Slice 07 sections for:
- runbook/threshold contract decisions,
- wrapper-adoption and bootstrap-principal validation evidence,
- downstream API/App no-change rationale.

### Task 4: Verification gates

**Files:**
- Verify only: repo scripts and planning docs

**Step 1: DB verification**

Run:
```powershell
pwsh -File database/deploy/Test-DbContractManifest.ps1 -RepoRoot (Get-Location)
pwsh -File database/deploy/Test-SqlStaticRules.ps1 -RepoRoot (Get-Location)
pwsh -File scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)
pwsh -File scripts/Invoke-CycleChecks.ps1 -ChangedOnly
```
Expected: all PASS.

**Step 2: API/App downstream gate re-check**

Run:
```powershell
rg -n "ApprovalTimeout|TimeoutQueue|WF\\.Approvals\\.Timeout|usp_ProcessApprovalTimeoutQueueItem" C:/Dev/sf-quality-api
rg -n "ApprovalTimeout|TimeoutQueue|WF\\.Approvals\\.Timeout|usp_ProcessApprovalTimeoutQueueItem" C:/Dev/sf-quality-app
```
Expected: no concrete runtime consumer trigger evidence.

**Step 3: API/App cycle checks**

Run if repo touched or requested for explicit evidence:
```powershell
pwsh -File scripts/Invoke-CycleChecks.ps1 -ChangedOnly
```
Expected: PASS or SKIP with no failures.

### Task 5: Findings protocol and handoff updates

**Files:**
- Modify: `C:/Dev/sf-quality/docs/plans/2026-02-23-immediate-deployment-rbac-full-sequence-handoff.md`
- Create: `C:/Dev/sf-quality/docs/plans/2026-02-23-phase27-slice07-execution-handoff.md`

**Step 1: Revalidate carry-forward findings**

Revalidate/close/carry:
- `FND-20260223-01`
- `FND-20260223-02`
- processor-adoption dependency finding
- bootstrap self-check principal caveat finding

**Step 2: Enforce findings coverage evidence**

Run:
```powershell
rg -n "FND-[0-9]{8}-[0-9]{2}" C:/Dev/sf-quality/docs/plans/*.md
```
Expected: all open/partial findings have carry-forward targets with `file:line`.

**Step 3: Produce next-slice prompt**

Create Slice 08 prompt from post-Slice 07 baseline and open findings set.
