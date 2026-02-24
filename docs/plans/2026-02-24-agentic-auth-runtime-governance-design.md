# Agentic Auth Runtime Governance Design

Date: 2026-02-24
Author: Codex
Status: Approved for implementation

## Goal

Create a scalable, repeatable auth runtime operating model for agentic development across the `sf-quality` DB -> API -> App chain. The model must prevent one-off fixes, preserve decision continuity, and produce durable evidence.

## Why This Is Needed

Recent runtime failures showed two classes of risk:

1. Contract drift risk: API permission code and DB permission catalog drift (`NCR_SUBMIT` vs `WF.NCR.Submit`).
2. Operational drift risk: runtime probes depend on ad-hoc user identities and manual setup, which blocks repeatability for future agents.

## Scope

In scope:

1. `sf-quality-api` auth-gated route governance and runtime sanity scripts.
2. `sf-quality-db` dev-only probe identity fixture management (data-only; no schema changes).
3. Planning/state/verification documentation updates so future agents inherit the operating model.

Out of scope:

1. Production fixture identities.
2. Any DB schema changes for Phase 34 closeout.
3. Full business workflow E2E expansion beyond auth-chain sanity baseline.

## Operating Model

### Persona Model (Dev-only)

Three persistent probe identities are maintained in dev DB:

1. `deny_user`: authenticated but denied expected protected operation (`403` expected).
2. `allow_user`: non-admin user with role/permission grant expected to pass auth gate (non-`403` expected).
3. `admin_user`: break-glass admin via `UserPlantAccess.AccessLevel='Admin'` expected to bypass policy checks (non-`403` expected).

This avoids one-off identity setup and gives consistent probe semantics.

### Two-Layer Validation

1. Layer A - Quick auth sanity (every PR/run):
   1. DB/API preflight readiness.
   2. Three persona probes.
   3. Automatic evidence output.
2. Layer B - Deep workflow/runtime suite (release/scheduled):
   1. Broader state transition and data behavior checks.
   2. Uses stable fixture scenarios.

### Governance Rollout

1. Initial mode: advisory (warning only).
2. Promotion rule: move to blocking after **10 consecutive clean PR sanity runs**.
3. Decision and evidence links become required closeout artifacts.

## Architecture

### DB Responsibilities

1. Provide idempotent dev fixture setup script for probe identities.
2. Provide DB preflight checker for required permission and fixture integrity.
3. Keep fixture logic data-only; do not introduce schema changes.

### API Responsibilities

1. Use canonical DB permission codes for guarded routes (`WF.NCR.Submit` for submit gate).
2. Provide API preflight and quick sanity scripts that consume fixture OIDs.
3. Persist runtime probe evidence into timestamped artifact files.
4. Add regression tests that fail on permission code drift.

### Documentation Responsibilities

1. Decision file in workspace `docs/plans/`.
2. State and verification updates in both DB and API planning surfaces.
3. Explicit commands for future agents in repo docs.

## Data Flow

1. Fixture setup ensures `AppUser`, `UserPlantAccess`, and `UserRole`/permission grant states for three personas.
2. API request carries synthetic Easy Auth principal header with probe OID.
3. API resolves OID, creates user-scoped DB connection, reads session `UserId`, and calls `security.usp_CheckPermission`.
4. Resulting status code is captured by runtime probe scripts and written to evidence output.

## Error Handling

1. Preflight scripts fail fast with explicit missing dependencies:
   1. missing permission code
   2. missing plant
   3. missing role permission grant
   4. missing/incorrect fixture identities
2. Probe scripts return nonzero exit when observed statuses differ from expected persona outcomes.
3. Unknown SQL errors continue falling back to HTTP 500 via `SqlErrorMapper` null mapping behavior.

## Test Strategy

1. TDD for API behavior changes (failing test first):
   1. canonical permission code usage
   2. guard helper expectations
2. Script verification:
   1. preflight pass/fail paths
   2. quick sanity persona status assertions
3. Existing repo checks remain mandatory:
   1. build/tests
   2. planning/contract checks
   3. cycle checks

## Risks and Mitigations

1. Risk: fixture identities accidentally reused outside dev.
   Mitigation: scripts explicitly target `dev` and enforce environment guard.
2. Risk: admin probe hides role-grant regressions.
   Mitigation: always run both `allow_user` and `admin_user`; require both.
3. Risk: decision drift over time.
   Mitigation: decision record + state updates + required evidence links in verification.

## Success Criteria

1. API guarded submit route uses `WF.NCR.Submit`.
2. Dev fixture script can be rerun idempotently.
3. Quick sanity run produces:
   1. `deny_user` -> 403
   2. `allow_user` -> non-403
   3. `admin_user` -> non-403
4. Evidence artifact is produced and references exact command outputs.
5. Planning/state docs in API and DB reference the new operating model and scripts.
