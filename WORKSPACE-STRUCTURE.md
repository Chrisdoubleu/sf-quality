# sf-quality Workspace Structure

## Overview

**sf-quality** is a quality management system for Select Finishing, built as a **multi-repo architecture** (not a monorepo). Three independent Git repositories are tied together via a VS Code multi-folder workspace file and a contract-based governance chain.

```
c:\Dev\sf-quality\
├── sf-quality.code-workspace          # VS Code workspace linking all 3 repos
├── Reference_Architecture/            # Single source of truth for architecture patterns + execution plan
│   ├── README.md                      #   Index and reading order
│   ├── Execution_Plan.md             #   46 patterns → GSD phases across all repos
│   ├── Pattern_Mapping.md            #   Gap audit: 46 patterns vs. current implementation
│   ├── Specs/                         #   4 platform-agnostic JSON architecture specifications
│   ├── Briefings/                     #   Narrative orientation + agent guidance documents
│   └── Hidden_Patterns/              #   3 reverse-engineered implicit patterns
├── sf-quality-db/                     # Database repo (SQL Server)
├── sf-quality-api/                    # API repo (ASP.NET Core)
└── sf-quality-app/                    # Frontend repo (Next.js — planning only, no source yet)
```

---

## Repository Layout

### Is it a Monorepo?

**No.** Each subfolder has its own `.git` directory and is an independent repository. There is no `.git` at the `sf-quality/` root level. The only shared file is `sf-quality.code-workspace`, which configures VS Code to open all three folders together.

---

## Directory Structures (2 Levels Deep)

### sf-quality-db (Database)

```
sf-quality-db/
├── .git/
├── .github/workflows/                 # SQL validation, enforcement governance
├── .planning/                         # GSD planning artifacts
│   ├── codebase/                      #   Architecture, conventions, concerns docs
│   ├── config.json                    #   GSD workflow toggles
│   ├── contracts/                     #   db-contract-manifest.json (80 procs, 36 views)
│   ├── enforcement/                   #   Enforcement registry
│   ├── milestones/                    #   Milestone tracking
│   ├── phases/                        #   Phase planning (21+ phases)
│   ├── research/                      #   Research notes
│   ├── STATE.md / ROADMAP.md / PROJECT.md / REQUIREMENTS.md
├── database/
│   ├── archive/                       # Historical baselines
│   ├── deploy/                        # 67 PowerShell deploy/validation scripts
│   └── migrations/                    # 136 SQL migration files (source of truth)
├── docs/                              # Briefs, decisions, walkthroughs, standards, LPCS
│   ├── briefs/
│   ├── database-architecture/
│   ├── decisions/
│   ├── defect-knowledge-expansion/
│   ├── defect-taxonomy-v3/
│   ├── deliverables/
│   ├── evidence/
│   ├── handoffs/
│   ├── LPCS/
│   ├── Milestone v1.1/
│   ├── milestones/
│   ├── phases/
│   ├── project/
│   ├── research/
│   ├── standards/
│   ├── topology-expansion-handoff/
│   └── walkthroughs/
├── scripts/                           # Cross-repo validation scripts
├── AGENTS.md / CLAUDE.md / README.md
└── *.xlsx, *.ps1                      # Taxonomy workbooks, utility scripts
```

### sf-quality-api (API)

```
sf-quality-api/
├── .git/
├── .github/workflows/                 # Contract validation pipeline
├── .planning/                         # Planning artifacts
│   ├── codebase/                      #   Architecture docs
│   ├── contracts/                     #   db-contract-manifest.snapshot.json
│   │                                  #   api-openapi.publish.json
│   ├── decisions/                     #   ADRs
│   ├── phases/                        #   Phase planning (5/30 plans complete)
│   │   ├── 01-foundation-infrastructure/
│   │   ├── 02-lookups-reference-data/
│   │   ├── 03-ncr-lifecycle/
│   │   ├── 04-capa-complaint/
│   │   ├── 05-scar-audit-eightd/
│   │   ├── 06-rca-tools/
│   │   ├── 07-workflow-action-items/
│   │   ├── 08-knowledge-traceability/
│   │   ├── 09-dashboards-views/
│   │   └── 10-integration-deployment/
│   └── research/
├── docs/
├── scripts/                           # Cross-repo validation scripts
│   ├── Install-GitHooks.ps1
│   ├── Invoke-CycleChecks.ps1
│   ├── Test-DbContractReferences.ps1
│   ├── Test-OpenApiPublication.ps1
│   └── Test-PlanningConsistency.ps1
├── src/
│   └── SfQualityApi/                  # ASP.NET Core 9 project
│       ├── Auth/                      #   EasyAuthHandler
│       ├── Endpoints/                 #   NcrEndpoints.cs, DiagnosticEndpoints.cs
│       ├── Infrastructure/            #   DbConnectionFactory, SqlErrorMapper
│       ├── Middleware/                 #   CorrelationId, ErrorHandling
│       ├── Properties/
│       ├── appsettings.json
│       ├── appsettings.Development.json
│       ├── Program.cs
│       └── SfQualityApi.csproj
├── SfQualityApi.sln                   # Visual Studio solution file
├── AGENTS.md / CLAUDE.md / README.md
```

### sf-quality-app (Frontend)

```
sf-quality-app/
├── .git/
├── .github/workflows/                 # Planning contract validation
├── .planning/                         # Planning artifacts
│   ├── codebase/                      #   Architecture, conventions, concerns docs
│   │   ├── ARCHITECTURE.md
│   │   ├── CONCERNS.md
│   │   ├── CONVENTIONS.md
│   │   ├── INTEGRATIONS.md
│   │   ├── STACK.md
│   │   ├── STRUCTURE.md
│   │   └── TESTING.md
│   ├── config.json                    #   GSD workflow toggles
│   ├── contracts/                     #   api-openapi.snapshot.json
│   ├── decisions/                     #   ADRs
│   │   └── ADR-0001-frontend-platform-auth-boundary.md
│   ├── phases/                        #   Phase planning (0/2 plans, Phase 1 of 10)
│   │   ├── 01-frontend-foundation/
│   │   ├── 02-design-system-shell/
│   │   ├── 03-easy-auth-session/
│   │   ├── 04-lookup-driven-forms/
│   │   ├── 05-ncr-lifecycle-ux/
│   │   ├── 06-domain-workspaces/
│   │   ├── 07-workflow-approvals/
│   │   ├── 08-knowledge-traceability-ux/
│   │   ├── 09-dashboards-views/
│   │   └── 10-deployment-e2e-governance/
│   ├── research/                      #   ARCHITECTURE.md, FEATURES.md, PITFALLS.md, etc.
│   ├── STATE.md / ROADMAP.md / PROJECT.md / REQUIREMENTS.md
├── docs/
├── scripts/                           # Cross-repo validation scripts
│   ├── Install-GitHooks.ps1
│   ├── Invoke-CycleChecks.ps1
│   ├── Test-ApiContractReferences.ps1
│   └── Test-PlanningConsistency.ps1
├── AGENTS.md / CLAUDE.md / README.md
```

> **Note:** sf-quality-app has no `src/`, `package.json`, or `node_modules` yet. All architecture, stack, and governance decisions are locked; source scaffolding begins in Phase 1.

---

## Languages and Frameworks

| Repo | Primary Language | Framework | Key Dependencies |
|------|-----------------|-----------|-----------------|
| **sf-quality-db** | T-SQL (SQL Server) | None (raw migrations) | PowerShell (deploy/validation scripts) |
| **sf-quality-api** | C# | ASP.NET Core 9.0 | Dapper 2.1, Microsoft.Data.SqlClient, Serilog, Polly (resilience), Scalar (API docs) |
| **sf-quality-app** | TypeScript (planned) | Next.js 15 / React 19 | shadcn/ui, TanStack Query/Table, Tailwind CSS 4, zod, react-hook-form, recharts |

### Supporting Languages

- **PowerShell** — Deployment scripts, validation tooling, Git hooks (all 3 repos)
- **Python** — Single utility script (`database/deploy/Generate-DatabaseArchitectureSpec.py` in sf-quality-db)
- **YAML** — GitHub Actions CI/CD workflows (all 3 repos)
- **Markdown** — Extensive planning, architecture, and governance docs (all 3 repos)

---

## Shared Config and Resources at Root Level

| File / Folder | Purpose |
|---------------|---------|
| `sf-quality.code-workspace` | VS Code workspace linking all 3 folders with shared settings |
| `Reference_Architecture/` | Single source of truth for architecture patterns, gap analysis, and cross-repo execution plan |

There is **no** `package.json`, `docker-compose.yml`, `Dockerfile`, or any other shared config at the root. Each repo manages its own configuration independently.

---

## Cross-Repo Dependencies and Contracts

The three repos are connected via a **contract governance chain**, not shared code or npm packages.

### Contract Flow

```
sf-quality-db                    sf-quality-api                   sf-quality-app
─────────────                    ──────────────                   ──────────────
db-contract-manifest.json   →    db-contract-manifest.snapshot    (indirect only)
(80 procs, 36 views)             api-openapi.publish.json    →   api-openapi.snapshot.json
```

### How It Works

1. **sf-quality-db** publishes a contract manifest listing all stored procedures and views
2. **sf-quality-api** pins a snapshot of the DB manifest and validates that it only references objects in that manifest; it then publishes its own OpenAPI spec
3. **sf-quality-app** pins a snapshot of the API's OpenAPI spec and validates that it only calls documented endpoints

### Cross-Repo Validation

Each repo has `scripts/Invoke-CycleChecks.ps1` which validates contract consistency across all three siblings. GitHub Actions workflows enforce these checks on PRs.

### Shared Governance Patterns

All three repos share:
- `.planning/` directory structure with STATE.md, ROADMAP.md, PROJECT.md, REQUIREMENTS.md
- `AGENTS.md` and `CLAUDE.md` for AI agent governance
- `.planning/config.json` for GSD workflow toggles
- `.planning/contracts/` for contract artifacts
- `scripts/` for PowerShell validation tooling
- `.github/workflows/` for CI/CD pipelines

---

## Database Management

**Strategy:** Raw SQL migration files with PowerShell deployment scripts — no ORM for schema management.

| Aspect | Detail |
|--------|--------|
| **Migration files** | `database/migrations/` — 136 numbered SQL files (`001_schemas.sql` through `132+`) |
| **Migration style** | Additive, immutable history with `IF EXISTS`/`IF NOT EXISTS` guards |
| **Naming convention** | 3-digit prefix + snake_case (e.g., `020_seed_defects.sql`) |
| **Deploy scripts** | `database/deploy/` — 67 PowerShell scripts (per-phase and full-apply) |
| **Shared module** | `Deploy-Common.ps1` — dot-sourced by all phase apply scripts |
| **Verify/Smoke** | `Verify-Phase*.sql` and `Smoke-Phase*.sql` — post-deploy verification and smoke test SQL |
| **Validation** | `Test-SqlStaticRules.ps1` (static analysis), `Test-NcrOperationalParity.ps1` |
| **Dry run** | All deploy scripts support `-WhatIf` for non-destructive validation |
| **Database objects** | 80 stored procedures (`usp_*`), 36 views (`vw_*`) |
| **Schemas** | dbo, quality, rca, workflow, security, integration, ref, meta, audit |

**API data access** uses **Dapper** (lightweight micro-ORM) to call stored procedures — no Entity Framework, no LINQ-to-SQL. The API acts as a thin pass-through to database logic.

### Azure SQL Environments

| Environment | Server | Database |
|-------------|--------|----------|
| Dev | `sql-sf-quality-0b1f-dev.database.windows.net` | `sqldb-quality-core-dev` |
| Staging | `sql-sf-quality-0b1f-staging.database.windows.net` | `sqldb-quality-core-staging` |
| Prod | `sql-sf-quality-0b1f-dev.database.windows.net` | `sqldb-quality-core-prod` |
| Clean | `sql-sf-quality-0b1f-dev.database.windows.net` | `sqldb-quality-core-clean` |

---

## Deployment Setup

**Each repo deploys independently.** There is no shared deployment pipeline or orchestrated release.

| Repo | Hosting | Deployment Method |
|------|---------|-------------------|
| **sf-quality-db** | Azure SQL Database | PowerShell scripts (`Apply-Phase*.ps1`, `Apply-Full.ps1`) |
| **sf-quality-api** | Azure App Service (C#) | Manual / CI (dotnet publish) |
| **sf-quality-app** | Azure App Service (Node.js) | Not yet deployed (planning phase) |

### Authentication Architecture

- **Azure App Service Easy Auth** (Entra ID, single-tenant) provides the authentication boundary
- API reads `X-MS-CLIENT-PRINCIPAL` header from Easy Auth, extracts Azure AD Object ID
- API calls `dbo.usp_SetSessionContext(@CallerAzureOid)` on each connection for SQL row-level security
- Frontend will forward delegated tokens via `X-MS-TOKEN-AAD-ACCESS-TOKEN` server-side

### CI/CD Pipelines (GitHub Actions)

| Repo | Workflow | Purpose |
|------|----------|---------|
| **sf-quality-db** | `sql-validation.yml` | Static SQL checks, deploy to CI DB, run verify/smoke |
| **sf-quality-db** | `enforcement-governance.yml` | Enforcement registry checks |
| **sf-quality-api** | `planning-contract-validation.yml` | DB contract + OpenAPI validation |
| **sf-quality-app** | `planning-contract-validation.yml` | API contract + planning consistency |

---

## Project Maturity

| Repo | Status | Phases Shipped |
|------|--------|---------------|
| **sf-quality-db** | Production (v1.0 complete, v1.1 in progress) | 21+ phases |
| **sf-quality-api** | Early development (Phase 2 of ~30 complete) | 2 phases |
| **sf-quality-app** | Pre-development (planning only) | 0 phases |

---

## Quick Reference

```
sf-quality (workspace root)
│
├── sf-quality-db     T-SQL + PowerShell    Azure SQL         Production
├── sf-quality-api    C# / ASP.NET Core 9   Azure App Service Early dev
└── sf-quality-app    TypeScript / Next.js   Azure App Service Planning only
                      (planned)
```

**Architecture:** Contract-first, stored-procedure-driven backend with a thin API gateway and a React frontend. All business logic lives in the database. The API is a pass-through. The frontend consumes the API only.
