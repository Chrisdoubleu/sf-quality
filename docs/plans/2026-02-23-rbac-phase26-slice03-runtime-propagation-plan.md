# RBAC Phase 26 Slice 03 Runtime Propagation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Propagate Phase 26 alias-resolution and deterministic policy-envelope behavior from `SubmitNcr` to all remaining NCR transition endpoints with minimal churn.

**Architecture:** Reuse existing API runtime components introduced in Slice 02 (`CapabilityAliasResolver`, `PermissionGate`, `PolicyEnvelopeFactory`) and apply endpoint-by-endpoint wiring only where workflow transitions execute. Preserve DB policy authority, explicit-grant runtime model, and deny-by-default semantics.

**Tech Stack:** ASP.NET Core Minimal APIs, Dapper, OpenAPI publish artifact sync, cross-repo cycle checks.

---

### Task 1: Transition Capability Matrix Lock

**Files:**
- Modify: `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs`
- Modify: `sf-quality-api/.planning/contracts/api-openapi.publish.json`
- Test: `sf-quality-api/tests/SfQualityApi.Tests/Infrastructure/PermissionGateTests.cs`

**Steps:**
1. Add/confirm capability IDs for transition handlers:
   - `F-NCR.CONTAIN.COMPLETE`
   - `F-NCR.INVEST.START`
   - `F-NCR.DISP.PROPOSE`
   - `F-NCR.VERIFY.QUEUE`
   - `F-NCR.CLOSE.EXECUTE`
   - `F-NCR.VOID`
   - `F-NCR.REOPEN`
2. Add failing tests asserting `PermissionGate.RequireAsync` + capability IDs exist on each transition handler.
3. Run failing test subset.
4. Commit test-only red stage.

### Task 2: Runtime Wiring Across Remaining Transition Endpoints

**Files:**
- Modify: `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs`
- Modify: `sf-quality-api/src/SfQualityApi/Infrastructure/PermissionGate.cs` (if shared helper adjustments needed)
- Modify: `sf-quality-api/src/SfQualityApi/Middleware/ErrorHandlingMiddleware.cs` (only if context propagation needs extension)
- Test: `sf-quality-api/tests/SfQualityApi.Tests/Infrastructure/PermissionGateTests.cs`

**Steps:**
1. Inject `ICapabilityAliasResolver` and `PolicyEnvelopeFactory` into each remaining transition handler.
2. Call `PermissionGate.RequireAsync` with capability ID + operation + entity ID context.
3. Return `PolicyEnvelopeFactory.CreateAllow(...)` envelopes for success responses.
4. Keep non-transition routes untouched.
5. Run targeted tests and then full `dotnet test`.
6. Commit runtime propagation changes.

### Task 3: OpenAPI and App Snapshot Sync

**Files:**
- Modify: `sf-quality-api/.planning/contracts/api-openapi.publish.json`
- Modify: `sf-quality-api/.planning/STATE.md`
- Modify: `sf-quality-app/.planning/contracts/api-openapi.snapshot.json`
- Modify: `sf-quality-app/.planning/STATE.md`

**Steps:**
1. Update each transitioned operation response schema to `PolicyEnvelope`.
2. Add/confirm `x-entitlement` metadata for transitioned operations.
3. Bump API contract version patch.
4. Sync app snapshot from API publish artifact.
5. Update API/App state contract version lines.
6. Commit API/App contract sync changes.

### Task 4: Verification and Review Gate

**Files:**
- No functional changes expected.

**Steps:**
1. Run `dotnet test` in `sf-quality-api`.
2. Run `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` from `sf-quality-api`.
3. Perform formal review pass focused on:
   - envelope shape consistency
   - deny-by-default behavior
   - no ABAC/inheritance drift
4. Push and update handoff with next slice target.
