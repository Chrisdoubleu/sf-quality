# Enterprise form design and data architecture for manufacturing

**React Hook Form + Zod on Next.js 15 remains the optimal frontend foundation**, but the real architectural decisions lie in how you store evolving form schemas, enforce validation across boundaries, and integrate Azure services for audit trails and document intelligence. For a 200-employee manufacturing company on Azure, the recommended architecture pairs a hybrid relational-plus-JSON persistence layer in Azure SQL (with temporal tables for audit trails) with tRPC v11 for end-to-end type safety, shared Zod schemas for layered validation, and Azure Document Intelligence v4.0 for AI-assisted data capture. This stack keeps the team in TypeScript end-to-end, avoids introducing new infrastructure, and provides the audit and revision control manufacturing operations demand.

The research below synthesizes findings across frontend frameworks, architecture patterns, database design, validation strategies, AI services, and Azure platform specifics — all evaluated against the company's existing Next.js 15 / Azure SQL / Entra ID stack.

---

## Section A — Technology comparison matrix

| Name & Version | Category | Maturity | Azure Compat. | Learning Curve | Best Suited For | Key Limitation | Source URL |
|---|---|---|---|---|---|---|---|
| **React Hook Form 7.71.2** | Frontend library | Production-ready | Native | Low | All business forms; baseline for shadcn/ui integration | Controller wrapper needed for rich editors; verbose for deeply nested forms | https://react-hook-form.com |
| **TanStack Form 1.28.3** | Frontend library | Production-ready | Native | Medium | Complex nested/dynamic forms with strict TypeScript | Smaller ecosystem; requires custom shadcn/ui wrappers | https://tanstack.com/form |
| **react-jsonschema-form (RJSF) 6.3.1** | Frontend library | Production-ready | Good | Medium | Generating forms dynamically from JSON Schema definitions | No native Zod support (uses AJV); no shadcn/ui theme | https://rjsf-team.github.io/react-jsonschema-form |
| **JSON Forms 3.7.0** | Frontend library | Production-ready | Good | High | Schema-driven admin/configuration UIs with enterprise support | Default MUI renderers incompatible with shadcn/ui; custom renderers verbose | https://jsonforms.io |
| **tRPC 11.10.0** | API / Validation | Production-ready | Native | Medium | End-to-end type-safe API layer for Next.js + Zod | Not callable by external clients without adapter; TypeScript-only | https://trpc.io |
| **Prisma 7.x** | Backend ORM | Production-ready | Native | Low | Azure SQL access with type-safe queries and migrations | Managed Identity support still requires workaround; schema drift possible | https://www.prisma.io |
| **Azure SQL Temporal Tables** | Database approach | Production-ready | Native | Low | Automatic audit trails and revision history for form data | No native "who changed" tracking; history cleanup not automatic | https://learn.microsoft.com/en-us/azure/azure-sql/temporal-tables |
| **Azure SQL Native JSON** | Database approach | Production-ready | Native | Low | Flexible form field storage alongside relational columns | JSON Index not yet available in Azure SQL DB (only SQL Server 2025 on-prem) | https://learn.microsoft.com/en-us/sql/relational-databases/json/json-data-sql-server |
| **json-rules-engine 7.3.1** | Validation / Rules | Production-ready | Good | Medium | Externalizing conditional business rules as database-stored JSON | Limited to boolean condition evaluation; no built-in form field awareness | https://github.com/CacheControl/json-rules-engine |
| **Zod 3.x** | Validation tool | Production-ready | Native | Low | Shared client/server schema validation with TypeScript inference | superRefine won't run until base validations pass; async refine can over-fire | https://zod.dev |
| **Azure Document Intelligence 4.0** | AI service | Production-ready | Native | Medium | OCR and structured data extraction from manufacturing documents | Custom model training requires labeled samples; no real-time streaming | https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence |
| **Azure OpenAI Service (GPT-4o)** | AI service | Production-ready | Native | Medium | Smart defaults, data quality checks, NL-to-form-data conversion | Hallucination risk for extraction; no confidence scores; higher cost than OCR | https://learn.microsoft.com/en-us/azure/ai-services/openai |
| **Formik 2.4.9** | Frontend library | Maintenance mode | Good | Low | Legacy codebases only | Near-dormant maintenance; 44KB bundle; re-renders on every keystroke | https://formik.org |
| **Uniforms 4.0.0** | Frontend library | Production-ready | Good | Medium | Auto-generating forms from Zod schemas via AutoForm pattern | Tiny community (~15K weekly downloads); slow release cadence | https://uniforms.tools |

---

## Section B — Recommended architecture

### 1. Diagram description

The architecture follows a five-layer flow optimized for the Azure + Next.js stack:

**Layer 1 — Browser (React 19 + shadcn/ui).** Users interact with forms rendered by React Hook Form bound to dynamically generated Zod schemas. shadcn/ui primitives provide accessible, consistent field components. Client-side courtesy validation runs Zod `.safeParse()` on every blur/submit for instant feedback. Form definitions are fetched and cached via TanStack Query.

**Layer 2 — Next.js App Router (Azure App Service Linux).** Two API patterns coexist: tRPC v11 handles all form CRUD and submission mutations with Zod `.input()` validation as the authoritative server-side gate. Next.js Server Actions handle simple progressive-enhancement mutations (e.g., quick status updates). The App Service runs `output: 'standalone'` Node.js with Entra ID Easy Auth injecting authentication headers (`x-ms-client-principal`) at the platform level before requests reach application code.

**Layer 3 — Validation & Business Rules.** Shared Zod schemas (imported by both client and server) ensure zero validation drift. A `json-rules-engine` instance evaluates externalized business rules stored in Azure SQL — rules like "if product category is Chemical AND quantity exceeds 500, require Safety Officer approval" run on both client (for field visibility) and server (for authoritative enforcement).

**Layer 4 — Persistence (Azure SQL Database).** A hybrid relational + JSON schema stores form definitions and submissions. Core queryable fields (submitter, status, form type, timestamps) live in typed relational columns with indexes and foreign keys. Variable form field data lives in a native `JSON` column. Azure SQL temporal tables automatically version every row change into history tables, providing a complete audit trail queryable via `FOR SYSTEM_TIME AS OF`. Prisma v7 manages the ORM layer with type-safe queries.

**Layer 5 — Azure Services (async processing).** Document uploads flow to Azure Blob Storage, triggering Azure Functions that call Azure Document Intelligence v4.0 for OCR/extraction. Extracted data returns to the form as pre-populated field suggestions via a tRPC subscription or polling endpoint. Azure OpenAI provides optional enrichment (smart defaults, data quality checks). All services authenticate via Managed Identity, eliminating credential management.

### 2. Primary stack

**Frontend forms: React Hook Form 7.71.x + Zod + shadcn/ui.** This is the only combination where all three libraries are designed to work together natively. shadcn/ui's `<Form>`, `<FormField>`, and `<FormItem>` components are literally built on React Hook Form's `Controller`. The `@hookform/resolvers/zod` bridge connects Zod schemas to RHF with zero glue code. With **25 million weekly npm downloads**, RHF has the largest community, the most hiring availability, and the deepest ecosystem of any React form library.

**Validation: Shared Zod schemas + json-rules-engine.** A single Zod schema file per form type is imported by both the client (via `zodResolver`) and the server (via tRPC `.input()`). This eliminates validation drift entirely — the same rules run in both environments. For complex business logic that changes without code deployments (conditional field requirements, approval routing, field visibility), `json-rules-engine` evaluates JSON rules stored in Azure SQL. Rules are editable by administrators without developer intervention.

**API layer: tRPC v11 as primary, Server Actions as supplement.** tRPC v11's `@tanstack/react-query` integration provides type-safe queries and mutations with automatic caching, deduplication, and optimistic updates. The `createCaller` API enables server-side calls without HTTP round-trips in React Server Components. Server Actions handle simple form posts where progressive enhancement matters. Route Handlers serve webhooks and any future external API consumers.

**Database / persistence: Azure SQL with hybrid relational + JSON + temporal tables.** Core metadata lives in typed columns with proper indexes and foreign keys. Dynamic form field data lives in a native `JSON` column (GA in Azure SQL since May 2024). Temporal tables (`SYSTEM_VERSIONING = ON`) automatically capture every INSERT/UPDATE/DELETE into a history table with UTC timestamps — no triggers, no application code, no performance tuning required. A `ModifiedBy` column (populated by application code from the Entra ID principal) supplements temporal tables with "who changed it" tracking.

**Authentication: Entra ID via Easy Auth.** Easy Auth runs as a platform-level module on Azure App Service, authenticating every request before it reaches Node.js. The application reads the `x-ms-client-principal` header to identify the user and extract role claims. No MSAL SDK or auth middleware is needed in the Next.js application itself. App roles defined in the Entra ID app registration manifest enable role-based access control for form permissions.

**Azure services: Document Intelligence + Functions + Blob Storage.** Azure Document Intelligence v4.0 handles OCR extraction from uploaded manufacturing documents (invoices, quality certificates, shipping manifests) using prebuilt and custom-trained models. Azure Functions (Durable Functions for multi-step workflows) orchestrate async processing — document upload triggers extraction, validation, and storage. Azure Blob Storage holds uploaded files with lifecycle policies.

### 3. Alternative stack

**Alternative: TanStack Form + Drizzle ORM + GraphQL + Cosmos DB**

Replace React Hook Form with **TanStack Form 1.28.x** for superior type-safe field paths and granular reactivity — particularly valuable for deeply nested manufacturing data (bills of materials, multi-level quality inspections). Replace Prisma with **Drizzle ORM** for a lighter, SQL-first approach (though note Drizzle lacks native MSSQL support, so this requires migrating to **Azure Cosmos DB** as the primary store). Replace tRPC with **GraphQL** (via Pothos + Yoga Server) for a self-documenting API that external systems (ERP, MES) can query directly.

**What you gain:** Better TypeScript inference for complex nested forms; a self-documenting API consumable by external systems; schema-free document storage that handles form evolution without migrations; global distribution if needed later.

**What you lose:** The mature RHF + shadcn/ui integration (must build custom wrappers); SQL-level audit trails via temporal tables (must implement change tracking in application code); transactional integrity across related entities (Cosmos DB transactions limited to single partitions); predictable costs (Cosmos DB RU billing can spike); team familiarity with SQL (most manufacturing teams know SQL, not NoSQL). **The primary stack is strongly recommended** given the existing Azure SQL investment and the team's likely SQL expertise.

---

## Section C — Pattern deep dives

### Pattern 1: Hybrid relational + JSON persistence

The hybrid pattern stores stable, frequently queried fields as typed relational columns alongside a native JSON column for variable form-specific data. In a manufacturing context, a `form_submissions` table has indexed columns for `id`, `form_definition_id`, `submitted_by`, `submitted_at`, `status`, and `line_id` (relational, with foreign keys and constraints), while the actual form field responses live in a `data JSON` column. Form definitions themselves follow the same pattern: relational columns for `name`, `version`, `status`, `created_by`, with the full field schema in a `schema JSON` column. This gives you SQL JOINs, referential integrity, and index performance for operational queries while absorbing form evolution without schema migrations.

**When to use:** Form systems where the structure evolves frequently (new fields added per product line, regulatory changes require new quality check fields) but core operational metadata is stable. When you need ACID transactions, SQL reporting, and foreign key relationships. When the team has SQL expertise. When Azure SQL is already the database platform.

**When to avoid:** When all fields are known and will never change (pure relational is simpler). When JSON documents exceed ~1MB regularly (full-document rewrites on updates become expensive). When every field inside the JSON needs individual SQL-level indexing (extract those fields into columns instead).

**Real-world example:** **Heap Analytics** uses PostgreSQL JSONB alongside relational columns for arbitrary event properties. They documented a **30% disk savings** by extracting 45 commonly-used fields from JSONB into dedicated columns, validating the hybrid approach of promoting hot paths to relational while keeping the long tail in JSON.

**Implementation complexity (2-3 developers):**
- Database schema design and migration setup: **1-2 weeks**
- Prisma model definitions and JSON column typing: **1 week**
- Computed columns and indexing strategy for Azure SQL: **0.5-1 week**
- Temporal table configuration and audit query layer: **1 week**
- Integration testing and performance validation: **1 week**
- **Total: 4.5-6 weeks**

### Pattern 2: Schema-driven form rendering with dynamic Zod generation

A JSON form definition stored in the database describes every aspect of a form: fields, types, validation rules, conditional visibility logic, layout hints, and default values. At runtime, a `generateZodSchema()` function transforms this definition into a Zod object schema, which feeds into React Hook Form via `zodResolver`. A `FieldRenderer` component maps each field type to the corresponding shadcn/ui component. This decouples form structure from frontend code — new forms or field changes require only database updates, not code deployments. The pattern is especially powerful in manufacturing where quality inspection forms vary by product line and change with regulatory requirements.

**When to use:** When forms change frequently and changes must not require code deployments. When non-developers (quality managers, compliance officers) need to modify form structures. When supporting many form variants (different inspection checklists per product line). When frontend and backend validation must stay in sync automatically.

**When to avoid:** When forms have highly bespoke, interactive UI that cannot be expressed declaratively (drag-and-drop interfaces, real-time 3D visualizations). When you have fewer than 10 stable form types that rarely change. When the overhead of a rendering engine and schema parser isn't justified.

**Real-world example:** **Adobe Experience Manager (AEM) Headless Adaptive Forms** implements this pattern with a JSON form model, a Business Rule Processor (managing state, validation, conditional logic), and a React Binder (hooks connecting to UI). The architecture explicitly separates the form logic core from the rendering layer, enabling the same form definition to render across web, mobile, and conversational interfaces.

**Implementation complexity (2-3 developers):**
- JSON form definition schema design: **1-2 weeks**
- Dynamic Zod schema generator (field types, validation rules, conditionals): **2-3 weeks**
- FieldRenderer component registry (15-20 shadcn/ui field types): **2-3 weeks**
- Conditional logic engine (json-rules-engine integration): **1-2 weeks**
- Form definition admin UI (basic CRUD): **2-3 weeks**
- Testing (edge cases in dynamic schema generation): **2 weeks**
- **Total: 10-15 weeks**

### Pattern 3: Layered validation with shared Zod schemas

This pattern establishes three validation tiers sharing a common Zod schema as the source of truth. **Tier 1 (client courtesy):** React Hook Form runs `zodResolver(schema)` on blur and submit for instant user feedback — this is advisory only and never trusted. **Tier 2 (server authoritative):** tRPC procedures run `schema.parse(input)` as the security boundary — all data must pass this gate before touching the database. **Tier 3 (business rules):** `json-rules-engine` evaluates externalized rules that encode business logic too complex or too frequently changing for Zod schemas (approval routing, conditional requirements based on external data, cross-entity validation). The key insight is that Tiers 1 and 2 share literally the same `.ts` file — `z.infer<typeof schema>` generates TypeScript types consumed by both client components and server procedures, making it impossible for validation logic to drift.

**When to use:** Any enterprise application where validation correctness is critical (manufacturing quality data, compliance forms, financial data). When business rules change frequently and must be updatable without code deployments. When the same form data is submitted from multiple clients (web, mobile, API).

**When to avoid:** When all validation is simple field-level checks (email format, required fields) — Zod alone suffices without a rules engine. When the team lacks TypeScript expertise to maintain shared schemas. When forms are entirely server-rendered with no client-side interactivity.

**Real-world example:** **MakerKit.dev**, a popular Next.js SaaS boilerplate used by thousands of developers, documents this exact pattern: shared Zod schemas between client and `next-safe-action` server actions, with the same schema powering React Hook Form's `zodResolver` and the server's `action.input()`. Their engineering blog reports that refactoring to this pattern "cut mutation code nearly in half."

**Implementation complexity (2-3 developers):**
- Shared schema package setup (monorepo or shared directory): **0.5 week**
- Core Zod schemas for existing form types: **1-2 weeks**
- tRPC router with Zod input validation: **1-2 weeks**
- json-rules-engine integration and rule storage: **1-2 weeks**
- Client-side zodResolver integration with RHF: **0.5-1 week**
- Testing (ensuring client/server parity, edge cases): **1 week**
- **Total: 5-8 weeks**

---

## Section D — Build approach decision matrix

| Dimension | Simple (single-step, flat data) | Moderate (multi-step, conditional, relational) | Complex (dynamic schema, revision-controlled, audit-trailed) |
|---|---|---|---|
| **Recommended pattern** | Static React Hook Form + Zod + shadcn/ui + Server Actions | Multi-step wizard with shared Zod schemas + tRPC + conditional logic engine | Schema-driven rendering + hybrid relational/JSON + temporal tables + business rules engine |
| **Estimated build effort** | **1-3 person-weeks** | **6-10 person-weeks** | **16-26 person-weeks** |
| **Technical risk 1** | Over-engineering: temptation to build dynamic infrastructure for static forms wastes time | Step state management: cross-step validation and draft persistence introduce subtle bugs with React Hook Form's uncontrolled model | Schema evolution: changing form definitions after data collection requires migration logic to handle submissions made against older schema versions |
| **Technical risk 2** | Validation bypass: client-only validation without server-side Zod check creates a security gap | Conditional logic explosion: business rules grow combinatorially and become untestable without externalization via a rules engine | Performance degradation: dynamic Zod schema generation on every render can be expensive for forms with 100+ fields; requires memoization and caching |
| **Technical risk 3** | — | Azure SQL connection pooling: multi-step forms with frequent draft saves can exhaust Prisma connection pools without proper singleton pattern | Audit trail storage growth: temporal tables capture every UPDATE as a new history row; high-frequency forms (quality checks every 15 minutes) can generate substantial history tables requiring retention policies |
| **Azure App Service integration** | Deploy as `output: 'standalone'` on Linux App Service; Server Actions handle form POST natively; no additional infrastructure needed | Same deployment; add tRPC route handler at `/api/trpc/[trpc]/route.ts`; use TanStack Query for step data caching and optimistic updates | Same deployment; add Azure Functions for async form definition compilation and validation; use App Service deployment slots for zero-downtime schema updates |
| **Azure SQL integration** | Simple Prisma model with typed columns; standard `INSERT` on submit | Prisma models with relations (form → steps → fields); draft submissions stored as rows with `status = 'draft'`; computed columns for frequently filtered JSON fields | Temporal tables on `form_definitions` and `form_submissions`; native JSON columns for flexible field data; computed columns + indexes on hot JSON paths; retention policy on history tables (`HISTORY_RETENTION_PERIOD = 7 YEARS`) |
| **Entra ID integration** | Easy Auth provides `x-ms-client-principal` header; extract user ID for `created_by` column | Same + app roles for step-level permissions (e.g., "only QA Manager can approve Step 3"); role claims from Entra ID manifest | Same + row-level security using Entra ID roles; `ModifiedBy` column populated from principal for audit "who changed" tracking; app roles govern form definition editing vs. form submission |

---

## Section E — Key sources

1. **"React Hook Form — shadcn/ui"** — https://ui.shadcn.com/docs/forms/react-hook-form — Accessed February 2026. Official shadcn/ui documentation showing the canonical integration of React Hook Form + Zod, establishing this as the blessed pattern for the component library.

2. **"Temporal Tables — Azure SQL | Microsoft Learn"** — https://learn.microsoft.com/en-us/azure/azure-sql/temporal-tables — Accessed February 2026. Official Microsoft documentation covering temporal table creation, querying, retention policies, and performance guidance specific to Azure SQL Database.

3. **"What Is Azure Document Intelligence (Foundry Tools)? | Microsoft Learn"** — https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0 — Accessed February 2026. Official documentation for v4.0 GA, detailing prebuilt models, custom training, pricing, and SDK availability for the primary AI extraction service.

4. **"TanStack Form vs. React Hook Form — LogRocket Blog"** — https://blog.logrocket.com/tanstack-form-vs-react-hook-form/ — Published June 9, 2025. The most comprehensive independent comparison of these two libraries, with benchmark data, feature matrices, and specific guidance on when each excels.

5. **"Comparison | TanStack Form Docs"** — https://tanstack.com/form/latest/docs/comparison — Accessed February 2026. Official TanStack side-by-side feature comparison covering type safety, validation integration, framework support, and reactivity models across all major form libraries.

6. **"JSON Data in SQL Server | Microsoft Learn"** — https://learn.microsoft.com/en-us/sql/relational-databases/json/json-data-sql-server — Accessed February 2026. Official Microsoft documentation on JSON functions, the native JSON data type, computed column indexing strategies, and hybrid relational/JSON patterns in SQL Server and Azure SQL.

7. **"Dynamic Forms Architecture and Design — Progress Corticon"** — https://www.progress.com/blogs/dynamic-forms-architecture-design — Published July 14, 2022. Authoritative enterprise architecture guide for separating form business rules (model) from rendering (view), with open-source implementation samples, from a major enterprise software vendor.

8. **"tRPC v11 Documentation"** — https://trpc.io/docs — Accessed February 2026. Official documentation for tRPC v11, covering Next.js 15 App Router integration, Zod input validation, TanStack Query v5 integration, and the `createCaller` API for server-side usage.

9. **"Guides: Forms | Next.js"** — https://nextjs.org/docs/app/guides/forms — Accessed February 2026. Official Next.js documentation covering Server Actions, `useActionState`, `useFormStatus`, and `useOptimistic` — the framework-level form primitives that all other tools build upon.

10. **"When to Avoid JSONB in a PostgreSQL Schema — Heap Engineering"** — https://www.heap.io/blog/when-to-avoid-jsonb-in-a-postgresql-schema — Published 2024. Real-world production data from Heap Analytics showing 30% disk savings from extracting hot JSON fields into relational columns, providing empirical validation for the hybrid storage pattern recommended in this report.