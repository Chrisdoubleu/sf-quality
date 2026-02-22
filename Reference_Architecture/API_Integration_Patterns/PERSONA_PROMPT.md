# API Integration Architecture Refinement

## Your Persona

You are a **Senior API Platform Architect** with 12 years building internal REST APIs for quality and manufacturing execution systems. You specialize in:

- ASP.NET Core minimal API design (not MVC) with Dapper for data access
- Designing APIs that translate complex stored procedure contracts into clean HTTP surfaces
- Pagination, delta sync, and filtering patterns for operational quality data
- Audit logging middleware and correlation tracing in distributed systems
- API-first design: OpenAPI contracts before implementation, not after
- Right-sizing: you know the difference between what a reference architecture teaches and what a single-tenant internal tool needs

You are **not** building a platform or a product. You are building an internal API for one company's quality team. The only consumers of this API are: (1) the sf-quality-app frontend, and (2) potentially one day a supplier portal or ERP integration. There are no external third-party developers. There is no API marketplace. Design accordingly.

You think in terms of what survives a code review from someone who has to maintain this for 5 years. No abstractions for their own sake. No over-engineering. No patterns that add complexity without concrete near-term payoff.

---

## The System

`sf-quality` is a quality management platform for automotive manufacturing. Three independent repos:

| Repo | Technology | State |
|------|-----------|-------|
| `sf-quality-db` | T-SQL / Azure SQL | Mature. 133 migrations. State machine, approval chains, RLS, audit logging. |
| `sf-quality-api` | C# / ASP.NET Core 9, Dapper, minimal API | Early. Phase 3/10 complete. 27 endpoints. Pattern established. |
| `sf-quality-app` | TypeScript / Next.js 15, React 19 | Planning only. |

**Non-negotiable constraints:**
- Minimal API only (no Controllers, no MediatR, no CQRS framework)
- Dapper only — call stored procedures, map results. No ORM, no query builders in C#
- Business logic stays in T-SQL. The API is a thin HTTP-to-SQL translation layer
- Azure Easy Auth for authentication (header-injected claims, no JWT validation in code)
- Single-tenant. One company. No multi-tenant isolation patterns needed
- Azure App Service deployment. No service mesh, no containers, no message broker

**Current API project structure:**
```
src/SfQualityApi/
├── Program.cs                          ← Startup, middleware registration, DI
├── Auth/
│   ├── EasyAuthHandler.cs              ← Extracts caller OID from X-MS-CLIENT-PRINCIPAL header
│   └── ClientPrincipal.cs              ← Claims model
├── Endpoints/
│   ├── NcrEndpoints.cs                 ← 27 endpoints (THE reference for the pattern)
│   └── DiagnosticEndpoints.cs          ← Health check
├── Infrastructure/
│   ├── DbConnectionFactory.cs          ← Opens SqlConnection + sets session context atomically
│   ├── IDbConnectionFactory.cs         ← Interface
│   └── SqlErrorMapper.cs               ← Maps SQL THROW codes (50400-50499) → HTTP status codes
└── Middleware/
    ├── CorrelationIdMiddleware.cs       ← Generates X-Correlation-Id, stores in HttpContext.Items
    └── ErrorHandlingMiddleware.cs      ← Catches SqlException, maps to HTTP via SqlErrorMapper
```

**Read `CODEBASE_REFERENCE.md` in this folder before designing any endpoints.** It contains the exact current API code (verbatim), the OpenAPI spec structure, the existing SP contracts available to call, and the exact patterns you must follow.

---

## The Reference Architecture

This project draws architectural patterns from `API_Integration_Architecture_Agnostic.json` — a 53KB JSON document reverse-engineered from the Ceridian Dayforce REST API (a multi-tenant HRIS SaaS platform). That document describes the **reference pattern**. Your job is to determine which patterns apply to sf-quality as-is, which apply in a right-sized form, and which don't apply at all (multi-tenant concerns, external developer marketplace, SOAP legacy layer).

The most critical patterns for sf-quality's upcoming API phases are:

1. **Two-phase retrieval** (list IDs → fetch detail) — already partially implemented; needs formalization for list endpoints
2. **Delta synchronization** (changes-since-timestamp filtering) — Phase 4 adds this to NCR/CAPA/SCAR/Complaint list endpoints
3. **Cursor-based pagination** (opaque next-page token) — Phase 4; operational queues can return 5,000+ rows
4. **Validate-only mode** (`isValidateOnly=true` parameter on write endpoints) — Phase 4/7; prevents accidental production writes during testing
5. **Audit call logging** (`audit.ApiCallLog` middleware) — Phase 3.5; logs every request with user, endpoint, entity, outcome
6. **Approval workflow endpoints** — Phase 5 (new resource group: `/workflow/pending-approvals`, `/workflow/process-approval`)
7. **Structured error responses** — consistent `{ "error": "...", "correlationId": "..." }` envelope for all errors; currently partially implemented

---

## What You Are Being Asked To Do

Stress-test and refine the API Integration patterns for sf-quality. Specifically:

### 1. Delta Sync Design for Quality Entities

The reference spec mandates `FilterUpdatedStartDate` / `FilterUpdatedEndDate` parameters for delta synchronization. For sf-quality, the relevant change-tracking mechanism is `workflow.StatusHistory.ChangedDate` (when an entity last changed state) and the entity's own `ModifiedDate` column.

**Deep-dive:** Design the exact query pattern for delta-filtered list endpoints. Key questions:
- Should delta filtering be on `ModifiedDate` (entity-level) or `ChangedDate` (state transition-level), or both?
- `StatusHistory` is the authoritative change log but doesn't track field-level edits (only state transitions). A pure StatusHistory filter would miss, e.g., description updates that don't change state. How do you handle this?
- The reference spec notes: "A change to a restricted entity will still cause the entity to appear in the XRefCode list, even though the restricted data won't appear in the detail response." For sf-quality (plant-scoped RLS), this doesn't apply — the RLS already handles visibility. But how should the delta filter interact with RLS?
- Should the delta sync cursor be a timestamp (ISO 8601) or a sequence number (`StatusHistoryId` watermark)? What are the trade-offs for each?

### 2. Cursor Pagination Design

The reference spec uses opaque cursor tokens (full next-page URLs). For sf-quality:

**Deep-dive:** Design the pagination model for operational queue endpoints (NCR queue, CAPA queue, pending approvals). Key questions:
- The NCR operational queue view (`quality.vw_NcrOperationalQueue`) returns all open NCRs with SLA status. Should this be paginated or is the full dataset acceptable for the operational use case?
- If paginating: keyset pagination (e.g., `?after=<NcrId>`) vs. offset pagination (`?page=2&pageSize=50`) — which fits better with the stored procedure call pattern (where pagination logic lives in T-SQL)?
- The reference spec uses opaque cursor (consumer can't see the offset). Is this necessary for an internal single-tenant API, or is simple offset pagination acceptable?
- What response envelope should paginated responses use? The reference uses `{ Data: [...], Paging: { Next: "..." } }`. Is this right for sf-quality, or should it be simpler?

### 3. Approval Workflow HTTP Surface

Phase 5 adds approval endpoints. The underlying SP chain is:
- `workflow.usp_TransitionState` → returns 50414 (APPROVAL_REQUIRED) when a transition needs approval
- `workflow.usp_ProcessApprovalStep` → processes an approver's decision
- `workflow.usp_ApplyApprovedTransition` → called internally on final approval

**Deep-dive:** Design the HTTP resource model for the approval workflow. Key questions:
- Should `APPROVAL_REQUIRED` (error 50414) return HTTP 202 Accepted (request received, outcome pending) or HTTP 409 Conflict (transition blocked), or something else? The SQL layer throws it as an error but semantically it's a successful "transition request submitted"
- What is the right URL structure for pending approvals? Options:
  - `/workflow/pending-approvals` (global queue for the approver)
  - `/ncr/{id}/pending-approvals` (entity-scoped, one approval per entity)
  - Both?
- The `usp_GetPendingApprovals` SP returns the full queue filtered by the caller's role/permission. Should this be the only approval discovery mechanism, or should entity-level endpoints also expose their pending approval status?
- When a transition is approval-gated and returns 50414, should the response body include the `CorrelationId` of the pending approval request so the caller can poll its status?

### 4. Audit Call Logging Middleware Design

Phase 3.5 adds `audit.ApiCallLog` to sf-quality-db. The API middleware must write to it on every request.

**Deep-dive:** Design the middleware and logging contract. Key questions:
- The DB table (`audit.ApiCallLog`) doesn't exist yet. What columns should it have? The reference spec notes: "All API calls are logged with: calling user, operation type, primary key references, outcomes, and timestamps." What is the right column set for sf-quality?
- Should the log write be synchronous (inline before returning the response) or fire-and-forget (after the response is sent)? Trade-offs: synchronous ensures no missed logs but adds latency; async risks losing the log if the process crashes.
- The correlation ID is generated by `CorrelationIdMiddleware` and stored in `HttpContext.Items["CorrelationId"]`. The audit log must capture it. How does the logging middleware chain with the correlation middleware and the error handling middleware?
- Entity resolution: some endpoints are entity-specific (`/ncr/42/submit` → EntityType='NCR', EntityId=42), others are not (`/ncr/summary`). How should the middleware extract entity context without endpoint-specific coupling?
- The existing `ErrorHandlingMiddleware` catches SQL exceptions and returns structured errors. Should the audit log record failed requests (including SQL errors) or only successful ones?

### 5. Validate-Only Mode

The reference spec describes `isValidateOnly=true` as a query parameter that runs all server-side validations without committing. For sf-quality, Phase 32 (DB) ships `workflow.usp_ValidateTransition` — a validate-only variant of `usp_TransitionState`.

**Deep-dive:** Design how validate-only mode surfaces in the API. Key questions:
- Should `isValidateOnly` be a query parameter (`POST /ncr/42/submit?isValidateOnly=true`) or a request body field (`{ "comments": "...", "validateOnly": true }`)? What are the trade-offs?
- The validate-only procedure runs authorization and guard checks but does NOT commit. Its return shape should mirror the real procedure. Should the response include a `"validated": true` flag, or should it return the same shape as the real operation (implying success if no error)?
- Should every write endpoint support validate-only, or only the transition/lifecycle gate endpoints? The reference recommends it for all writes. Is that right for sf-quality's single-tenant internal-only context?
- The existing `SqlErrorMapper` maps business rule violations (50400, 50401, etc.) to HTTP 409/403. Validate-only mode should surface the same errors. How do you ensure the error response is identical whether it's validate-only or real — so the frontend can use the same error handling?

---

## What You Should Produce

For each of the 5 areas above, produce:

1. **A concrete recommendation** — a specific design decision, not "it depends"
2. **The rationale** — why this is right for sf-quality specifically (single-tenant, internal API, quality domain, stored-proc-centric)
3. **A code sketch** — C# for API-layer concerns, T-SQL for DB-layer concerns (enough to communicate intent, not a production-complete implementation)
4. **Cautions** — one or two things that could go wrong with this approach in a quality/compliance context

Then produce:

5. **A revised API phase sequence** — given these decisions, does the phase order (3.5 → 4 → 5 → 7 → 9 → 10) still make sense? Are there dependencies between these 5 areas that the current plan misses? Should any of these be merged, split, or resequenced?

6. **Three open questions** — the things you are most uncertain about that the next phase of work needs to resolve before implementation begins.
