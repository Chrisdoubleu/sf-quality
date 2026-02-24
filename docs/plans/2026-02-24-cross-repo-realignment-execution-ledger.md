# Cross-Repo Realignment Execution Ledger

Date: 2026-02-24
Scope: `sf-quality-db`, `sf-quality-api`, `sf-quality-app`
Wave: 1 (planning/status realignment)

## Decision Lock

1. No new DB Phase 35 feature work unless it is a blocker for API/App delivery.
2. Run planning realignment first to remove stale phase/status drift.
3. Run API catch-up in strict order: Phase 4, then Phase 6, then Phase 8/9.
4. Start App Phase 1 as API catch-up starts, then App Phase 2/3.
5. After each wave: tests + cycle checks + evidence note + merge.

## Baseline Snapshot (Pre-Realignment)

| Repo | Branch | Clean |
|------|--------|-------|
| `sf-quality-db` | `main...origin/main` | yes |
| `sf-quality-api` | `main...origin/main` | yes |
| `sf-quality-app` | `main...origin/main` | yes |

## Numeric/Status Correction Map

| Repo | Artifact | Observed Before | Canonical After | Reason |
|------|----------|-----------------|-----------------|--------|
| db | `.planning/STATE.md` | "Phase 35 readiness handoff" as next focus | Phase 35 blocker-only freeze | API/App consumer catch-up takes precedence |
| db | `.planning/ROADMAP.md` | "Phase 35 starts at migration 151" | Phase 35 queued; execute only on blocker exception | Preserve producer stability while consumers catch up |
| api | `.planning/STATE.md` | focus drifted to "Phase 8/9 prep" and stale SqlErrorMapper note | strict catch-up order `4 -> 6 -> 8/9`; corrected runtime decisions | Runtime hotfix merged and sequencing was stale |
| api | `.planning/ROADMAP.md` | app shown as blocked | app phase 1 unblocked during API catch-up | OpenAPI gate is green and catch-up policy changed |
| app | `.planning/STATE.md` | unlocked but no execution policy | startup now explicitly sequenced with API catch-up | prevent drift and idle state |
| app | `.planning/ROADMAP.md` | generic unlocked statement | precise phase gating and start order | enforce predictable cross-repo execution |

## Commands and Verification Evidence

Executed on 2026-02-24:
1. `pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-db'; pwsh scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)"`
Result:
`Planning consistency checks PASSED.`
`Phase directories validated: 10`
2. `pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)"`
Result:
`Planning consistency checks PASSED.`
`Phase directories validated: 10`
3. `pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-app'; pwsh scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)"`
Result:
`Planning consistency checks PASSED.`
`Phase directories validated: 10`

Cross-repo cycle checks:
1. `pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly"`
Result:
`All cycle checks passed.`
Summary:
- `db`: `EnforcementRegistry`, `DbContractManifest`, `SqlStaticRules` -> `PASS`
- `api`: `PlanningConsistency`, `DbContractReferences`, `OpenApiPublication` -> `PASS`
- `app`: `PlanningConsistency`, `ApiContractReferences` -> `PASS`

## Risks/Flags

1. `human_needed` remains possible for admin allow-path runtime probe in API runtime sanity closeout.
2. Root workspace has pre-existing untracked docs under `docs/Organization Forms Reference/` and must remain untouched by this wave.
