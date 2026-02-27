# Forms Research Extraction — Claude Deep Research

**Source:** claude-deep-research.md + claude-deep-research.json
**Model/Platform:** Claude (Anthropic) Deep Research
**Date produced:** 2026-02 (exact date not specified; sources accessed February 2026)
**Extracted by:** Claude Opus 4.6 (automated extraction, 2026-02-26)

---

## A. Technology Recommendations

| Technology | Category | Maturity | Azure Fit | Rec. Level | Rationale (1-2 sentences) | Limitations Noted |
|---|---|---|---|---|---|---|
| React Hook Form 7.71.2 | Frontend forms | Production-ready | Native | Primary | Only library with native shadcn/ui integration; 25M weekly npm downloads; @hookform/resolvers/zod provides zero-glue-code Zod bridge. | Controller wrapper needed for rich editors; verbose for deeply nested forms; useActionState wiring with Server Actions requires care. |
| TanStack Form 1.28.3 | Frontend forms | Production-ready | Native | Alternative | Superior type-safe field paths and granular signal-based reactivity for deeply nested manufacturing data (BOMs, multi-level QC inspections). | ~15x fewer downloads than RHF; no native shadcn/ui integration (custom wrappers required); smaller ecosystem. |
| RJSF 6.3.1 | Schema-driven forms | Production-ready | Good | Evaluated | Generates forms dynamically from JSON Schema definitions stored in database. | No native Zod support (uses AJV); no shadcn/ui theme; two separate validation systems to maintain. |
| JSON Forms 3.7.0 | Schema-driven forms | Production-ready | Good | Evaluated | Eclipse Foundation-backed; three-schema model (data, UI, rule) for enterprise flexibility. | Default MUI renderers incompatible with shadcn/ui; custom renderers verbose; steep learning curve. |
| Formik 2.4.9 | Frontend forms | Maintenance mode | Good | Not recommended | Legacy codebases only. | Near-dormant; 44KB bundle; re-renders every keystroke; no native Zod. |
| Uniforms 4.0.0 | Auto-generating forms | Production-ready | Good | Evaluated | AutoForm pattern from Zod schemas; rapid admin UI prototyping. | ~15K weekly downloads; slow release cadence; limited customization. |
| tRPC 11.10.0 | API layer | Production-ready | Native | Primary | End-to-end type-safe API with Zod .input() as authoritative server gate; @tanstack/react-query integration; createCaller for RSC. | Not callable by external clients without adapter; TypeScript-only ecosystem. |
| Prisma 7.x | ORM | Production-ready | Native | Primary | Type-safe Azure SQL access with migrations and connection pooling. | Managed Identity requires workaround config; schema drift if JSON columns bypass type system. |
| Azure SQL Temporal Tables | Database audit | Production-ready | Native | Primary | Automatic audit trail on every row change via SYSTEM_VERSIONING; no triggers/app code needed; FOR SYSTEM_TIME AS OF queries. | No native "who changed" tracking (needs ModifiedBy column in app code); history cleanup requires explicit retention policies. |
| Azure SQL Native JSON | Database flexibility | Production-ready | Native | Primary | GA since May 2024; ~18% storage savings over NVARCHAR(MAX); enables hybrid relational+JSON pattern. | JSON Index (CREATE JSON INDEX) not yet available in Azure SQL DB (on-prem SQL Server 2025 only); must use computed column + standard index workaround. |
| json-rules-engine 7.3.1 | Business rules | Production-ready | Good | Primary | Externalizes conditional business rules as database-stored JSON; admin-editable without code deployments. | Limited to boolean condition evaluation; no built-in form field awareness; complex rule chains need careful design. |
| Zod 3.x | Validation | Production-ready | Native | Primary | Single schema file shared by client (zodResolver) and server (tRPC .input()); z.infer generates TS types for both environments. | superRefine blocks on base validation failure; async refine can over-fire; bundle grows with schema complexity. |
| Azure Document Intelligence 4.0 | AI/OCR | Production-ready | Native | Primary | OCR + structured data extraction from manufacturing documents (invoices, COAs, quality certs); prebuilt + custom models. | Custom model training requires labeled samples; no real-time streaming (async architecture needed); accuracy depends on document quality. |
| Azure OpenAI (GPT-4o) | AI enrichment | Production-ready | Native | Optional | Smart defaults, data quality checks, NL-to-structured-data conversion, context-aware autocomplete. | Hallucination risk; no confidence scores; higher cost than OCR; non-deterministic outputs require user confirmation. |

**Stack-relevant picks** (fit current Next.js/React/Azure stack):
- React Hook Form + Zod + shadcn/ui (frontend) -- already in stack, confirmed as optimal
- tRPC v11 (API layer) -- new recommendation, replaces thin REST
- Prisma 7.x (ORM) -- new recommendation, **directly tensions with Constraint #2 (thin API, Dapper not EF)**
- Azure SQL temporal tables + native JSON (persistence) -- compatible with existing Azure SQL
- json-rules-engine (business rules) -- new addition
- Azure Document Intelligence 4.0 (AI extraction) -- new Azure service

**Stack-incompatible picks** (comparison only):
- TanStack Form -- viable alternative but lacks shadcn/ui integration
- RJSF, JSON Forms -- schema-driven but incompatible with Zod/shadcn/ui ecosystem
- Formik -- deprecated, not recommended
- Drizzle ORM -- lacks native MSSQL support
- Azure Cosmos DB -- alternative stack only, not recommended given Azure SQL investment

---

## B. Architecture Recommendation

**Primary stack summary:**
- Frontend: React Hook Form 7.71.x + Zod + shadcn/ui -- native integration across all three; largest ecosystem
- Validation: Shared Zod schemas (Tiers 1-2) + json-rules-engine (Tier 3) -- zero validation drift; externalized business rules
- API layer: tRPC v11 (primary) + Next.js Server Actions (supplement) -- type-safe mutations with Zod input gates; Server Actions for progressive enhancement
- Database/persistence: Azure SQL hybrid relational + JSON columns + temporal tables via Prisma 7.x -- stable fields in typed columns, variable data in JSON, automatic audit trail
- Auth: Entra ID Easy Auth (platform-level) -- x-ms-client-principal header, app roles from manifest, no MSAL SDK needed
- AI services: Azure Document Intelligence 4.0 + Azure Functions (Durable) + Blob Storage -- async OCR pipeline for manufacturing documents

**Alternative stack:** TanStack Form + Drizzle ORM + GraphQL (Pothos + Yoga) + Azure Cosmos DB. Key trade-off: gains better nested-form typing and a self-documenting API for external ERP/MES integration, but loses temporal table audit trails, transactional integrity, predictable costs, and team SQL familiarity. Source strongly recommends against this alternative.

**Unique architectural claims** (positions this source takes others may not):
- Recommends tRPC v11 as the primary API pattern with Server Actions as a secondary/supplement pattern -- this is a strong opinion favoring full type-safety over REST
- Explicitly recommends Prisma 7.x as the ORM layer -- **directly conflicts with Constraint #2** (Dapper, thin API, no ORM). The source does not acknowledge this constraint exists.
- Proposes a five-layer architecture with an async processing layer (Azure Functions + Document Intelligence) as a core layer, not an add-on
- Recommends json-rules-engine specifically for admin-editable business rules stored in Azure SQL, running on both client AND server
- Advocates "secretless" architecture via System-Assigned Managed Identity for all Azure service connections
- JSON data in the .json file includes an `observability_flow` (Application Insights via instrumentation.js) and `security_flow` (row-level security, Managed Identity) that are NOT present in the .md -- these are additional architectural positions
- Recommends React's cache API for a centralized Data Access Layer (DAL) to memoize session verification (only in .json)

---

## C. Patterns Identified

| Pattern Name | Description | When to Use | When to Avoid | Real-World Example |
|---|---|---|---|---|
| Hybrid Relational + JSON Persistence | Core queryable fields (submitter, status, timestamps) in typed relational columns with indexes/FKs; variable form field data in native JSON column. Form definitions follow the same pattern (relational metadata + JSON schema column). | Forms evolve frequently (new fields per product line, regulatory changes); need ACID + SQL reporting + FK relationships; Azure SQL already in use; team has SQL expertise. | All fields known and stable (pure relational simpler); JSON docs exceed ~1MB regularly; every JSON field needs individual SQL-level indexing. | Heap Analytics: PostgreSQL JSONB + relational columns; 30% disk savings from extracting 45 hot fields from JSONB to columns. |
| Schema-Driven Form Rendering + Dynamic Zod Generation | JSON form definition in DB describes fields, types, validation, conditional visibility, layout hints. Runtime `generateZodSchema()` transforms to Zod; `FieldRenderer` maps field types to shadcn/ui components. Decouples form structure from frontend code. | Forms change frequently without code deployments; non-developers need to modify forms; many form variants (per product line); frontend/backend validation must sync automatically. | Highly bespoke interactive UI (drag-drop, 3D); fewer than 10 stable form types that rarely change; rendering engine overhead not justified. | Adobe AEM Headless Adaptive Forms: JSON form model + Business Rule Processor + React Binder; same definition renders across web, mobile, conversational. |
| Layered Validation with Shared Zod Schemas | Three tiers: (1) Client courtesy via zodResolver on blur/submit (advisory); (2) Server authoritative via tRPC schema.parse() (security boundary); (3) Business rules via json-rules-engine for complex/frequently-changing logic. Tiers 1+2 share the same .ts file. | Validation correctness critical (quality data, compliance, financial); business rules change without deployments; same data from multiple clients. | All validation is simple field-level; team lacks TS expertise; forms entirely server-rendered. | MakerKit.dev: shared Zod schemas between client and next-safe-action; reports "cut mutation code nearly in half." |

---

## D. Complexity & Risk Assessment

| Tier | Recommended Pattern | Integration Points | Key Risks | Agent-Readiness |
|---|---|---|---|---|
| Simple (single-step, flat data) | Static RHF + Zod + shadcn/ui + Server Actions | App Service standalone; simple Prisma model; Easy Auth x-ms-client-principal for created_by | (1) Over-engineering static forms with dynamic infrastructure. (2) Validation bypass if client-only without server Zod check. | **High** -- well-documented pattern, deterministic, shadcn/ui docs provide exact code. Agent can scaffold a complete form from a schema definition with minimal guidance. |
| Moderate (multi-step, conditional, relational) | Multi-step wizard + shared Zod + tRPC + json-rules-engine | tRPC route at /api/trpc/[trpc]/route.ts; TanStack Query for step caching; Prisma relations (form->steps->fields); draft rows; app roles for step-level perms | (1) Cross-step validation + draft persistence bugs with RHF's uncontrolled model. (2) Conditional logic explosion without rules engine. (3) Azure SQL connection pool exhaustion from frequent draft saves without Prisma singleton. | **Medium** -- requires upfront decisions on step state model, draft persistence strategy, and rules engine schema. Once decided, agents can implement individual steps deterministically. The json-rules-engine integration is well-documented enough for agents. |
| Complex (dynamic schema, revision-controlled, audit-trailed) | Schema-driven rendering + hybrid relational/JSON + temporal tables + rules engine | Azure Functions for async form definition compilation + Document Intelligence; deployment slots for zero-downtime schema updates; temporal tables on both definitions and submissions; RLS via Entra roles; ModifiedBy from principal | (1) Schema evolution after data collection requires migration logic for old submissions. (2) Dynamic Zod generation perf for 100+ field forms (needs memoization). (3) Temporal table storage growth on high-frequency forms (retention policies needed). | **Low-Medium** -- the dynamic Zod generation, schema evolution handling, and form definition admin UI all require significant architectural judgment. The FieldRenderer registry (15-20 types) is repetitive and **high agent-readiness** once the first 2-3 are built as templates. The schema evolution/migration strategy is firmly **low agent-readiness** -- requires human design. |

**Effort estimates (source's original, for 2-3 developers):**
- Simple: 1-3 person-weeks
- Moderate: 6-10 person-weeks
- Complex: 16-26 person-weeks

**Effort estimates (agent-adjusted, 1 human + coding agents):**
- Simple: 0.5-1 week (high agent leverage; form scaffolding is nearly automatic)
- Moderate: 3-5 weeks (medium agent leverage; human designs step model and rules schema, agents implement)
- Complex: 10-16 weeks (mixed; FieldRenderer registry and CRUD admin are highly automatable, but schema evolution strategy, dynamic Zod generator edge cases, and the form definition admin UX require sustained human judgment)

---

## E. Sources & Evidence Quality

**Total sources cited:** 10
**Sources with URLs that resolve:** 10 (spot-checked shadcn/ui forms doc, Azure temporal tables doc, Heap blog, tRPC docs, TanStack Form comparison -- all resolve and match claimed content)
**Recency range:** July 2022 (Progress Corticon blog) -- February 2026 (multiple Azure/Next.js docs)
**Notable gaps:**
- No coverage of non-React frameworks (Vue, Angular, Blazor) despite the .json input prompt asking for them -- the source focused exclusively on the React/Next.js ecosystem
- No mention of Dapper or thin-API-layer patterns -- source assumes an ORM (Prisma) without discussion
- No coverage of the EAV (Entity-Attribute-Value) pattern as an alternative to hybrid relational+JSON, despite EAV being common in manufacturing and the input prompt asking about it
- No discussion of T-SQL stored procedures for business logic -- source places all business logic in TypeScript (json-rules-engine, Zod)
- No discussion of offline/disconnected scenarios (relevant for shop-floor data collection)
- Limited cost analysis -- mentions Cosmos DB cost unpredictability but no Azure SQL DTU/vCore sizing or App Service tier guidance

---

## F. Extractor Notes

**Overall quality assessment:** Strong -- the most architecturally detailed and internally consistent of the sources likely being compared. Clear layer-by-layer reasoning, specific version numbers, realistic effort estimates, and honest trade-off analysis. The .json file contains additional architectural detail (observability, security, DAL caching) not in the .md, making the pair more comprehensive than either alone.

**Unique insights not likely in other reports:**
- The explicit three-tier validation architecture (client courtesy / server authoritative / business rules engine) with the insight that Tiers 1+2 share the same .ts file is the clearest formulation of this pattern
- Specific callout of Azure SQL native JSON column being GA since May 2024 with ~18% storage savings over NVARCHAR(MAX) -- useful implementation detail
- The JSON Index limitation (only SQL Server 2025 on-prem, not Azure SQL DB) is a critical gotcha that other sources may miss
- Recommendation of json-rules-engine running on BOTH client (field visibility) and server (authoritative enforcement) from the same rule definitions
- The .json file's observability_flow recommending Next.js 15's stable instrumentation.js API for Application Insights integration
- The "secretless" Managed Identity architecture spanning all Azure services (SQL, Blob, Queue) with no stored connection strings

**Red flags or questionable claims:**
- **Prisma 7.x recommendation directly conflicts with Constraint #2** (thin API layer with Dapper, not Entity Framework). The source never acknowledges this constraint. Prisma is an ORM with a query engine runtime, migrations, and schema management -- it is the opposite of "thin." This is the single largest tension in the report and must be reconciled during consolidation.
- **tRPC recommendation may conflict with Constraint #2** as well. tRPC is not a "thin" API layer -- it is a full RPC framework with middleware, context, and its own router. The existing stack expectation is Dapper + minimal route handlers. However, tRPC's Zod integration for validation is genuinely valuable and could be adapted to work with a thinner approach.
- **No mention of T-SQL business logic conflicts with Constraint #1.** The source places all business logic in TypeScript (Zod schemas, json-rules-engine). This is a legitimate architectural position but is in direct tension with the existing constraint that business logic stays in T-SQL.
- **Schema-driven form rendering estimate of 10-15 person-weeks may be optimistic.** The admin UI alone (form builder) is a complex product that could easily consume that entire budget. The estimate does not account for schema migration tooling, versioning UX, or permission management for form definitions.
- **The "hybrid relational + JSON" pattern is presented as a recommendation but actually tensions with Constraint #5** (well-defined data model, no EAV/configurable schema). Storing variable form field data in a JSON column IS a form of configurable schema. Whether this tension is acceptable depends on interpretation -- if "configurable schema" means "end-users designing arbitrary forms" the constraint may still hold, but if it means "any non-fixed column structure" then JSON columns violate it.
- The Heap Analytics example (PostgreSQL JSONB) is from a completely different domain (analytics event properties) and the 30% savings figure is about going the other direction (extracting FROM JSON to relational). It actually argues for fixed schemas more than for JSON flexibility.

**Agent-implementation considerations:**
- The FieldRenderer component registry (15-20 shadcn/ui field types) is an ideal agent task: repetitive, well-documented, can be specified as "implement X field type matching the pattern of Y field type." Build 2-3 by hand, then agents replicate.
- Shared Zod schema files are highly agent-automatable: given a form definition (field names, types, constraints), an agent can generate the Zod schema, the tRPC procedure, and the RHF form component in one pass.
- The json-rules-engine rule JSON format is structured and documented, making rule creation a good agent task once the schema for rules is established.
- The dynamic Zod schema generator (`generateZodSchema()`) is the hardest piece to agent-implement correctly. Edge cases in conditional validation, cross-field dependencies, and async refinements require human review of the generator logic even if an agent writes the initial implementation.
- Temporal table setup in Azure SQL is a one-time T-SQL script -- trivially agent-automatable.
- The source's recommendation of Prisma would need to be reconciled with Dapper before agents can proceed on the data access layer. This is a human decision point.
