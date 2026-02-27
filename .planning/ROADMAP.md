# Roadmap: sf-quality

## Overview

Milestone v1.0 delivers the Spring Pivot + Forms Foundation across four repos. Work begins with forms architecture adjudication (which gates all Quality Forms work), then fans out into three parallel tracks: Spring Boot API migration, App foundation completion, and Quality Forms database schema. These converge into Quality Forms API endpoints and finally Quality Forms App UX. Eight phases, four repos, strict producer-first sequencing.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: [sf-quality] Forms Architecture Adjudication** - Rule on 11 architectural decisions and produce deliverables that gate all Quality Forms work
- [ ] **Phase 2: [sf-quality-api] Spring Boot Infrastructure** - Stand up Spring Boot 3.x / Java 21 project with all cross-cutting concerns replicating the C# foundation
- [ ] **Phase 3: [sf-quality-api] Spring Boot NCR Endpoints** - Port all 24 NCR routes and permission gate pattern to Java
- [ ] **Phase 4: [sf-quality-api] Spring Boot Remaining Domain Endpoints** - Port CAPA, Complaint, RCA, Knowledge, Dashboard, Integration endpoints and deploy config
- [ ] **Phase 5: [sf-quality-app] App Foundation Completion** - Complete phases 1-3 of sf-quality-app (data layer, design system, auth session)
- [ ] **Phase 6: [sf-quality-db] Quality Forms Database** - Create inspection schema, stored procedures, and publish updated DB contract manifest
- [ ] **Phase 7: [sf-quality-api] Quality Forms API Endpoints** - Implement Quality Forms template, assignment, execution, and rules endpoints in Spring Boot
- [ ] **Phase 8: [sf-quality-app] Quality Forms App UX** - Build field registry, conditional logic, inspection forms, wizard pattern, NCR lifecycle, and domain workspaces

## Parallelism

```
Phase 1 (ADJ) ─────────────────────────┬──> Phase 6 (DB) ──> Phase 7 (QF-API) ──> Phase 8 (QF-APP)
                                        │                          ^                      ^
Phase 2 (Spring Infra) ──> Phase 3 ──> Phase 4 ───────────────────┘                      |
                           (NCR)        (Remaining)                                       |
                                                                                          |
Phase 5 (App Foundation) ────────────────────────────────────────────────────────────────>┘
```

- Phases 2 and 5 can start immediately (no dependency on Phase 1)
- Phase 6 starts after Phase 1 completes
- Phases 2, 5, and 6 can run in parallel
- Phase 3 depends on Phase 2
- Phase 4 depends on Phase 3
- Phase 7 depends on Phases 4 AND 6 (needs both Spring Boot domain endpoints and DB contracts)
- Phase 8 depends on Phases 1, 5, AND 7 (needs adjudication rulings, app foundation, and QF-API contracts)

## Phase Details

### Phase 1: [sf-quality] Forms Architecture Adjudication
**Goal**: All 11 forms architecture decisions are ruled, recorded, and translated into actionable deliverables that downstream phases consume
**Depends on**: Nothing (first phase)
**Repo**: sf-quality (workspace root -- Reference_Architecture/)
**Requirements**: ADJ-01, ADJ-02, ADJ-03, ADJ-04, ADJ-05
**Success Criteria** (what must be TRUE):
  1. FINAL_DECISIONS.md exists in `03_adjudication/` with all 11 decisions ruled -- each has ID, decision text, ruling, evidence summary, and downstream impact
  2. Forms architecture spec exists in `04_deliverables/` and aligns to the rulings (especially Decision 5 JSON vs typed columns, Decision 6 rules engine approach, Decision 11 data model)
  3. Coding conventions doc exists in `04_deliverables/` with forms-specific patterns that an agent can consume when building in sf-quality-app
  4. CONTEXT.md templates exist in `04_deliverables/` for app phases 4-6, seeded with adjudication outcomes
  5. Forms Research Consolidation README shows Stages 03 and 04 marked complete
**Plans**: TBD

Plans:
- [ ] 01-01: TBD
- [ ] 01-02: TBD

### Phase 2: [sf-quality-api] Spring Boot Infrastructure
**Goal**: A fully operational Spring Boot 3.x / Java 21 project exists in sf-quality-api with all cross-cutting infrastructure -- Easy Auth, session context, error mapping, MyBatis, OpenAPI, pagination, correlation IDs, audit logging, rate limiting, retry, CORS, health check, contract validation, and CI
**Depends on**: Nothing (can start in parallel with Phase 1)
**Repo**: sf-quality-api
**Requirements**: SPRING-01, SPRING-02, SPRING-03, SPRING-04, SPRING-05, SPRING-06, SPRING-07, SPRING-08, SPRING-09, SPRING-10, SPRING-11, SPRING-12, SPRING-13, SPRING-14, SPRING-15
**Success Criteria** (what must be TRUE):
  1. `mvn package` (or Gradle equivalent) succeeds and produces a deployable artifact with Spring Boot 3.x on Java 21
  2. A request with `X-MS-CLIENT-PRINCIPAL` header results in `dbo.usp_SetSessionContext` being called with the extracted Azure OID before any user query executes
  3. `GET /v1/diagnostics/health` returns 200 with anonymous access, and the published OpenAPI spec (springdoc) preserves the same route paths and response schemas as the C# `api-openapi.publish.json`
  4. SQL error codes 50400/50401/50404 map to HTTP 400/401/404 respectively, and transient SQL errors trigger retry with exponential backoff
  5. GitHub Actions CI validates build, contract references against `db-contract-manifest.snapshot.json`, and OpenAPI publication on PRs
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD
- [ ] 02-03: TBD

### Phase 3: [sf-quality-api] Spring Boot NCR Endpoints
**Goal**: All 24 NCR routes are live in Java with identical request/response shapes to the C# implementation, and the permission gate pattern protects workflow submit routes
**Depends on**: Phase 2
**Repo**: sf-quality-api
**Requirements**: SPRING-16, SPRING-17
**Success Criteria** (what must be TRUE):
  1. All 24 NCR routes respond with the same JSON shapes as the C# implementation -- POST/PUT/DELETE NCR, GET summary/queue, all 16 lifecycle gates, 3 supporting data routes, 4 analytics routes
  2. Workflow submit routes call `security.usp_CheckPermission(@UserId, @PermissionCode, @PlantId)` and reject unauthorized requests with appropriate HTTP status
  3. Cursor-based pagination on list endpoints returns `PagedResponse{items, nextCursor}` matching the existing contract
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD

### Phase 4: [sf-quality-api] Spring Boot Remaining Domain Endpoints
**Goal**: All remaining API phases (CAPA, Complaint, RCA, Knowledge, Dashboard, Integration) are ported to Java and the app can be deployed to Azure App Service as a Spring Boot application
**Depends on**: Phase 3
**Repo**: sf-quality-api
**Requirements**: SPRING-18, SPRING-19, SPRING-20, SPRING-21, SPRING-22, SPRING-23
**Success Criteria** (what must be TRUE):
  1. CAPA and Complaint CRUD endpoints respond correctly, calling the corresponding `quality.usp_Create/Update/Delete` stored procedures
  2. All 16 `rca.*` stored procedure routes are accessible and return expected shapes for Fishbone, 5-Why, Is/Is Not, PFMEA, and 8D reports
  3. Knowledge, traceability, dashboard, and operational view endpoints serve data from the correct views (`dbo.vw_DefectKnowledge_*`, `quality.vw_*`)
  4. Integration endpoints support service-principal auth path for `integration.usp_GetPendingNotifications` and `integration.usp_AcknowledgeNcrOutboxEvent`
  5. Spring Boot deploys to Azure App Service with correct `application-prod.properties` (Azure SQL connection string, Easy Auth config, startup command)
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD
- [ ] 04-03: TBD

### Phase 5: [sf-quality-app] App Foundation Completion
**Goal**: sf-quality-app phases 1-3 are complete -- data fetching layer, design system, and authenticated session propagation all work end-to-end in a deployed environment
**Depends on**: Nothing (can start in parallel with Phases 1-4)
**Repo**: sf-quality-app
**Requirements**: APP-01, APP-02, APP-03
**Success Criteria** (what must be TRUE):
  1. TanStack Query provider is configured with API client types generated from the OpenAPI snapshot, and API calls work against dev/staging/prod base URLs
  2. shadcn/ui component library is installed with Radix primitives, lucide-react icons, app shell layout (header/nav/main), dark/light mode toggle, and framer-motion baseline
  3. Easy Auth session propagation works end-to-end in a deployed environment -- delegated bearer token forwarding to sf-quality-api confirmed, plant scope selector (Pattern #38) and feature entitlement tree (Pattern #37) functional
**Plans**: TBD

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD
- [ ] 05-03: TBD

### Phase 6: [sf-quality-db] Quality Forms Database
**Goal**: The Quality Forms Module database schema exists in sf-quality-db with inspection template/assignment/execution tables, response storage (aligned to adjudication Decision 5), business rules storage (aligned to Decision 6), stored procedures, and an updated contract manifest
**Depends on**: Phase 1 (adjudication rulings on JSON vs typed columns, data model approach, rules engine)
**Repo**: sf-quality-db
**Requirements**: DB-01, DB-02, DB-03, DB-04, DB-05, DB-06
**Success Criteria** (what must be TRUE):
  1. Inspection template tables (`InspectionTemplate`, `InspectionTemplateSection`, `InspectionTemplateItem`) exist with typed relational columns for stable fields, aligned to Decision 11 ruling
  2. Inspection assignment and execution tables exist with temporal table support for audit trails, aligned to Decision 8 ruling
  3. Inspection response storage exists (6 typed response tables OR hybrid JSON column) aligned to Decision 5 ruling, and business rules storage exists if Decision 6 selected Option B
  4. All 29 Quality Forms stored procedures are created and callable (template management, assignment, submission, finding linkage)
  5. `db-contract-manifest.snapshot.json` is updated and published with all new Quality Forms procedures and views
**Plans**: TBD

Plans:
- [ ] 06-01: TBD
- [ ] 06-02: TBD

### Phase 7: [sf-quality-api] Quality Forms API Endpoints
**Goal**: Spring Boot exposes all Quality Forms endpoints (template management, assignment, execution, business rules) and the updated OpenAPI contract is published for sf-quality-app consumption
**Depends on**: Phase 4 (Spring Boot fully operational) AND Phase 6 (DB contracts published)
**Repo**: sf-quality-api
**Requirements**: QF-API-01, QF-API-02, QF-API-03, QF-API-04, QF-API-05
**Success Criteria** (what must be TRUE):
  1. Template management endpoints (CRUD for inspection templates, sections, items) call the corresponding Quality Forms stored procedures and return expected shapes
  2. Assignment endpoints manage the lifecycle of assigning templates to jobs/equipment/products
  3. Execution endpoints support starting an inspection, submitting typed responses, and attaching findings to NCRs
  4. Business rules endpoints read/write json-rules-engine rule definitions (if Decision 6B was selected in adjudication)
  5. Updated OpenAPI spec is published and sf-quality-app snapshot is updated with the Quality Forms endpoint surface
**Plans**: TBD

Plans:
- [ ] 07-01: TBD
- [ ] 07-02: TBD

### Phase 8: [sf-quality-app] Quality Forms App UX
**Goal**: Quality Forms UX is complete -- operators can fill out inspection forms with all field types, conditional logic, multi-step wizards, and the NCR lifecycle and domain workspace UIs are functional
**Depends on**: Phase 1 (adjudication rulings for forms patterns), Phase 5 (app foundation), AND Phase 7 (QF-API contracts published)
**Repo**: sf-quality-app
**Requirements**: QF-APP-01, QF-APP-02, QF-APP-03, QF-APP-04, QF-APP-05, QF-APP-06
**Success Criteria** (what must be TRUE):
  1. Field registry is built with all 6 inspection field types (numeric, attribute, text, datetime, selection, attachment) as shadcn/ui components, with React Hook Form + Zod validation and form preflight via API
  2. Conditional field logic evaluates client-side for instant UX feedback -- using json-rules-engine (Decision 6B) or structured TypeScript rules module (Decision 6C)
  3. An operator can select an inspection template, work through sections, enter responses by field type, and submit an inspection -- including multi-step wizard navigation with draft persistence and server-side step validation
  4. NCR lifecycle UX is complete -- create/edit/submit/disposition/close/void/reopen NCR, queue and summary views, containment/investigation/verification workflow screens
  5. CAPA and Complaint domain workspace UIs exist and consume the corresponding Spring Boot endpoints
**Plans**: TBD

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD
- [ ] 08-03: TBD

## Progress

**Execution Order:**
Phases 1, 2, and 5 can start in parallel. Phase 6 starts after Phase 1. Phase 3 after Phase 2. Phase 4 after Phase 3. Phase 7 after Phases 4 and 6. Phase 8 after Phases 1, 5, and 7.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. [sf-quality] Forms Architecture Adjudication | 0/TBD | Not started | - |
| 2. [sf-quality-api] Spring Boot Infrastructure | 0/TBD | Not started | - |
| 3. [sf-quality-api] Spring Boot NCR Endpoints | 0/TBD | Not started | - |
| 4. [sf-quality-api] Spring Boot Remaining Domain Endpoints | 0/TBD | Not started | - |
| 5. [sf-quality-app] App Foundation Completion | 0/TBD | Not started | - |
| 6. [sf-quality-db] Quality Forms Database | 0/TBD | Not started | - |
| 7. [sf-quality-api] Quality Forms API Endpoints | 0/TBD | Not started | - |
| 8. [sf-quality-app] Quality Forms App UX | 0/TBD | Not started | - |
