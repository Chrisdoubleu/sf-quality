# Divergence Log

**Generated:** 2026-02-26
**Inputs:** 4 extraction files (ChatGPT, Parallel, Gemini, Claude)

**This is the most important synthesis artifact.** It surfaces cross-source disagreements, challenges to existing constraints, and challenges to the Quality_Forms_Module design. All claims are grounded in the extraction files.

---

## Cross-Source Disagreements

| ID | Topic | Position A (source) | Position B (source) | Impact | Resolution Needed |
|---|---|---|---|---|---|
| D-01 | **API pattern** | Route Handlers as BFF (ChatGPT) | Server Actions as sole API (Gemini) | **Blocking** | Four sources, four API patterns. ChatGPT: Route Handlers. Parallel: Server Actions + Route Handlers. Gemini: Server Actions only. Claude: tRPC v11. No consensus. Must decide API architecture before any implementation. |
| D-02 | **Data access layer / ORM** | Prisma 7.x (Claude) | Drizzle or Prisma (Gemini) | **Blocking** | ChatGPT and Parallel are silent on ORM. Gemini recommends Drizzle/Prisma. Claude recommends Prisma 7.x. Nobody recommends Dapper. The existing constraint (#2) specifies Dapper — zero sources support it. Must decide: keep Dapper, adopt an ORM, or find a middle path. |
| D-03 | **Business rules engine** | json-rules-engine (Gemini, Claude) | "Policy model" / JsonLogic (ChatGPT, Parallel) | **Significant** | Broad consensus on externalizing business rules from UI code. No consensus on the specific tool. json-rules-engine has the strongest case (2 sources, documented library, JSON-stored rules). JsonLogic is only a placeholder mention. ChatGPT's "policy model" is conceptual, not a concrete recommendation. |
| D-04 | **Role of LLMs in AI pipeline** | Azure OpenAI for structured outputs + confidence-tiered workflow (ChatGPT) | Document Intelligence only; LLMs "far inferior" for structured extraction (Gemini) | **Significant** | ChatGPT is the strongest LLM advocate. Gemini explicitly rejects LLMs for structured form extraction. Claude and Parallel include Azure OpenAI as optional. The resolution depends on use case: OCR from scanned forms (Document Intelligence wins) vs. NL-to-structured mapping (LLMs may add value). |
| D-05 | **Dynamic form complexity scope** | Field registry / form runtime as middle path (ChatGPT) | Full metadata-driven / schema-driven engine (Parallel, Gemini, Claude) | **Significant** | ChatGPT recommends a lighter "field registry + form runtime" that stops short of full metadata-driven rendering. Parallel, Gemini, and Claude describe fuller schema-driven engines (though all agree it's Complex tier only). Gemini explicitly warns against "form engine" Turing-complete drift. The resolution determines scope of the Complex tier. |
| D-06 | **Audit strategy depth** | Three-layer: temporal + app events + Azure SQL Auditing (ChatGPT) | Temporal tables alone sufficient (Gemini, Claude) | **Minor** | ChatGPT's three-layer strategy is more comprehensive but adds operational complexity. Parallel adds CDC as complement. Gemini and Claude treat temporal tables as sufficient. For a QMS with regulatory audit requirements, the three-layer approach may be warranted. |
| D-07 | **Server Actions vs. separate API** | Server Actions bypass API layer entirely (Parallel, Gemini) | Separate API layer exists (ChatGPT Route Handlers, Claude tRPC) | **Blocking** | Parallel and Gemini assume Server Actions talk directly to the database. ChatGPT and Claude maintain a separate API layer. This is a fundamental architectural decision: does the API layer exist as a separate concern, or does Next.js Server Actions absorb it? Directly related to Constraints #1 and #2. |
| D-08 | **Zod version** | Zod 4.3.6 (ChatGPT) | Zod 3.24 / 3.x (Gemini, Claude) | **Minor** | ChatGPT references Zod 4.x; others reference 3.x. Zod 4 may not be GA or widely adopted yet. Verify current stable version. Functionally equivalent for this architecture. |

---

## Challenges to Existing Constraints

For each Pattern_Mapping.md non-negotiable constraint, whether the research confirms, challenges, or is silent on it.

### Constraint #1: Business logic stays in T-SQL (no C# domain service layer)

| Aspect | Detail |
|---|---|
| **Constraint** | Business logic stays in T-SQL (no C# domain service layer) |
| **Research Position** | **CHALLENGED — unanimously and fundamentally.** |
| **Sources** | 4/4 challenge. Zero sources mention T-SQL for business logic. |
| **Evidence** | ChatGPT: business policy evaluation in the API layer (TypeScript). Parallel: Zod validation + JsonLogic in Server Actions. Gemini: json-rules-engine in Node.js, explicitly ignores T-SQL. Claude: json-rules-engine + Zod .input() in tRPC, all TypeScript. Every source places form validation, conditional logic, and business rules in TypeScript/Node.js. None recommend stored procedures for form business logic. |
| **Impact** | **Blocking.** |
| **Recommendation** | This constraint was designed for a C#/Dapper backend where T-SQL was the natural place for business logic. In a Next.js/TypeScript stack, T-SQL business logic means: (a) Zod schemas cannot be shared (server validation must call a stored procedure), (b) business rules cannot run on the client (no conditional field visibility without a server round-trip), (c) json-rules-engine or any rules engine is ruled out. The constraint may need revision for the forms domain specifically — perhaps scoped to: "data integrity rules stay in T-SQL (constraints, triggers, computed columns); form business logic (validation, conditional visibility, workflow routing) lives in TypeScript." |

### Constraint #2: API layer stays thin (Dapper, not Entity Framework)

| Aspect | Detail |
|---|---|
| **Constraint** | API layer stays thin (Dapper, not Entity Framework) |
| **Research Position** | **CHALLENGED — by 3/4 sources; ignored by 1.** |
| **Sources** | Gemini: recommends Drizzle/Prisma. Claude: recommends Prisma 7.x + tRPC. Parallel: assumes Server Actions bypass API entirely. ChatGPT: does not mention Dapper or ORM. |
| **Evidence** | No source recommends Dapper. No source recommends a "thin" API layer. Claude explicitly recommends Prisma 7.x (a full ORM with query engine, migrations, and connection pooling). Gemini recommends Drizzle or Prisma. Parallel bypasses the API layer concept entirely with Server Actions direct to SQL. ChatGPT recommends Route Handlers as BFF but does not discuss data access. |
| **Impact** | **Blocking.** |
| **Recommendation** | The constraint was designed for a C#/Dapper backend where "thin API" meant "no heavy ORM like Entity Framework." In the TypeScript world, the equivalent spectrum is: raw SQL queries → query builder (e.g., Kysely) → lightweight ORM (Drizzle) → full ORM (Prisma). The "thin" principle may still apply: use a lightweight query builder or Drizzle rather than Prisma. But Dapper specifically is a .NET library and does not exist in the TypeScript ecosystem. The constraint needs translation, not just confirmation or rejection. |

### Constraint #3: Single-tenant system

| Aspect | Detail |
|---|---|
| **Constraint** | Single-tenant system |
| **Research Position** | **UNCHALLENGED.** |
| **Sources** | 0/4 discuss multi-tenancy. |
| **Evidence** | No source recommends or mentions multi-tenancy. All architectures assume a single-tenant deployment. Parallel mentions Row-Level Security but for data isolation within a single tenant (role-based), not multi-tenancy. |
| **Impact** | None. |
| **Recommendation** | Constraint holds. No revision needed. |

### Constraint #4: Azure App Service deployment (no message brokers/orchestration)

| Aspect | Detail |
|---|---|
| **Constraint** | Azure App Service deployment (no message brokers/orchestration) |
| **Research Position** | **PARTIALLY CHALLENGED.** |
| **Sources** | 3/4 recommend Azure Functions for async processing. |
| **Evidence** | ChatGPT: Azure Functions 4.x for OCR, AI enrichment, scheduled jobs. Parallel: Functions + Queue + Blob for Document Intelligence pipeline. Claude: Azure Functions (Durable) + Blob for async OCR. Gemini: does not mention Functions. All sources keep the main application on App Service. The challenge is specifically for async AI/OCR pipelines that need background processing. |
| **Impact** | **Significant.** |
| **Recommendation** | The constraint's intent (keep deployment simple, no Kafka/RabbitMQ/Service Bus) is not challenged. The research recommends Azure Functions specifically for Document Intelligence OCR pipelines, which are event-driven and well-suited to Functions consumption plan. This is a scoped exception, not a constraint revision: "App Service for the main application; Azure Functions for async AI/OCR pipelines only." Queue Storage (not Service Bus) as the trigger mechanism keeps it simple. |

### Constraint #5: Quality domain data model is well-defined (no EAV/configurable schema)

| Aspect | Detail |
|---|---|
| **Constraint** | Quality domain data model is well-defined (no EAV/configurable schema) |
| **Research Position** | **CHALLENGED — unanimously, but with nuance.** |
| **Sources** | 4/4 recommend hybrid relational + JSON columns for form data. |
| **Evidence** | All 4 sources independently arrive at: typed relational columns for stable/queryable fields + JSON columns for variable/evolving form payloads. ChatGPT: "canonical submission payload as JSON + projected columns." Parallel: native JSON type for evolving payloads. Gemini: JSON for evolving form schemas. Claude: variable form field data in JSON column. None recommend pure EAV. None recommend fully configurable schemas. All recommend a bounded hybrid. |
| **Impact** | **Blocking.** |
| **Recommendation** | The key adjudication question is whether JSON columns for variable form data constitute a "configurable schema" violation. Arguments for "scoped exception, not violation": (1) Core quality event entities (NCRs, CAPAs, 8Ds, SCARs) keep fully typed relational schemas. (2) JSON columns are used ONLY for genuinely variable inspection checklist data that varies by product/machine/line. (3) The JSON content is still validated by Zod schemas — it is not untyped. (4) No end-user can define arbitrary schemas — form definitions are developer-controlled or admin-controlled with constraints. Arguments for "this IS a constraint violation": (1) Storing data in a JSON column means the database schema does not fully describe the data shape. (2) Reporting and querying require JSON functions rather than simple column references. (3) It opens a path toward runtime-configurable schemas that the constraint was designed to prevent. The resolution likely involves a scoped exception with guardrails: "JSON columns are permitted for inspection checklist variable data only, with mandatory Zod schema validation and computed column indexes for reporting fields." |

---

## Challenges to Quality_Forms_Module Design

The existing inspection template design (typed-per-entity schema with 30 migrations, 29 SPs, 29 endpoints) is evaluated against research recommendations.

| Design Aspect | Current Approach | Research Alternative | Sources | Trade-off |
|---|---|---|---|---|
| **Data model** | Typed relational tables per entity (inspection templates have dedicated columns per field) | Hybrid: relational metadata columns + JSON column for variable inspection fields | 4/4 | Current approach is more agent-friendly and query-friendly. Research approach handles variability better. Trade-off depends on how much inspection checklists actually vary across products/machines. If variation is low, typed tables win. If variation is high (dozens of checklist variants), JSON wins. |
| **Stored procedures** | 29 SPs for CRUD operations on inspection templates | Server Actions / tRPC / Route Handlers calling ORM or query builder | 4/4 | Current approach keeps logic close to data (performance, transaction safety). Research approach enables shared Zod validation and TypeScript business rules. The 29 SPs represent significant existing investment that would be discarded. |
| **API endpoints** | 29 dedicated endpoints (thin, one-to-one with SPs) | Fewer, more general endpoints; or Server Actions eliminating the endpoint concept | 4/4 | Current approach is explicit and traceable. Research approach reduces boilerplate. Neither is wrong — this is a style decision driven by the API layer choice (D-01). |
| **Validation** | Server-side only (in SPs or API layer) | Shared Zod schemas: client courtesy + server authoritative | 4/4 | Research approach unanimously preferred. Shared Zod schemas eliminate validation drift and improve UX. This is compatible with the current design — Zod schemas can coexist with SP validation as a transition path. |
| **Business rules** | Hardcoded in application/SP logic | Externalized json-rules-engine with database-stored JSON rules | 2/4 (Gemini, Claude) | Research approach enables rule changes without deployments. Current approach is simpler if rules rarely change. For inspection templates specifically, conditional required fields and visibility logic are common enough to justify externalization. |
| **Audit trail** | Application-level logging | Azure SQL Temporal Tables (automatic, database-level) | 4/4 | Research approach unanimously preferred. Temporal tables provide immutable, circumvention-proof audit with zero application code. This is additive — can be applied to existing tables without changing application logic. |
| **Form variability** | One schema per inspection type (typed) | Schema-driven rendering from JSON definitions for variable inspections | 3/4 (Parallel, Gemini, Claude) | The fundamental question: do inspection checklists vary enough across products/machines to justify schema-driven rendering? If yes, the current typed-per-entity approach requires a new migration + SP + endpoint for each variant — this does not scale. If no, the current approach is simpler and more agent-friendly. |
| **Effort model** | 30 migrations, 29 SPs, 29 endpoints = high per-entity cost, high agent-readiness per instance | Fewer artifacts per form type, but higher infrastructure cost (renderer, rules engine, schema management) | 4/4 | Current: O(n) effort per form type, each highly automatable. Research: O(1) infrastructure investment + O(small) per form definition. Crossover point depends on how many form types exist. With <10 types, current approach may win. With >20 types, research approach wins. |

---

## Summary: What Must Be Resolved Before Implementation

### Blocking (cannot proceed without decision)

1. **API pattern and data access layer** (D-01, D-02, D-07): Choose between Route Handlers / Server Actions / tRPC, and between Dapper (constraint) / query builder / ORM. This is the foundational architectural decision.

2. **Constraint #1 revision**: Decide whether form business logic (validation, conditional visibility, workflow routing) moves to TypeScript, while data integrity rules (constraints, triggers) stay in T-SQL. All 4 sources assume TypeScript business logic.

3. **Constraint #2 translation**: Translate "Dapper, not EF" into the TypeScript ecosystem. Options: raw SQL queries, Kysely (query builder), Drizzle (lightweight ORM), Prisma (full ORM). The "thin" principle may be preserved with Drizzle or Kysely.

4. **Constraint #5 scoping**: Decide whether hybrid relational + JSON columns are permitted for inspection checklist variable data (scoped exception) or whether all form data must be fully typed relational (constraint holds). All 4 sources recommend the hybrid approach.

5. **Quality_Forms_Module design fate**: Does the existing typed-per-entity design (30 migrations, 29 SPs, 29 endpoints) hold for core quality events, get modified to include JSON for variable data, or get replaced by schema-driven rendering?

### Significant (affects approach, not direction)

6. **Business rules engine selection**: json-rules-engine vs. alternatives. Gemini and Claude provide the strongest case.

7. **LLM role in AI pipeline**: Core component (ChatGPT position) vs. OCR-only (Gemini position). Determines whether Azure OpenAI is in scope.

8. **Dynamic form scope**: Field registry (lighter, ChatGPT) vs. full schema-driven engine (heavier, Gemini/Claude). Affects Complex tier implementation.

9. **Audit depth**: Three-layer strategy (ChatGPT) vs. temporal tables alone. Affects infrastructure complexity.

10. **Azure Functions for async pipelines**: Scoped exception to Constraint #4 for AI/OCR processing.
