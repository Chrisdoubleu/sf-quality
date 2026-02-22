# GSD Operations Dashboard

**Purpose:** Keep one live operational view across DB, API, and App so phase work does not drift from the contract chain.

**How to use:** Update this file before and after every `/gsd:discuss-phase`, `/gsd:plan-phase`, `/gsd:execute-phase`, and `/gsd:verify-work`.

---

## 1) Current Snapshot


| Area                | Current State                                     | Last Updated |
| ------------------- | ------------------------------------------------- | ------------ |
| `sf-quality-db`     | v2.0 in progress, Phase 23 next, v3.0 not started | 2026-02-22   |
| `sf-quality-api`    | Phase 3 complete, Phase 3.5 next                  | 2026-02-22   |
| `sf-quality-app`    | Phase 1 not started                               | 2026-02-22   |
| Quality Forms track | No-go until Section H gates are green             | 2026-02-22   |


---

## 2) Cross-Repo Gate Ledger

Mark each gate `READY` only after the producer repo phase is executed, verified, and its contract artifact is refreshed/published.


| Gate ID         | Producer Phase            | Consumer Phase                   | Required Artifact                                                      | Status  | Verified On | Notes |
| --------------- | ------------------------- | -------------------------------- | ---------------------------------------------------------------------- | ------- | ----------- | ----- |
| GATE-DB29-API35 | DB Phase 29               | API Phase 3.5                    | `db-contract-manifest.json` refreshed with `audit.ApiCallLog`          | BLOCKED | -           |       |
| GATE-DB29-API4  | DB Phase 29               | API Phase 4                      | DB proc contract includes temporal/query support used by API           | BLOCKED | -           |       |
| GATE-DB31-API5  | DB Phase 31               | API Phase 5                      | `db-contract-manifest.json` refreshed with SCAR party status contract  | BLOCKED | -           |       |
| GATE-DB32-API7  | DB Phase 32               | API Phase 7                      | `db-contract-manifest.json` refreshed with validate-only contracts     | BLOCKED | -           |       |
| GATE-DB28-API7  | DB Phase 28               | API Phase 7+                     | `db-contract-manifest.json` refreshed with notification queue contract | BLOCKED | -           |       |
| GATE-API4-APP4  | API Phase 4+              | App Phase 4+                     | OpenAPI published and app snapshot refreshed                           | BLOCKED | -           |       |
| GATE-QF-ENTRY   | Core gates + QF checklist | QF DB Phase 34 / API 11 / App 11 | All Section H entry checks green                                       | BLOCKED | -           |       |


---

## 3) Phase Readiness Board

Use this before opening any phase.


| Repo | Phase | Context Ready | Dependencies Ready | Discuss Done | Plan Done | Execute Done | Verify Done | Blockers |
| ---- | ----- | ------------- | ------------------ | ------------ | --------- | ------------ | ----------- | -------- |
| DB   | 23    | YES           | YES                | NO           | NO        | NO           | NO          |          |
| DB   | 24    | NO            | NO                 | NO           | NO        | NO           | NO          |          |
| DB   | 29    | NO            | NO                 | NO           | NO        | NO           | NO          |          |
| API  | 3.5   | NO            | NO                 | NO           | NO        | NO           | NO          |          |
| APP  | 3     | NO            | NO                 | NO           | NO        | NO           | NO          |          |
| APP  | 4     | NO            | NO                 | NO           | NO        | NO           | NO          |          |


Add rows for each active phase as you open new work.

---

## 4) Execution Log

Append one row per command run. This creates auditability when you need to reconstruct why a gate is blocked.


| Date       | Repo | Phase | Command | Result | Artifacts Updated | Next Action |
| ---------- | ---- | ----- | ------- | ------ | ----------------- | ----------- |
| 2026-02-22 | -    | -     | -       | -      | -                 | -           |
| 2026-02-22 | DB   | 23    | phase preflight packet authoring + planning/codebase drift refresh | complete | 23 phase packet + planning metadata | run `/gsd:list-assumptions 23` |


---

## 5) Artifact Sync Checklist

Use this after any phase that changes cross-repo contracts.


| Artifact                    | Producer Repo | Trigger                                                          | Synced? | Date | Notes |
| --------------------------- | ------------- | ---------------------------------------------------------------- | ------- | ---- | ----- |
| `db-contract-manifest.json` | DB            | Any phase adding/changing procs/views/tables consumed by API/App | NO      | -    |       |
| OpenAPI spec                | API           | Any phase changing endpoint surface/contracts                    | NO      | -    |       |
| App API snapshot/types      | App           | Any API contract version change consumed by app                  | NO      | -    |       |


---

## 6) Quality Forms Entry Gate Checklist

Do not open QF execution phases until all items below are checked.

- DB Phase 23 complete
- DB Phase 24 complete
- DB contract manifest refreshed for Phase 21-24 state
- API Phase 3.5 complete
- 50414 handling aligned to HTTP 202 contract semantics
- All 9 implementation-start criteria in `../Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md` are green
- Quality Forms API docs aligned with `/v1` route conventions

