# Reconciled Actions & Remaining TODOs

Live validation has closed prior unknowns. This file now records:
- what is confirmed,
- what is still mandatory before build,
- what remains as implementation/configuration follow-up.

---

## Resolved by Live Validation (2026-02-22)

Source:
- `Reference_Architecture/Quality_Forms_Module/00_ground_truth/live-db-validation-notes-2026-02-22.md`

1. `dbo.StatusCode` schema is known and explicit.
   - Required non-default insert fields: `StatusCode`, `StatusName`, `EntityType`, `StatusCategory`.
   - Implication: remove dynamic schema-discovery behavior in status seed flows.

2. `workflow.usp_TransitionState` is hard-coded for known entity types.
   - `InspectionTemplate` and `Inspection` are not currently handled.
   - Implication: explicit dispatch/load/update paths are required before publish/submit rollout.

3. Cross-environment signature consistency verified (dev/prod hash match at validation time).

---

## Must-Fix Before Build (Authoritative)

Use the authoritative checklist in:
- `Reference_Architecture/Quality_Forms_Module/03_adjudication/quality-forms-module-final-authoritative-review.md`

Mandatory blockers include:
1. Additive-safe workflow entity-type constraint extension (migration `159`).
2. Inspection security feature/permission seed migration (live next migration number).
3. Explicit workflow transition dispatch support for `InspectionTemplate` and `Inspection`.
4. Explicit `dbo.StatusCode` contract usage in status/workflow seed migrations (`158`/`160`).
5. Deterministic full stored procedure contracts for all 29 procedures.
6. Deterministic full API endpoint contracts for all 29 endpoints.
7. Executable phase gating with manifest/OpenAPI/app snapshot publication steps.
8. RLS-safe service/scheduler execution model definition and enforcement.

---

## Remaining Implementation/Configuration Tasks

These are still required, but they are configuration/hardening follow-up tasks rather than unresolved unknowns.

1. Shift model governance:
   - confirm existing shift lookup category usage, or add one in a dedicated migration.

2. Controlled-document numbering:
   - confirm numbering rules for `INSP_TEMPLATE` and `INSP_ATTACHMENT`.

3. Approval chain role configuration:
   - seed/configure `workflow.ApprovalChain` and `workflow.ApprovalStep` with environment role IDs.

4. Attachment flow finalization:
   - enforce initiate -> SAS generation -> finalize contract across DB/API/app.

5. Performance validation:
   - run representative query tests on production-like volumes and add covering indexes where needed.
