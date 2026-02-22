# Enterprise Architecture Conformance Assessment and Authoritative Remediation Plan

Date: 2026-02-22  
Workspace scope:
- `C:/Dev/sf-quality`
- `C:/Dev/sf-quality-db`
- `C:/Dev/sf-quality-api`
- `C:/Dev/sf-quality-app`

## 1. Executive Summary

The current platform is a **single-tenant, SQL-centric modular monolith** with strong plant-level isolation and a thin API layer. It shows meaningful progress toward modularity and eventing, but falls short of strict bounded-context enforcement, generalized event-driven decoupling, and hexagonal ports/adapters separation.

The most critical risk is the **workflow engine acting as a cross-domain god module**. It directly reads/writes multiple domain tables and is also bypassed by direct writes from quality procedures. This creates high change-coupling and raises regression risk whenever a domain schema evolves.

The most effective low-regret path is:
1. Harden boundaries first (adapter-proc pattern, stop cross-schema direct writes).
2. Generalize outbox/events next (without breaking synchronous gate paths).
3. Deepen ABAC from plant to department/jurisdiction.
4. Add API ports/adapters to remove endpoint-level SQL coupling.
5. Apply explicit hard-FK vs soft-reference policy for cross-context links (inspection-NCR first).

## 2. Current State Assessment

### 2.1 Architecture posture
- **Deployment and tenancy**: Explicit single-tenant model.
  - Evidence: `Reference_Architecture/README.md:127`
  - Evidence: `WORKSPACE-STRUCTURE.md:271`
- **Overall style**: Smart database + thin API.
  - Business rules and state machine enforcement are heavily implemented in SQL stored procedures.
  - API largely orchestrates caller context and delegates to SQL contracts.

### 2.2 Authorization posture vs target ABAC model
- **Strong alignment**: Plant-level ABAC via `SESSION_CONTEXT` + RLS + policy SPs.
  - Evidence: `C:/Dev/sf-quality-db/database/migrations/006_rls_predicates.sql:44`
  - Evidence: `C:/Dev/sf-quality-db/database/migrations/096_create_policy_engine_sps.sql:189`
- **Gap**: Department/jurisdiction ABAC is not materially enforced in primary predicates or policy pipeline.
  - `dbo.Department` exists as a data model, but predicate checks are plant-centric.
  - Evidence: `C:/Dev/sf-quality-db/database/migrations/005_security_tables.sql:91`
  - Evidence: `C:/Dev/sf-quality-db/database/migrations/096_create_policy_engine_sps.sql:151`
  - Evidence: `C:/Dev/sf-quality-db/database/migrations/007_session_context_sp.sql:67`

## 3. Bounded Context and Module Mapping

| Context / Module | Primary responsibility | Key evidence |
|---|---|---|
| `quality` | NCR/CAPA/complaint/SCAR/audit-finding domain records | `C:/Dev/sf-quality-db/database/migrations/028_ncr_tables.sql:102`, `C:/Dev/sf-quality-db/database/migrations/029_capa_tables.sql:96`, `C:/Dev/sf-quality-db/database/migrations/031_complaint_scar_audit.sql:436` |
| `rca` | Root-cause methods (8D, fishbone, etc.) | `C:/Dev/sf-quality-db/database/migrations/037_eightd_tables.sql:86`, `C:/Dev/sf-quality-db/database/migrations/038_fishbone_tables.sql:36` |
| `workflow` | State machine and status history | `C:/Dev/sf-quality-db/database/migrations/046_workflow_state_machine.sql:68`, `C:/Dev/sf-quality-db/database/migrations/048_status_tracking_tables.sql:108` |
| `security` | Permission catalog, role-permission constraints, policy engine, RLS predicates | `C:/Dev/sf-quality-db/database/migrations/091_create_security_catalog.sql:27`, `C:/Dev/sf-quality-db/database/migrations/096_create_policy_engine_sps.sql:36`, `C:/Dev/sf-quality-db/database/migrations/006_rls_predicates.sql:44` |
| `integration` | Notification outbox polling + ack ledger | `C:/Dev/sf-quality-db/database/migrations/119_phase16_integration_schema_ack_table.sql:28`, `C:/Dev/sf-quality-db/database/migrations/121_phase16_outbox_view_and_sps.sql:144` |
| `audit` | Cross-domain audit logging and history | `C:/Dev/sf-quality-db/database/migrations/003_audit_log.sql:25` |
| `inspection` (proposed package) | Inspection templates, execution, NCR linkage | `Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/db/migrations/131_create_inspection_schema.sql:12` |

## 4. Architectural Alignment and Violations

## 4.1 Modular Monolith (Strict Bounded Contexts)

### Strong alignment

1. Clear schema-level context partitioning.

```sql
-- C:/Dev/sf-quality-db/database/migrations/001_schemas.sql:25-52
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'quality')
    EXEC(N'CREATE SCHEMA quality');
...
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'workflow')
    EXEC(N'CREATE SCHEMA workflow');
...
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'security')
    EXEC(N'CREATE SCHEMA security');
```

2. Existing internal API boundary usage in some flows (quality -> workflow transition SP call).

```sql
-- C:/Dev/sf-quality-db/database/migrations/112_gate_create_submit.sql:237-242
EXEC workflow.usp_TransitionState
    @CallerAzureOid = @CallerAzureOid,
    @EntityType     = N'NCR',
    @EntityId       = @NcrId,
    @ToStatusCode   = N'NCR-OPEN',
    @Comments       = @Comments;
```

### Violations

1. Workflow SP directly queries and updates entity tables across multiple contexts (tight bidirectional coupling).

```sql
-- C:/Dev/sf-quality-db/database/migrations/061_workflow_transition_sp.sql:59-70
IF @EntityType = N'NCR'
BEGIN
    SELECT ... FROM quality.NonConformanceReport ...
END
ELSE IF @EntityType = N'CAPA'
BEGIN
    SELECT ... FROM quality.CorrectiveAction ...
END
```

```sql
-- C:/Dev/sf-quality-db/database/migrations/061_workflow_transition_sp.sql:338-344
IF @EntityType = N'NCR'
    UPDATE quality.NonConformanceReport ...
ELSE IF @EntityType = N'CAPA'
    UPDATE quality.CorrectiveAction ...
```

2. Quality module bypasses workflow-owned API and writes workflow-owned table directly.

```sql
-- C:/Dev/sf-quality-db/database/migrations/112_gate_create_submit.sql:129-138
INSERT INTO workflow.StatusHistory (
    EntityType, EntityId, PlantId,
    FromStatusCodeId, ToStatusCodeId, TransitionId,
    ChangedById, MostRecent, CreatedBy
)
VALUES (N'NCR', @NewNcrId, @PlantId, NULL, @DraftStatusId, NULL, @UserId, 1, @UserId);
```

3. Proposed inspection package introduces hard cross-context FKs to NCR context.

```sql
-- C:/Dev/sf-quality/Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/db/migrations/146_create_inspection_instance.sql:74-75
AutoNcrId INT NULL
    CONSTRAINT FK_Inspection_AutoNcr REFERENCES quality.NonConformanceReport(NonConformanceReportId),
```

```sql
-- C:/Dev/sf-quality/Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/db/migrations/148_create_inspection_ncr_link.sql:22-23
NcrId INT NOT NULL
    CONSTRAINT FK_InspectionNcrLink_Ncr REFERENCES quality.NonConformanceReport(NonConformanceReportId),
```

Assessment: **Partially aligned, with high-severity coupling hot spots**.

## 4.2 Event-Driven Architecture (EDA)

### Strong alignment

1. Transactional outbox pull model exists for NCR transitions.

```sql
-- C:/Dev/sf-quality-db/database/migrations/121_phase16_outbox_view_and_sps.sql:29
CREATE OR ALTER VIEW quality.vw_NcrNotificationOutbox
```

2. Consumer-aware polling and idempotent ack ledger exist.

```sql
-- C:/Dev/sf-quality-db/database/migrations/121_phase16_outbox_view_and_sps.sql:144-155
CREATE OR ALTER PROCEDURE integration.usp_GetPendingNotifications ...
FROM quality.vw_NcrNotificationOutbox o
WHERE o.EventKey > @AfterEventKey
```

```sql
-- C:/Dev/sf-quality-db/database/migrations/119_phase16_integration_schema_ack_table.sql:38-39
CONSTRAINT UQ_NcrNotificationAck_Event_Consumer
    UNIQUE (EventKey, ConsumerId)
```

### Violations

1. Outbox stream is NCR-only, not cross-domain.

```sql
-- C:/Dev/sf-quality-db/database/migrations/121_phase16_outbox_view_and_sps.sql:114
WHERE sh.EntityType = N'NCR'
```

2. Internal event subscription metadata and in-app notification queue are missing (documented gap).

```md
<!-- Reference_Architecture/GSD_Seeding/DB_Planning/V3_PHASE_CONTEXTS/28-CONTEXT.md:13-17 -->
- Gap: Outbox/pull-ack pattern is implemented for NCR transitions only...
- Gap: No internal user notification queue exists...
```

3. Inspection integration flow proposes synchronous direct creation call into NCR SP instead of publication/subscription decoupling.

```md
<!-- C:/Dev/sf-quality/Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/05_integration_architecture.md:96-99 -->
alt NCR trigger met
  DB->>NCR: quality.usp_CreateNcrQuick(...)
  NCR-->>DB: NewNcrId
```

Assessment: **Foundational EDA capability exists, but scope is narrow and coupling remains synchronous across modules**.

## 4.3 Hexagonal Architecture (Ports and Adapters)

### Strong alignment

1. UI boundary correctly constrained to API; no direct SQL from app repo.

```md
<!-- C:/Dev/sf-quality-app/README.md:14 -->
- No direct SQL access - all data flows through sf-quality-api
```

2. API sets SQL session caller context consistently through dedicated infrastructure.

```csharp
// C:/Dev/sf-quality-api/src/SfQualityApi/Infrastructure/DbConnectionFactory.cs:36-39
await conn.ExecuteAsync(
    "dbo.usp_SetSessionContext",
    new { CallerAzureOid = callerOid },
    commandType: CommandType.StoredProcedure);
```

### Violations

1. Endpoint layer is tightly bound to concrete SQL object names and inline SQL text.

```csharp
// C:/Dev/sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs:199-202
var result = await conn.QuerySingleOrDefaultAsync(
    "quality.usp_CreateNcrQuick",
    p,
    commandType: CommandType.StoredProcedure);
```

```csharp
// C:/Dev/sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs:341-343
var rows = await conn.QueryAsync(
    "SELECT * FROM quality.vw_OpenNCRSummary",
    commandType: CommandType.Text);
```

2. Core transition rules are persistence-bound in workflow SPs and directly reference domain tables.

```sql
-- C:/Dev/sf-quality-db/database/migrations/098_harden_workflow_transition_sp.sql:539-542
IF @EntityType = N'NCR'
    UPDATE quality.NonConformanceReport
    SET StatusCodeId = @ToStatusId ...
```

Assessment: **Hexagonal separation is present at repo boundary (UI->API->DB) but weak inside API and absent in DB-domain core separation**.

## 5. Cross-Cutting Risk Register (Prioritized)

1. **Critical**: Workflow god-module coupling (`workflow.usp_TransitionState`) can break multiple domains on any schema/state change.  
   Evidence: `C:/Dev/sf-quality-db/database/migrations/061_workflow_transition_sp.sql:59`, `C:/Dev/sf-quality-db/database/migrations/061_workflow_transition_sp.sql:338`

2. **High**: Context ownership violation (`quality` writing `workflow.StatusHistory`) weakens encapsulation and transition audit correctness.  
   Evidence: `C:/Dev/sf-quality-db/database/migrations/112_gate_create_submit.sql:129`

3. **High**: Eventing is not generalized; non-NCR domains cannot decouple secondary reactions reliably.  
   Evidence: `C:/Dev/sf-quality-db/database/migrations/121_phase16_outbox_view_and_sps.sql:114`

4. **High**: Target ABAC model not implemented at department/jurisdiction granularity.  
   Evidence: `C:/Dev/sf-quality-db/database/migrations/096_create_policy_engine_sps.sql:151`, `C:/Dev/sf-quality-db/database/migrations/007_session_context_sp.sql:67`

5. **Medium**: API endpoint SQL coupling slows testability and evolution toward stable contracts.  
   Evidence: `C:/Dev/sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs:342`

6. **Medium**: Proposed inspection cross-context FKs may over-couple lifecycles if relationship is process-optional.  
   Evidence: `C:/Dev/sf-quality/Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/db/migrations/146_create_inspection_instance.sql:75`, `C:/Dev/sf-quality/Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/db/migrations/148_create_inspection_ncr_link.sql:23`

## 6. Authoritative Remediation Plan (Low-Regret Sequence)

This plan intentionally avoids a risky big-bang rewrite and preserves operational stability.

### Phase 1 (Immediate): Boundary Hardening

Objective: Remove the highest coupling risks while preserving current synchronous gate behavior.

Actions:
1. Replace workflow CASE/table dispatch with **entity adapter procedures** owned by each bounded context.
2. Keep transition orchestration in `workflow`, but delegate entity read/write through adapter interfaces.
3. Remove direct `quality -> workflow.StatusHistory` inserts; require workflow-owned SP for status history writes.
4. Add SQL static-rule enforcement in CI to block unauthorized cross-schema DML.

Required deliverables:
- `workflow.usp_TransitionState` refactored to call adapters.
- Adapter contracts per entity type (NCR, CAPA, Complaint, SCAR, AuditFinding, EightD).
- Allowlist file for exceptional cross-schema operations.
- Failing CI test for any non-allowlisted cross-schema direct DML.

Exit criteria:
- No direct DML to foreign context tables in transition/create gate procedures.
- Transition behavior parity validated by smoke tests.

### Phase 2: Outbox Generalization and Internal Eventing

Objective: Move from NCR-only outbox to platform event backbone.

Actions:
1. Create `integration.DomainEventOutbox` with at least:
   - `EventId`, `EntityType`, `EntityId`, `EventType`, `PayloadJson`, `OccurredAtUtc`, `CorrelationId`.
2. Create generic consumer ledger (`integration.DomainEventAck`) and generic polling procedures.
3. Publish domain events from workflow transitions and approvals.
4. Add `workflow.EventSubscription` metadata and `workflow.NotificationQueue`.
5. Keep compatibility layer (`vw_NcrNotificationOutbox` and NCR polling SP aliases) until consumers migrate.

Exit criteria:
- CAPA/SCAR/Complaint/AuditFinding events are emitted and consumable through generic outbox.
- NCR consumers run unchanged through compatibility objects during migration window.

### Phase 3: ABAC Deepening (Department/Jurisdiction)

Objective: Implement target authorization model for same-plant internal separation.

Actions:
1. Extend context assignment model:
   - Add user-to-department/jurisdiction access mapping tables.
2. Extend session setup:
   - Add scoped claims in `dbo.usp_SetSessionContext` for department/jurisdiction context.
3. Extend policy engine:
   - Update `security.usp_CheckPermission` and `security.usp_EvaluatePolicy` to evaluate department/jurisdiction constraints.
4. Extend RLS:
   - Add/compose predicates beyond plant where domain data has department/jurisdiction columns.
5. Add explicit deny tests for same-plant cross-department access.

Exit criteria:
- User in Plant A/Department X cannot access Plant A/Department Y resources unless explicitly granted.
- Policy engine returns deterministic deny reasons for scope failures.

### Phase 4: API Ports/Adapters Layer

Objective: Reduce endpoint-level SQL coupling and improve testability without violating SQL-first constraints.

Actions:
1. Introduce repository ports (for example `INcrRepository`, `IWorkflowQueryRepository`).
2. Move all SQL object calls and text queries out of endpoint methods into adapter classes.
3. Eliminate inline `CommandType.Text` SQL from endpoints.
4. Add service/repository unit tests with mocks and contract tests against DB SP signatures.

Exit criteria:
- Endpoints no longer contain raw SQL strings.
- DB contract changes are caught by targeted adapter tests.

### Phase 5: Inspection-NCR Integration Coupling Policy

Objective: Prevent accidental over-coupling as inspection module is introduced.

Actions:
1. Classify each cross-context relationship as one of:
   - **Hard FK allowed**: immutable identity/invariant requiring strict referential integrity.
   - **Soft reference required**: optional process linkage where eventual reconciliation is acceptable.
2. For `Inspection.AutoNcrId`, default to soft reference + validation job unless a hard invariant is formally approved.
3. Shift inspection-triggered NCR creation toward event publication where possible.

Exit criteria:
- Written FK policy standard approved and applied to inspection migrations.
- Reconciliation job/report exists for soft links.

## 7. Top 5 Immediate Recommendations

1. **Refactor workflow transition SP to adapter-proc pattern first** (`061`, `098`, `099`) to remove god-module table coupling.  
2. **Prohibit direct cross-context writes** (starting with `112_gate_create_submit.sql:129`) and enforce via static SQL lint in CI.  
3. **Generalize outbox infrastructure** (`121`, `119`) and add subscription/notification metadata (`EventSubscription`, `NotificationQueue`).  
4. **Implement department/jurisdiction ABAC extension** on top of existing plant RLS/policy model (`006`, `007`, `096`).  
5. **Introduce API repository ports** and remove endpoint inline SQL (`NcrEndpoints.cs`) while preserving SQL-authoritative business logic.

## 8. Implementation Notes and Guardrails

- Do not switch to event-only status propagation in one step. Keep synchronous critical-path state updates until parity and monitoring are proven.
- Do not remove all cross-schema FKs by default. Apply explicit hard-FK vs soft-reference criteria per relationship.
- Do not migrate core business rules out of SQL in this program unless separately approved; this plan is compatible with SQL-authoritative domain logic.
- Maintain backward compatibility for existing NCR integration consumers during outbox generalization.

## 9. Suggested Ticket Backbone (Execution-Ready)

1. `ARCH-01` Refactor `workflow.usp_TransitionState` to adapter interfaces (NCR/CAPA/EightD first).
2. `ARCH-02` Remove direct `workflow.StatusHistory` writes from quality gate SPs.
3. `ARCH-03` Add SQL static boundary checker and exception allowlist to CI.
4. `ARCH-04` Create generic `integration.DomainEventOutbox` + ack + polling procs.
5. `ARCH-05` Add compatibility view/procs for NCR outbox consumers.
6. `ARCH-06` Add `workflow.EventSubscription` and `workflow.NotificationQueue`.
7. `ARCH-07` Extend authorization model to department/jurisdiction mappings and policy checks.
8. `ARCH-08` Add ABAC deny-path tests for same-plant cross-department access.
9. `ARCH-09` Add API repositories and remove inline SQL from NCR endpoints.
10. `ARCH-10` Publish and enforce cross-context FK policy; apply to inspection package migrations.

## 10. Final Determination

The system is on a pragmatic enterprise trajectory, but currently sits at:
- **Moderate alignment** with modular monolith goals,
- **Early-to-moderate alignment** with event-driven goals,
- **Low-to-moderate alignment** with strict hexagonal goals.

The remediation sequence above is authoritative because it addresses the highest coupling risks first, preserves operational behavior, and incrementally introduces stronger boundaries, richer ABAC scope control, and cleaner ports/adapters without requiring destabilizing rewrites.
