# Architecture

> **Architecture Note (2026-02):** Some sections reference Power Automate as a consumer. The notification consumption mechanism is now TBD. The frontend is Next.js 15 + ASP.NET Core 9 API, not Power Apps.

**Analysis Date:** 2026-02-22

## Pattern Overview

**Overall:** Database-centric workflow enforcement with migration-driven schema evolution, extended with a structured knowledge intelligence layer

**Key Characteristics:**
- Database as the integration API surface (no middleware tier)
- Stored procedures are the mutation contract (external clients call SPs, not direct table writes)
- Row-level security provides multi-plant isolation at the data layer
- Temporal tables capture complete audit history with 7-year retention
- Workflow state machine enforces lifecycle governance through deterministic transition rules
- Phase-based migration model with immutable history and additive-only changes
- [v2.0] Six-layer cascade: Taxonomy → Classification → Knowledge → Decision Support → Transactions → Analytics
- [v2.0] Structured defect knowledge guiding investigation, disposition, and root cause analysis at every NCR gate

## Layers

**Database Schema Layer:**
- Purpose: Organize entities by domain and system responsibility
- Location: Defined in `database/migrations/001_schemas.sql`
- Contains: 7 schemas (dbo, quality, rca, workflow, apqp, security, audit)
- Depends on: SQL Server infrastructure
- Used by: All tables, views, stored procedures, and functions

**Data Access Control Layer:**
- Purpose: Enforce plant-based row isolation and write permissions
- Location: `security` schema
- Contains: RLS predicate functions (`security.fn_PlantAccessPredicate`, `security.fn_PlantWriteBlockPredicate`), security policies (`security.PlantIsolationPolicy`)
- Depends on: SESSION_CONTEXT set by `dbo.usp_SetSessionContext`, `dbo.UserPlantAccess`, `dbo.UserRole`
- Used by: All plant-scoped tables (automatic filtering on SELECT/INSERT/UPDATE/DELETE)

**Authorization Layer:**
- Purpose: Permission-driven security with 5-layer policy engine (Feature → Permission → Scope → Constraints → Workflow)
- Location: `security` schema
- Contains: Permission catalog (`security.Permission`, `security.RolePermission`), policy engine SPs (`security.usp_CheckPermission`, `security.usp_EvaluatePolicy`), authority rules (`quality.DispositionAuthorityRule`, `workflow.NcrSeverityThreshold`)
- Depends on: Data access control layer, workflow state machine
- Used by: Gate SPs, workflow transition SP, approval lifecycle

**Domain Entity Layer:**
- Purpose: Quality event entities with temporal history and audit logging
- Location: `quality` schema (NCR, CAPA, complaints, etc.), `rca` schema (8D, Fishbone, 5 Whys, etc.)
- Contains: System-versioned temporal tables with history in `audit` schema, audit triggers generating `audit.AuditLog` rows
- Depends on: Reference/dimension tables in `dbo`, workflow state machine, RLS predicates
- Used by: CRUD stored procedures, workflow transition SP, dashboard views

**Reference & Dimension Layer:**
- Purpose: Shared lookup tables, topology metadata, defect taxonomy
- Location: `dbo` schema
- Contains: Plant, StatusCode, PriorityLevel, DefectType, Customer, Supplier, Part, ProcessArea, ProductionLine, Equipment, LayerType, CoatingSystem, etc.
- Depends on: Schemas only
- Used by: Domain entities (FK relationships), workflow configuration, RLS predicates, knowledge layer

**Quality Intelligence Layer (v2.0):**
- Purpose: Structured knowledge that guides investigation, disposition, and root cause analysis decisions
- Location: `dbo` schema (knowledge tables), `analytics` schema (analytical views)
- Contains: 9 knowledge extension tables (DefectTypeRootCause, DefectTypeInvestigationStep, DefectTypeTestMethod, DefectTypeDispositionGuidance, DefectTypeContainmentGuidance, DefectTypeConfusionPair, DefectTypeParameterCheck, DefectTypeStandardReference, DefectTypeControlPoint), advisory retrieval SP (`quality.usp_GetDefectKnowledge`), knowledge views, analytical views
- Depends on: Reference & Dimension layer (DefectType, LineType FKs), classification bridges (DefectTypeLineType, DefectTypeProcessFamily)
- Used by: Application surface (gate SPs query knowledge as advisory context), operational views (DefectType info in triage queue), analytics views (cross-process Pareto, root cause distribution)
- Architecture: Six-layer cascade model — Taxonomy (L1) → Classification (L2) → Knowledge (L3) → Decision Support (L4) → Transactions (L5) → Analytics (L6). Defect knowledge is the first implementation; same pattern extends to equipment, supplier, process domains.
- Key pattern: Universal rows (LineTypeId = NULL) provide process-agnostic knowledge; process-specific rows (LineTypeId = ECOAT/POWDER/LIQUID) add mechanism-specific detail. Retrieval precedence: process-specific first, universal second, merged without duplicates.
- Vision document: `docs/v2.0-quality-intelligence-platform-vision.md`

**Workflow State Machine Layer:**
- Purpose: Lifecycle governance and transition rules
- Location: `workflow` schema
- Contains: WorkflowProcess, WorkflowState, WorkflowTransition (with guards), StatusHistory, SlaConfiguration, EscalationRule, ApprovalChain
- Depends on: Reference layer (StatusCode, Role), authorization layer (Permission)
- Used by: `workflow.usp_TransitionState`, gate SPs, approval SPs, operational views

**Application Surface Layer:**
- Purpose: SP and view interface for external consumption
- Location: `quality` schema (SPs and views), `workflow` schema (SPs), `rca` schema (SPs)
- Contains: 18 gate SPs (NCR lifecycle), 6 CRUD SP sets (NCR, CAPA, Complaint, SCAR, AuditFinding, 8D), 8 dashboard views, 4 traceability views, 9 KPI views, workflow/approval/escalation SPs
- Depends on: All layers below
- Used by: External consumers (primarily ASP.NET Core API and frontend clients through API boundary)

**Audit & History Layer:**
- Purpose: Temporal versioning and audit trail
- Location: `audit` schema
- Contains: History tables (clustered columnstore for compression), `audit.AuditLog` (trigger-generated change log)
- Depends on: Domain entity layer (temporal versioning), audit trigger utility (`dbo.usp_CreateAuditTrigger`)
- Used by: Compliance reporting, change investigation, temporal queries

## Data Flow

**NCR Creation Flow (Example):**

1. Client calls `quality.usp_CreateNCR` with `@CallerAzureOid` and NCR details
2. SP calls `dbo.usp_SetSessionContext` to establish SESSION_CONTEXT (UserId, PlantId, IsAdmin)
3. SP validates inputs and calls `dbo.usp_GenerateDocumentNumber` for NCR number
4. SP inserts into `quality.NonConformanceReport` (RLS BLOCK predicate enforces plant match)
5. Audit trigger fires, writes to `audit.AuditLog`
6. Temporal versioning captures row in `audit.NonConformanceReportHistory`
7. SP inserts initial status into `workflow.StatusHistory` with MostRecent=1
8. Transaction commits, returns NonConformanceReportId

**Workflow Transition Flow:**

1. Client calls `workflow.usp_TransitionState` with EntityType, EntityId, and ToStatusCode
2. SP validates transition exists in `workflow.WorkflowTransition` for current state → target state
3. SP checks RequiredPermissionId against `security.RolePermission` (or RequiredRoleId fallback)
4. SP evaluates guard (SeveritySkip, ChildEntityState, Classification, RejectionCount, FastClose)
5. If approval-gated transition, creates `workflow.PendingApprovalTransition` and blocks
6. Otherwise, updates entity StatusCodeId, inserts `workflow.StatusHistory` with MostRecent=1, clears old MostRecent
7. Transaction commits

**Knowledge Retrieval Flow (v2.0):**

1. Client calls `quality.usp_GetDefectKnowledge` with `@DefectTypeId`, `@LineTypeId` (optional), `@Sections` (optional)
2. SP queries knowledge tables, applying retrieval precedence: process-specific rows (matching LineTypeId) first, universal rows (NULL LineTypeId) second
3. Returns multiple result sets — one per knowledge section (root causes, investigation steps, test methods, disposition guidance, containment guidance, confusion pairs, parameter checks, standard references, control points)
4. Alternatively, client queries knowledge views directly for ad-hoc access (one view per knowledge table, pre-joined with DefectType and LineType)
5. Knowledge is advisory — guides but does not force decisions; gate SPs remain the authoritative mutation contract

**State Management:**

- Session identity: Caller establishes via `@CallerAzureOid` → `usp_SetSessionContext` → SESSION_CONTEXT
- Workflow state: Tracked in entity StatusCodeId + `workflow.StatusHistory` with MostRecent flag
- Audit state: Temporal `ValidFrom`/`ValidTo` for time-travel queries, `audit.AuditLog` for change log

## Key Abstractions

**EntityTypeRegistry:**
- Purpose: Normalize entity type codes across workflow, status, approval, and escalation tables
- Examples: `dbo.EntityTypeRegistry`
- Pattern: FK target for EntityType fields, prevents CHECK constraint drift, enables centralized entity metadata

**DocumentNumbering:**
- Purpose: Deterministic, plant-scoped, year-scoped document number generation
- Examples: `dbo.DocumentNumberConfig`, `dbo.DocumentNumberSequence`, `dbo.usp_GenerateDocumentNumber`
- Pattern: Sequence per (DocumentTypeCode, PlantId, Year), formatted output via template

**StatusCode:**
- Purpose: Shared status vocabulary across all entity types
- Examples: `dbo.StatusCode` (EntityType, StatusCode, StatusName, StatusCategory)
- Pattern: Single table with EntityType discriminator, used by WorkflowState to map statuses into workflow positions

**RLS Predicates:**
- Purpose: Plant-based row filtering and write blocking
- Examples: `security.fn_PlantAccessPredicate` (filter), `security.fn_PlantWriteBlockPredicate` (block)
- Pattern: Table-valued functions with SCHEMABINDING, applied via security policy to all plant-scoped tables

**Workflow Guards:**
- Purpose: Conditional transition logic without dynamic SQL
- Examples: SeveritySkip (low-severity fast-path), ChildEntityState (blocks close until children closed), Classification (NCR type routing), RejectionCount (supplier rejection threshold), FastClose (reconciliation + approval + CAPA checks)
- Pattern: GuardType + GuardExpression in WorkflowTransition, evaluated via CASE dispatch in `usp_TransitionState`

**Permission-Driven Authorization:**
- Purpose: Fine-grained access control with plant-scoped constraints
- Examples: `security.Permission`, `security.RolePermission`, `security.usp_CheckPermission`, `security.usp_EvaluatePolicy`
- Pattern: 5-layer policy stack (Feature → Permission → Scope → Constraints → Workflow), dual-path rollout with RoleId fallback

**Gate Stored Procedures:**
- Purpose: Lifecycle-specific mutation contracts with built-in authorization and reconciliation
- Examples: `quality.usp_Gate_CreateNCR`, `quality.usp_Gate_SubmitForApproval`, `quality.usp_Gate_ProcessDisposition`, `quality.usp_Gate_CloseNCR`
- Pattern: Single-responsibility SPs for each NCR lifecycle gate, TVP contract for disposition lines, authority/reconciliation enforcement, consistent error codes

## Entry Points

**Migration Deployment:**
- Location: `database/deploy/Apply-Phase*.ps1`
- Triggers: Manual execution by operator (dev/staging/prod target)
- Responsibilities: Acquire Entra token, open SQL connection, execute migration batch sequence, run verify/smoke tests

**Session Context Initialization:**
- Location: `database/migrations/007_session_context_sp.sql` → `dbo.usp_SetSessionContext`
- Triggers: Called as first statement by all mutation SPs
- Responsibilities: Resolve AzureAdObjectId → AppUserId, set SESSION_CONTEXT (UserId, PlantId, IsAdmin, DisplayName, Email)

**CRUD Surface:**
- Location: `database/migrations/058_crud_ncr_capa.sql`, `059_crud_complaint_scar.sql`, `060_crud_audit_eightd.sql`
- Triggers: External client calls (API layer and approved integration consumers)
- Responsibilities: Create/Update/Delete operations on quality entities with document number generation, status history initialization, child entity validation

**Gate SP Surface:**
- Location: `database/migrations/112_gate_create_submit.sql` through `118_gate_edge_transitions.sql`
- Triggers: External client calls for NCR lifecycle operations
- Responsibilities: Lifecycle-specific mutations (create, submit, containment, investigation, disposition, verification, close, void) with authority/reconciliation/workflow enforcement

**Workflow Transition:**
- Location: `database/migrations/061_workflow_transition_sp.sql` → `workflow.usp_TransitionState`
- Triggers: Called by gate SPs or directly by clients for status changes
- Responsibilities: Central state machine logic (validate transition, check permissions, evaluate guards, update status, record history)

**Dashboard/Reporting:**
- Location: `database/migrations/067_dashboard_views.sql`, `068_kpi_analytics_views.sql`, `069_traceability_views.sql`
- Triggers: SELECT queries from external BI tools, dashboards, Power BI
- Responsibilities: Aggregated views of open NCRs/CAPAs/Complaints, action items, aging analysis, KPIs, traceability links

**Knowledge Retrieval (v2.0):**
- Location: `quality.usp_GetDefectKnowledge` (advisory SP), knowledge views in `dbo` schema, analytics views in `analytics` schema
- Triggers: External client calls alongside gate SP operations (e.g., fetch knowledge context when starting investigation)
- Responsibilities: Structured knowledge retrieval for defect investigation, disposition guidance, root cause hypothesis ranking, confusion pair differentiation, process parameter checks

## Error Handling

**Strategy:** Deterministic error codes with THROW, consistent transaction rollback, XACT_ABORT enforcement

**Patterns:**
- Input validation: `THROW 50400, N'Descriptive message', 1;`
- Authentication failure: `THROW 50401, N'User not found or inactive', 1;`
- Authorization failure: `THROW 50410-50419, N'Permission denied', 1;` (policy layer)
- Resource not found: `THROW 50404, N'Entity not found', 1;`
- Business rule violation: `THROW 50500-50599, N'Rule description', 1;`
- Transition blocked: `THROW 52201, N'Transition not allowed', 1;` (gate SPs)
- Authority denied: `THROW 52101, N'Authorization failed', 1;` (gate SPs)
- All mutation SPs use `SET XACT_ABORT ON; BEGIN TRY ... BEGIN TRANSACTION ... COMMIT ... END TRY BEGIN CATCH ... ROLLBACK ... ;THROW END CATCH`

## Cross-Cutting Concerns

**Logging:** Trigger-based audit logging to `audit.AuditLog` (who, what, when, entity context), temporal history for time-travel queries

**Validation:** Input validation at SP boundary with THROW 50400, FK constraint enforcement at table level, CHECK constraints for domain rules, RLS policy enforcement for plant isolation

**Authentication:** Entra ID (Azure AD) via SESSION_CONTEXT, `dbo.usp_SetSessionContext` resolves AzureAdObjectId → AppUserId, admin bypass via IsAdmin flag

**Authorization:** Permission-driven policy engine (`security.usp_CheckPermission`, `security.usp_EvaluatePolicy`) with plant-scoped constraints, RoleId fallback for dual-path rollout, workflow transition authorization via RequiredPermissionId/RequiredRoleId

**Data Isolation:** RLS predicates applied to all plant-scoped tables (FILTER + BLOCK), SESSION_CONTEXT(N'PlantId') enforced, Admin bypass for cross-plant visibility

**Audit Trail:** Temporal versioning on all entity tables (7-year retention, clustered columnstore history), audit triggers on all mutable tables, StatusHistory for workflow changes with MostRecent flag

**Idempotency:** All migrations use IF NOT EXISTS guards, CREATE OR ALTER for SPs/views/functions, MERGE for seed data upserts, security policy DROP/rebuild choreography for predicate updates

**Deployment Validation:** Static rules checker (`database/deploy/Test-SqlStaticRules.ps1`), verify queries (`database/deploy/Verify-Phase*.sql`), smoke tests (`database/deploy/Smoke-Phase*.sql`), enforcement registry checker (`database/deploy/Test-EnforcementRegistry.ps1`), CI pipeline (`.github/workflows/sql-validation.yml`)

---

*Architecture analysis: 2026-02-22 — metadata refreshed for current integration model and phase state.*
