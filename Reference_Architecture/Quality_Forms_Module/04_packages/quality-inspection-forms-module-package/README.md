# Quality Inspection Forms Module — Architecture Package

This folder is a **complete packaged export** of the Quality Inspection Forms module design for **sf-quality**.

## Current Status (2026-02-22)

Implementation is **blocked** pending closure of authoritative pre-build items in:
- `Reference_Architecture/Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md`

It contains:
- DB schema migrations (`db/migrations/*.sql`)
- Detailed stored procedure contracts (`docs/02_stored_procedure_contracts.md`)
- API endpoint design (`docs/03_api_endpoint_design.md`)
- Frontend architecture (builder + operator fill) (`docs/04_frontend_form_builder_architecture.md`)
- Integration architecture & diagrams (`docs/05_integration_architecture.md`)
- Phasing plan (`docs/06_phasing_recommendation.md`)
- The verbatim **CODEBASE_REFERENCE.md** used as the compatibility baseline (`reference/`)

> **Important:** Migration numbers in this package start at **131** because the reference shows the current highest shipped migration is `130_*`. If additional migrations have landed since, **renumber forward** (do not overwrite history).

---

## Folder Structure

```
quality-inspection-forms-module-package/
├─ README.md
├─ index.md
├─ docs/
│  ├─ 00_key_decisions.md
│  ├─ 01_database_schema_design.md
│  ├─ 02_stored_procedure_contracts.md
│  ├─ 03_api_endpoint_design.md
│  ├─ 04_frontend_form_builder_architecture.md
│  ├─ 05_integration_architecture.md
│  ├─ 06_phasing_recommendation.md
│  └─ 07_open_questions_and_todos.md
├─ db/
│  └─ migrations/
│     ├─ 131_create_inspection_schema.sql
│     ├─ ...
│     └─ 160_seed_workflow_inspection.sql
├─ api/
│  └─ README.md
├─ app/
│  └─ README.md
└─ reference/
   └─ CODEBASE_REFERENCE.md
```

---

## Quick Start

0. **Preflight gate (required)**
   - Review and close the "Implementation Start Criteria" checklist in:
     - `Reference_Architecture/Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md`
   - Do not execute package migrations until the checklist is green.

1. **Read the baseline reference**
   - `reference/CODEBASE_REFERENCE.md`

2. **Read the design documents**
   - Start at `index.md` → then follow the docs in order.

3. **DB implementation path**
   - Apply the corrected migration set in order after blocker closure (renumber from live highest migration at execution time).
   - Then implement stored procedures per `docs/02_stored_procedure_contracts.md`.

4. **API implementation path**
   - Implement endpoints per `docs/03_api_endpoint_design.md` using the existing Minimal API + Dapper patterns.

5. **App implementation path**
   - Build `sf-quality-app` using the component hierarchy and query/mutation patterns in `docs/04_frontend_form_builder_architecture.md`.

---

## Notes on Compatibility

- Business logic remains in **T-SQL stored procedures** (API stays thin).
- Row-level security remains enforced via `dbo.usp_SetSessionContext(@CallerAzureOid)` + RLS predicates.
- Response storage is **strongly typed** (no generic `FieldName/FieldValue` EAV table).
- API endpoint surface should be versioned under `/v1`.
- Approval-required workflow outcomes should follow `50414 -> 202 Accepted` semantics (some frozen reference snapshots may still show legacy `403` mapping).

See `docs/07_open_questions_and_todos.md` for reconciled live-validation outcomes plus remaining implementation/configuration tasks.
