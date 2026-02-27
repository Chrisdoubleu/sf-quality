# Forms Architecture — Decision Brief for Human Adjudication

**Date:** 2026-02-26
**For:** Chris Walsh
**Purpose:** Organize every decision you need to make, with plain-language context, pros/cons, and impact assessment. Read this before writing rulings in `03_adjudication/FINAL_DECISIONS.md`.

---

## Critical Context The Research Missed

Before diving into decisions, there is one fact that **reframes everything**:

**Your API is C# / ASP.NET Core 9.0 with Dapper. It is not a Node.js/TypeScript API.**

All 4 research sources assumed a TypeScript-everywhere stack. They recommended tRPC, Prisma, Drizzle, Server Actions talking directly to SQL — all TypeScript tools. None of them acknowledged that your actual system has a C# API sitting between the Next.js frontend and Azure SQL.

Your real architecture is:

```
sf-quality-app (Next.js 15 / TypeScript)
        ↓ calls
sf-quality-api (ASP.NET Core 9.0 / C# / Dapper)
        ↓ calls
sf-quality-db  (Azure SQL / T-SQL stored procedures)
```

Connected by a contract chain: DB publishes a manifest → API publishes OpenAPI → App pins a snapshot. Three independent repos, three independent deployments.

**This means:**

- "Use Prisma" doesn't make sense — Prisma is a Node.js ORM and your API is C#
- "Use tRPC" doesn't make sense — tRPC is TypeScript-to-TypeScript RPC
- "Server Actions talk directly to SQL" would bypass your entire API layer and contract chain
- "Put business rules in TypeScript json-rules-engine" would split business logic across two languages (C# API + TypeScript frontend)

The research is still valuable — it tells you what the industry recommends for forms architecture. But every recommendation needs to be filtered through your actual three-repo, two-language reality.

**The real question for each decision is:** Does the research make a strong enough case to change your existing architecture, or should you adapt the research recommendations to fit within your existing architecture?

---

## How This Document Is Organized

- **Section 1:** The 5 Constraint Decisions (the big ones)
- **Section 2:** Architecture Pattern Decisions (how to build forms)
- **Section 3:** Technology Choices (specific tools)
- **Section 4:** The Quality_Forms_Module Question (keep, modify, or replace the existing design)

Each decision includes:

- What it is (plain English)
- What your system does today
- What the research recommends
- Your options with honest pros/cons — evaluated on technical merit, not effort
- What happens if you get it wrong

---

# Section 1: Constraint Decisions

These are the big architectural calls. Everything else flows from these.

---

## Decision 1: Where Does Business Logic Live?

**Constraint #1:** "Business logic stays in T-SQL (stored procedures, not in the API or frontend)"

### What This Means In Plain English

Right now, when your system needs to decide something — "is this NCR valid?", "should this defect auto-close?", "what's the next approval step?" — that logic runs inside SQL Server as stored procedures. Your C# API just passes data through. Your frontend just shows what the API returns.

The research says: for *forms specifically*, business logic should live in TypeScript. Things like "show this field only when severity = Critical" or "require an attachment when the defect type is Safety" — those rules should run in the browser (for instant UX feedback) AND on the server (for security). If they live only in T-SQL, you can't show/hide fields without a round trip to the server for every change.

### What The Research Said

- **4/4 sources** put form validation and conditional logic in TypeScript/Node.js
- **0/4 sources** mention T-SQL for any form business logic
- Two sources (Gemini, Claude) specifically recommend `json-rules-engine` — a JavaScript library that evaluates business rules stored as JSON
- The core argument: forms need instant client-side feedback (field visibility, conditional validation, step gating) that cannot wait for a server round trip

### Your Options

**Option A: Keep all business logic in T-SQL (constraint holds)**

- Pros:
  - One authoritative place for all business rules (the database).
  - The database is the ultimate enforcement boundary — nothing can bypass it.
  - Your 29 stored procedures for the Quality Forms Module work as designed.
- Cons:
  - Every conditional field requires an API round trip. User changes a dropdown → wait for server → fields appear/disappear. On a factory floor tablet with mediocre Wi-Fi, this means a sluggish, frustrating UX.
  - You cannot share validation between client and server. You'll write validation rules twice — once in TypeScript (for UX) and once in T-SQL (for enforcement) — and they WILL drift over time. Drift means a user fills out a form that looks valid, submits it, and gets a server error. That's a bad experience.
  - Forms are fundamentally different from CRUD operations. A defect status transition is a server event. But "show these 5 fields when the user picks 'Critical'" is a UI interaction that shouldn't hit the network.
  - 0/4 research sources support this approach for forms. The consensus against it is unanimous.
- Risk if wrong: Sluggish forms that manufacturing floor operators hate. Validation drift bugs that erode trust in the system.

**Option B: Split the boundary — form UX logic in TypeScript, data integrity in T-SQL**

- Pros:
  - Forms get instant client-side feedback (show/hide fields, conditional validation, step navigation) with zero network latency.
  - Shared Zod schemas eliminate validation drift — the exact same schema runs in the browser and in the Next.js server before data ever hits the API.
  - Core data rules (foreign key constraints, status transitions, approval workflows, referential integrity) stay in T-SQL where they are today. The database remains the ultimate enforcement boundary.
  - The C# API stays as-is. The Next.js app handles form UX logic before calling the API. Compatible with your contract chain (App → API → DB).
  - This is how modern web forms actually work everywhere — client-side for UX, server-side for enforcement. The boundary is natural, not artificial.
- Cons:
  - Business logic now lives in two places: TypeScript (form presentation rules) and T-SQL (data integrity rules). You need a clear, documented boundary for what goes where.
  - If the boundary isn't enforced, rules will drift into the wrong layer over time.
- Risk if wrong: Confusion about where to put new rules. Mitigated by a clear documented rule: "Does it affect what the user sees? → TypeScript. Does it affect what the database accepts? → T-SQL."

**Option C: Move all business logic to TypeScript (constraint fully revised)**

- Pros:
  - One language for all logic. Maximum consistency.
  - Full research alignment.
  - TypeScript rules are more testable (unit tests in Jest vs. testing stored procedures).
- Cons:
  - Your entire stored procedure library (80 procs) loses its business logic — the procs become even thinner or get removed.
  - The database stops being the enforcement boundary. Any bug in the TypeScript layer could write bad data.
  - Your C# API becomes unnecessary if all logic is in TypeScript — you'd need to rethink the whole stack.
  - The research assumed a TypeScript-only stack. They recommended this because they didn't know a C# API existed. In a two-language system, "all logic in TypeScript" means the database is unprotected.
- Risk if wrong: Data integrity issues. The database's greatest strength is that it enforces rules regardless of which client calls it. Moving rules out of SQL removes that guarantee.

**My read:** Option B is the technically correct answer. The research is right that form UX logic must run client-side — round-tripping to the server for field visibility is objectively bad UX. But the research is wrong that ALL logic should leave the database — they didn't know your database IS the enforcement boundary with 80 procs. The split is natural: presentation logic (what you see) in TypeScript, data integrity logic (what's allowed) in T-SQL.

---

## Decision 2: What Happens To The C# API and Dapper?

**Constraint #2:** "API layer stays thin (Dapper micro-ORM, not Entity Framework)"

### What This Means In Plain English

Your API is a C# application that receives HTTP requests from the frontend, calls stored procedures via Dapper (a lightweight .NET library), and returns results. It doesn't contain business logic — it's a "pass-through gateway." The constraint says to keep it that way and not add a heavy ORM.

The research recommended TypeScript ORMs (Prisma, Drizzle) and TypeScript API patterns (tRPC, Server Actions). None of these work with your C# API. The research assumed a different architecture.

### What The Research Said

- **Gemini:** Use Drizzle or Prisma (TypeScript ORMs)
- **Claude:** Use Prisma 7.x + tRPC
- **Parallel:** Use Server Actions direct to SQL (bypass API entirely)
- **ChatGPT:** Use Route Handlers as BFF (closest to your current pattern)
- **0/4 sources** mention Dapper or C# API

### Your Options

**Option A: Keep the C# API with Dapper exactly as-is**

- Pros:
  - The contract chain (DB manifest → API OpenAPI → App snapshot) is a proven governance mechanism that catches breaking changes at PR time. This is genuinely valuable architecture, not just legacy.
  - Dapper + stored procedures is the fastest data access pattern in .NET. No ORM overhead, no query translation, no N+1 problems.
  - The thin API pattern is actually ideal for your system — the API is a security boundary (Easy Auth, session context) and a contract surface (OpenAPI), not a business logic layer.
  - The 29 planned inspection endpoints fit this model perfectly — each one is a thin wrapper around a stored procedure.
- Cons:
  - Two languages (C# + TypeScript) means context-switching.
  - No shared types between frontend and API — TypeScript types on one side, C# DTOs on the other. Changes to a form schema require updating both.
  - The API is pure boilerplate — every endpoint is "deserialize request, call proc, serialize response." It's repetitive by design, which agents handle well but still adds surface area.
- Risk if wrong: Type drift between frontend and API. Mitigated by OpenAPI contract validation (which you already have).

**Option B: Keep C# API for existing domains, add Next.js Server Actions for forms**

- Pros:
  - Forms-specific logic (validation, conditional rules) stays in TypeScript where shared Zod schemas work.
  - Reduces C# boilerplate for new form endpoints.
- Cons:
  - Two API patterns in one system. Every new endpoint requires deciding which pattern to use.
  - Server Actions would still need to call stored procedures for data writes — so either Next.js connects directly to Azure SQL (adding a SQL client to the frontend, bypassing the API security boundary) or Server Actions call the C# API over HTTP (adding network latency for no benefit vs. just calling the API from the client).
  - Breaks the contract chain for the forms domain. The App would no longer pin an API OpenAPI snapshot for form endpoints — you lose the automated breaking-change detection.
  - The split creates an architectural seam that grows over time. "Which forms go through the API? Which go through Server Actions?" becomes an ongoing question.
- Risk if wrong: Architecture fragmentation. The contract chain — your strongest governance mechanism — gets partially bypassed.

**Option C: Replace C# API entirely with a TypeScript API layer**

- Pros:
  - One language across the entire stack. Maximum developer (and agent) consistency.
  - Shared Zod schemas end-to-end — frontend, API, and validation all speak TypeScript.
  - Full research alignment.
  - Eliminates the C#/TypeScript context switch permanently.
- Cons:
  - Your C# API IS the security boundary — it enforces Easy Auth, sets SQL session context (`usp_SetSessionContext`), and provides the OpenAPI contract surface. A replacement must replicate all of this.
  - A TypeScript API still needs to call stored procedures. The research recommended ORMs (Prisma, Drizzle), but your logic is IN the stored procedures, not in ORM models. A TypeScript API calling stored procedures via `mssql` or `tedious` is just Dapper in a different language.
  - The contract chain governance (DB manifest → API OpenAPI → App snapshot) is already built with CI/CD enforcement. Rebuilding it for a TypeScript API is real work for equivalent functionality.
  - The 80 stored procedure call sites need to be rewritten in TypeScript. The procs themselves don't change, just the calling code.
- Risk if wrong: You rebuild something that already works. The new version may actually be better long-term (one language is genuinely simpler), but it needs to match every capability the current API provides.

**My read:** This is the hardest decision because Option A is correct TODAY but Option C may be correct LONG-TERM. The C# API exists, works, and has governance. But every research source independently concluded that TypeScript end-to-end is the better architecture for forms-heavy applications. The honest answer: Option A is the right choice IF you're committed to the C#/Dapper stack for the long haul. Option C is the right choice IF you'd eventually want a TypeScript-only stack anyway. Option B is the worst choice — it gives you the downsides of both without the full benefits of either.

---

## Decision 3: Single-Tenant — Does It Hold?

**Constraint #3:** "Single-tenant system"

**No source challenges this. 0/4 even mention multi-tenancy. Constraint holds. No decision needed.**

---

## Decision 4: Azure App Service + Azure Functions?

**Constraint #4:** "Azure App Service deployment (no message brokers/orchestration)"

### What This Means In Plain English

Your system runs on Azure App Service — a straightforward "put your app here and it runs" hosting service. The constraint says no complex messaging infrastructure (Kafka, RabbitMQ, Service Bus).

Three of four research sources recommend Azure Functions for one specific use case: processing scanned documents with AI. The idea is: someone uploads a paper inspection form → it goes to blob storage → an Azure Function picks it up → Document Intelligence extracts the data → results land in the database.

### Your Options

**Option A: Constraint holds — no Azure Functions**

- Pros: Simpler infrastructure. One deployment target.
- Cons: If you want AI-assisted document processing, you'd need to do it synchronously in the API request (user waits while OCR runs — could be 10-30 seconds for a multi-page document) or build a polling mechanism in your API (reinventing what Functions gives you natively).
- Risk if wrong: You build a worse async processing mechanism than what Azure Functions provides out of the box.

**Option B: Scoped exception — Azure Functions for async AI/OCR pipelines only**

- Pros: Right tool for the right job. Document processing is inherently async — upload → process → notify. Functions consumption plan scales to zero when idle (you pay nothing when no documents are being processed). The Blob trigger pattern (upload file → Function fires → processes → writes results) is exactly what this use case needs.
- Cons: One more Azure resource to manage and deploy.
- Risk if wrong: Minimal. Functions for blob-triggered processing is one of the most proven Azure patterns.

**My read:** Option B. Azure Functions for blob-triggered async processing is precisely what the service was designed for. The constraint's intent (no complex messaging) is sound — this isn't adding Kafka or Service Bus. It's adding a serverless function that fires when a file appears in blob storage.

---

## Decision 5: Can Form Data Use JSON Columns?

**Constraint #5:** "Quality domain data model is well-defined (no EAV/configurable schema)"

### What This Means In Plain English

Your database uses typed tables — every column has a specific name and data type. An NCR has `NcrNumber`, `Status`, `Severity`, etc. as real columns. The constraint says: don't use flexible storage patterns where you can create arbitrary fields at runtime (like Entity-Attribute-Value tables or schemaless document stores).

All 4 research sources recommend a hybrid approach: keep typed relational columns for the important stuff (status, owner, dates, foreign keys) but add a JSON column for variable form data (inspection checklists that differ by product/machine).

### Why This Matters For Your System Specifically

Your Quality Forms Module currently has **6 typed response tables** for inspection data:

- `InspectionResponseNumeric` (for numeric measurements)
- `InspectionResponseAttribute` (for pass/fail)
- `InspectionResponseText` (for free text)
- `InspectionResponseDatetime` (for date/time values)
- `InspectionResponseSelection` (for dropdown choices)
- `InspectionResponseAttachment` (for file uploads)

This is a well-designed typed approach. Each response type has its own table with appropriate columns and constraints. It's queryable, indexable, and the database enforces data types.

The research alternative: instead of 6 typed response tables, store the entire inspection response as a JSON document in a single column, with key fields (inspector, date, status) extracted to relational columns for querying.

### Your Options

**Option A: Constraint holds — keep fully typed response tables**

- Pros:
  - Every field is queryable with standard SQL. No JSON functions needed for reporting.
  - Database enforces types at the storage level (a numeric response literally cannot contain text).
  - SPC (Statistical Process Control) and reporting queries are straightforward column references — `SELECT AVG(MeasuredValue) FROM InspectionResponseNumeric WHERE ...`. This matters a LOT for a quality system.
  - Full referential integrity — foreign keys, check constraints, unique constraints all work naturally on typed columns.
- Cons:
  - The 6-table design assumes you know all response types upfront. If a new type emerges (barcode scan, GPS coordinate, signature capture), it's a new table, new procs, new endpoints.
  - If inspection checklists vary significantly by product/machine, you need either many nullable columns or a new response table variant per checklist type. This doesn't scale well past ~15-20 distinct checklist shapes.
  - The typed design forces the database to know the form structure. If form structure changes frequently, the database becomes a bottleneck for change.
- Risk if wrong: If checklist variability is high, the typed tables become a constant source of schema changes. But if variability is low, this is the objectively correct design.

**Option B: Scoped exception — JSON columns for variable checklist data only**

- Pros:
  - Core quality events (NCRs, CAPAs, 8Ds, SCARs) stay fully typed. No change there — these have stable, known schemas.
  - Inspection checklist responses that genuinely vary by product/machine can use a JSON column — one table handles any checklist shape.
  - Zod validates the JSON content at the application boundary — it's not untyped, it's validated-at-runtime. The schema is defined in code (Zod), just not in the database DDL.
  - Computed column indexes on frequently-queried JSON fields give you SQL query performance where you need it.
  - Azure SQL's native JSON type (GA since May 2024) provides ~18% storage savings over NVARCHAR(MAX) and supports partial document updates.
  - This is the most architecturally honest answer: core quality data IS well-defined (typed tables). Checklist data IS variable (JSON). Use the right tool for each.
- Cons:
  - Reporting on JSON data requires `JSON_VALUE` / `OPENJSON` functions — more complex than column references. SPC queries on measurements stored in JSON are uglier.
  - JSON Index (`CREATE JSON INDEX`) is NOT available in Azure SQL Database — only SQL Server 2025 on-prem. You must use computed columns as a workaround for indexing.
  - The database schema no longer fully describes the data shape for JSON columns. You need documentation discipline to know what's in the JSON.
  - Slippery slope risk: once JSON columns exist, the temptation to use them for everything grows. Need a clear rule for what goes typed vs. JSON.
- Risk if wrong: Reporting complexity increases. Mitigated by promoting frequently-queried fields to computed columns.

**Option C: Full hybrid for all form types**

- Pros:
  - Maximum flexibility. All form submissions (not just inspections) use hybrid relational + JSON. Consistent data access pattern across the entire forms domain.
  - Fewest tables, fewest procs, fewest endpoints. The simplest schema.
  - Full alignment with all 4 research sources.
- Cons:
  - The existing Quality Forms Module design (6 typed response tables, 27 tables total) gets redesigned.
  - Stable quality event forms (NCRs, CAPAs, 8Ds) lose type enforcement at the database level for no benefit — their schemas don't vary.
  - JSON columns in a quality system for SPC data means your statistical queries hit JSON functions instead of typed columns. For a manufacturing quality system, this is a real cost — SPC queries run constantly.
  - You're using a flexible tool where a rigid tool is better. NCR data doesn't need JSON flexibility.
- Risk if wrong: Over-engineering. Quality event forms with stable schemas lose database-level type safety for flexibility they don't need.

**My read:** This depends entirely on a factual question: **How much do inspection checklists actually vary across your products and machines at Select Finishing?**

- If the answer is "we have 5-10 standard checklists and they rarely change" → **Option A**. Your typed tables are the right design and the research is solving a problem you don't have.
- If the answer is "every product line has its own checklist and new products get new checklists" → **Option B**. The typed tables will become a constant migration treadmill while JSON handles variability naturally.
- If the answer is "I genuinely don't know yet" → **Option B** is the safer bet. It preserves typed tables for everything except the genuinely variable part. You can always promote JSON fields to typed columns later; going the other direction is harder.

Option C is only right if you want ALL form data (including NCRs, CAPAs, etc.) in JSON, which makes no technical sense for stable schemas.

---

# Section 2: Architecture Pattern Decisions

---

## Decision 6: How Should Forms Handle Conditional Logic?

### What This Means

Many quality forms have rules like: "If defect severity is Critical, require a photo attachment" or "If inspection type is Receiving, show the supplier fields." These rules control which fields appear, which are required, and what values are valid.

### What The Research Said

- **Gemini + Claude:** Use `json-rules-engine` — a JavaScript library where rules are stored as JSON in the database. Business users (or developers) edit rules without code deployments.
- **ChatGPT:** Build a "policy model" — conceptually similar but not tied to a specific library.
- **Parallel:** Mentions JsonLogic as a placeholder; no depth.

### Your Options

**Option A: Hardcode rules in React components**

- How it works: `if (severity === 'Critical') { showPhotoField = true }` in your TypeScript code.
- Pros: Simple. Easy to understand. Easy to debug. Every rule is visible in the code. Highly agent-friendly — agents can generate conditional logic from a plain-English spec trivially.
- Cons: Every rule change requires a code deployment. Rules are scattered across components — there's no single place to see "all the conditional logic in the system." As rule count grows, components become cluttered with conditional logic that obscures the form structure.
- Best for: Systems with relatively few, stable rules.

++***Option B: Externalize rules with json-rules-engine***++

- ++***How it works: Rules stored as JSON in the database. A rules engine evaluates them at runtime. Same rules can run client-side (for UX) and server-side (for enforcement).***++
- ++***Pros: Rules are data, not code — they can be changed, versioned, and audited independently of deployments. All rules live in one place (the database). Rules are inherently testable (input → engine → output). For a regulated quality system, having auditable, versioned business rules is a genuine compliance advantage.***++
- ++***Cons: Another dependency. Bridging async rule evaluation with React Hook Form's synchronous rendering requires custom hooks (limited public examples, though both Gemini and Claude describe the pattern). The rules need a management mechanism (even if it's just SQL inserts initially, not a full admin UI).***++
- ++***Best for: Systems with many conditional rules that change with some frequency, especially where audit trails on rule changes matter.***++

**Option C: Build rules as a structured TypeScript module (middle ground)**

- How it works: Rules defined as typed TypeScript objects in a dedicated `/rules` module — not scattered across components, but also not in a database. A simple engine evaluates them.
- Pros: All rules in one place. TypeScript type-safety on rule definitions. No external dependency. Can be refactored to database-stored rules later by just changing the data source.
- Cons: Rule changes still require deployment. You're building a mini rules engine.
- Best for: Getting the organizational benefits of externalized rules without the database storage complexity upfront.

**My read:** For a manufacturing quality system — where conditional logic controls things like escalation paths, required evidence, and regulatory compliance fields — the rules ARE the product. They deserve to be first-class, auditable, and centralized. Option B (json-rules-engine) is the technically best answer. Option C is a reasonable stepping stone if you want to solidify the rule patterns before committing to database storage. Option A is only right if your forms genuinely have very little conditional logic, which seems unlikely for a quality management system.

---

## Decision 7: How Complex Should Dynamic Forms Get?

### What This Means

This is the "form engine" question. At one extreme, every form is a handcrafted React component. At the other extreme, forms are generated at runtime from JSON definitions stored in the database — a "form engine."

### What The Research Said

All 4 sources agree on a three-tier model:

- **Simple forms** (flat, single-step): Handcrafted React components. Everyone agrees.
- **Moderate forms** (multi-step, conditional): Wizard pattern with shared validation. Everyone agrees.
- **Complex forms** (dynamic, variable): This is where they diverge.

For the Complex tier:

- **ChatGPT:** Build a "field registry + form runtime" — a lightweight mapping of field types to components. NOT a full form engine.
- **Gemini:** Build a full schema-driven rendering engine, but explicitly warns: "Moving from Moderate to Complex is a profound paradigm shift — you're transitioning from building forms to building a form engine."
- **Claude:** Build a `FieldRenderer` registry with 15-20 component types. Build 2-3 by hand, then agents replicate the pattern.
- **Parallel:** Full metadata-driven rendering from database-stored JSON.

### Your Options

**Option A: No form engine — every form is hand-built**

- Pros: No infrastructure investment. Every form is a standalone React component — easy to understand, test, and modify independently.
- Cons: Code duplication across similar forms. No consistency enforcement — each form may implement the same field type differently. Maintenance burden grows linearly with form count. If you have 30+ form types, you have 30+ components that each implement their own version of "date picker with validation."

**Option B: Field registry (lightweight)**

- How it works: A mapping from field types (text, number, date, dropdown, pass/fail, photo, measurement) to shadcn/ui components with standard Zod schemas. Forms are still defined in code, but they compose from a shared registry of standardized field components.
- Pros: Consistency by default — every "numeric measurement" field looks and validates the same way across all forms. Reduced duplication. The registry is highly agent-friendly (once the registry exists, agents compose forms by selecting field types from it). Progressive — you can start with 5 field types and add more as needed.
- Cons: Form structure is still in code. Adding a genuinely new form type still requires writing a React component (though it's now mostly composition from registry pieces).

**Option C: Full schema-driven form engine**

- How it works: Form definitions stored as JSON in the database. A rendering engine reads the definition and generates the form at runtime. Changes to form structure don't require code deployments.
- Pros: Maximum flexibility. Scales to hundreds of form types. Non-developers can eventually create new forms through an admin UI. The rendering engine, once built, makes new forms nearly free to add.
- Cons: The engine itself is a product — it needs schema versioning, backward compatibility, testing infrastructure, and governance to prevent it from becoming a low-code platform. Gemini's warning is real: "you're transitioning from building forms to building a form engine." Testing is harder — infinite form permutations from JSON definitions vs. finite known components.
- Gemini's critical insight: The risk of "Turing-complete drift" — where the engine's expressive power keeps growing until it's an accidental programming language — is real and has killed projects.

**My read:** Option B (field registry) is the technically best starting point for any system. It gives you the core benefit (consistency, composability) without the core risk (building a product within your product). The question is whether you ALSO need Option C. That depends on whether non-developers need to create forms and whether form count exceeds what code-defined composition can handle. For a manufacturing QMS, the likely answer is: field registry first, evaluate schema-driven engine only when/if the form catalog grows beyond what the registry pattern can support. Gemini's warning about form engine drift is the most important single insight in the entire research.

---

## Decision 8: Audit Strategy Depth

### What The Research Said

- **ChatGPT (most comprehensive):** Three-layer audit — temporal tables (what changed) + application audit events (who changed it and why) + Azure SQL Auditing (compliance evidence).
- **Parallel:** Temporal tables + CDC (Change Data Capture) for downstream event streams.
- **Gemini + Claude:** Temporal tables alone are sufficient.

### Your Options

**Option A: Temporal tables only**

- Pros: Zero application code for audit. Database handles everything. Point-in-time queries built in.
- Cons: Temporal tables track WHAT changed and WHEN, but not WHO or WHY. You'd need to add `ModifiedBy` and `ModifiedReason` columns manually to get the business context.

**Option B: Temporal tables + application audit events**

- Pros: Complete audit picture. Temporal tables give you "what changed when" (forensic). Application audit events give you "who changed it, through which workflow, with what justification" (operational/compliance). For a quality system under regulatory audit (ISO 9001, IATF 16949, FDA 21 CFR Part 11), having BOTH layers is not optional — auditors want to know who approved the change and why, not just that a row was updated.
- Cons: Application audit events require code in the API layer — each meaningful action writes an audit record. More tables, more data. But this is inherent to the requirement, not optional overhead.

**Option C: Full three-layer (temporal + app events + Azure SQL Auditing)**

- Pros: Three independent audit trails. Azure SQL Auditing provides a database-level log that even DBAs can't tamper with (writes to immutable storage). Strongest possible compliance posture.
- Cons: ChatGPT uniquely flagged that Azure SQL Auditing "may not record all events under very high load." It's supplementary evidence, not a replacement for the other two layers. Adds operational overhead (configuring audit destinations, managing retention, querying across three audit systems).

**My read:** Option B is the correct answer for a regulated quality system. Temporal tables are non-negotiable (4/4 unanimous). Application audit events are required by the nature of the domain — quality auditors need to know WHO approved a change, not just that it happened. Azure SQL Auditing (Option C) is a nice-to-have compliance layer but adds complexity without changing the core audit capability. Your stored procedures already have session context (`usp_SetSessionContext`) — leveraging that for audit events is natural.

---

# Section 3: Technology Choices

---

## Decision 9: Business Rules Engine — Which One?

If you chose to externalize rules (Decision 6, Options B or C), which tool?


| Option                  | Sources                 | Pros                                                                                                | Cons                                                                                                                 |
| ----------------------- | ----------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **json-rules-engine**   | Gemini, Claude          | Well-documented, 7.3K GitHub stars, JSON-stored rules, runs in browser + server, active maintenance | Limited to boolean condition evaluation; no built-in form field awareness; async evaluation needs custom React hooks |
| **JsonLogic**           | Parallel (mention only) | Simpler rule format, widely used in form builders                                                   | Less flexible than json-rules-engine; designed for simple evaluations, not complex rule chains                       |
| **Custom policy model** | ChatGPT (conceptual)    | Tailored to your exact needs; no external dependency                                                | You build and maintain the engine yourself; no community, no ecosystem                                               |


**My read:** json-rules-engine. Two independent sources recommended it with specific reasoning. It's the most capable option, it runs isomorphically (browser + server), and its JSON rule format is naturally storable in a database. The async evaluation challenge with React Hook Form is real but solvable with a custom hook — and both Gemini and Claude describe the integration pattern.

---

## Decision 10: LLM Role in AI Pipeline


| Option                                   | Sources                   | Trade-off                                                                                                                                                                                                                                                             |
| ---------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Document Intelligence only**           | Gemini                    | Deterministic extraction. Consistent results. Lower cost. Purpose-built for structured document OCR. Gemini: "far superior to probabilistic LLMs for structured extraction."                                                                                          |
| **Document Intelligence + Azure OpenAI** | ChatGPT, Claude, Parallel | LLMs add value for: natural language → structured data mapping, smart defaults based on context, data quality checks, classification of unstructured text. Non-deterministic — same input may produce different output. Requires confidence scoring and human review. |


**My read:** Both, with clear scope boundaries. Document Intelligence for OCR and structured extraction (scanned inspection forms, packing slips, COAs) — this is what it's built for and it's deterministic. Azure OpenAI for genuinely unstructured-to-structured tasks (classifying free-text defect descriptions, suggesting root cause categories, NL-to-form mapping) — these are tasks where LLMs genuinely outperform rule-based approaches. ChatGPT's confidence-tiered workflow (auto-fill high-confidence / flag medium / require attestation for critical) is the right operational model for LLM output in a quality system.

---

# Section 4: The Quality_Forms_Module Question

---

## Decision 11: Does The Existing Inspection Design Hold?

This is the meta-decision that connects everything else.

### What Exists Today

The Quality Forms Module has a complete design:

- **27 inspection tables** (11 template definition, 2 assignment, 4 execution, 6 typed response, 4 temporal)
- **29 stored procedures** (template management, assignment, submission, finding linkage)
- **29 API endpoints** (thin Dapper pass-through to procs)
- **Three contract-chain waves** (QF-A, QF-B, QF-C)
- **9 entry gates** that must be green before any work starts

This design uses typed-per-entity schemas — every response type has its own table with proper constraints.

### What The Research Recommends Instead

All 4 sources recommend a hybrid relational + JSON approach with schema-driven rendering for variable forms. This would mean:

- Fewer tables (maybe 5-10 instead of 27)
- Fewer stored procedures (maybe 10 instead of 29)
- Fewer API endpoints (maybe 10 instead of 29)
- A JSON column for variable inspection data instead of 6 typed response tables
- A rendering engine or field registry instead of hand-built form components

### Your Options

**Option A: Keep the existing design as-is**

- Pros:
  - Typed tables are the strongest data integrity guarantee for a quality system. The database enforces every constraint.
  - The design has been through a final authoritative review.
  - 29 SPs and 29 endpoints are highly agent-friendly — repetitive, templated patterns.
  - It fits your existing constraints and contract chain perfectly.
  - SPC and reporting queries are straightforward column references.
- Cons:
  - No shared Zod validation — validation is in T-SQL SPs, not shareable with the frontend. This means validation drift between client and server (Decision 1).
  - If checklist variability is high, 6 typed response tables become a migration bottleneck.
  - The research unanimously says typed-per-entity for variable data isn't the modern approach.
  - The design doesn't account for form UX concerns (conditional field visibility, multi-step wizards, draft saving) — it's a data/API design, not a form interaction design.
- Best when: The inspection schema is stable and you're willing to accept duplicate validation.

**Option B: Modify the existing design — add Zod validation + field registry, keep typed tables**

- Pros:
  - Keep the 27-table schema, the SPs, and the contract chain.
  - Add shared Zod schemas in the frontend for client-side validation that mirrors the SP validation rules.
  - Add temporal tables to the template definitions (already planned in the design).
  - Add a field registry for consistent form rendering across all inspection types.
  - Incorporates the research's best ideas (shared Zod, temporal audit, field registry, conditional logic in TypeScript) without changing the data model.
  - This is an additive modification — everything that exists keeps working while new capabilities layer on top.
- Cons:
  - Validation logic exists in two places (Zod in TypeScript + CHECK constraints in T-SQL). They must be kept in sync. This is manageable if the Zod schemas are treated as the source of truth and the T-SQL constraints are a safety net, not a competing rule set.
  - Doesn't address the variability question — if checklist shapes need to change frequently, you still need 6-table migrations per new shape.
- Best when: You want the research's UX and validation improvements while preserving the existing data architecture.

++***Option C: Redesign with hybrid relational + JSON***++

- ++***Pros:***++
  - ++***Full alignment with all 4 research sources.***++
  - ++***The hybrid model is architecturally cleaner for variable inspection data: stable metadata (inspector, date, status, template reference) in typed columns; variable checklist responses in a validated JSON column.***++
  - ++***Fewer tables = simpler schema = easier to reason about.***++
  - ++***Schema-driven rendering becomes naturally possible — the JSON form definition and JSON response data are the same paradigm.***++
  - ++***Computed column indexes provide SQL query performance on the JSON fields you actually report on.***++
  - ++***This is the design you would arrive at if you started fresh with the research recommendations.***++
- ++***Cons:***++
  - ++***The existing 27-table design gets redesigned. The design work isn't wasted (it clarified the domain model), but the specific schema changes.***++
  - ++***JSON-based SPC queries are more complex than typed column queries. For a quality system that runs statistical analysis on measurement data, this matters.***++
  - ++***The 9 entry gates and contract-chain waves may need adjustment.***++
  - ++***Reporting users (if any use SQL directly) need to learn JSON functions.***++
- ++***Best when: You want the best long-term architecture for a forms-heavy quality system with variable inspection checklists.***++

**My read:** This is the central question of the entire consolidation. The honest answer:

- **If inspection checklists are mostly stable** (5-10 templates, rare changes): **Option B**. Layer Zod + field registry on top of the existing typed design. You get better UX and validation without touching the database.
- **If inspection checklists are genuinely variable** (per-product, per-machine, change when new products onboard): **Option C**. The typed-per-entity design will fight you on every schema change while the hybrid design absorbs variability naturally.
- **The research unanimously recommends Option C.** But the research didn't know your system uses typed tables with stored procedures, and the research didn't ask how variable your actual checklists are. The right answer depends on your domain reality, not the research consensus.

The one thing I'd push back on regardless: **Option A is the weakest choice.** Even if you keep typed tables, adding Zod validation and a field registry (Option B) makes the forms objectively better for users. The question is B vs. C, not whether to modernize.

---

# Decision Summary Card

For quick reference — fill in your rulings:


| #   | Decision                         | Options                                                                   | Impact        |
| --- | -------------------------------- | ------------------------------------------------------------------------- | ------------- |
| 1   | Where does business logic live?  | A: All T-SQL / **B: Split boundary** / C: All TypeScript                  | Blocking      |
| 2   | What happens to C# API + Dapper? | A: Keep as-is / B: Hybrid / C: Replace                                    | Blocking      |
| 3   | Single-tenant?                   | **Holds (no decision needed)**                                            | None          |
| 4   | Azure Functions exception?       | A: No Functions / **B: Scoped for AI/OCR**                                | Significant   |
| 5   | JSON columns for form data?      | A: No (typed only) / B: Scoped exception / C: Full hybrid                 | Blocking      |
| 6   | Conditional logic approach?      | A: Hardcoded / **B: Rules engine** / C: Structured TS module              | Significant   |
| 7   | Dynamic form complexity?         | A: No engine / **B: Field registry** / C: Full engine                     | Significant   |
| 8   | Audit depth?                     | A: Temporal only / **B: Temporal + app events** / C: Three-layer          | Significant   |
| 9   | Business rules engine?           | **json-rules-engine** (if externalizing)                                  | Depends on D6 |
| 10  | LLM role?                        | A: Doc Intelligence only / **B: Both, scoped**                            | Significant   |
| 11  | Quality_Forms_Module design?     | A: Keep as-is / B: Modify (add Zod + field registry) / C: Redesign hybrid | Blocking      |


*Bold = my lean, evaluated on technical merit regardless of effort. Your call.*

---

## What Happens After You Decide

Once you've made your rulings on these 11 decisions, I can:

1. Write `03_adjudication/FINAL_DECISIONS.md` with your rulings, evidence, and rationale
2. Generate `04_deliverables/` (architecture spec, GSD seeding content, coding conventions) aligned to your decisions
3. Update the README status tracker

The adjudication format from the design doc requires each decision to have: ID, Question, Decision (ACCEPT/REJECT/MODIFY), Ruling, Evidence, and Impact.