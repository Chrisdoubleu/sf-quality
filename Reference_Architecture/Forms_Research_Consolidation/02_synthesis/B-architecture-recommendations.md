# B — Architecture Recommendations (Layer-by-Layer Comparison)

**Generated:** 2026-02-26
**Inputs:** 4 extraction files (ChatGPT, Parallel, Gemini, Claude)

---

## Layer-by-Layer Comparison

### 1. Frontend Layer

| Aspect | ChatGPT | Parallel | Gemini | Claude |
|---|---|---|---|---|
| **Core library** | RHF + shadcn/ui | RHF + shadcn/ui | RHF + shadcn/ui | RHF + shadcn/ui |
| **Dynamic forms** | Field registry + form runtime (middle path) | Schema-driven / metadata-driven | Factory pattern for field-type-to-component mapping | FieldRenderer registry (15-20 types) |
| **Complex forms** | JSON Forms evaluated | XState for wizards | json-rules-engine for conditional visibility | json-rules-engine on client + server |
| **Alternative** | JSON Forms 3.7 for large catalogs | TanStack Form for large dynamic forms | — | TanStack Form as alternative |

**UNANIMOUS:** React Hook Form + Zod + shadcn/ui as the frontend stack. No dissent.

**CONTESTED:** How to handle dynamic/variable forms. All 4 propose some form of field registry or renderer pattern, but naming and scope differ. ChatGPT's "field registry" is lightest; Gemini's "factory pattern" and Claude's "FieldRenderer registry" are similar; Parallel goes furthest toward full schema-driven rendering.

---

### 2. Validation Layer

| Aspect | ChatGPT | Parallel | Gemini | Claude |
|---|---|---|---|---|
| **Schema tool** | Zod 4.3.6 | Zod (shared schemas) | Zod 3.24 | Zod 3.x |
| **Client** | zodResolver for UX | zodResolver for UX | zodResolver (courtesy) | zodResolver (courtesy) |
| **Server** | safeParse (authoritative) | safeParse in Server Actions | safeParse in Server Actions | tRPC .input() (authoritative) |
| **Business rules** | "Policy model" (conceptual) | JsonLogic placeholder | json-rules-engine (dedicated) | json-rules-engine (dedicated) |
| **Sharing model** | Shared schemas | Single Zod schema export | Single .ts file shared | Three-tier: client courtesy / server authority / rules engine |

**UNANIMOUS:** Shared Zod schemas between client and server. All 4 sources agree on this without qualification.

**CONTESTED:** Business rules engine. Gemini and Claude explicitly recommend json-rules-engine. ChatGPT describes a "policy model" without naming a tool. Parallel mentions JsonLogic as a placeholder. The principle of externalizing rules is broadly agreed; the specific implementation is not.

**UNIQUE (Claude):** Three-tier validation architecture (client courtesy → server authoritative → business rules engine) with Tiers 1+2 sharing the same .ts file. This is the clearest formulation across all sources.

---

### 3. API Layer

| Aspect | ChatGPT | Parallel | Gemini | Claude |
|---|---|---|---|---|
| **Primary pattern** | Route Handlers (BFF) | Server Actions | Server Actions (sole API) | tRPC v11 |
| **Secondary** | Azure Functions (async) | Route Handlers (complex) | — | Server Actions (supplement) |
| **Escape hatch** | NestJS 11.x | — | — | — |
| **Data access** | Not specified | Direct to Azure SQL | Drizzle or Prisma | Prisma 7.x |
| **Contract approach** | ts-rest evaluated | — | — | tRPC Zod .input() |

**NO CONSENSUS.** This is the most contested layer. Four sources, four different API patterns.

- **ChatGPT** keeps the closest to a traditional API (Route Handlers as BFF), but still doesn't mention Dapper
- **Parallel** bypasses the API layer entirely with Server Actions direct to SQL
- **Gemini** eliminates REST, goes Server Actions only, and recommends an ORM (Drizzle/Prisma)
- **Claude** introduces tRPC as a full RPC framework with Zod integration

**BLOCKING:** None of the 4 sources recommend the existing constraint (#2): a thin API layer using Dapper. See DIVERGENCE_LOG.md.

---

### 4. Database / Persistence Layer

| Aspect | ChatGPT | Parallel | Gemini | Claude |
|---|---|---|---|---|
| **Storage model** | Hybrid relational + JSON | Hybrid relational + JSON | Hybrid relational + JSON | Hybrid relational + JSON |
| **JSON approach** | OPENJSON/ISJSON functions | Native JSON type (May 2024) | JSON columns | Native JSON type (May 2024, ~18% savings) |
| **Audit** | Temporal tables + audit events + Azure SQL Auditing (3-layer) | Temporal tables + CDC | Temporal tables | Temporal tables |
| **JSON indexing** | Deliberate strategy needed | Computed column indexes | JSON indexing strategies | Computed columns (JSON Index not in Azure SQL DB) |
| **Variable data** | Canonical JSON payload + projected columns | JSON columns for evolving payloads | JSON for evolving form schemas | JSON for variable form fields |

**UNANIMOUS:** Hybrid relational + JSON storage model. All 4 sources independently arrive at the same conclusion: stable/queryable fields in typed relational columns, variable/evolving data in JSON columns.

**UNANIMOUS:** Azure SQL Temporal Tables for audit trail. 4/4.

**CONTESTED:** Audit depth. ChatGPT recommends a three-layer audit strategy (temporal + app events + Azure SQL Auditing). Parallel adds CDC as complementary. Gemini and Claude rely on temporal tables alone.

**IMPORTANT:** The unanimous hybrid relational + JSON recommendation directly tensions with Constraint #5 (well-defined data model, no EAV/configurable schema). See DIVERGENCE_LOG.md.

**UNIQUE (Claude):** JSON Index (CREATE JSON INDEX) is not available in Azure SQL Database — only on-prem SQL Server 2025. Must use computed column + standard index workaround. Critical implementation detail other sources miss.

---

### 5. Auth Layer

| Aspect | ChatGPT | Parallel | Gemini | Claude |
|---|---|---|---|---|
| **Platform auth** | Entra ID via Easy Auth | Entra ID via Easy Auth | Entra ID via Easy Auth | Entra ID via Easy Auth |
| **Identity flow** | x-ms-client-principal | x-ms-client-principal + x-ms-token-aad-access-token | x-ms-client-principal (Base64 JSON decode) | x-ms-client-principal + app roles |
| **Downstream** | Managed Identity | System-Assigned Managed Identity (secretless) | Managed Identity | System-Assigned Managed Identity (secretless) |
| **Authorization** | App-level role/group decisions | Centralized DAL with React cache() | App-level RBAC from headers | App roles from Entra manifest |

**UNANIMOUS:** Entra ID via Easy Auth at platform level. Zero dissent. This is an automatic decision.

**UNIQUE (Parallel):** Centralized Data Access Layer using React's cache API for memoized session verification.

**UNIQUE (Gemini):** Detailed x-ms-client-principal Base64 JSON decoding flow for RBAC within Server Actions.

---

### 6. AI Services Layer

| Aspect | ChatGPT | Parallel | Gemini | Claude |
|---|---|---|---|---|
| **OCR** | Document Intelligence v4.0 | Document Intelligence v4.0 | Document Intelligence v4.0 | Document Intelligence v4.0 |
| **LLM** | Azure OpenAI structured outputs | Azure OpenAI (smart defaults) | Not recommended for extraction | Azure OpenAI GPT-4o (optional) |
| **Pipeline** | Confidence-tiered workflow | Async (Blob → Queue → Function) | Deterministic OCR preferred | Azure Functions (Durable) + Blob |
| **Human review** | Auto-fill / flag / require attestation | Human-in-the-loop always | Implicit (OCR outputs for user review) | User confirmation required |

**UNANIMOUS:** Azure Document Intelligence v4.0 for OCR extraction. 4/4.

**CONTESTED:** Role of LLMs. Gemini explicitly says Document Intelligence is "far superior to probabilistic LLMs" for structured extraction and omits Azure OpenAI entirely. ChatGPT is the strongest LLM advocate with a confidence-tiered workflow. Claude and Parallel include Azure OpenAI as optional.

**UNIQUE (ChatGPT):** Confidence-tiered AI workflow: auto-fill high-confidence fields, flag medium-confidence, require attestation for critical fields. Most operationally detailed AI integration.

---

## Summary: Unanimous Agreements (Near-Automatic Decisions)

These have 4/4 consensus and can proceed to adjudication as likely ACCEPT:

1. **React Hook Form + Zod + shadcn/ui** as frontend stack
2. **Shared Zod schemas** between client and server validation
3. **Azure SQL Temporal Tables** for audit trail
4. **Entra ID via Easy Auth** for authentication
5. **Azure Document Intelligence v4.0** for OCR
6. **Managed Identity** for Azure service connections
7. **Three-tier complexity model** (Simple / Moderate / Complex) with different patterns per tier
8. **Hybrid relational + JSON** storage model (but tensions with Constraint #5)

## Summary: Contested Positions (Need Adjudication)

1. **API pattern** — 4 different recommendations, none matching Constraint #2 (BLOCKING)
2. **Data access / ORM** — Prisma, Drizzle, or Dapper? (BLOCKING)
3. **Business rules engine** — json-rules-engine vs. policy model vs. JsonLogic (SIGNIFICANT)
4. **LLM role in AI pipeline** — core vs. optional vs. excluded (SIGNIFICANT)
5. **Audit depth** — temporal only vs. 3-layer strategy (MINOR)
6. **Dynamic form complexity** — field registry vs. full schema-driven engine (SIGNIFICANT)
