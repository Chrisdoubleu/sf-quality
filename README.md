# sf-quality

A quality management system for Select Finishing, built as three independent Git repositories connected by contract-based governance. The database owns all business logic via stored procedures, the API is a thin HTTP pass-through, and the frontend consumes the API exclusively. Repos are linked by a VS Code workspace file and validated by a cross-repo contract chain.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Git | 2.x+ | Source control |
| VS Code | Latest | IDE (with multi-folder workspace) |
| PowerShell | 7+ | Deploy scripts, validation, Git hooks |
| .NET SDK | 9.0 | API development (`sf-quality-api`) |
| Node.js | 22 LTS | Frontend development (`sf-quality-app`, when scaffolded) |
| Azure Data Studio or SSMS | Latest | Database inspection and ad-hoc queries |
| Azure CLI | Latest | Deployment and environment access |

## Clone and Setup

```bash
git clone https://github.com/Chrisdoubleu/sf-quality.git
cd sf-quality
pwsh Setup.ps1
```

`Setup.ps1` clones all three child repos and installs their Git hooks. Then open `sf-quality.code-workspace` in VS Code — all three repos will appear as workspace folders (Database, API, Frontend).

## Repo Responsibilities

| Repo | Owns | Tech Stack | Status |
|------|------|-----------|--------|
| **sf-quality-db** | Schema, stored procedures, views, RLS, workflow gates | T-SQL, PowerShell | Active (v1.0 shipped, v1.1 shipped 2026-02-17, v2.0 active — Phase 21.1 complete, Phase 23 next) |
| **sf-quality-api** | HTTP endpoints, auth boundary, SQL error mapping | C# / ASP.NET Core 9, Dapper | Early development (Phase 2 of 10) |
| **sf-quality-app** | UI, forms, dashboards, user workflows | TypeScript / Next.js 15, React 19 | Planning (no source yet) |

## Contract Governance

The three repos stay in sync via a publish-and-snapshot contract chain:

```
sf-quality-db                      sf-quality-api                     sf-quality-app
──────────────                     ──────────────                     ──────────────
db-contract-manifest.json    →     db-contract-manifest.snapshot      (indirect only)
(80 procs, 36 views)               api-openapi.publish.json     →    api-openapi.snapshot.json
```

1. **db** publishes a manifest of all stored procedures and views
2. **api** snapshots the db manifest, validates references, and publishes an OpenAPI spec
3. **app** snapshots the API's OpenAPI spec and validates endpoint references

To validate cross-repo consistency from any repo:

```powershell
pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly
```

## Environment Setup

Four Azure SQL environments are configured in `sf-quality-db/database/deploy/deploy-config.json`:

| Environment | Purpose |
|-------------|---------|
| **dev** | Active development and testing |
| **staging** | Pre-production validation |
| **prod** | Production |
| **clean** | Baseline reference (empty schema) |

Connection details (server names, database names) are in the deploy config. Credentials are managed via Azure AD authentication — no passwords are stored in the repos.

## Development Workflow

Changes flow downstream through the contract chain:

1. **Schema first** — make database changes in `sf-quality-db`, run migrations, update the contract manifest
2. **API second** — update the db contract snapshot in `sf-quality-api`, add/modify endpoints, publish the OpenAPI spec
3. **Frontend third** — update the API contract snapshot in `sf-quality-app`, build the UI

When an upstream repo changes its contract, downstream repos must update their pinned snapshots and re-run cycle checks.

## Deployment

Each repo deploys independently. There is no shared deployment pipeline.

| Repo | Method | Details |
|------|--------|---------|
| **sf-quality-db** | PowerShell scripts to Azure SQL | See `sf-quality-db/README.md` |
| **sf-quality-api** | .NET publish to Azure App Service | See `sf-quality-api/README.md` |
| **sf-quality-app** | Node.js to Azure App Service | See `sf-quality-app/README.md` (not yet deployed) |

## Reference Architecture

The `Reference_Architecture/` folder at workspace root contains platform-agnostic architectural patterns reverse-engineered from a production enterprise platform, mapped to sf-quality's implementation gaps. See [Reference_Architecture/README.md](Reference_Architecture/README.md) for the full index.

| Document | Description |
|----------|-------------|
| [Execution_Plan.md](Reference_Architecture/Execution_Plan.md) | 46 patterns translated into GSD phases across all 3 repos |
| [Pattern_Mapping.md](Reference_Architecture/Pattern_Mapping.md) | Gap audit: 46 patterns vs. current implementation |
| [Specs/](Reference_Architecture/Specs/) | 4 platform-agnostic JSON architecture specifications |
| [Briefings/](Reference_Architecture/Briefings/) | Narrative orientation documents |
| [Hidden_Patterns/](Reference_Architecture/Hidden_Patterns/) | 3 reverse-engineered implicit patterns |

This folder is the single source of truth — child repos reference it via relative paths, not copies.

## AI Agent Governance

Each repo contains `AGENTS.md` and `CLAUDE.md` files that define rules for how coding agents (Claude, Cursor, etc.) interact with the codebase — including SQL validation requirements, planning closeout contracts, and enforcement registries. Agents must read these files before making changes.
