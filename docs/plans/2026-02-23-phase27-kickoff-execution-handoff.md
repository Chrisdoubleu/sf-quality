# Phase 27 Kickoff Execution Handoff (2026-02-23)

## Purpose
Hand off to a new execution chat to start Phase 27 (`approval-lifecycle-timeout-processing`) from a clean, merged post-Phase-26 baseline.

## Post-Phase-26 Baseline (Merged + Clean)
- Root repo (`sf-quality`) `master`: `3357ec5`
  - PR merged: https://github.com/Chrisdoubleu/sf-quality/pull/8
- DB repo (`sf-quality-db`) `main`: `d845797`
  - PR merged: https://github.com/Chrisdoubleu/sf-quality-db/pull/12
- API repo (`sf-quality-api`) `main`: `806a452`
  - Phase 26 runtime/authz integration is present on main.
- App repo (`sf-quality-app`) `main`: `2e390f4`
  - Phase 26 published contract snapshot alignment is present on main.

## What Is Already Done
1. Phase 26 Slice 01-08 execution is complete.
2. Producer-first chain alignment (DB -> API -> App) is in place for Phase 26 outputs.
3. Repos/worktrees were cleaned; no pending local edits are required to continue.

## Required Read-First Inputs
- Prior closeout handoff:
  - `C:/Dev/sf-quality/docs/plans/2026-02-23-rbac-phase26-execution-handoff.md`
- DB Phase 27 planning stubs:
  - `C:/Dev/sf-quality-db/.planning/phases/27-approval-lifecycle-timeout-processing/27-CONTEXT.md`
  - `C:/Dev/sf-quality-db/.planning/phases/27-approval-lifecycle-timeout-processing/27-RESEARCH.md`
  - `C:/Dev/sf-quality-db/.planning/phases/27-approval-lifecycle-timeout-processing/27-VERIFICATION.md`
- Decision constraint:
  - `C:/Dev/sf-quality-db/.planning/decisions/ADR-2026-02-22-abac-decision-gate.md`
- Phase 26 contract artifacts to preserve compatibility with:
  - `C:/Dev/sf-quality-db/.planning/contracts/rbac-capability-alias-map.json`
  - `C:/Dev/sf-quality-db/.planning/contracts/deny-reason-envelope.json`
  - `C:/Dev/sf-quality-api/.planning/contracts/api-openapi.publish.json`
  - `C:/Dev/sf-quality-app/.planning/contracts/api-openapi.snapshot.json`

## Non-Negotiable Constraints
1. Do not rerun full remediation or full `.planning` scans.
2. Preserve ABAC defer decision unless explicit trigger change is evidenced.
3. Preserve producer-first contract-chain gating (DB -> API -> App).
4. Preserve explicit-grant runtime model and deny-by-default behavior.
5. Keep patch set low churn and verification-first.

## Required Skill Sequence For New Chat
1. Invoke `using-superpowers` first.
2. Invoke `brainstorming` before proposing architecture/design execution changes.
3. Invoke `writing-plans` before making multi-file edits.
4. Invoke `executing-plans` when implementing the approved plan.
5. Invoke `verification-before-completion` before any success claim.
6. If substantial edits are made, invoke `requesting-code-review` before handoff.
7. At branch completion, invoke `finishing-a-development-branch`.

## Execution Outcomes Required In Next Chat
A) Phase 27 Slice Plan
- Define concrete, low-churn slices for Phase 27 with Slice 01 clearly scoped for immediate execution.
- Update DB Phase 27 planning docs from stub state into actionable status.

B) Phase 27 Slice 01 Implementation (Producer-First)
- Implement DB-first timeout/approval lifecycle contract surface for Slice 01.
- Update DB planning/contracts artifacts required by Slice 01.
- Propagate only necessary downstream changes to API, then App, without bypassing producer gates.

C) Verification
- Run `pwsh -File scripts/Invoke-CycleChecks.ps1 -ChangedOnly` in each touched repo as applicable.
- If API runtime code changes, run `dotnet test` in `sf-quality-api`.
- Report pass/fail per repo and identify any drift findings.

D) Review + Handoff
- Summarize findings (bugs/risks/regressions first).
- Produce the next-slice handoff prompt (Phase 27 continuation).

---

## Paste-Ready New Chat Prompt

```text
Continue from the post-Phase-26 merged baseline and start Phase 27 execution (approval lifecycle + timeout processing) without repeating full-repo discovery.

Load this handoff first:
- C:/Dev/sf-quality/docs/plans/2026-02-23-phase27-kickoff-execution-handoff.md

Current merged anchors:
- sf-quality master: 3357ec5
- sf-quality-db main: d845797
- sf-quality-api main: 806a452
- sf-quality-app main: 2e390f4

Required skill sequence:
1. Invoke `using-superpowers` first.
2. Invoke `brainstorming` before proposing architecture/design execution changes.
3. Invoke `writing-plans` before making multi-file edits.
4. Invoke `executing-plans` when implementing the approved plan.
5. Invoke `verification-before-completion` before any completion claim.
6. If substantial edits are made, invoke `requesting-code-review` before handoff.
7. At branch completion, invoke `finishing-a-development-branch`.

Read-first inputs:
- C:/Dev/sf-quality/docs/plans/2026-02-23-rbac-phase26-execution-handoff.md
- C:/Dev/sf-quality-db/.planning/phases/27-approval-lifecycle-timeout-processing/27-CONTEXT.md
- C:/Dev/sf-quality-db/.planning/phases/27-approval-lifecycle-timeout-processing/27-RESEARCH.md
- C:/Dev/sf-quality-db/.planning/phases/27-approval-lifecycle-timeout-processing/27-VERIFICATION.md
- C:/Dev/sf-quality-db/.planning/decisions/ADR-2026-02-22-abac-decision-gate.md
- C:/Dev/sf-quality-db/.planning/contracts/rbac-capability-alias-map.json
- C:/Dev/sf-quality-db/.planning/contracts/deny-reason-envelope.json
- C:/Dev/sf-quality-api/.planning/contracts/api-openapi.publish.json
- C:/Dev/sf-quality-app/.planning/contracts/api-openapi.snapshot.json

Execution constraints:
1. Do not rerun full remediation or full planning scans.
2. Preserve ABAC defer decision unless explicit trigger change is evidenced.
3. Preserve producer-first contract-chain gating (DB -> API -> App).
4. Preserve explicit-grant runtime model and deny-by-default behavior.
5. Keep patch set low churn and verification-first.

Deliverables:
A) Define and document Phase 27 slice map, then finalize an implementable Slice 01.
B) Apply Slice 01 DB-first implementation and only required downstream API/App updates.
C) Run verification (`Invoke-CycleChecks.ps1 -ChangedOnly` in touched repos; include `dotnet test` in API if runtime code changed).
D) Provide review findings and a follow-up prompt for the next Phase 27 slice.
```
