# sf-quality-db Codebase Reference

**Purpose:** Self-contained reference document for an AI working on hidden pattern implementation phases (25, 27, 30, 32) in `sf-quality-db`. This file contains the **exact current DDL** extracted from migration files so you can reason about what exists, what must change, and what constraints you must honor — without needing codebase access.

**Companion to:** `HANDOFF_CONTEXT.md` (architectural decisions, persona, governance)

---

## 1. Migration Conventions

All migrations live in `sf-quality-db/database/migrations/` and are numbered sequentially. The current count is 133 migrations (migrations 001–133 deployed).

### Naming pattern
```
NNN_descriptive_name.sql
```
Examples: `037_eightd_tables.sql`, `097_create_pending_transition_lifecycle.sql`, `104_add_customer_quality_rules.sql`

### Idempotency pattern (mandatory — every migration must be re-runnable)

**Tables:** `IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = N'...' AND schema_id = SCHEMA_ID(N'...'))`

**Stored procedures:** `CREATE OR ALTER PROCEDURE`

**Constraints/Indexes (added after CREATE):**
```sql
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = N'FK_...')
    ALTER TABLE ... ADD CONSTRAINT FK_... FOREIGN KEY ...

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_...' AND object_id = OBJECT_ID(N'...'))
    CREATE NONCLUSTERED INDEX IX_... ON ...
```

**Seed data:** `MERGE ... ON ... WHEN NOT MATCHED THEN INSERT` (never plain INSERT)

**Object existence check for table-wide DDL:**
```sql
IF OBJECT_ID(N'dbo.TableName', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.TableName (...)
END
```

### Constraint naming convention (INFRA-12)

| Prefix | Usage |
|--------|-------|
| `PK_TableName` | Primary key |
| `FK_TableName_ReferencedTable` | Foreign key |
| `UQ_TableName_ColumnOrDesc` | Unique constraint |
| `CK_TableName_ColumnOrDesc` | Check constraint |
| `DF_TableName_ColumnName` | Default constraint |
| `IX_TableName_ColumnOrDesc` | Nonclustered index |

### Temporal table pattern (system-versioned, 7-year retention)

History table created **first**, in the `audit` schema, with clustered columnstore index. Then current table with HIDDEN period columns.

```sql
-- Step 1: History table (audit schema)
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = N'FooHistory' AND schema_id = SCHEMA_ID(N'audit'))
BEGIN
    CREATE TABLE audit.FooHistory (
        FooId       INT NOT NULL,
        -- all columns matching dbo.Foo EXACTLY (no IDENTITY, no constraints, no defaults)
        ValidFrom   DATETIME2(0) NOT NULL,
        ValidTo     DATETIME2(0) NOT NULL
    );
    CREATE CLUSTERED COLUMNSTORE INDEX IX_FooHistory ON audit.FooHistory;
END
GO

-- Step 2: Current table (with temporal versioning)
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = N'Foo' AND schema_id = SCHEMA_ID(N'dbo'))
BEGIN
    CREATE TABLE dbo.Foo (
        FooId       INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Foo PRIMARY KEY CLUSTERED,
        -- ... columns ...
        CreatedBy   INT NULL,
        CreatedDate DATETIME2(0) NOT NULL CONSTRAINT DF_Foo_CreatedDate DEFAULT SYSUTCDATETIME(),
        ModifiedBy  INT NULL,
        ModifiedDate DATETIME2(0) NULL,
        ValidFrom   DATETIME2(0) GENERATED ALWAYS AS ROW START HIDDEN
                    CONSTRAINT DF_Foo_ValidFrom DEFAULT SYSUTCDATETIME(),
        ValidTo     DATETIME2(0) GENERATED ALWAYS AS ROW END HIDDEN
                    CONSTRAINT DF_Foo_ValidTo DEFAULT CONVERT(DATETIME2(0), '9999-12-31 23:59:59'),
        PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
    )
    WITH (SYSTEM_VERSIONING = ON (
        HISTORY_TABLE = audit.FooHistory,
        HISTORY_RETENTION_PERIOD = 7 YEARS
    ));
END
GO
```

---

## 2. Database Schemas

| Schema | Purpose |
|--------|---------|
| `dbo` | Core reference data, users, plants, lookups |
| `quality` | Quality domain entities (NCR, CAPA, SCAR, Complaint, AuditFinding) |
| `rca` | Root cause analysis domain (EightDReport, EightDStep) |
| `workflow` | Workflow engine: state machine, transitions, approvals, pending transitions |
| `audit` | History tables for temporal versioning + ApiCallLog |
| `security` | Permission/policy engine (RolePermission, usp_EvaluatePolicy, usp_CheckPermission) |
| `knowledge` | Knowledge base views (Phase 21, read-only) |

---

## 3. Entity Type Registry

The system uses string-based `EntityType` tokens across workflow, escalation, and approval tables. These tokens are the canonical identifiers for all guided processes.

**Current registered entity types (from constraint `CK_EscalationRule_EntityType` and `usp_TransitionState` dispatch CASE):**

| EntityType Token | Domain Table | Schema |
|-----------------|--------------|--------|
| `N'NCR'` | `quality.NonConformanceReport` | quality |
| `N'CAPA'` | `quality.CorrectiveAction` | quality |
| `N'Complaint'` | `quality.CustomerComplaint` | quality |
| `N'SCAR'` | `quality.SupplierCar` | quality |
| `N'AuditFinding'` | `quality.AuditFinding` | quality |
| `N'EightDReport'` | `rca.EightDReport` | rca |

**Note:** When adding new entity types to the system, CHECK constraints on `EscalationRule`, `EscalationLog`, `ApprovalRecord`, and the CASE dispatch in `usp_TransitionState` and `usp_ProcessApprovalStep` must all be updated.

---

## 4. Key Table DDL — Current State

### 4.1 rca.EightDReport (temporal, system-versioned)

Created in `037_eightd_tables.sql`.

```sql
CREATE TABLE rca.EightDReport (
    EightDReportId          INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_EightDReport PRIMARY KEY CLUSTERED,
    ReportNumber            NVARCHAR(30)    NOT NULL
        CONSTRAINT UQ_EightDReport_ReportNumber UNIQUE,
    CorrectiveActionId      INT             NOT NULL
        CONSTRAINT FK_EightDReport_CorrectiveAction
            REFERENCES quality.CorrectiveAction(CorrectiveActionId),
    CustomerComplaintId     INT             NOT NULL
        CONSTRAINT FK_EightDReport_CustomerComplaint
            REFERENCES quality.CustomerComplaint(CustomerComplaintId),
    PlantId                 INT             NOT NULL
        CONSTRAINT FK_EightDReport_Plant REFERENCES dbo.Plant(PlantId),
    StatusCodeId            INT             NOT NULL
        CONSTRAINT FK_EightDReport_StatusCode REFERENCES dbo.StatusCode(StatusCodeId),
    Title                   NVARCHAR(200)   NOT NULL,
    SubmittedToCustomerDate DATETIME2(0)    NULL,
    CustomerResponseDate    DATETIME2(0)    NULL,
    IsCustomerAccepted      BIT             NULL,
    ClosedById              INT             NULL
        CONSTRAINT FK_EightDReport_ClosedBy REFERENCES dbo.AppUser(AppUserId),
    ClosedDate              DATETIME2(0)    NULL,
    CreatedById             INT             NOT NULL
        CONSTRAINT FK_EightDReport_CreatedBy REFERENCES dbo.AppUser(AppUserId),
    CreatedDate             DATETIME2(0)    NOT NULL
        CONSTRAINT DF_EightDReport_CreatedDate DEFAULT SYSUTCDATETIME(),
    ModifiedBy              INT             NULL,
    ModifiedDate            DATETIME2(0)    NULL,
    -- Temporal columns (HIDDEN)
    ValidFrom               DATETIME2(0)    GENERATED ALWAYS AS ROW START HIDDEN ...,
    ValidTo                 DATETIME2(0)    GENERATED ALWAYS AS ROW END HIDDEN ...,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
)
WITH (SYSTEM_VERSIONING = ON (
    HISTORY_TABLE = audit.EightDReportHistory,
    HISTORY_RETENTION_PERIOD = 7 YEARS
));
```

**Phase 25 adds to `rca.EightDReport`:** `DefinitionVersion INT NOT NULL DEFAULT 1` — pins the step configuration version at investigation creation. This prevents mid-investigation changes to step definitions from corrupting in-progress work.

---

### 4.2 rca.EightDStep (NOT temporal — current state)

Created in `037_eightd_tables.sql`. **This is the primary table modified in Phase 25.**

```sql
CREATE TABLE rca.EightDStep (
    EightDStepId        INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_EightDStep PRIMARY KEY CLUSTERED,
    EightDReportId      INT NOT NULL
        CONSTRAINT FK_EightDStep_EightDReport
            REFERENCES rca.EightDReport(EightDReportId),
    DisciplineNumber    TINYINT NOT NULL
        CONSTRAINT CK_EightDStep_DisciplineNumber CHECK (DisciplineNumber BETWEEN 0 AND 8),
    DisciplineName      NVARCHAR(50) NOT NULL,
    OwnerId             INT NULL,
    TargetDate          DATE NULL,
    CompletionDate      DATE NULL,
    IsComplete          BIT NOT NULL
        CONSTRAINT DF_EightDStep_IsComplete DEFAULT 0,
    StepOutput          NVARCHAR(MAX) NULL,
    SortOrder           INT NOT NULL
        CONSTRAINT DF_EightDStep_SortOrder DEFAULT 0,
    CreatedBy           INT NULL, CreatedDate DATETIME2(0) NULL,
    ModifiedBy          INT NULL, ModifiedDate DATETIME2(0) NULL,
    CONSTRAINT UQ_EightDStep_ReportDiscipline UNIQUE (EightDReportId, DisciplineNumber)
);
```

**Phase 25 changes:** Migration replaces `IsComplete BIT` with a 7-state `StepStatus TINYINT` enum and adds prerequisite/skip columns. The exact migration adds these columns:

| Column to add | Type | Default | Notes |
|--------------|------|---------|-------|
| `StepStatus` | `TINYINT NOT NULL` | `DEFAULT 0` | Replaces `IsComplete`. 7 states: 0=NotStarted, 1=InProgress, 2=Submitted, 3=PendingApproval, 4=Committed, 5=Skipped, 6=ReturnedForChanges |
| `IsSkippable` | `BIT NOT NULL` | `DEFAULT 0` | Whether this discipline can be bypassed |
| `SkippedReason` | `NVARCHAR(500) NULL` | — | Required when Skipped |
| `SkippedByUserId` | `INT NULL` FK→`dbo.AppUser` | — | Who approved the skip |
| `PrerequisiteStepNumber` | `TINYINT NULL` | — | If non-null, this step cannot reach `PendingApproval` until its prerequisite is in state `Committed` |

**Note:** `IsComplete BIT` must be dropped (or deprecated by a computed column) in Phase 25. The 7-state enum replaces it entirely. `Committed` (value 4) maps to what `IsComplete = 1` meant. Backward compatibility: update any procs reading `IsComplete` to read `StepStatus = 4` instead.

---

### 4.3 workflow.WorkflowProcess (temporal)

Created in `046_workflow_state_machine.sql`. Defines the 6 lifecycle process types.

```sql
CREATE TABLE workflow.WorkflowProcess (
    WorkflowProcessId   INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_WorkflowProcess PRIMARY KEY CLUSTERED,
    ProcessCode         NVARCHAR(30) NOT NULL CONSTRAINT UQ_WorkflowProcess_ProcessCode UNIQUE,
    ProcessName         NVARCHAR(100) NOT NULL,
    EntityType          NVARCHAR(30) NOT NULL,   -- matches EntityType registry tokens above
    Description         NVARCHAR(500) NULL,
    IsActive            BIT NOT NULL CONSTRAINT DF_WorkflowProcess_IsActive DEFAULT 1,
    CreatedBy INT NULL, CreatedDate DATETIME2(0) NOT NULL ...,
    ModifiedBy INT NULL, ModifiedDate DATETIME2(0) NULL,
    -- Temporal (HIDDEN)
    ValidFrom DATETIME2(0) GENERATED ALWAYS AS ROW START HIDDEN ...,
    ValidTo   DATETIME2(0) GENERATED ALWAYS AS ROW END HIDDEN ...
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = audit.WorkflowProcessHistory, HISTORY_RETENTION_PERIOD = 7 YEARS));
```

---

### 4.4 workflow.WorkflowState (temporal)

Created in `046_workflow_state_machine.sql`. Maps StatusCode IDs into workflow positions.

```sql
CREATE TABLE workflow.WorkflowState (
    WorkflowStateId     INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_WorkflowState PRIMARY KEY CLUSTERED,
    WorkflowProcessId   INT NOT NULL CONSTRAINT FK_WorkflowState_Process
                            REFERENCES workflow.WorkflowProcess(WorkflowProcessId),
    StatusCodeId        INT NOT NULL CONSTRAINT FK_WorkflowState_StatusCode
                            REFERENCES dbo.StatusCode(StatusCodeId),
    StateType           NVARCHAR(15) NOT NULL
                        CONSTRAINT CK_WorkflowState_StateType
                            CHECK (StateType IN (N'Start', N'Normal', N'Terminal', N'Cancelled')),
    SortOrder           INT NOT NULL CONSTRAINT DF_WorkflowState_SortOrder DEFAULT 0,
    IsActive            BIT NOT NULL CONSTRAINT DF_WorkflowState_IsActive DEFAULT 1,
    -- Unique: one StatusCode per process
    CONSTRAINT UQ_WorkflowState_Process_StatusCode UNIQUE (WorkflowProcessId, StatusCodeId),
    -- Standard audit + temporal
    ...
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = audit.WorkflowStateHistory, HISTORY_RETENTION_PERIOD = 7 YEARS));
```

---

### 4.5 workflow.WorkflowTransition (temporal) — the state machine heart

Created in `046_workflow_state_machine.sql`. Defines valid From→To state pairs with guard expressions.

```sql
CREATE TABLE workflow.WorkflowTransition (
    WorkflowTransitionId INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_WorkflowTransition PRIMARY KEY CLUSTERED,
    WorkflowProcessId    INT NOT NULL CONSTRAINT FK_WorkflowTransition_Process
                             REFERENCES workflow.WorkflowProcess(WorkflowProcessId),
    FromStateId          INT NOT NULL CONSTRAINT FK_WorkflowTransition_FromState
                             REFERENCES workflow.WorkflowState(WorkflowStateId),
    ToStateId            INT NOT NULL CONSTRAINT FK_WorkflowTransition_ToState
                             REFERENCES workflow.WorkflowState(WorkflowStateId),
    TransitionName       NVARCHAR(100) NOT NULL,
    RequiredRoleId       INT NULL CONSTRAINT FK_WorkflowTransition_RequiredRole
                             REFERENCES dbo.[Role](RoleId),
    SlaHours             INT NULL,
    SlaBaselineType      NVARCHAR(15) NULL
                         CONSTRAINT CK_WorkflowTransition_SlaBaselineType
                             CHECK (SlaBaselineType IN (N'StateEntry', N'Creation')),
    GuardType            NVARCHAR(30) NULL,      -- see Guard Expression section below
    GuardExpression      NVARCHAR(500) NULL,
    ApprovalChainId      INT NULL,               -- FK→workflow.ApprovalChain (added post-creation)
    IsAutoFire           BIT NOT NULL CONSTRAINT DF_WorkflowTransition_IsAutoFire DEFAULT 0,
    SortOrder            INT NOT NULL CONSTRAINT DF_WorkflowTransition_SortOrder DEFAULT 0,
    IsActive             BIT NOT NULL CONSTRAINT DF_WorkflowTransition_IsActive DEFAULT 1,
    CONSTRAINT CK_WorkflowTransition_NoSelfTransition CHECK (FromStateId != ToStateId),
    -- Standard audit + temporal
    ...
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = audit.WorkflowTransitionHistory, HISTORY_RETENTION_PERIOD = 7 YEARS));
```

**Guard types in `GuardType`** (evaluated by `usp_TransitionState`):
| GuardType | What it checks |
|-----------|---------------|
| `N'SeveritySkip'` | NCR severity rating vs configurable threshold — allows lower-severity NCRs to skip a transition |
| `N'ChildEntityState'` | All child entities (action items / linked 8D / linked CAPA) are in closed/complete state |
| `N'Classification'` | Entity classification-dependent routing (AuditFinding severity: Major/Minor/OFI) |
| `N'RejectionCount'` | Number of rejections meets threshold — extracted from `GuardExpression` as `COUNT >= N` |
| `N'FastClose'` | NCR-specific: all disposition lines reconciled, no pending approvals, linked CAPA in advanced state |

**Guard enforcement:** CASE-based dispatch in `usp_TransitionState` — no dynamic SQL. Adding a new guard type requires both a new `ELSE IF @GuardType = N'...'` block AND a documented `GuardType` value.

**`RequiredPermissionId INT NULL`** — Added in migration 098. Not in original 046 DDL. The presence of this column enables the dual-path authorization (permission-first, role fallback) in `usp_TransitionState`.

---

### 4.6 workflow.ApprovalChain (temporal)

Created in `051_escalation_approval_tables.sql`.

```sql
CREATE TABLE workflow.ApprovalChain (
    ApprovalChainId     INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_ApprovalChain PRIMARY KEY CLUSTERED,
    ChainName           NVARCHAR(100) NOT NULL,
    ChainType           NVARCHAR(15) NOT NULL
                        CONSTRAINT CK_ApprovalChain_ChainType
                            CHECK (ChainType IN (N'Sequential', N'Parallel', N'Mixed')),
    TimeoutAction       NVARCHAR(15) NOT NULL
                        CONSTRAINT CK_ApprovalChain_TimeoutAction
                            CHECK (TimeoutAction IN (N'Escalate', N'Remind', N'AutoApprove')),
    TimeoutHours        INT NULL,
    Description         NVARCHAR(500) NULL,
    IsActive            BIT NOT NULL CONSTRAINT DF_ApprovalChain_IsActive DEFAULT 1,
    -- Standard audit + temporal
    ...
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = audit.ApprovalChainHistory, HISTORY_RETENTION_PERIOD = 7 YEARS));
```

---

### 4.7 workflow.ApprovalStep (NOT temporal)

Created in `051_escalation_approval_tables.sql`. Extended later (migrations 096–099 reference `ApproverPermissionId` and `ApproverPoolCode` columns not in the original DDL).

**Original columns from 051:**
```sql
CREATE TABLE workflow.ApprovalStep (
    ApprovalStepId      INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_ApprovalStep PRIMARY KEY CLUSTERED,
    ApprovalChainId     INT NOT NULL CONSTRAINT FK_ApprovalStep_Chain
                            REFERENCES workflow.ApprovalChain(ApprovalChainId),
    SequenceOrder       INT NOT NULL,            -- parallel steps share same SequenceOrder value
    ApproverRoleId      INT NOT NULL CONSTRAINT FK_ApprovalStep_ApproverRole
                            REFERENCES dbo.[Role](RoleId),
    StepName            NVARCHAR(100) NOT NULL,
    IsRequired          BIT NOT NULL CONSTRAINT DF_ApprovalStep_IsRequired DEFAULT 1,
    CreatedBy INT NULL, CreatedDate DATETIME2(0) NOT NULL ...,
    ModifiedBy INT NULL, ModifiedDate DATETIME2(0) NULL
);
```

**Additional columns added post-051 (referenced in 099):**
- `ApproverPermissionId INT NULL` FK→`security.Permission(PermissionId)` — for the permission-based authorization path
- `ApproverPoolCode VARCHAR(50) NULL` — future: dynamic approver pool resolution (not yet activated in v1)

---

### 4.8 workflow.ApprovalRecord (NOT temporal — IS the approval audit trail)

Created in `051_escalation_approval_tables.sql`.

```sql
CREATE TABLE workflow.ApprovalRecord (
    ApprovalRecordId        INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_ApprovalRecord PRIMARY KEY CLUSTERED,
    ApprovalStepId          INT NOT NULL CONSTRAINT FK_ApprovalRecord_Step
                                REFERENCES workflow.ApprovalStep(ApprovalStepId),
    EntityType              NVARCHAR(30) NOT NULL
                            CONSTRAINT CK_ApprovalRecord_EntityType
                                CHECK (EntityType IN (N'NCR', N'CAPA', N'Complaint', N'SCAR', N'AuditFinding', N'EightDReport')),
    EntityId                INT NOT NULL,
    PlantId                 INT NOT NULL CONSTRAINT FK_ApprovalRecord_Plant
                                REFERENCES dbo.Plant(PlantId),
    Decision                NVARCHAR(15) NOT NULL
                            CONSTRAINT CK_ApprovalRecord_Decision
                                CHECK (Decision IN (N'Pending', N'Approved', N'Rejected', N'Returned', N'Deferred')),
    DecisionById            INT NULL CONSTRAINT FK_ApprovalRecord_DecisionBy
                                REFERENCES dbo.AppUser(AppUserId),
    DecisionDate            DATETIME2(0) NULL,
    Comments                NVARCHAR(500) NULL,
    ElectronicSignatureId   INT NULL CONSTRAINT FK_ApprovalRecord_Signature
                                REFERENCES workflow.ElectronicSignature(ElectronicSignatureId),
    CreatedBy INT NULL,
    CreatedDate DATETIME2(0) NOT NULL CONSTRAINT DF_ApprovalRecord_CreatedDate DEFAULT SYSUTCDATETIME()
);
```

**Note:** `ApprovalRequestId INT NULL` also present (added in 098/099 linkage — references `PendingApprovalTransition.PendingTransitionId`).

---

### 4.9 workflow.PendingApprovalTransition — CURRENT state (Phase 27 target)

Created in `097_create_pending_transition_lifecycle.sql`. This is the staging mechanism for approval-gated state transitions.

```sql
CREATE TABLE workflow.PendingApprovalTransition (
    PendingTransitionId     INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_PendingApprovalTransition PRIMARY KEY CLUSTERED,
    EntityType              NVARCHAR(30) NOT NULL,
    EntityId                INT NOT NULL,
    PlantId                 INT NOT NULL,
    TransitionId            INT NOT NULL,        -- FK→workflow.WorkflowTransition
    ApprovalChainId         INT NOT NULL,        -- FK→workflow.ApprovalChain
    RequestedByUserId       INT NOT NULL,
    RequestedDate           DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    Status                  NVARCHAR(20) NOT NULL
        CHECK (Status IN (N'Pending', N'Approved', N'Applied', N'Rejected', N'Cancelled', N'Expired')),
    ContextJson             NVARCHAR(MAX) NULL,  -- JSON blob with comments etc.
    CompletedDate           DATETIME2(0) NULL,
    CompletedByUserId       INT NULL,
    IsActive                BIT NOT NULL DEFAULT(1),
    CorrelationId           UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID()
);
```

**Phase 27 adds two columns:**
```sql
ALTER TABLE workflow.PendingApprovalTransition
    ADD BaseEntityRowVersion  BINARY(8) NULL,   -- entity's @@ROWVERSION at request time
        BaseWorkflowStateId   INT NULL;          -- FK→workflow.WorkflowState at request time
```

These are captured when the pending row is created, then re-checked in `usp_ApplyApprovedTransition` before committing the state change. If the entity's current row version differs, the commit is blocked with a conflict error (50416 or similar). "Rescind, don't revert" — compensation is manual, not automated.

---

### 4.10 dbo.CustomerQualityRule — Policy Resolution Engine example

Created in `104_add_customer_quality_rules.sql`. This is the production implementation of the Policy Resolution Engine pattern.

```sql
CREATE TABLE dbo.CustomerQualityRule (
    CustomerQualityRuleId       INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_CustomerQualityRule PRIMARY KEY CLUSTERED,
    PlantId                     INT NOT NULL,           -- FK→dbo.Plant
    CustomerId                  INT NOT NULL,           -- FK→dbo.Customer
    DispositionCodeId           INT NULL,               -- NULL = applies to any disposition
    RuleTypeId                  INT NOT NULL,           -- FK→dbo.LookupValue (CustomerApprovalRuleType)
    NotificationSlaTierId       INT NULL,               -- FK→dbo.LookupValue (CustomerNotificationSlaTier)
    NotificationSlaHours        INT NULL,               -- explicit hours override
    RequiresCustomerApproval    BIT NOT NULL DEFAULT(0),
    RequiresConcession          BIT NOT NULL DEFAULT(0),
    MinSeverityForRule          INT NULL,               -- NULL = no min severity filter
    MaxSeverityForRule          INT NULL,               -- NULL = no max severity filter
    RulePriority                INT NOT NULL DEFAULT(100), -- lower = higher priority
    EffectiveFrom               DATE NOT NULL,
    EffectiveTo                 DATE NULL,              -- NULL = no expiry
    IsActive                    BIT NOT NULL DEFAULT(1),
    Notes                       NVARCHAR(500) NULL,
    CreatedAtUtc                DATETIME2(3) NOT NULL DEFAULT SYSUTCDATETIME(),
    CreatedByUserId             INT NULL,
    ModifiedAtUtc               DATETIME2(3) NULL,
    ModifiedByUserId            INT NULL,

    CONSTRAINT CK_CustomerQualityRule_SevRange CHECK (
        (MinSeverityForRule IS NULL AND MaxSeverityForRule IS NULL)
        OR (MinSeverityForRule IS NOT NULL AND MaxSeverityForRule IS NOT NULL
            AND MinSeverityForRule BETWEEN 1 AND 10
            AND MaxSeverityForRule BETWEEN 1 AND 10
            AND MinSeverityForRule <= MaxSeverityForRule)
    ),
    CONSTRAINT CK_CustomerQualityRule_Effective CHECK (
        EffectiveTo IS NULL OR EffectiveTo >= EffectiveFrom
    ),
    CONSTRAINT UQ_CustomerQualityRule_Precedence
        UNIQUE (PlantId, CustomerId, DispositionCodeId, RulePriority)
);
```

**Seeded lookup values:**

`CustomerApprovalRuleType`: `APPROVAL_REQUIRED`, `CONCESSION_REQUIRED`, `NOTIFICATION_ONLY`, `ESCALATION_OVERRIDE`

`CustomerNotificationSlaTier`: `TIER1_IMMEDIATE` (4h), `TIER2_SAMEDAY` (business day), `TIER3_STANDARD` (48h)

**Policy resolution query pattern** — most-specific wins, effective-dated:
```sql
SELECT TOP 1 *
FROM dbo.CustomerQualityRule
WHERE CustomerId = @CustomerId
  AND PlantId = @PlantId
  AND (DispositionCodeId = @DispositionCodeId OR DispositionCodeId IS NULL)
  AND IsActive = 1
  AND EffectiveFrom <= CAST(SYSUTCDATETIME() AS DATE)
  AND (EffectiveTo IS NULL OR EffectiveTo >= CAST(SYSUTCDATETIME() AS DATE))
ORDER BY
    CASE WHEN DispositionCodeId IS NOT NULL THEN 0 ELSE 1 END,  -- specific before wildcard
    RulePriority ASC                                              -- lower priority number wins
```

---

## 5. Key Stored Procedure Signatures

### 5.1 workflow.usp_TransitionState (migration 098 — latest version)

The central state machine executor. Created with `CREATE OR ALTER`.

```sql
CREATE OR ALTER PROCEDURE workflow.usp_TransitionState
    @CallerAzureOid     UNIQUEIDENTIFIER,   -- Azure AD OID for identity resolution
    @EntityType         NVARCHAR(30),        -- 'NCR', 'CAPA', 'Complaint', 'SCAR', 'AuditFinding', 'EightDReport'
    @EntityId           INT,
    @ToStatusCode       NVARCHAR(30),        -- target status code string (e.g. 'NCR-SUBMITTED')
    @Comments           NVARCHAR(500) = NULL,
    @TransitionReason   NVARCHAR(500) = NULL
AS
```

**Execution path (in order):**
1. Resolve `@CallerAzureOid` → `@UserId` via `dbo.usp_SetSessionContext`
2. Validate `@EntityType` in `dbo.EntityTypeRegistry`
3. CASE dispatch to read entity's current `StatusCodeId` and `PlantId`
4. Resolve `@ToStatusCode` → `@ToStatusId`
5. Look up transition (`workflow.WorkflowTransition` join `WorkflowState`) — throws 50400 if no valid transition
6. Dual-path authorization: if `RequiredPermissionId IS NOT NULL` → `security.usp_EvaluatePolicy`; else if `RequiredRoleId IS NOT NULL` → check `dbo.UserRole` with `PlantId` scope
7. Evaluate guard expression (`@GuardType` CASE dispatch, no dynamic SQL)
8. **Approval lifecycle gate:** if transition has `ApprovalChainId IS NOT NULL`, create `PendingApprovalTransition` + `ApprovalRecord` rows, then `THROW 50414` (APPROVAL_REQUIRED — not an error, it's the expected path)
9. Calculate `DurationInState` from `workflow.StatusHistory`
10. In transaction: UPDATE entity's `StatusCodeId`, UPDATE `StatusHistory.MostRecent = 0`, INSERT new `StatusHistory` row
11. Return new `StatusHistory` row

**Error codes:**
| Code | Meaning |
|------|---------|
| 50400 | Invalid transition or guard condition not met |
| 50401 | Authorization denied |
| 50404 | Entity not found |
| 50411 | Permission ID doesn't resolve |
| 50413 | Separation of duty violation |
| 50414 | APPROVAL_REQUIRED (expected — pending request created) |
| 50415 | No required approval steps configured |
| 50417 | Duplicate pending approval request |

---

### 5.2 workflow.usp_ProcessApprovalStep (migration 099 — latest version)

Records approval decisions and drives the approval lifecycle.

```sql
CREATE OR ALTER PROCEDURE workflow.usp_ProcessApprovalStep
    @CallerAzureOid     UNIQUEIDENTIFIER,
    @ApprovalRecordId   INT,
    @Decision           NVARCHAR(20),        -- 'Approved', 'Rejected', 'Deferred'
    @Comments           NVARCHAR(500) = NULL
AS
```

**Execution path:**
1. Resolve `@CallerAzureOid` → `@UserId`
2. Validate `@Decision` IN ('Approved', 'Rejected', 'Deferred')
3. Validate `ApprovalRecord` exists and is 'Pending'
4. Resolve entity `PlantId` via CASE dispatch
5. Dual-path approver check: `ApproverPermissionId` path → `security.usp_CheckPermission`; else `ApproverRoleId` path → `dbo.UserRole` with `PlantId`
6. **SoD check (error 50413):** if approver = requestor AND `security.RolePermissionConstraint` has `ConstraintType = 'SeparationOfDuty'` AND no `security.SoDException` → throw 50413
7. In transaction: UPDATE `ApprovalRecord` with decision; if Rejected → UPDATE `PendingApprovalTransition.Status = 'Rejected'`
8. If Approved: check if all required steps in chain now have non-Pending decisions. If yes (`IsChainComplete = 1`): UPDATE `PendingApprovalTransition.Status = 'Approved'`, then call `workflow.usp_ApplyApprovedTransition`

---

### 5.3 workflow.usp_ApplyApprovedTransition (migration 097)

Applies a fully-approved transition. Called by `usp_ProcessApprovalStep` on chain completion.

```sql
CREATE OR ALTER PROCEDURE workflow.usp_ApplyApprovedTransition
    @PendingTransitionId    INT
AS
```

**Execution path:**
1. Read the `PendingApprovalTransition` row (validates Status = 'Approved')
2. Re-read the entity's **current** `StatusCodeId` via CASE dispatch
3. **Stale-state check:** compare current `StatusCodeId` against expected `FromStateId` (the state recorded when the pending row was created). If they differ → the entity has moved since the approval was staged → throw 50416 (stale state, approval chain invalidated)
4. In transaction: UPDATE entity's `StatusCodeId` to `ToStatusCodeId`, UPDATE `StatusHistory`, UPDATE `PendingApprovalTransition.Status = 'Applied'`

**Phase 27 extends this:** Before the stale-state check, also compare `BaseEntityRowVersion` (captured at request time) against the entity's current `@@ROWVERSION`. Conflicting row versions trigger 50416 with additional conflict detail.

---

### 5.4 security.usp_EvaluatePolicy (migration 096)

Full 5-layer policy evaluation. Wraps `security.usp_CheckPermission`.

```sql
CREATE OR ALTER PROCEDURE security.usp_EvaluatePolicy
    @UserId         INT,
    @PermissionCode VARCHAR(100),
    @PlantId        INT,
    @FeatureCode    VARCHAR(100)    = NULL,
    @EntityType     NVARCHAR(30)    = NULL,
    @EntityId       INT             = NULL,
    @ContextJson    NVARCHAR(MAX)   = NULL,
    @ResultCode     INT             OUTPUT      -- 0 = pass, 50410-50419 = denial code
AS
```

Returns 0 on success. Callers check `@ResultCode <> 0` to detect denial. Layer 5 (workflow gating) is handled by the calling SP, not here.

---

## 6. Escalation and SLA Infrastructure

### workflow.EscalationRule (NOT temporal)

```sql
CREATE TABLE workflow.EscalationRule (
    EscalationRuleId    INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_EscalationRule PRIMARY KEY CLUSTERED,
    EntityType          NVARCHAR(30) NOT NULL
        CHECK (EntityType IN (N'NCR', N'CAPA', N'Complaint', N'SCAR', N'AuditFinding', N'EightDReport')),
    TriggerType         NVARCHAR(30) NOT NULL
        CHECK (TriggerType IN (N'OverdueDays', N'SeverityThreshold', N'NoActivity', N'RepeatIssue')),
    TriggerValue        INT NOT NULL,
    EscalationLevel     INT NOT NULL DEFAULT 1,
    TargetRoleId        INT NOT NULL REFERENCES dbo.[Role](RoleId),
    EscalationAction    NVARCHAR(30) NOT NULL DEFAULT N'Notify'
        CHECK (EscalationAction IN (N'Notify', N'BumpPriority', N'NotifyAndBump')),
    BumpPriority        BIT NOT NULL DEFAULT 1,
    PlantId             INT NULL REFERENCES dbo.Plant(PlantId),   -- NULL = global
    IsActive            BIT NOT NULL DEFAULT 1,
    ...
);
```

### workflow.SlaConfiguration (temporal)

Per-transition SLA overrides. Schema-ready in v1, not yet seeded.

```sql
CREATE TABLE workflow.SlaConfiguration (
    SlaConfigurationId  INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_SlaConfiguration PRIMARY KEY CLUSTERED,
    EntityType          NVARCHAR(30) NOT NULL,
    TransitionId        INT NOT NULL REFERENCES workflow.WorkflowTransition(WorkflowTransitionId),
    CustomerId          INT NULL REFERENCES dbo.Customer(CustomerId),
    SeverityRatingId    INT NULL REFERENCES dbo.SeverityRating(SeverityRatingId),
    PlantId             INT NULL REFERENCES dbo.Plant(PlantId),
    SlaHours            INT NOT NULL,
    Priority            INT NOT NULL DEFAULT 0,
    IsActive            BIT NOT NULL DEFAULT 1,
    ...
)
WITH (SYSTEM_VERSIONING = ON (...));
```

---

## 7. What Phase 25 Must Build

**Migration number:** Will be ~134 or 135 (next available after current 133).

**Primary deliverable:** Enhance `rca.EightDStep` to support 7-state step tracking for guided process orchestration.

### Exact schema changes required

**1. Add `StepStatus TINYINT` to `rca.EightDStep`:**
```sql
-- Add new column (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'rca.EightDStep') AND name = N'StepStatus')
    ALTER TABLE rca.EightDStep ADD StepStatus TINYINT NOT NULL
        CONSTRAINT DF_EightDStep_StepStatus DEFAULT 0
        CONSTRAINT CK_EightDStep_StepStatus CHECK (StepStatus BETWEEN 0 AND 6);
```

**State enum values:**
```
0 = NotStarted         -- initial state (replaces IsComplete = 0)
1 = InProgress         -- user has begun entering data
2 = Submitted          -- user completed input, workflow initiated
3 = PendingApproval    -- workflow is waiting on approval
4 = Committed          -- approved and committed to record (replaces IsComplete = 1)
5 = Skipped            -- explicitly bypassed with reason
6 = ReturnedForChanges -- approval rejected, returned to submitter
```

**2. Add prerequisite/skip columns:**
```sql
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'rca.EightDStep') AND name = N'IsSkippable')
    ALTER TABLE rca.EightDStep ADD
        IsSkippable             BIT NOT NULL CONSTRAINT DF_EightDStep_IsSkippable DEFAULT 0,
        SkippedReason           NVARCHAR(500) NULL,
        SkippedByUserId         INT NULL CONSTRAINT FK_EightDStep_SkippedBy
                                    REFERENCES dbo.AppUser(AppUserId),
        PrerequisiteStepNumber  TINYINT NULL
                                CONSTRAINT CK_EightDStep_PrereqBetween
                                    CHECK (PrerequisiteStepNumber BETWEEN 0 AND 8);
```

**3. Add `DefinitionVersion` to `rca.EightDReport`:**
```sql
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'rca.EightDReport') AND name = N'DefinitionVersion')
    ALTER TABLE rca.EightDReport ADD DefinitionVersion INT NOT NULL
        CONSTRAINT DF_EightDReport_DefinitionVersion DEFAULT 1;
```

**4. Deprecate `IsComplete`:** Either DROP the column (preferred if no API/view reads it) or add a computed column `IsComplete AS CAST(CASE WHEN StepStatus = 4 THEN 1 ELSE 0 END AS BIT)`. Check all procs and views that read `IsComplete` first.

**Stored procedure deliverables:**
- New: `rca.usp_UpdateEightDStepStatus(@CallerAzureOid, @EightDStepId, @NewStatus TINYINT, @Reason NVARCHAR(500) = NULL)`
  - Validates prerequisite step is Committed before allowing PendingApproval on steps with `PrerequisiteStepNumber IS NOT NULL`
  - Validates Skipped steps have `SkippedReason` and `SkippedByUserId`
  - Validates state transitions are legal (e.g., cannot go from Committed back to InProgress)
- Update: `rca.usp_GetEightDStepProgress(@EightDReportId)` — returns all 9 steps with current status and prerequisite status

**Guard enforcement for report closure:** All required steps (IsSkippable = 0) must be in state Committed before `EightDReport` can transition to its closed status. This is a guard on the `EightDReport` workflow transition, not on the individual steps.

---

## 8. What Phase 27 Must Build

**Primary deliverable:** Optimistic concurrency protection on `workflow.PendingApprovalTransition` → `usp_ApplyApprovedTransition`.

### Schema change
```sql
-- Add to workflow.PendingApprovalTransition (idempotent)
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'workflow.PendingApprovalTransition') AND name = N'BaseEntityRowVersion')
    ALTER TABLE workflow.PendingApprovalTransition ADD
        BaseEntityRowVersion    BINARY(8) NULL,     -- @@ROWVERSION of entity at request time
        BaseWorkflowStateId     INT NULL;            -- WorkflowStateId of entity at request time
```

### Procedure change (usp_ApplyApprovedTransition)
After the existing stale-state check (compare current StatusCodeId vs expected FromStateId), add:
```sql
-- Row version conflict check
IF @BaseEntityRowVersion IS NOT NULL
BEGIN
    DECLARE @CurrentRowVersion BINARY(8);
    -- Read current @@ROWVERSION via CASE dispatch on EntityType
    IF @EntityType = N'NCR'
        SELECT @CurrentRowVersion = %%physloc%% -- or stored rowversion column if exists

    -- If row version changed, entity was modified after staging
    IF @CurrentRowVersion != @BaseEntityRowVersion
        THROW 50416, N'Entity was modified after approval was staged; re-validate and resubmit', 1;
END
```

**Note:** `@@ROWVERSION` gives the database-wide version, not per-row. The clean approach is to add a `RowVersion ROWVERSION` column (auto-updated on every row modification) to each entity table. If those columns don't exist yet, Phase 27 must also add them to the entity tables.

### Population in usp_TransitionState
When creating the `PendingApprovalTransition` row (Step 7.5 in usp_TransitionState), capture:
```sql
INSERT INTO workflow.PendingApprovalTransition (
    EntityType, EntityId, PlantId, TransitionId, ApprovalChainId,
    RequestedByUserId, Status, ContextJson,
    BaseEntityRowVersion, BaseWorkflowStateId   -- NEW
)
VALUES (
    @EntityType, @EntityId, @PlantId, @TransitionId, @ApprovalChainId,
    @UserId, N'Pending', ...,
    @CurrentRowVersion,     -- captured just before INSERT
    @CurrentWorkflowStateId -- the FromStateId of the matched transition
);
```

---

## 9. What Phase 30 Must Build

**Primary deliverable:** SLA expiration processing and escalation batch job.

This phase extends the existing `workflow.SlaConfiguration` (schema-ready, not yet seeded) and `workflow.EscalationRule` (seeded) into an operational batch processor.

**Key tables already exist:**
- `workflow.SlaConfiguration` — defines SLA hours per transition
- `workflow.EscalationRule` — defines escalation triggers
- `workflow.EscalationLog` — escalation event history
- `workflow.StatusHistory` — tracks when entities entered each state (used for SLA elapsed calculation)

**Phase 30 deliverables:**
- Seed `workflow.SlaConfiguration` for NCR, CAPA, Complaint, SCAR, EightDReport transitions
- New proc: `workflow.usp_ProcessSlaExpirations(@ProcessedCount INT OUTPUT)` — batch job runner
  - Reads all `PendingApprovalTransition` rows with `Status = 'Pending'`
  - For each: checks if elapsed time since `RequestedDate` exceeds chain's `TimeoutHours`
  - On timeout: UPDATE `Status = 'Expired'`, trigger EscalationRule evaluation
- New proc: `workflow.usp_EvaluateEntitySla(@EntityType, @EntityId)` — returns SLA status (within/warning/overdue/expired) for a single entity based on current state's SLA config
- Update `workflow.PendingApprovalTransition` with `ExpiresAt DATETIME2(0) NULL` — computed at INSERT from chain `TimeoutHours`

---

## 10. What Phase 32 Must Build

**Primary deliverable:** Validate-only stored procedures and reference data seeding for API consumption.

Phase 32 creates `_Validate` variants of key mutation procedures that run all business rules and guards but do NOT commit any changes. The API uses these to surface validation errors to users before they attempt a real submission.

**Pattern:**
```sql
CREATE OR ALTER PROCEDURE workflow.usp_ValidateTransition
    @CallerAzureOid     UNIQUEIDENTIFIER,
    @EntityType         NVARCHAR(30),
    @EntityId           INT,
    @ToStatusCode       NVARCHAR(30)
AS
-- Runs Steps 1-7 of usp_TransitionState (identity, lookup, authorization, guards)
-- Returns: IsValid BIT, ErrorCode INT NULL, ErrorMessage NVARCHAR(500) NULL
-- Does NOT execute Step 8 (approval gate), Step 9 (transaction), or Step 10 (history)
```

**Reference data seeding:** Seeds `workflow.WorkflowProcess`, `workflow.WorkflowState`, `workflow.WorkflowTransition` with the full NCR, CAPA, Complaint, SCAR, AuditFinding, EightDReport state machines using idempotent MERGE statements.

---

## 11. Audit Infrastructure

### audit.AuditLog (universal change tracking)

Every mutable entity has an audit trigger created by `dbo.usp_CreateAuditTrigger`. The trigger logs to `audit.AuditLog` with: `EntityType`, `EntityId`, `ChangedByUserId`, `ChangedAt`, `ColumnName`, `OldValue`, `NewValue`.

### audit.ApiCallLog (planned — Phase 29)

Not yet created. Phase 29 creates this table. The API middleware then writes to it on every request. This is a cross-repo gate: `sf-quality-api` Phase 3.5 depends on `audit.ApiCallLog` existing in the DB.

### Temporal history tables

All configuration tables (WorkflowProcess, WorkflowState, WorkflowTransition, ApprovalChain, CustomerQualityRule, etc.) use SQL Server system-versioned temporal tables with 7-year history retention. The history tables live in `audit` schema with clustered columnstore indexes.

---

## 12. Contract Chain

The contract between repos flows through JSON files:

```
sf-quality-db:
  ├── .planning/db-contract-manifest.json      ← lists all procs/views available to API
  └── database/migrations/*.sql                ← migrations

sf-quality-api:
  ├── .planning/api-openapi.publish.json       ← OpenAPI spec driving API dev
  └── .planning/api-openapi.snapshot.json      ← snapshot of deployed state

sf-quality-app:
  └── .planning/requirements/...              ← app requirements
```

When a DB phase ships new procs/views that the API will consume, the `db-contract-manifest.json` must be refreshed before API planning begins. **The manifest is currently stale** — it doesn't reflect Phase 21's 9 knowledge views and 1 procedure. Must be refreshed to v1.1.0 before any v3.0 work begins.

**Current manifest state:** v1.0.0, reflects Phases 1–20. Phase 21 additions (knowledge views) not yet included.
