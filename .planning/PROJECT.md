# sf-quality

## What This Is

sf-quality is a multi-repo Quality Management System for manufacturing (Select Finishing). It manages NCRs, CAPAs, 8Ds, SCARs, inspection workflows, and quality event triage across three independent repos with a contract-chain governance model: database publishes a manifest → API publishes OpenAPI → app pins a snapshot.

The three repos: `sf-quality-db` (Azure SQL / T-SQL / stored procedures, production v3.0) → `sf-quality-api` (currently ASP.NET Core 9.0 / C# / Dapper, ~50% complete, migrating to Spring Boot / Java) → `sf-quality-app` (Next.js 15 / React 19 / TypeScript, phases 1-3 in progress, phases 4-10 not started).

## Core Value

Manufacturing operators and quality engineers can initiate, route, track, and close quality events — with full audit trails — without leaving the system.

## Current Milestone: v1.0 — Spring Pivot + Forms Foundation

**Goal:** Resolve forms architecture decisions, migrate the API from C# to Spring Boot/Java, complete the app foundation, and implement the Quality Forms Module end-to-end (DB → API → App).

**Target features:**
- Adjudication of 11 forms architecture decisions (DECISION_BRIEF.md)
- Spring Boot / Java replacement of sf-quality-api (full rewrite, all 10 phases in Java)
- App phases 1-3 completion (foundation, design system, Easy Auth session)
- Quality Forms Module: DB schema + Spring Boot endpoints + App UX (phases 4-6)

## Requirements

### Validated

<!-- Shipped and confirmed valuable from pre-GSD work. -->

- ✓ sf-quality-db v3.0 complete — 99 stored procedures, 38 views, 153 migrations, 8 schemas (dbo, quality, rca, apqp, workflow, security, audit, integration)
- ✓ Contract chain governance: DB manifest → API OpenAPI → App snapshot, CI-enforced
- ✓ Azure Easy Auth via App Service — authentication infrastructure in place across all repos
- ✓ Session context via `dbo.usp_SetSessionContext` — role-based SQL session context, RLS enforced
- ✓ sf-quality-api phases 1-3.5, 5, 7 complete in C# — Foundation, Contract Sync, NCR endpoints (24 routes), Infrastructure Hardening, Workflow/Action Items
- ✓ sf-quality-app auth boundary built — server-only Easy Auth parsing, token forwarding, AppShell scaffold
- ✓ Forms Research Consolidation stages 00-02 complete — 4-source synthesis, DIVERGENCE_LOG.md, DECISION_BRIEF.md produced
- ✓ Role terminology and triage artifacts remediated across all repos

### Active

- [ ] Adjudication of 11 architectural decisions → FINAL_DECISIONS.md + deliverables
- [ ] Spring Boot / Java API replacing C# ASP.NET Core — all infrastructure + all 10 API phases in Java
- [ ] App phases 1-3 complete (TanStack Query, shadcn/ui design system, Easy Auth session UX)
- [ ] Quality Forms Module: DB schema and stored procedures (sf-quality-db Phase 35+)
- [ ] Quality Forms Module: Spring Boot API endpoints (29 endpoints)
- [ ] Quality Forms Module: App UX — field registry, React Hook Form + Zod, conditional logic, inspection forms (App phases 4-6)

### Out of Scope

- Multi-tenancy — single-tenant system by design
- Message brokers / Service Bus / Kafka — App Service + Azure Functions (scoped for AI/OCR only, future milestone)
- Spring Data JPA / Hibernate — thin data access layer (MyBatis only, equivalent to Dapper)
- Full schema-driven form engine — field registry pattern only for this milestone; Gemini's "form engine drift" warning respected
- Azure OpenAI / LLM integration — deferred to future milestone; Document Intelligence is future too
- App phases 7-10 (Workflow Approvals, Knowledge, Dashboards, E2E Governance) — deferred to v1.1
- EAV patterns — scoped JSON exception for variable inspection checklist data only

## Context

**Architecture:** Three independent repos, each with its own CI/CD and governance. Planning lives in workspace root (`sf-quality`). Execution happens in child repo contexts — the user switches repos to execute each phase.

**Cross-repo execution model:**
- Planning artifacts: `sf-quality/.planning/`
- Adjudication / deliverables: `sf-quality` context (Reference_Architecture/)
- DB Quality Forms: switch to `sf-quality-db` context
- API migration: switch to `sf-quality-api` context
- App forms + foundation: switch to `sf-quality-app` context

**Spring Boot migration context:** The C# API is a thin pass-through. Every endpoint: receive HTTP → parse Easy Auth header → open SQL connection → call `usp_SetSessionContext` → call stored proc via Dapper → return JSON. Spring Boot with MyBatis replicates this exactly. Colleague (Java/Spring Boot) advises on patterns; agentic coding implements. OpenAPI contract shape MUST be preserved.

**Critical infrastructure to replicate in Spring Boot:**
- `X-MS-CLIENT-PRINCIPAL` base64 parsing for Easy Auth identity
- `dbo.usp_SetSessionContext(@CallerAzureOid)` on every user-scoped connection
- `security.usp_CheckPermission` gate for workflow submit routes
- SQL error code → HTTP status mapping (50400→400, 50401→401, 50404→404, 52xxx→domain-specific)
- `PagedResponse<T>{items, nextCursor}` cursor-based pagination envelope
- Correlation ID propagation (X-Correlation-Id)
- Audit API call logging (route/method/status/duration/oid)
- Rate limiting (120 req/60s fixed window per identity)
- Transient SQL retry (3 retries, exponential backoff + jitter via Polly equivalent)

**Forms architecture foundation:** Adjudication decisions feed directly into the Quality Forms implementation. Forms work cannot begin until adjudication is complete. DB forms schema cannot begin until adjudication decisions on JSON vs typed columns (Decision 5) and data model approach (Decision 11) are resolved.

**DB freeze state:** sf-quality-db is in blocker-only freeze for Phase 35. Quality Forms DB work IS the blocker that needs to land — it directly unblocks API and App quality forms phases.

## Constraints

- **Cross-repo**: Each repo has its own governance — never commit to child repos from workspace root context
- **Contract chain**: Spring Boot API must produce identical OpenAPI spec shape — app requires no changes when API language changes
- **Data access**: MyBatis (thin SQL mapper) only — no Spring Data JPA / Hibernate
- **Stored procedures**: All data logic stays in T-SQL stored procedures; Spring Boot / Java just calls them
- **Deployment**: Azure App Service — no containerization, no Kubernetes in scope
- **Single-tenant**: No multi-tenant design patterns needed
- **Producer-first sequencing**: DB must publish contracts before API phases execute; API must publish OpenAPI before App phases execute

## Key Decisions

| Decision | Rationale | Outcome |
|---|---|---|
| API language: C# → Java / Spring Boot | Aligns with colleague's skills; agentic coding handles translation | — Pending |
| Data access: Dapper → MyBatis | Closest Java analog to Dapper — thin, SQL-first, no ORM | — Pending |
| Forms business logic boundary | Form UX logic in TypeScript; data integrity in T-SQL | — Pending adjudication |
| Forms UI: React Hook Form + Zod + shadcn/ui | Unanimous 4/4 research consensus | — Pending implementation |
| Business rules: json-rules-engine | 2/4 sources, strongest case for regulated quality system | — Pending adjudication |
| JSON columns: scoped exception for inspection checklists | All 4 sources recommend hybrid; Decision 5 adjudication needed | — Pending adjudication |

---
*Last updated: 2026-02-26 — Milestone v1.0 started (Spring Pivot + Forms Foundation)*
