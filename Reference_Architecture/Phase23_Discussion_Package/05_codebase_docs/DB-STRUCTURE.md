# Codebase Structure

**Analysis Date:** 2026-02-22

## Directory Layout

```
sf-quality-db/
├── .claude/                # Claude Code configuration
├── .github/workflows/      # CI/CD pipelines
├── .planning/              # Roadmap, requirements, phase plans
│   ├── codebase/           # Codebase mapping documents
│   ├── enforcement/        # Enforcement registry and validation
│   ├── milestones/         # Milestone tracking (v1.0, v1.1)
│   ├── phases/             # Phase-by-phase planning artifacts (01-24 currently present)
│   └── research/           # Research outputs
├── .vscode/                # VS Code settings
├── database/               # Database source code (migrations + deployment)
│   ├── archive/            # Historical baseline (phase00)
│   ├── deploy/             # Deployment scripts and validation
│   │   ├── output/         # Generated reports
│   │   └── reports/        # Validation reports
│   └── migrations/         # Migration SQL files (001-130 + suffix forward-fixes)
├── docs/                   # Documentation root
│   ├── briefs/             # Analysis briefs
│   ├── database-architecture/  # YAML schema references
│   ├── database-audit/     # Automated schema snapshots
│   ├── decisions/          # Architecture Decision Records
│   ├── deliverables/       # Milestone deliverables
│   ├── handoffs/           # Handoff packages
│   ├── milestones/         # Milestone authority documents
│   ├── phases/             # Legacy phase documentation
│   ├── project/            # Canonical project narrative
│   ├── research/           # Research artifacts
│   ├── standards/          # Documentation standards
│   ├── topology-expansion-handoff/  # Historical topology package
│   └── walkthroughs/       # Domain walkthroughs
├── AGENTS.md               # Agent execution contract
├── CHANGELOG.md            # Change log
├── CONTRIBUTING.md         # Contributor guide
└── README.md               # Project overview
```

## Directory Purposes

**.planning/**
- Purpose: Planning and execution artifacts for GSD workflow
- Contains: Roadmap, requirements, phase plans, summaries, verification, enforcement registry
- Key files: `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `enforcement/ENFORCEMENT-REGISTRY.json`

**.planning/phases/**
- Purpose: Phase-specific planning artifacts organized by phase number
- Contains: Subdirectories for each phase (01-17+), each with CONTEXT, RESEARCH, PLAN, SUMMARY, VERIFICATION files
- Key files: `{NN}-CONTEXT.md`, `{NN}-RESEARCH.md`, `{NN}-{PP}-PLAN.md`, `{NN}-{PP}-SUMMARY.md`, `{NN}-VERIFICATION.md`

**.planning/codebase/**
- Purpose: Codebase mapping documents for GSD commands
- Contains: Architecture, structure, conventions, testing, stack, integrations, concerns
- Key files: `ARCHITECTURE.md`, `STRUCTURE.md` (this file)

**database/migrations/**
- Purpose: Immutable migration history (source of truth for schema evolution)
- Contains: SQL migration files numbered 001-130 (plus suffix forward-fixes; additive-only, no edits after deployment)
- Key files: `001_schemas.sql` (7 schemas), `028_ncr_tables.sql` (NCR entity), `046_workflow_state_machine.sql` (workflow), `058_crud_ncr_capa.sql` (CRUD SPs), `112_gate_create_submit.sql` through `118_gate_edge_transitions.sql` (gate SP suite), `128_knowledge_retrieval_layer.sql`, `129_rootcause_hypothesis_contracts.sql`, `130_defect_taxonomy_v3_cleanup.sql`

**database/deploy/**
- Purpose: Deployment orchestration and validation scripts
- Contains: PowerShell deployment scripts (Apply-Phase*.ps1), verification SQL (Verify-Phase*.sql), smoke tests (Smoke-Phase*.sql), validation utilities
- Key files: `Deploy-Common.ps1` (shared functions), `Apply-Phase21.ps1` and `Apply-Phase21-1.ps1` (latest v2.0 deployment scripts), `Test-SqlStaticRules.ps1`, `Test-EnforcementRegistry.ps1`, `deploy-config.json` (environment configuration)

**database/deploy/output/**
- Purpose: Generated reports and artifacts
- Contains: Defect walkthrough exports, paint defect analysis
- Key files: Paint defect walkthrough workbooks

**docs/project/**
- Purpose: Canonical project narrative and phase dossiers
- Contains: Project system overview, phase compendium, traceability matrix, v1.0/v1.1 phase dossiers
- Key files: `PROJECT-SYSTEM-OVERVIEW.md`, `phases/PHASES-AND-FEATURES-COMPENDIUM.md`, `phases/TRACEABILITY-MATRIX.md`

**docs/handoffs/**
- Purpose: Handoff packages for milestone transitions
- Contains: Phase 12 decision closeout, Phase 14 role security, production topology, quality disposition agent package
- Key files: `phase-12-decision-closeout-package/`, `Role Security/phase14-role-security-consolidated-v2.md`, `production-topology/`, `quality-disposition-agent-package/`

**docs/milestones/**
- Purpose: Milestone authority index and documentation
- Contains: v1.0 and v1.1 milestone documentation
- Key files: `README.md`, `v1.0-ROADMAP.md`, `v1.1/README.md`

**docs/decisions/**
- Purpose: Architecture Decision Records (ADRs)
- Contains: Decision log for design choices
- Key files: `README.md` (ADR index)

**.github/workflows/**
- Purpose: CI/CD pipelines
- Contains: SQL validation workflow, enforcement governance workflow
- Key files: `sql-validation.yml`, `enforcement-governance.yml`

## Key File Locations

**Entry Points:**
- `README.md`: Project overview and quick start
- `database/deploy/Apply-Phase21.ps1`: Current v2.0 retrieval-layer deploy script
- `database/deploy/Apply-Phase21-1.ps1`: Phase 21.1 taxonomy v3 deploy script
- `database/deploy/Apply-Full.ps1`: full-chain install orchestration
- `.planning/PROJECT.md`: project summary and requirements

**Configuration:**
- `database/deploy/deploy-config.json`: Environment configuration (dev, staging, prod server/database)
- `.planning/config.json`: GSD workflow toggles (research, plan_check, verifier)
- `.planning/enforcement/ENFORCEMENT-REGISTRY.json`: Enforcement rules registry

**Core Logic:**
- `database/migrations/001_schemas.sql`: 7-schema model
- `database/migrations/006_rls_predicates.sql`: RLS filter and block predicates
- `database/migrations/007_session_context_sp.sql`: Session context initialization SP
- `database/migrations/046_workflow_state_machine.sql`: Workflow state machine tables
- `database/migrations/061_workflow_transition_sp.sql`: Central workflow transition SP
- `database/migrations/058_crud_ncr_capa.sql`: NCR/CAPA CRUD SPs
- `database/migrations/091_create_security_catalog.sql`: Permission catalog
- `database/migrations/096_create_policy_engine_sps.sql`: Policy engine SPs
- `database/migrations/112_gate_create_submit.sql` through `118_gate_edge_transitions.sql`: 18 gate SPs
- `database/migrations/125_defect_knowledge_schema.sql` through `130_defect_taxonomy_v3_cleanup.sql`: v2.0 knowledge and taxonomy hardening chain

**Testing:**
- `database/deploy/Verify-Phase01.sql` through `Verify-Phase21.sql`: Verification queries
- `database/deploy/Smoke-Phase07.sql` through `Smoke-Phase21.sql`: Smoke tests
- `database/deploy/Test-SqlStaticRules.ps1`: Static analysis
- `database/deploy/Test-EnforcementRegistry.ps1`: Enforcement validation
- `database/deploy/Test-NcrOperationalParity.ps1`: Parity checker

## Naming Conventions

**Files:**
- Migrations: `{NNN}_{descriptive_name}.sql` (e.g., `001_schemas.sql`, `028_ncr_tables.sql`)
- Deployment scripts: `Apply-Phase{NN}-Plan{PP}.ps1` or `Apply-Phase{NN}.ps1` for consolidated
- Verification: `Verify-Phase{NN}.sql`
- Smoke tests: `Smoke-Phase{NN}.sql`
- Planning: `{NN}-{PP}-PLAN.md`, `{NN}-{PP}-SUMMARY.md`, `{NN}-VERIFICATION.md`

**Directories:**
- Phase directories: `{NN}-{kebab-case-description}` (e.g., `01-infrastructure-security`, `15-gate-stored-procedures`)
- Lowercase with hyphens for multi-word directories (`.planning/phases/`, `docs/database-architecture/`)

**SQL Objects:**
- Tables: `PascalCase` with `Id` suffix for primary keys (e.g., `NonConformanceReport`, `NonConformanceReportId`)
- Stored procedures: `usp_{PascalCaseAction}` (e.g., `usp_CreateNCR`, `usp_TransitionState`)
- Gate SPs: `usp_Gate_{PascalCaseAction}` (e.g., `usp_Gate_CreateNCR`, `usp_Gate_ProcessDisposition`)
- Views: `vw_{PascalCaseDescription}` (e.g., `vw_OpenNCRSummary`, `vw_EffectivenessResults`)
- Functions: `fn_{PascalCaseDescription}` (e.g., `fn_PlantAccessPredicate`)
- Schemas: lowercase (dbo, quality, rca, workflow, apqp, security, audit)
- No `LU_` or `JN_` prefixes (legacy pattern, not used)

## Where to Add New Code

**New Migration:**
- Primary code: `database/migrations/{NNN}_{descriptive_name}.sql`
- Tests: `database/deploy/Verify-Phase{NN}.sql`, `database/deploy/Smoke-Phase{NN}.sql`
- Deployment: `database/deploy/Apply-Phase{NN}-Plan{PP}.ps1` or add to consolidated `Apply-Phase{NN}.ps1`
- Planning: `.planning/phases/{NN}-{phase-name}/{NN}-{PP}-PLAN.md`

**New Stored Procedure:**
- Implementation: Add to migration file in `database/migrations/` (e.g., `058_crud_ncr_capa.sql` for CRUD SPs, `112_gate_create_submit.sql` for gate SPs)
- Pattern: `CREATE OR ALTER PROCEDURE {schema}.{usp_Name}` with `@CallerAzureOid` as first parameter, `SET XACT_ABORT ON; BEGIN TRY ... END TRY BEGIN CATCH ... ;THROW END CATCH` wrapper
- Verification: Add to `Verify-Phase{NN}.sql` (e.g., check SP exists, parameter count)
- Smoke test: Add to `Smoke-Phase{NN}.sql` (e.g., call SP with test data, verify result, rollback)

**New Table:**
- Implementation: Add to migration file in `database/migrations/`
- Pattern: Create history table FIRST in `audit` schema with clustered columnstore, then create current table with `SYSTEM_VERSIONING = ON`, add RLS predicates if plant-scoped, add audit trigger via `dbo.usp_CreateAuditTrigger`
- Dependencies: Ensure FK targets exist from prior migrations
- Verification: Add to `Verify-Phase{NN}.sql` (e.g., table exists, column count, temporal versioning enabled, RLS policy enrolled)

**New View:**
- Implementation: Add to migration file in `database/migrations/` (e.g., `067_dashboard_views.sql`, `068_kpi_analytics_views.sql`)
- Pattern: `CREATE OR ALTER VIEW {schema}.vw_{Name} AS SELECT ...` (no WITH SCHEMABINDING for dashboard views, RLS-transparent)
- Verification: Add to `Verify-Phase{NN}.sql` (view exists, column check)

**New Deployment Validation:**
- Static rules: Add to `database/deploy/Test-SqlStaticRules.ps1`
- Enforcement rule: Add to `.planning/enforcement/ENFORCEMENT-REGISTRY.json`
- CI workflow: Update `.github/workflows/sql-validation.yml` if needed

**Utilities:**
- Shared helpers: `database/deploy/Deploy-Common.ps1` (PowerShell functions for deployment)
- Validation scripts: `database/deploy/Test-*.ps1`

## Special Directories

**database/archive/phase00/**
- Purpose: Historical baseline (never deployed, prototype only)
- Generated: No
- Committed: Yes
- Note: `001_quality_backend_baseline.sql` is a legacy artifact, NOT part of migration history

**database/deploy/output/**
- Purpose: Generated reports and analysis artifacts
- Generated: Yes (via `Export-DefectWalkthrough.ps1`, `Build-DefectWalkthroughWorkbook.ps1`)
- Committed: No (excluded via `.gitignore` for large binaries)

**database/deploy/reports/**
- Purpose: Validation reports
- Generated: Yes (via deployment scripts)
- Committed: No

**docs/database-audit/**
- Purpose: Automated schema snapshots from live database
- Generated: Yes (via Azure SQL export scripts)
- Committed: Yes (timestamped snapshots for schema drift detection)

**docs/handoffs/**
- Purpose: Milestone handoff packages (ZIP archives + extracted directories)
- Generated: Yes (via phase closeout process)
- Committed: Yes (both ZIP and extracted for searchability)

**.planning/phases/{NN}-{phase-name}/**
- Purpose: Phase-specific planning artifacts
- Generated: Yes (via GSD commands: `/gsd:plan-phase`, `/gsd:execute-phase`)
- Committed: Yes
- Pattern: Each phase has CONTEXT.md (research input), RESEARCH.md (analysis), optional ASSUMPTIONS files, {PP}-PLAN.md (execution plan), {PP}-SUMMARY.md (execution summary), VERIFICATION.md (success criteria)

**docs/Milestone v1.1/**
- Purpose: v1.1 milestone deliverables and deep-dive reports
- Generated: Yes (via milestone closeout)
- Committed: Yes

## Migration Immutability Policy

**Critical Rule:** Migrations 001-086 are immutable. Never edit after deployment.

**Forward-Fix Pattern:**
- If bug found in deployed migration, create new migration with suffix (e.g., `086a_fix_audit_trigger_rowversion.sql`)
- Update utility SPs via `CREATE OR ALTER` in new migration
- Preserve audit trail by keeping original migration intact

**Examples:**
- `056_update_audit_trigger_utility.sql` → `086a_fix_audit_trigger_rowversion.sql` (forward-fix for ROWVERSION exclusion)
- `070_fix_statuscode_column_references.sql` (forward-fix for StatusCode column name bugs)

## RLS Policy Rebuild Pattern

**When modifying RLS predicates:**
1. `DROP SECURITY POLICY security.PlantIsolationPolicy;`
2. `CREATE OR ALTER FUNCTION security.fn_PlantAccessPredicate ...`
3. `CREATE OR ALTER FUNCTION security.fn_PlantWriteBlockPredicate ...`
4. Recreate policy with all table bindings

**When adding new plant-scoped tables:**
1. Save existing policy predicates to temp table
2. DROP policy
3. CREATE tables
4. Recreate policy with saved predicates + new table predicates
5. DELETE new tables from temp table before cursor loop (prevent duplication on re-run)

**Example:** `database/migrations/090_ncr_notes_hold_locations.sql`

## Deployment Artifacts Pattern

**Each phase produces:**
- `Apply-Phase{NN}-Plan{PP}.ps1`: Deployment orchestration script
- `Verify-Phase{NN}.sql`: Verification queries (counts, existence checks, FK validation)
- `Smoke-Phase{NN}.sql`: End-to-end smoke tests (SP calls with rollback)

**Consolidated deployment pattern:**
- Later phases use single `Apply-Phase{NN}.ps1` that includes all sub-plans
- Example: `Apply-Phase21.ps1` deploys v2.0 retrieval-layer migrations and runs verify/smoke stages

**Batch splitting:**
- GO delimiter splits SQL into batches
- PowerShell regex: `(?im)^[\t ]*GO[\t ]*(?:--.*)?\r?$`
- Cast result with `ForEach-Object { [string]$_ }` to avoid `[char]` type issues

---

*Structure analysis: 2026-02-22*
