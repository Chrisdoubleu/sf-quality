# Reference Architecture Package

## What This Is

Architectural patterns reverse-engineered from a production enterprise SaaS platform, abstracted into platform-agnostic terms. This package exists so that any AI agent working on our codebase has a shared vocabulary of proven engineering patterns to draw from — not to duplicate, but to recognize where they'd solve real problems.

The patterns came from an HRIS platform but the engineering is domain-agnostic: temporal modeling, hierarchy traversal, workflow orchestration, layered security, expression engines, delta sync, graph-based routing. These are system design patterns, not HR features.

---

## Our System

**Domain:** Quality management for automotive manufacturing — NCRs, CAPAs, SCARs, 8D investigations, audit management, defect taxonomy, LPCS documentation. Governed by IATF 16949 and CQI-12 standards. Traceability and auditability are not nice-to-haves; they're compliance requirements.

**Stack:**

| Layer | Tech | State |
|-------|------|-------|
| **sf-quality-db** | T-SQL stored procedures, SQL Server | Mature. v1.0 shipped, v1.1 in progress. 80+ procs, 36 views, 136 migrations, 21+ phases. |
| **sf-quality-api** | C# pass-through with Dapper | Early. Phase 2 of ~30. Thin by design. |
| **sf-quality-app** | Next.js (React/TypeScript) | Planning. No code yet. |
| **Repos** | Contract-governed multi-repo | Established interface contracts between layers. |

The business logic lives in T-SQL. The C# layer is a deliberate pass-through. The front-end hasn't been built yet. These are architectural choices, not limitations.

**What's already in the database (context, not a boundary):**

The database layer is mature and already implements several significant patterns. Know what exists so you can build on it, refine it, or identify where a reference pattern would strengthen an existing implementation — not so you can skip over it.

- Row-level security via `usp_SetSessionContext` and the security schema
- Multi-schema organization (quality, rca, workflow, security, integration, ref, meta, audit)
- Workflow gates for approval and state transitions
- Defect taxonomy with hierarchical classification
- Audit infrastructure
- Stored procedure conventions (`usp_*`) and view conventions (`vw_*`)
- Idempotent migration pattern with existence guards
- Contract manifest publishing (80 procs, 36 views)

**What's already in the API:**

- EasyAuth handler with Azure AD Object ID extraction
- Correlation ID middleware
- SQL error mapping to HTTP status codes
- Dapper-based stored procedure calls
- OpenAPI spec publishing and DB contract snapshot validation

---

## How To Use This Package

Read the reference files. Look at our code. Think about what applies.

Your job is to understand the engineering patterns in the reference architecture deeply enough to recognize opportunities in our codebase on your own. Don't apply patterns just because they exist in the reference — apply them because they solve a problem we actually have or will have.

Existing implementations are fair game for improvement. If our RLS could be strengthened by a pattern from the reference security architecture, or our workflow gates would benefit from a typed-node approach, say so. "Already built" means "understand what's there before recommending" — not "hands off."

**What matters:** The database is mature and already handles a lot. The API is still taking shape. The app is a blank slate. The quality domain has specific needs around workflow state machines, cross-organizational traceability, temporal auditability, and hierarchical classification. Ground your thinking in those realities.

### Reading Order

| Order | File | Content |
|-------|------|---------|
| 1 | This file | Orientation and codebase context |
| 2 | `Platform_System_Architecture_Technical_Patterns.json` | Pure engineering patterns — no domain language. Design patterns, data structures, algorithms. Start here. |
| 3 | `Security_Role_Architecture_Agnostic.json` | 10-layer security architecture: RBAC, feature gating, field-level access, org hierarchy scoping |
| 4 | `Workflow_Engine_Architecture_Agnostic.json` | DAG-based orchestration: typed nodes, expression DSL, dynamic routing, event chaining |
| 5 | `API_Integration_Architecture_Agnostic.json` | REST API patterns: entity model, delta sync, two-phase retrieval, event notifications |
| 6 | `architectural_briefing.md` | Narrative overview connecting the three spec files |

The three spec files describe how principals get access (Security), how state changes flow through approvals (Workflow), and how external systems read and write data (API). The Technical Patterns file synthesizes all three into named engineering patterns.

---

## Constraints

These reflect architectural decisions and infrastructure realities. They aren't negotiable.

- **Business logic stays in T-SQL.** Don't recommend moving stored procedure logic into C#.
- **The API layer stays thin.** Dapper, not Entity Framework. Pass-through, not domain service layer.
- **Single-tenant system.** Multi-tenant isolation patterns don't apply.
- **Azure App Service deployment.** No service bus, no message broker, no container orchestration.
- **The quality domain's data model is well-defined.** EAV / tenant-configurable schema patterns don't apply.
- **Prioritize.** Identify the highest-impact patterns for whatever specific area you're reviewing, not an exhaustive catalog.

---

## File Manifest

| File | Size | Format |
|------|------|--------|
| `README_AGENT_ORIENTATION.md` | ~4 KB | Markdown |
| `Platform_System_Architecture_Technical_Patterns.json` | ~49 KB | JSON |
| `Security_Role_Architecture_Agnostic.json` | ~61 KB | JSON |
| `Workflow_Engine_Architecture_Agnostic.json` | ~48 KB | JSON |
| `API_Integration_Architecture_Agnostic.json` | ~53 KB | JSON |
| `architectural_briefing.md` | ~19 KB | Markdown |
