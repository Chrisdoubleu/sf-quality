# DB Requirements Additions — v3.0 Architectural Hardening

**Apply to:** `sf-quality-db/.planning/REQUIREMENTS.md`
**When:** Append this block before running `/gsd:new-milestone` for v3.0
**Source:** Reference Architecture Pattern_Mapping.md, Execution_Plan.md

---

## Instructions

Append the following block to the end of `REQUIREMENTS.md`, after the existing v2.0 requirements and before the "Out of Scope" section. Update the traceability table at the bottom of REQUIREMENTS.md to include all ARCH-xx entries.

---

## v3.0 Architectural Hardening and Platform Maturation Requirements

**Core value:** Harden the existing SQL-first quality system to production-grade architecture — adding the authorization depth, workflow precision, audit durability, and data lifecycle controls that a reference enterprise quality platform requires.

### Workflow and Orchestration (ARCH-WORKFLOW)

- **ARCH-01:** Typed Workflow Step State Machine — Enhance `rca.EightDStep` with a per-step state enum (NotStarted/InProgress/Complete/Skipped/Blocked) replacing the `IsComplete` BIT flag, plus `IsSkippable`, `SkippedReason`, `SkippedByUserId`, and `PrerequisiteStepNumber` columns. Add `rca.vw_EightDCompletionStatus` for dashboard reporting and SLA evaluation.
  - *Implements:* Pattern #2 (Workflow Orchestration Engine), Pattern #11 (Guided Process Orchestration)
  - *Phase:* 25

- **ARCH-02:** Reusable Guard Definitions — Create `workflow.GuardDefinition` table decoupling guard logic from individual transition rows, and add notification metadata columns to `workflow.WorkflowTransition`.
  - *Implements:* Pattern #2 (Workflow Orchestration Engine)
  - *Phase:* 25

- **ARCH-03:** Versioned Workflow Process Metadata — Create `workflow.WorkflowProcessVersion` with activation window and immutable-after-activation flag to support workflow version pinning.
  - *Implements:* Pattern #11 (Workflow Immutability)
  - *Phase:* 25

- **ARCH-04:** Approval Timeout Auto-Resolution — Add `ExpiresAtUtc`/`TimeoutActionApplied` to `workflow.PendingApprovalTransition` and create `workflow.usp_ProcessPendingApprovalTimeouts` scheduled processor.
  - *Implements:* Pattern #3 (Approval Timeout and Auto-Resolution)
  - *Phase:* 27

- **ARCH-05:** Optimistic Commit Mode (Presave) — Add `IsPresave BIT DEFAULT 0` to `workflow.WorkflowTransition` and presave path to `workflow.usp_TransitionState` (immediate entity commit + parallel approval, with compensating reversal on rejection).
  - *Implements:* Pattern #20 (Optimistic Commit Mode for Safety-Critical Transitions)
  - *Phase:* 27

- **ARCH-06:** Event-Driven Workflow Chaining — Generalize outbox to CAPA/SCAR/Complaint/Audit entities. Add `workflow.EventSubscription` for internal event metadata and automatic workflow chaining.
  - *Implements:* Pattern #8 (Event-Driven Workflow Chaining + Outbox Generalization)
  - *Phase:* 28

- **ARCH-07:** Internal Notification Queue — Add `workflow.NotificationQueue` for internal user notifications and notification write hooks in transition/approval procedures.
  - *Implements:* Pattern #13 (Notification Queue)
  - *Phase:* 28

### Authorization and Security (ARCH-SECURITY)

- **ARCH-08:** Role Hierarchy and Subtractive Inheritance — Add `dbo.Role.ParentRoleId` + subtractive-inheritance validator. Add `security.vw_EffectiveCrudMatrix` diagnostic view for role x data x CRUD governance review.
  - *Implements:* Pattern #1 (Defense-in-Depth Layered Authorization Pipeline)
  - *Phase:* 26

- **ARCH-09:** Dynamic Approval Routing — Create `workflow.usp_ResolveApprovers` resolver procedure and extend `GuardExpression` syntax on `workflow.WorkflowTransition` to support field-change detection (severity reclassification → Director chain, default → Manager chain).
  - *Implements:* Pattern #6 (Hierarchy-Aware Dynamic Routing), Pattern #7 (Self-Approval Prevention)
  - *Phase:* 26

- **ARCH-10:** Centralized SoD Enforcement — Centralize separation-of-duties checks in `workflow.usp_EnforceSeparationOfDuties` helper; extend SoD coverage across all approval-gated transitions.
  - *Implements:* Pattern #7 (Self-Approval Prevention)
  - *Phase:* 26

### SLA and Policy (ARCH-SLA)

- **ARCH-11:** SLA Configuration and Enforcement — Seed `workflow.SlaConfiguration` with CAPA SLA thresholds (30/60/90-day by severity). Wire `workflow.usp_EvaluateEscalationRules` for CAPA entities. Add `quality.vw_CapaTimelineCompliance` dashboard view.
  - *Implements:* Pattern #12 (SLA / CAPA Timeline Compliance)
  - *Phase:* 30

- **ARCH-12:** Policy Resolution Engine — Add `security.vw_EffectivePolicyMap` diagnostic view for policy scope resolution (candidate → filter by scope → resolve conflicts by priority → return effective policy).
  - *Implements:* Pattern #17 (Policy Resolution Engine)
  - *Phase:* 30

- **ARCH-13:** Background Job Idempotency — Add `dbo.BackgroundJobRun` table (start/end/status/error/idempotency key) and idempotency keys on batch procedures to support safe retry of timeout processor and other jobs.
  - *Implements:* Pattern #17 (Job Processing / Background Queue)
  - *Phase:* 30

### Audit and Temporal Query (ARCH-AUDIT)

- **ARCH-14:** API Call Log — Create `audit.ApiCallLog` table (`ApiCallLogId`, `CorrelationId`, `Route`, `HttpMethod`, `CallerOid`, `HttpStatus`, `DurationMs`, `RequestTimestampUtc`) linked to entity audit trail by correlation ID.
  - *Implements:* Pattern #5 (Universal Change Audit with Anomaly Detection)
  - *Phase:* 29 ← **Execute first — API Phase 3.5 prerequisite**

- **ARCH-15:** Point-in-Time Read Procedures — Add optional `@AsOfUtc DATETIME2 = NULL` to key read procedures, routed through `FOR SYSTEM_TIME AS OF` for deterministic historical views.
  - *Implements:* Pattern #4 (Temporal Data Model and Point-in-Time Querying)
  - *Phase:* 29

- **ARCH-16:** Shared Hierarchy Traversal Helpers — Create `dbo.usp_GetTreeAncestors` and `dbo.usp_GetTreeDescendants` as reusable recursive helpers for plant/org/defect hierarchies, plus cycle-detection checks on all parent-child structures.
  - *Implements:* Pattern #22 (Tree Helpers and Hierarchy Navigation)
  - *Phase:* 29

### Multi-Party and Identity (ARCH-MULTIPARTY)

- **ARCH-17:** SCAR Party Status Tracking — Add `CustomerResponseStatus` / `SupplierResponseStatus` columns to `quality.SupplierCar`, create `quality.ScarPartyStatusHistory` table and `quality.vw_ScarPartyStatus` dashboard view.
  - *Implements:* Pattern #19 (Multi-Party Entity Lifecycle Tracking)
  - *Phase:* 31

- **ARCH-18:** External Document Identifier Indexes — Add unique indexes and key-lookup support on `quality.NcrExternalReference` and equivalent tables for fast external-key joins.
  - *Implements:* Pattern #9 (Dual-Key Identity Pattern)
  - *Phase:* 31

### Data Access and Reference (ARCH-DATA)

- **ARCH-19:** Validate-Only Write Mode — Add `@IsValidateOnly BIT = 0` to 6+ write procedures. On `@IsValidateOnly=1`, execute all validation → rollback → return validation resultset. Enables form preflight without side effects.
  - *Implements:* Pattern #14 (Validate-Only / Dry-Run Mode)
  - *Phase:* 32 ← **API Phase 7 prerequisite**

- **ARCH-20:** Canonical Lookup Views — Add canonical lookup views/procs per domain (DefectType, Severity, Disposition, ProcessFamily, etc.) as the authoritative codebook surface for consumers.
  - *Implements:* Pattern #10 (Codebook Views and Reference Data Contract)
  - *Phase:* 32

- **ARCH-21:** Configuration Portability — Create `security.usp_ExportConfiguration` / `usp_ImportConfiguration` with upsert semantics for portable configuration state across environments.
  - *Implements:* Pattern #15 (Config Portability)
  - *Phase:* 32

### Data Lifecycle (ARCH-LIFECYCLE)

- **ARCH-22:** Archive and Purge — Create `dbo.usp_ArchiveClosedRecords` evaluating `dbo.RecordRetentionPolicy`, `audit.usp_PurgeAuditBeyondRetention`, and `dbo.ArchivePurgeLog` tracking table.
  - *Implements:* Pattern #16 (Retention and Purging)
  - *Phase:* 33

- **ARCH-23:** Bulk Import Procedures — Create `dbo.usp_BulkImportLookupValues`, `dbo.usp_BulkImportDefectTypes`, `dbo.usp_BulkImportKnowledgeEntries` for bootstrapping and migration workflows.
  - *Implements:* Pattern #24 (Bulk Import)
  - *Phase:* 33

### Deferred

- **ARCH-DEFERRED-01:** Organizational Scoping (Pattern #21) — Deferred; no concrete gap beyond current plant-level RLS model in single-tenant scope.
- **ARCH-DEFERRED-02:** Document Storage Contract (Pattern #23) — Blocked pending storage decision (SharePoint vs. Azure Blob). Execute as `/gsd:quick` when decision is confirmed.
- **ARCH-DEFERRED-03:** Composite Aggregate Expansion (Pattern #18) — No hard dependency; execute as `/gsd:quick "Add expand parameters to composite detail procs"` before or alongside Phase 29.

---

## Updated Traceability Table (v3.0 additions)

| Req ID | Phase | Status |
|--------|-------|--------|
| ARCH-01 | 25 | Pending |
| ARCH-02 | 25 | Pending |
| ARCH-03 | 25 | Pending |
| ARCH-04 | 27 | Pending |
| ARCH-05 | 27 | Pending |
| ARCH-06 | 28 | Pending |
| ARCH-07 | 28 | Pending |
| ARCH-08 | 26 | Pending |
| ARCH-09 | 26 | Pending |
| ARCH-10 | 26 | Pending |
| ARCH-11 | 30 | Pending |
| ARCH-12 | 30 | Pending |
| ARCH-13 | 30 | Pending |
| ARCH-14 | 29 | Pending |
| ARCH-15 | 29 | Pending |
| ARCH-16 | 29 | Pending |
| ARCH-17 | 31 | Pending |
| ARCH-18 | 31 | Pending |
| ARCH-19 | 32 | Pending |
| ARCH-20 | 32 | Pending |
| ARCH-21 | 32 | Pending |
| ARCH-22 | 33 | Pending |
| ARCH-23 | 33 | Pending |
