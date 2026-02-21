# Execution Plan: 46 Reference Architecture Patterns → GSD Workflow

**Date:** 2026-02-21
**Scope:** Translate all 46 patterns from [Pattern_Mapping.md](Pattern_Mapping.md) into actionable GSD phases across sf-quality-db, sf-quality-api, and sf-quality-app.

### Related Documents

All documents referenced by this plan live within the `Reference_Architecture/` folder:

| Document | Path (relative to this file) | Purpose |
|----------|------------------------------|---------|
| Pattern Mapping | [Pattern_Mapping.md](Pattern_Mapping.md) | 46-pattern gap audit — source of all pattern numbers |
| Platform Technical Patterns | [Specs/Platform_System_Architecture_Technical_Patterns.json](Specs/Platform_System_Architecture_Technical_Patterns.json) | Synthesized engineering patterns |
| Security Architecture | [Specs/Security_Role_Architecture_Agnostic.json](Specs/Security_Role_Architecture_Agnostic.json) | 10-layer security spec |
| Workflow Architecture | [Specs/Workflow_Engine_Architecture_Agnostic.json](Specs/Workflow_Engine_Architecture_Agnostic.json) | DAG-based orchestration spec |
| API Architecture | [Specs/API_Integration_Architecture_Agnostic.json](Specs/API_Integration_Architecture_Agnostic.json) | REST API integration spec |
| Architectural Briefing | [Briefings/architectural_briefing.md](Briefings/architectural_briefing.md) | Narrative overview |
| Agent Orientation | [Briefings/Agent_Orientation_Revised.md](Briefings/Agent_Orientation_Revised.md) | Stack maturity, constraints, per-repo guidance |
| Hidden Patterns | [Hidden_Patterns/Hidden_Architecture_Patterns_Reverse_Engineered.json](Hidden_Patterns/Hidden_Architecture_Patterns_Reverse_Engineered.json) | 3 reverse-engineered implicit patterns |

Child repo planning artifacts (referenced but not modified from workspace root):

| Repo | Planning Root | Key Files |
|------|--------------|-----------|
| sf-quality-db | `../sf-quality-db/.planning/` | STATE.md, ROADMAP.md, REQUIREMENTS.md, PROJECT.md, MILESTONES.md |
| sf-quality-api | `../sf-quality-api/.planning/` | STATE.md, ROADMAP.md, REQUIREMENTS.md, PROJECT.md |
| sf-quality-app | `../sf-quality-app/.planning/` | STATE.md, ROADMAP.md, REQUIREMENTS.md, PROJECT.md |

---

## A. Context

The [Pattern Mapping](Pattern_Mapping.md) identifies 46 patterns (24 DB, 12 API, 9 App, 1 Cross-Repo) derived from four JSON specs ([Platform](Specs/Platform_System_Architecture_Technical_Patterns.json), [Security](Specs/Security_Role_Architecture_Agnostic.json), [Workflow](Specs/Workflow_Engine_Architecture_Agnostic.json), [API](Specs/API_Integration_Architecture_Agnostic.json)), an [architectural briefing](Briefings/architectural_briefing.md), and three [reverse-engineered hidden architecture patterns](Hidden_Patterns/Hidden_Architecture_Patterns_Reverse_Engineered.json). These patterns represent gaps between our current implementation and the reference platform's production-grade architecture. This plan translates those patterns into GSD-executable work organized by repo, milestone, phase, and dependency order.

**Key constraints:**

- Workspace root (sf-quality/) is coordination-only — no implementation files here
- Each repo is an independent GSD project — work planned and executed within repo context
- GSD phases should be completable in a single focused session (~2-5 migrations)
- DB must land before API; API must land before App (contract chain)
- GSD agents are context-window-bound — they need distilled information in phase context files

---

## B. Grouping Strategy — 46 Patterns into Phases

### B1. sf-quality-db — New v3.0 Milestone (Phases 25-33)

**Decision:** Create new v3.0 milestone "Architectural Hardening and Platform Maturation"

**Rationale:** v2.0 ("Quality Intelligence Platform") has 2 active remaining phases (23-24) with tightly scoped requirements (governance, incoming substrate). Phase 22 (analytics + security grants) is DEFERRED — schema still evolving, no consumers, role architecture not locked. SEC-01 grants ship inline with future migrations as needed. The 24 DB patterns represent a different initiative — making what exists production-grade. Absorbing them into v2.0 would dilute its narrative and bloat requirements from 37 to 60+. v3.0 begins after v2.0 ships.

**Note:** Pattern #5 (audit.vw_SuspiciousActivity) was previously considered for optional absorption into Phase 22 (analytics). With Phase 22 deferred, Pattern #5 stays in v3.0 Phase 29 (Audit Infrastructure) where it naturally groups with ApiCallLog, temporal queries, and tree helpers — all audit schema work with no analytics schema dependency.

| Phase | Name | Patterns | Type | Size |
|-------|------|----------|------|------|
| 25 | Workflow Engine Foundation Hardening | #2 Workflow Orchestration, #11 Workflow Immutability | Strengthen | Large |
| 26 | Authorization and Approval Pipeline | #1 Authorization Pipeline, #7 Self-Approval Prevention, #6 Dynamic Routing | Strengthen+New | Large |
| 27 | Approval Lifecycle and Timeout Processing | #3 Approval Timeout, #20 Optimistic Commit Mode | Strengthen+New | Large |
| 28 | Event-Driven Chaining and Notifications | #8 Outbox Generalization, #13 Notification Queue | Strengthen+New | Medium |
| 29 | Audit Infrastructure and Temporal Query | #5 Audit/Anomaly (ApiCallLog), #4 Temporal @AsOfUtc, #22 Tree Helpers | Strengthen | Medium |
| 30 | SLA Enforcement and Background Jobs | #12 SLA/CAPA Timelines, #17 Job Processing | Strengthen | Medium |
| 31 | Multi-Party Entity Lifecycle | #19 SCAR Party Status, #9 Dual-Key Identity | New+Strengthen | Medium |
| 32 | Validate-Only and Reference Data | #14 Validate-Only Mode, #10 Codebook Views, #15 Config Portability | New+Strengthen | Large |
| 33 | Data Lifecycle and Bulk Operations | #16 Retention/Purging, #24 Bulk Import | Strengthen+New | Medium |
| Quick | Document Storage Contract | #23 | Strengthen | Small |
| Quick | Composite Aggregate Expansion | #18 | Strengthen | Small |
| DEFER | Organizational Scoping | #21 (no concrete gap) | — | — |

#### Phase 25: Workflow Engine Foundation Hardening

**Patterns:** #2, #11

**Deliverables:**
- Enhance `rca.EightDStep`: step-state enum (NotStarted/InProgress/Complete/Skipped/Blocked), IsSkippable, SkippedReason/SkippedByUserId, PrerequisiteStepNumber
- Create `rca.vw_EightDCompletionStatus` (total/complete/skipped/in-progress/overdue counts)
- Reusable guard definitions table (`workflow.GuardDefinition`) decoupling guard logic from transition rows
- Notification metadata columns on `workflow.WorkflowTransition`
- Versioned workflow metadata: `workflow.WorkflowProcessVersion` with activation window, immutable-after-activation flag

**Dependencies:** None (foundation for 26-28)

#### Phase 26: Authorization and Approval Pipeline

**Patterns:** #1, #7, #6

**Deliverables:**
- `dbo.Role.ParentRoleId` + subtractive-inheritance validator
- `security.vw_EffectiveCrudMatrix` diagnostic view
- Centralized SoD helper (`workflow.usp_EnforceSeparationOfDuties`)
- Resolver proc `workflow.usp_ResolveApprovers` for dynamic routing
- Field-change-detection guard expression syntax on `workflow.WorkflowTransition`

**Dependencies:** Phase 25 (guard definitions)

#### Phase 27: Approval Lifecycle and Timeout Processing

**Patterns:** #3, #20

**Deliverables:**
- `ExpiresAtUtc`/`TimeoutActionApplied` on `workflow.PendingApprovalTransition`
- `workflow.usp_ProcessPendingApprovalTimeouts` scheduled processor
- `IsPresave BIT DEFAULT 0` on `workflow.WorkflowTransition`
- Presave path in `workflow.usp_TransitionState` (immediate commit + parallel approval)
- Compensated status + compensating transition logic for rejected presave

**Dependencies:** Phase 25, Phase 26

#### Phase 28: Event-Driven Chaining and Notifications

**Patterns:** #8, #13

**Deliverables:**
- Generalize outbox to CAPA/SCAR/Complaint/Audit entities
- `workflow.EventSubscription` table for internal event metadata
- `workflow.NotificationQueue` table for internal user notifications
- Notification write hooks in transition/approval procedures

**Dependencies:** Phase 25, Phase 27

#### Phase 29: Audit Infrastructure and Temporal Query

**Patterns:** #5 (ApiCallLog), #4, #22

**Deliverables:**
- `audit.ApiCallLog` table (correlationId, endpoint, duration, user, status)
- `@AsOfUtc DATETIME2 = NULL` on key read procs → `FOR SYSTEM_TIME AS OF`
- Shared hierarchy traversal helpers (`dbo.usp_GetTreeAncestors`/`Descendants`)
- Cycle-detection checks for all parent-child structures

**Dependencies:** None (independent track — must complete before API Phase 3.5)

#### Phase 30: SLA Enforcement and Background Jobs

**Patterns:** #12, #17

**Deliverables:**
- CAPA SLA seeds in `workflow.SlaConfiguration` (30/60/90-day by severity)
- Wire `workflow.usp_EvaluateEscalationRules` for CAPA entities
- `quality.vw_CapaTimelineCompliance` dashboard view
- `security.vw_EffectivePolicyMap` diagnostic view
- `dbo.BackgroundJobRun` table (start/end/status/error/idempotency key)
- Idempotency keys on batch procedures

**Dependencies:** Phase 27 (timeout processor is a background job)

#### Phase 31: Multi-Party Entity Lifecycle

**Patterns:** #19, #9

**Deliverables:**
- `CustomerResponseStatus`/`SupplierResponseStatus` columns on `quality.SupplierCar`
- `quality.ScarPartyStatusHistory` table
- `quality.vw_ScarPartyStatus` dashboard view
- External document identifier indexes on `quality.NcrExternalReference` etc.

**Dependencies:** None (independent track)

#### Phase 32: Validate-Only and Reference Data

**Patterns:** #14, #10, #15

**Deliverables:**
- `@IsValidateOnly BIT = 0` on 6+ write procedures with transaction-rollback pattern
- Canonical lookup views/procs per domain (DefectType, Severity, Disposition, etc.)
- `security.usp_ExportConfiguration`/`usp_ImportConfiguration` with upsert semantics

**Dependencies:** Phase 25 (validate-only on transition procs needs stable workflow foundation)

#### Phase 33: Data Lifecycle and Bulk Operations

**Patterns:** #16, #24

**Deliverables:**
- `dbo.usp_ArchiveClosedRecords` evaluating `dbo.RecordRetentionPolicy`
- `audit.usp_PurgeAuditBeyondRetention`
- `dbo.ArchivePurgeLog` table
- Bulk import procs: `dbo.usp_BulkImportLookupValues`, `dbo.usp_BulkImportDefectTypes`, `dbo.usp_BulkImportKnowledgeEntries`

**Dependencies:** None (independent track)

#### DB Dependency Graph

```
Phase 25 (Workflow Foundation)
  ├→ Phase 26 (Auth/Approval) → Phase 27 (Timeout/Presave)
  │                                ├→ Phase 28 (Events/Notifications)
  │                                └→ Phase 30 (SLA/Jobs)
  └→ Phase 32 (Validate-Only) [loose dependency]

Phase 29 (Audit/Temporal) ── INDEPENDENT
Phase 31 (Multi-Party/SCAR) ── INDEPENDENT
Phase 33 (Lifecycle/Bulk) ── INDEPENDENT
```

---

### B2. sf-quality-api — Insert Phase 3.5 + Enrich Existing Phases

**Decision:** Insert Phase 3.5 "API Infrastructure Hardening" before Phase 4. Expand scope of Phases 4, 7, 9, 10.

| Phase | Patterns Absorbed | Change Type |
|-------|-------------------|-------------|
| 3.5 (NEW) | #32 URL Versioning, #28 Audit Trail, #30 Rate Limiting | New phase (2 plans) |
| 4 (CAPA) | #31 Pagination, #34 Query Governor, #29 Symmetric Payloads | Scope expansion (2→3 plans) |
| 5-6 | #26 Error Mapping (ongoing each phase) | No structural change |
| 7 (Workflow) | #25 Feature Gating, #33 Validate-Only | Scope expansion |
| 9 (Dashboards) | #35 Two-Phase Retrieval | Minor expansion |
| 10 (Integration) | #27 Delta Sync, #36 Consumer Identity | Natural fit (already integration phase) |

#### Phase 3.5: API Infrastructure Hardening (NEW)

**Patterns:** #32, #28, #30

- **Plan 3.5-01:** URL versioning — `/v1` prefix on all 25 NCR routes + diagnostics; OpenAPI artifact → v0.3.0; route group refactoring
- **Plan 3.5-02:** Rate limiting + audit trail middleware — `AddRateLimiter` policies in Program.cs; `ApiCallLogMiddleware` writing to `audit.ApiCallLog` via Dapper; correlation ID linkage

**DB Prerequisite:** `audit.ApiCallLog` table must exist (DB Phase 29, or extracted as hotfix migration)

#### Phase 4 Expansion: CAPA + Query Infrastructure

**Added patterns:** #31 Cursor Pagination, #34 Query Governor, #29 Symmetric Payloads

- **New Plan 4-03:** Shared pagination infrastructure (cursor contracts, keyset query delegation) + query governor middleware + `GET /v1/ncr/{id}` canonical detail endpoint

**DB Prerequisite:** Cursor parameter support (`@AfterCursor`/`@PageSize`) on list procs

#### Phase 7 Expansion: Workflow + Feature Gating + Validate-Only

**Added patterns:** #25 Feature Gating, #33 Validate-Only

- Scope adds: Feature-gated endpoint authorization (permission check delegation to DB `security.usp_CheckPermission`); `?isValidateOnly=true` query parameter passthrough to DB procs

**DB Prerequisite:** Validate-only support in DB write procs (Phase 32)

#### Cross-Cutting: #26 Error Mapping Governance

Each phase from 4 onward includes a mandatory checklist item: verify all new DB error codes are mapped in `SqlErrorMapper.cs`. Automated cross-check script added in Phase 3.5 or 4.

---

### B3. sf-quality-app — No New Phases; Enrich Requirements + Context

All 9 app patterns are "Inform Planning." They map to existing phases via requirements and context enrichment:

| Pattern | Target Phase | Enrichment |
|---------|-------------|------------|
| #37 Feature Tree | Phase 3 (Auth) + Phase 7 | New req APP-AUTH-01: Feature entitlement tree from API |
| #38 Org Scope | Phase 3 (Auth) | New req APP-AUTH-02: Plant-scope selector from RLS |
| #39 Workflow Viz | Phase 7 (Workflow) | Enrich 07-CONTEXT: visual progress from workflow state machine |
| #40 Dashboards | Phase 9 | Enrich 09-CONTEXT: role-scoped parameterized widgets |
| #41 Knowledge | Phase 8 | Enrich 08-CONTEXT: in-form knowledge panels |
| #42 Notifications | Phase 7 | Enrich 07-CONTEXT: notification inbox (may defer to Phase 10) |
| #43 Audit Trail | Phase 8 | Enrich 08-CONTEXT: entity audit timeline component |
| #44 Form Preflight | Phase 4 (Forms) | New req APP-FORM-01: server-validated preflight via validate-only |
| #45 Drift Controls | Phase 10 | Enrich 10-CONTEXT: automated snapshot refresh + breaking-change detection |

**New requirements for REQUIREMENTS.md:**

- **APP-AUTH-01:** Feature entitlement tree governs UI action visibility
- **APP-AUTH-02:** Plant scope filtering reflects API-authorized scope
- **APP-WORKFLOW-03:** Workflow state visualization from API state machine
- **APP-WORKFLOW-04:** Notification inbox from API notification queue
- **APP-FORM-01:** Write forms support server-validated preflight
- **APP-TRACE-01:** Audit trail timeline from API audit data

---

### B4. Cross-Repo Pattern #46: Contract Chain Integrity

Distributed across phases:

- **API Phase 3.5:** Automated error-code cross-check script
- **API Phase 10:** Breaking-change detection in OpenAPI publication
- **App Phase 10:** Automated snapshot refresh trigger on API version increment

---

## C. Cross-Repo Dependency Map

**Critical Path: DB → API → App**

```
DB Phase 29 (audit.ApiCallLog table)
  └→ API Phase 3.5 (audit trail middleware)

DB Phase 32 (validate-only on write procs)
  └→ API Phase 7 (validate-only passthrough)
       └→ App Phase 4+ (form preflight)

DB Phase 28 (notification queue)
  └→ API Phase 7+ (notification endpoints)
       └→ App Phase 7 (notification inbox)

DB Phase 29 (temporal @AsOfUtc + cursor params)
  └→ API Phase 4 (pagination + two-phase retrieval)

DB Phase 31 (SCAR party status)
  └→ API Phase 5 (SCAR endpoints)
```

**Parallelization Opportunities:**

- DB Phases 29, 31, 33 are independent — can run in any order or interleaved
- App Phases 1-3 can start in parallel with API Phases 3.5-6 (no domain endpoint dependency)
- DB validate-only work (Phase 32) can run in parallel with API Phases 4-6

---

## D. Context Seeding Strategy

### D1. Reference Architecture Placement

Do NOT copy pattern mapping or spec files into each repo's `.planning/` folder. Instead:

- **Workspace root:** All reference architecture materials live in `sf-quality/Reference_Architecture/` as the single source of truth (see [README.md](README.md) for the full index)
- **Per-phase distillation:** Each phase CONTEXT file gets only the specific patterns, recommended approaches, migration citations, and proc signatures relevant to that phase — distilled from [Pattern_Mapping.md](Pattern_Mapping.md), not copy-pasted wholesale
- **Traceability:** Each phase CONTEXT references patterns by number (e.g., "Implements Pattern #14 — Validate-Only / Dry-Run Mode") with a pointer to `sf-quality/Reference_Architecture/Pattern_Mapping.md` for full context

### D2. Phase Context File Template

Each new phase CONTEXT file should include:

```markdown
## Reference Architecture Patterns
<!-- Which patterns this phase implements, by number and name -->

## Existing Artifacts
<!-- Specific migrations, procs, views, tables this phase builds on -->
<!-- Copied from the pattern mapping's "Code evidence" sections -->

## Recommended Approach (Distilled)
<!-- The specific deliverables from the pattern mapping's recommendations -->
<!-- Proc signatures, column names, SQL patterns as applicable -->

## Cross-Repo Dependencies
<!-- What must exist in other repos before/after this phase -->
```

### D3. Hidden Architecture Pattern Distillation

The [Hidden_Architecture_Patterns_Reverse_Engineered.json](Hidden_Patterns/Hidden_Architecture_Patterns_Reverse_Engineered.json) content should be distilled into phase context, not referenced as-is (it's 39 KB of dense JSON):

| Hidden Pattern | Distill Into | Key Extraction |
|----------------|-------------|----------------|
| Guided Process Orchestration | Phase 25 CONTEXT (8D step state enum rationale) | Per-step state machine concept; monitoring workflow concept → vw_EightDCompletionStatus |
| Policy Resolution Engine | Phase 30 CONTEXT (SLA policy resolution) | Candidate→filter→priority→resolve algorithm; point-in-time resolution; EffectivePolicyMap concept |
| Data Staging / Edit Mode | Phase 27 CONTEXT (optimistic commit), Phase 32 CONTEXT (validate-only) | Presave vs. Approved commit modes; validate-only via rollback; field-change-detection routing |

### D4. Specific SQL/Schema Content to Capture in Context Files

These patterns contain precise schema recommendations that must be in CONTEXT files for GSD execution agents:

- **Phase 25:** `rca.EightDStep` ALTER columns: `StepStatus TINYINT NOT NULL DEFAULT 0`, `IsSkippable BIT NOT NULL DEFAULT 0`, `SkippedReason NVARCHAR(500) NULL`, `SkippedByUserId INT NULL`, `PrerequisiteStepNumber TINYINT NULL`
- **Phase 27:** `workflow.PendingApprovalTransition` ALTER: `ExpiresAtUtc DATETIME2 NULL`, `TimeoutActionApplied NVARCHAR(50) NULL`; `workflow.WorkflowTransition` ALTER: `IsPresave BIT NOT NULL DEFAULT 0`
- **Phase 29:** `audit.ApiCallLog` columns: `ApiCallLogId INT IDENTITY`, `CorrelationId NVARCHAR(50)`, `Route NVARCHAR(500)`, `HttpMethod NVARCHAR(10)`, `CallerOid NVARCHAR(100)`, `HttpStatus INT`, `DurationMs INT`, `RequestTimestampUtc DATETIME2`
- **Phase 31:** `quality.SupplierCar` ALTER: `CustomerResponseStatus TINYINT NOT NULL DEFAULT 0`, `SupplierResponseStatus TINYINT NOT NULL DEFAULT 0`
- **Phase 32:** Validate-only pattern: `@IsValidateOnly BIT = 0` → execute all validation → `IF @IsValidateOnly = 1 BEGIN ROLLBACK; SELECT validation resultset; RETURN; END`

---

## E. GSD Workflow Sequence

### Step 0: Prerequisites — Complete v2.0 First

Phases 23-24 in sf-quality-db must ship before v3.0 begins. Phase 22 (Analytics Foundation and Security) is DEFERRED — preconditions not met (schema evolving, no consumers, role architecture not locked). See `sf-quality-db/.planning/phases/22-analytics-foundation-security/22-DEFERRAL.md`.

```
sf-quality-db: /gsd:plan-phase 23  →  /gsd:execute-phase 23
sf-quality-db: /gsd:plan-phase 24  →  /gsd:execute-phase 24
sf-quality-db: /gsd:complete-milestone  (archives v2.0; Phase 22 deferred to post-v2.0)
```

### Step 1: sf-quality-db — Initialize v3.0 Milestone

```
sf-quality-db: /gsd:new-milestone
  → Milestone name: "Architectural Hardening and Platform Maturation"
  → Milestone version: v3.0
  → Phases: 25-33 (as defined in Section B1)
  → Requirements: New ARCH-xx requirement IDs mapping to each pattern
```

This creates the ROADMAP entries, REQUIREMENTS entries, and phase directory stubs for all 9 phases.

### Step 2: sf-quality-db — Phase 29 First (API Prerequisite)

Phase 29 contains `audit.ApiCallLog` which API Phase 3.5 depends on. Execute this first from the independent track:

```
sf-quality-db: /gsd:discuss-phase 29   (gather context for audit/temporal/tree work)
sf-quality-db: /gsd:plan-phase 29
sf-quality-db: /gsd:execute-phase 29
```

### Step 3: sf-quality-api — Insert Phase 3.5 and Execute

After DB Phase 29 lands `audit.ApiCallLog`:

```
sf-quality-api: /gsd:insert-phase   (insert Phase 3.5 "API Infrastructure Hardening")
sf-quality-api: /gsd:discuss-phase 3.5
sf-quality-api: /gsd:plan-phase 3.5
sf-quality-api: /gsd:execute-phase 3.5
```

### Step 4: sf-quality-db — Main Dependency Chain (Phases 25-28, 30)

Can interleave with API Phase 4-6 execution:

```
sf-quality-db: /gsd:discuss-phase 25  →  /gsd:plan-phase 25  →  /gsd:execute-phase 25
sf-quality-db: /gsd:discuss-phase 26  →  /gsd:plan-phase 26  →  /gsd:execute-phase 26
sf-quality-db: /gsd:discuss-phase 27  →  /gsd:plan-phase 27  →  /gsd:execute-phase 27
sf-quality-db: /gsd:discuss-phase 28  →  /gsd:plan-phase 28  →  /gsd:execute-phase 28
sf-quality-db: /gsd:discuss-phase 30  →  /gsd:plan-phase 30  →  /gsd:execute-phase 30
```

**Note:** Use `/gsd:discuss-phase` before `/gsd:plan-phase` for all phases — these are complex, multi-pattern phases where the planner needs domain context gathering.

### Step 5: sf-quality-db — Independent Tracks (Phases 31, 32, 33)

Can execute in any order; 31 and 33 can interleave with Step 4:

```
sf-quality-db: /gsd:plan-phase 31  →  /gsd:execute-phase 31
sf-quality-db: /gsd:discuss-phase 32  →  /gsd:plan-phase 32  →  /gsd:execute-phase 32
sf-quality-db: /gsd:plan-phase 33  →  /gsd:execute-phase 33
```

Phase 32 gets `/gsd:discuss-phase` because validate-only is a cross-cutting pattern touching 6+ procs.
Phases 31 and 33 are straightforward enough to skip discuss.

### Step 6: sf-quality-db — Quick Items

```
sf-quality-db: /gsd:quick "Formalize document storage contract (#23)"
sf-quality-db: /gsd:quick "Add expand parameters to NCR detail proc (#18)"
```

### Step 7: sf-quality-db — Complete v3.0

```
sf-quality-db: /gsd:audit-milestone
sf-quality-db: /gsd:complete-milestone
```

### Step 8: sf-quality-api — Phases 4-10 (Enriched)

Execute with expanded scope per Section B2. Phase 4 waits for DB cursor/pagination support (can be a hotfix migration or part of Phase 29/32):

```
sf-quality-api: /gsd:plan-phase 4   →  /gsd:execute-phase 4    (CAPA + pagination + governor)
sf-quality-api: /gsd:plan-phase 5   →  /gsd:execute-phase 5    (SCAR/Audit)
sf-quality-api: /gsd:plan-phase 6   →  /gsd:execute-phase 6    (RCA Tools)
sf-quality-api: /gsd:plan-phase 7   →  /gsd:execute-phase 7    (Workflow + gating + validate-only)
sf-quality-api: /gsd:plan-phase 8   →  /gsd:execute-phase 8    (Knowledge)
sf-quality-api: /gsd:plan-phase 9   →  /gsd:execute-phase 9    (Dashboards + two-phase retrieval)
sf-quality-api: /gsd:plan-phase 10  →  /gsd:execute-phase 10   (Integration + delta sync)
```

### Step 9: sf-quality-app — Enrich Requirements, Then Execute Phases

First update planning artifacts (requirements + context enrichment per Section B3), then execute:

```
sf-quality-app: Update REQUIREMENTS.md with 6 new requirements
sf-quality-app: Enrich phase CONTEXT files (03, 04, 07, 08, 09, 10)
sf-quality-app: /gsd:plan-phase 1  →  /gsd:execute-phase 1
... (continue through Phase 10)
```

App Phases 1-3 can start in parallel with API Phases 3.5-6. App Phase 4+ should wait for API Phase 4+.

### Parallelization Summary

```
PARALLEL TRACK A (DB main chain):    25 → 26 → 27 → 28, 30
PARALLEL TRACK B (DB independent):   29 (first!), 31, 33
PARALLEL TRACK C (API):              3.5 (after DB 29) → 4 → 5 → 6 → 7 (after DB 32) → 8 → 9 → 10
PARALLEL TRACK D (App):              1 → 2 → 3 (can start with API 3.5) → 4+ (waits for API 4+)

Cross-track gates:
  DB 29 ──gate──→ API 3.5
  DB 32 ──gate──→ API 7
  DB 28 ──gate──→ API 7+ (notifications)
  DB 31 ──gate──→ API 5 (SCAR)
  API 4+ ──gate──→ App 4+
```

---

## F. Planning File Updates Summary

### sf-quality-db (`../sf-quality-db/`)

| File | Action |
|------|--------|
| `../sf-quality-db/.planning/PROJECT.md` | Add v3.0 milestone description |
| `../sf-quality-db/.planning/ROADMAP.md` | Add phases 25-33 with requirements, success criteria, plan tracking |
| `../sf-quality-db/.planning/REQUIREMENTS.md` | Add ARCH-01 through ARCH-24 requirement IDs (one per DB pattern) |
| `../sf-quality-db/.planning/MILESTONES.md` | Archive v2.0 (after completion), add v3.0 header |
| `../sf-quality-db/.planning/phases/25-*/25-CONTEXT.md` through `33-*/33-CONTEXT.md` | Create 9 phase context files with distilled pattern content |

### sf-quality-api (`../sf-quality-api/`)

| File | Action |
|------|--------|
| `../sf-quality-api/.planning/ROADMAP.md` | Insert Phase 3.5; update plan counts for Phases 4, 7, 9 |
| `../sf-quality-api/.planning/REQUIREMENTS.md` | Add API-INFRA-06 (URL versioning), API-INFRA-07 (rate limiting), API-INFRA-08 (audit trail), API-INFRA-09 (pagination), API-INFRA-10 (query governor) |
| `../sf-quality-api/.planning/phases/03.5-api-infrastructure-hardening/03.5-CONTEXT.md` | Create new phase directory + context file |
| `../sf-quality-api/.planning/phases/04-capa-complaint/04-CONTEXT.md` | Enrich with pagination, governor, symmetric payload patterns |
| `../sf-quality-api/.planning/phases/07-workflow-action-items/07-CONTEXT.md` | Enrich with feature gating, validate-only patterns |

### sf-quality-app (`../sf-quality-app/`)

| File | Action |
|------|--------|
| `../sf-quality-app/.planning/REQUIREMENTS.md` | Add 6 new requirements (APP-AUTH-01/02, APP-WORKFLOW-03/04, APP-FORM-01, APP-TRACE-01) |
| `../sf-quality-app/.planning/phases/03-easy-auth-session/03-CONTEXT.md` | Enrich with feature entitlement + org scope patterns |
| `../sf-quality-app/.planning/phases/04-lookup-driven-forms/04-CONTEXT.md` | Enrich with server-validated form preflight |
| `../sf-quality-app/.planning/phases/07-workflow-approvals/07-CONTEXT.md` | Enrich with workflow visualization, notification inbox |
| `../sf-quality-app/.planning/phases/08-knowledge-traceability-ux/08-CONTEXT.md` | Enrich with audit trail display, knowledge integration |
| `../sf-quality-app/.planning/phases/09-dashboards-views/09-CONTEXT.md` | Enrich with role-scoped dashboard parameterization |
| `../sf-quality-app/.planning/phases/10-deployment-e2e-governance/10-CONTEXT.md` | Enrich with contract drift controls |

---

## G. Verification

After all phases complete across all repos:

1. **Pattern coverage audit:** Walk all 46 patterns in [Pattern_Mapping.md](Pattern_Mapping.md) and verify each has either: a completed phase, a `/gsd:quick` execution, a documented deferral, or enriched requirements/context
2. **Contract chain integrity:** Run `Invoke-CycleChecks.ps1` in both API and App repos to confirm no drift
3. **DB contract manifest:** Update `../sf-quality-db/.planning/contracts/db-contract-manifest.json` to reflect all new procs/views from v3.0
4. **API OpenAPI artifact:** Verify version reflects all pattern additions
5. **Requirements traceability:** Every ARCH-xx, API-INFRA-xx, and APP-xx requirement links to a completed phase or documented deferral
6. **Cross-repo gates:** Confirm all DB prerequisites landed before their API/App consumers were executed
