# DB ROADMAP — v3.0 Milestone Section

**Apply to:** `sf-quality-db/.planning/ROADMAP.md`
**When:** Append after the v2.0 milestone section, once v2.0 is archived
**Source:** Reference Architecture Execution_Plan.md Section B1 + E

---

## Instructions

Append the following block at the end of `ROADMAP.md`, replacing the existing v2.0 milestone as the active milestone.

---

## v3.0 — Architectural Hardening and Platform Maturation

**Goal:** Harden the existing v2.0 quality intelligence platform to production-grade architecture. This milestone closes the gap between our current SQL-first implementation and a reference enterprise quality platform across five domains: workflow precision, authorization depth, audit durability, data lifecycle controls, and multi-party entity tracking.

**Migration range:** 131+
**Requirement areas:** ARCH-01..23 (23 requirements across 9 phases)
**Source authority:** `sf-quality/Reference_Architecture/Execution_Plan.md` — all phase definitions traceable to 46-pattern audit in Pattern_Mapping.md

**Dependency note:** DB Phase 29 must execute FIRST — it creates `audit.ApiCallLog` which API Phase 3.5 depends on.

---

### Phase 25 — Workflow Engine Foundation Hardening

**Goal:** Strengthen workflow orchestration foundations — step state machine, reusable guard definitions, workflow versioning.

**Requirements:** ARCH-01, ARCH-02, ARCH-03

**Success criteria:**
1. `workflow.GuardDefinition` table exists and is queryable with seeded guard definitions
2. `rca.EightDStep` has `StepStatus` column (replacing `IsComplete BIT`) with non-zero default behavior
3. `rca.vw_EightDCompletionStatus` returns non-null aggregated results for any EightDReport
4. `workflow.WorkflowProcessVersion` table exists with activation window columns

**Plans:** 2–3
**Dependencies:** None (foundation for Phases 26-28)
**Status:** Not started

---

### Phase 26 — Authorization and Approval Pipeline

**Goal:** Add role hierarchy, dynamic approval routing, and SoD centralization.

**Requirements:** ARCH-08, ARCH-09, ARCH-10

**Success criteria:**
1. `dbo.Role.ParentRoleId` column exists with subtractive-inheritance validator callable
2. `security.vw_EffectiveCrudMatrix` returns role × data × CRUD results
3. `workflow.usp_ResolveApprovers` resolves dynamic approvers for a test transition
4. `workflow.usp_EnforceSeparationOfDuties` callable and integrated into approval processing

**Plans:** 2–3
**Dependencies:** Phase 25 (guard definitions must exist)
**Status:** Not started

---

### Phase 27 — Approval Lifecycle and Timeout Processing

**Goal:** Add approval expiry processing and optimistic commit (presave) mode.

**Requirements:** ARCH-04, ARCH-05

**Success criteria:**
1. `workflow.usp_ProcessPendingApprovalTimeouts` processes expired approvals and applies chain timeout policy
2. Presave transitions (`IsPresave=1`) commit entity state immediately and create pending approval
3. Rejected presave creates compensating transition reverting entity state
4. `ExpiresAtUtc`/`TimeoutActionApplied` columns present on `workflow.PendingApprovalTransition`

**Plans:** 2–3
**Dependencies:** Phase 25, Phase 26
**Status:** Not started

---

### Phase 28 — Event-Driven Chaining and Notifications

**Goal:** Generalize outbox to all entities and add internal notification queue.

**Requirements:** ARCH-06, ARCH-07

**Success criteria:**
1. Outbox pattern covers CAPA, SCAR, Complaint, and Audit entities (not just NCR)
2. `workflow.EventSubscription` table exists with seeded subscriptions
3. `workflow.NotificationQueue` table exists and receives writes from approval/transition procedures

**Plans:** 2
**Dependencies:** Phase 25, Phase 27
**Status:** Not started

---

### Phase 29 — Audit Infrastructure and Temporal Query ⭐ Execute First

**Goal:** Add API call log, point-in-time query support, and shared hierarchy helpers.

**Requirements:** ARCH-14, ARCH-15, ARCH-16

**Success criteria:**
1. `audit.ApiCallLog` exists with all specified columns (`CorrelationId`, `Route`, `HttpMethod`, `CallerOid`, `HttpStatus`, `DurationMs`, `RequestTimestampUtc`)
2. At least one read proc accepts `@AsOfUtc DATETIME2 = NULL` and returns temporal results
3. `dbo.usp_GetTreeAncestors` / `dbo.usp_GetTreeDescendants` callable on existing hierarchies

**Plans:** 2
**Dependencies:** None — independent track; **MUST complete before API Phase 3.5**
**Status:** Not started

---

### Phase 30 — SLA Enforcement and Background Jobs

**Goal:** Wire SLA configuration and enforcement, add policy resolution view, add job idempotency.

**Requirements:** ARCH-11, ARCH-12, ARCH-13

**Success criteria:**
1. `workflow.SlaConfiguration` seeded with CAPA thresholds (30/60/90-day by severity)
2. `workflow.usp_EvaluateEscalationRules` wired and callable for CAPA entities
3. `quality.vw_CapaTimelineCompliance` returns compliance results
4. `security.vw_EffectivePolicyMap` returns policy resolution results
5. `dbo.BackgroundJobRun` table exists

**Plans:** 2–3
**Dependencies:** Phase 27 (timeout processor is a background job)
**Status:** Not started

---

### Phase 31 — Multi-Party Entity Lifecycle

**Goal:** Add SCAR party status tracking and external document identifier support.

**Requirements:** ARCH-17, ARCH-18

**Success criteria:**
1. `quality.SupplierCar` has `CustomerResponseStatus` and `SupplierResponseStatus` columns
2. `quality.ScarPartyStatusHistory` table exists
3. `quality.vw_ScarPartyStatus` returns party status dashboard data
4. Unique indexes exist on `quality.NcrExternalReference` for fast external-key lookups

**Plans:** 2
**Dependencies:** None — independent track; **refresh manifest after completion (gates API Phase 5)**
**Status:** Not started

---

### Phase 32 — Validate-Only and Reference Data

**Goal:** Add validate-only mode to write procs, canonical lookup views, and config portability.

**Requirements:** ARCH-19, ARCH-20, ARCH-21

**Success criteria:**
1. At least 6 write procs accept `@IsValidateOnly BIT = 0` and return validation resultsets on rollback
2. Canonical lookup views exist per domain (DefectType, Severity, Disposition, ProcessFamily)
3. `security.usp_ExportConfiguration` produces a portable JSON-compatible resultset
4. `security.usp_ImportConfiguration` with upsert semantics callable

**Plans:** 2–3
**Dependencies:** Phase 25 (stable workflow foundation for transition proc validate-only); **refresh manifest after completion (gates API Phase 7)**
**Status:** Not started

---

### Phase 33 — Data Lifecycle and Bulk Operations

**Goal:** Add archive/purge lifecycle and bulk import procedures.

**Requirements:** ARCH-22, ARCH-23

**Success criteria:**
1. `dbo.usp_ArchiveClosedRecords` evaluating `dbo.RecordRetentionPolicy` callable
2. `audit.usp_PurgeAuditBeyondRetention` callable
3. `dbo.ArchivePurgeLog` table exists
4. `dbo.usp_BulkImportLookupValues`, `dbo.usp_BulkImportDefectTypes`, `dbo.usp_BulkImportKnowledgeEntries` callable

**Plans:** 2
**Dependencies:** None — independent track
**Status:** Not started

---

### Quick Items (v3.0)

| Item | Pattern | Prerequisite | Status |
|------|---------|-------------|--------|
| Composite Aggregate Expansion | #18 | None — execute before/alongside Phase 29 so API Phase 4 can use `expand` param | Not started |
| Document Storage Contract | #23 | Storage decision must be confirmed first (SharePoint vs. Azure Blob) | Blocked |

---

### v3.0 Progress Tracking

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 25 | Workflow Engine Foundation Hardening | 2–3 | Not started | — |
| 26 | Authorization and Approval Pipeline | 2–3 | Not started | — |
| 27 | Approval Lifecycle and Timeout Processing | 2–3 | Not started | — |
| 28 | Event-Driven Chaining and Notifications | 2 | Not started | — |
| 29 | Audit Infrastructure and Temporal Query | 2 | Not started | — |
| 30 | SLA Enforcement and Background Jobs | 2–3 | Not started | — |
| 31 | Multi-Party Entity Lifecycle | 2 | Not started | — |
| 32 | Validate-Only and Reference Data | 2–3 | Not started | — |
| 33 | Data Lifecycle and Bulk Operations | 2 | Not started | — |
| Quick | Composite Aggregate Expansion | 1 | Not started | — |
| Quick | Document Storage Contract | 1 | Blocked | — |

---

### v3.0 Dependency Graph

```
Phase 25 (Workflow Foundation)
  ├→ Phase 26 (Auth/Approval) → Phase 27 (Timeout/Presave)
  │                                ├→ Phase 28 (Events/Notifications)
  │                                └→ Phase 30 (SLA/Jobs)
  └→ Phase 32 (Validate-Only) [loose dependency]

Phase 29 (Audit/Temporal) ── INDEPENDENT ── Execute FIRST
Phase 31 (Multi-Party/SCAR) ── INDEPENDENT
Phase 33 (Lifecycle/Bulk) ── INDEPENDENT
```

### Execution Notes

- Use `/gsd:discuss-phase` before `/gsd:plan-phase` for Phases 25, 26, 27, 28, 29, 30, 32 (complex, multi-pattern)
- Phases 31 and 33 are straightforward enough to skip discuss
- Run `Invoke-CycleChecks.ps1` after each wave
- Refresh `db-contract-manifest.json` incrementally: after Phase 29, after Phase 28 (covering 25-28), after Phase 31, after Phase 32
- Cross-repo amendment protocol: if API phase finds missing DB schema → pause, switch to DB context, run `/gsd:quick` hotfix migration, refresh manifest, resume API phase
