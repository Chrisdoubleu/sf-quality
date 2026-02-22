# Phase 29 — Audit Infrastructure and Temporal Query

**Milestone:** v3.0 Architectural Hardening and Platform Maturation
**Track:** Independent — **Execute this phase FIRST**
**Requirements:** ARCH-14, ARCH-15, ARCH-16
**Source patterns:** Pattern_Mapping.md #5, #4, #22

---

## Reference Architecture Patterns

### Pattern #5 — Universal Change Audit with Anomaly Detection
- **Gap:** `audit.ApiCallLog` table does not exist; API call durability is absent
- **Scope (single-tenant):** Add `audit.ApiCallLog` linked to entity audit trail by correlation ID. Full anomaly-detection ML pipeline is out of scope.

### Pattern #4 — Temporal Data Model and Point-in-Time Querying
- **Gap:** Temporal modeling is pervasive in the schema, but point-in-time query semantics are not consistently exposed through API-facing procedures
- **Scope:** Add optional `@AsOfUtc DATETIME2 = NULL` to key read procedures, routed through `FOR SYSTEM_TIME AS OF`

### Pattern #22 — Tree Helpers and Hierarchy Navigation
- **Gap:** No shared recursive hierarchy helpers; defect/plant/org hierarchies are traversed ad-hoc per consumer
- **Scope:** Create `dbo.usp_GetTreeAncestors` and `dbo.usp_GetTreeDescendants` as reusable helpers; add cycle-detection checks

---

## Existing Artifacts

This phase builds on:
- `audit.AuditLog` (migration 003) — entity mutation audit log
- `dbo.usp_CreateAuditTrigger` (migration 004) — audit trigger generator
- Temporal tables on NCR, workflow, and document entities (migrations 024, 028, 046, 048)
- `workflow.StatusHistory` with recency indexing (migration 048)
- Plant hierarchy in `dbo.Plant` (parent-child structure exists)
- `quality.vw_NcrGateAudit` (migration 120) — NCR audit view consumer

---

## Recommended Approach (Distilled)

### Plan 29-01: `audit.ApiCallLog` Table

Create the API call log table in the `audit` schema:

```sql
-- New table: audit.ApiCallLog
CREATE TABLE audit.ApiCallLog (
    ApiCallLogId       INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    CorrelationId      NVARCHAR(50)      NOT NULL,   -- matches X-Correlation-ID header
    Route              NVARCHAR(500)     NOT NULL,   -- e.g. /v1/ncr
    HttpMethod         NVARCHAR(10)      NOT NULL,   -- GET, POST, PUT, DELETE
    CallerOid          NVARCHAR(100)     NULL,       -- Azure AD OID from Easy Auth
    HttpStatus         INT               NOT NULL,
    DurationMs         INT               NOT NULL,
    RequestTimestampUtc DATETIME2(7)     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Index for correlation ID lookups (cross-reference with audit.AuditLog)
CREATE INDEX IX_ApiCallLog_CorrelationId ON audit.ApiCallLog (CorrelationId);
-- Index for time-range queries on audit trail
CREATE INDEX IX_ApiCallLog_Timestamp ON audit.ApiCallLog (RequestTimestampUtc DESC);
```

Grant `INSERT`, `SELECT` to API application identity.

### Plan 29-02: `@AsOfUtc` on Key Read Procs + Tree Helpers

**@AsOfUtc parameter additions** — add to these procs (at minimum):
- `quality.usp_GetNcrDetail` — `@AsOfUtc DATETIME2 = NULL`
- `quality.usp_GetWorkflowState` — `@AsOfUtc DATETIME2 = NULL`
- Pattern: `SELECT ... FROM table FOR SYSTEM_TIME AS OF @AsOfUtc WHERE ...` when `@AsOfUtc IS NOT NULL`, else standard query

**Tree helpers:**
```sql
-- dbo.usp_GetTreeAncestors(@NodeId INT, @HierarchyTable NVARCHAR(128))
-- Returns all ancestor rows up the parent chain
-- Uses recursive CTE with cycle-detection (MAX_RECURSION guard)

-- dbo.usp_GetTreeDescendants(@NodeId INT, @HierarchyTable NVARCHAR(128))
-- Returns all descendant rows down the child chain
-- Uses recursive CTE with MAX_RECURSION guard
```

Alternatively: implement as table-valued functions `dbo.tvf_GetTreeAncestors` / `dbo.tvf_GetTreeDescendants` if TVF syntax is preferred for JOIN usage.

Add cycle-detection CHECK to `dbo.Plant` and any other parent-child tables (verify `ParentPlantId != PlantId`).

---

## Cross-Repo Dependencies

| Dependency | Direction | Details |
|-----------|-----------|---------|
| `audit.ApiCallLog` table | DB → API | **Hard gate for API Phase 3.5** — `ApiCallLogMiddleware` writes to this table via Dapper. Phase 3.5 cannot execute until this migration is deployed and reflected in `db-contract-manifest.json`. |
| `@AsOfUtc` on read procs | DB → API | **Gate for API Phase 4** — pagination and two-phase retrieval infrastructure needs temporal query support |
| Tree helpers | DB → API | Informational for API Phase 9 (dashboards/hierarchy traversal) — not a hard gate |

**After this phase:**
1. Refresh `db-contract-manifest.json` for Phase 29 additions
2. Notify API team that `audit.ApiCallLog` is available — Phase 3.5 can proceed

---

## Entry Criteria

- Phase 22 DEFERRED status confirmed in `22-DEFERRAL.md`
- v3.0 milestone initialized (this phase directory created by `/gsd:new-milestone`)
- No API phase has started that depends on `audit.ApiCallLog` (i.e., API Phase 3.5 is NOT YET started)

## Exit Criteria (Acceptance Gate for API Phase 3.5)

1. `audit.ApiCallLog` table exists with all 8 specified columns and both indexes
2. At least one read proc accepts `@AsOfUtc DATETIME2 = NULL` and returns temporal results when provided
3. `dbo.usp_GetTreeAncestors` and `dbo.usp_GetTreeDescendants` (or TVF equivalents) callable on `dbo.Plant` hierarchy
4. Cycle-detection constraint exists on `dbo.Plant`
5. `db-contract-manifest.json` refreshed to include Phase 29 additions
6. `Invoke-CycleChecks.ps1` passes with no drift
