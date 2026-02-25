# Quality Event Triage Layer — Architectural Spec

**Created:** 2026-02-25
**Status:** DRAFT — Pending domain owner review
**Scope:** Upstream quality event intake and routing that extends (not replaces) the existing NCR workflow engine

---

## 1. Problem Statement

The current system implements a 7-state NCR lifecycle (Draft → Open → Contained → Investigating → Dispositioned → Pending Verification → Closed) plus five other quality entity workflows (CAPA, CustomerComplaint, SupplierCAR, AuditFinding, EightDReport). This is correct for **confirmed nonconformances** that require formal resolution.

But floor reality in a coating operation is that most quality events start as **"hey, this doesn't look right"** — and forcing every one of those through a 7-state lifecycle creates two problems:

1. **Adoption barrier.** Operators coming from paper/whiteboards won't open a formal NCR for a suspect part or a trending parameter. The friction kills the data before it's born.
2. **Missing event classes.** CQI-12 requires documented reaction to process deviations, equipment/calibration events, and SPC signals — none of which are "nonconforming product" and none of which have a home in the current entity model.

Both independent research outputs (ChatGPT Deep Research and Parallel Forms structured analysis) converge on the same industry pattern: mature automotive coating operations use a **hybrid model** with lightweight upstream intake that routes into formal workflows by signal strength, not by assumption that everything is an NCR.

## 2. Design Principles

1. **Extend, don't replace.** The NCR state engine, WorkflowProcess/State/Transition tables, StatusHistory, and usp_TransitionState are untouched. New workflows plug into the same infrastructure.
2. **Dead simple intake.** An operator on the floor needs to log an event in under 60 seconds. Minimal required fields. Classification happens downstream, not at point of capture.
3. **Signal strength drives routing.** Events escalate based on what they turn out to be, not what someone guessed at the start.
4. **Every record counts for trending.** Even events closed as "no action needed" feed accumulation logic. The closed observation that happens 15 times is the NCR you haven't written yet.
5. **CQI-12 audit trail.** Process deviations, calibration events, and monitoring frequency reversions are first-class records with their own lifecycles.

## 3. New Entity Types

Two new entity types extend the existing 6 in `dbo.EntityTypeRegistry`:

### 3.1 QualityAlert

**Purpose:** The "hey, this doesn't look right" record. Captures observations, weak signals, suspect product, and floor-level concerns before classification.

**Who creates it:** Anyone — operators, line leads, lab techs, supervisors. No role gate on creation.

**What it captures (minimal required fields):**
- Plant, production line (auto-populated from user context where possible)
- What was observed (free text, 500 chars — enough for "orange peel on rack 14 batch 2247")
- Alert source: Visual, Instrument, SPC Signal, Process Alarm, Customer Feedback, Other
- Shift (auto-populated)
- Reported by (auto-populated from session)

**What it captures (optional, added during review):**
- Part/lot affected
- Defect type (from existing `dbo.DefectType` hierarchy)
- Severity assessment
- Photos/attachments
- Equipment ID
- Linked process area

**Lifecycle (5 states + void):**

The lifecycle models the real floor decision chain: someone reports → someone confirms whether the problem is real and what it actually is → then based on what they confirmed, they decide what to do about it. The "what to do" decision splits on two axes: **familiarity** (have we seen this before?) and **severity** (how big is this?).

```
  ┌──────────────┐
  │    OPEN       │  ← Operator logs "something looks off"
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │ UNDER REVIEW  │  ← Supervisor evaluates: IS this a problem?
  └──────┬───────┘
         │
         ├──── No, it's not ──────────────────────────┐
         │                                             │
  ┌──────▼───────┐                              ┌──────▼───────┐
  │  CONFIRMED   │  ← Yes, problem is real.     │   CLOSED     │
  │              │     What is it? How bad?      │ (Not a       │
  └──────┬───────┘     (DefectType, Severity,    │  defect)     │
         │              Familiarity assessed)     └──────────────┘
         │
         ├─── Known + Minor ──────────────────────┐
         │                                         │
         ├─── Known + Major ───────┐        ┌──────▼───────┐
         │                         │        │  RESOLVED    │
         ├─── Unknown ─────┐       │        │ (handled     │
         │                 │       │        │  in place)   │
         │          ┌──────▼───────▼──┐     └──────────────┘
         │          │   ESCALATED     │
         │          │ (→ NCR or       │
         │          │   ProcDev)      │
         │          └─────────────────┘
         │
  ┌──────▼───────┐
  │   VOIDED     │  (available from Open, Under Review, or Confirmed)
  └──────────────┘
```

**The three exit paths from Confirmed reflect floor reality:**

1. **Resolved (Known + Minor):** "We've seen this before, it's 3 parts with orange peel, scrap them and move on." The supervisor records what they did (rework, scrap, use-as-is) directly on the alert. No NCR needed. This is the path that prevents the 7-state lifecycle from drowning the floor in paperwork for routine issues.

2. **Escalated — Known + Major:** "We've seen this before, but it's a whole rack / a whole shift / customer-visible. This needs formal containment and disposition." Creates an NCR. Because the defect is known, the NCR may skip investigation (via the existing severity guard on the NCR workflow).

3. **Escalated — Unknown:** "I've never seen this before" or "I don't know what caused this." Creates an NCR that requires full investigation. The unfamiliarity flag prevents the investigation skip guard from firing even if severity is rated Minor — because you can't skip investigating something you don't understand.

| State | Code | Type | Description |
|-------|------|------|-------------|
| Open | `QA-OPEN` | Start | Alert logged, awaiting review |
| Under Review | `QA-REVIEW` | Normal | Supervisor/QE evaluating: is this actually a problem? |
| Confirmed | `QA-CONFIRMED` | Normal | Problem confirmed. Assessing familiarity and severity to determine path. |
| Closed | `QA-CLOSED` | Terminal | Reviewed and determined not to be a defect (record preserved for trending) |
| Resolved | `QA-RESOLVED` | Terminal | Confirmed defect handled in place — known issue, minor severity, quick disposition recorded |
| Escalated | `QA-ESCALATED` | Terminal | Promoted to NCR or Process Deviation for formal resolution |
| Voided | `QA-VOIDED` | Cancelled | Duplicate or error |

**Transitions:**

| # | From | To | Name | Role | Guard | Notes |
|---|------|----|------|------|-------|-------|
| 1 | Open | Under Review | Begin Review | None | None | Supervisor picks it up |
| 2 | Under Review | Closed | Close — Not a Defect | Quality Workflow Approver - Plant | None | False signal, boundary sample OK. Record kept for trending. |
| 3 | Under Review | Confirmed | Confirm Defect | Quality Workflow Approver - Plant | None | Reviewer populates DefectTypeId, SeverityRatingId, FamiliarityCode |
| 4 | Confirmed | Resolved | Resolve in Place | Quality Workflow Approver - Plant | `Severity IN (Minor, Observation) AND Familiarity = 'Known'` | Quick disposition: ResolutionActionCode + notes recorded on alert. No NCR created. |
| 5 | Confirmed | Escalated | Escalate to NCR | Quality Workflow Approver - Plant | None | Creates linked NCR in Draft. NCR inherits DefectTypeId, SeverityRatingId from alert. |
| 6 | Confirmed | Escalated | Escalate to Process Deviation | Quality Workflow Approver - Plant | None | Creates linked ProcDev in Open. Used when root cause is process, not product. |
| 7 | Open | Voided | Void Alert | Quality Workflow Approver - Plant | None | Duplicate/error |
| 8 | Under Review | Voided | Void Alert | Quality Authority - Enterprise (Full) | None | Late-discovered duplicate |
| 9 | Confirmed | Voided | Void Alert | Quality Authority - Enterprise (Full) | None | Confirmed in error |
| 10 | Open | Confirmed | Direct Confirm | Quality Authority - Enterprise (Full) | None | Skip review for obvious defects (manager authority) |
| 11 | Confirmed | Under Review | Reclassify | Quality Workflow Coordinator | None | Confirmation was wrong, need to reassess |

**Key design choices:**

- **"Confirmed" is the decision gate.** The reviewer commits to what the defect IS (DefectType) and how bad it is (Severity) before choosing a path. This means every confirmed quality event has a normalized defect classification — even the ones resolved in place without an NCR.

- **"Resolved" is NOT a lesser "Closed."** Closed means "this wasn't a defect." Resolved means "this WAS a defect, we handled it, here's what we did." Both are terminal, but they mean completely different things for trending and metrics. Resolved alerts count as confirmed defects. Closed alerts count as false signals.

- **The guard on "Resolve in Place" enforces the boundary.** Only Known + Minor defects can be resolved without an NCR. If the supervisor tries to resolve a Major or Unknown defect in place, the system blocks it and requires escalation. This is the governance boundary between "floor handles it" and "quality system handles it."

- **Escalation carries context.** When an alert escalates to NCR, the NCR inherits DefectTypeId, SeverityRatingId, and FamiliarityCode from the alert. If FamiliarityCode = 'Unknown', the NCR's severity skip guard (transition #7 in the NCR workflow: "Skip Investigation (Minor)") is blocked — you cannot skip investigating something you haven't seen before, even if you initially rate it Minor.

- **The accumulation engine counts Confirmed + Resolved alerts, not just Closed ones.** Three resolved "orange peel" alerts in 30 days means the quick-fix approach isn't working — the accumulation rule fires and creates an NCR to force root cause investigation.

- **"Escalated" is still a terminal state on the QualityAlert.** The spawned entity (NCR, ProcDev) takes over. The link is captured in `quality.QualityEventLink` (already exists in migration 033). The QualityAlert record persists forever for trending.

### 3.2 ProcessDeviation

**Purpose:** A process parameter left validated limits, but product conformance is uncertain. This is the CQI-12 "reaction plan triggered" record. It is NOT an NCR — it may or may not produce nonconforming product.

**Who creates it:** Lab techs, operators (via process alarm), supervisors, or auto-escalated from a QualityAlert.

**What it captures (minimal required fields):**
- Plant, production line
- Deviation type: Chemistry Excursion, Temperature Excursion, Equipment Parameter, SPC Out-of-Control, Monitoring Frequency Reversion, Calibration/Pyrometry, Other
- Parameter name and spec limits (what was the target?)
- Actual value or condition observed
- Time window of deviation (start time, end time or ongoing)
- Reported by

**What it captures (added during assessment):**
- Affected lot/batch scope (parts processed during deviation window)
- Estimated quantity at risk
- Reaction plan reference (from control plan)
- Product risk assessment: Confirmed OK, Suspect (Hold), Confirmed Nonconforming
- Equipment ID
- Containment actions taken

**Lifecycle (5 states + void):**

```
  ┌──────────────┐
  │     OPEN     │  ← Deviation detected/logged
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │  ASSESSING   │  ← Determining product impact scope
  └──────┬───────┘
         │
         ├─────────────────────────────────┐
         │                                 │
  ┌──────▼───────┐                  ┌──────▼───────┐
  │ CONTAINED    │                  │ CLOSED       │
  │ (product     │                  │ (no product  │
  │  held)       │                  │  impact)     │
  └──────┬───────┘                  └──────────────┘
         │
         ├──────────────────┐
         │                  │
  ┌──────▼───────┐   ┌─────▼──────┐
  │ CLOSED       │   │ ESCALATED  │
  │ (product     │   │ (→ NCR)    │
  │  released)   │   │            │
  └──────────────┘   └────────────┘
```

| State | Code | Type | Description |
|-------|------|------|-------------|
| Open | `PD-OPEN` | Start | Deviation detected, not yet assessed |
| Assessing | `PD-ASSESS` | Normal | Evaluating product impact and scope |
| Contained | `PD-CONTAINED` | Normal | Suspect product quarantined, reaction plan active |
| Closed | `PD-CLOSED` | Terminal | Deviation resolved — product released or no product impact |
| Escalated | `PD-ESCALATED` | Terminal | Confirmed nonconforming product found → NCR created |
| Voided | `PD-VOIDED` | Cancelled | False alarm or duplicate |

**Transitions:**

| # | From | To | Name | Role | Guard | SLA | Notes |
|---|------|----|------|------|-------|-----|-------|
| 1 | Open | Assessing | Begin Assessment | None | None | 4hr (StateEntry) | CQI-12 expects prompt reaction |
| 2 | Assessing | Contained | Quarantine Product | None | None | — | Product held pending verification |
| 3 | Assessing | Closed | Close — No Product Impact | Quality Workflow Coordinator | None | — | Parameter corrected, product verified OK |
| 4 | Contained | Closed | Release Product | Quality Authority - Enterprise (Full) | None | — | Testing confirms product is conforming |
| 5 | Contained | Escalated | Escalate to NCR | Quality Workflow Coordinator | None | — | Testing confirms nonconformance → NCR |
| 6 | Open | Voided | Void Deviation | Quality Workflow Approver - Plant | None | — | False alarm |
| 7 | Assessing | Voided | Void Deviation | Quality Authority - Enterprise (Full) | None | — | Late-discovered false alarm |
| 8 | Contained | Assessing | Reassess Scope | Quality Workflow Coordinator | None | — | New information changes scope |

**Key design choice:** The 4-hour SLA on Open → Assessing is intentional. CQI-12 reaction plans expect prompt response to parameter deviations, and auditors will look for evidence of timely reaction. This is the audit trail that currently doesn't exist.

## 4. Accumulation Rules

This is the "death by a thousand cuts" defense. Both research outputs identify this as the #1 failure mode in coating quality systems — individually minor events that accumulate into major cost and customer risk.

### 4.1 Rule Structure

Accumulation rules are evaluated periodically (scheduled job) and on QualityAlert closure or resolution. **Resolved alerts count toward accumulation** — the fact that you quick-fixed something 3 times means the quick-fix approach isn't working. When a rule fires, it auto-creates a linked entity.

| Rule | Trigger Condition | Action |
|------|-------------------|--------|
| Repeat Alert → NCR | ≥ N QualityAlerts with same DefectTypeId at same PlantId within rolling M days where status is Resolved or Closed, where N and M are configurable (suggested default: 3 alerts in 30 days) | Auto-create NCR in Draft, linked to all triggering alerts. EscalationReason = 'AccumulationRule'. |
| Repeat ProcDev → CAPA | ≥ N ProcessDeviations with same DeviationType at same ProductionLineId within rolling M days (suggested default: 3 in 60 days) | Auto-create CAPA, linked to triggering deviations |
| Rework Rate Threshold | Rework disposition count / total NCR count at PlantId exceeds threshold in rolling window (suggested default: 15% in 90 days) | Auto-create QualityAlert flagged as "Systemic — Rework Rate" for management review |
| CQI-12 Monitoring Reversion | Any ProcessDeviation of type "Monitoring Frequency Reversion" | No auto-escalation, but flag on plant dashboard and include in CQI-12 audit report |

### 4.2 Implementation Approach

Accumulation rules do NOT require a new table. They fit naturally into the existing `workflow.EscalationRule` table (migration 051) which already has:
- `EntityType`, `ConditionExpression`, `ActionType`, `ActionConfig`
- Evaluation by the escalation engine scheduled process

The new entity types just need to be registered as valid targets in the escalation rule configuration.

## 5. How This Extends the Existing Schema

### 5.1 EntityTypeRegistry Additions

Two new rows in `dbo.EntityTypeRegistry`:

| EntityTypeCode | EntityTypeName | TableSchema | TableName | PrimaryKeyColumn |
|----------------|----------------|-------------|-----------|------------------|
| QualityAlert | Quality Alert | quality | QualityAlert | QualityAlertId |
| ProcessDeviation | Process Deviation | quality | ProcessDeviation | ProcessDeviationId |

### 5.2 StatusCode Additions

13 new rows continuing from the current max StatusCodeId (47):

| ID | Code | Name | EntityType | Category | IsFinal |
|----|------|------|------------|----------|---------|
| 48 | QA-OPEN | Open | QualityAlert | New | 0 |
| 49 | QA-REVIEW | Under Review | QualityAlert | Active | 0 |
| 50 | QA-CONFIRMED | Confirmed | QualityAlert | Active | 0 |
| 51 | QA-CLOSED | Closed | QualityAlert | Closed | 1 |
| 52 | QA-RESOLVED | Resolved | QualityAlert | Closed | 1 |
| 53 | QA-ESCALATED | Escalated | QualityAlert | Closed | 1 |
| 54 | QA-VOIDED | Voided | QualityAlert | Cancelled | 1 |
| 55 | PD-OPEN | Open | ProcessDeviation | New | 0 |
| 56 | PD-ASSESS | Assessing | ProcessDeviation | Active | 0 |
| 57 | PD-CONTAINED | Contained | ProcessDeviation | Active | 0 |
| 58 | PD-CLOSED | Closed | ProcessDeviation | Closed | 1 |
| 59 | PD-ESCALATED | Escalated | ProcessDeviation | Closed | 1 |
| 60 | PD-VOIDED | Voided | ProcessDeviation | Cancelled | 1 |

### 5.3 WorkflowProcess Additions

Two new rows continuing from current max WorkflowProcessId (6):

| ID | ProcessCode | ProcessName | EntityType |
|----|-------------|-------------|------------|
| 7 | QA | Quality Alert | QualityAlert |
| 8 | PD | Process Deviation | ProcessDeviation |

### 5.4 WorkflowState and WorkflowTransition

Seeded per the state tables and transition tables in Sections 3.1 and 3.2 above. All transitions run through the existing `workflow.usp_TransitionState` — no stored procedure changes needed because:
- Entity type dispatch already uses EntityTypeRegistry lookup
- StatusHistory is already polymorphic
- Guard evaluation is expression-based

### 5.5 Tables That Need EntityType Constraint Updates

The following tables reference EntityType and will need their FK or CHECK constraints updated to include `QualityAlert` and `ProcessDeviation`. Migration 055 already converted most of these from CHECK constraints to FK references against `dbo.EntityTypeRegistry`, so in most cases this is just adding rows to the registry (5.1 above).

Tables to verify:
- `dbo.StatusCode` (EntityType column — FK to EntityTypeRegistry)
- `workflow.StatusHistory` (EntityType column — FK to EntityTypeRegistry)
- `dbo.ActionItem` (ParentEntityType — FK to EntityTypeRegistry)
- `dbo.EntityFollower` (EntityType — FK to EntityTypeRegistry)
- `workflow.EscalationRule` (EntityType)
- `workflow.EscalationLog` (EntityType)
- `workflow.ApprovalRecord` (EntityType)
- `quality.QualityEventLink` (FromEntityType, ToEntityType)

## 6. Entity Table Designs

### 6.1 quality.QualityAlert

```
quality.QualityAlert (
    QualityAlertId       INT IDENTITY(1,1) PK,
    AlertNumber          NVARCHAR(50) UNIQUE,          -- Auto-generated: QA-{Plant}-{YYYYMMDD}-{SEQ}
    PlantId              INT FK NOT NULL,
    StatusCodeId         INT FK NOT NULL,              -- Current state
    ProductionLineId     INT FK NULL,
    EquipmentId          INT FK NULL,
    ShiftId              INT FK NULL,
    PartId               INT FK NULL,
    CustomerId           INT FK NULL,
    LotNumber            NVARCHAR(50) NULL,

    -- Core observation (the "60-second capture")
    AlertSourceCode      NVARCHAR(30) NOT NULL,        -- Visual, Instrument, SPCSignal, ProcessAlarm, CustomerFeedback, Other
    Description          NVARCHAR(500) NOT NULL,        -- What was observed
    QuantityAffected     INT NULL,

    -- Populated at Under Review → Confirmed transition
    DefectTypeId         INT FK NULL,                  -- What IS it (from dbo.DefectType taxonomy)
    SeverityRatingId     INT FK NULL,                  -- How bad is it (Minor, Moderate, Major, Critical)
    FamiliarityCode      NVARCHAR(20) NULL,            -- 'Known' or 'Unknown' — have we seen this before?
    ConfirmedById        INT FK NULL,                  -- Who confirmed the defect
    ConfirmedDate        DATETIME2(0) NULL,            -- When it was confirmed
    ConfirmationNotes    NVARCHAR(1000) NULL,          -- What the reviewer observed/determined

    -- Populated at Confirmed → Resolved transition (quick disposition for Known + Minor)
    ResolutionActionCode NVARCHAR(30) NULL,            -- Scrap, Rework, UseAsIs, Adjusted, Contained
    ResolutionNotes      NVARCHAR(500) NULL,           -- What was done
    QuantityRejected     INT NULL,                     -- How many scrapped/reworked
    ResolvedById         INT FK NULL,
    ResolvedDate         DATETIME2(0) NULL,

    -- Escalation tracking (populated at Confirmed → Escalated transition)
    EscalatedToEntityType NVARCHAR(30) NULL,           -- 'NCR' or 'ProcessDeviation'
    EscalatedToEntityId   INT NULL,                    -- ID of the spawned entity
    EscalationReason     NVARCHAR(30) NULL,            -- 'KnownMajor', 'Unknown', 'AccumulationRule'

    -- Accumulation flag
    AccumulationRuleId   INT FK NULL,                  -- If auto-created by accumulation rule

    -- GP-12 flag
    IsGp12Related        BIT NOT NULL DEFAULT 0,       -- Is this alert within an active GP-12 containment?

    -- Standard columns
    ReportedById         INT FK NOT NULL,
    ReportedDate         DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    DueDate              DATETIME2(0) NULL,
    CreatedBy            INT NULL,
    CreatedDate          DATETIME2(0) DEFAULT SYSUTCDATETIME(),
    ModifiedBy           INT NULL,
    ModifiedDate         DATETIME2(0) DEFAULT SYSUTCDATETIME(),

    -- Temporal
    ValidFrom            DATETIME2(0) GENERATED ALWAYS AS ROW START HIDDEN,
    ValidTo              DATETIME2(0) GENERATED ALWAYS AS ROW END HIDDEN,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
) WITH SYSTEM_VERSIONING
```

### 6.2 quality.ProcessDeviation

```
quality.ProcessDeviation (
    ProcessDeviationId   INT IDENTITY(1,1) PK,
    DeviationNumber      NVARCHAR(50) UNIQUE,          -- Auto-generated: PD-{Plant}-{YYYYMMDD}-{SEQ}
    PlantId              INT FK NOT NULL,
    StatusCodeId         INT FK NOT NULL,              -- Current state
    ProductionLineId     INT FK NULL,
    EquipmentId          INT FK NULL,
    ShiftId              INT FK NULL,

    -- Deviation details
    DeviationTypeCode    NVARCHAR(30) NOT NULL,        -- ChemistryExcursion, TemperatureExcursion,
                                                       -- EquipmentParameter, SPCOutOfControl,
                                                       -- MonitoringReversion, CalibrationPyrometry, Other
    ParameterName        NVARCHAR(100) NOT NULL,       -- "Bath pH", "Zone 2 Temp", "Film Thickness Cpk"
    SpecLimitLower       DECIMAL(12,4) NULL,
    SpecLimitUpper       DECIMAL(12,4) NULL,
    ControlLimitLower    DECIMAL(12,4) NULL,
    ControlLimitUpper    DECIMAL(12,4) NULL,
    ActualValue          NVARCHAR(100) NULL,            -- NVARCHAR to handle non-numeric ("Failed SAT")
    DeviationStartTime   DATETIME2(0) NOT NULL,
    DeviationEndTime     DATETIME2(0) NULL,            -- NULL = ongoing
    IsOngoing            AS (CASE WHEN DeviationEndTime IS NULL THEN 1 ELSE 0 END) PERSISTED,

    -- Product impact assessment
    ProductRiskAssessment NVARCHAR(30) NULL,            -- ConfirmedOK, Suspect, ConfirmedNC, NotAssessed
    AffectedLotNumbers   NVARCHAR(500) NULL,           -- Comma-delimited or structured
    EstimatedQuantityAtRisk INT NULL,
    ReactionPlanReference NVARCHAR(200) NULL,           -- Control plan reference
    ContainmentActions   NVARCHAR(1000) NULL,

    -- Escalation tracking
    EscalatedToEntityType NVARCHAR(30) NULL,
    EscalatedToEntityId   INT NULL,

    -- Source tracking
    SourceQualityAlertId INT FK NULL,                  -- If escalated from a QualityAlert
    AccumulationRuleId   INT FK NULL,                  -- If auto-created by accumulation rule

    -- Standard columns
    ReportedById         INT FK NOT NULL,
    ReportedDate         DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    DueDate              DATETIME2(0) NULL,
    CreatedBy            INT NULL,
    CreatedDate          DATETIME2(0) DEFAULT SYSUTCDATETIME(),
    ModifiedBy           INT NULL,
    ModifiedDate         DATETIME2(0) DEFAULT SYSUTCDATETIME(),

    -- Temporal
    ValidFrom            DATETIME2(0) GENERATED ALWAYS AS ROW START HIDDEN,
    ValidTo              DATETIME2(0) GENERATED ALWAYS AS ROW END HIDDEN,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
) WITH SYSTEM_VERSIONING
```

## 7. The Event Flow — End to End

Here's how the three tiers work together in practice:

### Scenario A: Operator spots orange peel (turns out to be nothing)
1. Operator opens QualityAlert: "Orange peel on rack 14, batch 2247" → **QA-OPEN**
2. Supervisor reviews against boundary samples → **QA-REVIEW**
3. Within spec, not a defect → **QA-CLOSED**
4. Record preserved for trending. If similar alerts accumulate in 30 days, the pattern is still visible even though each individual alert was a false signal.

### Scenario B1: Known + Minor defect (resolved in place)
1. Operator opens QualityAlert: "Orange peel on 3 parts, rack 14" → **QA-OPEN**
2. Supervisor reviews, sees the defect → **QA-REVIEW**
3. Supervisor confirms: DefectType = Orange Peel, Severity = Minor, Familiarity = Known → **QA-CONFIRMED**
4. Known + Minor guard passes. Supervisor records: ResolutionAction = Scrap, QuantityRejected = 3 → **QA-RESOLVED**
5. No NCR created. Three minutes total. But the resolved alert counts toward accumulation — if this happens 2 more times in 30 days, an NCR auto-fires.

### Scenario B2: Known + Major defect (escalated to NCR)
1. Operator opens QualityAlert: "Orange peel on entire batch 2247, ~40 parts" → **QA-OPEN**
2. Supervisor reviews, confirms the defect is real and widespread → **QA-REVIEW**
3. Supervisor confirms: DefectType = Orange Peel, Severity = Major, Familiarity = Known → **QA-CONFIRMED**
4. Major severity → "Resolve in Place" guard blocks. Supervisor escalates → **QA-ESCALATED**
5. NCR auto-created in **NCR-DRAFT**, inheriting DefectTypeId and SeverityRatingId from alert. Because defect is Known, the NCR's severity skip guard (transition #7) may allow bypassing Investigation if the root cause and fix are already understood.
6. NCR follows existing lifecycle. QualityEventLink connects the two.

### Scenario B3: Unknown defect (escalated to NCR with full investigation)
1. Operator opens QualityAlert: "Weird blistering pattern I've never seen, rack 14" → **QA-OPEN**
2. Supervisor reviews, doesn't recognize the failure mode → **QA-REVIEW**
3. Supervisor confirms: DefectType = Blistering, Severity = Minor, Familiarity = Unknown → **QA-CONFIRMED**
4. Unknown familiarity → "Resolve in Place" guard blocks (even though severity is Minor). Supervisor escalates, EscalationReason = 'Unknown' → **QA-ESCALATED**
5. NCR auto-created in **NCR-DRAFT**. The FamiliarityCode = 'Unknown' flag propagates to the NCR and **blocks the severity skip guard** — this NCR must go through full Investigation even though severity is Minor, because you can't skip investigating something you don't understand.
6. NCR follows full lifecycle including Investigation phase.

### Scenario C: Bath pH alarm fires
1. Lab tech opens ProcessDeviation: "E-coat bath pH 6.8, spec max 6.5" → **PD-OPEN**
2. QE begins assessment: what lots ran during excursion window? → **PD-ASSESS**
3. Product quarantined, reaction plan activated → **PD-CONTAINED**
4. Testing shows adhesion is fine, product released → **PD-CLOSED**

### Scenario D: Oven SAT failure with product impact
1. Operator opens ProcessDeviation: "Zone 2 SAT failed, 385°F vs 400°F spec" → **PD-OPEN**
2. QE assesses: 3 racks of parts ran during window → **PD-ASSESS**
3. Product quarantined → **PD-CONTAINED**
4. Solvent rub test fails on sample → **PD-ESCALATED** + NCR created
5. NCR follows full lifecycle for the affected product.

### Scenario E: Chronic low-level issue (accumulation)
1. QualityAlert #1: "Slight color shift on line 3" → Confirmed (Known, Minor) → **Resolved** — supervisor scraps 2 parts
2. QualityAlert #2 (8 days later): "Color drift on line 3 again" → Confirmed (Known, Minor) → **Resolved** — supervisor adjusts parameter
3. QualityAlert #3 (12 days later): "Color still drifting on line 3" → Confirmed (Known, Minor) → **Resolved** — supervisor scraps 4 parts
4. Accumulation rule fires: 3 Resolved alerts, same DefectType (Color), same Plant, within 30 days
5. NCR auto-created in **NCR-DRAFT**, EscalationReason = 'AccumulationRule', linked to all 3 alerts. Dashboard notification to QE.
6. The NCR forces formal investigation — the three quick-fix resolutions prove the root cause hasn't been addressed.

## 8. What This Does NOT Change

- **NCR state engine**: Untouched. All 11 transitions, guards, SLAs remain as-is.
- **CAPA, CustomerComplaint, SupplierCAR, AuditFinding, EightDReport**: Untouched.
- **usp_TransitionState**: No code changes needed (entity dispatch is already dynamic).
- **StatusHistory**: Already polymorphic, already handles new entity types.
- **QualityEventLink**: Already supports arbitrary entity-to-entity links.
- **Security model**: New entity types get RLS predicates via existing PlantId-based pattern.
- **Audit triggers**: Follow existing temporal + AuditLog pattern.

## 9. What This Gives You That You Don't Have Today

| Capability | Current State | With Triage Layer |
|------------|---------------|-------------------|
| Operator logs "something looks off" | No home in the system | QualityAlert — 60 seconds, minimal fields |
| Known minor defect handled without NCR paperwork | Doesn't happen — either ignored or forced into NCR | QualityAlert → Confirmed → Resolved in place. Defect recorded, disposition documented, no 7-state NCR overhead |
| Unknown or major defect gets full investigation | Only if someone decides to create an NCR | QualityAlert → Confirmed → Escalated to NCR. System enforces that Unknown defects cannot skip investigation |
| Process parameter deviation tracked | Not tracked unless someone writes an NCR | ProcessDeviation — dedicated workflow with CQI-12 audit trail |
| CQI-12 reaction plan evidence | Paper or nothing | ProcessDeviation with SLA, time-stamped state transitions |
| Chronic issue detection | Manual — someone has to notice | Accumulation rules auto-fire NCRs from resolved alerts that repeat |
| Auditor asks "show me your reaction to this bath excursion" | Scramble through paper logs | Pull ProcessDeviation record with full history |
| SPC signal → quality system linkage | Gap | QualityAlert with source=SPCSignal, or ProcessDeviation with type=SPCOutOfControl |
| Calibration/pyrometry failure tracking | Gap (CQI-12 requires this) | ProcessDeviation with type=CalibrationPyrometry |
| Trending of non-NCR events | Impossible — no data captured | QualityAlert records preserved — Resolved alerts count as confirmed defects for metrics, Closed alerts count as false signals |

## 10. Migration Sequence (Estimated)

When this spec is approved and moves to implementation in `sf-quality-db`:

1. Add EntityTypeRegistry rows for QualityAlert, ProcessDeviation
2. Add StatusCode rows (IDs 48-60)
3. Create `quality.QualityAlert` table with temporal versioning
4. Create `quality.ProcessDeviation` table with temporal versioning
5. Create audit triggers for both tables
6. Add WorkflowProcess rows (IDs 7-8)
7. Add WorkflowState rows mapping to StatusCode IDs 48-60
8. Add WorkflowTransition rows per Section 3.1 and 3.2
9. Add RLS predicates for both tables
10. Seed accumulation rules in EscalationRule
11. Add number sequence generation for AlertNumber and DeviationNumber

No changes to existing migrations. All additive.

## 11. Plant Forms Mapping — How Current Paper Forms Weave Into This Layer

The Organization Forms Reference for Plant 1 and Plant 2 reveals exactly how quality data enters the system today — on paper and spreadsheets. This section maps every form category to its home in the triage layer, showing what each form becomes in the digital system.

### 11.1 Form Category Summary

Analysis of the Plant 1 forms manifest (135 forms) and Plant 2 production forms (~80 forms) reveals these categories:

| Category | Plant 1 Count | Plant 2 Presence | Current Medium |
|----------|--------------|------------------|----------------|
| PROCESS CONTROL | ~10 (powder checklists, e-coat checklists, recipe params, temp logs) | ~15 (oven verification, paint kitchen temp, booth cleaning, TPM) | Daily paper/Excel logs |
| LAB / CHEMISTRY | ~12 (daily lab analysis, PB ratio, BASF process DB, chemical additions) | ~5 (paint mix info, batch verification, solvent usage) | Lab tech Excel sheets |
| DEFECT TRACKING | ~10 (per-customer defect tracking sheets) | Embedded in customer forms | Paper tally sheets |
| QUALITY INSPECTION | ~20 (per-customer inspection & test forms) | ~8 (per-customer inspection forms) | Paper at unload stations |
| GP-12 / CONTAINMENT | ~10 (per-customer GP-12 forms) | Per-customer | Paper, sometimes Excel |
| NCR / DISPOSITION | 3 (Out-of-Spec Reaction, Rejected Material Disposition, Crash Reports) | Hold tags, Rework tags | Paper tags + Excel logs |
| PRODUCTION TRACKING | ~8 (paint records, load/unload sheets) | ~12 (load sheets, production tracking, scheduling) | Paper/Excel |
| MAINTENANCE / PM | ~6 (filter change, cleaning logs, tank cleaning) | ~5 (TPM checklists, maintenance logs, rack burn-off) | Paper/Excel |

### 11.2 Critical Form-to-Entity Mapping

#### Forms That Become Quality Alerts

These are the paper forms where operators and inspectors currently record "something doesn't look right" — the exact data that has no home in the current digital system:

| Current Form | Plant | What It Captures | Digital Home |
|-------------|-------|------------------|-------------|
| **Defect Tracking Sheets** (per-customer: ABM, Warren, Polycon, JAC, AGS, Accurate, etc.) | 1 | Defects found at unload, tallied by type per shift | **QualityAlert** — each defect entry becomes an alert. Accumulation rules replace manual trending. |
| **E-Coat Defect Tracking** (8.2.1.3.1.7) | 1 | E-coat defects by type and count | **QualityAlert** with source=Visual, linked to customer/part |
| **Powder Defect Tracking Sheet** (8.2.1.3.1.5) | 1 | Powder defects by type and count | **QualityAlert** with source=Visual |
| **Part Fallout Log** (8.2.1.2.29) | 1 | Parts that fall off racks or are damaged in the e-coat tank | **QualityAlert** with source=ProcessAlarm (trap-point event per CQI-12) |
| **E-Coat Crash Reports** (Supervisor: 8.2.1.3.1.19, Tech: 8.2.1.3.1.20) | 1 | E-coat line crash events — equipment failure causing product/process impact | **QualityAlert** with immediate escalation path to ProcessDeviation or NCR |
| **Customer-specific Inspection Forms** (per customer, both plants) | 1 & 2 | Pass/fail inspection results at unload | Inspection Forms Module captures the pass; **QualityAlert** is the "fail" path |

**Key insight:** Today, defect tracking sheets are filled out on paper and only reviewed when someone decides to look. In the digital system, every defect entry logged on a tracking sheet becomes a QualityAlert record. The accumulation engine then does what humans currently can't — it watches for patterns across shifts, lines, and customers automatically.

#### Forms That Become Process Deviations

These are the forms where process parameters are recorded and where out-of-spec conditions are documented:

| Current Form | Plant | What It Captures | Digital Home |
|-------------|-------|------------------|-------------|
| **Out of Specification Reaction Form** (8.2.1.2.10) | 1 | E-coat parameter out of spec + reaction taken | **ProcessDeviation** — this form IS the ProcessDeviation entity. DeviationType=ChemistryExcursion or TemperatureExcursion |
| **Daily Temperature Check Log** (8.2.1.1.1) | 1 | Powder cure oven temperatures per shift | Normal readings → process monitoring data. Out-of-spec reading → **ProcessDeviation** auto-created |
| **E-coat Daily Temp Log** (8.2.1.2.26) | 1 | E-coat tank and oven temperatures | Same pattern — normal data is monitoring, excursion triggers ProcessDeviation |
| **Daily Lab Analysis Template** (8.2.1.2.11) | 1 | E-coat bath chemistry (pH, conductivity, solids, P/B ratio) | Normal readings → lab data. Out-of-range → **ProcessDeviation** with type=ChemistryExcursion |
| **Pre-Treat Daily Checklist** (8.2.1.2.2) | 1 | Pre-treatment stage parameters | Same pattern |
| **Oven Verification Log** (8.2.2.1.16) | 2 | Cure oven temperature verification | Same pattern — SAT/TUS failures → ProcessDeviation with type=CalibrationPyrometry |
| **Paint Kitchen Temp Log** (8.2.2.1.2) | 2 | Material storage temperatures | Excursion → ProcessDeviation with type=EquipmentParameter |
| **New Paint Batch Verification** (8.2.2.26) | 2 | Incoming paint batch acceptance testing | Failure → ProcessDeviation with type=ChemistryExcursion, or SupplierCAR if material-caused |
| **Metering Pump Control Sheet** (8.2.1.2.22) | 1 | Chemical metering pump settings and readings | Excursion → ProcessDeviation |
| **Amps Tracking** (8.2.1.2.15) | 1 | E-coat amperage over time | Trend outside control limits → ProcessDeviation with type=SPCOutOfControl |
| **Pigment Binder Ratio** (8.2.1.2.5) | 1 | P/B ratio tracking for e-coat bath | Out-of-spec ratio → ProcessDeviation with type=ChemistryExcursion |

**Key insight:** The "Out of Specification Reaction Form" (8.2.1.2.10) is the most direct validation of the ProcessDeviation entity. Your e-coat team already documents this workflow on paper — parameter deviation → reaction → product assessment. The digital ProcessDeviation entity formalizes exactly what that form does, with timestamps, SLAs, and linkage to affected lots.

#### Forms That Map to NCR / Disposition (Existing Entity)

| Current Form | Plant | What It Captures | Digital Home |
|-------------|-------|------------------|-------------|
| **Rejected Material Disposition Log** (8.2.1.2.28) | 1 | Rejected e-coat material with disposition decisions | **NCR** entity (already built) — this log IS the NCR lifecycle on paper |
| **Hold Tag** (8.2.2.12) | 2 | Physical tag on quarantined product | NCR status = NCR-CONTAINED. Hold tag is the physical manifestation of the containment state. |
| **Hold For Review** (8.2.2.13) | 2 | Product held pending quality review | QualityAlert → Under Review, OR NCR → Open (depending on signal strength) |
| **Rework - To Be Sanded** (8.2.2.15) | 2 | Product routed to sanding rework | NCR disposition = Rework, with rework type captured |
| **To Be Buffed** (8.2.2.16) | 2 | Product routed to buffing rework | NCR disposition = Rework |
| **Sanded - Ready For Paint** (8.2.2.10) | 2 | Product that has been sanded and is ready for recoat | NCR rework tracking — confirms rework step complete |

**Key insight:** Plant 2's physical tags (Hold, Rework, Sanded, Buffed) are the paper equivalent of NCR status transitions. The digital system replaces these tags with status states — but the system could still generate printable tags from the NCR record for the shop floor.

#### Forms That Map to GP-12 / Containment (Customer-Specific)

| Current Form | Plant | Customer | Digital Home |
|-------------|-------|----------|-------------|
| **Blank GP 12 Testing Form** (8.2.1.3.1.11) | 1 | General | Inspection Forms Module with GP-12 template flag |
| **GP12 Flow** (8.2.1.3.1.13) | 1 | General | Reference document — informs workflow configuration |
| **Needs GP12 Tags** (8.2.1.3.1.12) | 1 | General | NCR containment label with GP-12 flag |
| **Customer-specific GP-12 forms** (Presstran, Warren, JNM, Tiercon, JAC, Takumi, AGS, Toyotetsu) | 1 | Various | Customer-specific inspection templates within Inspection Forms Module, linked to containment workflow |
| **Hino Bumpers Inspection GP12 data sheet** (8.2.1.3.6.9) | 1 | AGS/Hino | Customer-specific GP-12 inspection linked to containment state |

**Key insight:** GP-12 (EPC) forms are customer-specific inspection templates that operate *during* a containment period. In the digital system, these map to the Inspection Forms Module (already spec'd) with a containment mode flag. A single GP-12 defect found should auto-create a QualityAlert that immediately escalates to NCR — matching the GM requirement that a single defect restarts the GP-12 exit clock.

### 11.3 The Two-Plant Contrast That Shapes the Design

Plant 1 and Plant 2 reveal fundamentally different form architectures that the triage layer must accommodate:

**Plant 1 (Powder + E-Coat)** — organized by **coating technology**, then by **customer** for inspection:
- 8.2.1.1 = Powder line process forms (technology-specific)
- 8.2.1.2 = E-coat line process forms (technology-specific)
- 8.2.1.3 = Inspection/testing organized by **customer** (~18 customer folders)
- Has explicit lab/chemistry forms (PB ratio, daily lab analysis, BASF process database)
- Has explicit reaction/disposition forms (Out of Spec Reaction, Rejected Material Disposition)

**Plant 2 (Liquid Spray)** — organized by **production line**, then by **customer** for inspection:
- 8.2.2.1 = Lines 101-103 shared forms (line-level operations)
- 8.2.2.2 = Line 102 specific forms (robotic spray, more automated)
- 8.2.2.3 = Customer-specific forms (Rollstamp, Mytox, Laval Tool, Metelix, KB Components, Polycon)
- Has physical status tags as forms (Hold Tag, Rework, Sanded, Buffed, etc.)
- Has paint mixing / batch verification forms (liquid-specific)
- Has solvent usage tracking (liquid-specific regulatory/EHS)

**What this means for the triage layer:**

1. **QualityAlert.AlertSourceCode needs to be broad enough** for both plants. Plant 1 operators report from inspection stations (Visual, Instrument). Plant 2 operators also report from line operations and rework stations. The current source codes (Visual, Instrument, SPCSignal, ProcessAlarm, CustomerFeedback, Other) cover both.

2. **ProcessDeviation.DeviationTypeCode needs technology-aware options.** "ChemistryExcursion" means bath pH/conductivity/PB ratio at Plant 1 (e-coat) but means paint viscosity/mix ratio/pot life at Plant 2 (liquid). The type code is technology-agnostic by design — the specifics (ParameterName, spec limits, actual values) make it concrete.

3. **Customer-specific inspection forms are the bridge between the Inspection Forms Module and the QualityAlert.** A failed inspection result (captured in the Forms Module) should auto-generate a QualityAlert. Customer-specific defect tracking consolidates into the same QualityAlert entity regardless of which customer folder the paper form came from.

4. **Plant 2's physical tags prove the NCR disposition model is right.** The physical tags (Hold, Rework, Sanded, Ready For Paint) are a 1:1 mapping to NCR containment states and disposition codes. The digital system should be able to generate printable versions of these tags.

### 11.4 Forms That Don't Map to the Triage Layer (But Do Map Elsewhere)

For completeness — these form categories are important but are not quality event intake. They map to other planned modules:

| Category | Example Forms | Maps To |
|----------|--------------|---------|
| PRODUCTION TRACKING | Load Sheets, Paint Records, Part Load Sheets, Production Reports | Production Run / Load Tracking module (not yet built — listed in architecture_snapshot.md discovery targets) |
| MAINTENANCE / PM | Filter Change Logs, Cleaning Schedules, Tank Cleaning Records, TPM Checklists, Rack Burn-Off Trackers | Maintenance / PM module (not yet built) |
| LAB / CHEMISTRY (routine) | Daily Lab Analysis (normal readings), PB Ratio tracking (normal), BASF Process Database | Lab Chemistry / Bath Analysis module (not yet built) — routine data feeds trend monitoring; excursions trigger ProcessDeviations |
| SHIPPING | Shipping forms (Plant 2: 8.2.2.4) | Shipping / logistics (out of scope for quality event triage) |
| SCHEDULING | Schedule Templates, Painter Schedules, Daily Painter Line Up | Production scheduling (out of scope) |

### 11.5 The Streamlining Story

Today across both plants, there are roughly **200+ paper/Excel forms** in active use. The triage layer doesn't replace all of them — it replaces the **quality event capture and routing** forms specifically:

| What Goes Away | What Replaces It |
|---------------|-----------------|
| Per-customer defect tracking sheets (10+ at Plant 1) | One QualityAlert entity, filtered by Customer |
| Out of Specification Reaction Form (paper) | ProcessDeviation entity with structured workflow |
| Rejected Material Disposition Log (Excel) | NCR entity with disposition workflow (already built) |
| E-Coat Crash Reports (separate Supervisor + Tech forms) | One QualityAlert with escalation to ProcessDeviation/NCR |
| Physical Hold / Rework / Sanded tags (Plant 2) | NCR status states + printable tags generated from records |
| GP-12 defect tallies (per customer, per program) | QualityAlert with GP-12 flag + auto-escalation on single defect |
| Manual trending of defect sheets ("anyone notice we're getting more orange peel?") | Accumulation engine auto-fires NCRs from patterns |

The process control forms (temperature logs, checklists, lab analysis) remain as **data capture** — but now they have a **trigger mechanism**. An out-of-spec reading on a daily temp log doesn't just get circled on paper anymore. It creates a ProcessDeviation with a 4-hour SLA, links to the affected lots, and forces a documented product risk assessment.

## 12. Validation Against Consolidated QSA Audit Findings

The _Consolidation folder contains dual-AI audit synthesis for Plants 1 and 2 (completed 2026-02-24). This section maps how the triage layer addresses gaps and entity proposals identified in that work.

### 12.1 Gaps the Triage Layer Directly Closes

| Gap ID | Gap Name | Severity | How Triage Layer Addresses It |
|--------|----------|----------|-------------------------------|
| **GAP-01** | No formal NCR system at either plant | CRITICAL | NCR already built. Triage layer provides the **missing intake pathway** — QualityAlert and ProcessDeviation are how floor events reach the NCR. Without this layer, the NCR system has no front door. |
| **GAP-21** | OOS → NCR auto-trigger | HIGH | ProcessDeviation entity + escalation transition (PD-CONTAINED → PD-ESCALATED) creates the auto-trigger pathway. Plant 1's Out-of-Spec Reaction Form (8.2.1.2.10) becomes a ProcessDeviation that can escalate to NCR when product impact is confirmed. ChatGPT finding C8 from Plant 1 audit ("OOS auto-trigger NCR") is directly implemented. |
| **GAP-23** | Inspection-to-NCR disconnect | CRITICAL | QualityAlert is the bridge. When an inspection finds a defect, it creates a QualityAlert. Supervisor escalates to NCR. This is the `POST /v1/inspection/{id}/escalate` endpoint the Plant 2 synthesis identified as "critical new endpoint." The triage layer IS the missing intake mechanism. |
| **GAP-22** | Post-paint rework black hole | CRITICAL | QualityAlert captures the initial defect that triggers rework. The NCR tracks the disposition (Rework). The PostPaintReworkEvent entity (proposed in Plant 2 synthesis) tracks the rework execution. The triage layer completes the first two legs of the defect→NCR→rework chain. |
| **GAP-26** | No spec limits on process parameters | HIGH | ProcessDeviation entity captures SpecLimitLower, SpecLimitUpper, ControlLimitLower, ControlLimitUpper, ActualValue. When the ProcessParameterReading entity (proposed in Plant 1 synthesis) is built, out-of-spec readings can auto-create ProcessDeviations. |

### 12.2 Gaps the Triage Layer Indirectly Supports

| Gap ID | Gap Name | Connection |
|--------|----------|------------|
| GAP-03 | Defect taxonomy fragmented | QualityAlert.DefectTypeId normalizes the 97 Plant 1 defect strings and 78 Plant 2 defect strings into the unified DefectType taxonomy. No more "orange peel" vs "Orange Peel" vs "OP" vs "O/P" across customer forms. |
| GAP-04 | No PPM/yield calculation | QualityAlerts with DefectType linkage + QuantityAffected provide numerator. Production run tracking (separate module) provides denominator. Triage layer captures data that was previously lost. |
| GAP-08 | Zero cost data | QualityAlert → NCR escalation gives every event an opportunity to capture EstimatedCost on the NCR. Process Deviations that don't escalate still document containment effort. |
| GAP-11 | No GP-12 exit gate | QualityAlert with GP-12 flag + single-defect auto-escalation rule implements the GM requirement that one defect restarts the GP-12 exit clock. |
| GAP-13 | Process params decoupled from quality | ProcessDeviation explicitly links process parameter excursions to product impact assessment. This is the coupling mechanism that currently doesn't exist. |

### 12.3 Entity Proposals Validated and Extended

The consolidated audit identified 15 Plant 1 entities and 12 Plant 2 entities. The triage layer entities (QualityAlert, ProcessDeviation) were **not in either audit's entity proposals** — they fill a gap the audits identified but didn't name:

> *"Inspection-to-NCR disconnect is the single most critical gap. Zero of 16 inspection forms reference NCR. Gate alarms are paper-only. No escalation mechanism exists."* — Plant 2 Synthesis, Finding #7

> *"No NCR system exists. The platform's NCR entity is a quantum leap from paper."* — Plant 1 Synthesis, Finding #1

The audits correctly identified that the NCR entity is built but has no intake pathway. The triage layer IS the intake pathway. Specifically:

- **QualityAlert** closes the gap between inspection forms and the NCR entity
- **ProcessDeviation** closes the gap between process control forms and the NCR entity
- **Accumulation rules** close the gap between chronic low-level defects and formal NCR creation

### 12.4 Cross-Plant Scoring Impact

The consolidation tracker shows overall readiness scores of 30/100 (Plant 1) and 25/100 (Plant 2), with NCR/Disposition scoring 15/100 and 10/100 respectively. The triage layer directly impacts these scores:

| Dimension | Current Consensus | Expected Impact |
|-----------|-------------------|-----------------|
| NCR/Disposition | 13 (avg) | QualityAlert → NCR escalation gives every plant an NCR intake pathway. Score should rise to 60+ once deployed with the existing NCR engine. |
| Defect Tracking | 31 (avg) | QualityAlert with DefectTypeId normalizes taxonomy. Accumulation engine replaces manual trending. Score target: 70+. |
| Process Control | 37 (avg) | ProcessDeviation with structured parameter capture, spec limits, and SLA replaces circled values on paper. CQI-12 compliant. Score target: 65+. |
| Traceability | 17 (avg) | QualityAlert→NCR link + ProcessDeviation→NCR link + QualityEventLink creates traceable chains where paper had breaks. Partial improvement — full traceability requires ProductionRun and LoadRecord entities. |

### 12.5 Audit Findings That Validate Specific Design Choices

| Design Choice in Triage Layer | Audit Evidence |
|-------------------------------|----------------|
| QualityAlert.AlertSourceCode includes "CustomerFeedback" | Plant 2 Finding #10: GP-12 exists for Tesla only — customer complaints need an intake pathway |
| ProcessDeviation.DeviationTypeCode includes "CalibrationPyrometry" | Plant 1 GAP-10: No calibration linkage. CQI-12 requires SAT/TUS failure tracking. |
| ProcessDeviation captures SpecLimitLower/Upper | Plant 2 GAP-26: Only 1 of 26+ parameters has documented spec limits. Digital system must enforce. ChatGPT Plant 1 finding C7: Specific spec limits extracted (Bath Temp 90-98°F, pH 5.2-6.0, Oven 380-415°F). |
| QualityAlert.DefectTypeId links to dbo.DefectType | Plant 1: 97 defect strings → 38 types. Plant 2: 78 strings → 46 types. Master taxonomy reconciled in DEFECT_TAXONOMY_MASTER.csv. |
| Accumulation rule: 3 alerts same DefectType in 30 days → NCR | ChatGPT Plant 1 finding C8: "OOS auto-trigger NCR when repeated." Plant 2 defect universality data: DIRT and SAG/RUN appear on all 11 customer form families — accumulation will catch chronic issues. |
| QualityAlert minimal required fields (plant, line, description, source) | Plant 1+2 consensus: Tablet-first, shift selector as global context. 53 Plant 1 forms → 12 templates. 84 Plant 2 forms → 17 templates. The triage layer follows the same simplification principle. |
| ProcessDeviation.ProductRiskAssessment (ConfirmedOK/Suspect/ConfirmedNC) | Plant 2 inspection pattern: count-based routing into Good/Buff/Repaint/Scrap buckets. The 3-option risk assessment mirrors this binary sorting but adds the "Suspect/Hold" middle state that paper skips. |
