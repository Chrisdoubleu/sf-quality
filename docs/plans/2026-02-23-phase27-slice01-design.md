# Phase 27 Slice 01 Design (Approval Lifecycle Timeout Contract)

## Scope
Establish a DB-first timeout processing contract for approval lifecycle records without changing ABAC posture, explicit-grant authorization, or deny-by-default semantics.

## Problem
`workflow.ApprovalTimeoutQueue` exists (migration `133`) but there is no contract-level entry point to:
1. deterministically enqueue expired pending approvals, and
2. read unprocessed timeout work for downstream processors.

That leaves timeout processing infrastructure-only, not contract-addressable.

## Approach Options
1. **Recommended: queue contract SPs in `workflow` only (low churn)**
   - Add `workflow.usp_EnqueueApprovalTimeouts` and `workflow.usp_GetApprovalTimeoutQueue`.
   - Keep behavior producer-owned in DB and avoid API/App runtime changes in Slice 01.
   - Pros: minimal risk, deterministic, producer-first.
   - Cons: no API surface yet (deferred to later slice).

2. Add queue contract SPs plus API endpoints in the same slice
   - Pros: immediate end-to-end surface.
   - Cons: wider churn, higher regression risk, unnecessary for initial producer contract.

3. Contract-only docs update with no SQL changes
   - Pros: lowest code churn.
   - Cons: does not create executable timeout contract surface.

## Selected Design
Use option 1.

### Architecture
- **Producer contract layer (DB):**
  - `workflow.usp_EnqueueApprovalTimeouts`
  - `workflow.usp_GetApprovalTimeoutQueue`
- **Existing queue store:** `workflow.ApprovalTimeoutQueue` (already present)
- **Existing approval lifecycle sources:**
  - `workflow.PendingApprovalTransition`
  - `workflow.ApprovalChain` (`TimeoutHours`, `TimeoutAction`)

### Data Flow
1. Enqueue step scans `PendingApprovalTransition` rows with `Status='Pending'`.
2. Join to `ApprovalChain` and compute timeout cutoff from `RequestedDate + TimeoutHours`.
3. Insert due rows into `ApprovalTimeoutQueue` with idempotent uniqueness on `(EntityType, EntityId, TimeoutAtUtc)`.
4. Read step returns unprocessed queue rows (`ProcessedAtUtc IS NULL`) with deterministic ordering.

### Error Handling
- No new deny/authorization codes introduced in Slice 01.
- Procedures are idempotent and deterministic.
- Caller identity context is established via `@CallerAzureOid` to satisfy existing DB SP conventions.

### Compatibility and Constraints
- Preserve ABAC defer decision (`ADR-2026-02-22-abac-decision-gate.md`).
- Preserve explicit-grant and deny-by-default runtime behavior.
- No full remediation scans.
- Producer-first gating remains active; downstream changes only if DB contract deltas require it.

### Verification Strategy
- DB:
  - `pwsh -File scripts/Invoke-CycleChecks.ps1 -ChangedOnly`
  - Ensure DB contract manifest validation remains green.
- API/App:
  - Run cycle checks only if changed.
  - Run `dotnet test` in API only if runtime code changes.
