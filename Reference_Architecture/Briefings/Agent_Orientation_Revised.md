# Reference Architecture Package — Agent Orientation Guide

## Why This Package Exists

This package gives AI agents a vocabulary of proven architectural patterns drawn from a mature, production-grade enterprise platform. The goal is not to replicate that platform. The goal is to give agents enough design literacy to recognize when a pattern like effective-dated temporal modeling, layered authorization, or graph-based workflow orchestration would solve a real problem in our codebase — and to recommend it with enough specificity to be actionable.

Without this context, agents default to generic best practices. With it, they can ground recommendations in patterns that have been proven at scale, then right-size them for our reality.

---

## Our Tech Stack and Maturity

Before you read the architecture files, understand what you're looking at and where each layer stands today.

| Layer | Technology | Current State |
|-------|-----------|---------------|
| **Database** | T-SQL stored procedures on Azure SQL | **Production.** 80 stored procedures, 36 views, 136 migrations. Row-level security, workflow gates, defect taxonomy, audit logging, and multi-schema organization are already shipped. |
| **API** | C# / ASP.NET Core 9, Dapper | **Early development.** Thin pass-through to stored procedures. EasyAuth integration, correlation IDs, and SQL error mapping are in place. ~28 of 30 phases remain. |
| **UI** | TypeScript / Next.js 15, React 19 | **Planning only.** Architecture, stack, and governance decisions are locked. No source code yet. |
| **Cross-repo** | Contract-governed multi-repo | **Working.** DB publishes a procedure/view manifest, API snapshots it and publishes OpenAPI, App will snapshot that. Cycle checks validate the chain. |

**The business logic lives in T-SQL. The API is a pass-through by design. This is not changing.**

---

## What's In This Package

### Reading Order

| Order | File | What It Teaches You |
|-------|------|---------------------|
| 1 | `Briefings/Agent_Orientation_Revised.md` | You're reading it. Context, stack, and instructions. |
| 2 | `Specs/Platform_System_Architecture_Technical_Patterns.json` | **Start here.** Synthesized engineering patterns — design patterns, data structures, infrastructure decisions — with no domain language. |
| 3 | `Specs/Security_Role_Architecture_Agnostic.json` | Deep dive: layered security pipeline, RBAC tree, feature gating, field-level access, org hierarchy scoping. |
| 4 | `Specs/Workflow_Engine_Architecture_Agnostic.json` | Deep dive: DAG-based orchestration, typed node system, expression DSL, dynamic routing, event chaining. |
| 5 | `Specs/API_Integration_Architecture_Agnostic.json` | Deep dive: REST patterns, delta sync, entity model, two-phase retrieval, rate limiting, event notifications. |
| 6 | `Briefings/architectural_briefing.md` | Narrative overview of the Security and Workflow specs. Does not cover API or Hidden Patterns. |

### How The Files Relate

```
Security_Role_Architecture_Agnostic.json ──┐
                                           ├──> Platform_System_Architecture_Technical_Patterns.json
Workflow_Engine_Architecture_Agnostic.json ─┤       (synthesized engineering patterns)
                                           │
API_Integration_Architecture_Agnostic.json ─┘
```

---

## How To Use This Package — By Repo

### sf-quality-db (Production — look for upgrade opportunities)

The database layer is mature. Many foundational patterns are already in place. Focus on gaps between what exists and what the reference architecture shows is possible.

**Already implemented (do not re-recommend):**
- Row-level security via `usp_SetSessionContext` and security schema
- Multi-schema organization (quality, rca, workflow, security, integration, ref, meta, audit)
- Workflow gates for approval/state transitions
- Defect taxonomy with hierarchical classification
- Stored procedure naming conventions (`usp_*`) and view conventions (`vw_*`)
- Idempotent migration pattern with existence guards

**Patterns worth evaluating:**
- **Effective-dated temporal modeling (SCD Type 2)** — Are we storing only current state where point-in-time queries would be valuable? NCR status history, CAPA effectiveness reviews, and audit findings all have temporal dimensions. SQL Server temporal tables or manual EffectiveFrom/EffectiveTo columns are natural fits.
- **Hierarchy-aware traversal optimization** — Our defect taxonomy and organizational structures use tree relationships. Are our recursive CTEs using early-termination, or are they walking more of the tree than needed?
- **Codebook/lookup consolidation** — The `ref` schema likely holds reference data. Is it using a consistent pattern (stable external codes + display values), or are enumerations scattered across schemas?
- **Change detection for delta sync** — If any procedures support "give me what changed since X," compare that against timestamp-windowed CDC. This becomes critical once the API layer needs to support external consumers or the UI needs efficient polling.
- **Stored procedure security layering** — Beyond RLS, is there a reusable authorization check pattern that all write procedures call through, or is each procedure doing its own ad-hoc permission check?

### sf-quality-api (Early Development — patterns are most actionable here)

The API layer has the most runway for incorporating reference patterns during initial development. These should be evaluated as phases are planned, not bolted on later.

**Already in place:**
- EasyAuth handler with Azure AD Object ID extraction
- Correlation ID middleware
- SQL error mapping to HTTP status codes
- Dapper-based stored procedure calls (no ORM)

**Patterns worth incorporating as endpoints are built:**
- **Symmetric read/write payloads** — Ensure GET response structures match POST/PATCH request structures. This is a zero-cost decision that dramatically simplifies both the UI integration and any future external consumers. Decide this before endpoints proliferate.
- **Validate-only mode** — Add a dry-run flag to write endpoints that runs stored procedure validation without committing. Cheap to implement in a pass-through layer and high-value for the UI's form validation experience.
- **Response projection** — Field-level filtering middleware that strips response fields based on caller context. Keeps the logic in C# (where it belongs for HTTP-layer concerns) without moving business logic out of T-SQL.
- **Two-phase retrieval** — For collection endpoints (NCR lists, CAPA lists), separate cheap discovery (filtered list of IDs/summaries) from secured detail (full entity fetch). This maps cleanly to the existing pattern of list views (`vw_*`) + detail procedures (`usp_*`).
- **Cursor-based pagination** — For any endpoint returning large collections, use opaque continuation tokens instead of offset/limit. More stable under concurrent writes, which matters for a quality system where NCRs are being created and updated continuously.

### sf-quality-app (Planning Only — patterns should inform architecture decisions)

There is no source code to review yet. Pattern recommendations for this layer should feed into phase planning, not code review.

**Decisions that reference patterns can inform:**
- **Feature entitlement model** — Should the UI use a tree-structured feature gating system (whitelist model via React context provider), or is the quality system's permission model simple enough for flat role checks? Decide before Phase 3 (Easy Auth Session).
- **Role-scoped rendering** — Will the same screens render differently based on user role (e.g., quality engineer vs. production supervisor vs. auditor)? If so, the reference architecture's behavioral parameterization pattern should inform the component architecture in Phase 2 (Design System Shell).
- **Form-to-workflow binding** — NCR workflows, CAPA approvals, and SCAR processes all have approval flows. Should these be hardcoded per form or driven by configuration from the workflow gates in the database? Decide before Phase 5 (NCR Lifecycle UX).
- **Selective expansion** — Loading strategy for entity detail views. Fetch the NCR summary first, then expand related CAPAs, attachments, RCA data on demand? The reference architecture's Expand parameter pattern is directly relevant.

### Cross-Repo (Already Sophisticated — look for incremental improvements)

The contract governance chain is working and validated by CI. Do not propose rearchitecting it.

**Worth evaluating:**
- **Stable external identifiers** — Are contract interfaces using stable codes that survive internal ID changes, or are they leaking surrogate keys? The reference architecture's dual-key identity pattern (internal ID + external XRefCode) is directly applicable to contract manifests.
- **Environment promotion** — Is configuration movement between dev/staging/prod standardized across all three repos, or does each repo handle promotion differently?

---

## Constraints — What NOT To Recommend

- **Do not recommend rewriting stored procedures in C#.** Business logic lives in T-SQL. Apply patterns there.
- **Do not propose a heavy ORM layer.** The C# layer uses Dapper by design.
- **Do not recommend multi-tenant isolation patterns.** This is a single-tenant system for one organization.
- **Do not recommend patterns that require a service bus or message broker.** We deploy to Azure App Service, not a microservices platform.
- **Do not recommend EAV (Entity-Attribute-Value) for custom properties.** The quality domain's data model is well-defined, not tenant-configurable.
- **Do not try to implement all patterns at once.** Identify the 2-3 with the highest impact for whatever specific area you are reviewing.
- **Do not re-recommend things that are already built.** Read the maturity section above.

---

## Key Engineering Concepts Quick Reference

### Data Patterns
| Pattern | What It Solves | Where It Fits |
|---------|---------------|---------------|
| SCD Type 2 effective dating | Point-in-time queries, history without losing current state | T-SQL: NCR status history, CAPA tracking, audit findings |
| Dual-key entity identity | Stable API identifiers that survive internal refactoring | Cross-repo contracts, API endpoint design |
| Composite aggregate root | Central entity with subordinate collections | T-SQL: NCR with attachments, actions, RCA links |
| Adjacency-list tree traversal | Efficient hierarchy queries with early termination | T-SQL: defect taxonomy, org structure |

### Security Patterns
| Pattern | What It Solves | Where It Fits |
|---------|---------------|---------------|
| Defense-in-depth authorization | Multiple independent security checks, all must pass | T-SQL + C#: layered security check pipeline |
| Monotonic subtractive RBAC | Child roles can only narrow parent permissions | T-SQL: role hierarchy in security schema |
| Feature tree (whitelist) | Capability entitlements as a navigable tree | Next.js: React context-based feature gating |

### API Patterns
| Pattern | What It Solves | Where It Fits |
|---------|---------------|---------------|
| Symmetric read/write payloads | GET response = POST/PATCH request structure | C#: endpoint design convention |
| Two-phase retrieval | Cheap list + secured detail, avoids over-fetching | C#: collection endpoints backed by views + procs |
| Timestamp-windowed CDC | Efficient delta sync via high-water-mark polling | T-SQL + C#: change detection for UI polling |
| Cursor-based pagination | Stable pagination under concurrent writes | C#: collection endpoint middleware |
| Validate-only mode | Dry-run writes for form validation | C#: query parameter on write endpoints |

### Workflow Patterns
| Pattern | What It Solves | Where It Fits |
|---------|---------------|---------------|
| Typed node graph | Structured approval flows with defined node behaviors | T-SQL: workflow gate evolution |
| Hierarchy-aware routing | Resolve approval recipients at runtime via tree traversal | T-SQL: dynamic approver resolution |
| Structural immutability after activation | Frozen workflow topology once execution begins | T-SQL: workflow instance integrity |

---

## Design Pattern Cross-Reference

| Pattern | Where It Appears | Applicable Layer |
|---------|-----------------|-----------------|
| Aggregate Root (DDD) | Entity data model | T-SQL: parent/child stored proc organization |
| Chain of Responsibility | Authorization pipeline | T-SQL + C#: reusable security check layer |
| Strategy | Workflow routing | T-SQL: configurable routing algorithms |
| State Machine | Workflow execution | T-SQL: status-driven stored procedures |
| Observer / Pub-Sub | Event notifications | Cross-repo: contract-based event flow |
| Command | Write operations | C#: POST/PATCH with dry-run mode |
| Facade | REST API layer | C#: the pass-through layer IS a facade |
| Proxy | Field-level filtering | C#: response filtering middleware |
| CQRS (partial) | Two-phase retrieval | T-SQL: separate list views vs. detail procedures |
| Event Sourcing (partial) | Audit trail | T-SQL: temporal tables / shadow tables |
| Flyweight | Reference data | T-SQL: shared codebook/lookup tables in ref schema |

---

## File Manifest

| File | Size | Format |
|------|------|--------|
| `Briefings/Agent_Orientation_Revised.md` | ~14 KB | Markdown |
| `Specs/Platform_System_Architecture_Technical_Patterns.json` | ~49 KB | JSON |
| `Specs/Security_Role_Architecture_Agnostic.json` | ~61 KB | JSON |
| `Specs/Workflow_Engine_Architecture_Agnostic.json` | ~48 KB | JSON |
| `Specs/API_Integration_Architecture_Agnostic.json` | ~53 KB | JSON |
| `Briefings/architectural_briefing.md` | ~19 KB | Markdown |

**Total: ~240 KB of structured architectural knowledge.**
