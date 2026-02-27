# E — Sources & Evidence Quality

**Generated:** 2026-02-26
**Inputs:** 4 extraction files (ChatGPT, Parallel, Gemini, Claude)

---

## Source Overview

| Source | Total Citations | Resolvable (spot-check) | Recency Range | Quality Rating |
|---|---|---|---|---|
| ChatGPT | 10 formal + inline refs | 10/10 | Jul 2025 — Feb 2026 | Strong |
| Parallel | 10 formal + ~40 in JSON | 5/5 spot-checked | Jan 2021 — Feb 2026 | Adequate |
| Gemini | 60 numbered references | ~8/10 spot-checked | Apr 2025 — Feb 2026 | Strong |
| Claude | 10 formal | 10/10 spot-checked | Jul 2022 — Feb 2026 | Strong |

---

## Multi-Researcher Citations (Higher Confidence)

Technologies/resources cited by 3+ sources carry higher evidence confidence.

| Citation Topic | Sources Citing | Confidence |
|---|---|---|
| React Hook Form documentation (react-hook-form.com) | ChatGPT, Parallel, Gemini, Claude | **Very High** |
| Azure SQL Temporal Tables (learn.microsoft.com) | ChatGPT, Parallel, Gemini, Claude | **Very High** |
| Zod documentation / npm | ChatGPT, Parallel, Gemini, Claude | **Very High** |
| Azure AI Document Intelligence docs | ChatGPT, Parallel, Gemini, Claude | **Very High** |
| TanStack Form documentation | Parallel, Gemini, Claude | **High** |
| shadcn/ui forms documentation | Gemini, Claude | **Medium** |
| Next.js App Router / Server Actions docs | Parallel, Gemini, Claude | **High** |
| Azure SQL JSON features (OPENJSON, native JSON type) | ChatGPT, Parallel, Claude | **High** |
| json-rules-engine (GitHub) | Gemini, Claude | **Medium** |
| Application Insights / OpenTelemetry | Parallel, Gemini, Claude | **High** |

---

## Single-Researcher Citations (Verify Before Relying)

| Citation | Source | Topic | Verification Status |
|---|---|---|---|
| ServiceNow UI policies as pattern example | ChatGPT | Policy-driven conditional logic | Plausible — ServiceNow is well-known for UI policies |
| Salesforce metadata-driven design | ChatGPT | Schema-driven forms | Plausible — Salesforce platform is metadata-driven |
| Hike Medical — PostgreSQL JSONB FormSchema | Gemini | Schema-driven rendering | Cited as Medium blog post; harder to verify |
| Pallet.com — shared Zod schemas | Gemini | Isomorphic validation | Cited as blog post; plausible for logistics startup |
| OUTsurance — temporal tables for insurance | Gemini | Temporal auditing | Plausible — insurance industry case |
| Heap Analytics — JSONB + relational | Claude | Hybrid persistence | Blog post cited; 30% savings figure needs context (about extracting FROM JSON) |
| MakerKit.dev — shared Zod + next-safe-action | Claude | Isomorphic validation | Developer tool documentation; plausible |
| Adobe AEM Headless Adaptive Forms | Claude | Schema-driven rendering | Adobe product documentation; verifiable |
| Azure SQL native JSON GA May 2024 | Parallel, Claude | JSON columns | Cited by 2 sources — verify against Azure SQL compatibility level requirements |
| Azure SQL Auditing reliability caveat | ChatGPT | Audit | Specific claim: "may not record all events under high load." Verify against Microsoft docs. |
| JSON Index not in Azure SQL DB | Claude | JSON indexing | Specific claim: only SQL Server 2025 on-prem. Verify against Azure SQL feature matrix. |
| CDC + Temporal as complementary | Parallel | Audit | Plausible — distinct features serving different purposes |

---

## Evidence Gaps

Significant topics where research coverage is weak or absent across ALL sources.

| Gap | Sources Covering | Impact |
|---|---|---|
| **Dapper / thin API layer patterns** | 0/4 | **Blocking** — no source addresses the existing data access approach. Cannot compare research recommendations against current architecture without this. |
| **T-SQL stored procedure patterns for business logic** | 0/4 | **Blocking** — all sources place business logic in TypeScript. No evidence base for evaluating whether T-SQL business logic is viable for forms. |
| **Offline/disconnected form scenarios** | 0/4 | **Significant** — manufacturing floor connectivity is a real concern. No source discusses PWA, local storage, or sync patterns. |
| **EAV pattern evaluation** | 0/4 | **Minor** — the prompt asked about EAV but no source covered it. The hybrid JSON approach may make EAV irrelevant, but the gap should be noted. |
| **Form accessibility (WCAG)** | 0/4 (beyond noting Radix is a11y-focused) | **Significant** — shadcn/ui + Radix provides a foundation, but no source discusses accessibility testing or requirements for manufacturing/quality contexts. |
| **Testing strategies for dynamic forms** | 0/4 detailed | **Significant** — Gemini acknowledges testing overhead as a risk but offers no concrete patterns. No source covers snapshot testing, contract testing, or property-based testing for schema-driven forms. |
| **Form builder / admin UI patterns** | 1/4 (ChatGPT briefly) | **Significant** — if metadata-driven rendering is adopted, someone must create/edit form definitions. Only ChatGPT mentions a "4-6 person-week" admin phase with no detail. |
| **Non-React framework in-depth comparison** | Gemini, Parallel (table only) | **Minor** — all sources include Angular/Vue/Blazor in comparison tables but none provide depth. Not needed given stack commitment, but the comparison is superficial. |
| **Cost analysis / Azure pricing** | 0/4 | **Minor** — no source discusses DTU/vCore sizing, App Service tier, or Functions consumption plan costs. |

---

## Source Bias Assessment

| Source | Potential Bias | Impact on Recommendations |
|---|---|---|
| ChatGPT | Most conservative; closest to traditional enterprise architecture. Tends toward heavier patterns (NestJS, three-layer audit). | May over-engineer for a 1-human + agents team. |
| Parallel | Assumes Next.js Server Actions are the default mutation path. Does not question this assumption. | May understate the need for a separate API layer. |
| Gemini | Strongest opinions (Server Actions as sole API, Document Intelligence over LLMs, json-rules-engine). Takes positions rather than presenting options. | Clear recommendations but may dismiss valid alternatives too quickly. |
| Claude | Recommends the most tooling (tRPC, Prisma, json-rules-engine) — heaviest stack. | May over-tool for the actual problem. tRPC + Prisma is a significant stack addition. |
| **All 4** | None acknowledge existing constraints (#1, #2, #5). All recommend architectures that assume greenfield TypeScript-first development. | **Systematic bias**: the research was prompted for "best practices" without being grounded in existing constraints. This is by design (the research should challenge constraints) but it means every recommendation needs evaluation against constraints, not blind adoption. |

---

## Recency Notes

- All sources cite documentation accessed in February 2026
- Oldest cited source: January 2021 (sqlshack audit overview, via Parallel)
- Most technology versions cited are current as of February 2026
- Azure SQL native JSON type (May 2024 GA) — cited by Parallel and Claude. Verify compatibility level requirements for current Azure SQL DB tier.
- Gemini sources have the weakest date provenance: most are "Accessed February 26, 2026" with no original publication dates
