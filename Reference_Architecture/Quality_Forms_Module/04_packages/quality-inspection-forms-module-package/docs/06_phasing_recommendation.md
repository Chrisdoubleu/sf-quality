# Deliverable 6: Phasing Recommendation

This module follows strict contract-chain sequencing:

`sf-quality-db` publishes manifest -> `sf-quality-api` publishes OpenAPI -> `sf-quality-app` refreshes snapshot/types

---

## Authoritative Status

Implementation start is **blocked** until pre-build blockers are closed in:
- `Reference_Architecture/Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md`

---

## Entry Gates (Must Be True Before Wave QF-A)

1. DB v2.0 Phases 23-24 are complete and DB manifest is refreshed.
2. API Phase 3.5 hardening is complete (`/v1` route baseline active).
3. Approval-required semantics are aligned to `50414 -> HTTP 202 Accepted`.
4. Migration blockers are closed:
   - additive-safe `159`
   - explicit `dbo.StatusCode` contract in `158`/`160`
   - inspection permission/feature seeds present
   - `workflow.usp_TransitionState` supports `InspectionTemplate` and `Inspection`
5. Stored procedure contracts are deterministic and complete for all 29 procedures.
6. API endpoint contracts are deterministic and complete for all 29 endpoints.

---

## Cross-Repo Wave Plan

### Wave QF-A — Foundations and Safety Closure

**DB (planned Phase 34)**
- Close must-fix migration safety and execution blockers.
- Publish updated `db-contract-manifest.json`.

**API (planned Phase 11)**
- Implement template + inspection core endpoints under `/v1`.
- Preserve thin-gateway behavior and `202` approval-required handling.
- Publish OpenAPI artifact.

**App (planned Phase 11)**
- Implement template list/editor/publish UX against `/v1` contracts.
- Refresh API snapshot/types after API publish.

**Gate to proceed:** DB manifest published -> API OpenAPI published -> App snapshot refreshed.

---

### Wave QF-B — Operations (Assignment, Scheduling, Due Queue)

**DB (planned Phase 35)**
- Implement/close assignment + schedule + due creation contract surface.
- Publish updated `db-contract-manifest.json`.

**API (planned Phase 12)**
- Implement assignment/schedule/due queue/reporting endpoints under `/v1`.
- Publish OpenAPI artifact.

**App (planned Phase 12)**
- Implement due queue + operator fill/submit/review flows.
- Refresh API snapshot/types after API publish.

**Gate to proceed:** DB manifest published -> API OpenAPI published -> App snapshot refreshed.

---

### Wave QF-C — Hardening, Attachments, Analytics/SPC

**DB (planned Phase 36)**
- Harden 29-procedure contract surface.
- Finalize attachment and analytics/SPC DB contracts.
- Publish updated `db-contract-manifest.json`.

**API (planned Phase 13)**
- Implement attachment initiate/finalize orchestration and SPC/reporting endpoints.
- Publish OpenAPI artifact.

**App (planned Phase 13)**
- Implement attachment UX hardening + analytics/SPC surfaces.
- Refresh API snapshot/types after API publish.

**Gate to complete module:** DB manifest published -> API OpenAPI published -> App snapshot refreshed.

---

## Non-Negotiable Rules

1. SQL remains authoritative for business rules.
2. API remains thin and versioned (`/v1/...`).
3. Approval-required is a pending-success path (`202 Accepted`), not forbidden.
4. No API/App implementation begins for a wave until upstream contract artifacts are published.
5. Manifest/OpenAPI/snapshot publication tasks are mandatory completion criteria for every wave.
