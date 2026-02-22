# Hidden Architecture Patterns — Refinement Review

**Source:** Principal Enterprise Systems Architect review of `Hidden_Architecture_Patterns_Reverse_Engineered.json`
**Prompted by:** `Phase_Implementation/REFINEMENT_PROMPT.md`
**Revised JSON output:** `Hidden_Architecture_Patterns_Refined.json`
**Date:** 2026-02-22

---

## Pattern 1: Guided Process Orchestration — Review

### Inference Validation

**Inference: "Guided process is a separate orchestration layer above the workflow engine (saga coordinator)."**
*Partially agree.* The behavior absolutely looks like a two-tier system: a parent "bundle" tracking overall progress while each step runs its own workflow. That's the right mental model.

What's weak is the "separate engine" implication. It can still be implemented inside the same workflow runtime as a specialization/template:

- Likely true: guided process has its own definition lifecycle (Draft→Published), effective dating, ordering, skip flags, and it coordinates multiple child workflow executions.
- Not proven: that it is a distinct runtime "above" workflow. The "system-generated monitoring workflow" is just as plausibly a workflow definition generated into the same workflow tables and executed by the same engine, not a separate orchestrator service.

**Refined conclusion:** Treat it as a logical orchestration layer that may be physically implemented as generated workflow + coordination tables, not necessarily a wholly separate subsystem.

---

**Inference: "Each step has an independent state machine with at least 4 states (Not Started / In Progress / Completed / Skipped)."**
*Agree on the existence of per-step state, disagree that 4 states is enough.* The evidence ("forms completed", "forms skipped", monitoring history logging "submission and processing status") strongly implies a richer state model than the junior doc proposes.

A realistic per-step state model needs to separate:
- "User finished data entry" vs
- "Approval is pending" vs
- "Change is committed" vs
- "Returned for changes"

**Refined state set (7-state, practical):**
`0 NotStarted → 1 InProgress → 2 Submitted → 3 PendingApproval → 4 Committed`
plus `5 Skipped` and `6 ReturnedForChanges`.

That's materially better than a 4-state model because it matches how approvals actually behave and how "monitoring workflow history" would be populated.

---

**Inference: "Ordering is presentation order only; steps can be skipped without blocking subsequent steps."**
*Disagree.* The evidence cited is not strong enough to conclude "no enforcement." "Move up/down ordering" + "skippable per form" is exactly what wizards use when they do enforce progression. Also, the existence of "Completed (all forms processed)" implies a concept of "required forms" even if you can navigate ahead.

Most likely real behavior (and what you want for 8D):
- Navigation order can be flexible (you can view later steps early),
- but submission/commit gating is enforced:
  - You can't complete the guided process until required steps are committed or formally skipped.
  - You often can't submit step N if prerequisites aren't satisfied.

This matters because AIAG 8D is dependency-heavy (D5 without D4 is nonsense).

---

**Inference: "Modes (Read Only / Edit / New) control shared data context passed to all steps."**
*Mostly agree.* Mode at the bundle level strongly implies a shared context (either "create new root record" or "edit existing root record"). The one caveat: you can have mixed semantics inside "New" (step 1 creates root; step 2–N edit/extend it). But that still supports the "mode is global parameter" idea.

---

**Inference: "System-generated monitoring workflow subscribes to completion events from child workflows; it's a join/barrier."**
*Agree on the join/barrier concept; the "subscribe to domain events" mechanism is plausible but not proven.* It could also be implemented as:
- A row-per-step progress table updated synchronously at each child workflow terminal node, and the monitoring instance is simply driven by those updates; or
- Periodic evaluation (polling) of step states.

**Refined conclusion:** The barrier/join pattern is right. The event subscription detail is an implementation guess.

---

**Quality mapping: "8D Investigation as Guided Process."**
*Agree, but only if you enforce prerequisites and allow rework loops.* Real 8D is not a straight-through checklist. It has "returned for changes" and "blocked" realities you must model.

### Blind Spots Identified

1. **Rework loops are not optional.** Approvals reject/return steps. Your step model must explicitly represent "ReturnedForChanges" and allow resubmission without losing audit trail.

2. **Ownership and editing rules per step.** In practice: one "owner" (Quality Engineer) writes D4; cross-functional users contribute evidence; management approves. That needs step-level role gating and (sometimes) contributor roles.

3. **Step prerequisites are not just "order."** Some dependencies are hard ("D5 requires D4 committed"). Others are conditional ("D3 containment may be skippable only if no shipment occurred"). You need rule-based prerequisites, not just `StepNumber - 1`.

4. **Abandonment and stale instances.** Guided processes get started and left open for weeks. You need:
   - "Open but idle" tracking
   - Reminders/escalations
   - Explicit cancel/close behavior

5. **Configuration versioning.** If step definitions change, in-flight investigations must not break. Pinning a `DefinitionVersion` to the instance is mandatory.

6. **Monitoring visibility and audit.** The "monitoring workflow history" concept implies a user-readable progress log. Relying only on generic audit logs makes it harder to present "what happened" in a usable way.

### Open Questions Resolved

**Q: Can a non-skippable form block progression to the next form?**
For 8D (and quality workflows generally): yes, but block at the right boundary. Don't block "viewing" later steps; block these actions:
- Moving a step to Submitted/PendingApproval
- Marking the guided process instance Completed
- Closing the parent record (e.g., EightDReport Closed, NCR Closed)

This gives you a usable UI while still enforcing process integrity.

**Q: Is ordering only UI ordering or a hard dependency chain?**
Treat ordering as UI order; treat prerequisites as the enforcement mechanism. That's the clean design: order controls user experience; prerequisite rules control correctness.

### Deepened Quality Management Mapping

**Step-level deliverables and failure modes:**

| Step | Key Deliverables | Common Failures | Architectural Need |
|------|-----------------|-----------------|-------------------|
| D1 Team Formation | Team members, roles, containment owner, QE owner, plant, customer link | "Fake team" (names selected but no accountability); missing supplier participation for SCAR-driven 8D | Enforce `OwnerId` required before downstream steps can go `PendingApproval` |
| D2 Problem Description | Defect code, part number, lot/serial, where found, escape point, severity, photos/evidence | Incomplete traceability; missing "escape point" makes D3/D4 weak | Require minimum traceability fields before D3 can be submitted |
| D3 Containment Actions | Quarantine, sort instructions, stop-ship, customer notification trigger, containment verification | Containment created but not executed; needs immediate visibility | Support "presave/provisional" containment + separate approval trail |
| D4 Root Cause Analysis | 5-Why, Ishikawa, data evidence, root cause + escape cause, validation evidence | Jumping to corrective action without evidence; confusing symptom with cause | Enforce D4 cannot be committed unless evidence fields present and D3 committed/skipped |
| D5 Corrective Actions | Actions, owners, due dates, linked CAPA actions | Actions defined but not feasible; not linked to root cause | Require mapping to root cause categories; enforce at least one action |
| D6 Implementation & Verification | Implementation proof, verification results | "Implemented" checked without proof | Allow attachments and evidence references; enforce verification sign-off |
| D7 Prevent Recurrence | Systemic changes (PFMEA, control plan updates, training) | Treating D7 as duplicate of D5; missing document control updates | Integrate policy rules requiring specific doc updates |
| D8 Closure / Recognition | Closure statement, lessons learned | Irrelevant; often legitimately skippable | Skippable with reason + authorized skipper |

**Quality-specific edge cases you must handle:**

- **Customer-driven requirements:** Some customers require formal D3 notification within X hours; others require D4 submission before they accept containment. This is policy-driven gating (Pattern 2).
- **Multi-party investigations (SCAR):** Supplier provides D4/D5 content; customer approves. This is a guided process with party-specific pending states (Pattern 3 multi-party).
- **Regulatory retention:** 7-year history isn't "nice to have." You need immutable step history, not just current values.

### Single-Tenant Right-Sizing

| Decision | Action |
|----------|--------|
| Prerequisite enforcement | **Keep** |
| 7-state per-step tracking including `ReturnedForChanges` | **Keep** |
| `DefinitionVersion` pinned to the instance | **Keep** |
| Progress summary + progress history | **Keep** |
| Approval chains and SoD controls | **Keep** |
| Complex system-generated monitoring workflows | **Simplify** — compute progress from step status rows |
| "Published" lifecycle governance | **Simplify** — treat as "active version" |
| Tenant isolation complexity | **Drop** |
| Overly generic configurability | **Drop** |

---

## Pattern 2: Policy Resolution Engine — Review

### Inference Validation

**Inference: "One generalized resolution pattern exists across all policy types."**
*Partially agree.* The consistent API surface suggests shared conventions (XRefCode identifiers, effective dating, ContextDate), but that doesn't prove a single engine. Enterprise platforms often standardize data shape while still implementing resolution logic per domain.

What's sound: policy resolution is almost certainly effective-dated and conflict-resolving.
What's weak: assuming the same conflict strategy applies everywhere (priority vs specificity vs most recent).

**Refined conclusion:** There's a shared policy model (effective-dated assignments + identifiers), and domain-specific resolution rules that usually follow a small set of precedence patterns.

---

**Inference: "Resolution algorithm = candidates → scope filter → conflict resolution → single effective policy."**
*Agree, but it needs deterministic tie-breaking and a clear specificity model.*
Without explicit tie-breakers you get "policy flicker" (different results depending on query plan / data order).

**Minimum required tie-break order:**
1. Specificity score (more fields matched beats wildcard)
2. Priority (lower number wins — pick one convention and stick to it)
3. `EffectiveFrom` (most recent wins)
4. Stable ID (ascending) as a final deterministic tie-break

---

**Inference: "Policy is a container of rules; resolution chooses container; domain engine executes rules."**
*Agree.* That's exactly how real systems avoid exploding the policy matrix.

---

**Inference: "Policies assigned via hierarchy chain rather than directly."**
*Mostly agree.* But many systems allow both inherited policy (org/workcenter/customer) AND direct override at entity level ("exception" assignments). If you don't model exceptions, you'll end up hardcoding one-off logic later.

---

**Inference: "Raw → processed pipeline (raw punches to processed punches) is policy-driven transformation."**
*Agree.* It's a visible example of: raw input + resolved policy → deterministic transformation + rejected-but-preserved outputs.

### Blind Spots Identified

1. **Not all "policies" resolve to a single winner.** In quality, you'll have cases where rules are additive: notification recipients (multiple), escalation triggers (multiple), "required documents" set (multiple).

2. **Ambiguity management is missing.** You need a defined behavior when two policies tie: pick deterministic winner, log warning, or error out.

3. **Exception handling is missing.** "Customer rule override" or "plant override" must be explicit. Otherwise you'll bury it in procedural code.

4. **Policy version pinning vs live re-evaluation.** For compliance, you need to answer: "Which policy version was used when this NCR was submitted?" If you don't persist that, audits get ugly.

5. **Performance/indexing isn't mentioned.** Effective-dated precedence queries can be cheap or awful depending on indexes.

### Open Questions Resolved

**Q: Is a generalized policy engine overkill for quality?**
A generalized framework is justified; a generalized expression language rule engine is overkill.

Given your target stack already has `dbo.CustomerQualityRule` with effective dating and priority, you should standardize that pattern and reuse it. What you should NOT build:
- An arbitrary rule DSL
- A generic "any entity, any dimension" engine with dynamic SQL everywhere

Keep it narrow:
- A few policy tables with consistent columns
- A consistent resolution approach (specificity + priority + dates)
- Stored procedures that resolve and return one policy row (or a set, when additive)

This is exactly "right-sized."

### Deepened Quality Management Mapping

| Policy Type | Inputs | Output | Failure Modes |
|------------|--------|--------|---------------|
| Customer notification & approval rules | Customer, disposition, severity | SLA tier, approval required flag, concession required flag | Wrong SLA tier → late notification → customer escalation |
| CAPA timeline policy | Severity, customer, audit finding type, plant | Due dates (30/60/90), escalation schedule, effectiveness verification window | CAPA overdue because timeline was wrong or changed mid-stream |
| Inspection frequency / containment policy | Customer, part family, defect family, supplier, plant | Sample size, frequency, mandatory containment steps | Under-inspection → escapes; over-inspection → capacity waste |
| SCAR trigger policy | Repeat issue count, supplier score, defect severity | Trigger SCAR yes/no, response SLA, escalation path | SCAR not issued when required; supplier disputes unauditable thresholds |

### Single-Tenant Right-Sizing

| Decision | Action |
|----------|--------|
| Effective dating | **Keep** |
| Priority + specificity + deterministic tie-breaks | **Keep** |
| Auditability ("which policy was used?") | **Keep** |
| Tenant dimension | **Drop** |
| EAV / tenant-configurable schema | **Drop** |
| General-purpose rule DSL | **Drop** |

---

## Pattern 3: Data Staging and Edit Mode Architecture — Review

### Inference Validation

**Inference: "There is a separate transactional staging store for pending changes until workflow Process node commits."**
*Agree.* The evidence is strong and direct:
- Staged transaction XML exists because it "hasn't yet been committed"
- "Requester can't alter XML data"
- Validate-only mode exists across write endpoints

---

**Inference: "Presave vs Approved are two commit timing patterns."**
*Agree, with an important refinement:* presave is only safe if the committed record is clearly marked as provisional/pending approval. So presave must be: commit + pending flag + rejection handling (rescind/void, NOT silent rollback).

---

**Inference: "Edit modes enable partial entity staging; multiple pending changes can coexist on the same entity without conflict."**
*Partially agree.* Edit modes clearly support partial updates and distinct workflows. What's not proven is "multiple pending changes can coexist on the same entity without conflict." That requires either strict serialization or merge/conflict logic. Most systems do not allow free-for-all concurrent pending edits unless they built real conflict detection.

**Refined conclusion:** Partial staging is likely. Concurrent partial staging is plausible but requires explicit conflict strategy.

---

**Inference: "Multi-party staging supports per-party state tracking (I-9 pending employer/employee)."**
*Agree on the concept.* Can be implemented as one record with multiple party-specific status columns plus separate staged payload per party.

### Blind Spots Identified

1. **Conflict handling is missing (your #1 gap).** When pending approvals sit for days, the base entity changes. You must decide what happens.

2. **Re-validation at apply time.** Guard expressions and policy checks done at submission time may be invalid at approval time.

3. **Idempotency.** Approval apply procedures will be retried (API retries, user double-clicks). Apply must be safe to run twice.

4. **Staged data lifetime and audit retention.** If you discard staged payloads on rejection, you lose evidence of what was proposed. For regulated quality work, that's often unacceptable.

5. **Presave downstream side effects.** Once presaved data triggers actions (quarantine, line stop), you cannot "roll it back" like a database change.

### Open Questions Resolved

**Q: Concurrent staging conflicts (your explicit attention item)**

Scenario: User A stages containment edits; User B stages severity reclassification. Both go into approvals. A commits first and changes the entity state and/or fields that B's guards evaluated against.

**Correct answer: B must be revalidated at apply time, not trusted.** This is non-negotiable if approvals can take time.

Two checks required at apply time:

1. **State consistency check** — If the approval assumes the entity was in workflow state X when staged, but it's now in state Y, the approval may no longer be valid. Block apply and require resubmission.

2. **Data consistency check** — If the fields B intends to change have been modified since staging, block apply. If only unrelated fields changed, you can either still block (simplest, safest) or allow merge (only if you can prove no field overlap).

Your current workflow transition infrastructure is already moving in this direction by capturing base state and row version in `workflow.PendingApprovalTransition` (Phase 27 plan). Carry the same idea into data staging.

**Q: Presave compensation completeness (your explicit attention item)**

When a presave record is later rejected, do NOT attempt "revert to prior state" as the primary strategy. In quality operations, presaved actions can drive real-world behavior.

**Use rescind, don't revert:**
- Presave commits create records flagged as `Provisional` / `PendingApproval`
- Rejection changes them to `Rescinded` / `Invalidated` (never silent deletion)
- Rejection also creates required follow-up tasks (explicit human action) where physical rollback might be needed (e.g., "release quarantine" must be explicitly confirmed, not inferred)

This is the only approach that stays honest and audit-friendly.

### Deepened Quality Management Mapping

| Scenario | Pattern | Edge Cases | Architectural Needs |
|----------|---------|-----------|---------------------|
| NCR investigation staging | Pessimistic (approve → commit) | Long-running drafts; returned-for-changes loops; attachment updates | Staged payload retrievable exactly as proposed; apply must revalidate; history must show who proposed, who approved, what changed |
| Containment with immediate visibility | Presave (commit → approve) | Time-critical, incomplete info; containment may be escalated or superseded | `IsProvisional` flag lifecycle; "superseded by action X" linkage; explicit rescind workflow |
| SCAR cross-organizational | Multi-party | Supplier submits late; customer extends deadline; supplier disputes defect definition | Per-party status tracking; per-party staged payload; commit barrier = both sides accepted; audit trail per party |
| Edit modes (field-group workflows) | Partial entity staging | Severity reclassification affects SLA/notification rules | Change-set type specific validation; apply-time conflict checks; explicit "approval is stale" outcome |

### Single-Tenant Right-Sizing

| Decision | Action |
|----------|--------|
| Staging + immutable submitted payload | **Keep** |
| Validate-only execution path | **Keep** |
| Apply-time revalidation and conflict detection | **Keep — do NOT simplify away** |
| Audit retention of staged payloads | **Keep** |
| Rescind vs revert for presave | **Keep — do NOT simplify away** |
| Concurrency handling | **Keep — single-tenant needs this equally** |
| Tenant partitioning keys | **Drop** |

---

## Cross-Pattern Synthesis — Review

### Interaction Model Gaps

What the current pipeline sketch misses:

1. **Correlation and traceability objects.** You need a durable link between: guided process instance → step instance → staged change-set/transaction payload → approval chain/records → final committed change.

2. **When policy resolution happens and whether it's pinned.** If you resolve policies at submission time but apply at approval time, you have drift.

3. **Apply-time revalidation and stale-approval handling.** "Approval granted" must not equal "apply is safe."

4. **Side effect management.** Notifications, escalations, tasks, customer comms must be consistent and not double-fired on retry.

5. **Partial completion.** Abandoned guided process and "returned for changes" are not exceptional; they are normal.

### Failure Propagation Analysis

**Guided process layer:**
- Step never submitted → process stays Open; SLA reminders/escalations fire
- Step skipped improperly → closure guard must block parent closure
- User abandons mid-way → SLA escalation triggers reminders/escalations

**Staging layer:**
- Validation fails → step stays InProgress; nothing goes to approval
- Staging submission succeeds but approval creation fails → must roll back staging submission transaction (atomicity)
- Apply fails due to conflict → step moves to ReturnedForChanges with conflict reason

**Policy resolution failure:**
- No matching policy → fall back to default or hard error depending on domain (for customer notification SLA, default is acceptable; for customer approval required, hard error is safer)
- Ambiguous match → deterministic winner + logged warning, OR reject as misconfiguration for high-stakes policies

**Workflow/approval failure:**
- No approval steps configured → hard error (already treated as 50415-style)
- Timeout/expired → step remains blocked; escalation rule fires; may allow auto-approve only if explicitly configured

**Commit failure:**
- Concurrency conflict → block apply; do NOT partially update
- Constraint violation → reject apply; return for changes with concrete error

### Compensation and Rollback Flows

| Scenario | Compensation |
|----------|-------------|
| Approved-mode staging rejection | Discard staged payload + mark step ReturnedForChanges; preserve proposed payload + decision trail for audit |
| Presave-mode rejection | Mark provisional record Rescinded/Superseded; create explicit follow-up tasks; never automatic rollback |
| State transition — stale approval | Block apply; compensation is "resubmit the intended transition under current state" (rescind, don't revert) |

### Concurrency and Conflict Resolution

Pick one strategy and implement consistently:

**Strategy A (safe + simple): Strict serialization per entity**
- Only one pending change-set of any kind per entity allowed
- Any other attempt returns conflict
- Simplest to reason about, but reduces throughput

**Strategy B (safe + usable): Field-group concurrency**
- Allow multiple pending change-sets if they target different field groups (Severity vs Containment)
- Apply-time conflict rules:
  - If targeted fields changed since staging → block apply
  - If unrelated fields changed → allow apply
- Requires that each change-set records base values for targeted fields (not just rowversion)

Given the "severity vs containment" example, Strategy B is worth it only if you implement overlap detection cleanly. Otherwise, use Strategy A and accept the limitation.

### Partial Completion Scenarios

**Guided process abandoned:**
- Track `LastActivityAt`
- Escalate via SLA rules
- Allow explicit Cancel with reason (preserve history)

**Policy changes while staging is in progress:**
- At apply time, re-resolve policies and revalidate
- If result differs materially (e.g., now customer approval required), block apply and require resubmission

**Definition changes while staging is in progress:**
- Pin `DefinitionVersion` to the instance at creation
- Never "hot-swap" step definitions on an in-flight report

---

## New Inferences

1. **"Validate-only" is a first-class execution path, not a convenience flag.** If Dayforce exposes validate-only on every write endpoint, that implies validations are implemented in a reusable pipeline that can run without committing. Mirror that pattern in stored procedures from the start, not as a bolt-on.

2. **Immutability of submitted payload implies copy-on-write rework.** "Returned-for-changes" isn't "edit the submitted transaction." It's "create a new transaction based on prior, with a link to the prior." Essential for audit.

3. **Monitoring workflow history implies "human-readable progress log," not just raw audit records.** Systems that succeed operationally provide progress narratives ("D3 submitted by X; approved by Y; returned by Z"). Generic audit logs alone won't serve this need.

4. **The system is designed to tolerate partial completion indefinitely.** "Effective dating," "published," and "monitoring status" all imply long-lived processes with midstream changes and governance. That's exactly the quality domain.

---

## Revised Quality Management Architecture Recommendations

Everything below fits the non-negotiables: business logic in T-SQL, single tenant, Azure SQL + App Service, strongly typed model, no message broker, no EF. All recommendations align with existing infrastructure in sf-quality-db.

### 1. Guided Process Orchestration for 8D

The existing `rca.EightDStep.IsComplete BIT` is insufficient. Phase 25 must upgrade to a 7-state step model.

**Prerequisite enforcement at submission boundary (not navigation boundary):**

In `rca.usp_UpdateEightDStepStatus` (planned), enforce: if `PrerequisiteStepNumber IS NOT NULL`, then prerequisite must be `StepStatus = 4` (Committed) before allowing `Submitted (2)`, `PendingApproval (3)`, or `Committed (4)`. Allow `InProgress (1)` regardless — so users can draft ahead, but block submit.

**"Skipped" as a controlled act:**

For `StepStatus = 5 (Skipped)` require:
- `IsSkippable = 1`
- `SkippedReason IS NOT NULL`
- `SkippedByUserId IS NOT NULL` (enforce permission/role)

**Closure guard on parent workflow:**

Closing an `EightDReport` must be blocked unless all required steps (`IsSkippable = 0`) are committed. Implement as a `GuardType = 'EightDAllRequiredStepsCommitted'` on the close transition — consistent with existing CASE-based guard dispatch in `usp_TransitionState`.

```sql
-- Guard logic:
-- COUNT of required steps where StepStatus != 4 and not skipped must be zero
```

### 2. Data Staging for Quality Entity Edit Modes

`workflow.PendingApprovalTransition` solves approval-gated state transitions. It does NOT solve data change approvals (containment edit, severity reclassification). A new staging table is needed.

**New table: `workflow.PendingEntityChangeSet`**

```sql
CREATE TABLE workflow.PendingEntityChangeSet (
    PendingChangeSetId      INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_PendingEntityChangeSet PRIMARY KEY CLUSTERED,
    EntityType              NVARCHAR(30)    NOT NULL,
    EntityId                INT             NOT NULL,
    PlantId                 INT             NOT NULL
        CONSTRAINT FK_PendingEntityChangeSet_Plant REFERENCES dbo.Plant(PlantId),
    ChangeSetTypeCode       NVARCHAR(50)    NOT NULL,
        -- e.g.: NCR_ContainmentEdit, NCR_SeverityEdit, EightDStep_Submission, SCAR_CustomerSideEdit
    RequestedByUserId       INT             NOT NULL
        CONSTRAINT FK_PendingEntityChangeSet_RequestedBy REFERENCES dbo.AppUser(AppUserId),
    RequestedDate           DATETIME2(0)    NOT NULL
        CONSTRAINT DF_PendingEntityChangeSet_RequestedDate DEFAULT SYSUTCDATETIME(),
    Status                  NVARCHAR(20)    NOT NULL
        CONSTRAINT CK_PendingEntityChangeSet_Status
            CHECK (Status IN (N'Pending', N'Approved', N'Applied', N'Rejected', N'Cancelled', N'Expired')),
    ApprovalChainId         INT             NOT NULL
        CONSTRAINT FK_PendingEntityChangeSet_ApprovalChain
            REFERENCES workflow.ApprovalChain(ApprovalChainId),
    PayloadJson             NVARCHAR(MAX)   NOT NULL,   -- immutable staged payload
    BaseEntityRowVersion    BINARY(8)       NULL,       -- captured at request time
    BaseStatusCodeId        INT             NULL,       -- optional: entity state at request time
    ExpiresAt               DATETIME2(0)    NULL,
    CompletedDate           DATETIME2(0)    NULL,
    CompletedByUserId       INT             NULL
        CONSTRAINT FK_PendingEntityChangeSet_CompletedBy REFERENCES dbo.AppUser(AppUserId),
    CorrelationId           UNIQUEIDENTIFIER NOT NULL
        CONSTRAINT DF_PendingEntityChangeSet_CorrelationId DEFAULT NEWID(),
    IsActive                BIT             NOT NULL
        CONSTRAINT DF_PendingEntityChangeSet_IsActive DEFAULT 1,
    CreatedBy               INT             NULL,
    CreatedDate             DATETIME2(0)    NOT NULL
        CONSTRAINT DF_PendingEntityChangeSet_CreatedDate DEFAULT SYSUTCDATETIME(),
    ModifiedBy              INT             NULL,
    ModifiedDate            DATETIME2(0)    NULL
);

-- Filtered unique index: one active Pending change-set per entity + type
CREATE UNIQUE INDEX UX_PendingEntityChangeSet_OneActive
    ON workflow.PendingEntityChangeSet (EntityType, EntityId, ChangeSetTypeCode)
    WHERE Status = N'Pending' AND IsActive = 1;

-- Index for expiration processing
CREATE NONCLUSTERED INDEX IX_PendingEntityChangeSet_StatusExpiry
    ON workflow.PendingEntityChangeSet (Status, ExpiresAt)
    WHERE Status = N'Pending';
```

**Link approval records to change-sets:**

Add `PendingChangeSetId INT NULL FK → workflow.PendingEntityChangeSet` to `workflow.ApprovalRecord`. Change-set approvals then create `ApprovalRecord` rows exactly like transitions do — reusing the existing SoD enforcement in `usp_ProcessApprovalStep`.

**Apply-time conflict detection:**

At apply time in `workflow.usp_ApplyApprovedChangeSet`:
1. **Stale state check:** if `BaseStatusCodeId` was captured and current `StatusCodeId` differs → block apply
2. **Conflict check:** if `BaseEntityRowVersion` differs from current → block apply (or implement base-field overlap checks for specific `ChangeSetTypeCode` values that need parallel edit support)

**Presave containment pattern:**

```sql
-- Containment action committed immediately with provisional flag
IsProvisional BIT NOT NULL DEFAULT 1

-- Approval rejection marks it Rescinded (never silent delete)
-- Rejection triggers a follow-up task for explicit human action
```

### 3. Policy Resolution

`dbo.CustomerQualityRule` already implements the pattern correctly. Standardize it into resolver stored procedures so no duplicate query logic exists.

**Recommended resolver procedure:**

```sql
CREATE OR ALTER PROCEDURE dbo.usp_ResolveCustomerQualityRule
    @PlantId            INT,
    @CustomerId         INT,
    @DispositionCodeId  INT  = NULL,
    @SeverityRating     INT  = NULL,
    @AsOfDate           DATE = NULL      -- defaults to CAST(SYSUTCDATETIME() AS DATE)
AS
BEGIN
    SET NOCOUNT ON;
    IF @AsOfDate IS NULL SET @AsOfDate = CAST(SYSUTCDATETIME() AS DATE);

    SELECT TOP 1 *
    FROM dbo.CustomerQualityRule
    WHERE PlantId = @PlantId
      AND CustomerId = @CustomerId
      AND (DispositionCodeId = @DispositionCodeId OR DispositionCodeId IS NULL)
      AND (@SeverityRating IS NULL
           OR (MinSeverityForRule IS NULL AND MaxSeverityForRule IS NULL)
           OR (@SeverityRating BETWEEN MinSeverityForRule AND MaxSeverityForRule))
      AND IsActive = 1
      AND EffectiveFrom <= @AsOfDate
      AND (EffectiveTo IS NULL OR EffectiveTo >= @AsOfDate)
    ORDER BY
        CASE WHEN DispositionCodeId IS NOT NULL THEN 0 ELSE 1 END, -- specific before wildcard
        RulePriority ASC,                                            -- lower wins
        EffectiveFrom DESC,                                          -- most recent
        CustomerQualityRuleId ASC;                                   -- stable tie-break
END
```

**Pin applied policy on key transactions:**

When an NCR is submitted or customer notification is triggered, store:
- `AppliedCustomerQualityRuleId INT NULL`
- `AppliedRuleEvaluatedAtUtc DATETIME2(0) NULL`

This prevents audit ambiguity when policies change after the fact.

### 4. SLA + Expiration + Validate-Only

Extend existing Phase 30 and Phase 32 plans to cover change-sets:

**Phase 30 — Expiration processor handles both transitions and change-sets:**
```sql
-- workflow.usp_ProcessSlaExpirations should handle:
-- 1. PendingApprovalTransition where Status = 'Pending' and now > ExpiresAt
-- 2. PendingEntityChangeSet where Status = 'Pending' and now > ExpiresAt
-- Then call workflow.usp_EvaluateEscalationRules for both
```

**Phase 32 — Validate-only variants for change-set operations:**
```sql
-- Per high-impact edit mode:
quality.usp_ValidateNcrSeverityEdit(@CallerAzureOid, @NcrId, @NewSeverityRatingId)
quality.usp_ValidateNcrContainmentEdit(@CallerAzureOid, @NcrId, ...)
rca.usp_ValidateEightDStepSubmission(@CallerAzureOid, @EightDStepId, @NewStatus)
-- Each runs: permission checks, prerequisite checks, policy resolution checks
-- Returns: IsValid BIT, ErrorCode INT NULL, ErrorMessage NVARCHAR(500) NULL
-- Does NOT stage and does NOT commit
```

---

## Confirmed Architectural Decisions (from this review)

These decisions were made in the session that produced this review. Do not re-open without strong reason.

| Decision | Summary |
|----------|---------|
| **Phase 25 scope** | Do NOT build a full guided process framework. Stay scoped to surgical 8D enhancements. Framework is the right abstraction when a second process type is added. |
| **Phase 27 staging** | Keep `workflow.PendingApprovalTransition` as the staging mechanism. Add `BaseEntityRowVersion` + `BaseWorkflowStateId` for conflict detection. No new staging schema. |
| **7-state step enum** | `NotStarted (0)`, `InProgress (1)`, `Submitted (2)`, `PendingApproval (3)`, `Committed (4)`, `Skipped (5)`, `ReturnedForChanges (6)`. Deferred: `Withdrawn`, `Invalidated`, `Conflict`. |
| **Rescind not revert** | All presave/provisional compensation uses Rescinded/Superseded status + follow-up tasks. Never silent rollback. |
| **Policy engine scope** | No rule DSL. Typed resolver procs over typed policy tables. `dbo.CustomerQualityRule` pattern is the template. |
