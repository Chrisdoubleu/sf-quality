# Execution Plan: 46 Reference Architecture Patterns → GSD Workflow

**Date:** 2026-02-21
**Last Updated:** 2026-02-22
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
| Hidden Patterns | [Hidden_Patterns/Hidden_Architecture_Patterns_Refined.json](Hidden_Patterns/Hidden_Architecture_Patterns_Refined.json) | 3 reverse-engineered implicit patterns (authoritative refined version; see _Reverse_Engineered.json for original baseline) |
| Quality Forms Final Review | [Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md](Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md) | Authoritative go/no-go and blocker checklist for inspection forms |
| Quality Forms Package | [Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/index.md](Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/index.md) | Implementation package index (DB/API/App inspection artifacts) |

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

**Rationale:** v2.0 ("Quality Intelligence Platform") has 2 active remaining phases (23-24) with tightly scoped requirements (governance, incoming substrate). Phase 22 is DEFERRED (see Step 0 for full deferral context). The 24 DB patterns represent a different initiative — making what exists production-grade. Absorbing them into v2.0 would dilute its narrative and bloat requirements from 37 to 60+. v3.0 begins after v2.0 ships.

**Note:** Pattern #5 (audit.vw_SuspiciousActivity) was previously considered for Phase 22 (analytics). With Phase 22 deferred (Step 0), Pattern #5 stays in v3.0 Phase 29 where it naturally groups with ApiCallLog, temporal queries, and tree helpers — all audit schema work with no analytics schema dependency.

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

**Quick item notes:**
- **#23 (Document Storage):** Prerequisite: pending storage decision must be resolved first. Workspace memory notes "SharePoint references: decision pending on document storage — do not clean up yet." Cannot execute until storage contract direction is confirmed.
- **#18 (Composite Aggregate):** No dependencies. Consider executing before or concurrent with DB Phase 29 (first executed phase) so that the `expand` parameter is available for API Phase 4 pagination/query infrastructure planning.
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

**Acceptance criteria (gate for Phase 26):**
1. `workflow.GuardDefinition` table exists and is queryable with seeded guard definitions
2. `rca.EightDStep` has `StepStatus` column with non-zero default behavior
3. `rca.vw_EightDCompletionStatus` returns non-null aggregated results
4. `workflow.WorkflowProcessVersion` table exists with activation window columns

#### Phase 26: Authorization and Approval Pipeline

**Patterns:** #1, #7, #6

**Deliverables:**
- Business-role overlay mapping between RBAC package capability IDs (`F-*`) and runtime permission codes (`WF.*`) with deterministic alias resolution.
- Delegation hierarchy metadata for role-assignment authority only (no runtime permission inheritance).
- `security.vw_EffectiveCrudMatrix` diagnostic view (effective grants + deny reasons + merged constraints).
- Centralized SoD helper (`workflow.usp_EnforceSeparationOfDuties`) with explicit waiver checks.
- Resolver proc `workflow.usp_ResolveApprovers` for dynamic routing using explicit grants and scope constraints.

**Dependencies:** Phase 25 (guard definitions)

**Acceptance criteria (gate for Phase 27):**
1. Capability alias mapping resolves `F-*` -> `WF.*` deterministically for test transitions.
2. Permission evaluation remains explicit-grant-only; hierarchy metadata is not used for inherited allow decisions.
3. `security.vw_EffectiveCrudMatrix` returns role x data x CRUD with deterministic conflict handling.
4. `workflow.usp_ResolveApprovers` resolves dynamic approvers for a test transition using assignment scope + constraints.

#### Phase 27: Approval Lifecycle and Timeout Processing

**Patterns:** #3, #20

**Deliverables:**
- `ExpiresAtUtc`/`TimeoutActionApplied` on `workflow.PendingApprovalTransition`
- `workflow.usp_ProcessPendingApprovalTimeouts` scheduled processor
- `IsPresave BIT DEFAULT 0` on `workflow.WorkflowTransition`
- Presave path in `workflow.usp_TransitionState` (immediate commit + parallel approval)
- Compensated status + compensating transition logic for rejected presave

**Dependencies:** Phase 25, Phase 26

**Acceptance criteria (gate for Phase 28):**
1. `workflow.usp_ProcessPendingApprovalTimeouts` processes expired approvals
2. Presave transitions on `IsPresave=1` commit entity state immediately and create pending approval
3. Rejected presave creates compensating transition reverting entity state

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

**Acceptance criteria (gate for API Phase 3.5):**
1. `audit.ApiCallLog` table exists with all specified columns
2. At least one read proc accepts `@AsOfUtc DATETIME2 = NULL` and returns temporal results
3. `dbo.usp_GetTreeAncestors`/`dbo.usp_GetTreeDescendants` callable on existing hierarchies

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

**Acceptance criteria (gate for API Phase 7):**
1. At least 3 write procs accept `@IsValidateOnly BIT = 0` and return validation resultsets on rollback
2. Canonical lookup views exist per domain (DefectType, Severity, Disposition)
3. `security.usp_ExportConfiguration` produces a portable JSON-compatible resultset

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
| #37 Feature Tree | Phase 3 (Auth) + Phase 7 | New req APP-AUTH-04: Feature entitlement tree from API |
| #38 Org Scope | Phase 3 (Auth) | New req APP-AUTH-05: Plant-scope selector from RLS |
| #39 Workflow Viz | Phase 7 (Workflow) | Enrich 07-CONTEXT: visual progress from workflow state machine |
| #40 Dashboards | Phase 9 | Enrich 09-CONTEXT: role-scoped parameterized widgets |
| #41 Knowledge | Phase 8 | Enrich 08-CONTEXT: in-form knowledge panels |
| #42 Notifications | Phase 7 | Enrich 07-CONTEXT: notification inbox (may defer to Phase 10) |
| #43 Audit Trail | Phase 8 | Enrich 08-CONTEXT: entity audit timeline component |
| #44 Form Preflight | Phase 4 (Forms) | New req APP-FORM-03: server-validated preflight via validate-only |
| #45 Drift Controls | Phase 10 | Enrich 10-CONTEXT: automated snapshot refresh + breaking-change detection |

**New requirements for REQUIREMENTS.md:**

Note: IDs are numbered to avoid collision with existing APP-AUTH-01 through APP-AUTH-03, APP-FORM-01/02, and APP-TRACE-01 already in REQUIREMENTS.md.

- **APP-AUTH-04:** Feature entitlement tree governs UI action visibility
- **APP-AUTH-05:** Plant scope filtering reflects API-authorized scope
- **APP-WORKFLOW-03:** Workflow state visualization from API state machine
- **APP-WORKFLOW-04:** Notification inbox from API notification queue
- **APP-FORM-03:** Write forms support server-validated preflight
- **APP-TRACE-02:** Audit trail timeline from API audit data

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

### Cross-Repo Amendment Protocol

If an API phase discovers that a prerequisite DB schema needs modification (e.g., API Phase 3.5 finds `audit.ApiCallLog` needs an additional column):

1. **Pause** the API phase at the discovery point
2. **Switch to sf-quality-db** and run `/gsd:quick "Hotfix migration: [description of schema change]"`
3. **Refresh** `db-contract-manifest.json` to reflect the hotfix
4. **Resume** the API phase with the updated schema available

This keeps schema changes in the DB repo (where they belong), maintains the contract chain, and avoids cross-repo file modifications. Hotfix migrations follow the same idempotent migration pattern as all other DB migrations.

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

### D2. Phase Context File Authorship

**Who creates them:** The `/gsd:discuss-phase` agent creates the phase CONTEXT file as its primary output. During discuss-phase, the agent should read the relevant patterns from `Reference_Architecture/Pattern_Mapping.md` and create the phase CONTEXT file using the template below, including the specific schema content from Section D4.

**When they're created:** Before `/gsd:plan-phase` runs. For phases that skip discuss (Phases 31, 33), the user creates a minimal CONTEXT file from the template before invoking `/gsd:plan-phase`.

### Phase Context File Template

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

### Step 0: Prerequisites — Complete v2.0 and Refresh Manifest

Phases 23-24 in sf-quality-db must ship before v3.0 begins.

**Phase 22 deferral (consolidated context):** Phase 22 "Analytics Foundation and Security" is DEFERRED. Preconditions not met: schema is still evolving across v2.0 phases, no analytics consumers exist, and the role architecture is not locked for security grant generation. The SEC-01 requirement (security grants) is not part of Pattern #21 — SEC-01 ships inline with future migrations that add grant-requiring objects. Pattern #21 (Organizational Scoping) is independently deferred in v3.0 (Section B1) because there is no concrete gap beyond the current plant-level model. Full deferral rationale: `sf-quality-db/.planning/phases/22-analytics-foundation-security/22-DEFERRAL.md`.

**Manifest prerequisite:** The `db-contract-manifest.json` is currently v1.0.0 and does not reflect the 9 knowledge views and 1 advisory procedure added in Phase 21. Refresh the manifest to reflect Phase 21 additions before v3.0 work begins, so that API phase planners have an accurate contract surface.

```
sf-quality-db: /gsd:discuss-phase 23  →  /gsd:plan-phase 23  →  /gsd:execute-phase 23
sf-quality-db: /gsd:discuss-phase 24  →  /gsd:plan-phase 24  →  /gsd:execute-phase 24
sf-quality-db: /gsd:quick "Refresh db-contract-manifest.json to reflect Phase 21-24 additions"
sf-quality-db: /gsd:complete-milestone  (archives v2.0; Phase 22 deferred — see above)
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
sf-quality-db: /gsd:verify-work 29     (acceptance: audit.ApiCallLog exists, @AsOfUtc on key procs, tree helpers callable)
sf-quality-db: /gsd:quick "Refresh db-contract-manifest.json for Phase 29 additions"
```

### Step 2.5: sf-quality-api — Phase 3.4 Plumbing Fixes (Prerequisite for 3.5)

Before inserting Phase 3.5, confirm whether Phase 3.4 middleware changes were already completed as part of Phase 3, or execute as a quick item:

```
sf-quality-api: Check git log — if CorrelationIdMiddleware GUID enforcement, SqlErrorNumber
                stash on ErrorHandlingMiddleware, and 50414→HTTP 202 handler are already
                present, skip this step.

sf-quality-api: /gsd:quick "Phase 3.4: Middleware plumbing — enforce GUID correlation IDs,
                stash SqlErrorNumber on ErrorHandlingMiddleware, add 50414→HTTP 202 mapping,
                remove 50414 from SqlErrorMapper"
```

**Source:** [API_Integration_Patterns/Phase_Implementation/HANDOFF_CONTEXT.md](API_Integration_Patterns/Phase_Implementation/HANDOFF_CONTEXT.md)

**Note:** No DB migration required for Phase 3.4 — these are middleware-only changes.

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
sf-quality-db: /gsd:verify-work 25    (acceptance: guard definitions table queryable, EightDStep has StepStatus, vw_EightDCompletionStatus returns results)
sf-quality-db: /gsd:discuss-phase 26  →  /gsd:plan-phase 26  →  /gsd:execute-phase 26
sf-quality-db: /gsd:verify-work 26    (acceptance: F-* to WF.* alias mapping deterministic, explicit-grant-only evaluation preserved, vw_EffectiveCrudMatrix queryable, usp_ResolveApprovers callable)
sf-quality-db: /gsd:discuss-phase 27  →  /gsd:plan-phase 27  →  /gsd:execute-phase 27
sf-quality-db: /gsd:verify-work 27    (acceptance: timeout processor runs, presave transitions commit immediately, compensated status on rejection)
sf-quality-db: /gsd:discuss-phase 28  →  /gsd:plan-phase 28  →  /gsd:execute-phase 28
sf-quality-db: /gsd:verify-work 28    (acceptance: NotificationQueue writes on approval, outbox covers CAPA/SCAR)
sf-quality-db: /gsd:quick "Refresh db-contract-manifest.json for Phases 25-28 additions"
sf-quality-db: /gsd:discuss-phase 30  →  /gsd:plan-phase 30  →  /gsd:execute-phase 30
```

**Note:** Use `/gsd:discuss-phase` before `/gsd:plan-phase` for all phases — these are complex, multi-pattern phases where the planner needs domain context gathering.

**Note:** Verification (`/gsd:verify-work`) runs after each phase in the dependency chain to catch issues before dependents begin. The manifest refresh after Phase 28 covers all cross-repo-visible artifacts from Phases 25-28.

### Step 5: sf-quality-db — Independent Tracks (Phases 31, 32, 33)

Can execute in any order; 31 and 33 can interleave with Step 4:

```
sf-quality-db: /gsd:plan-phase 31  →  /gsd:execute-phase 31
sf-quality-db: /gsd:quick "Refresh db-contract-manifest.json for Phase 31 SCAR party status additions"
sf-quality-db: /gsd:discuss-phase 32  →  /gsd:plan-phase 32  →  /gsd:execute-phase 32
sf-quality-db: /gsd:quick "Refresh db-contract-manifest.json for Phase 32 validate-only procs"
sf-quality-db: /gsd:plan-phase 33  →  /gsd:execute-phase 33
```

Phase 32 gets `/gsd:discuss-phase` because validate-only is a cross-cutting pattern touching 6+ procs.
Phases 31 and 33 are straightforward enough to skip discuss.
Manifest refreshes after Phases 31 and 32 because both introduce cross-repo-visible artifacts (SCAR party status → API Phase 5; validate-only procs → API Phase 7).

### Step 6: sf-quality-db — Quick Items

**#18 should run early** (before or alongside Step 2) so API Phase 4 can consume the `expand` parameter:

```
sf-quality-db: /gsd:quick "Add expand parameters to NCR detail proc (#18)"
```

**#23 runs when ready** — blocked until the document storage decision is resolved:

```
sf-quality-db: /gsd:quick "Formalize document storage contract (#23)"   (prerequisite: storage decision confirmed)
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
| `../sf-quality-app/.planning/REQUIREMENTS.md` | Add 6 new requirements (APP-AUTH-04/05, APP-WORKFLOW-03/04, APP-FORM-03, APP-TRACE-02) |
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
3. **DB contract manifest:** Verify `../sf-quality-db/.planning/contracts/db-contract-manifest.json` reflects all new procs/views from v3.0 (incremental refreshes happen after Phases 29, 28, 31, and 32 per the workflow sequence — this step confirms completeness)
4. **API OpenAPI artifact:** Verify version reflects all pattern additions
5. **Requirements traceability:** Every ARCH-xx, API-INFRA-xx, and APP-xx requirement links to a completed phase or documented deferral
6. **Cross-repo gates:** Confirm all DB prerequisites landed before their API/App consumers were executed

If Section H is executed, add:

7. **Quality Forms entry-gate audit:** Verify all nine checks in `Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md` "Implementation Start Criteria" are green before opening Quality Forms phases in any child repo.
8. **STRUCT-10 FK policy audit:** Verify `Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/08_inspection_fk_policy.md` is approved and referenced before opening Quality Forms phases.

---

## H. Quality Forms Module Integration (Post-Core Extension Track)

This section weaves `Reference_Architecture/Quality_Forms_Module/` into the master sequence across DB/API/App.

This track is **not** part of the original 46-pattern closure scope. It is a follow-on module track that starts only after core contract-chain prerequisites are met.

### H1. Current Snapshot and Entry Gates

**Current planning snapshot (2026-02-22):**
- `sf-quality-db`: v2.0 active (Phase 23 next), v3.0 not started
- `sf-quality-api`: Phase 3 complete, Phase 3.5 next
- `sf-quality-app`: Phase 1 not started
- Quality Forms package status: **No-go** (`Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md`)

**Mandatory entry gates before any Quality Forms repo phase opens:**
1. DB Phase 23 and 24 complete, and DB contract manifest refreshed from live state.
2. API Phase 3.5 complete (versioned `/v1` surface, audit middleware, hardening in place).
3. API 50414 handling uses 202 contract semantics (per `API_Integration_Patterns/Phase_Implementation/DECISIONS.md`), and Quality Forms docs are aligned to that behavior.
4. All nine "Implementation Start Criteria" items in the Quality Forms final review are checked.
5. Quality Forms API docs are normalized to the active API conventions (`/v1` route versioning, contract-chain publication steps, deterministic error mapping).
6. STRUCT-10 inspection FK policy is approved in `Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/08_inspection_fk_policy.md`.

### H2. Phase Insertion Strategy Across Repos

Use a dedicated post-core extension wave and insert phased work in each repo roadmap:

| Repo | Inserted Phase(s) | Goal | Hard Dependency |
|------|-------------------|------|-----------------|
| `sf-quality-db` | **34-36** (new module wave) | Land inspection schema + seeds + workflow safety fixes + deterministic 29-proc implementation contracts | H1 gates + DB Phase 23/24 complete |
| `sf-quality-api` | **11-13** (new module wave) | Land 29 inspection endpoints as thin proc gateway, publish OpenAPI artifacts each wave | DB 34-36 contract publication gates |
| `sf-quality-app` | **11-13** (new module wave) | Land template builder, operator due/fill flow, inspection analytics/attachments UX | API 11-13 OpenAPI gates + App Phase 1-4 baseline |

Recommended DB breakdown:
- **DB 34:** Blocker closure + migration safety (159 additive constraint, explicit StatusCode contract in 158/160, security seed migration, workflow dispatch/service-context guarantees documented)
- **DB 35:** Inspection schema rollout and naming/contract corrections from adjudication
- **DB 36:** Stored procedure implementation hardening (all 29 deterministic contracts), schedule/NCR/attachment integration, performance validation

Recommended API breakdown:
- **API 11:** Template + inspection instance core endpoints
- **API 12:** Assignment/scheduling/due queue/reporting endpoints
- **API 13:** Attachment finalize/SAS orchestration boundaries, SPC extract endpoint, final contract/governance checks

Recommended App breakdown:
- **App 11:** Template list/editor/publish workflow UX
- **App 12:** Due queue + inspection fill/submit/review UX
- **App 13:** Inspection analytics, attachment UX hardening, release governance

### H3. Contract Chain Waves for Quality Forms

Do not execute Quality Forms as one large batch. Use three contract waves:

1. **Wave QF-A (Foundations)**
   - DB 34 complete -> refresh `db-contract-manifest.json`
   - API 11 complete -> publish OpenAPI
   - App 11 complete -> refresh app API snapshot/types

2. **Wave QF-B (Operations)**
   - DB 35 complete -> refresh manifest
   - API 12 complete -> publish OpenAPI
   - App 12 complete -> refresh app snapshot/types

3. **Wave QF-C (Hardening/Analytics)**
   - DB 36 complete -> refresh manifest
   - API 13 complete -> publish OpenAPI
   - App 13 complete -> refresh app snapshot/types

Each wave is blocked until the previous repo in the chain has published its contract artifact.

### H4. Planning Artifacts to Update When Opening the Track

When H2 begins, update child repo planning files (in repo context):

- `../sf-quality-db/.planning/ROADMAP.md`: add DB phases 34-36 under a post-v3 module milestone
- `../sf-quality-db/.planning/REQUIREMENTS.md`: add Quality Forms requirement IDs mapped to adjudication decisions
- `../sf-quality-db/.planning/phases/*/`: add DB 34-36 CONTEXT files sourced from Quality Forms package + final adjudication
- `../sf-quality-api/.planning/ROADMAP.md`: add API phases 11-13 for inspection endpoints
- `../sf-quality-api/.planning/REQUIREMENTS.md`: add inspection endpoint contract requirements
- `../sf-quality-api/.planning/phases/*/`: add API 11-13 CONTEXT files based on finalized 29 endpoint contracts
- `../sf-quality-app/.planning/ROADMAP.md`: add App phases 11-13 for inspection UX
- `../sf-quality-app/.planning/REQUIREMENTS.md`: add inspection builder/operator analytics UX requirements
- `../sf-quality-app/.planning/phases/*/`: add App 11-13 CONTEXT files based on finalized API contracts

### H5. Non-Negotiable Quality Forms Alignment Rules

1. Keep SQL authoritative: no business-rule migration into API or app.
2. Preserve approval semantics: API approval-required responses follow 202 contract handling.
3. Preserve route governance: inspection endpoints must be versioned under `/v1`.
4. Enforce contract chain after each wave: DB manifest -> API publish -> App snapshot.
5. Do not start API/App Quality Forms execution while DB checklist gates are open.

## Reconciliation Addendum (2026-02-22)

- Namespace split: keep `ARCH-*` and add `STRUCT-01` through `STRUCT-10` for structural-remediation tracking.
- Phase 25 is expanded to explicitly cover `STRUCT-01`, `STRUCT-02`, and `STRUCT-03` boundary hardening outcomes.
- Phase 26.1 is inserted as an ABAC deepening branch controlled by an explicit decision gate.
- API Phase 3.6 is inserted for ports/adapters refactoring and endpoint SQL boundary cleanup.
- Pre-QF entry requires `STRUCT-10` inspection FK policy approval and stage-gate linkage.
