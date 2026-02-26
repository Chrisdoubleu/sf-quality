# Requirements: sf-quality

**Defined:** 2026-02-26
**Core Value:** Manufacturing operators and quality engineers can initiate, route, track, and close quality events — with full audit trails — without leaving the system.
**Milestone:** v1.0 — Spring Pivot + Forms Foundation

---

## v1.0 Requirements

### Adjudication (sf-quality workspace — Reference_Architecture/)

- [ ] **ADJ-01**: All 11 architectural decisions from DECISION_BRIEF.md are ruled and recorded in `03_adjudication/FINAL_DECISIONS.md` with ID, decision, ruling, evidence, and impact
- [ ] **ADJ-02**: Forms architecture spec produced in `04_deliverables/` — authoritative specification aligned to adjudication rulings
- [ ] **ADJ-03**: Coding conventions doc produced in `04_deliverables/` — forms-specific patterns for agents building in sf-quality-app
- [ ] **ADJ-04**: GSD seeding content produced in `04_deliverables/` — CONTEXT.md templates for app phases 4-6 consuming the forms architecture
- [ ] **ADJ-05**: Forms Research Consolidation README updated — Stages 03 and 04 marked complete

### Spring Boot Migration — Infrastructure (sf-quality-api)

- [ ] **SPRING-01**: New Spring Boot 3.x / Java 21 project structure replaces ASP.NET Core project in sf-quality-api — same repo, same deployment target (Azure App Service)
- [ ] **SPRING-02**: Easy Auth identity extraction implemented — `X-MS-CLIENT-PRINCIPAL` base64 header parsed to extract Azure OID and display name (equivalent to `EasyAuthHandler.cs`)
- [ ] **SPRING-03**: SQL session context set on every user-scoped connection — `dbo.usp_SetSessionContext(@CallerAzureOid)` called via MyBatis before any user query (equivalent to `DbConnectionFactory.CreateForUserAsync`)
- [ ] **SPRING-04**: SQL error code → HTTP status mapping preserved exactly — 50400→400, 50401→401, 50404→404, 50410-50419→domain codes, 52xxx→NCR gate codes (equivalent to `SqlErrorMapper`)
- [ ] **SPRING-05**: MyBatis configured as the sole data access layer — mapper interfaces for all stored procedure calls; no Spring Data JPA, no Hibernate, no JDBC template for mutations
- [ ] **SPRING-06**: OpenAPI 3.x spec published via springdoc-openapi — same route paths, request/response schemas, and pagination envelope as current C# `api-openapi.publish.json` (version-bumped to `0.4.0`)
- [ ] **SPRING-07**: Cursor-based pagination envelope preserved — `PagedResponse<T>{items, nextCursor}` JSON shape unchanged so sf-quality-app requires no contract changes
- [ ] **SPRING-08**: Correlation ID middleware implemented — `X-Correlation-Id` extracted or generated, propagated through request lifecycle and structured logs
- [ ] **SPRING-09**: Audit API call logging implemented — structured log per request with route, method, HTTP status, duration ms, and caller OID
- [ ] **SPRING-10**: Rate limiting implemented — 120 requests per 60-second window per authenticated identity (or IP for anonymous)
- [ ] **SPRING-11**: Transient SQL retry implemented — 3 retries with exponential backoff and jitter for transient SQL connection errors (equivalent to Polly `"sql-transient"` pipeline)
- [ ] **SPRING-12**: CORS configured — explicit origin allowlist from environment config, never wildcard
- [ ] **SPRING-13**: Health check endpoint live — `GET /v1/diagnostics/health` returns 200, anonymous access
- [ ] **SPRING-14**: DB contract snapshot validation — Spring Boot project references only stored procedures and views listed in `.planning/contracts/db-contract-manifest.snapshot.json`
- [ ] **SPRING-15**: CI pipeline adapted — GitHub Actions workflow validates `mvn build` (or Gradle equivalent), contract references, and OpenAPI publication on PRs

### Spring Boot Migration — NCR Endpoints (sf-quality-api, completing Phase 3 equivalent)

- [ ] **SPRING-16**: All 24 NCR routes ported to Java with identical request/response shapes — POST `/ncr`, POST `/ncr/full`, PUT `/ncr/{id}`, DELETE `/ncr/{id}`, GET `/ncr/summary`, GET `/ncr/queue`, all 16 lifecycle gate routes, all 3 supporting data routes, all 4 analytics routes
- [ ] **SPRING-17**: PermissionGate pattern replicated in Java — `security.usp_CheckPermission(@UserId, @PermissionCode, @PlantId)` called before workflow submit routes

### Spring Boot Migration — Remaining API Phases (sf-quality-api, Phases 4, 6, 8, 9, 10 in Java)

- [ ] **SPRING-18**: CAPA and Complaint CRUD endpoints implemented in Java — maps to `quality.usp_CreateCAPA`, `quality.usp_UpdateCAPA`, `quality.usp_DeleteCAPA`, `quality.usp_CreateComplaint`, `quality.usp_UpdateComplaint`, `quality.usp_DeleteComplaint` and associated views (Phase 4 equivalent)
- [ ] **SPRING-19**: RCA tools endpoints implemented in Java — Fishbone, 5-Why, Is/Is Not, PFMEA, 8D report routes mapping to all 16 `rca.*` stored procedures (Phase 6 equivalent)
- [ ] **SPRING-20**: Knowledge and traceability endpoints implemented in Java — defect knowledge retrieval, traceability chain, all 9 `dbo.vw_DefectKnowledge_*` views and `dbo.usp_GetTraceabilityChain` (Phase 8 equivalent)
- [ ] **SPRING-21**: Dashboard and operational view endpoints implemented in Java — NCR pareto, hold aging, CAPA aging, cost of quality, escalation alerts, PPM views, all `quality.vw_*` analytics views (Phase 9 equivalent)
- [ ] **SPRING-22**: Integration endpoints implemented in Java — `integration.usp_GetPendingNotifications`, `integration.usp_AcknowledgeNcrOutboxEvent`, service-principal auth path (Phase 10 equivalent)
- [ ] **SPRING-23**: Azure App Service deployment config for Spring Boot — `application.properties` / `application-prod.properties` with Azure SQL connection string, Easy Auth config, App Service startup command

### App Foundation Completion (sf-quality-app, Phases 1-3)

- [ ] **APP-01**: Phase 1 complete — TanStack Query provider configured, API client types generated from OpenAPI snapshot, environment config (dev/staging/prod API base URLs), Prettier + ESLint enforced
- [ ] **APP-02**: Phase 2 complete — shadcn/ui component library installed and configured, Radix primitives, lucide-react icons, app shell layout finalized (header/nav/main), next-themes dark/light mode toggle, nuqs URL state, framer-motion baseline
- [ ] **APP-03**: Phase 3 complete — Easy Auth session propagation validated end-to-end in deployed environment, delegated bearer token forwarding to sf-quality-api confirmed working, plant scope selector with RLS scope (Pattern #38), feature entitlement tree (Pattern #37)

### Quality Forms Module — Database (sf-quality-db, Phase 35)

- [ ] **DB-01**: Inspection template schema created — tables for `InspectionTemplate`, `InspectionTemplateSection`, `InspectionTemplateItem` with typed relational columns for stable fields (aligned to adjudication Decision 11 ruling)
- [ ] **DB-02**: Inspection assignment and execution tables created — `InspectionAssignment`, `InspectionExecution` with temporal table support for audit (Decision 8 ruling)
- [ ] **DB-03**: Inspection response tables created — 6 typed response tables (`InspectionResponseNumeric`, `InspectionResponseAttribute`, `InspectionResponseText`, `InspectionResponseDatetime`, `InspectionResponseSelection`, `InspectionResponseAttachment`) OR hybrid JSON column (aligned to Decision 5 ruling)
- [ ] **DB-04**: Business rules storage created — table for json-rules-engine rule definitions if Decision 6 selects Option B (externalized rules)
- [ ] **DB-05**: Quality Forms stored procedures created — 29 procedures for template management, assignment, submission, and finding linkage (per Quality Forms Module design)
- [ ] **DB-06**: DB contract manifest updated and published — sf-quality-api snapshot updated to include new Quality Forms procs and any new views

### Quality Forms Module — API Endpoints (sf-quality-api, Phase QF)

- [ ] **QF-API-01**: Quality Forms template management endpoints — create/read/update/delete inspection templates, sections, and items via stored procedures
- [ ] **QF-API-02**: Inspection assignment endpoints — assign templates to jobs/equipment/products, manage assignment lifecycle
- [ ] **QF-API-03**: Inspection execution endpoints — start inspection, submit responses by type, attach findings to NCRs
- [ ] **QF-API-04**: Business rules endpoints — read/write json-rules-engine rule definitions (if Decision 6B selected)
- [ ] **QF-API-05**: OpenAPI contract updated and published — app snapshot updated with Quality Forms endpoint surface

### Quality Forms Module — App UX (sf-quality-app, Phases 4-6)

- [ ] **QF-APP-01**: Phase 4 complete — React Hook Form + Zod installed, field registry built with all inspection field types (numeric, attribute, text, datetime, selection, attachment) as shadcn/ui components, form preflight validation via API (Pattern #44), lookup/dropdown consumption from API
- [ ] **QF-APP-02**: Field-level conditional logic implemented — json-rules-engine integrated (if Decision 6B selected) or structured TypeScript rules module (if Decision 6C), evaluated client-side for instant UX feedback
- [ ] **QF-APP-03**: Inspection form execution UX — operator selects template, works through sections, enters responses by field type, submits inspection
- [ ] **QF-APP-04**: Multi-step wizard pattern implemented for multi-section inspections — step navigation, draft persistence (save progress, resume later), server-side step validation before advance
- [ ] **QF-APP-05**: NCR lifecycle UX complete (Phase 5) — create/edit/submit/disposition/close/void/reopen NCR UI, NCR queue and summary views, containment/investigation/verification workflow screens
- [ ] **QF-APP-06**: Domain workspaces started (Phase 6) — CAPA and Complaint workspace UIs consuming the corresponding Spring Boot endpoints

---

## v2 Requirements (deferred)

### App Completion

- **APP-V2-01**: Phase 7 — Workflow, Action Items, and Approvals UX
- **APP-V2-02**: Phase 8 — Knowledge and Traceability UX
- **APP-V2-03**: Phase 9 — Dashboards and Operational Analytics views (Recharts integration)
- **APP-V2-04**: Phase 10 — Playwright E2E tests, Vitest coverage, governance promotion to blocking, App Service deployment

### AI/OCR Pipeline

- **AI-V2-01**: Azure Document Intelligence integration for scanned inspection forms
- **AI-V2-02**: Azure Functions for async document processing pipeline (blob trigger → Document Intelligence → results to DB)
- **AI-V2-03**: Confidence-tiered AI workflow (auto-fill high-confidence / flag medium / require attestation for critical fields)

### Advanced Forms

- **FORMS-V2-01**: Schema-driven form engine for variable inspection checklists (only if field registry proves insufficient at scale)
- **FORMS-V2-02**: Admin UI for managing json-rules-engine rule definitions

---

## Out of Scope

| Feature | Reason |
|---|---|
| Spring Data JPA / Hibernate | Violates thin-API constraint — MyBatis only (equivalent to Dapper) |
| Multi-tenancy | Single-tenant system by design |
| Azure Service Bus / Kafka / RabbitMQ | App Service constraints; Functions + Queue Storage only for async |
| Azure OpenAI / LLM integration | Deferred to v2 — adjudication may scope in |
| Full schema-driven form engine | Risk of "form engine drift" (Gemini warning); field registry sufficient for v1 |
| App phases 7-10 | Deferred to v1.1 — foundation + forms core takes priority |
| EF Core / LINQ-to-SQL | Spring Boot equivalent excluded for same reason as C# EF |
| Power Apps, Blazor, other frontend frameworks | Next.js 15 is locked; no alternatives |

---

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Repo | Status |
|---|---|---|---|
| ADJ-01 through ADJ-05 | Phase 1 | sf-quality | Pending |
| SPRING-01 through SPRING-15 | Phase 2 | sf-quality-api | Pending |
| SPRING-16 through SPRING-17 | Phase 3 | sf-quality-api | Pending |
| SPRING-18 through SPRING-23 | Phases 4-7 | sf-quality-api | Pending |
| APP-01 | Phase 8 | sf-quality-app | Pending |
| APP-02 through APP-03 | Phase 9 | sf-quality-app | Pending |
| DB-01 through DB-06 | Phase 10 | sf-quality-db | Pending |
| QF-API-01 through QF-API-05 | Phase 11 | sf-quality-api | Pending |
| QF-APP-01 through QF-APP-06 | Phases 12-13 | sf-quality-app | Pending |

**Coverage:**
- v1.0 requirements: 56 total
- Mapped to phases: 56
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-26*
*Last updated: 2026-02-26 after milestone v1.0 initialization*
