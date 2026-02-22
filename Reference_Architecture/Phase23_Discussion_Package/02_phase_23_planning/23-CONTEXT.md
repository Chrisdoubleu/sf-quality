# Phase 23 Context

## Goal

Close v2.0 governance and deployment readiness so the database contract is current, documented, and safe for downstream API/App planning before v3.0 initialization.

Phase 23 is the immediate next executable phase after Phase 22 deferral.

## Phase Position and Dependencies

- Current chain: Phase 21.1 COMPLETE -> Phase 22 DEFERRED -> **Phase 23 NEXT**
- Blocking dependency: none (Phase 22 is explicitly deferred, not pending)
- Downstream dependency: Phase 24 and v3.0 kickoff depend on Phase 23 contract/documentation closure

## Requirement Mapping (Primary)

- `PLAT-01` six-layer cascade pattern documented as repeatable operating model
- `PLAT-02` process-family onboarding template and naming governance closure (`KNOW-13` completion path)
- `PLAT-03` extension model documentation for future v3.0 domains
- `PLAT-04` deploy/verify framework consolidation for knowledge layer
- `PLAT-05` knowledge maintenance model (forward-fix + IsVerified governance semantics)
- `PLAT-06` internal data feedback loop model
- `DEPLOY-01` v2.0 deploy orchestration closure (through migration 130)
- `SEC-01` grant closure for deployed v2.0 objects is handled inline in this phase because Phase 22 is deferred

## Mandatory Deliverables

1. **Contract Manifest Refresh (Critical)**
   - Refresh `.planning/contracts/db-contract-manifest.json` from current migration surface.
   - Minimum correction: migration file count must reflect current chain (`133`).
   - Confirm procedure/view object inventory reflects Phase 21 + 21.1 authority surface.

2. **Cross-Repo Contract Sync Notes**
   - Document parity status against:
     - `../sf-quality-api/.planning/contracts/db-contract-manifest.snapshot.json`
     - `../sf-quality-api/.planning/contracts/api-openapi.publish.json`
     - `../sf-quality-app/.planning/contracts/api-openapi.snapshot.json`
   - Record exact drift and required follow-up actions.

3. **Security Grant Closure**
   - Validate grant coverage for Phase 18-21.1 objects and add missing grants if any exist.
   - Keep role model aligned with the existing 5-role security architecture.

4. **Deploy and Verification Governance Closure**
   - Align deploy docs/scripts with current migration chain through 130.
   - Ensure verification pattern references current authority files and current phase sequence.

5. **Codebase Mapping Refresh**
   - Update stale metadata in `.planning/codebase/*` where migration counts, phase pointers, or integration model references drift from current state.

## Out of Scope

- Creating new analytics views (`ANALYTICS-*` remains deferred with Phase 22)
- Starting v3.0 phases (25-33)
- Implementing Phase 24 substrate schema changes
- API route versioning or middleware implementation (belongs to API Phase 3.5)

## Required Inputs (Planner Must Review)

### From this repo (`sf-quality-db`)

- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/contracts/db-contract-manifest.json`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/CONCERNS.md`
- `.planning/phases/23-platform-governance-documentation-deployment/23-ASSUMPTIONS-FINAL.md`

### From `sf-quality-api`

- `../sf-quality-api/.planning/STATE.md`
- `../sf-quality-api/.planning/ROADMAP.md`
- `../sf-quality-api/.planning/REQUIREMENTS.md`
- `../sf-quality-api/.planning/contracts/db-contract-manifest.snapshot.json`
- `../sf-quality-api/.planning/contracts/api-openapi.publish.json`

### From `sf-quality-app`

- `../sf-quality-app/.planning/STATE.md`
- `../sf-quality-app/.planning/ROADMAP.md`
- `../sf-quality-app/.planning/REQUIREMENTS.md`
- `../sf-quality-app/.planning/contracts/api-openapi.snapshot.json`

## Planner Generation Requirements (Mandatory)

1. Planner must review current artifacts in both sibling repos before writing plans.
2. Every generated execute plan for this phase must include post-wave command:
   - `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly`
3. The cycle-check command must appear inside each plan's top-level verification block.
4. Research output must document assumptions and impacts for both `sf-quality-api` and `sf-quality-app`.
5. Plan set must include an explicit contract-artifact update step (manifest refresh and cross-repo snapshot follow-up note).

## Entry Criteria

- Phase 21.1 completion context accepted as baseline.
- Phase 22 deferral documented and acknowledged as non-blocking for Phase 23.
- Phase 23 assumptions reviewed (`23-ASSUMPTIONS-FINAL.md`).

## Exit Criteria

- `23-RESEARCH.md` includes explicit DB/API/App artifact alignment notes and drift findings.
- Generated plans preserve contract-chain compatibility and include cycle-check commands.
- `db-contract-manifest.json` refresh is planned as a required execute deliverable.
- Phase verification checklist (`23-VERIFICATION.md`) is ready before execution.
