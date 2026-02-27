# A — Technology Comparison (Cross-Source Master Matrix)

**Generated:** 2026-02-26
**Inputs:** 4 extraction files (ChatGPT, Parallel, Gemini, Claude)

---

## Stack-Relevant Technologies

Technologies that fit the current Next.js 15 / React 19 / TypeScript / Azure SQL / Azure App Service stack.

| Technology | Category | ChatGPT | Parallel | Gemini | Claude | Consensus | Recommendation Variance |
|---|---|---|---|---|---|---|---|
| **React Hook Form 7.71.x** | Frontend forms | Primary (keep) | Primary | Primary | Primary | **4/4 Unanimous** | None — all agree RHF is the baseline. |
| **Zod 3.x / 4.x** | Validation | Primary (4.3.6) | Primary | Primary (3.24) | Primary (3.x) | **4/4 Unanimous** | Minor version disagreement (3.x vs 4.x). All agree on shared client/server schemas. |
| **@hookform/resolvers (Zod)** | Validation bridge | Recommended | Implied | Implied | Implied | **4/4** | All use zodResolver; ChatGPT names the package explicitly. |
| **shadcn/ui + Radix** | UI components | Baseline (keep) | Implied | Primary | Primary | **4/4** | All assume shadcn/ui as the component library. |
| **Azure SQL Temporal Tables** | Audit/history | Recommended | Primary | Primary | Primary | **4/4 Unanimous** | None — strongest consensus in the entire comparison. |
| **Azure SQL JSON Columns** | Persistence | Recommended (hybrid) | Primary (native JSON type) | Primary (hybrid) | Primary (native JSON type) | **4/4 Unanimous** | Consensus on hybrid relational+JSON. Parallel and Claude cite native JSON type (May 2024 GA, ~18% savings). **Tensions with Constraint #5.** |
| **Azure AI Document Intelligence v4.0** | AI/OCR | Recommended | Optional | Primary | Primary | **4/4** | All recommend; Gemini most emphatic ("far superior to LLMs for structured extraction"). Claude and ChatGPT give it Primary/Recommended. Parallel marks Optional. |
| **Entra ID via Easy Auth** | Auth | Primary | Primary | Primary | Primary | **4/4 Unanimous** | None — universal agreement on platform-level auth via x-ms-client-principal. |
| **Managed Identity (secretless)** | Security | Implied | Explicit | Explicit | Explicit | **4/4** | Parallel, Gemini, and Claude explicitly recommend System-Assigned Managed Identity for all Azure connections. ChatGPT implies it. |
| **Azure Functions** | Async processing | Recommended (4.x) | Implied (for AI pipeline) | Not mentioned | Primary (Durable) | **3/4** | ChatGPT, Parallel, Claude recommend for async AI/OCR pipelines. Gemini does not mention. **Partially challenges Constraint #4** (no message brokers/orchestration). |
| **json-rules-engine 7.3.x** | Business rules | Not mentioned | Not mentioned (JsonLogic placeholder) | Primary | Primary | **2/4 Explicit** | Gemini and Claude explicitly recommend. ChatGPT recommends a "policy model" conceptually. Parallel mentions JsonLogic as placeholder. Partial consensus on externalizing rules; no consensus on specific tool. |
| **Azure OpenAI (GPT-4o)** | AI enrichment | Recommended (structured outputs) | Optional | Not mentioned | Optional | **3/4** | ChatGPT strongest advocate (confidence-tiered workflow). Parallel and Claude include as optional. Gemini omits, preferring Document Intelligence exclusively. |
| **TanStack Query** | Client caching | Implied | Explicit | Not mentioned | Implied (via tRPC) | **3/4** | Parallel most explicit. Claude uses it via tRPC integration. ChatGPT implies. |
| **TanStack Form 1.28.x** | Frontend forms (alt) | Not mentioned | Alternative | Acknowledged (premature) | Alternative | **3/4 as alternative** | Nobody recommends it as primary. Parallel and Claude list as viable alternative; Gemini acknowledges but deems premature. |
| **XState** | State machines | Not mentioned | Conditional | Implied (wizard pattern) | Not mentioned | **2/4** | Parallel recommends for complex wizards. Gemini describes wizard + logic engine pattern. |
| **tRPC 11.x** | API layer | Not mentioned | Not mentioned | Not mentioned | Primary | **1/4** | Claude-only recommendation. Strong type-safety argument but no other source mentions it. **Conflicts with Constraint #2.** |
| **Prisma 7.x** | ORM | Not mentioned | Not mentioned | Not mentioned | Primary | **1/4** | Claude-only recommendation. **Directly conflicts with Constraint #2** (Dapper, not ORM). |
| **Drizzle ORM** | ORM | Not mentioned | Not mentioned | Recommended (or Prisma) | Evaluated (lacks MSSQL) | **1/4** | Gemini recommends Drizzle or Prisma. Claude notes Drizzle lacks native MSSQL support. **Conflicts with Constraint #2.** |
| **ts-rest** | API contracts | Evaluate | Not mentioned | Not mentioned | Not mentioned | **1/4** | ChatGPT-only. Contract-first REST APIs with shared types. |
| **JSON Forms 3.7.0** | Schema-driven forms | Evaluate | Not mentioned | Not mentioned | Evaluated (incompatible) | **2/4 evaluated** | ChatGPT evaluates positively; Claude evaluates as incompatible with Zod/shadcn ecosystem. Not recommended by either. |
| **RJSF 6.3.1** | Schema-driven forms | Not mentioned | Not mentioned | Not mentioned | Evaluated (no Zod) | **1/4** | Claude-only evaluation. No native Zod support; two validation systems. |
| **NestJS 11.x** | Backend framework | Future option | Not mentioned | Not mentioned | Not mentioned | **1/4** | ChatGPT-only. Positioned as escape hatch if BFF outgrows route handlers. |
| **Application Insights / OpenTelemetry** | Observability | Implied | Explicit | Explicit | Explicit (via .json) | **4/4** | Parallel provides specific packages (`@vercel/otel`, `@azure/monitor-opentelemetry-exporter`). |

---

## API Layer Comparison (No Consensus)

This deserves special attention because no two sources agree on the API pattern:

| Source | Primary API Pattern | Secondary | Notes |
|---|---|---|---|
| ChatGPT | Next.js Route Handlers (BFF) | Azure Functions (async) | Mentions NestJS as future escape hatch |
| Parallel | Server Actions | Route Handlers (complex orchestration) | Assumes direct Azure SQL access from Server Actions |
| Gemini | Server Actions (sole API) | None | Eliminates REST tier entirely; recommends Drizzle/Prisma |
| Claude | tRPC v11 | Server Actions (supplement) | Full RPC framework with Zod input gates |

**None mention Dapper. None recommend a thin REST API. This is a blocking divergence — see DIVERGENCE_LOG.md.**

---

## ORM / Data Access Comparison (No Consensus)

| Source | Recommendation | Notes |
|---|---|---|
| ChatGPT | Silent | Does not discuss ORM or data access layer |
| Parallel | Silent | Assumes Server Actions talk directly to Azure SQL |
| Gemini | Drizzle or Prisma | Explicitly recommends TypeScript ORM |
| Claude | Prisma 7.x | Explicitly recommends with connection pooling |

**None mention Dapper. This is a blocking divergence — see DIVERGENCE_LOG.md.**

---

## Stack-Incompatible Technologies (Appendix)

Included by sources for comparison only. All sources agree these are not recommended for the current stack.

| Technology | Sources Mentioning | Reason for Exclusion |
|---|---|---|
| Angular Reactive Forms / @ngx-formly | ChatGPT, Parallel, Gemini | Angular ecosystem — requires full framework switch |
| Vue 3 / FormKit / VeeValidate | ChatGPT, Parallel, Gemini | Vue ecosystem — requires full framework switch |
| Blazor / MudBlazor / FluentValidation | ChatGPT, Parallel, Gemini | .NET/WASM — paradigm mismatch with TypeScript stack |
| Apollo Server / GraphQL | ChatGPT, Parallel, Gemini | All agree: overkill for CRUD-heavy single-SQL-backend app |
| Formik 2.4.9 | Claude | Maintenance mode, not recommended |
| Azure Cosmos DB | Claude | Alternative stack only; not recommended given Azure SQL investment |
