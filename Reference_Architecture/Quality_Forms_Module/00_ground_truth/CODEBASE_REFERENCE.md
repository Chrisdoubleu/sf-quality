# Quality Inspection Forms Module — Codebase Reference

**Purpose:** Verbatim source code, DDL, procedure signatures, and architectural patterns from the current sf-quality system. Read this entire document before designing the Forms module. Every design decision must be compatible with what's here.

**Last Updated:** 2026-02-22
**DB Manifest Version:** 1.0.0 (133 migrations shipped)
**API Version:** 0.2.0 (27 endpoints, Phase 3 complete)
**App Status:** Planning only (no source code)

---

## 1. Database Schema Architecture

### 7-Schema Model

```
dbo         — Infrastructure tier: Plant, AppUser, StatusCode, DefectType, Lookup, Supplier, Customer, Part, Equipment
quality     — Domain tier: NCR, CAPA, Complaints, AuditFinding, SCARecord, Disposition, Containment
rca         — Domain tier: 8D, Fishbone, 5Whys, IsIsNot, PFMEA (root cause analysis)
apqp        — Domain tier: APQP/PPAP/ECO/Control Plans (reserved, minimal content)
workflow    — Domain tier: State machine, transitions, status history, action items, approvals, escalations
security    — System tier: RLS predicates, permissions, policy engine, role constraints
audit       — System tier: History tables (clustered columnstore), AuditLog (7-year retention)
```

**Convention:** New module tables should go in an appropriate existing schema or a new `inspection` schema if the scope justifies it.

### Naming Conventions (Enforced)

| Element | Convention | Example |
|---------|-----------|---------|
| Table | PascalCase, singular noun | `quality.NonConformanceReport` |
| Column | PascalCase | `DefectTypeId`, `IsActive`, `CreatedDate` |
| Primary Key | `{TableName}Id` | `NonConformanceReportId` |
| Foreign Key | Referenced table's PK name | `CustomerId`, `PlantId` |
| Boolean | `Is*` prefix | `IsActive`, `IsSkippable`, `IsRequired` |
| Constraint PK | `PK_{TableName}` | `PK_NonConformanceReport` |
| Constraint FK | `FK_{Table}_{ReferencedTable}` | `FK_Part_Customer` |
| Constraint UQ | `UQ_{Table}_{Columns}` | `UQ_Part_PartNumber_PartRevision` |
| Constraint CK | `CK_{Table}_{Rule}` | `CK_DefectType_HierarchyLevel` |
| Constraint DF | `DF_{Table}_{Column}` | `DF_DefectType_IsActive` |
| Index | `IX_{Table}_{Columns}` | `IX_StatusHistory_PlantId_ChangedDate` |
| Unique Index | `UX_{Table}_{Columns}` | `UX_StatusHistory_MostRecent` |
| Stored Proc | `{schema}.usp_{Action}{Entity}` | `quality.usp_CreateNCR` |
| View | `{schema}.vw_{Description}` | `quality.vw_NcrOperationalQueue` |
| Migration | `{NNN}_{snake_case_description}.sql` | `130_taxonomy_v3_cleanup.sql` |

### Standard Column Patterns

**Audit Columns (on every mutable table):**
```sql
CreatedBy       INT             NULL,
CreatedDate     DATETIME2(0)    NOT NULL
    CONSTRAINT DF_{Table}_CreatedDate DEFAULT SYSUTCDATETIME(),
ModifiedBy      INT             NULL,
ModifiedDate    DATETIME2(0)    NULL,
```

**Temporal Versioning (on auditable business entities):**
```sql
ValidFrom       DATETIME2(0)    GENERATED ALWAYS AS ROW START HIDDEN
    CONSTRAINT DF_{Table}_ValidFrom DEFAULT SYSUTCDATETIME(),
ValidTo         DATETIME2(0)    GENERATED ALWAYS AS ROW END HIDDEN
    CONSTRAINT DF_{Table}_ValidTo DEFAULT CONVERT(DATETIME2(0), '9999-12-31 23:59:59'),
PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
```
```sql
WITH (SYSTEM_VERSIONING = ON (
    HISTORY_TABLE = audit.{Table}History,
    HISTORY_RETENTION_PERIOD = 7 YEARS
));
```

**Soft Delete / Active Flag:**
```sql
IsActive        BIT             NOT NULL
    CONSTRAINT DF_{Table}_IsActive DEFAULT 1,
```

**Plant Scoping (for RLS-governed tables):**
```sql
PlantId         INT             NOT NULL
    CONSTRAINT FK_{Table}_Plant REFERENCES dbo.Plant(PlantId),
```

---

## 2. Key Reference Tables (Verbatim DDL)

### dbo.Plant

```sql
CREATE TABLE dbo.Plant (
    PlantId         INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Plant PRIMARY KEY CLUSTERED,
    PlantCode       NVARCHAR(10)    NOT NULL
        CONSTRAINT UQ_Plant_PlantCode UNIQUE,
    PlantName       NVARCHAR(100)   NOT NULL,
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_Plant_IsActive DEFAULT 1,
    -- standard audit + temporal columns
);
```

### dbo.Customer

```sql
CREATE TABLE dbo.Customer (
    CustomerId      INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Customer PRIMARY KEY CLUSTERED,
    PlantId         INT             NOT NULL
        CONSTRAINT FK_Customer_Plant REFERENCES dbo.Plant(PlantId),
    CustomerCode    NVARCHAR(20)    NOT NULL
        CONSTRAINT UQ_Customer_CustomerCode UNIQUE,
    CustomerName    NVARCHAR(200)   NOT NULL,
    OemTier         NVARCHAR(20)    NULL,
    DunsNumber      NVARCHAR(13)    NULL,
    ContactName     NVARCHAR(100)   NULL,
    ContactEmail    NVARCHAR(200)   NULL,
    ContactPhone    NVARCHAR(20)    NULL,
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_Customer_IsActive DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
);
```

### dbo.Part (Global — NO PlantId)

```sql
CREATE TABLE dbo.Part (
    PartId          INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Part PRIMARY KEY CLUSTERED,
    CustomerId      INT             NULL
        CONSTRAINT FK_Part_Customer REFERENCES dbo.Customer(CustomerId),
    PartNumber      NVARCHAR(50)    NOT NULL,
    PartRevision    NVARCHAR(10)    NULL,
    PartName        NVARCHAR(200)   NULL,
    Description     NVARCHAR(500)   NULL,
    CoatingType     NVARCHAR(50)    NULL,
    SubstrateType   NVARCHAR(50)    NULL,
    DrawingNumber   NVARCHAR(50)    NULL,
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_Part_IsActive DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
    CONSTRAINT UQ_Part_PartNumber_PartRevision UNIQUE (PartNumber, PartRevision)
);
```

### dbo.ProductionLine

```sql
CREATE TABLE dbo.ProductionLine (
    ProductionLineId INT            IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_ProductionLine PRIMARY KEY CLUSTERED,
    PlantId         INT             NOT NULL
        CONSTRAINT FK_ProductionLine_Plant REFERENCES dbo.Plant(PlantId),
    LineTypeId      INT             NOT NULL
        CONSTRAINT FK_ProductionLine_LineType REFERENCES dbo.LineType(LineTypeId),
    LineCode        NVARCHAR(20)    NOT NULL
        CONSTRAINT UQ_ProductionLine_LineCode UNIQUE,
    LineName        NVARCHAR(100)   NOT NULL,
    Description     NVARCHAR(500)   NULL,
    ApplicationMethod NVARCHAR(20)  NULL,       -- Manual, Robotic, Automated
    HandlingMethod  NVARCHAR(20)    NULL,       -- Continuous Conveyor, Batch Rack, Immersion
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_ProductionLine_IsActive DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
);
```

### dbo.LineType (Immutable Reference)

```sql
-- 7 finishing technologies seeded:
-- ECOAT, POWDER, LIQUID, PRETREAT, ASSEMBLY, PACKAGING, OTHER
CREATE TABLE dbo.LineType (
    LineTypeId      INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_LineType PRIMARY KEY CLUSTERED,
    LineTypeCode    NVARCHAR(20)    NOT NULL
        CONSTRAINT UQ_LineType_LineTypeCode UNIQUE,
    LineTypeName    NVARCHAR(100)   NOT NULL,
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_LineType_IsActive DEFAULT 1
);
```

### dbo.Equipment

```sql
CREATE TABLE dbo.Equipment (
    EquipmentId     INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Equipment PRIMARY KEY CLUSTERED,
    PlantId         INT             NOT NULL
        CONSTRAINT FK_Equipment_Plant REFERENCES dbo.Plant(PlantId),
    ProductionLineId INT            NULL
        CONSTRAINT FK_Equipment_ProductionLine REFERENCES dbo.ProductionLine(ProductionLineId),
    ProcessAreaId   INT             NULL
        CONSTRAINT FK_Equipment_ProcessArea REFERENCES dbo.ProcessArea(ProcessAreaId),
    EquipmentName   NVARCHAR(100)   NOT NULL,
    EquipmentCode   NVARCHAR(20)    NULL
        CONSTRAINT UQ_Equipment_EquipmentCode UNIQUE,
    Description     NVARCHAR(500)   NULL,
    EquipmentType   NVARCHAR(50)    NULL,       -- Oven, Booth, Tank, Gauge, Meter, etc.
    Manufacturer    NVARCHAR(100)   NULL,
    ModelNumber     NVARCHAR(50)    NULL,
    SerialNumber    NVARCHAR(50)    NULL,
    IsPortable      BIT             NOT NULL
        CONSTRAINT DF_Equipment_IsPortable DEFAULT 0,
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_Equipment_IsActive DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
);
```

### dbo.DefectType (Hierarchical Taxonomy — ~82 active codes)

```sql
CREATE TABLE dbo.DefectType (
    DefectTypeId    INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_DefectType PRIMARY KEY CLUSTERED,
    ParentDefectTypeId INT          NULL
        CONSTRAINT FK_DefectType_Parent REFERENCES dbo.DefectType(DefectTypeId),
    DefectCode      NVARCHAR(20)    NOT NULL
        CONSTRAINT UQ_DefectType_DefectCode UNIQUE,
    DefectName      NVARCHAR(100)   NOT NULL,
    Description     NVARCHAR(500)   NULL,
    HierarchyLevel  TINYINT         NOT NULL
        CONSTRAINT CK_DefectType_HierarchyLevel CHECK (HierarchyLevel IN (1, 2)),
    DefaultSeverityId INT           NULL
        CONSTRAINT FK_DefectType_DefaultSeverity REFERENCES dbo.SeverityRating(SeverityRatingId),
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_DefectType_IsActive DEFAULT 1,
    SortOrder       INT             NOT NULL
        CONSTRAINT DF_DefectType_SortOrder DEFAULT 0,
    -- standard audit + temporal columns (7yr retention)
);
```

### dbo.CustomerQualityRule (Effective-Dated, Priority-Ranked)

```sql
CREATE TABLE dbo.CustomerQualityRule (
    CustomerQualityRuleId INT       IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_CustomerQualityRule PRIMARY KEY CLUSTERED,
    CustomerId      INT             NOT NULL
        CONSTRAINT FK_CustomerQualityRule_Customer REFERENCES dbo.Customer(CustomerId),
    PlantId         INT             NOT NULL
        CONSTRAINT FK_CustomerQualityRule_Plant REFERENCES dbo.Plant(PlantId),
    DispositionCodeId INT           NULL
        CONSTRAINT FK_CustomerQualityRule_DispositionCode REFERENCES dbo.DispositionCode(DispositionCodeId),
    RuleTypeId      INT             NOT NULL,       -- LookupValue FK (CustomerApprovalRuleType)
    NotificationSlaTierId INT       NULL,           -- LookupValue FK (TIER1_IMMEDIATE/TIER2_SAMEDAY/TIER3_STANDARD)
    NotificationSlaHours INT        NULL,           -- Hours for notification SLA (4/8/48)
    RequiresCustomerApproval BIT    NOT NULL DEFAULT 0,
    RequiresConcession BIT          NOT NULL DEFAULT 0,
    MinSeverityForRule INT          NULL,
    MaxSeverityForRule INT          NULL,
    RulePriority    INT             NOT NULL,
    EffectiveFrom   DATE            NOT NULL,
    EffectiveTo     DATE            NULL,
    IsActive        BIT             NOT NULL DEFAULT 1,
    -- standard audit columns
    CONSTRAINT UQ_CustomerQualityRule UNIQUE (PlantId, CustomerId, DispositionCodeId, RulePriority)
);
```

### dbo.LookupCategory / dbo.LookupValue (Generic Reference Data)

```sql
CREATE TABLE dbo.LookupCategory (
    LookupCategoryId INT           IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_LookupCategory PRIMARY KEY CLUSTERED,
    CategoryCode    NVARCHAR(50)    NOT NULL
        CONSTRAINT UQ_LookupCategory_CategoryCode UNIQUE,
    CategoryName    NVARCHAR(200)   NOT NULL,
    Description     NVARCHAR(500)   NULL,
    IsSystemManaged BIT             NOT NULL DEFAULT 0,
    IsActive        BIT             NOT NULL DEFAULT 1,
    -- standard audit columns
);

CREATE TABLE dbo.LookupValue (
    LookupValueId   INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_LookupValue PRIMARY KEY CLUSTERED,
    LookupCategoryId INT            NOT NULL
        CONSTRAINT FK_LookupValue_Category REFERENCES dbo.LookupCategory(LookupCategoryId),
    ValueCode       NVARCHAR(50)    NOT NULL,
    ValueName       NVARCHAR(200)   NOT NULL,
    Description     NVARCHAR(500)   NULL,
    SortOrder       INT             NOT NULL DEFAULT 0,
    IsActive        BIT             NOT NULL DEFAULT 1,
    -- standard audit columns
    CONSTRAINT UQ_LookupValue_Category_Code UNIQUE (LookupCategoryId, ValueCode)
);
```

### dbo.Document / dbo.DocumentType

```sql
CREATE TABLE dbo.DocumentType (
    DocumentTypeId  INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_DocumentType PRIMARY KEY CLUSTERED,
    TypeCode        NVARCHAR(20)    NOT NULL
        CONSTRAINT UQ_DocumentType_TypeCode UNIQUE,
    TypeName        NVARCHAR(100)   NOT NULL,
    IsActive        BIT             NOT NULL DEFAULT 1,
    -- standard audit columns
);

CREATE TABLE dbo.Document (
    DocumentId      INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Document PRIMARY KEY CLUSTERED,
    PlantId         INT             NOT NULL
        CONSTRAINT FK_Document_Plant REFERENCES dbo.Plant(PlantId),
    DocumentTypeId  INT             NOT NULL
        CONSTRAINT FK_Document_DocumentType REFERENCES dbo.DocumentType(DocumentTypeId),
    DocumentNumber  NVARCHAR(50)    NULL,
    DocumentTitle   NVARCHAR(200)   NOT NULL,
    StoragePath     NVARCHAR(500)   NULL,
    ExternalUrl     NVARCHAR(500)   NULL,
    Description     NVARCHAR(500)   NULL,
    IsActive        BIT             NOT NULL DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
);
```

---

## 3. Workflow Engine (Verbatim DDL)

### workflow.WorkflowProcess

```sql
CREATE TABLE workflow.WorkflowProcess (
    WorkflowProcessId INT          IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_WorkflowProcess PRIMARY KEY CLUSTERED,
    EntityType      NVARCHAR(30)    NOT NULL
        CONSTRAINT CK_WorkflowProcess_EntityType CHECK (EntityType IN (
            N'NCR', N'CAPA', N'CustomerComplaint', N'SupplierCAR', N'AuditFinding', N'EightDReport'
        )),
    ProcessName     NVARCHAR(100)   NOT NULL,
    ProcessVersion  NVARCHAR(10)    NOT NULL
        CONSTRAINT DF_WorkflowProcess_Version DEFAULT N'1.0',
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_WorkflowProcess_IsActive DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
    CONSTRAINT UQ_WorkflowProcess_EntityType UNIQUE (EntityType)
);
```

### workflow.WorkflowState

```sql
CREATE TABLE workflow.WorkflowState (
    WorkflowStateId INT            IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_WorkflowState PRIMARY KEY CLUSTERED,
    WorkflowProcessId INT          NOT NULL
        CONSTRAINT FK_WorkflowState_WorkflowProcess REFERENCES workflow.WorkflowProcess(WorkflowProcessId),
    StatusCodeId    INT             NOT NULL
        CONSTRAINT FK_WorkflowState_StatusCode REFERENCES dbo.StatusCode(StatusCodeId),
    StateType       NVARCHAR(20)    NOT NULL
        CONSTRAINT CK_WorkflowState_StateType CHECK (StateType IN (
            N'Start', N'Normal', N'Terminal', N'Cancelled'
        )),
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_WorkflowState_IsActive DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
);
```

### workflow.WorkflowTransition

```sql
CREATE TABLE workflow.WorkflowTransition (
    WorkflowTransitionId INT       IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_WorkflowTransition PRIMARY KEY CLUSTERED,
    WorkflowProcessId INT          NOT NULL
        CONSTRAINT FK_WorkflowTransition_WorkflowProcess REFERENCES workflow.WorkflowProcess(WorkflowProcessId),
    FromStateId     INT             NOT NULL
        CONSTRAINT FK_WorkflowTransition_FromState REFERENCES workflow.WorkflowState(WorkflowStateId),
    ToStateId       INT             NOT NULL
        CONSTRAINT FK_WorkflowTransition_ToState REFERENCES workflow.WorkflowState(WorkflowStateId),
    TransitionName  NVARCHAR(100)   NOT NULL,
    GuardType       NVARCHAR(30)    NULL,           -- SeveritySkip, ChildEntityState, Classification, RejectionCount, FastClose
    GuardExpression NVARCHAR(500)   NULL,
    RequiredRoleId  INT             NULL
        CONSTRAINT FK_WorkflowTransition_RequiredRole REFERENCES dbo.Role(RoleId),
    SlaHours        INT             NULL,
    SlaBaselineType NVARCHAR(20)    NULL,
    IsAutoFire      BIT             NOT NULL DEFAULT 0,
    IsActive        BIT             NOT NULL
        CONSTRAINT DF_WorkflowTransition_IsActive DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
    CONSTRAINT CK_WorkflowTransition_NoSelfTransition CHECK (FromStateId <> ToStateId)
);
```

### workflow.StatusHistory (Immutable Audit Trail)

```sql
CREATE TABLE workflow.StatusHistory (
    StatusHistoryId INT            IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_StatusHistory PRIMARY KEY CLUSTERED,
    EntityType      NVARCHAR(30)    NOT NULL,
    EntityId        INT             NOT NULL,
    FromStatusCodeId INT            NULL
        CONSTRAINT FK_StatusHistory_FromStatus REFERENCES dbo.StatusCode(StatusCodeId),
    ToStatusCodeId  INT             NOT NULL
        CONSTRAINT FK_StatusHistory_ToStatus REFERENCES dbo.StatusCode(StatusCodeId),
    TransitionId    INT             NULL
        CONSTRAINT FK_StatusHistory_Transition REFERENCES workflow.WorkflowTransition(WorkflowTransitionId),
    ChangedById     INT             NOT NULL
        CONSTRAINT FK_StatusHistory_ChangedBy REFERENCES dbo.AppUser(AppUserId),
    ChangedDate     DATETIME2(0)    NOT NULL
        CONSTRAINT DF_StatusHistory_ChangedDate DEFAULT SYSUTCDATETIME(),
    PlantId         INT             NOT NULL
        CONSTRAINT FK_StatusHistory_Plant REFERENCES dbo.Plant(PlantId),
    DurationInState INT             NULL,           -- seconds in prior state
    SlaStatus       NVARCHAR(20)    NULL,           -- OnTrack, AtRisk, Breached
    ReasonComment   NVARCHAR(500)   NULL,
    MostRecent      BIT             NOT NULL
        CONSTRAINT DF_StatusHistory_MostRecent DEFAULT 1,
    -- NO temporal versioning (immutable by design)
);
-- Partial unique index: only one MostRecent=1 per entity
CREATE UNIQUE INDEX UX_StatusHistory_MostRecent
    ON workflow.StatusHistory(EntityType, EntityId) WHERE MostRecent = 1;
```

### workflow.ApprovalChain / ApprovalStep / ApprovalRecord

```sql
CREATE TABLE workflow.ApprovalChain (
    ApprovalChainId INT            IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_ApprovalChain PRIMARY KEY CLUSTERED,
    EntityType      NVARCHAR(30)    NOT NULL,
    TransitionId    INT             NOT NULL
        CONSTRAINT FK_ApprovalChain_Transition REFERENCES workflow.WorkflowTransition(WorkflowTransitionId),
    ChainName       NVARCHAR(100)   NOT NULL,
    IsActive        BIT             NOT NULL DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
);

CREATE TABLE workflow.ApprovalStep (
    ApprovalStepId  INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_ApprovalStep PRIMARY KEY CLUSTERED,
    ApprovalChainId INT             NOT NULL
        CONSTRAINT FK_ApprovalStep_Chain REFERENCES workflow.ApprovalChain(ApprovalChainId),
    StepSequence    INT             NOT NULL,
    RequiredRoleId  INT             NOT NULL
        CONSTRAINT FK_ApprovalStep_RequiredRole REFERENCES dbo.Role(RoleId),
    IsActive        BIT             NOT NULL DEFAULT 1,
    -- standard audit + temporal columns (7yr retention)
);

CREATE TABLE workflow.ApprovalRecord (
    ApprovalRecordId INT           IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_ApprovalRecord PRIMARY KEY CLUSTERED,
    ApprovalStepId  INT             NOT NULL
        CONSTRAINT FK_ApprovalRecord_Step REFERENCES workflow.ApprovalStep(ApprovalStepId),
    EntityType      NVARCHAR(30)    NOT NULL,
    EntityId        INT             NOT NULL,
    DecidedById     INT             NULL
        CONSTRAINT FK_ApprovalRecord_DecidedBy REFERENCES dbo.AppUser(AppUserId),
    Decision        NVARCHAR(20)    NULL,           -- Approved, Rejected, Escalated
    DecisionDate    DATETIME2(0)    NULL,
    Comments        NVARCHAR(500)   NULL,
    -- NO temporal (immutable record)
);
```

---

## 4. Security Catalog (Verbatim DDL)

### security.Feature

```sql
CREATE TABLE security.Feature (
    FeatureId       INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Feature PRIMARY KEY,
    FeatureCode     VARCHAR(100)    NOT NULL
        CONSTRAINT UQ_Feature_FeatureCode UNIQUE,
    FeatureName     NVARCHAR(200)   NOT NULL,
    FeatureType     VARCHAR(20)     NOT NULL,       -- Module | Page | Component
    ParentFeatureId INT             NULL
        CONSTRAINT FK_Feature_Parent REFERENCES security.Feature(FeatureId),
    IsEnabled       BIT             NOT NULL DEFAULT 1,
    IsActive        BIT             NOT NULL DEFAULT 1,
    CreatedAtUtc    DATETIME2(3)    NOT NULL DEFAULT SYSUTCDATETIME(),
    ModifiedAtUtc   DATETIME2(3)    NULL
);
```

### security.Permission

```sql
CREATE TABLE security.Permission (
    PermissionId    INT             IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_Permission PRIMARY KEY,
    PermissionCode  VARCHAR(100)    NOT NULL
        CONSTRAINT UQ_Permission_PermissionCode UNIQUE,
    PermissionName  NVARCHAR(200)   NOT NULL,
    PermissionCategory VARCHAR(30)  NOT NULL,       -- Workflow | CRUD | System | DataExport
    ResourceType    VARCHAR(50)     NOT NULL,
    ActionType      VARCHAR(80)     NOT NULL,
    FeatureId       INT             NULL
        CONSTRAINT FK_Permission_Feature REFERENCES security.Feature(FeatureId),
    IsWorkflowPermission BIT        NOT NULL DEFAULT 0,
    IsActive        BIT             NOT NULL DEFAULT 1,
    CreatedAtUtc    DATETIME2(3)    NOT NULL DEFAULT SYSUTCDATETIME(),
    ModifiedAtUtc   DATETIME2(3)    NULL
);
```

### security.RolePermission

```sql
CREATE TABLE security.RolePermission (
    RolePermissionId INT            IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_RolePermission PRIMARY KEY,
    RoleId          INT             NOT NULL
        CONSTRAINT FK_RolePermission_Role REFERENCES dbo.Role(RoleId),
    PermissionId    INT             NOT NULL
        CONSTRAINT FK_RolePermission_Permission REFERENCES security.Permission(PermissionId),
    GrantType       VARCHAR(10)     NOT NULL,       -- Allow | Deny
    IsActive        BIT             NOT NULL DEFAULT 1,
    CreatedAtUtc    DATETIME2(3)    NOT NULL DEFAULT SYSUTCDATETIME(),
    ModifiedAtUtc   DATETIME2(3)    NULL,
    CONSTRAINT UQ_RolePermission UNIQUE (RoleId, PermissionId),
    CONSTRAINT CK_RolePermission_GrantType CHECK (GrantType IN ('Allow','Deny'))
);
```

---

## 5. Key Stored Procedure Signatures

### workflow.usp_TransitionState

```sql
CREATE OR ALTER PROCEDURE workflow.usp_TransitionState
    @CallerAzureOid     UNIQUEIDENTIFIER,
    @EntityType         NVARCHAR(30),
    @EntityId           INT,
    @ToStatusCode       NVARCHAR(30),
    @Comments           NVARCHAR(500) = NULL,
    @TransitionReason   NVARCHAR(500) = NULL
```

**Behavior:**
1. Sets session context via `@CallerAzureOid`
2. Resolves current entity status and target transition
3. Evaluates guard expressions (SeveritySkip, ChildEntityState, Classification, RejectionCount, FastClose)
4. Checks permission via `security.usp_EvaluatePolicy`
5. If approval-gated: creates `PendingApprovalTransition`, returns APPROVAL_REQUIRED (50414)
6. Otherwise: updates entity status, records `StatusHistory`, fires auto-transitions
7. Returns new StatusHistory row

### security.usp_CheckPermission (5-Layer Policy Engine)

```sql
CREATE OR ALTER PROCEDURE security.usp_CheckPermission
    @UserId         INT,
    @PermissionCode VARCHAR(100),
    @PlantId        INT,
    @FeatureCode    VARCHAR(100) = NULL,
    @EntityType     NVARCHAR(30) = NULL,
    @EntityId       INT          = NULL
```

**Layers:**
1. **Feature (L1):** IsEnabled + IsActive + user has RoleFeature grant
2. **Permission (L2):** Deny precedence → requires at least one Allow
3. **Scope (L3):** UserPlantAccess + active role at plant

**Error codes:** 50410 (Feature), 50411 (Permission), 50412 (Scope), 50413 (Constraint), 50414 (Approval), 50415 (Config), 50419 (Unavailable)

### quality.usp_GetDefectKnowledge (Advisory Knowledge Retrieval)

```sql
CREATE OR ALTER PROCEDURE quality.usp_GetDefectKnowledge
    @DefectTypeId       INT,
    @LineTypeId         INT          = NULL,
    @Sections           NVARCHAR(200) = NULL,    -- CSV: 'RootCauses,TestMethods,ContainmentGuidance'
    @SeverityRatingId   INT          = NULL,
    @NcrId              INT          = NULL,
    @CallerAzureOid     UNIQUEIDENTIFIER
```

**Returns:** Up to 9 result sets (one per knowledge domain). Process-specific rows sort before universal rows.

### NCR Gate Procedures (18 total — representative examples)

```sql
-- Create + submit
CREATE OR ALTER PROCEDURE quality.usp_Gate_NCR_Create_Submit
    @CallerAzureOid UNIQUEIDENTIFIER, @PlantId INT, @DefectTypeId INT,
    @Description NVARCHAR(2000), @QuantityAffected DECIMAL(18,4),
    @CorrelationId NVARCHAR(100) = NULL, @Comments NVARCHAR(500) = NULL,
    -- ... 15+ optional parameters
    @NewNcrId INT OUTPUT

-- Gate transitions
CREATE OR ALTER PROCEDURE quality.usp_Gate_NCR_Containment
    @CallerAzureOid UNIQUEIDENTIFIER, @NcrId INT,
    @CorrelationId NVARCHAR(100) = NULL, @Comments NVARCHAR(500) = NULL

CREATE OR ALTER PROCEDURE quality.usp_Gate_NCR_Investigation_Start
    @CallerAzureOid UNIQUEIDENTIFIER, @NcrId INT,
    @DefectOriginId INT = NULL,
    @CorrelationId NVARCHAR(100) = NULL, @Comments NVARCHAR(500) = NULL

CREATE OR ALTER PROCEDURE quality.usp_Gate_NCR_Close
    @CallerAzureOid UNIQUEIDENTIFIER, @NcrId INT,
    @FastClose BIT = 0,
    @CorrelationId NVARCHAR(100) = NULL, @Comments NVARCHAR(500) = NULL
```

**Error Code Pattern:**
```sql
-- Business errors: 5xxxx range
THROW 50400, 'Validation failed', 1;           -- Bad request
THROW 52101, '{"code":52101,"gate":"GATE-02"}', 1;  -- Gate authority denied
THROW 52201, '{"code":52201,"gate":"GATE-03"}', 1;  -- Transition blocked
THROW 52202, '{"code":52202,"gate":"GATE-05"}', 1;  -- Completeness validation
```

---

## 6. API Patterns (Verbatim C# Source)

### DbConnectionFactory

```csharp
public sealed class DbConnectionFactory : IDbConnectionFactory
{
    private readonly string _connectionString;
    private readonly ILogger<DbConnectionFactory> _logger;

    public async Task<SqlConnection> CreateForUserAsync(string callerOid, CancellationToken ct = default)
    {
        var conn = new SqlConnection(_connectionString);
        try
        {
            await conn.OpenAsync(ct);
            await conn.ExecuteAsync(
                "dbo.usp_SetSessionContext",
                new { CallerAzureOid = callerOid },
                commandType: CommandType.StoredProcedure);
            return conn;
        }
        catch { await conn.DisposeAsync(); throw; }
    }

    public async Task<SqlConnection> CreateForServiceAsync(CancellationToken ct = default)
    {
        var conn = new SqlConnection(_connectionString);
        try { await conn.OpenAsync(ct); return conn; }
        catch { await conn.DisposeAsync(); throw; }
    }
}
```

### SqlErrorMapper

```csharp
public static class SqlErrorMapper
{
    private static readonly Dictionary<int, int> BusinessErrorMap = new()
    {
        [50400] = 400, [50401] = 401, [50404] = 404,
        [50410] = 403, [50411] = 403, [50412] = 403,
        [50413] = 403, [50414] = 403, [50415] = 403,
        [50416] = 403, [50417] = 403, [50418] = 403, [50419] = 403,
        [52061] = 400, [52101] = 403, [52201] = 409,
        [52202] = 422, [52203] = 422, [52301] = 409, [52401] = 409,
    };

    public static int? MapToHttpStatus(int sqlErrorNumber)
        => BusinessErrorMap.GetValueOrDefault(sqlErrorNumber);
}
```

### Endpoint Pattern: CREATE with OUTPUT param

```csharp
private static async Task<IResult> CreateNcrQuick(
    HttpContext context, IDbConnectionFactory db,
    CreateNcrQuickRequest request, CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();
    var correlationId = context.Items["CorrelationId"]?.ToString();

    await using var conn = await db.CreateForUserAsync(oid, ct);

    var p = new DynamicParameters();
    p.Add("CallerAzureOid", oid);
    p.Add("PlantId", request.PlantId);
    p.Add("DefectTypeId", request.DefectTypeId);
    // ... all request fields mapped to SP params
    p.Add("NewNcrId", dbType: DbType.Int32, direction: ParameterDirection.Output);

    var result = await conn.QuerySingleOrDefaultAsync(
        "quality.usp_CreateNcrQuick", p, commandType: CommandType.StoredProcedure);

    var newId = p.Get<int>("NewNcrId");
    return Results.Created($"/ncr/{newId}", result);
}
```

### Endpoint Pattern: Gate Transition (anonymous objects)

```csharp
private static async Task<IResult> SubmitNcr(
    int id, HttpContext context, IDbConnectionFactory db,
    GateTransitionRequest? request, CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();
    var correlationId = context.Items["CorrelationId"]?.ToString();

    await using var conn = await db.CreateForUserAsync(oid, ct);

    var result = await conn.QuerySingleOrDefaultAsync(
        "quality.usp_SubmitNcr",
        new { CallerAzureOid = oid, NcrId = id,
              CorrelationId = correlationId, Comments = request?.Comments },
        commandType: CommandType.StoredProcedure);

    return Results.Ok(result);
}
```

### Endpoint Pattern: View (QueryAsync)

```csharp
private static async Task<IResult> GetNcrOperationalQueue(
    HttpContext context, IDbConnectionFactory db, CancellationToken ct)
{
    var oid = EasyAuthHandler.GetCallerOid(context.User);
    if (oid is null) return Results.Unauthorized();

    await using var conn = await db.CreateForUserAsync(oid, ct);
    var rows = await conn.QueryAsync(
        "SELECT * FROM quality.vw_NcrOperationalQueue",
        commandType: CommandType.Text);

    return Results.Ok(rows);
}
```

### DTO Pattern: C# Records with Default Parameters

```csharp
// Required fields = no default. Optional fields = nullable with default null.
public record CreateNcrQuickRequest(
    int PlantId,
    int DefectTypeId,
    string Description,
    decimal QuantityAffected,
    string? Comments = null,
    int? PriorityLevelId = null,
    int? SeverityRatingId = null,
    int? CustomerId = null,
    int? PartId = null,
    int? SupplierId = null,
    string? LotNumber = null,
    string? NcrType = null);

// Gate transition: minimal DTOs
public record GateTransitionRequest(string? Comments = null);
public record StartInvestigationRequest(int? DefectOriginId = null, string? Comments = null);
public record CloseNcrRequest(bool? FastClose = null, string? Comments = null);
public record VoidNcrRequest(string? ReasonComment = null, string? Comments = null);

// Edge transitions: required ReasonComment for audit trail
public record RejectVerificationRequest(string ReasonComment, string? Comments = null);
public record ReopenNcrRequest(string ReasonComment, string? Comments = null);
```

### Endpoint Registration Pattern

```csharp
public static WebApplication MapNcrEndpoints(this WebApplication app)
{
    var group = app.MapGroup("/ncr")
        .WithTags("NCR")
        .RequireAuthorization();

    group.MapPost("/", CreateNcrQuick)
        .WithName("CreateNcrQuick")
        .WithSummary("Create NCR with minimum required fields")
        .Produces<object>(201)
        .ProducesProblem(400);

    group.MapPost("/{id:int}/submit", SubmitNcr)
        .WithName("SubmitNcr")
        .WithSummary("Submit NCR (DRAFT->OPEN)")
        .Produces<object>(200)
        .ProducesProblem(409);

    // ... pattern repeats for all 25 endpoints
    return app;
}
```

---

## 7. Frontend Architecture (Planned — No Source Code Yet)

### Locked Technology Stack

| Library | Version | Purpose |
|---------|---------|---------|
| Next.js | ^15.x | App Router, server components, server actions |
| React | ^19.x | UI framework |
| TypeScript | ^5.x | Type safety (strict mode) |
| Tailwind CSS | ^4.x | Utility-first styling |
| shadcn/ui | Latest | Component library (source files, fully modifiable) |
| TanStack Query | ^5.x | Server state management (ONLY data-fetching pattern) |
| TanStack Table | ^8.x | Headless table (sorting, filtering, pagination) |
| react-hook-form | ^7.x | Form state management |
| zod | ^3.x | Schema validation (courtesy — gate procs are authoritative) |
| recharts | ^2.x | Charts and data visualization |
| nuqs | Latest | Type-safe URL search parameters |
| next-themes | Latest | Dark/light mode |
| framer-motion | ^11.x | Animations |

### Planned Project Structure

```
src/
├── app/
│   ├── (auth)/                     ← Protected route group
│   │   ├── dashboard/
│   │   ├── layout.tsx
│   │   └── [domain modules]/       ← NCR, CAPA, Complaint, SCAR, etc.
│   ├── login/
│   └── layout.tsx
├── components/
│   ├── ui/                         ← shadcn/ui source files
│   ├── data-tables/
│   ├── forms/
│   ├── charts/
│   └── layout/
├── hooks/
│   ├── queries/                    ← TanStack Query hooks
│   └── mutations/                  ← TanStack mutation hooks
├── lib/
│   ├── api.ts                      ← Server-side only, token forwarding
│   ├── auth.ts
│   └── utils.ts
├── types/
│   └── api-openapi.snapshot.json   ← Contract from sf-quality-api
└── styles/
    └── globals.css
```

### Key Frontend Constraints

1. **Browser components NEVER call the API directly.** All API access goes through `src/lib/api.ts` (server-side) via TanStack Query hooks.
2. **No business logic in frontend.** UI renders API response state. Validation is courtesy only — gate procs are authoritative.
3. **Form pattern:** react-hook-form + zod schema for client-side UX → API call → SP validates authoritatively.
4. **Data tables:** TanStack Table for all tabular data (sorting, filtering, pagination, row selection).
5. **Auth:** Azure Easy Auth at App Service level. No MSAL, no NextAuth. Server reads `X-MS-CLIENT-PRINCIPAL` headers.

---

## 8. Existing Knowledge Extension Pattern (Model for Forms Module)

The defect knowledge system (Migrations 125-130) provides a **direct architectural precedent** for the forms module. Study this pattern:

### 9 Knowledge Tables (all follow same structure)

```sql
-- Example: dbo.DefectTypeRootCause
CREATE TABLE dbo.DefectTypeRootCause (
    DefectTypeRootCauseId   INT IDENTITY(1,1) NOT NULL
        CONSTRAINT PK_DefectTypeRootCause PRIMARY KEY CLUSTERED,
    DefectTypeId    INT         NOT NULL
        CONSTRAINT FK_DTRC_DefectType REFERENCES dbo.DefectType(DefectTypeId),
    LineTypeId      INT         NULL,               -- NULL = universal (applies to all line types)
        CONSTRAINT FK_DTRC_LineType REFERENCES dbo.LineType(LineTypeId),
    CauseCode       NVARCHAR(30)    NOT NULL,
    CauseName       NVARCHAR(200)   NOT NULL,
    CauseDescription NVARCHAR(500)  NULL,
    IshikawaCategoryCode NVARCHAR(20) NULL,         -- MAN/MACHINE/MATERIAL/METHOD/MEASUREMENT/ENVIRONMENT
    CauseLevelCode  NVARCHAR(20)    NULL,           -- ROOT/CONTRIBUTING/NODETECT/SYSTEMIC
    Likelihood      NVARCHAR(10)    NULL,           -- HIGH/MEDIUM/LOW
    SortOrder       INT             NOT NULL DEFAULT 0,
    IsActive        BIT             NOT NULL DEFAULT 1,
    IsVerified      BIT             NOT NULL DEFAULT 0,
    VerifiedBy      INT             NULL,
    VerifiedDate    DATETIME2(0)    NULL,
    -- standard audit columns
    CONSTRAINT UQ_DTRC_DefectType_LineType_CauseCode UNIQUE (DefectTypeId, LineTypeId, CauseCode)
);
```

**Key pattern:** `LineTypeId NULL = universal`. The knowledge views return process-specific rows BEFORE universal rows, letting consumers show the most relevant data first.

### Knowledge Retrieval View Pattern

```sql
CREATE VIEW dbo.vw_DefectKnowledge_RootCauses AS
SELECT
    rc.DefectTypeRootCauseId,
    rc.DefectTypeId,
    dt.DefectCode,
    dt.DefectName,
    rc.LineTypeId,
    lt.LineTypeCode,
    lt.LineTypeName,
    rc.CauseCode, rc.CauseName, rc.CauseDescription,
    rc.IshikawaCategoryCode, rc.CauseLevelCode, rc.Likelihood,
    rc.SortOrder, rc.IsActive, rc.IsVerified, rc.VerifiedBy, rc.VerifiedDate
FROM dbo.DefectTypeRootCause rc
    INNER JOIN dbo.DefectType dt ON rc.DefectTypeId = dt.DefectTypeId
    LEFT JOIN dbo.LineType lt ON rc.LineTypeId = lt.LineTypeId
WHERE rc.IsActive = 1;
```

---

## 9. Contract Manifest (Procedure & View Index)

### Stored Procedures Available (80 total, representative list)

| Schema | Procedure | Purpose |
|--------|-----------|---------|
| dbo | usp_SetSessionContext | Set RLS session context from Azure OID |
| dbo | usp_GenerateDocumentNumber | Auto-number documents by plant |
| quality | usp_CreateNCR | Full NCR create |
| quality | usp_CreateNcrQuick | Minimal NCR create |
| quality | usp_UpdateNCR | Update NCR fields |
| quality | usp_DeleteNCR | Soft delete NCR |
| quality | usp_Gate_NCR_Create_Submit | Create + submit in one transaction |
| quality | usp_Gate_NCR_Containment | Complete containment gate |
| quality | usp_Gate_NCR_Investigation_Start | Start investigation gate |
| quality | usp_Gate_NCR_Investigation_Complete | Complete investigation gate |
| quality | usp_Gate_NCR_Disposition | Record disposition gate |
| quality | usp_Gate_NCR_Verify_Effectiveness | Effectiveness verification gate |
| quality | usp_Gate_NCR_Close | Close NCR gate |
| quality | usp_Gate_NCR_Void | Void NCR gate |
| quality | usp_GetDefectKnowledge | Advisory knowledge retrieval |
| quality | usp_CreateCAPA | Create CAPA |
| quality | usp_CreateComplaint | Create complaint |
| quality | usp_CreateSCARecord | Create SCAR |
| quality | usp_CreateAuditFinding | Create audit finding |
| quality | usp_CreateEightD | Create 8D report |
| workflow | usp_TransitionState | Core state machine |
| workflow | usp_RecordStatusHistory | Immutable status audit |
| workflow | usp_CheckPermission | 5-layer policy check |
| workflow | usp_StartApprovalProcess | Initiate approval chain |
| workflow | usp_SubmitApprovalDecision | Submit approval decision |
| workflow | usp_EscalateApproval | Escalate pending approval |
| workflow | usp_RecallApprovalProcess | Recall in-flight approval |
| workflow | usp_EvaluateEscalationRules | Batch escalation processor |
| security | usp_CheckPermission | 5-layer policy evaluation |
| security | usp_EvaluatePolicy | Full 5-layer with constraints |
| integration | usp_AcknowledgeNcrOutboxEvent | Outbox consumer ack |
| integration | usp_GetPendingNotifications | Consumer-aware polling |

### Views Available (36 total, representative list)

| Schema | View | Purpose |
|--------|------|---------|
| quality | vw_OpenNCRSummary | Dashboard: open NCRs |
| quality | vw_NcrOperationalQueue | Queue with SLA status, defect knowledge |
| quality | vw_NcrDispositionBalance | Quantity reconciliation |
| quality | vw_NcrHoldAging | Severity-linked hold aging |
| quality | vw_NcrCustomerApprovalAging | Customer SLA breach tracking |
| quality | vw_NcrGateAudit | Complete gate transition timeline |
| quality | vw_NcrNotificationOutbox | Consumer-agnostic NCR event stream |
| dbo | vw_DefectKnowledge_RootCauses | Knowledge: root cause hypotheses |
| dbo | vw_DefectKnowledge_InvestigationSteps | Knowledge: 8D checklist |
| dbo | vw_DefectKnowledge_TestMethods | Knowledge: ASTM/CQI-12 methods |
| dbo | vw_DefectKnowledge_DispositionGuidance | Knowledge: disposition by severity |
| dbo | vw_DefectKnowledge_ContainmentGuidance | Knowledge: containment actions |
| dbo | vw_DefectKnowledge_ConfusionPairs | Knowledge: confused defect pairs |
| dbo | vw_DefectKnowledge_ParameterChecks | Knowledge: process parameters |
| dbo | vw_DefectKnowledge_StandardReferences | Knowledge: CQI-12/ASTM refs |
| dbo | vw_DefectKnowledge_ControlPoints | Knowledge: preventive controls |

---

## 10. Cross-Repo Contract Chain

```
sf-quality-db                          sf-quality-api                        sf-quality-app
─────────────                          ──────────────                        ──────────────
db-contract-manifest.json  ──────►  db-contract-manifest.snapshot.json
(80 procs, 36 views)                api-openapi.publish.json  ──────►  api-openapi.snapshot.json
                                    (27 endpoints, v0.2.0)
```

**Validation scripts:**
- `Test-DbContractReferences.ps1` — API references only valid DB objects
- `Test-OpenApiPublication.ps1` — OpenAPI artifact is structurally valid
- `Test-ApiContractReferences.ps1` — App references only valid API endpoints
- `Invoke-CycleChecks.ps1` — Cross-repo drift prevention

---

## 11. Migration Numbering & Phase Context

**Current highest migration:** `130_taxonomy_v3_cleanup.sql`

**Planned future phases (from Execution_Plan.md):**
- DB Phase 23: Platform Governance (TBD numbering)
- DB Phase 24: Substrate Integration (TBD numbering)
- DB Phases 25-33: Reference Architecture v3.0 patterns

**The Forms module would logically be a new milestone (v3.0 or v4.0) with its own phase numbering.** Migration numbers should continue sequentially from the highest existing number at time of implementation.

---

## 12. RLS Pattern (Row-Level Security)

All plant-scoped tables must have RLS predicates:

```sql
-- Filter predicate (SELECT): only return rows matching session plant
CREATE SECURITY POLICY security.PlantIsolationPolicy
    ADD FILTER PREDICATE security.fn_PlantAccessPredicate(PlantId)
        ON quality.NonConformanceReport,
    -- ... repeated for each table

-- Block predicate (INSERT/UPDATE/DELETE): prevent writes outside plant
    ADD BLOCK PREDICATE security.fn_PlantWriteBlockPredicate(PlantId)
        ON quality.NonConformanceReport AFTER INSERT,
    ADD BLOCK PREDICATE security.fn_PlantWriteBlockPredicate(PlantId)
        ON quality.NonConformanceReport AFTER UPDATE;
```

**Convention:** Any new table with a `PlantId` column MUST be added to the RLS security policy.
