# Phase 26 — Authorization and Approval Pipeline

**Milestone:** v3.0 Architectural Hardening and Platform Maturation
**Track:** Main dependency chain (gate: Phase 25 complete)
**Requirements:** ARCH-08, ARCH-09, ARCH-10
**Source patterns:** Pattern_Mapping.md #1, #7, #6

---

## Reference Architecture Patterns

### Pattern #1 — Defense-in-Depth Layered Authorization Pipeline
- **Gap:** Parent-child role inheritance is not explicitly modeled as a constrained tree. CRUD matrix semantics are not represented as an auditable role × data × CRUD matrix view.
- **Scope:** Add `dbo.Role.ParentRoleId` with subtractive-inheritance validator; add `security.vw_EffectiveCrudMatrix` diagnostic view.

### Pattern #7 — Self-Approval Prevention (SoD)
- **Gap:** Core SoD guard exists in `workflow.usp_ProcessApprovalStep` but coverage assurance across all approval paths and future entities is not formalized.
- **Scope:** Centralize SoD logic in `workflow.usp_EnforceSeparationOfDuties` shared helper.

### Pattern #6 — Hierarchy-Aware Dynamic Routing for Approval Resolution
- **Gap:** Approval routing is configured statically (`workflow.ApprovalStep.ApproverRoleId`). No runtime resolver for dynamic approver selection.
- **Scope:** Add `workflow.usp_ResolveApprovers` resolver procedure. Extend `GuardExpression` syntax on `workflow.WorkflowTransition` to support field-change detection for routing decisions.

**Hidden Pattern Context — Data Staging Edit Modes:**
The reference platform's data staging pattern reveals that different field groups on the same entity trigger different approval workflows (e.g., severity reclassification → Director chain; containment update → Manager chain). We achieve this via field-change-detection guard conditions on existing `workflow.WorkflowTransition` rows, not a separate field-group framework.

---

## Existing Artifacts

This phase builds on:
- `dbo.Role` with `RoleTier` (migration 005) — role hierarchy table without ParentRoleId
- `security.Feature`, `security.Permission`, `security.RolePermission` (migration 091)
- `security.usp_CheckPermission`, `security.usp_EvaluatePolicy` (migration 096)
- `workflow.ApprovalChain`, `workflow.ApprovalStep.ApproverRoleId` (migration 051) — static routing
- `workflow.usp_ProcessApprovalStep` (migration 099) — existing SoD guard
- `dbo.DispositionAuthorityRule` (migration 101) — existing authority constraint
- `workflow.GuardDefinition` (Phase 25 deliverable — must exist before this phase)

---

## Recommended Approach (Distilled)

### Plan 26-01: Role Hierarchy + CRUD Matrix View

```sql
-- Add ParentRoleId to dbo.Role for subtractive inheritance tree
ALTER TABLE dbo.Role ADD
    ParentRoleId INT NULL REFERENCES dbo.Role(RoleId);

-- Cycle prevention constraint (role cannot be its own parent)
ALTER TABLE dbo.Role ADD CONSTRAINT CHK_Role_NoSelfParent
    CHECK (ParentRoleId IS NULL OR ParentRoleId != RoleId);

-- Create subtractive-inheritance validator stored proc
-- workflow.usp_ValidateRoleInheritance(@RoleId INT)
-- Walks parent chain to detect cycles; raises 50xxx on violation
```

Create `security.vw_EffectiveCrudMatrix`:
```sql
-- Returns role x object x CRUD matrix for governance review
-- Joins dbo.Role (with parent hierarchy), security.RolePermission, security.Permission
-- Include inherited permissions from parent roles (subtractive model: child inherits all, can remove)
SELECT
    r.RoleId,
    r.RoleName,
    r.ParentRoleId,
    p.ObjectName,
    p.CanCreate,
    p.CanRead,
    p.CanUpdate,
    p.CanDelete
FROM dbo.Role r
JOIN security.RolePermission rp ON rp.RoleId = r.RoleId
JOIN security.Permission p ON p.PermissionId = rp.PermissionId;
```

### Plan 26-02: Dynamic Approval Resolver + SoD Centralization

**`workflow.usp_ResolveApprovers`** — dynamic approver resolution proc:
```sql
-- workflow.usp_ResolveApprovers(@TransitionId INT, @EntityId INT, @EntityType NVARCHAR(50))
-- Walks ApprovalChain for the transition
-- For dynamic-routing steps, evaluates guard conditions against entity field changes
-- Returns: table of (UserId, RoleId, ApprovalStepId, IsDynamicRoute BIT)
```

**Field-change-detection guard syntax extension:**
Add `FieldChangeTarget` column to `workflow.WorkflowTransition`:
```sql
ALTER TABLE workflow.WorkflowTransition ADD
    FieldChangeTarget   NVARCHAR(200) NULL,  -- e.g. 'SeverityId:changed' → triggers this transition's routing
    DynamicRouteChainId INT NULL REFERENCES workflow.ApprovalChain(ApprovalChainId);
```

**`workflow.usp_EnforceSeparationOfDuties`** — centralized SoD helper:
```sql
-- workflow.usp_EnforceSeparationOfDuties(@EntityId INT, @EntityType NVARCHAR(50), @ApprovingUserId INT)
-- Raises 50413 if approving user initiated or previously approved same entity in this chain
-- Called from usp_ProcessApprovalStep (replace inline SoD check with this proc call)
```

---

## Cross-Repo Dependencies

| Dependency | Direction | Details |
|-----------|-----------|---------|
| Phase 25 | DB → this phase | `workflow.GuardDefinition` must exist for guard-condition approach |
| This phase → Phase 27 | DB → DB | `usp_ResolveApprovers` output is used by approval lifecycle processing |
| `security.vw_EffectiveCrudMatrix` | DB → API Phase 7 | API feature-gating endpoint will expose this view |

## Entry Criteria

- Phase 25 COMPLETE (guard definitions exist, EightDStep has StepStatus)
- Planner has reviewed this CONTEXT file

## Exit Criteria (Gate for Phase 27)

1. `dbo.Role.ParentRoleId` column exists with cycle-prevention CHECK constraint
2. `security.vw_EffectiveCrudMatrix` is queryable and returns role × data × CRUD rows
3. `workflow.usp_ResolveApprovers` callable and returns approver list for a test transition
4. `workflow.usp_EnforceSeparationOfDuties` callable and integrated into `workflow.usp_ProcessApprovalStep`
5. `Invoke-CycleChecks.ps1` passes

## Reconciliation Addendum (2026-02-22)

- Phase 26 feeds a decision-gated Phase 26.1 branch for ABAC deepening; implement/defer is governed by ADR checklist outcomes.
- If any ABAC trigger is true, Phase 26.1 executes with deny-path verification before downstream consumer phases proceed.
