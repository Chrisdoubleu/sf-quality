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

1. `human_needed` confirmed for admin allow-path runtime probe in API runtime sanity closeout (dev DB has no active user-role assignments).
2. Root workspace has pre-existing untracked docs under `docs/Organization Forms Reference/` and must remain untouched by this wave.

## Wave Execution Record (Merged)

| Wave | Repo | PR | Merge Commit |
|------|------|----|--------------|
| 1A | `sf-quality` | https://github.com/Chrisdoubleu/sf-quality/pull/11 | `111656a4ed00f46d2c1b9a13919fa9c35ea9f6d4` |
| 1B | `sf-quality-db` | https://github.com/Chrisdoubleu/sf-quality-db/pull/25 | `2a9720b3fec5bf408cebbfa2755cac7d6bdd6125` |
| 1C | `sf-quality-api` | https://github.com/Chrisdoubleu/sf-quality-api/pull/9 | `035bbf7abd803a822e2e00bbcbc2662e709853a9` |
| 1D | `sf-quality-app` | https://github.com/Chrisdoubleu/sf-quality-app/pull/4 | `ed281afd05328cee0f84435b54a25f0d0bbbe8f8` |
| 2 | `sf-quality-api` (Phase 4 slice) | https://github.com/Chrisdoubleu/sf-quality-api/pull/10 | `e82d12ba7dd7a663d6a92499adba9dda58f31fd8` |
| 3 | `sf-quality-api` (Phase 6 slice) | https://github.com/Chrisdoubleu/sf-quality-api/pull/11 | `4c219411aa5306826faf39dbc14f193d1d17b4d1` |
| 4 | `sf-quality-api` (Phase 8/9 slice) | https://github.com/Chrisdoubleu/sf-quality-api/pull/12 | `e620ddc99005ead6cd581d43814e433709613992` |
| 5 | `sf-quality-app` (Phase 1 slice) | https://github.com/Chrisdoubleu/sf-quality-app/pull/5 | `76bb49fbf3005db6b6c73e1e43e375193bca8591` |
| 6 | `sf-quality-app` (Phase 2/3 slice) | https://github.com/Chrisdoubleu/sf-quality-app/pull/6 | `2f706f32c95e13107f83c21b27cbbecfb27f0d1a` |

## Post-Wave Verification Snapshot

1. API verification after Phase 8/9 slice:
   - `dotnet build SfQualityApi.sln -v minimal` -> `Build succeeded. 0 Warning(s), 0 Error(s).`
   - `dotnet test tests/SfQualityApi.Tests/SfQualityApi.Tests.csproj -v minimal` -> `Passed: 37, Failed: 0`
   - `pwsh scripts/Test-DbContractReferences.ps1 -RepoRoot (Get-Location)` -> `PASSED`
   - `pwsh scripts/Test-OpenApiPublication.ps1 -RepoRoot (Get-Location)` -> `PASSED`
   - `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` -> `All cycle checks passed.`
2. App verification after Phase 2/3 slice:
   - `pwsh scripts/Test-AuthSessionPropagation.ps1 -RepoRoot (Get-Location)` -> `PASSED`
   - `pwsh scripts/Test-ServerApiBoundary.ps1 -RepoRoot (Get-Location)` -> `PASSED`
   - `pwsh scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)` -> `PASSED`
   - `pwsh scripts/Test-ApiContractReferences.ps1 -RepoRoot (Get-Location)` -> `PASSED`
   - `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` -> `All cycle checks passed.`

## Runtime Sanity Closeout Attempt (2026-02-24)

1. Runtime command evidence recorded at:
   - `docs/plans/evidence/2026-02-24-runtime-sanity-closeout.md`
2. Runtime probe results:
   - non-admin deny probe (`2FA67B5A-5880-4D2A-BFAD-6F5D29EBF101`) -> `403` (`PASS`)
   - admin allow probe candidate (`7CB31D63-9EA5-43EB-BCC3-BE10CA6F6C03`) -> `403` (`FAIL`; expected non-`403`)
3. Correlation IDs captured:
   - health: `2af594ff-d076-4f87-a4d3-032ee84c0e76`
   - non-admin deny: `41f59491-19e7-49de-8297-72e6f8969b75`
   - admin candidate: `5df45e3f-5358-4d77-8b9f-9d3719157998`
4. DB identity/authorization evidence:
   - `dbo.UserRole WHERE IsActive=1` -> `0` rows
   - `dbo.UserPlantAccess` -> `0` rows
   - `WF.NCR.Submit` grants exist at role level, but all matching rows had `UserId = NULL`
5. Outcome:
   - deny-path proof complete
   - allow-path proof blocked pending manual provisioning of an active user-role mapping that grants `WF.NCR.Submit` (`human_needed`)

## Open Items

1. Runtime sanity closeout deny-path is verified; admin allow-path remains blocked until a permissioned admin identity is provisioned in dev DB.
2. DB Phase 35 remains blocked except for formally documented API/App blocker exceptions.
