# Architecture Constraints

These are non-negotiable. They are load-bearing decisions with 24+ phases of implementation behind them. Any plan for Phase 23 must comply with all of them.

---

## The 8 Non-Negotiable Constraints

### 1. Business logic lives in T-SQL stored procedures

The API is a thin HTTP-to-SQL translation layer. It does not contain business rules. All validation, authorization, workflow enforcement, and data transformation happens in stored procedures. This is why Phase 23's documentation deliverables must explain the system in SP/view terms, not API/app terms.

### 2. Dapper only — no Entity Framework

No query builders. No ORM. Stored procedures called via `CommandType.StoredProcedure`. This means the API's contract with the DB is entirely through the procedure/view surface listed in `db-contract-manifest.json`.

### 3. Single-tenant system

One company, one Azure SQL database. No multi-tenant isolation patterns. The RLS model is for plant-level isolation within one organization, not multi-tenant data separation.

### 4. Azure App Service deployment

No service bus, no message broker, no container orchestration, no serverless functions. The deploy chain is: Azure SQL Database + Azure App Service. PowerShell deploy scripts target these directly.

### 5. Idempotent migrations — immutable once deployed

Every schema change is a numbered migration file (`001_schemas.sql` through `130_defect_taxonomy_v3_cleanup.sql`) with existence guards (IF NOT EXISTS, CREATE OR ALTER). Once a migration is deployed, it is NEVER modified. Bugs are fixed via forward-fix migrations (e.g., `086a_fix_audit_trigger_rowversion.sql`). This means Phase 23 cannot retroactively fix any migration file from 001-130.

### 6. Contract-governed repos — changes propagate forward only

```
DB manifest → API snapshot/publish → App snapshot
```

The DB publishes a manifest of its procedure and view surface. The API snapshots that manifest and publishes an OpenAPI spec. The App snapshots the OpenAPI spec. No backward propagation. Phase 23's manifest refresh must be reflected in the API snapshot before the API plans new endpoints against v2.0 objects.

### 7. Row-level security via SESSION_CONTEXT

Every user-scoped query runs through `dbo.usp_SetSessionContext(@CallerAzureOid)` which establishes SESSION_CONTEXT(N'UserId'), SESSION_CONTEXT(N'PlantId'), SESSION_CONTEXT(N'IsAdmin'). All plant-scoped tables have FILTER + BLOCK predicates via `security.PlantIsolationPolicy`. Knowledge tables (migration 125) intentionally have NO RLS enrollment — they are reference data, not plant-scoped transactional data.

### 8. No EAV (Entity-Attribute-Value) patterns

The data model is strongly typed. The 9 knowledge extension tables are each typed columns for specific knowledge domains — they are not a generic `FieldName/FieldValue` structure. Metadata-driven form definitions are acceptable in the App layer; EAV for database storage is not.

---

## The 7-Schema Model

All database objects are organized in schemas. No new schemas should be created in Phase 23 (governance phase, not a schema expansion phase):

| Schema | Purpose |
|--------|---------|
| `dbo` | Reference and dimension tables, core utility SPs, knowledge extension tables |
| `quality` | Quality event entities (NCR, CAPA, SCAR, Complaint, AuditFinding), gate SPs, operational views |
| `rca` | Root cause analysis entities (8D, Fishbone, 5 Whys, PFMEA, Is/Is-Not) |
| `workflow` | Workflow engine (states, transitions, guards, approvals, SLA, escalation, action items) |
| `security` | Permission catalog, RLS predicates, policy engine SPs |
| `audit` | History tables, AuditLog, temporal versioning |
| `apqp` | (Reserved for future APQP/Control Plan work) |
| `integration` | Notification outbox acknowledgement (added in v1.1 Phase 16) |
| `analytics` | Reserved for Phase 22 analytics views (DEFERRED) |

---

## Security Model

The Phase 16 security model (migration 123) established 5 DB roles with scoped grants:

| Role | Purpose |
|------|---------|
| `dbrole_ncr_ops_exec` | Execute NCR operational SPs |
| `dbrole_ncr_ops_read` | SELECT on operational views |
| `dbrole_ncr_admin` | Admin-level access |
| `dbrole_ncr_audit_read` | Read-only audit trail access |
| `dbrole_ncr_integration` | Integration consumer (outbox, notifications) |

Phase 23's SEC-01 deliverable must verify whether knowledge SPs and views added in Phases 21-21.1 have appropriate grants against these roles. The key question: which role should have EXECUTE on `quality.usp_GetDefectKnowledge` and SELECT on the 9 `dbo.vw_DefectKnowledge_*` views?

---

## Workflow Authorization Pattern

The 18 gate SPs follow this pattern:
1. Call `dbo.usp_SetSessionContext(@CallerAzureOid)` first
2. Validate authority via `security.usp_CheckPermission` or `security.usp_EvaluatePolicy`
3. Call `workflow.usp_TransitionState` by @ToStatusCode (never by @TransitionId)
4. Use deterministic error codes: 50400 (validation), 50401 (auth), 50410-50419 (policy), 52xxx (gate-specific)

Knowledge SPs (`quality.usp_GetDefectKnowledge`, `quality.usp_PrePopulateRootCauses`) are advisory — they do not transition state and do not require workflow authorization. They do call `dbo.usp_SetSessionContext` when `@NcrId` is used (RLS needed to resolve the NCR's line type).

---

## Migration Naming Convention

```
001_schemas.sql                              (3-digit sequential)
086a_fix_audit_trigger_rowversion.sql        (3-digit + alpha suffix for forward-fixes)
126a_defect_knowledge_seed_ecoat.sql         (3-digit + alpha suffix for same-number variants)
126b_defect_knowledge_seed_powder.sql
126c_defect_knowledge_seed_liquid.sql
126d_confusion_pair_bidirectional_fix.sql
127_containment_guidance_ecoat_powder.sql    (127 Section A — containment)
130_defect_taxonomy_v3_cleanup.sql
```

Current range: 001 through 130 (plus forward-fix 086a and multi-suffix 126a/b/c/d). Total file count: 133.

Phase 23 plans may create new migration files if grant closure requires SQL (e.g., a `131_knowledge_layer_grants.sql`). The next migration would be `131`.
