# Immediate Deployment + RBAC Full Sequence Handoff (2026-02-23)

## Purpose
Capture the full execution scope discussed: immediate infra/auth de-risking plus RBAC producer-first slice execution across DB -> API -> App, with strict planning/governance coverage so no planning or phase updates are missed.

## Scope (End-to-End)
1. Infra/Auth gate:
   - A1 `sf-quality-db`: derisking Step 1 artifacts + run provisioning/bootstrap.
   - A2 `sf-quality-api`: Phase 3.1 auth-chain deployment/validation slice.
   - A3 `sf-quality-app`: Phase 1 foundation/auth-probe deployment slice.
2. RBAC execution slice:
   - B1 `sf-quality-db`: Phase 26.2 producer authority artifacts (`F-*` -> `WF.*`, deterministic deny envelope).
   - B2 `sf-quality-api`: Phase 7.1 consumer contract exposure (no policy reimplementation).
   - B3 `sf-quality-app`: Phase 7 envelope-driven entitlement/deny rendering only.

## Critical Constraints (Must Preserve)
1. Do not run full remediation scans.
2. ABAC deepening remains deferred per ADR unless explicit trigger evidence changes:
   - `C:/Dev/sf-quality-db/.planning/decisions/ADR-2026-02-22-abac-decision-gate.md`
3. Producer-first gating is mandatory:
   - DB -> API -> App
4. Conflict default:
   - Option 1 overlay model (default)
   - Option 2 replace model only with explicit approval.
5. Run `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` after each execute wave.

## Mandatory Skill Sequence
1. `using-superpowers`
2. `brainstorming`
3. `writing-plans`
4. `executing-plans`
5. `verification-before-completion`
6. `requesting-code-review` (if substantial edits)
7. `finishing-a-development-branch`

## Full Planning Corpus Coverage Protocol (Mandatory)
1. During brainstorming and writing-plans, scan all planning corpus files in all repos:
   - `C:/Dev/sf-quality-db/.planning/**`
   - `C:/Dev/sf-quality-api/.planning/**`
   - `C:/Dev/sf-quality-app/.planning/**`
2. Include all phase files in coverage:
   - `C:/Dev/sf-quality-db/.planning/phases/**`
   - `C:/Dev/sf-quality-api/.planning/phases/**`
   - `C:/Dev/sf-quality-app/.planning/phases/**`
3. Build and maintain a `Planning Impact Matrix` with:
   - `repo`, `file`, `change required?`, `reason`, `owner wave (A1/A2/A3/B1/B2/B3)`, `status`
4. Every planning/state/contract/phase file reviewed must be either:
   - updated in the owning wave, or
   - explicitly marked `no-change` with rationale in the matrix.
5. No completion claim is allowed until Planning Impact Matrix coverage is complete.

## Documentation Placement Map (Where To Record What)

### Workspace-level orchestration + handoffs
- `C:/Dev/sf-quality/docs/plans/`
- Use for: master execution ledger, wave handoff, follow-up prompt.

### DB producer authority + infra + contracts
- Planning/state:
  - `C:/Dev/sf-quality-db/.planning/STATE.md`
  - `C:/Dev/sf-quality-db/.planning/ROADMAP.md`
  - `C:/Dev/sf-quality-db/.planning/PROJECT.md`
  - `C:/Dev/sf-quality-db/.planning/REQUIREMENTS.md`
  - `C:/Dev/sf-quality-db/.planning/codebase/CONCERNS.md`
- Infra/auth implementation:
  - `C:/Dev/sf-quality-db/database/deploy/Deploy-Infrastructure.ps1`
  - `C:/Dev/sf-quality-db/database/deploy/Bootstrap-AuthValidation.ps1`
  - `C:/Dev/sf-quality-db/database/deploy/deploy-config.json`
- Producer contracts:
  - `C:/Dev/sf-quality-db/.planning/contracts/rbac-capability-alias-map.json`
  - `C:/Dev/sf-quality-db/.planning/contracts/deny-reason-envelope.json`

### API consumer contract exposure + publication
- Planning/state:
  - `C:/Dev/sf-quality-api/.planning/STATE.md`
  - `C:/Dev/sf-quality-api/.planning/ROADMAP.md`
  - `C:/Dev/sf-quality-api/.planning/PROJECT.md`
  - `C:/Dev/sf-quality-api/.planning/REQUIREMENTS.md`
  - `C:/Dev/sf-quality-api/.planning/phases/07-workflow-action-items/07-CONTEXT.md`
  - `C:/Dev/sf-quality-api/.planning/phases/03.1-auth-chain-validation/` (create/update in A2)
- Runtime/contracts:
  - `C:/Dev/sf-quality-api/src/SfQualityApi/Endpoints/DiagnosticEndpoints.cs`
  - `C:/Dev/sf-quality-api/src/SfQualityApi/appsettings.json`
  - `C:/Dev/sf-quality-api/.planning/contracts/api-openapi.publish.json`
  - `C:/Dev/sf-quality-api/.planning/contracts/rbac-capability-alias-map.snapshot.json`
  - `C:/Dev/sf-quality-api/.planning/contracts/deny-reason-envelope.snapshot.json`
  - `C:/Dev/sf-quality-api/.github/workflows/deploy-api.yml`

### App consumer rendering + snapshots
- Planning/state:
  - `C:/Dev/sf-quality-app/.planning/STATE.md`
  - `C:/Dev/sf-quality-app/.planning/ROADMAP.md`
  - `C:/Dev/sf-quality-app/.planning/PROJECT.md`
  - `C:/Dev/sf-quality-app/.planning/REQUIREMENTS.md`
  - `C:/Dev/sf-quality-app/.planning/phases/01-frontend-foundation-contract-tooling/01-CONTEXT.md`
  - `C:/Dev/sf-quality-app/.planning/phases/07-workflow-action-approvals/07-CONTEXT.md`
- Contracts/workflows:
  - `C:/Dev/sf-quality-app/.planning/contracts/api-openapi.snapshot.json`
  - `C:/Dev/sf-quality-app/.planning/contracts/rbac-capability-alias-map.snapshot.json`
  - `C:/Dev/sf-quality-app/.planning/contracts/deny-reason-envelope.snapshot.json`
  - `C:/Dev/sf-quality-app/.github/workflows/deploy-app.yml`

## Required Read-First Inputs
- `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/docs/plans/2026-02-23-rbac-phase26-execution-handoff.md`
- `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/.planning/INFRASTRUCTURE-DERISKING-PLAN.md`
- RBAC package:
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/00-PLAN.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/01-design-foundations.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/02-role-catalog-operational.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/03-role-catalog-oversight-admin.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/04-feature-component-map.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/05-functional-area-matrix.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/06-plant-composition-examples.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/07-constraint-catalog.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/08-delegation-hierarchy.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/09-extensibility-guide.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/10-merge-semantics.md`
  - `C:/Dev/sf-quality/.worktrees/workspace-remediation-2026-02-22/sf-quality-db/docs/handoffs/Role Security/RBAC-Package-2026-02-23/99-FINAL.md`

## Mandatory Execution Order

### A) Infra/Auth Gate

#### A1 `sf-quality-db`
1. `/gsd:quick`
2. Implement derisking Step 1 artifacts:
   - `Deploy-Infrastructure.ps1`
   - `Bootstrap-AuthValidation.ps1`
   - `deploy-config.json` updates
3. Run:
   - `Deploy-Infrastructure.ps1 -WhatIf`
   - `Deploy-Infrastructure.ps1` (real)
   - `Bootstrap-AuthValidation.ps1`
4. `/gsd:verify-work`
5. `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly`

#### A2 `sf-quality-api`
1. `/gsd:insert-phase`
2. `/gsd:discuss-phase 3.1`
3. `/gsd:plan-phase 3.1`
4. `/gsd:execute-phase 3.1`
5. `/gsd:verify-work`
6. `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly`

#### A3 `sf-quality-app`
1. `/gsd:discuss-phase 1`
2. `/gsd:plan-phase 1`
3. `/gsd:execute-phase 1`
4. `/gsd:verify-work`
5. `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly`

### B) RBAC Slice Execution (Producer-First)

#### B1 `sf-quality-db`
1. `/gsd:insert-phase`
2. `/gsd:discuss-phase 26.2`
3. `/gsd:plan-phase 26.2`
4. `/gsd:execute-phase 26.2`
5. `/gsd:verify-work`
6. Deliver DB authority artifacts:
   - `F-*` -> `WF.*` alias contract
   - deterministic deny-reason envelope

#### B2 `sf-quality-api`
1. `/gsd:insert-phase`
2. `/gsd:discuss-phase 7.1`
3. `/gsd:plan-phase 7.1`
4. `/gsd:execute-phase 7.1`
5. `/gsd:verify-work`
6. Deliver API contract exposure for alias map + deny envelope (no policy logic reimplementation)

#### B3 `sf-quality-app`
1. `/gsd:discuss-phase 7`
2. `/gsd:plan-phase 7`
3. `/gsd:execute-phase 7`
4. `/gsd:verify-work`
5. Deliver envelope-only entitlement/deny rendering (no local policy logic)

## Verification Gates (Before Any Completion Claim)
1. DB:
   - `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly`
2. API:
   - `dotnet test`
   - `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly`
3. App:
   - `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly`
4. Cross-repo:
   - confirm producer artifact propagation DB -> API -> App
   - confirm Planning Impact Matrix has no uncovered planning/phase files

## Final Handoff Requirements
1. Commit SHAs by repo and touched file list.
2. Verification evidence (exact commands, pass/fail).
3. Review findings first (bugs/risks/regressions), then summary.
4. Residual risks/blockers.
5. Planning Impact Matrix with explicit update/no-change rationale.
6. Next-slice prompt from new baseline.

## Chat-End Findings Capture Protocol (Mandatory)
1. Every completion message must include findings with stable IDs:
   - Format: `FND-YYYYMMDD-XX`
   - Severity required (`High`/`Medium`/`Low`/`Info`)
   - Status required (`Open`/`Closed`/`Partial`)
2. Every `Open` or `Partial` finding must be carried into the next handoff file in a dedicated section:
   - `Open Findings Carry-Forward`
   - Include exact finding text (or an exact quote-safe paraphrase) plus the same ID.
3. Handoff must include a `Findings Mapping Table` with columns:
   - `finding_id`, `severity`, `status`, `owner_wave`, `target_handoff_file`, `target_line_ref`, `closure_slice`
4. No completion claim is allowed until coverage evidence is printed:
   - run: `rg -n "FND-[0-9]{8}-[0-9]{2}" C:/Dev/sf-quality/docs/plans/*.md`
   - report each `Open`/`Partial` finding with a concrete file reference (`path:line`) in the final response.
5. If any finding is intentionally not carried forward, final response must include:
   - explicit `WAIVED` marker,
   - rationale,
   - approver name/date,
   - replacement control.

## Findings Block Template (Use In Every Final Message)
```text
Findings
- [Medium][Open][FND-YYYYMMDD-XX] <finding text>
- [Low][Open][FND-YYYYMMDD-YY] <finding text>

Carry-Forward Coverage
- FND-YYYYMMDD-XX -> C:/Dev/sf-quality/docs/plans/<handoff>.md:<line>
- FND-YYYYMMDD-YY -> C:/Dev/sf-quality/docs/plans/<handoff>.md:<line>
```

## Pre-Execution Closeout Snapshot (2026-02-23)
1. Workspace repo `sf-quality` merged and pushed to `origin/master` at `a0989d5f5118f345916a9478a32aa6082a564200`.
2. DB repo `sf-quality-db` merged locally to `main` at `2c13db6fbd81a2ce822e90182fe41c064f681f11`.
3. Direct push to `origin/main` is blocked by repository rule (PR required); branch `phase27/slice01-timeout-contract-local` was pushed and PR opened:
   - `https://github.com/Chrisdoubleu/sf-quality-db/pull/13`
4. API/App repos remain clean on `main` baseline (no new local changes).

## Open Findings Carry-Forward
- [Medium][Open][FND-20260223-01] `sf-quality-db` direct push to `main` is blocked by repository rules; producer baseline integration remains pending until PR `#13` merges.
- [Low][Open][FND-20260223-02] Local `sf-quality-db/main` remains ahead of `origin/main` by 3 commits while PR `#13` is pending, creating accidental-work risk if new changes are started from local `main` before sync.

## Findings Mapping Table
| finding_id | severity | status | owner_wave | target_handoff_file | target_line_ref | closure_slice |
| --- | --- | --- | --- | --- | --- | --- |
| FND-20260223-01 | Medium | Open | Pre-Execution | C:/Dev/sf-quality/docs/plans/2026-02-23-immediate-deployment-rbac-full-sequence-handoff.md | `Open Findings Carry-Forward` section | Merge after PR #13 |
| FND-20260223-02 | Low | Open | Pre-Execution | C:/Dev/sf-quality/docs/plans/2026-02-23-immediate-deployment-rbac-full-sequence-handoff.md | `Open Findings Carry-Forward` section | Post-merge sync to `origin/main` |
