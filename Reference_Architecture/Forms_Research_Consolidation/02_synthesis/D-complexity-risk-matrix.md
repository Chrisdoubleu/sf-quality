# D — Complexity & Risk Matrix (Cross-Source Overlay)

**Generated:** 2026-02-26
**Inputs:** 4 extraction files (ChatGPT, Parallel, Gemini, Claude)

---

## Tier Definitions — Cross-Source Comparison

### Simple Tier

| Aspect | ChatGPT | Parallel | Gemini | Claude |
|---|---|---|---|---|
| **Scope** | Single-step, flat data | Single-step, flat data | Single-step, flat data | Single-step, flat data |
| **Pattern** | Component-first RHF + Zod + thin API + relational tables | Server Actions + RHF + Zod + direct SQL | Static React + Basic RHF + inline Zod + Server Action to flat table | Static RHF + Zod + shadcn/ui + Server Actions |
| **Effort (original)** | 3-6 person-weeks | 1-2 weeks | 1-2 weeks per form | 1-3 person-weeks |
| **Effort (agent-adjusted)** | Not provided | ~1 week | Not provided | 0.5-1 week |
| **Agent-Readiness** | High | High | High | High |
| **Audit** | Lightweight auditing | Basic CRUD | Non-temporal tables | Simple Prisma model |

**Consensus:** Complete agreement on scope and agent-readiness. ChatGPT's effort estimate (3-6 weeks) is an outlier — likely assumes a traditional team. All others converge on 1-2 weeks.

---

### Moderate Tier

| Aspect | ChatGPT | Parallel | Gemini | Claude |
|---|---|---|---|---|
| **Scope** | Multi-step, conditional logic, relational data | Multi-step, conditional, relational | Multi-step, conditional logic | Multi-step, conditional, relational |
| **Pattern** | Policy-driven conditional + persisted drafts + hybrid relational/JSON | Hybrid Route Handlers + Server Actions + TanStack Query | Wizard + json-rules-engine + shared Zod + RHF cross-step state | Multi-step wizard + shared Zod + tRPC + json-rules-engine |
| **Effort (original)** | 10-20 person-weeks | 3-6 weeks | Not specified | 6-10 person-weeks |
| **Effort (agent-adjusted)** | Not provided | 2-3 weeks | Not provided | 3-5 weeks |
| **Agent-Readiness** | Medium | Medium | Medium | Medium |
| **Key additions** | Policy model, draft persistence | Transactions, TanStack Query | json-rules-engine, temporal tables | tRPC, json-rules-engine, draft rows |

**Consensus:** Agreement on scope and agent-readiness (Medium). Patterns diverge — ChatGPT uses "policy-driven," Gemini/Claude use json-rules-engine, Parallel uses a simpler hybrid approach. All agree draft persistence is needed.

---

### Complex Tier

| Aspect | ChatGPT | Parallel | Gemini | Claude |
|---|---|---|---|---|
| **Scope** | Dynamic schema, revision-controlled, audit-trailed | Dynamic schema, audit-trailed | Dynamic schema, revision-controlled, audit-trailed | Dynamic schema, revision-controlled, audit-trailed |
| **Pattern** | Metadata-driven schema forms + temporal + externalized audit | Schema-driven/metadata-driven + temporal + JSON columns + Azure Functions | Metadata-driven UI + JSON columns + temporal + Document Intelligence | Schema-driven rendering + hybrid relational/JSON + temporal + rules engine |
| **Effort (original)** | 24-45 person-weeks | 10-20 weeks | Not specified | 16-26 person-weeks |
| **Effort (agent-adjusted)** | 8-15 weeks (extractor estimate) | 6-10 weeks (extractor estimate) | Not provided | 10-16 weeks |
| **Agent-Readiness** | Low | Low | Low | Low-Medium |
| **Key risk** | Schema versioning mistakes; governance overhead | Schema evolution breaking old data; system complexity | Backward compat; performance; testing overhead; "form engine" drift | Schema evolution; dynamic Zod perf; temporal storage growth |

**Consensus:** Agreement on scope, core pattern (metadata/schema-driven), and agent-readiness (Low). Effort estimates vary widely (10-45 person-weeks original). All identify schema evolution as the top risk.

---

## Effort Estimate Overlay

| Tier | ChatGPT | Parallel | Gemini | Claude | Synthesized Range (Agent-Adjusted) |
|---|---|---|---|---|---|
| Simple | 3-6 pw | 1-2 wk | 1-2 wk/form | 1-3 pw | **0.5-1 week** per form with agents |
| Moderate | 10-20 pw | 3-6 wk | Not specified | 6-10 pw | **3-5 weeks** (1 wk design + 2-4 wk agent execution) |
| Complex | 24-45 pw | 10-20 wk | Not specified | 16-26 pw | **10-16 weeks** (4-6 wk design + 6-10 wk agent execution) |

*pw = person-weeks. Agent-adjusted assumes 1 human + coding agents.*

---

## Agent-Readiness Summary

| Tier | Agent-Readiness | Human Work Required | Agent Work |
|---|---|---|---|
| **Simple** | **High** (4/4) | Spec the form (field list, rules, target table) | Scaffold form + schema + API route + SQL proc |
| **Moderate** | **Medium** (4/4) | Step model design, rules schema, draft persistence strategy, transaction boundaries | Implement each step, rule, endpoint |
| **Complex** | **Low** (4/4) | Schema design, renderer architecture, versioning semantics, governance | FieldRenderer registry (once pattern set), CRUD admin, individual renderers |

**Key insight (Claude):** The FieldRenderer registry within the Complex tier is **High** agent-readiness once 2-3 types are built as templates. The overall tier is Low because the architecture decisions around it are human-heavy.

---

## Consolidated Risk Register

Union of all risks from all 4 sources, deduplicated.

### Blocking Risks

| ID | Risk | Tier | Sources | Mitigation |
|---|---|---|---|---|
| R-01 | **Constraint conflict: no source recommends the existing API/data-access pattern** (Dapper, thin API, T-SQL business logic). Proceeding with any source's recommendations requires modifying Constraints #1 and #2 or rejecting the research. | All | 4/4 | Adjudication required. Cannot build until resolved. |
| R-02 | **Schema evolution breaking backward compatibility** — changing form definitions after data has been collected creates migration challenges for historical submissions. | Complex | 4/4 | Semantic versioning for form schemas; migration logic for old submissions; temporal tables preserve historical state. |
| R-03 | **Constraint #5 tension: hybrid JSON columns are a form of configurable schema** — all 4 sources recommend it, but it tensions with "well-defined data model, no EAV." | All | 4/4 | Adjudication required. Scoped exception vs. constraint revision. |

### Significant Risks

| ID | Risk | Tier | Sources | Mitigation |
|---|---|---|---|---|
| R-04 | **Validation drift between client and server** if shared Zod schema discipline breaks down. | All | 4/4 | Shared Zod schemas (the pattern itself is the mitigation). Enforce via CI/linting. |
| R-05 | **Rule precedence bugs** — conflicting conditions in business rules engine produce unexpected behavior. | Moderate, Complex | ChatGPT, Claude | Rule testing framework; precedence documentation; admin UI for rule visualization. |
| R-06 | **Draft/resume consistency** — partial data in multi-step forms creates edge cases with step gating and validation. | Moderate | ChatGPT, Parallel, Claude | Explicit draft persistence strategy; server-side step validation before advancing. |
| R-07 | **Dynamic Zod generation performance** for 100+ field forms (memoization needed). | Complex | Claude | Memoize generated schemas; cache per form definition version. |
| R-08 | **Temporal table storage growth** on high-frequency update forms. | All with temporal | Gemini, Claude | Retention policies; history table partitioning; monitoring. |
| R-09 | **Azure SQL connection pool exhaustion** from frequent draft saves without Prisma singleton / connection management. | Moderate | Claude | Connection pooling strategy; batch saves; debounce. |
| R-10 | **"Form engine" Turing-complete drift** — schema-driven rendering becomes an accidental low-code platform. | Complex | Gemini | Scope constraints on what the engine can express; no general-purpose scripting. |
| R-11 | **Azure Functions cold starts** affecting async pipeline latency. | All with Functions | ChatGPT | Premium plan or always-ready instances for latency-sensitive pipelines. |

### Minor Risks

| ID | Risk | Tier | Sources | Mitigation |
|---|---|---|---|---|
| R-12 | **Renderer customization cost** for matching shadcn/ui look-and-feel in JSON Forms or RJSF. | Complex | ChatGPT, Claude | Build native shadcn/ui renderers rather than adapting third-party themes. |
| R-13 | **Azure SQL Auditing reliability** — may not record all events under very high load. | All with Azure SQL Auditing | ChatGPT | Do not use as sole audit trail; supplement with temporal tables + app events. |
| R-14 | **JSON column type-safety reduction** vs. normalized tables. | All with JSON | Parallel | Computed column indexes; Zod validation at application boundary; projected columns for reporting. |
| R-15 | **Azure OpenAI non-deterministic outputs** require guardrails for quality data. | All with LLM | Parallel, Claude | Human-in-the-loop always; confidence scoring; never auto-commit AI data in regulated contexts. |
| R-16 | **No offline/disconnected form support** — all 4 sources ignore manufacturing floor connectivity issues. | All | 0/4 (gap) | Evidence gap. Needs separate evaluation if shop-floor use requires offline capability. |
| R-17 | **Testing strategy for dynamic forms** poorly covered. | Complex | Gemini | Needs explicit testing strategy (snapshot, contract, property-based). |
