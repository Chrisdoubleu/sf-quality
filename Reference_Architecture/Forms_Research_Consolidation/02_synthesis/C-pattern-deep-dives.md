# C — Pattern Deep Dives (Deduplicated Catalog)

**Generated:** 2026-02-26
**Inputs:** 4 extraction files (ChatGPT, Parallel, Gemini, Claude)

---

## Pattern Confidence Ranking

Patterns are ranked by: (1) number of sources recommending, (2) relevance to manufacturing QMS + Azure SQL + audit requirements, (3) agent-readiness.

---

## Tier 1: High-Confidence Patterns (3-4 sources)

### P-01: Shared Zod Schema Validation (Isomorphic Client-Server)

**Sources:** 4/4 (ChatGPT, Parallel, Gemini, Claude)
**Confidence:** Very High

| Aspect | Cross-Source View |
|---|---|
| **Description** | Single Zod schema .ts file defines form shape and constraints. Client uses zodResolver for courtesy validation (UX feedback). Server imports same schema for authoritative enforcement (security boundary). |
| **When to Use** | All forms. Universally recommended by every source. |
| **When to Avoid** | Legacy systems with entrenched non-TypeScript backend validation where rewrite is infeasible (Claude). |
| **Consensus** | Complete. All 4 sources describe this identically. |
| **Variance** | ChatGPT: Zod + server safeParse(). Parallel: Zod + Server Action safeParse(). Gemini: Zod + Server Action safeParse(). Claude: Zod + tRPC .input() as the server gate. The principle is identical; only the server invocation mechanism differs. |
| **QMS Relevance** | Critical — quality data integrity requires server-side validation that cannot be bypassed. Shared schemas eliminate the #1 bug category (client/server validation drift). |
| **Agent-Readiness** | **High** — deterministic pattern. Given a field list + rules, an agent can generate the Zod schema and both client/server integration points. |
| **Real-World** | MakerKit.dev (Claude): shared Zod schemas with next-safe-action, "cut mutation code nearly in half." Pallet.com (Gemini): shared Zod across internal systems and AI agents. |

---

### P-02: Hybrid Relational + JSON Persistence

**Sources:** 4/4 (ChatGPT, Parallel, Gemini, Claude)
**Confidence:** Very High (but tensions with Constraint #5)

| Aspect | Cross-Source View |
|---|---|
| **Description** | Core queryable fields (submitter, status, timestamps, foreign keys) stored in typed relational columns with indexes. Variable/evolving form field data stored in JSON column. Form definitions may also follow this pattern. |
| **When to Use** | Forms that evolve (new fields per product line, regulatory changes); need ACID + SQL reporting + FK relationships; variable sections exist alongside stable metadata (Claude, Gemini). |
| **When to Avoid** | All fields are known and stable — pure relational is simpler (Claude). JSON docs routinely exceed ~1MB (Claude). Every JSON field needs individual SQL-level indexing (Claude). |
| **Consensus** | Complete on the principle. All 4 arrive at hybrid independently. |
| **Variance** | ChatGPT: "canonical submission payload as JSON + projected columns for reporting." Parallel: native JSON type (May 2024 GA, 18% savings). Gemini: JSON columns alongside relational. Claude: native JSON type + computed column indexes (notes JSON Index not in Azure SQL DB). |
| **QMS Relevance** | High — inspection checklists genuinely vary by machine type, product line, and regulatory context. The hybrid model accommodates this while keeping core quality event fields (NCR number, status, owner, dates) in typed columns. |
| **Agent-Readiness** | **Medium** — agents need a clear contract for what goes in relational columns vs. JSON. A typed-per-entity schema is more agent-friendly (Parallel extractor notes). Once the boundary is defined, agents can implement. |
| **Constraint Tension** | **Directly tensions with Constraint #5.** Storing variable data in JSON IS a form of configurable schema. Whether this is an acceptable scoped exception or a full constraint violation requires adjudication. |
| **Real-World** | Heap Analytics (Claude): PostgreSQL JSONB + relational columns, 30% disk savings from extracting hot fields. |

---

### P-03: System-Versioned Temporal Auditing

**Sources:** 4/4 (ChatGPT, Parallel, Gemini, Claude)
**Confidence:** Very High

| Aspect | Cross-Source View |
|---|---|
| **Description** | Azure SQL feature. Automatically tracks full history of data changes. Creates Period Start/End datetime2 columns and mirrored History Table. On UPDATE/DELETE, previous row state is autonomously archived. Enables FOR SYSTEM_TIME AS OF time-travel queries. |
| **When to Use** | All quality event tables, form submission tables, and form definition tables. Regulatory compliance, data forensics, point-in-time reconstruction. |
| **When to Avoid** | Highly volatile tables with millions of transient updates/hour (IoT telemetry, session state) — history bloat (Gemini). |
| **Consensus** | Complete. All 4 recommend without qualification. |
| **Variance** | ChatGPT: three-layer audit (temporal + app events + Azure SQL Auditing). Parallel: CDC as complement. Gemini: temporal alone. Claude: temporal alone + notes no native "who changed" tracking (needs ModifiedBy column). |
| **QMS Relevance** | Critical — manufacturing quality systems have regulatory audit requirements (FDA 21 CFR Part 11, ISO 9001, IATF 16949). Temporal tables provide immutable, database-level audit trail that cannot be circumvented by application code. |
| **Agent-Readiness** | **High** — converting tables to system-versioned is a well-documented SQL operation. An agent can generate ALTER TABLE statements from current schema with zero ambiguity. |
| **Real-World** | OUTsurance (Gemini): temporal tables for point-in-time policy snapshots. |

---

### P-04: Three-Tier Complexity Model

**Sources:** 4/4 (ChatGPT, Parallel, Gemini, Claude)
**Confidence:** Very High

| Aspect | Cross-Source View |
|---|---|
| **Description** | Forms classified into Simple / Moderate / Complex tiers, each with different architectural patterns, effort estimates, and agent-readiness levels. Prevents over-engineering simple forms with infrastructure designed for complex ones. |
| **When to Use** | Always — as the decision framework for how to build each form type. |
| **Tier Boundaries** | Simple: single-step, flat data, static schema. Moderate: multi-step, conditional logic, relational data. Complex: dynamic schema, revision-controlled, audit-trailed, metadata-driven. |
| **Consensus** | Complete on the three-tier structure. |
| **Variance** | Effort estimates vary significantly (see D-complexity-risk-matrix.md). Agent-readiness assessments are consistent: Simple=High, Moderate=Medium, Complex=Low. |
| **QMS Relevance** | Critical — the quality domain has all three tiers. Simple: basic data collection forms. Moderate: NCR workflows with conditional logic. Complex: configurable inspection checklists per product/machine. |
| **Agent-Readiness** | The model itself determines agent-readiness per form. Simple tier is highly automatable. |

---

### P-05: Metadata-Driven / Schema-Driven Form Rendering

**Sources:** 4/4 (ChatGPT, Parallel, Gemini, Claude)
**Confidence:** High (all mention it, but with varying enthusiasm)

| Aspect | Cross-Source View |
|---|---|
| **Description** | Form structure, layout, validation, and conditional logic defined by external JSON payload (stored in DB). Frontend is a rendering engine that maps field types to React components. Decouples form structure from frontend code. |
| **When to Use** | Complex tier only. Many forms, frequent changes, non-developer form modification needed. Gemini explicitly warns: "only justified at Complex tier." |
| **When to Avoid** | Simple/Moderate forms (all sources). Bespoke interactive UI (Gemini). Fewer than 10 stable form types (Claude). |
| **Consensus** | All 4 describe the pattern. All 4 agree it's high-complexity, high-reward. |
| **Variance** | ChatGPT: "field registry + form runtime" as a lighter middle path. Parallel: full schema-driven/metadata-driven. Gemini: factory pattern for field-type-to-component mapping; warns against "Turing-complete drift." Claude: FieldRenderer registry as the agent-friendly entry point. |
| **QMS Relevance** | High for inspection checklists (vary by product/machine). Lower for core quality events (NCRs, CAPAs, 8Ds) which have stable schemas. |
| **Agent-Readiness** | **Low** for the engine design. **High** for individual field type renderers once the pattern is established (Claude: "build 2-3 by hand, agents replicate"). |
| **Constraint Tension** | Tensions with Constraint #5. A full metadata-driven engine IS a configurable schema system. A limited field registry with developer-controlled definitions may be acceptable. |
| **Real-World** | Hike Medical (Gemini): PostgreSQL JSONB FormSchema for clinical workflows. Adobe AEM Headless Adaptive Forms (Claude): JSON form model rendering across web/mobile. Salesforce (ChatGPT): metadata-driven design as core principle. |

---

## Tier 2: Medium-Confidence Patterns (2 sources)

### P-06: Externalized Business Rules Engine

**Sources:** 2/4 explicit (Gemini, Claude), 2/4 conceptual (ChatGPT, Parallel)
**Confidence:** Medium-High

| Aspect | Cross-Source View |
|---|---|
| **Description** | Business rules for conditional visibility, validation, and workflow logic stored as JSON in database. Evaluated by a rules engine at runtime rather than hardcoded in components. |
| **Specific tool** | Gemini: json-rules-engine 7.3. Claude: json-rules-engine 7.3.1. ChatGPT: "policy model" (unnamed). Parallel: JsonLogic (placeholder). |
| **When to Use** | Conditional logic is pervasive (compliance workflows, safety forms, QA nonconformance). Rules change without deployments. |
| **When to Avoid** | All rules are simple, deterministic code. Minimal conditionality. (ChatGPT) |
| **QMS Relevance** | High — quality workflows have significant conditional logic (escalation paths, required fields based on severity, approval routing). |
| **Agent-Readiness** | **Medium** — the library is documented, but bridging async rule evaluation with RHF's synchronous rendering requires custom hooks with limited public examples (Gemini extractor). |
| **Unique (Claude):** | Rules run on BOTH client (field visibility) and server (authoritative enforcement) from the same definitions. |

---

### P-07: State Machine-Driven Wizards (XState)

**Sources:** 2/4 (Parallel, Gemini)
**Confidence:** Medium

| Aspect | Cross-Source View |
|---|---|
| **Description** | Formal state machines define valid states and transitions for multi-step forms. Prevents impossible states (skipping required steps, double submission). |
| **When to Use** | Complex wizards with conditional branching, interdependencies between steps. Manufacturing config wizards, complex order forms. |
| **When to Avoid** | Simple linear forms where useState or URL params suffice. |
| **QMS Relevance** | Medium — 8D and CAPA workflows are multi-step with conditional paths. Inspection forms are less wizard-like. |
| **Agent-Readiness** | **Medium** — state machine definition is JSON config (agent-suitable); designing which states/transitions exist requires human domain expertise. |

---

### P-08: Confidence-Tiered AI Workflow

**Sources:** 2/4 explicit (ChatGPT, Claude), 2/4 implied (Parallel, Gemini)
**Confidence:** Medium-High

| Aspect | Cross-Source View |
|---|---|
| **Description** | AI-extracted data categorized by confidence level. High-confidence: auto-fill. Medium-confidence: flag for review. Low-confidence or critical fields: require human attestation. |
| **When to Use** | Any AI-assisted data entry (OCR, LLM extraction). |
| **Consensus** | All 4 agree on human-in-the-loop. ChatGPT provides the most operational detail (three tiers). |
| **QMS Relevance** | Critical — quality data cannot be auto-filled without review in regulated contexts. Confidence tiers map naturally to field criticality in quality systems. |
| **Agent-Readiness** | **Medium** — the integration code is documented, but confidence thresholds and review UX require human judgment. |

---

## Tier 3: Single-Source Patterns (1 source — verify before adopting)

### P-09: Three-Layer Audit Strategy

**Source:** ChatGPT only
**Description:** Temporal tables (forensic history) + application audit events (business narrative — who/why/which policy) + Azure SQL Auditing (compliance evidence to Storage/Log Analytics). Each layer covers gaps in the others.
**QMS Relevance:** Very high — the three layers map to different audit audiences (data forensics, operational traceability, compliance evidence).
**Note:** ChatGPT uniquely calls out Azure SQL Auditing's reliability caveat: "may not record all events under high load."

### P-10: CDC as Complementary Audit

**Source:** Parallel only
**Description:** Change Data Capture alongside Temporal Tables — CDC for change tracking streams, temporal for point-in-time reconstruction.
**QMS Relevance:** Medium — CDC is useful for downstream integrations (event streaming to analytics) but adds operational complexity.

### P-11: Field Registry as Middle Path

**Source:** ChatGPT primarily (Claude's FieldRenderer registry is similar)
**Description:** A registry mapping field types to React components + Zod schemas, positioned between hardcoded forms and full metadata-driven rendering. Lighter than a form engine; more structured than ad-hoc forms.
**QMS Relevance:** High — provides structure without the governance overhead of a full form engine.
**Agent-Readiness:** **High** — deterministic contract per field type.

### P-12: Form Engine Drift Warning

**Source:** Gemini only
**Description:** Explicit warning that moving from Moderate to Complex tier is "a profound paradigm shift: transitioning from building forms to building a form engine." Warns against Turing-complete drift where the engine becomes a low-code platform.
**QMS Relevance:** Important design guardrail — a quality system should not accidentally become a general-purpose form builder.

---

## Agent-Readiness Summary by Pattern

| Pattern | Agent-Readiness | Blocker |
|---|---|---|
| P-01: Shared Zod Validation | **High** | None |
| P-02: Hybrid Relational + JSON | **Medium** | Needs boundary definition (what's relational vs. JSON) |
| P-03: Temporal Auditing | **High** | None |
| P-04: Three-Tier Model | N/A (framework) | N/A |
| P-05: Schema-Driven Rendering | **Low** (engine) / **High** (renderers) | Engine design requires human architect |
| P-06: Business Rules Engine | **Medium** | Rules schema + async-to-sync bridge design |
| P-07: XState Wizards | **Medium** | State/transition design requires domain expertise |
| P-08: AI Confidence Tiers | **Medium** | Threshold design + review UX |
| P-09: Three-Layer Audit | **High** | Decision on whether to adopt all three layers |
| P-10: CDC Complement | **Medium** | Operational complexity vs. value |
| P-11: Field Registry | **High** | None once contract defined |
| P-12: Form Engine Warning | N/A (guardrail) | N/A |
