# Workspace Remediation Full Program Design

Date: 2026-02-22  
Scope: Full program execution for `WORKSPACE_REMEDIATION_DEEP_DIVE_EXECUTION_SAFE_PLAN.md`  
Mode: Strict stage-gated, execution-safe

## 1. Objective

Deliver the full remediation program (Stages 0-7) across `sf-quality-db`, `sf-quality-api`, `sf-quality-app`, and workspace-root architecture artifacts without breaking the contract chain or introducing new coupling regressions.

## 2. Approved Decisions

1. Target scope: full program.
2. Strategy: strict stage-gated program.
3. Safety preference: maximum gate enforcement over delivery speed.

## 3. Architecture

The program uses a split control-plane/execution-plane model:

1. Control plane: `sf-quality/Reference_Architecture` defines stage sequence, gate IDs, reconciliation mapping, and no-break rules.
2. Execution plane: each child repo implements only its owned changes and publishes artifacts for consumers.

Producer-first flow is mandatory:

1. Stage 0 (safety hardening) must pass before structural phases.
2. Stage 2 reconciliation must complete before v3.0 initialization.
3. DB producer gates unlock API consumer phases.
4. API publication readiness unlocks app execution.
5. QF extension starts only after explicit entry gate completion.

## 4. Components and Responsibilities

1. Workspace root (`Reference_Architecture`):
   - Reconcile execution plan and assessment into one authoritative sequence.
   - Resolve requirement namespace (`ARCH-*` vs `STRUCT-*`).
   - Define and track gate matrix and failure protocol.
2. `sf-quality-db`:
   - Enforce schema/module boundaries.
   - Expand static rules to detect cross-schema DML violations.
   - Deliver structural phases (25, 26, optional 26.1, 27, 28, 30+) with contract-safe publishing.
3. `sf-quality-api`:
   - Fix Phase 3.4 behavioral gaps.
   - Add ports/adapters boundary in Phase 3.6.
   - Expand CI trigger scope so runtime changes cannot bypass checks.
4. `sf-quality-app`:
   - Expand CI trigger scope for runtime paths.
   - Continue only when API contract gates are green.

## 5. Data and Contract Flow

The contract chain remains authoritative and linear:

1. DB publishes `db-contract-manifest.json`.
2. API snapshots DB contract and publishes OpenAPI.
3. App snapshots OpenAPI.

No consumer phase may proceed with stale producer artifacts. Artifact refresh decisions follow explicit rules: refresh only when contract surfaces change.

## 6. Gate and Failure Model

Each stage transition requires objective evidence:

1. Local checks in touched repos.
2. Cross-repo `Invoke-CycleChecks.ps1`.
3. Behavioral assertions for known hazards (API 3.4).
4. Gate result recorded as pass/block with command output references.

Failure protocol is deterministic:

1. Pause consumer.
2. Open producer hotfix.
3. Re-verify producer.
4. Refresh artifacts.
5. Re-run cycle checks.
6. Resume consumer.

## 7. Testing and Verification Design

Verification operates at four layers:

1. Static/contract checks (planning consistency, manifest references, OpenAPI publication).
2. Runtime/build checks (`dotnet build`, repo-specific scripts).
3. Boundary guard checks (cross-schema DML deny and endpoint inline SQL ban).
4. Stability trend checks (`GATE-STABILITY-3PH`).

No stage may claim completion without recorded command evidence.

## 8. Documentation Outputs

1. This design doc: `docs/plans/2026-02-22-workspace-remediation-full-program-design.md`.
2. Implementation plan doc: `docs/plans/2026-02-22-workspace-remediation-full-program.md`.

Execution handoff modes:

1. Preferred: `superpowers:executing-plans` in a separate execution session.
2. Alternate: `superpowers:subagent-driven-development` in current session.

## 9. Non-Goals

1. No cross-repo speculative edits in a single change set.
2. No big-bang rewrite of workflow, API, or app layers.
3. No weakening of contract-chain checks for speed.

## 10. Approval Record

1. Approach approved: Strict Stage-Gated Program.
2. Design Section 1 (Architecture): approved.
3. Design Section 2 (Task Model): approved.
4. Design Section 3 (Verification Model): approved.
5. Design Section 4 (Documentation/Handoff): approved.
