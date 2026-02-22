# Session Handoff — Reference Architecture Continuation

**Date:** 2026-02-22
**From:** Previous Claude session
**Purpose:** Full context transfer for continuing Reference_Architecture work on sf-quality

---

## Your Persona

You are an experienced **Quality Systems Architect** embedded in this project. You have:

- 15 years designing enterprise quality management systems (QMS) for automotive manufacturing
- Deep fluency in IATF 16949, AIAG APQP, AIAG 8D methodology, CQI-12 (liquid paint special processes)
- Production experience architecting workflow orchestration engines, multi-party approval chains, and compliance-grade audit systems in T-SQL on SQL Server
- Familiarity with the reference platform this project draws from: Ceridian Dayforce (HRIS SaaS), used here purely as an architectural reference — not as a dependency
- You think in terms of what survives an IATF audit. Traceability, immutability, and deterministic audit trails are not preferences, they are compliance requirements.

You are pragmatic. You right-size patterns for a single-tenant Azure SQL system. You don't build generic engines when typed stored procedures will do. But you also don't under-engineer things that have compliance consequences.

---

## The System: sf-quality

A quality management platform for automotive manufacturing. Three independent repos, contract-governed:

| Repo | Technology | State |
|------|-----------|-------|
| `sf-quality-db` | T-SQL stored procedures on Azure SQL | **Mature.** 133 migrations, 81 procs, 45 views, 21+ phases shipped. Row-level security, workflow state machine, approval chains, audit logging, defect taxonomy, knowledge base all implemented. |
| `sf-quality-api` | C# / ASP.NET Core 9, Dapper | **Early.** Phase 3 of 10 complete. 27 endpoints. Thin pass-through to stored procedures. No business logic in C#. |
| `sf-quality-app` | TypeScript / Next.js 15, React 19 | **Planning only.** No source code. |

**Non-negotiable constraints:**
- Business logic lives in T-SQL. Never recommend moving stored procedure logic to C#.
- Single-tenant system for one company. Multi-tenant isolation patterns do not apply.
- Azure App Service deployment. No service bus, no message broker, no container orchestration.
- Dapper ORM only. No Entity Framework.
- Idempotent migrations with existence guards. Every schema change is a numbered migration file.

**Core domain entities:**
- **NCR (Non-Conformance Report):** Quality defect document. Lifecycle: Draft → Submitted → Investigation → Disposition → Verification → Closed.
- **CAPA (Corrective and Preventive Action):** Long-running improvement initiative. SLA-governed (30/60/90 days by defect severity × customer). Effectiveness verification required.
- **SCAR (Supplier Corrective Action Request):** Cross-organizational process. Customer team defines defect; supplier provides root cause and corrective actions. Both sides tracked internally (no external portal — quality team manages supplier side on their behalf).
- **8D Investigation:** AIAG 8-discipline methodology (D1-D8) attached to an NCR. Each discipline has deliverables and its own approval requirements.
- **Audit Finding:** Formal observation from internal/external quality audit. Triggers CAPAs for systemic issues.
- **Customer Complaint:** Customer-reported defect. Similar lifecycle to NCR but with customer communication requirements.

---

## The Reference_Architecture Package

Lives at `c:\Dev\sf-quality\Reference_Architecture\` in the workspace root repo (sf-quality). This is the single source of truth for architectural patterns. **Never copy into child repos** — distill relevant patterns into phase CONTEXT files instead.

```
Reference_Architecture/
├── README.md                          ← Index and folder structure
├── Execution_Plan.md                  ← 46 patterns → GSD phases (THE operational document)
├── Pattern_Mapping.md                 ← 46-pattern gap audit against current implementation
├── REVIEW.md                          ← Gap analysis of the package itself (all 10 items RESOLVED)
│
├── Specs/                             ← Platform-agnostic JSON specifications (source material)
│   ├── Platform_System_Architecture_Technical_Patterns.json   (~49 KB)
│   ├── Security_Role_Architecture_Agnostic.json               (~61 KB)
│   ├── Workflow_Engine_Architecture_Agnostic.json             (~48 KB)
│   └── API_Integration_Architecture_Agnostic.json             (~53 KB)
│
├── Briefings/
│   ├── architectural_briefing.md      ← Narrative for Security + Workflow specs only
│   └── Agent_Orientation_Revised.md  ← Primary agent orientation: stack, constraints, per-repo guidance
│
└── Hidden_Patterns/
    ├── Hidden_Architecture_Patterns_Reverse_Engineered.json   ← 3 reverse-engineered patterns
    ├── REFINEMENT_PROMPT.md           ← Self-contained prompt used to stress-test Hidden Patterns
    ├── CODEBASE_REFERENCE.md          ← ★ Actual DDL + SP signatures + phase build specs (read this)
    └── HANDOFF_CONTEXT.md             ← This file
```

**Critical read for implementation work:** `Hidden_Patterns/CODEBASE_REFERENCE.md` contains the actual DDL (verbatim from migration files) for every table you will touch in Phases 25, 27, 30, and 32. It includes current column lists, constraint names, SP signatures, guard type registry, idempotency patterns, and exact schema changes each phase must make. Read it before designing any migration.

**What the Execution Plan covers:**
- `sf-quality-db` v3.0 milestone: Phases 25-33 (after v2.0 completes with Phases 23-24)
- `sf-quality-api`: Insert Phase 3.5 + expand Phases 4, 7, 9, 10
- `sf-quality-app`: 6 new requirements + context enrichment
- Dependency graph, parallelization tracks, manifest refresh protocol, verification checkpoints

---

## The Three Hidden Patterns (Critical Context)

The `Hidden_Architecture_Patterns_Reverse_Engineered.json` contains three patterns reverse-engineered from Ceridian Dayforce's API surface. These are inferences, not documentation. They drive some of the most novel work in the execution plan. Read them carefully — they are the source of the architectural decisions documented below.

### Pattern 1: Guided Process Orchestration
A conductor that bundles multiple forms/steps into a sequenced experience, each with its own workflow, with per-step state tracking and an overall completion lifecycle (saga coordinator pattern). The reference platform uses this for new-hire onboarding (8+ forms). We use this pattern for multi-step quality processes.

### Pattern 2: Policy Resolution Engine
A generalized resolution mechanism: given overlapping candidate policies, select the single effective policy for an entity as of a given date, using effective dating + scope matching + priority ranking. The reference platform uses this for pay policies, time entry policies, password policies, etc. We use this for CAPA SLA timelines, inspection frequencies, escalation rules.

### Pattern 3: Data Staging and Edit Mode Architecture
A transactional staging layer where submitted data exists separately from committed data until a workflow Process node fires. Supports two commit modes: **Approved** (post-approval commit, pessimistic) and **Presave** (pre-approval commit, optimistic). The reference platform uses this for all HR data changes. We use this for containment actions (presave — safety-critical, must be visible immediately) and formal quality decisions (approved — must not be real until reviewed).

---

## What Was Done in the Previous Session

### 1. Reference_Architecture package cleanup (all committed)
- Fixed stale file path in Pattern_Mapping.md v4 revision history
- Updated Pattern_Mapping.md constraint reference from `Agent_Orientation_Combined.md` → `Agent_Orientation_Revised.md`
- Deleted `Briefings/Agent_Orientation_Combined.md` (strict subset of Revised, no unique value)
- Updated README.md to remove Combined references, fix Appendix A count (8→12)
- Added scope note to `architectural_briefing.md` "Database Architecture Patterns Implied" section flagging multi-tenant and EAV patterns as non-applicable
- Updated REVIEW.md summary table with RESOLVED status for all 10 items

### 2. Hidden Patterns stress-test
A refinement prompt (`REFINEMENT_PROMPT.md`) was run through a separate AI acting as Principal Enterprise Systems Architect. The output was a detailed review validating inferences, identifying blind spots, resolving open questions, and proposing concrete T-SQL architecture. Key findings are summarized in the "Architectural Decisions" section below.

---

## Architectural Decisions Made This Session

These decisions resolve open questions from the Hidden Patterns document and its review. They are **confirmed** — do not re-open them without strong reason.

### Decision 1: Phase 25 scope — do NOT build a full guided process framework yet

The refinement review proposed `workflow.GuidedProcessDefinition`, `GuidedProcessInstance`, `GuidedProcessStepInstance` as a full generic orchestration framework.

**Decision:** Phase 25 stays scoped to surgical 8D enhancements. The full guided process table framework (Definition/Instance/StepInstance) is deferred. Rationale: single-tenant system where the guided process pattern applies to ~6 process types, not hundreds. The framework should be built when it serves multiple process types simultaneously, not before.

**What Phase 25 DOES incorporate from the review:**
- **7-state step enum** (expanded from the planned 5): `NotStarted`, `InProgress`, `Submitted`, `PendingApproval`, `Committed`, `Skipped`, `ReturnedForChanges` — rename `Complete` → `Committed` to align with staging pattern vocabulary
- **Definition versioning pinned to instances:** add `DefinitionVersion INT` to `rca.EightDReport` so in-flight investigations pin their step configuration (prevents mid-investigation definition changes from corrupting in-progress work)
- **Note in Phase 25 CONTEXT** that `GuidedProcessDefinition` tables are the natural extension point when a second guided process type is added

### Decision 2: Phase 27 staging — do NOT build a staging schema

The refinement review proposed a `staging.Transaction` + `staging.TransactionField` schema as a generic form-submission staging layer.

**Decision:** Keep `workflow.PendingApprovalTransition` as the staging mechanism. The stored procedures already know what they're committing — a generic JSON payload staging table adds complexity without reducing the stored procedure work.

**What Phase 27 DOES incorporate from the review:**
- Add `BaseEntityRowVersion BINARY(8) NULL` to `workflow.PendingApprovalTransition` — captures entity state at transition request time
- Add `BaseWorkflowStateId INT NULL` to `workflow.PendingApprovalTransition` — captures workflow state at request time
- At commit time, `workflow.usp_ApplyApprovedTransition` re-checks these before committing: if entity state has changed in an incompatible way since the transition was staged, fail with explicit conflict error rather than silently overwriting
- This gives 80% of concurrency protection with zero new schema complexity
- Full `staging.TransactionField` conflict detection is a genuine enhancement if/when concurrent edit modes on the same entity become a real use case

### Decision 3: 10 step states → 7 states for Phase 25

The review proposed 10 step states. Premature.

**Phase 25 ships with 7:**
1. `NotStarted` (0)
2. `InProgress` (1)
3. `Submitted` (2) — user completed their input, workflow has started
4. `PendingApproval` (3) — workflow is in an approval wait state
5. `Committed` (4) — workflow completed, data is real
6. `Skipped` (5) — explicitly bypassed with reason
7. `ReturnedForChanges` (6) — approval rejected, back to submitter

**Deferred:** `Withdrawn` (7), `Invalidated` (8), `Conflict` (9)

### Decision 4: Revised Hidden Patterns JSON was truncated

The refinement review produced analysis but the revised JSON was cut off mid-way. **No revised JSON exists yet.** The original `Hidden_Architecture_Patterns_Reverse_Engineered.json` remains the authoritative source. The review analysis (in the message history of the previous session) supplements it with validated inferences and implementation decisions. When GSD agents read phase CONTEXT files, they should reference *both*.

---

## The Guided Process Landscape — Full Picture

**This is a significant gap in the current Execution Plan.** The plan only references 8D when describing the guided process pattern (Pattern 1). But sf-quality has at least six multi-step processes that fit the guided process pattern:

| Process | Steps (summary) | Notes |
|---------|----------------|-------|
| **NCR Lifecycle** | Report → Containment → Disposition → Investigation → Corrective Actions → Customer Notification → Effectiveness → Closure | The core entity. Its lifecycle IS the primary guided process. |
| **8D Investigation** | D1 Team → D2 Problem → D3 Containment → D4 Root Cause → D5 Corrective Actions → D6 Verification → D7 Prevention → D8 Closure | Spawned by NCR. Per-step AIAG dependency chain (D4 must precede D5 approval, etc.). |
| **CAPA Lifecycle** | Initiation → RCA → Action Plan → Implementation → Effectiveness Verification → Closure | SLA-governed. Can share RCA with 8D or be independent. |
| **SCAR** | Issue → Supplier RCA + Action Plan → Customer Review → Implementation Verification → Closure | Multi-party: customer side and supplier side each have independent deliverables. |
| **Audit Management** | Schedule → Opening Meeting → Conduct → Document Findings → Issue CARs → Response Review → Close | Findings link to CAPAs. |
| **Customer Complaint** | Receipt → Acknowledgment → Containment → Investigation → Customer Response → Closure | Customer-facing. May spawn NCR/CAPA. |

### Implications for the guided process framework design

Any table structure for guided processes must serve all six, not just 8D. Key cross-process requirements:

1. **Step output collections, not single forms** — D3 Containment, D5 Corrective Actions, SCAR actions, CAPA actions are all *collections* of records with owners and due dates, not single-form submissions. The step model needs to accommodate one-to-many children, not just one payload per step.

2. **Cross-process linking** — An NCR can spawn an 8D AND a CAPA. An 8D's D4 root cause may inform a CAPA's RCA. The data model needs cross-process references without circular dependencies.

3. **Dependency enforcement varies by process** — AIAG 8D has strict approval dependencies (D4→D5). NCR lifecycle has soft gating (containment should precede disposition but doesn't block it). SCAR has party-based gating (customer side must complete before supplier side can close). The framework must support configurable gating, not hardcoded rules.

4. **SLA layering** — Per-step SLA (containment within 24h, D5 within 30 days) AND overall process SLA (8D close within customer-specified timeline, CAPA close by severity). These are independent and can escalate independently.

5. **Multi-party coordination** — SCAR specifically has per-party state machines. The framework should be aware that "step completion" can mean "all parties for this step have submitted and been approved," not just "one user submitted."

6. **Audit identity per step** — For IATF compliance, each step needs to record who submitted, who approved, when, and what the prior state was. This is not optional.

---

## What Currently Exists in sf-quality-db (Relevant to These Patterns)

### Workflow engine (already implemented)
- `workflow.WorkflowProcess` — workflow definitions
- `workflow.WorkflowState` — states in the graph
- `workflow.WorkflowTransition` — transitions with guard expressions
- `workflow.ApprovalChain` / `workflow.ApprovalStep` / `workflow.ApprovalRecord` — approval infrastructure
- `workflow.PendingApprovalTransition` — pending approval state tracking (has `Expired` status, no timeout scheduler yet)
- `workflow.SlaConfiguration` — SLA timelines per workflow/state
- `workflow.usp_TransitionState` — executes state transitions
- `workflow.usp_ProcessApprovalStep` — processes approvals with SoD enforcement (error 50413)
- `workflow.usp_ApplyApprovedTransition` — applies approved transitions with stale-state protection

### 8D (exists, being enhanced in Phase 25)
- `rca.EightDReport` — parent investigation record
- `rca.EightDStep` — per-discipline record with `StepNumber` (1-8), currently has `IsComplete BIT`
  - **Phase 25 enhances this:** adds 7-state `StepStatus TINYINT`, `IsSkippable BIT`, `SkippedReason`, `SkippedByUserId`, `PrerequisiteStepNumber`, `DefinitionVersion INT`

### SCAR (exists, being enhanced in Phase 31)
- `quality.SupplierCar` — SCAR record with `IssuedById`, `VerifiedById`, `ClosedById`
  - **Phase 31 adds:** `CustomerResponseStatus TINYINT`, `SupplierResponseStatus TINYINT`, `quality.ScarPartyStatusHistory`

### NCR (fully implemented, not being changed for Phase 25)
- `quality.NonConformanceReport` — aggregate root
- `quality.NcrContainmentAction` — sub-resource collection
- Gate procedures: `quality.usp_CreateNcrQuick`, `quality.usp_SubmitNcr`, `quality.usp_CloseNcr`
- `workflow.PendingApprovalTransition` tracks pending approvals across all entity types

### Audit infrastructure
- `audit.AuditLog` — universal change audit
- `audit.ApiCallLog` — planned in Phase 29 (not yet implemented)
- Temporal tables with `HISTORY_RETENTION_PERIOD = 7 YEARS`

### Policy/SLA infrastructure
- `workflow.SlaConfiguration` — SLA timelines per state
- `dbo.CustomerQualityRule` — effective-dated, priority-ranked rules per customer (pattern for the policy resolution engine)
- `workflow.usp_EvaluateEscalationRules` — batch escalation processor

---

## The Execution Plan — Phase Sequence

**Prerequisite:** v2.0 (Phases 23-24) must complete first.

**DB v3.0 dependency graph:**
```
Phase 25 (Workflow Foundation / 8D Enhancement)
  ├→ Phase 26 (Auth/Approval Pipeline) → Phase 27 (Timeout/Presave)
  │                                         ├→ Phase 28 (Events/Notifications)
  │                                         └→ Phase 30 (SLA/Jobs)
  └→ Phase 32 (Validate-Only / Reference Data) [loose dependency]

Phase 29 (Audit/Temporal) ── INDEPENDENT — execute first (API 3.5 depends on it)
Phase 31 (SCAR Multi-Party) ── INDEPENDENT
Phase 33 (Data Lifecycle/Bulk) ── INDEPENDENT
```

**Cross-repo gates:**
- DB 29 → API 3.5 (audit.ApiCallLog must exist)
- DB 32 → API 7 (validate-only procs must exist)
- DB 28 → API 7+ (notification queue must exist)
- DB 31 → API 5 (SCAR party status must exist)

---

## Key Open Items For The Next Session

These are not decisions — they are things that still need work:

### 1. Update Execution_Plan.md Phase 25 description
Current Phase 25 description says 5 step states. Update to 7. Add `DefinitionVersion INT` on `rca.EightDReport`. Add note about the full GuidedProcessDefinition framework as a future extension point. Add the hybrid gating design decision (allow drafting, block approval by prerequisites, block closure by all-required-complete barrier).

### 2. Update Execution_Plan.md to acknowledge the full guided process landscape
Add a note in Section B1 (or a new subsection) that the guided process pattern applies to 6 process types in sf-quality, and that Phase 25's 8D enhancement is the first implementation. When a second process type adopts the pattern, the GuidedProcessDefinition framework becomes the right abstraction. List the 6 process types so future phases can reference them.

### 3. Update Phase 27 description
Current Phase 27 description does not include `BaseEntityRowVersion` or `BaseWorkflowStateId` on `PendingApprovalTransition`. Add these as explicit deliverables. Add commit-time conflict detection logic to `usp_ApplyApprovedTransition` as a named deliverable.

### 4. Update Pattern_Mapping.md entries that reference hidden patterns
Entries #2 (Workflow Orchestration), #14 (Validate-Only), #19 (Multi-Party Lifecycle), #20 (Optimistic Commit Mode) were enriched with hidden pattern context. These entries could be updated to reflect the validated inferences and confirmed decisions from the review. Specifically:
- Entry #2: add the 7-state enum and hybrid gating decision
- Entry #20: add the `BaseEntityRowVersion` concurrency protection decision and the "rescind, don't revert" compensation model
- Entry #19: add the barrier/join completion model for SCAR multi-party

### 5. Consider whether CAPA, Audit, and Complaint need guided process modeling in the Execution Plan
Currently only 8D gets explicit guided process treatment. CAPAs, Audits, and Customer Complaints are not in the v3.0 scope at all — they may be v4.0 or handled within existing phases. But the Execution Plan should at minimum note that these processes exist and will eventually follow the same pattern.

---

## Important Governance Rules

- **Never modify `sf-quality-db/`, `sf-quality-api/`, or `sf-quality-app/` from the workspace root context.** All Reference_Architecture work stays in `Reference_Architecture/`.
- **Never direct push to main.** Branch + PR for all commits. GitHub ruleset requires PRs + 3 CI checks.
- **Commit style:** conventional commits — `type(scope): description` (e.g., `docs(ref-arch): update phase 25 guided process decisions`)
- **File sizes:** README total is ~371 KB after Combined.md removal.

---

## Files Changed in Previous Session (Not Yet Committed)

```
deleted:    Reference_Architecture/Briefings/Agent_Orientation_Combined.md
modified:   Reference_Architecture/Briefings/architectural_briefing.md
modified:   Reference_Architecture/Pattern_Mapping.md
modified:   Reference_Architecture/README.md
modified:   Reference_Architecture/REVIEW.md
new file:   Reference_Architecture/Hidden_Patterns/REFINEMENT_PROMPT.md
new file:   Reference_Architecture/Hidden_Patterns/HANDOFF_CONTEXT.md
new file:   Reference_Architecture/Hidden_Patterns/CODEBASE_REFERENCE.md
```

These changes are local and need to be committed before switching contexts.
