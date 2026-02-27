# Forms Research Extraction — Gemini 2.5 Pro Deep Research

**Source:** gemini-deep-research.md, gemini-deep-research.json
**Model/Platform:** Gemini 2.5 Pro (Deep Research mode)
**Date produced:** 2026-02-26
**Extracted by:** Claude Opus 4.6

---

## A. Technology Recommendations

| Technology | Category | Maturity | Azure Fit | Rec. Level | Rationale (1-2 sentences) | Limitations Noted |
|---|---|---|---|---|---|---|
| React Hook Form v7.71 | Frontend library | Production-ready | Native | Primary pick | Uncontrolled component architecture prevents re-render cascades in 100+ field manufacturing forms. Seamless shadcn/ui integration. | Struggles with deeply nested, highly dynamic schema generation without extensive custom wrapper logic. |
| TanStack Form v1.28 | Frontend library | Emerging | Native | Acknowledged alternative | Framework-agnostic with first-class deep TypeScript inference and granular reactivity. | Smaller ecosystem, higher boilerplate, steeper learning curve than RHF. |
| Angular Reactive Forms v19 | Frontend framework | Production-ready | Good | Comparison only | Gold standard for prescriptive, monolithic enterprise SPAs with observable-based data flow. | Tightly coupled to Angular; severe architectural friction for a Next.js team. |
| FormKit v1.7 | Frontend library | Production-ready | Limited | Comparison only | Vue 3 schema-based rendering with out-of-the-box accessibility and integrated validation. | Vue-exclusive; entirely incompatible with React/Next.js stack. |
| Blazor FluentValidation (.NET 11) | Validation tool | Production-ready | Native | Comparison only | Full C# stack for Microsoft-centric teams with existing .NET business logic. | Requires WASM overhead or SignalR; paradigm mismatch for TypeScript environments. |
| Azure SQL Temporal Tables | Database approach | Production-ready | Native | Primary pick | Zero-code immutable audit trail with point-in-time data reconstruction via FOR SYSTEM_TIME AS OF. | History tables can grow exponentially; requires retention policies and specialized indexing. |
| Azure SQL JSON Columns | Database approach | Production-ready | Native | Primary pick | Stores evolving form definitions and loosely structured submission payloads alongside relational data. | Deeply nested JSON querying degrades without proper JSON indexing strategies. |
| Zod v3.24 | Validation tool | Production-ready | Native | Primary pick | Single schema definition shared between client (courtesy) and server (authoritative) validation. End-to-end type safety. | Complex async validation (cross-referencing DB records) complicates synchronous form state updates. |
| json-rules-engine v7.3 | Business logic engine | Production-ready | Native | Primary pick | Decouples conditional visibility and validation logic from UI code; rules stored as JSON. | Requires custom React hooks to bridge async rule evaluation with synchronous rendering cycles. |
| Azure AI Document Intelligence v4.0 | AI service | Production-ready | Native | Primary pick | Deterministic, layout-aware OCR for structured data extraction from scanned manufacturing forms. Superior to LLMs for tabular data. | Custom neural models require upfront training data and manual labeling; no zero-shot adaptability. |
| Azure App Service Easy Auth | Auth gateway | Production-ready | Native | Primary pick | Zero-code OAuth 2.0 delegation to Entra ID; injects X-MS-CLIENT-PRINCIPAL headers into requests. | Lacks granular resource-level authorization; app code must still parse headers for RBAC. |

**Stack-relevant picks** (fit current Next.js/React/Azure stack):
- React Hook Form v7.71 — confirmed as baseline, recommended over TanStack Form for maturity/ecosystem
- Zod v3.24 — isomorphic validation, shared schemas between client and Server Actions
- json-rules-engine v7.3 — decoupled business rules for conditional form logic
- Azure SQL Temporal Tables — automated audit trail, zero application code
- Azure SQL JSON Columns — hybrid relational+document storage for evolving form schemas
- Azure AI Document Intelligence v4.0 — OCR/extraction for legacy paper form ingestion
- Azure App Service Easy Auth — out-of-process Entra ID authentication gateway

**Stack-incompatible picks** (comparison only):
- Angular Reactive Forms v19 — requires full framework switch, team retraining
- FormKit v1.7 — Vue-exclusive
- Blazor FluentValidation — requires .NET/WASM paradigm shift away from TypeScript
- TanStack Form v1.28 — technically compatible but deemed premature vs. RHF for this context

---

## B. Architecture Recommendation

**Primary stack summary:**
- Frontend: React Hook Form v7 + shadcn/ui + Tailwind CSS 4 — uncontrolled components maintain 60fps on factory-floor tablets; native shadcn integration for accessible, customized UI
- Validation: Zod (isomorphic) — single schema definition shared between React client components and Next.js Server Actions via safeParse(); eliminates duplicate validation logic
- API layer: Next.js 15 Server Actions (useActionState) — eliminates REST boilerplate; secure server-side RPC with progressive enhancement if JS fails; concurrent React 19 features
- Database/persistence: Azure SQL (JSON columns + System-Versioned Temporal Tables) — JSON columns for evolving form payloads, temporal tables for zero-code immutable audit trail with point-in-time reconstruction
- Auth: Microsoft Entra ID via Easy Auth — out-of-process gateway handles OAuth 2.0 token rotation, session management; app consumes X-MS-CLIENT-PRINCIPAL headers; Managed Identity for downstream Azure resources
- AI services: Azure AI Document Intelligence v4.0 — deterministic OCR extraction from scanned manufacturing forms; outputs structured JSON that hydrates RHF state for user review

**Alternative stack:** GraphQL API (Apollo Server) + Entity-Attribute-Value database schema + TanStack Form. Gains unparalleled query flexibility and strict relational typing per form field; GraphQL enables selective data fetching for future mobile/vendor clients. Loses significant developer velocity and runtime performance — EAV requires expensive JOINs to reconstruct submissions, GraphQL introduces complexity (depth limits, auth middleware), and it abandons the simplicity of the Next.js unified full-stack model.

**Unique architectural claims** (positions this source takes others may not):
- Explicitly recommends Server Actions as the API layer rather than traditional REST routes — frames this as eliminating an entire architectural tier
- Recommends json-rules-engine as a dedicated business rules engine decoupled from UI code, stored as JSON — not just inline conditional logic
- Strongly positions Azure SQL JSON columns as a hybrid approach (relational + document) rather than choosing one paradigm — "schema-less flexibility for form payloads while maintaining strict relational auditability"
- Frames the metadata-driven form engine as a tiered decision: only justified at the Complex tier, explicitly warns against over-engineering simpler forms with it
- Recommends TypeScript ORM (Drizzle or Prisma) rather than Dapper for the persistence layer — this directly conflicts with constraint #2 (thin API layer, Dapper)
- Calls Document Intelligence "far superior to probabilistic LLMs" for structured form extraction — takes a strong position on deterministic vs. probabilistic AI
- Describes the complete X-MS-CLIENT-PRINCIPAL header decoding flow in detail, including Base64 JSON extraction for RBAC
- Includes an observability layer (Application Insights with correlation IDs) spanning client, Server Actions, and database queries

---

## C. Patterns Identified

| Pattern Name | Description | When to Use | When to Avoid | Real-World Example |
|---|---|---|---|---|
| Metadata-Driven UI Generation (Schema-Driven Dynamic Forms) | Entire form structure, layout, validation, and conditional logic defined by external JSON payload. Frontend is a deterministic rendering engine using factory pattern to map field types to React components. State managed as flat key-value map. | Dozens/hundreds of distinct forms that change frequently; business admins need to create new workflows without engineering sprints; rapidly evolving regulatory requirements. | Bespoke consumer-facing interfaces requiring pixel-perfect animations; simple forms where abstraction creates unnecessary technical debt and debugging complexity. | Hike Medical — encodes clinical workflow UI and conditional logic into FormSchema stored in PostgreSQL JSONB, enabling real-time form updates across web/mobile without deployments. |
| Shared Schema Boundary Validation (Isomorphic Client-Server Validation) | Single Zod schema .ts file defines form shape/constraints. Client uses @hookform/resolvers/zod for courtesy validation; Server Action imports same schema and runs safeParse() for authoritative validation. Single source of truth eliminates duplicate logic. | All modern Next.js applications with user input; enterprise systems where client-side JS can be bypassed (cURL, direct API calls). Universally recommended. | Only legacy systems with heavily entrenched language-agnostic backend validation (e.g., mature Java Spring Boot + Hibernate) where TypeScript rewrite is infeasible. | Pallet.com — uses shared Zod schemas to enforce type safety across internal systems, AI agents, and frontend interfaces in logistics workflows. |
| System-Versioned Temporal Auditing (Database-Level Version Control) | Azure SQL feature that automatically tracks full history of data changes. Creates Period Start/End datetime2 columns and mirrored History Table. On UPDATE/DELETE, previous row state is autonomously archived. Enables FOR SYSTEM_TIME AS OF time-travel queries. | Manufacturing, healthcare, financial enterprises requiring regulatory compliance, data forensics, or point-in-time form state reconstruction. Superior to application-layer auditing (no race conditions, no code circumvention). | Highly volatile tables with millions of transient updates/hour (IoT telemetry, session state) where history table bloat causes severe storage/performance costs. | OUTsurance (insurance) — temporal tables for point-in-time policy snapshots, proving compliance while hiding versioning complexity behind native DB mechanisms. |
| Wizard Pattern + Logic Engine | Multi-step form UI segmented via state machine. RHF manages state across unmounted steps. Conditional visibility decoupled to json-rules-engine. Shared Zod schemas validate complex nested payloads. | Multi-step workflows with conditional logic and relational data (employee onboarding, multi-stage QA inspections). | Single-step flat forms where wizard overhead is unjustified. | (No specific company cited — described as the Moderate tier recommendation.) |
| Static React Components + Basic RHF | Forms hardcoded in Next.js Client Components with inline Zod schemas. Direct Server Action submission to flat DB table. | Single-step, flat data, isolated scope (contact forms, simple inventory checks). 1-2 weeks per form. | Anything requiring conditional logic, revision control, or schema evolution. | (No specific company cited — described as the Simple tier recommendation.) |

---

## D. Complexity & Risk Assessment

| Tier | Recommended Pattern | Integration Points | Key Risks | Agent-Readiness |
|---|---|---|---|---|
| Simple (single-step, flat data) | Static React Components + Basic RHF + inline Zod + Server Action to flat table | Easy Auth secures endpoint; Azure SQL parameterized INSERTs to non-temporal tables | Code duplication/boilerplate fatigue across similar forms; stale data without optimistic UI; field changes require full CI/CD cycle | **High** — deterministic, well-documented pattern; RHF+Zod+Server Action is a well-trodden path with abundant examples; easily specified as agent prompt |
| Moderate (multi-step, conditional logic) | Wizard Pattern + json-rules-engine + shared Zod schemas + RHF cross-step state | Azure SQL Temporal Tables for QA data versioning; Entra ID RBAC from X-MS-CLIENT-PRINCIPAL header for step-level authorization | State loss on abandoned multi-step forms (requires draft-saving/local storage hydration); validation desync when hidden fields block submission if schema not dynamically updated | **Medium** — state machine design and rules engine integration require architectural decisions upfront (which steps, what rules, draft persistence strategy); once designed, agents can build each step |
| Complex (dynamic schema, revision-controlled, audit-trailed) | Metadata-Driven UI + JSON columns + Temporal Tables + Document Intelligence | Azure AI Document Intelligence v4.0 for OCR auto-population; Azure SQL JSON_VALUE querying + columnstore indexes on history tables | Schema evolution breaking backward compatibility if semantic versioning ignored; performance degradation from nested dynamic components + JSON querying; testing overhead from infinite form permutations | **Low** — requires significant human judgment on schema design, renderer boundaries, and preventing the engine from becoming a Turing-complete low-code platform; novel integration between json-rules-engine and dynamic RHF contexts has limited documentation |

**Agent-Readiness** ratings:
- **High** — well-documented, deterministic, can be specified as a clear prompt/plan for coding agents
- **Medium** — requires some architectural decisions upfront, then agents can execute
- **Low** — requires significant human judgment during implementation, ambiguous contracts, or novel integration with limited documentation

---

## E. Sources & Evidence Quality

**Total sources cited:** 60 (numbered references in the .md Works Cited section)
**Sources with URLs that resolve:** ~8 of 10 key sources appear to resolve (spot-checked: react-hook-form.com, learn.microsoft.com temporal tables, tanstack.com/form, github.com/CacheControl/json-rules-engine, learn.microsoft.com/document-intelligence all valid; the Hike Medical Medium post and Pallet.com blog are plausible but harder to verify; the tecktol.com Zod article and bizdata360 REST vs GraphQL are less well-known domains)
**Recency range:** April 2025 (oldest dated source: Medium article on Next.js forms) — February 2026 (most sources accessed date). Bulk of sources are "Accessed February 26, 2026" with no original publication dates, making true recency hard to assess.
**Notable gaps:**
- No coverage of T-SQL stored procedure patterns for business logic — the source assumes all server-side logic lives in Node.js/TypeScript, completely ignoring constraint #1 (business logic stays in T-SQL)
- No mention of Dapper — recommends Drizzle or Prisma as the ORM, directly conflicting with constraint #2 (thin API layer, Dapper)
- No discussion of offline/progressive web app capabilities for factory floor scenarios
- Weak coverage of testing strategies for dynamic forms — acknowledges testing overhead as a risk but offers no concrete patterns (snapshot testing, contract testing, property-based testing)
- No discussion of form versioning at the application level (schema version migrations, backward-compatible rendering of historical submissions)
- No cost analysis or Azure pricing considerations
- AI coverage limited to Document Intelligence — no mention of Azure OpenAI for smart defaults, LLM-assisted field suggestions, or data quality checks beyond OCR

---

## F. Extractor Notes

**Overall quality assessment:** Strong — the most comprehensive and architecturally detailed source of the set. The 56KB .md provides a full end-to-end architecture with specific technology versions, detailed data flow descriptions, and well-reasoned trade-off analysis. The .json provides cleanly structured data that aligns with the .md but adds useful structured fields (the full diagram description with frontend/API/persistence/background/observability/security flows).

**Unique insights not likely in other reports:**
- json-rules-engine as a dedicated, decoupled business rules engine for conditional form logic — most sources likely recommend inline conditional rendering rather than a separate rules engine with JSON-stored rules
- Detailed X-MS-CLIENT-PRINCIPAL header decoding flow for RBAC within Server Actions — practical implementation detail for Easy Auth integration
- Explicit tiered complexity model (Simple/Moderate/Complex) with different architectural patterns per tier — prevents over-engineering simple forms with the schema-driven engine
- Strong position that Document Intelligence is "far superior to probabilistic LLMs" for structured form extraction — useful counterpoint to LLM-everything approaches
- Observability layer description including Application Insights correlation IDs spanning client through database
- Factory pattern description for mapping JSON schema field types to shadcn/ui components — actionable implementation detail
- The "form engine" warning: "Moving from Moderate to Complex represents a profound paradigm shift: transitioning from building forms to building a form engine" with explicit caution against Turing-complete drift

**Red flags or questionable claims:**
- **ORM recommendation directly conflicts with established constraints.** Source recommends Drizzle or Prisma. The project uses Dapper with T-SQL stored procedures. This is not a minor deviation — it represents a fundamentally different persistence philosophy (ORM-managed migrations vs. DBA-managed T-SQL).
- **Server Actions as the sole API layer is aggressive.** While Server Actions are excellent for form submissions, the source presents them as a complete replacement for REST API routes. This may not hold for all use cases (e.g., external integrations, mobile clients, third-party consumers). The alternative stack section acknowledges this implicitly via GraphQL but frames it only as a negative.
- **Ignores T-SQL business logic entirely.** Constraint #1 says business logic stays in T-SQL. The source puts all business logic in Node.js via json-rules-engine and Zod. This is the single biggest tension with the existing architecture.
- **JSON columns for form payloads directly tensions with constraint #5** (well-defined data model, no EAV/configurable schema). The source recommends JSON columns for "evolving schemas" and "unpredictable payloads" — this is effectively a schema-flexible approach that the constraint is designed to prevent.
- **"60fps on factory floor tablets" is an unsubstantiated performance claim.** While RHF's uncontrolled component model is genuinely performant, the 60fps claim on low-powered devices is marketing language, not a benchmarked result.
- **Person-week estimates assume a 2-3 developer team, not a 1-human + agents team.** The 6-8 week estimate for the schema-driven engine and 10-15+ weeks for the complex tier need significant recalibration.
- **Many sources are "Accessed February 26, 2026" with no original publication dates.** This makes it impossible to assess whether the underlying research is current or recycled from older articles.
- **EAV is presented as a strawman alternative.** The alternative stack bundles EAV + GraphQL + TanStack Form together and then dismantles the whole package. A fairer comparison would evaluate each technology independently.

**Agent-implementation considerations:**
- **Simple tier is highly agent-ready.** Static RHF + Zod + Server Action forms are a well-documented, deterministic pattern. An agent can scaffold these from a clear spec (field list, validation rules, target table) with minimal human input.
- **Shared Zod schema pattern (2-3 person-weeks) is the highest-value agent target.** Well-documented, deterministic, and eliminates a major bug category. An agent could generate Zod schemas from a SQL table definition or TypeScript interface with high confidence.
- **Temporal table DDL migration is highly agent-ready.** Converting existing tables to system-versioned temporal is a well-documented SQL operation. An agent could generate the ALTER TABLE statements from the current schema with zero ambiguity.
- **The schema-driven form renderer requires a human architect first.** The JSON schema format, component mapping rules, and rules engine integration all require design decisions before an agent can build. Once the schema contract is defined, agents can build the renderer, but the contract itself is a human judgment call.
- **json-rules-engine integration is a medium-readiness task.** The library is well-documented, but bridging its async evaluation with RHF's synchronous rendering requires custom hooks that have limited public examples. An agent would need a clear interface contract.
- **The ORM conflict must be resolved before any agent work on the persistence layer.** If the team sticks with Dapper + T-SQL (constraints #1 and #2), the entire "TypeScript ORM" recommendation from this source must be translated into stored procedure calls. This is a human decision with cascading implications.
- **Document Intelligence integration is medium agent-readiness.** The REST API is well-documented, but mapping extracted key-value pairs to specific form schemas requires domain knowledge about which fields map where. The confidence scoring and human review workflow need design before an agent builds it.
