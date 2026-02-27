# Forms Research Extraction — Parallel (ChatGPT)

**Source:** parallel-deep-research.md + parallel-deep-research.json
**Model/Platform:** ChatGPT Parallel Deep Research
**Date produced:** 2026-02-26 (extraction date; source undated, likely early 2026 based on citation recency)
**Extracted by:** Claude Opus 4.6

---

## A. Technology Recommendations

| Technology | Category | Maturity | Azure Fit | Rec. Level | Rationale (1-2 sentences) | Limitations Noted |
|---|---|---|---|---|---|---|
| React Hook Form + Zod | Frontend form library | Production-ready | Good | **Primary** | Low learning curve, high performance via uncontrolled inputs, shared Zod schemas enable client/server validation from one source of truth. | Can trigger re-renders in extremely large forms; requires `useActionState` hook for Next.js 15 Server Actions integration. |
| TanStack Form | Headless form library | Production-ready | Good | Alternative | Signal-based architecture avoids full form re-renders; better granular reactivity for very large/dynamic forms. | Steep learning curve; headless nature means all UI bindings built from scratch; fewer community resources than RHF. |
| Azure SQL - JSON Columns | Database approach | Production-ready | Native | **Primary** | Hybrid model: relational columns for stable metadata + JSON columns for evolving form payloads avoids EAV complexity and schema migration fatigue. | Reduced type-safety vs. normalized tables; query performance depends on computed-column indexing strategy. |
| Azure SQL - Temporal Tables | Database approach | Production-ready | Native | **Primary** | System-versioned audit trails with point-in-time querying; no custom application logic for revision history. | Increases storage; requires specific T-SQL syntax (`FOR SYSTEM_TIME`) for history queries. |
| Layered Validation (Zod shared schemas) | Validation architecture | Production-ready | High | **Primary** | Single Zod schema exported from shared module used by both `zodResolver` (client UX) and `safeParse` (server authority). | Requires disciplined module separation to avoid leaking server deps into client bundle. |
| XState (State Machine Wizards) | Form architecture pattern | Production-ready | Good | Conditional | Prevents impossible states in multi-step forms; separates business logic from UI; makes complex flows testable and visualizable. | Overkill for simple linear forms; large machines hard to debug without `xstate-inspect` tooling. |
| Schema-Driven / Dynamic Forms | Form architecture pattern | Production-ready | High | Conditional | Runtime form generation from JSON metadata; enables code-free field changes without deployments. | Significant complexity (10-20 weeks); reduces compile-time type safety; requires robust schema versioning. |
| Azure AI Document Intelligence v4.0 | AI-assisted input | Production-ready | Native | Optional | OCR and intelligent extraction from invoices, receipts, custom forms; custom model training for specific layouts. | Accuracy depends on source document quality; requires async architecture (Functions + Queues) for production. |
| Azure OpenAI for Forms | AI-assisted input | Production-ready | Native | Optional | Schema-aware suggestions, smart defaults, data quality checks; structured JSON output via function calling. | Non-deterministic outputs; requires guardrails, prompt engineering, and human confirmation for high-impact actions. |
| REST API (Server Actions) | API pattern | Production-ready | Native | **Primary** | Native Next.js 15 integration; co-locates server logic with UI; built-in CSRF protection; secretless via Managed Identity. | Schema evolution requires versioning discipline; can lead to over/under-fetching. |
| GraphQL API | API pattern | Production-ready | Good | Alternative | Superior for complex data graphs and precise client-driven data fetching. | Adds operational complexity (caching, N+1, schema maintenance); overkill for single SQL backend with simple form submissions. |

**Stack-relevant picks** (fit current Next.js/React/Azure stack):
- React Hook Form + Zod (confirmed as optimal default)
- TanStack Form (viable upgrade path for very large dynamic forms)
- Next.js 15 Server Actions (primary mutation path)
- Azure SQL JSON columns + Temporal Tables (persistence + audit)
- Layered Zod validation (client + server shared schemas)
- Azure AI Document Intelligence (async OCR pipeline)
- Azure OpenAI (smart defaults, data quality checks)
- Application Insights via OpenTelemetry / `instrumentation.js` (observability)

**Stack-incompatible picks** (comparison only):
- Angular Reactive Forms + ngx-formly (requires full stack shift away from React)
- Vue FormKit + VeeValidate (requires full stack shift away from React)
- Blazor / MudBlazor + FluentValidation (requires re-skilling to C#/.NET)

---

## B. Architecture Recommendation

**Primary stack summary:**
- **Frontend:** Next.js 15 (App Router) + React Hook Form + Zod + shadcn/ui. RHF minimizes re-renders; Zod provides type-safe schemas shared across client/server. Uses Next.js `<Form>` component for progressive enhancement.
- **Validation:** Layered Zod schemas. Client-side via `zodResolver` for UX feedback; server-side via `schema.safeParse()` in Server Actions for authoritative enforcement. Placeholder for a code-first business rules engine (JsonLogic or Durable Functions) for complex dynamic logic.
- **API layer:** Next.js 15 Server Actions for standard mutations; Route Handlers (API Routes) for complex orchestration involving relational data across multiple steps. TanStack Query for client-side caching of relational data.
- **Database/persistence:** Azure SQL with hybrid model: relational columns for stable/frequently-queried fields, JSON columns for evolving form payloads. System-Versioned Temporal Tables for automatic audit trails. Row-Level Security (RLS) for data isolation. CDC (Change Data Capture) mentioned as complementary audit mechanism.
- **Auth:** Entra ID via Easy Auth. `x-ms-client-principal` header for user claims; `x-ms-token-aad-access-token` for downstream API calls. Centralized Data Access Layer (DAL) maps claims to application roles using React `cache` API for memoization. System-Assigned Managed Identity for secretless access to Azure SQL, Blob Storage, Queue Storage.
- **AI services:** Azure AI Document Intelligence for OCR in async pipeline (Blob -> Queue -> Function). Azure OpenAI for schema-aware suggestions and data quality checks. Always human-in-the-loop before committing AI-extracted data.

**Alternative stack:** GraphQL BFF (Apollo Server or GraphQL Helix) positioned between Next.js client and backend services. Offers end-to-end type safety via formal schema and precise client-driven data fetching. Trade-off: adds significant operational overhead (schema management, resolver logic, caching, N+1 mitigation) that is likely not justified for a mid-size company with a single SQL backend.

**Unique architectural claims** (positions this source takes others may not):
- Explicitly recommends **hybrid relational + JSON columns** as the data model (not pure relational, not EAV, not document store) -- with specific guidance on promoting stable fields to relational columns and keeping evolving data in JSON
- Emphasizes a **"secretless" architecture** using System-Assigned Managed Identity across all Azure services (SQL, Blob, Queue) -- eliminating connection strings entirely
- Recommends **`useActionState`** as the bridge between React Hook Form and Next.js 15 Server Actions (specific API-level integration guidance)
- Mentions **CDC (Change Data Capture)** as a complement to Temporal Tables for audit -- most sources only mention one or the other
- Proposes a **centralized Data Access Layer (DAL)** using React's `cache` API for memoized session verification
- Calls out **PII avoidance strategies** (data masking, selective logging) in observability as an explicit design concern
- Suggests **Azure SQL native JSON data type** (not just NVARCHAR(MAX) with JSON functions) -- references May 2024 native JSON support with ~18% storage savings and faster writes

---

## C. Patterns Identified

| Pattern Name | Description | When to Use | When to Avoid | Real-World Example |
|---|---|---|---|---|
| Layered Validation Orchestration | Single Zod schema as authoritative contract, shared between client (`zodResolver`) and server (`safeParse` in Server Actions). Eliminates validation duplication; enables progressive enhancement. | All standard data entry forms requiring consistency and data integrity. | When validation depends on external legacy systems (SOAP) that cannot be modeled in Zod; extremely stringent client bundle size constraints. | No named company cited; described as widely adopted pattern. Mentions `drizzle-zod` for auto-generating validators from DB schema. |
| State Machine-Driven Wizards (XState) | Formal state machines define valid states and transitions for multi-step forms. Prevents impossible states (e.g., skipping required steps, double submission). Separates business logic (machine) from UI (component). | Complex wizards with conditional branching, interdependencies between steps, manufacturing config wizards, complex order forms. | Simple linear forms where `useState` or URL query params suffice. | Cites `xstate-wizards` library for "incredibly complex questionnaires." References blog post on XState + Next.js App Router with component-level state machines. |
| Schema-Driven / Metadata-Driven Dynamic Forms | Forms generated at runtime from JSON metadata stored in database. Generic "Form Renderer" component iterates metadata to render shadcn/ui components bound to RHF. Enables non-developer form structure changes without code deployment. | High-variability inputs: inspection checklists differing by machine type, product configurators that change frequently, user-defined fields. | Static forms (login, profile) where compile-time type safety is preferred. | No named company cited directly; mentions Siemens and GE as examples of companies using similar patterns in industrial software. Cites `zod-to-json-schema` and `@sinclair/typebox` for bridging TypeScript types and stored JSON metadata. |

---

## D. Complexity & Risk Assessment

| Tier | Recommended Pattern | Integration Points | Key Risks | Agent-Readiness |
|---|---|---|---|---|
| **Simple** (single-step, flat data) | Server Actions + RHF + Zod. Direct mutation via Server Actions; client validation for UX only. Server Components for initial data population. | App Service hosts Next.js. Azure SQL basic CRUD via Managed Identity. Entra ID via Easy Auth for claims. App Insights for request tracing. Bicep/Terraform for IaC. | Over-engineering; duplicating validation logic when it should be shared. | **High** -- well-documented pattern, deterministic structure. A coding agent can scaffold a complete form (schema, component, server action, SQL proc) from a clear spec. 1-2 weeks. |
| **Moderate** (multi-step, conditional, relational) | Hybrid: Route Handlers for complex orchestration + Server Actions for simple step mutations. TanStack Query for client-side caching. | Azure SQL with transactions for multi-step commits. Entra ID claims mapped to app roles. Temporal Tables for auditing critical data. App Insights custom events for funnel tracking. | Data consistency across steps; complex conditional logic; query performance. | **Medium** -- requires upfront decisions on step-flow architecture, state management approach (URL-based vs. XState vs. context), and transaction boundaries. Once decided, agents can execute each step. 3-6 weeks. |
| **Complex** (dynamic schema, audit-trailed) | Schema-Driven/Metadata-Driven + Temporal Tables + JSON columns. Route Handlers for schema management and versioning. Azure Functions for async processing. | Azure SQL JSON columns + Temporal Tables extensively. Entra ID RBAC for schema management access. Managed Identity throughout. Functions + Blob + Queue for AI-assisted input. App Insights for schema change monitoring. | Schema evolution breaking old data; query performance on large history datasets; overall system complexity. | **Low** -- requires significant human judgment on metadata schema design, form renderer architecture, and versioning strategy. The form renderer itself is agent-buildable once the metadata contract is locked, but locking that contract is a human-heavy design phase. 10-20 weeks. |

---

## E. Sources & Evidence Quality

**Total sources cited:** 10 in key sources list; 11 in references; ~40+ unique URLs in JSON `outputBasis` citations
**Sources with URLs that resolve:** Spot-checked 5 -- all resolve:
- react-hook-form.com (OK)
- learn.microsoft.com/en-us/azure/azure-sql/database/temporal-tables-overview (OK)
- tanstack.com/form/latest (OK)
- red-gate.com/simple-talk/.../effective-strategies-for-storing-and-parsing-json-in-sql-server (OK)
- nextjs.org/docs/app/guides/open-telemetry (OK)

**Recency range:** 2021-01-28 (sqlshack audit overview) to 2026-02-18 (SigNoz OpenTelemetry Next.js guide)
**Notable gaps:**
- **No coverage of Dapper or thin-API constraints** -- the source assumes Next.js Server Actions talk directly to Azure SQL, ignoring the existing constraint (#2) that the API layer uses Dapper. No mention of Dapper anywhere.
- **No coverage of existing typed-per-entity schema design** -- does not acknowledge or evaluate the current approach of typed relational tables per entity. Goes straight to recommending hybrid JSON columns without comparing against the existing pattern.
- **No real-world named case studies** -- pattern deep dives cite no specific companies using these patterns in production (Siemens/GE are generic hand-waves in the JSON file).
- **No coverage of offline/disconnected scenarios** -- relevant for manufacturing floor data collection.
- **Weak on business rules engines** -- mentions JsonLogic and Durable Functions as "placeholders" but provides no depth on implementation.
- **No coverage of form accessibility (a11y)** -- despite recommending shadcn/ui + Radix (which are a11y-focused), no specific accessibility testing or requirements discussed.
- **No evaluation of Formik or Final Form** -- only RHF baseline comparison, missing the two other major React form libraries.

---

## F. Extractor Notes

**Overall quality assessment:** Adequate -- The source provides a well-organized, comprehensive survey of the forms technology landscape with good Azure integration depth, but it lacks critical engagement with the existing constraints and makes several assumptions that do not match the actual system architecture.

**Unique insights not likely in other reports:**
- **Native JSON data type in Azure SQL** (not just NVARCHAR+JSON functions): cites May 2024 GA with 18% storage savings and faster writes via partial document updates. This is a concrete, actionable data point.
- **CDC + Temporal Tables as complementary audit mechanisms**: most sources recommend one or the other; this source positions CDC for change tracking and Temporal for point-in-time querying as a combined approach.
- **`useActionState` as the specific RHF <-> Server Actions bridge**: provides API-level integration guidance rather than just conceptual recommendations.
- **PII avoidance in observability**: explicit call-out of data masking and selective logging for compliance -- a practical concern often overlooked.
- **Computed column indexing strategy for JSON**: detailed T-SQL patterns for `JSON_VALUE` computed columns with standard indexes, including execution plan comparisons.
- **`@vercel/otel` + `@azure/monitor-opentelemetry-exporter` for App Insights**: specific package-level integration guidance for OpenTelemetry in Next.js on Azure.

**Red flags or questionable claims:**
- **Server Actions as the primary API layer contradicts constraint #2** (API layer stays thin, uses Dapper). The source assumes Next.js talks directly to Azure SQL from Server Actions, bypassing any separate API layer entirely. This is a fundamental architectural mismatch that would need reconciliation.
- **"4-8 person-weeks" for Layered Validation setup** seems inflated for a pattern that is essentially "export Zod schema, import in both places." This estimate appears to include full team onboarding and standardization across all forms, not just the pattern itself.
- **"10-20 person-weeks" for Schema-Driven Forms** is a wide range that reveals uncertainty. The source does not break this down into buildable phases.
- **Hybrid JSON columns recommendation directly tensions with constraint #5** (quality domain data model is well-defined, no EAV/configurable schema). The source recommends JSON columns for "evolving form payloads" without acknowledging that the existing data model is typed and stable. This needs careful evaluation -- the recommendation may still have merit for genuinely variable data (e.g., inspection checklists) but should not be applied to core quality event entities.
- **No acknowledgment of the thin-API / Dapper architecture** means the entire "Server Actions -> Azure SQL" flow needs reinterpretation. In the actual system, Server Actions would call the Dapper-based API, not talk to SQL directly.
- **"Secretless architecture" via Managed Identity is aspirational but accurate** -- it is the correct target state, but the source does not address migration complexity from connection-string-based auth.
- **GraphQL alternative recommendation feels like template padding** -- the source itself acknowledges it is overkill for a single SQL backend, yet dedicates significant space to it.
- **JSON data type was in public preview (Dec 2024 per cited source)** -- the claim of GA status needs verification against current Azure SQL compatibility level requirements.

**Agent-implementation considerations:**
- **Simple tier is highly agent-ready**: a coding agent can scaffold form + schema + server action + SQL proc from a well-defined spec. The Layered Validation pattern is essentially a file-organization convention that agents handle well.
- **The hybrid JSON column approach would complicate agent work** if adopted: agents need clear contracts for what goes in relational columns vs. JSON. A typed-per-entity schema (the existing approach) is actually MORE agent-friendly because the contract is explicit in the table DDL and Zod schema.
- **XState wizards are medium agent-readiness**: the state machine definition is highly agent-suitable (it is essentially a JSON config), but designing which states/transitions are needed requires human domain expertise.
- **The Schema-Driven/Dynamic Forms pattern is the LEAST agent-friendly** option in the report: it requires building a generic renderer, which involves significant design judgment about component mapping, validation binding, and edge cases. Once built, populating it with specific form definitions would be agent-ready.
- **The `outputBasis` section in the JSON file is valuable for traceability** -- it provides citation-level evidence for each claim, which is unusual for AI research outputs and increases confidence in the factual claims (while the reasoning/synthesis remains AI-generated).
- **The source's estimates assume a 3-6 person team** -- for a 1-human + agents team, the "person-weeks" metric needs reinterpretation. Simple tier: ~1 week with agents. Moderate: ~2-3 weeks (1 week design, 1-2 weeks agent execution). Complex: ~6-10 weeks (3-4 weeks design, 3-6 weeks agent execution with ongoing human review).
