# Section A — Technology Comparison Matrix

| Name & version | Category (frontend library / backend framework / database approach / validation tool / AI service) | Maturity level | Azure stack compatibility (Native / Good / Limited) | Learning curve (Low / Medium / High) | Best suited for (specific use case) | Key limitation | Source URL |
|---|---|---|---|---|---|---|---|
| React Hook Form 7.71.2 | Frontend library | Production-ready | Good | Medium | High-performance “business forms” in React with large field counts, nested arrays, and complex validation UX | Not schema-first; dynamic schema-driven forms need additional architecture (field registry + renderer + metadata/rules model) | https://www.npmjs.com/package/react-hook-form citeturn0search0 |
| Zod 4.3.6 | Validation tool | Production-ready | Good | Medium | Shared, type-inferred validation schemas (client courtesy + server authoritative), plus schema reuse for OpenAPI/JSON Schema generation | Zod is great for validation, but it isn’t a full rules engine; complex “policy” logic still needs a rules layer | https://www.npmjs.com/package/zod citeturn0search1 |
| @hookform/resolvers 5.2.2 | Validation tool | Production-ready | Good | Low | Wiring Zod (and other validators) into React Hook Form cleanly, with consistent error mapping | Tight coupling at the “resolver boundary” means you must standardize error formats and coercion rules across client/server to avoid drift | https://www.npmjs.com/package/@hookform/resolvers citeturn7search0 |
| JSON Forms 3.7.0 | Frontend library | Production-ready | Good | High | Large catalogs of forms that must be generated from JSON Schema + UI schema (dynamic forms, configurable layouts, rapid change) across React/Angular/Vue | Renderer customization cost is real; matching shadcn/ui look-and-feel typically requires building custom renderers and UI schema conventions | https://www.npmjs.com/%40jsonforms/core citeturn0search14 |
| Angular 21 Reactive Forms | Frontend library | Production-ready | Good | High | Highly structured enterprise UIs where Angular is already standard; strong reactive patterns and form model control | Doesn’t integrate with your React/Next.js stack without running a separate frontend codebase and UI system | https://angular.dev/guide/forms/reactive-forms citeturn13search3 |
| @ngx-formly/core 7.1.0 | Frontend library | Production-ready | Good | Medium | JSON-powered dynamic forms in Angular (metadata-driven patterns similar to enterprise platforms) | Angular-only; also introduces another “form schema dialect” you must govern to prevent untestable sprawl | https://github.com/ngx-formly/ngx-formly/releases citeturn20view5 |
| Vue 3.5.28 | Frontend library | Production-ready | Good | High | Vue-based business apps (if your org has Vue talent) with modern component composition | Switching ecosystems is a full strategic decision (components, patterns, tooling, hiring), not “just a library swap” | https://vuejs.org/about/releases citeturn17search2 |
| FormKit (@formkit/vue) 1.7.2 | Frontend library | Production-ready | Good | Medium | Vue form building with a cohesive form framework (generation + validation + theming + structure) | Vue-only; your existing React Hook Form + Zod investment doesn’t transfer directly | https://npmjs.com/package/%40formkit/vue citeturn1search1 |
| ASP.NET Core Blazor (.NET 10) EditForm & validation | Frontend library | Production-ready | Native | High | .NET-centric enterprises building internal line-of-business apps with C# end-to-end, including forms and validation patterns | Not aligned with your current Next.js + React stack; using it would materially increase platform surface area | https://learn.microsoft.com/en-us/aspnet/core/blazor/forms/validation?view=aspnetcore-10.0 citeturn13search0 |
| MudBlazor 9.0.0 | Frontend library | Production-ready | Native | Medium | Blazor apps that need a mature component library (including inputs/forms) with consistent UX | Material-style UI defaults may not match your shadcn/Radix conventions; plus it’s irrelevant unless you adopt Blazor | https://www.nuget.org/packages/MudBlazor citeturn18view0 |
| NestJS 11.1.14 | Backend framework | Production-ready | Good | Medium | Structured Node/TypeScript backend (controllers, DI, modules) when Next.js route handlers start getting too crowded | More framework weight than “plain route handlers”; you pay for architecture (worth it only if complexity justifies it) | https://github.com/nestjs/nest/releases citeturn20view0 |
| ts-rest 3.52.1 | Backend framework | Production-ready | Good | Medium | Contract-first REST APIs with shared types/validation across client and server (works well with Zod + OpenAPI generation) | Contract discipline required; if teams bypass it, you end up with “two API styles” and type drift | https://www.npmjs.com/package/@ts-rest/core citeturn4search2 |
| Apollo Server 5.4.0 | Backend framework | Production-ready | Good | High | GraphQL for client-driven data fetching when UIs need flexible queries across many resources | GraphQL adds governance overhead (schema lifecycle, authorization per field, query cost controls) and can be overkill for CRUD-heavy internal apps | https://www.npmjs.com/package/@apollo/server citeturn4search3 |
| Azure SQL Database system-versioned temporal tables (SQL Server 2016+) | Database approach | Production-ready | Native | Medium | Auditability + revision history for business records (including form definitions and form submissions), with point-in-time queries | History growth is real; you must plan retention, indexing, and “who changed what” reporting outside the raw history rows | https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables?view=sql-server-ver17 citeturn21view4 |
| Azure SQL JSON features (OPENJSON/ISJSON/etc.) | Database approach | Production-ready | Native | Medium | Hybrid “relational + JSON” storage for form submissions whose structure evolves (store canonical JSON; project key fields for reporting) | JSON is flexible but not free: indexing strategy, validation constraints, and reporting pipelines must be designed deliberately | https://learn.microsoft.com/en-us/azure/azure-sql/database/json-features?view=azuresql citeturn21view5 |
| Auditing for Azure SQL Database | Database approach | Production-ready | Native | Medium | Compliance-grade database event auditing to Storage / Log Analytics / Event Hubs for investigation and anomaly review | It prioritizes DB availability and may not record all audited events under very high activity or network load—so it cannot be your *only* audit trail | https://learn.microsoft.com/en-us/azure/azure-sql/database/auditing-overview?view=azuresql citeturn20view7 |
| Azure AI Document Intelligence (v4.0) | AI service | Production-ready | Native | Medium | OCR + document understanding for upload-to-form workflows (invoices, packing slips, inspections, compliance documents) using REST/SDKs | Extraction confidence varies by document quality; you need a human-review loop for low-confidence fields and strong monitoring/feedback | https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0 citeturn20view8 |
| Azure OpenAI structured outputs (JSON Schema) | AI service | Production-ready | Native | Medium | LLM-assisted “map unstructured text → your form schema” with strict JSON Schema adherence (safer than free-form JSON) | Still needs guardrails: schema adherence ≠ factual correctness; you must enforce server-side validation and apply human review for critical fields | https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/structured-outputs?view=foundry-classic citeturn20view9 |
| Azure Functions Runtime 4.x (Node.js 22 GA supported) | Backend framework | Production-ready | Native | Medium | Async workloads: OCR extraction jobs, AI enrichment, scheduled data quality checks, webhooks, background validation/reprocessing | Cold starts and dependency size can hurt; functions are best for event-driven processing, not your main “transaction API” | https://learn.microsoft.com/en-us/azure/azure-functions/functions-versions citeturn19search0 |

Top 5 production-ready, code-first form options for complex enterprise forms (compared to the baseline React Hook Form + Zod) are: **React Hook Form + Zod** (baseline), **JSON Forms**, **Angular Reactive Forms**, **@ngx-formly/core**, and **Blazor EditForm**. The blunt reality is that none of the non-React options are “drop-in” improvements for your environment—they only make sense if you’re willing to run a second frontend stack (Angular/Vue/Blazor) or you have a strong strategic reason (existing talent, corporate standardization, acquisition, etc.). citeturn0search0turn0search1turn13search3turn20view5turn13search0

JSON-schema-driven frameworks (notably JSON Forms) win when you have *many* forms, frequent change, and you need centralized governance over field types and layouts. You trade away some UI component freedom and pay an upfront renderer customization cost—especially if you want tight alignment to shadcn/ui + Radix primitives rather than “generic” renderers. citeturn0search18turn0search14

Angular and Blazor form stacks are mature, but for your current Next.js 15 + React 19 environment, their “advantages” mostly convert into organizational costs: duplicated UI component systems, duplicated validation stacks, duplicated build/deploy pipelines, and harder hiring/onboarding. In other words: technically solid, strategically expensive. citeturn13search3turn13search0

# Section B — Recommended Architecture

1. **Diagram description — component layers and data flow**

A user opens a form page in the Next.js App Router UI (server-rendered shell + client form runtime). The client runtime fetches a **Form Definition** (schema + UI schema + policy rules + version) and optionally a **Draft Submission**. The user edits fields using a field registry (shadcn/ui-based inputs), with **client-side courtesy validation** via React Hook Form + Zod. On save/submit, the client calls a backend **Form Submission API** (your BFF) over HTTPS, sending the form version and payload.

The API performs **authoritative validation** (Zod + business policy evaluation) and writes with a transaction to Azure SQL: (a) the current submission row, (b) history via temporal tables, and (c) an append-only domain audit event. Azure SQL Auditing streams database-level events to Log Analytics/Event Hubs/Storage for compliance visibility. citeturn21view4turn20view7

For AI-assisted entry, the user uploads a document (scan/photo/PDF). The API stores the file in Blob Storage and enqueues a message; an Azure Function consumes the queue and calls Document Intelligence to extract text/fields/tables and returns extraction results + confidence. Optionally, the Function calls Azure OpenAI structured outputs to map extracted text into your target JSON Schema, producing a “suggested form payload” that is stored as a draft suggestion and presented back to the user for review before submission. citeturn19search6turn20view8turn20view9turn19search0

Authentication is handled by App Service built-in authentication (“Easy Auth”) against Entra ID; the API trusts only validated identity headers/tokens and enforces authorization (roles/groups) per form and per operation. App telemetry (frontend/server/API/functions) goes to Application Insights with correlation IDs passed through requests. citeturn2search2turn12search4

2. **Primary stack — named technologies by layer with rationale**

**Frontend forms**: Next.js 15 (App Router) + React 19 + TypeScript strict, using React Hook Form 7.71.2 and shadcn/ui components. This is the right baseline because it is performant at scale and aligns with your existing component primitives, so you keep one UI system and one mental model. The key architectural add-on is a **field registry + form runtime** so you can handle “complex” and “dynamic” form definitions without devolving into one-off forms. citeturn0search0

**Validation**: Zod 4.3.6 as the single schema source, shared between client and server for consistent parsing and type inference. Client validation exists for UX, but the server re-validates everything (including conditional rules and async checks) to remain authoritative. If you need validator portability later, Standard Schema is emerging as a cross-library interface, but you can adopt it incrementally without abandoning Zod. citeturn0search1turn8search0turn8search2

**API layer**: Next.js Route Handlers (BFF style) for the main transactional form API, plus Azure Functions 4.x for async/long-running work (OCR/extraction, enrichment, scheduled data quality jobs). This split is pragmatic: you keep your latency-sensitive writes close to the app, and push variable-duration tasks to event-driven compute. If/when your API grows beyond a clean BFF, migrate the API layer to NestJS 11.x (same language, clearer modularity) rather than adding a second backend ecosystem prematurely. citeturn19search0turn19search1turn20view0

**Database / persistence**: Azure SQL as the system of record, using a **hybrid relational + JSON** storage model for evolving form payloads. Store the canonical submission payload as JSON (for forward compatibility) and project a small set of high-value fields into relational columns (for reporting, joins, constraints, and indexing). Use Azure SQL JSON functions (ISJSON/OPENJSON/etc.) and constraints to keep payloads well-formed, and add indexes on projected fields (or computed columns) for the queries you actually run. citeturn21view5turn5search4turn15search0turn15search4

**Audit trails and revision control**: Use **system-versioned temporal tables** for FormDefinitionVersion and FormSubmission tables so every change produces an automatic history row you can query “as of time.” Add **application-level audit events** (append-only, business-context rich, includes who/why/correlation ID) because temporal history is structural change tracking—not a complete business audit narrative. Enable **Azure SQL Auditing** to externalize database event logs for compliance review, but treat it as supplementary because it may allow transactions to proceed without recording all audited events under extreme conditions. citeturn21view4turn20view7

**Authentication / authorization**: Entra ID via App Service built-in authentication (Easy Auth). This is the cleanest fit for your App Service hosting because it centralizes sign-in and token handling at the platform edge, and your app focuses on authorization decisions (roles/groups, form-level permissions, record-level security). Use managed identity for downstream Azure resources wherever possible (SQL, Key Vault, Storage) to avoid password/secrets sprawl. citeturn2search2turn11search6turn11search4turn11search2

**Azure AI services**: Azure Document Intelligence for extraction (OCR + tables + key-value pairs + custom models) and Azure OpenAI structured outputs for schema-constrained mapping and data quality checks. In production, make the workflow confidence-aware: auto-fill high-confidence fields, flag low-confidence fields, and require user attestation for critical fields (e.g., safety incidents, QA holds). citeturn20view8turn9search6turn20view9

3. **Alternative stack — one complete alternative with explicit trade-offs**

**Alternative**: Keep the same Next.js frontend, but build the backend as **ASP.NET Core 10 minimal APIs** with either REST + OpenAPI (first-class tooling) or GraphQL (Hot Chocolate), using FluentValidation for business validation and a .NET-based rules engine where appropriate, still persisting to Azure SQL with temporal tables/auditing. citeturn17search5turn13search0turn6search1turn7search3turn21view4turn20view7

**What you gain**: A very mature enterprise backend ecosystem (profiling, auth middleware patterns, long-lived governance norms) and strong developer tooling around OpenAPI and production diagnostics. You also gain access to .NET-native validation and rule frameworks that many enterprise teams already understand. citeturn17search5turn16search3

**What you lose**: The simplicity of having one primary language/runtime across the stack. In a 200-person company, that matters: two backend stacks tends to create “two standards,” duplicated deployment skills, and slower iteration unless you already have deep .NET strength. You also add operational surface area without necessarily improving form UX, because your frontend still needs the same schema/policy/runtime architecture. citeturn13search0turn2search2

# Section C — Pattern Deep Dives

**Pattern name: Metadata-driven schema forms (Schema + UI schema + versioning)**

This pattern treats each form as **data**: a versioned definition containing a schema (field types, requiredness, constraints), a UI schema (layout, grouping, stepper structure), and optional policies/rules. The runtime renders forms from those definitions rather than hardcoding each form in React components. In enterprise software, this is dominant when form catalogs grow large and the business demands frequent changes without rewriting UI code—because it turns “build a new form” into “publish a new versioned definition.” citeturn0search18turn21view0

**When to use vs. when to avoid**: Use it when you have (a) many forms, (b) frequent changes, (c) a need for version-aware history (“what did the user see when they submitted?”), and (d) governance requirements (approved field types, consistent labels, consistent validation semantics). Avoid it when you have only a handful of forms that rarely change, or where UI interaction is highly bespoke (complex canvases, non-standard widgets) because the schema abstraction becomes friction and you’ll end up “escaping” into custom code constantly. citeturn0search18turn21view4

**Real-world example**: The entity["company","Salesforce","crm company"] platform explicitly describes metadata-driven design as a core architectural principle, where applications are collections of metadata that control behavior and user experience. citeturn21view0

**Implementation complexity estimate (2–3 developers)**  
Total: **24–40 person-weeks**, typically broken into:
- **Form definition model + storage (versioning, publish workflow, migrations)**: 6–10 person-weeks
- **Renderer runtime (field registry, layout engine, repeatable sections, accessibility)**: 8–14 person-weeks
- **Policy/rule hooks (visibility/requiredness/state transitions; server parity)**: 4–8 person-weeks
- **Admin tooling MVP (create/edit/publish definitions; diff/rollback)**: 4–6 person-weeks
- **Hardening (tests, performance, telemetry, upgrade strategy)**: 2–4 person-weeks

**Pattern name: Policy-driven conditional logic (client guidance + server authority)**

This pattern separates “what should happen” (policies) from “how the UI is built” (components). Policies can define when fields become required, visible, read-only, or auto-populated based on other values, and the same policy model is enforced server-side for correctness. In enterprise environments, this is dominant because “conditional business logic” changes constantly—and if it’s embedded as scattered `if` statements across UI components, it becomes untestable and risky to change. citeturn21view1

**When to use vs. when to avoid**: Use it when conditionality is pervasive (e.g., compliance workflows, safety forms, QA nonconformance, maintenance procedures) and when policy changes must be audited and versioned. Avoid it if conditional logic is minimal, or if every rule is truly domain-code-level and must be expressed as deterministic code (in which case, keep rules in code but still centralize them). citeturn21view1turn20view7

**Real-world example**: entity["company","ServiceNow","it service mgmt company"] UI policies dynamically change form behavior (mandatory, read-only, hide/show) and are positioned as a performant way to implement form behavior rules. citeturn21view1

**Implementation complexity estimate (2–3 developers)**  
Total: **12–22 person-weeks**, typically broken into:
- **Policy model design (operators, precedence, execution order, safe expression language)**: 3–5 person-weeks
- **Client runtime integration (reactive evaluation, dependency graph, UX messaging)**: 4–7 person-weeks
- **Server enforcement (authoritative evaluation + error format + audit hooks)**: 3–6 person-weeks
- **Policy authoring UI + testing harness (playground, fixtures, regression tests)**: 2–4 person-weeks

**Pattern name: Versioned records with built-in history (temporal tables + application audit events)**

This pattern combines database-managed row history with app-managed audit narratives. Temporal tables provide automatic “previous row versions” for point-in-time recovery and investigation, while the application emits append-only audit events that capture business meaning (who submitted, who approved, why it was rejected, which policy triggered). In regulated enterprises, this is dominant because it provides both forensic traceability (history rows) and operational traceability (business audit events). citeturn21view4turn20view7

**When to use vs. when to avoid**: Use it when audit and revision history are requirements (not “nice-to-have”), when form definitions evolve over time, and when you need to reproduce historical truth (“what was the record on Jan 3?”). Avoid relying on temporal tables alone when you need workflow-level audit (approvals, attestations, reason codes), because temporal history doesn’t capture “why”—it captures “what changed.” citeturn21view4turn20view7

**Real-world example**: entity["company","Microsoft","technology company"] documents system-versioned temporal tables as keeping a full history of data changes and enabling point-in-time analysis, and Azure SQL Auditing as emitting database event logs to Storage/Log Analytics/Event Hubs (with performance-focused caveats). citeturn21view4turn20view7

**Implementation complexity estimate (2–3 developers)**  
Total: **14–26 person-weeks**, typically broken into:
- **Schema & migration work (temporal tables, retention/indexing strategy, diffs)**: 5–8 person-weeks
- **Audit event model (event types, correlation IDs, PII policy, storage)**: 3–6 person-weeks
- **Authorization + identity attribution (who/what/when, Entra ID claims mapping)**: 2–4 person-weeks
- **Reporting & investigation UX (timeline views, “as-of” views, export)**: 3–6 person-weeks
- **Compliance hardening (log retention, monitoring, incident playbooks)**: 1–2 person-weeks

# Section D — Build Approach Decision Matrix

| Form complexity tier | Recommended architecture pattern | Estimated build effort (person-weeks) | Key technical risks (2–3) | Integration points with Azure App Service / Azure SQL / Entra ID (specific services/features) |
|---|---|---|---|---|
| Simple (single-step, flat data) | Component-first forms (RHF + Zod) with thin API and standard relational tables | **3–6** | Validation drift if server re-validation is skipped; authorization gaps if API trusts client state; weak audit narrative if you only log “updated row” | App Service Easy Auth for sign-in and protected routes citeturn2search2; Azure SQL basic tables + optional lightweight auditing citeturn12search5; Application Insights for request tracing and exceptions citeturn12search4 |
| Moderate (multi-step, conditional logic, relational data) | Policy-driven conditional logic + persisted drafts + hybrid relational/JSON payload model | **10–20** | Rule precedence bugs (conflicting conditions); draft/resume consistency (partial data, step gating); reporting pain if JSON payload isn’t projected/indexed intentionally | Azure SQL JSON functions to validate and transform payloads (ISJSON/OPENJSON) citeturn21view5; temporal tables for submission history “as-of” views citeturn21view4; App Service Easy Auth with group/role-based authorization; Azure Functions (optional) for async validations/enrichment citeturn19search0 |
| Complex (dynamic schema, revision-controlled, audit-trailed) | Metadata-driven schema forms (schema + UI schema + versioning) + temporal history + externalized auditing | **24–45** | Schema versioning mistakes (breaking old submissions, inability to reproduce historical UI); governance overhead (uncontrolled schema sprawl); audit gaps if you rely only on DB auditing under load | Temporal tables for full row history across form definitions and submissions citeturn21view4; Azure SQL Auditing to Storage/Log Analytics/Event Hubs (supplementary evidence stream) citeturn20view7; Entra ID via Easy Auth for identity and protected access citeturn2search2; Document Intelligence + Azure Functions for document-driven data entry pipelines citeturn20view8turn19search0; Azure OpenAI structured outputs for schema-constrained AI assistance citeturn20view9 |

# Section E — Key Sources

1. **Authentication and Authorization — Azure App Service (Easy Auth)**  
URL: https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization  
Publication date: Nov 4, 2025  
Why authoritative: Official platform documentation describing App Service built-in authentication/authorization behavior and configuration expectations. citeturn2search2

2. **Temporal Tables — SQL Server (applies to Azure SQL Database)**  
URL: https://learn.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables?view=sql-server-ver17  
Publication date: Nov 18, 2025  
Why authoritative: Canonical documentation for system-versioned temporal tables, including how full history is captured and queried for point-in-time analysis. citeturn21view4

3. **Auditing for Azure SQL Database and Azure Synapse Analytics**  
URL: https://learn.microsoft.com/en-us/azure/azure-sql/database/auditing-overview?view=azuresql  
Publication date: Jan 21, 2026  
Why authoritative: Official Azure SQL auditing guidance covering supported sinks (Storage/Log Analytics/Event Hubs) and operational caveats under load. citeturn12search5turn20view7

4. **Work with JSON Data — Azure SQL Database & Azure SQL Managed Instance**  
URL: https://learn.microsoft.com/en-us/azure/azure-sql/database/json-features?view=azuresql  
Publication date: Jul 24, 2025  
Why authoritative: Microsoft’s official reference for JSON constraints/functions (ISJSON/OPENJSON/etc.) used to implement hybrid relational/JSON persistence in Azure SQL. citeturn5search0turn21view5

5. **What is Azure Document Intelligence in Foundry Tools?**  
URL: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0  
Publication date: Accessed Feb 26, 2026  
Why authoritative: Official service overview describing extraction capabilities (OCR, tables, key/value pairs) and custom model support for production document workflows. citeturn20view8

6. **How to use structured outputs with Azure OpenAI (JSON Schema)**  
URL: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/structured-outputs?view=foundry-classic  
Publication date: Accessed Feb 26, 2026  
Why authoritative: Official guidance explaining schema-constrained model outputs for reliable extraction and workflow automation using JSON Schema. citeturn20view9

7. **Best practices for RESTful web API design — Azure Architecture Center**  
URL: https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design  
Publication date: Accessed Feb 26, 2026  
Why authoritative: Microsoft’s architecture guidance on REST principles (loose coupling, platform independence), which directly informs API design trade-offs in enterprise systems. citeturn21view3

8. **Support for GraphQL APIs — Azure API Management**  
URL: https://learn.microsoft.com/en-us/azure/api-management/graphql-apis-overview  
Publication date: Sep 30, 2025  
Why authoritative: Microsoft’s practical explanation of GraphQL vs REST goals and how GraphQL is operationalized and governed in Azure API ecosystems. citeturn6search13turn21view2

9. **The Salesforce Platform — metadata-driven design principle**  
URL: https://architect.salesforce.com/docs/architect/fundamentals/guide/platform-transformation  
Publication date: Accessed Feb 26, 2026  
Why authoritative: First-party architecture guidance from entity["company","Salesforce","crm company"] explicitly describing metadata-driven design as a core principle—directly relevant to enterprise dynamic form architecture. citeturn21view0

10. **Using UI policies — dynamic form behavior rules**  
URL: https://www.servicenow.com/docs/r/platform-administration/t_CreateAUIPolicy.html  
Publication date: Updated July 31, 2025  
Why authoritative: First-party documentation from entity["company","ServiceNow","it service mgmt company"] describing declarative policy-based control of form behavior, a common enterprise pattern for conditional logic. citeturn21view1