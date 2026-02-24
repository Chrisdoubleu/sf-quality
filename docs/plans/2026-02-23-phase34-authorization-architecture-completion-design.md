# Phase 34: Authorization Architecture Completion — Design Document

**Date:** 2026-02-23
**Phase:** 34-authorization-architecture-completion
**Repo:** sf-quality-db
**Migrations:** 145-150
**Posture:** Extend + Complete + Converge (not rebuild)

---

## Executive Summary

Phase 34 completes the authorization architecture by adding permission bundle composition, deterministic materialization, admin fast-path, and centralized auth retrofit for remaining inline patterns. It builds on Phase 14's existing foundation (migrations 091-110) which already provides the security catalog, policy engine, and hardened core workflow procedures.

## Locked Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Bundle granularity | 54 atomic domain bundles (1:1 with permissions) | All 15 roles have distinct footprints; atomic = exact parity, zero over-granting |
| App bundle model | 15 role-specific app bundles | Each composes exact atoms; cleanest for future app-driven customization |
| Composition direction | App bundles compose domain bundles only (no direct permission refs) | Locked model: "App bundles compose domain bundles; they do not duplicate permissions" |
| System admin | Policy engine fast-path (`IsAdmin=1` -> RETURN) | RLS already bypasses for admin; this closes the policy engine gap |
| Materialization | Verification-first (prove parity on Allow rows before switching) | 328 Allow rows must match computed set; 381 Deny rows are vestigial |
| NULL PlantId | ANY-scope check (not skip) | User must hold permission in at least one plant; RLS handles row filtering |
| Data lifecycle | Standalone atoms, not in business bundles | Destructive ops segregated from operational personas; admin-only via fast-path |
| Deny semantics | Deny-by-default: absence = deny; existing Deny rows preserved but vestigial | Bundles define Allow surface; materialization produces Allow rows only |

## Security Contracts

### IsAdmin Fast-Path Contract

`IsAdmin` is a **break-glass super-admin flag**, not a plant-scoped admin indicator. It is set exclusively by the trusted session bootstrap (`dbo.usp_SetSessionContext`) based on the authoritative `UserPlantAccess` table, and locked with `@read_only = 1` for the lifetime of the connection. No application code, caller, or stored procedure can set or modify it after bootstrap.

A user with `AccessLevel = 'Admin'` on any plant is treated as a global super-admin with complete RLS bypass and policy engine bypass.

Evidence: `007_session_context_sp.sql` lines 56-62 (derivation), line 69 (`@read_only = 1`), `144_phase27_timeout_operational_hardening_contract.sql` (nested-call hardening).

### Policy Engine Return-Code Contract

- Success/Allow: `RETURN` (implicit 0) from `usp_CheckPermission`; `@ResultCode = 0` from `usp_EvaluatePolicy`
- Deny: `THROW 5041x` with deterministic error code
- Error codes: 50410 (FEATURE_DENIED), 50411 (PERMISSION_DENIED), 50412 (SCOPE_DENIED), 50413 (CONSTRAINT_DENIED), 50414 (APPROVAL_REQUIRED), 50415 (CONFIG_INVALID), 50419 (POLICY_UNAVAILABLE)

### Data Lifecycle Segregation Contract

Data lifecycle permissions (`SYS.DataLifecycle.Archive`, `SYS.DataLifecycle.Import`, `SYS.DataLifecycle.Purge`) are system-level destructive capabilities segregated from all business role bundles. Access is provided exclusively through the `IsAdmin` fast-path or future dedicated lifecycle operator bundles. No business persona (Roles 1-15) receives these permissions through the standard bundle -> materialization chain.

## Canonical Permission Matrix Source

The single source of truth for bundle composition is:
- `092_seed_workflow_permissions_features.sql` Section C (15x47 role-permission matrix)
- `141_phase27_timeout_processor_authorization.sql` Section B (4 timeout permissions for Role 1)

### Reconciled Allow Counts

| RoleId | Role Name | Allow Count |
|---|---|---|
| 1 | Quality Authority - Enterprise | 51 (47 + 4 timeout) |
| 2 | Enterprise Reopen/Cancel | 10 |
| 3 | Engineering Contributor - Enterprise | 27 |
| 4 | Maintenance Contributor - Enterprise | 16 |
| 5 | Operations Lead - Multi-Plant | 40 |
| 6 | Process Engineering Lead - Multi-Plant | 33 |
| 7 | Plant Workflow Manager | 40 |
| 8 | Production Workflow Lead | 17 |
| 9 | Quality Workflow Approver - Plant | 40 |
| 10 | Quality Workflow Coordinator | 19 |
| 11 | Quality Data Steward | 5 |
| 12 | Maintenance Workflow Lead | 13 |
| 13 | Floor Supervisor | 5 |
| 14 | Floor Reporter | 1 |
| 15 | Process Engineering Contributor | 11 |
| **Total** | | **328 Allow / 709 total rows** |

Migration seeding in Slice 3 must generate app bundle composition from this matrix, not from hand-counted values.

## What Already Exists (Phase 14, migrations 091-110)

- `security.Feature` + 10 features
- `security.Permission` + 47 permissions (+ 4 timeout from 141)
- `security.RolePermission` + 709 rows (328 Allow, 381 Deny)
- `security.RoleFeature` derived grants
- `security.RolePermissionConstraint` + SoD constraints
- `security.SoDException`
- `security.usp_CheckPermission` (Layers 1-3)
- `security.usp_EvaluatePolicy` (Layers 1-4 + fail-safe)
- `security.usp_ValidateSecurityConfig`
- Hardened `usp_TransitionState` (098), `usp_ProcessApprovalStep` (099), `usp_GetPendingApprovals` (099), `usp_RecordStatusOverride` (102)
- `usp_GetAvailableTransitions` (100, dual-path, plant-scoped)
- `workflow.NcrSeverityThreshold`, `quality.DispositionAuthorityRule`

## What Phase 34 Builds (gaps)

- Bundle composition tables (PermissionBundle, PermissionBundleItem, RoleBundle)
- 54 atomic domain bundles + 15 app bundles + 15 RoleBundle entries
- 3 new data lifecycle permissions (standalone, not in business bundles)
- Materialization SP with cycle detection and parity verification
- Admin fast-path in policy engine (Layer 0)
- ANY-scope check for NULL PlantId in policy engine
- Centralized auth retrofit: 8 Phase 27 timeout procedures + 3 data lifecycle procedures
- E2E verification gate

## Slice Plan

### Slice 1 -- Migration 145: Bundle DDL + Policy Engine Hardening

**Creates 3 tables:**
- `security.PermissionBundle` (BundleId PK, BundleCode UQ, BundleName, BundleType CHECK('Domain','App'), Description, IsActive)
- `security.PermissionBundleItem` (BundleItemId PK, BundleId FK, PermissionId FK NULL, ChildBundleId FK NULL, CHECK XOR, filtered UQs)
- `security.RoleBundle` (RoleBundleId PK, RoleId FK, BundleId FK, IsActive, UQ(RoleId,BundleId))

**Audit triggers:** 3 (via `usp_CreateAuditTrigger`)

**ALTER `security.usp_CheckPermission`:**
- Layer 0: Admin fast-path (`IF CAST(SESSION_CONTEXT(N'IsAdmin') AS BIT) = 1 RETURN`)
- Layer 3: NULL PlantId -> ANY-scope check (verify user holds permission in at least one plant via RolePermission+UserRole join; THROW 50411 if no grant in any scope)

**ALTER `security.usp_EvaluatePolicy`:**
- Layer 0: Admin fast-path (`IF @IsAdmin = 1 SET @ResultCode = 0; RETURN`)

**Verification:**
```
pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly
-- 3 tables exist, 3 audit triggers, both SPs recompile
-- Admin fast-path returns without hitting Layer 2+
-- NULL PlantId with valid grant passes; without any grant throws 50411
```

### Slice 2 -- Migration 146: Atomic Domain Bundle Seeding + New Permissions

**New permissions (3 rows, MERGE):** SYS.DataLifecycle.Archive, SYS.DataLifecycle.Import, SYS.DataLifecycle.Purge

**Atomic domain bundles (54 rows, MERGE on BundleCode):** One Domain bundle per permission (DOM.WF.NCR.SUBMIT through DOM.SYS.PURGE). Each gets exactly 1 PermissionBundleItem linking to its permission.

**Integrity check (fail-fast):** Every active permission maps to exactly one domain bundle. THROW 51462 if orphaned or duplicated.

**Verification:**
```
pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly
-- 54 domain bundles, 54 PermissionBundleItem rows, 0 orphans
```

### Slice 3 -- Migration 147: App Bundle Seeding + Role-Bundle Wiring

**App bundles (15 rows, MERGE on BundleCode):** One App bundle per role. Each composes the exact atomic domain bundles matching the role's Allow grants from 092+141.

**PermissionBundleItem rows for app bundles (~328 ChildBundleId references):** Generated from canonical matrix source.

**RoleBundle rows (15 rows, MERGE on RoleId+BundleId):** One entry per role.

**Note:** Data lifecycle atoms (DOM.SYS.ARCHIVE/IMPORT/PURGE) are NOT included in any app bundle. "App bundle" means "consumable bundle shape for a persona."

**Verification:**
```
pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly
-- 15 app bundles, 15 RoleBundle entries, correct atom counts per role
```

### Slice 4 -- Migration 148: Materialization SP + Parity Gate

**Creates `security.usp_MaterializeBundlePermissions`:**
- Parameters: @DryRun BIT = 0, @RoleId INT = NULL
- Output: @MatchCount, @NewCount, @OrphanCount
- Recursive CTE: Role -> RoleBundle -> App Bundle -> PermissionBundleItem.ChildBundleId -> Domain Bundle -> PermissionBundleItem.PermissionId -> Permission
- **Cycle detection** inside the CTE (MAXRECURSION + visited-set check)
- Produces Allow grants only (deny-by-default)
- @DryRun=1: compare to current Allow rows in RolePermission; report match/new/orphan
- @DryRun=0: MERGE Allow grants; mark orphaned Allow rows IsActive=0; regenerate RoleFeature

**Migration gate:** `EXEC usp_MaterializeBundlePermissions @DryRun = 1` -> assert 328 match, 0 new, 0 orphan

**Existing Deny rows:** Preserved (not touched by materialization). Vestigial but harmless.

**Verification:**
```
pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly
-- SP compiles, parity passes, RolePermission unchanged
```

### Slice 5 -- Migration 149: Centralized Auth Retrofit

**Phase 27 timeout procedures (8 ALTERs):** Replace inline 3-table JOIN auth with `EXEC security.usp_CheckPermission`. Each retrofitted procedure includes a comment proving RLS coverage on underlying query.

| Procedure | Permission Code | PlantId |
|---|---|---|
| usp_EnqueueApprovalTimeouts | WF.Approvals.Timeout.Enqueue | Entity PlantId |
| usp_GetApprovalTimeoutQueue | WF.Approvals.Timeout.Queue.Read | NULL (ANY-scope) |
| usp_GetApprovalTimeoutDeadLetterQueue | WF.Approvals.Timeout.Queue.Read | NULL (ANY-scope) |
| usp_GetApprovalTimeoutAckPendingQueue | WF.Approvals.Timeout.Acknowledge | NULL (ANY-scope) |
| usp_GetApprovalTimeoutOperationalAlerts | WF.Approvals.Timeout.Queue.Read | NULL (ANY-scope) |
| usp_ApplyApprovalTimeoutQueueItem | WF.Approvals.Timeout.Apply | ResolvedPlantId or NULL |
| usp_AcknowledgeApprovalTimeoutQueueItem | WF.Approvals.Timeout.Acknowledge | ResolvedPlantId or NULL |
| usp_RedriveApprovalTimeoutDeadLetterQueueItem | WF.Approvals.Timeout.Apply | ResolvedPlantId or NULL |

**Data lifecycle procedures (3 ALTERs):** Add `EXEC security.usp_CheckPermission` after session context.

| Procedure | Permission Code | PlantId |
|---|---|---|
| quality.usp_ArchiveClosedNcrBatch | SYS.DataLifecycle.Archive | NULL (cross-plant) |
| quality.usp_BulkImportNcrStaging | SYS.DataLifecycle.Import | NULL (cross-plant) |
| quality.usp_PurgeArchivedNcr | SYS.DataLifecycle.Purge | NULL (cross-plant) |

**Verification:**
```
pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly
-- All 11 procedures recompile
-- No remaining inline 3-table JOIN auth patterns
-- Admin fast-path still works for all procedures
```

### Slice 6 -- Migration 150: E2E Verification + Readiness Gate

**10 verification checks (THROW on failure):**
1. Bundle table integrity: 54 domain + 15 app + 15 RoleBundle
2. Domain atom 1:1: every domain bundle has exactly 1 PermissionBundleItem with PermissionId
3. App composition purity: all app bundle items use ChildBundleId only
4. No circular refs in bundle graph
5. Permission coverage: all 54 active permissions in exactly 1 domain bundle
6. Role coverage: all 15 active roles have exactly 1 RoleBundle
7. Materialization parity: @DryRun=1 -> 328 match, 0 new, 0 orphan
8. SP recompile chain: sp_refreshsqlmodule on all altered SPs
9. ValidateSecurityConfig passes
10. Admin fast-path: usp_CheckPermission returns immediately for IsAdmin=1

**Additional checks:**
- IsAdmin set @read_only=1 in session bootstrap (documentation assertion)
- Every Get*Queue procedure reads from RLS-protected tables (RLS coverage proof)

**Known gap register (PRINT, non-blocking):**
- quality.usp_UpsertScarPartyLifecycle (136) -- no auth
- quality.usp_ValidateOnlyNcrWrite (137) -- no auth
- workflow.usp_RecordStatusChange (132) -- no auth
- quality.usp_GetWorkflowReferenceData (137) -- read-only, no auth

**Registration:**
```
Phase 34 (Authorization Architecture Completion) COMPLETE
  Migrations: 145-150 (6 total)
  Tables: 3 new
  Domain bundles: 54 atomic
  App bundles: 15 role-specific
  Permissions: 3 new (data lifecycle, standalone)
  Procedures hardened: 13 (2 policy engine + 8 timeout + 3 lifecycle)
  RolePermission: 709 rows (328 Allow, 381 Deny vestigial)
  Phase 35 starts at migration 151
```

## Non-Negotiable Constraints (preserved from 34-CONTEXT.md)

1. Do not touch RLS predicates
2. Do not implement ABAC deepening
3. Do not change API or App repos
4. Do not break existing behavior; additive migrations only
5. Preserve producer-first DB -> API -> App chain
6. Preserve explicit-grant deny-by-default
7. Super-admin fast-path for IsAdmin=1
8. Domain + App bundle composition exactly as locked
9. Run `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` after each slice

## Future Work (Not Phase 34)

- App-driven bundle customization UI (API/App phases)
- Dedicated APP.DATA-LIFECYCLE-OPERATOR bundle for non-admin service accounts
- Remove vestigial Deny rows from RolePermission when bundle model stable
- Auth hardening for remaining 4 no-auth procedures (132, 136, 137)
- Legacy role fallback sunset (dead code if all transitions have RequiredPermissionId)
