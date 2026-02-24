# Agentic Auth Runtime Governance Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish reusable auth runtime governance for agentic development by introducing deterministic dev probe fixtures, canonical API permission usage, and repeatable preflight/sanity evidence scripts.

**Architecture:** DB owns dev fixture data and readiness checks; API owns canonical permission wiring and runtime probe orchestration; workspace planning docs preserve decisions and execution evidence. The implementation is additive and data-only in DB (no schema changes).

**Tech Stack:** PowerShell 7, Azure CLI token auth, Azure SQL via existing deploy common helpers, .NET 9/xUnit, existing planning and cycle-check scripts.

---

### Task 1: Create Decision/Design Artifacts

**Files:**
- Create: `docs/plans/2026-02-24-agentic-auth-runtime-governance-design.md`
- Create: `docs/plans/2026-02-24-agentic-auth-runtime-governance-implementation-plan.md`

**Step 1: Add decision and architecture record**

Write the approved operating model sections:
1. Persona model (`deny_user`, `allow_user`, `admin_user`)
2. Two-layer validation
3. Advisory->blocking promotion rule (`10` consecutive clean PR runs)
4. Ownership split (DB/API/docs)

**Step 2: Confirm artifacts are visible in repo history**

Run: `git -C C:/Dev/sf-quality status --short`
Expected: new plan/design files are listed.

**Step 3: Commit decision artifacts**

Run:
```bash
git -C C:/Dev/sf-quality add docs/plans/2026-02-24-agentic-auth-runtime-governance-design.md docs/plans/2026-02-24-agentic-auth-runtime-governance-implementation-plan.md
git -C C:/Dev/sf-quality commit -m "Add auth runtime governance design and implementation plan"
```

### Task 2: Add DB Dev Fixture and Preflight Scripts

**Files:**
- Create: `sf-quality-db/database/deploy/Set-AuthRuntimeProbeFixtures.ps1`
- Create: `sf-quality-db/database/deploy/Test-AuthRuntimeProbePreflight.ps1`
- Modify: `sf-quality-db/README.md` (script usage section)
- Modify: `sf-quality-db/.planning/STATE.md` (decision + script references)

**Step 1: Write failing verification expectation**

Define expected preflight checks:
1. canonical permission code exists (`WF.NCR.Submit`)
2. at least one plant exists
3. role grant exists for `WF.NCR.Submit` (for `allow_user`)
4. fixture users resolve and satisfy persona constraints

**Step 2: Implement idempotent fixture setup script**

Script behavior:
1. default `-Environment dev`
2. upsert three `AppUser` rows with deterministic OIDs
3. ensure `deny_user` has no role/plant grant
4. ensure `allow_user` has `UserPlantAccess=Standard` + one role with `WF.NCR.Submit` allow on chosen plant
5. ensure `admin_user` has `UserPlantAccess=Admin` on chosen plant

**Step 3: Implement preflight script**

Script behavior:
1. connect via existing deploy helpers
2. validate required objects/data
3. print PASS/FAIL checks with explicit reasons
4. exit nonzero on failure

**Step 4: Verify scripts against dev**

Run:
```bash
pwsh sf-quality-db/database/deploy/Set-AuthRuntimeProbeFixtures.ps1 -Environment dev
pwsh sf-quality-db/database/deploy/Test-AuthRuntimeProbePreflight.ps1 -Environment dev
```
Expected: both pass; fixture identities are stable on rerun.

**Step 5: Commit DB changes**

Run:
```bash
git -C C:/Dev/sf-quality/sf-quality-db add database/deploy/Set-AuthRuntimeProbeFixtures.ps1 database/deploy/Test-AuthRuntimeProbePreflight.ps1 README.md .planning/STATE.md
git -C C:/Dev/sf-quality/sf-quality-db commit -m "Add dev auth runtime probe fixtures and preflight checks"
```

### Task 3: TDD API Canonical Permission + Guardrails

**Files:**
- Modify: `sf-quality-api/tests/SfQualityApi.Tests/Infrastructure/PermissionGateTests.cs`
- Modify: `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs`

**Step 1: Write failing test**

Add assertion expecting `WF.NCR.Submit` in guarded submit route source.

**Step 2: Run test to verify fail**

Run:
```bash
dotnet test C:/Dev/sf-quality/sf-quality-api/tests/SfQualityApi.Tests/SfQualityApi.Tests.csproj -v minimal --filter "FullyQualifiedName~PermissionGateTests"
```
Expected: fail while source still uses `NCR_SUBMIT`.

**Step 3: Write minimal implementation**

Replace route permission string in `NcrEndpoints.SubmitNcr` with `WF.NCR.Submit`.

**Step 4: Run tests to verify pass**

Run:
```bash
dotnet test C:/Dev/sf-quality/sf-quality-api/tests/SfQualityApi.Tests/SfQualityApi.Tests.csproj -v minimal --filter "FullyQualifiedName~PermissionGateTests"
```
Expected: pass.

**Step 5: Commit API contract fix**

Run:
```bash
git -C C:/Dev/sf-quality/sf-quality-api add src/SfQualityApi/Endpoints/NcrEndpoints.cs tests/SfQualityApi.Tests/Infrastructure/PermissionGateTests.cs
git -C C:/Dev/sf-quality/sf-quality-api commit -m "Use canonical WF.NCR.Submit permission code on submit route"
```

### Task 4: Add API Preflight + Quick Runtime Sanity Scripts

**Files:**
- Create: `sf-quality-api/scripts/Test-AuthRuntimeProbePreflight.ps1`
- Create: `sf-quality-api/scripts/Invoke-AuthRuntimeSanity.ps1`
- Modify: `sf-quality-api/README.md`
- Modify: `sf-quality-api/.planning/STATE.md`
- Modify: `sf-quality-api/.planning/phases/07-workflow-action-items/07-VERIFICATION.md`

**Step 1: Implement API preflight script**

Preflight script should:
1. read expected probe OIDs (defaults match DB fixture script)
2. call DB preflight script or run equivalent direct DB checks
3. validate local API launch prerequisites
4. fail fast with actionable messages

**Step 2: Implement quick sanity script**

Sanity script should:
1. launch API locally with dev connection string override
2. run 3 persona probes against submit validate-only route
3. assert `deny_user=403`, `allow_user!=403`, `admin_user!=403`
4. emit timestamped evidence files under `docs/plans/evidence/YYYY-MM-DD/runtime-auth-sanity/`

**Step 3: Verify script behavior**

Run:
```bash
pwsh C:/Dev/sf-quality/sf-quality-api/scripts/Test-AuthRuntimeProbePreflight.ps1 -Environment dev
pwsh C:/Dev/sf-quality/sf-quality-api/scripts/Invoke-AuthRuntimeSanity.ps1 -Environment dev
```
Expected: preflight pass and 3 expected status outcomes with evidence files written.

**Step 4: Commit script and docs updates**

Run:
```bash
git -C C:/Dev/sf-quality/sf-quality-api add scripts/Test-AuthRuntimeProbePreflight.ps1 scripts/Invoke-AuthRuntimeSanity.ps1 README.md .planning/STATE.md .planning/phases/07-workflow-action-items/07-VERIFICATION.md
git -C C:/Dev/sf-quality/sf-quality-api commit -m "Add auth runtime preflight and three-persona sanity automation"
```

### Task 5: Cross-Repo Verification and Publication

**Files:**
- Modify if needed: `sf-quality-api/.github/workflows/planning-contract-validation.yml`
- Modify if needed: `sf-quality-db/.github/workflows/sql-validation.yml`

**Step 1: Run required API verification**

Run:
```bash
dotnet build C:/Dev/sf-quality/sf-quality-api/SfQualityApi.sln -v minimal
dotnet test C:/Dev/sf-quality/sf-quality-api/tests/SfQualityApi.Tests/SfQualityApi.Tests.csproj -v minimal
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Test-DbContractReferences.ps1 -RepoRoot (Get-Location)"
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Test-OpenApiPublication.ps1 -RepoRoot (Get-Location)"
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly"
```
Expected: pass.

**Step 2: Run DB/static checks**

Run:
```bash
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-db'; pwsh database/deploy/Test-EnforcementRegistry.ps1 -RepoRoot (Get-Location)"
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-db'; pwsh database/deploy/Test-SqlStaticRules.ps1 -RepoRoot (Get-Location)"
```
Expected: pass.

**Step 3: Push branches and open PRs**

1. Push DB branch and open PR.
2. Push API branch and open PR.
3. Include decision doc and runtime evidence links in PR descriptions.

**Step 4: Merge and sync**

1. Merge PRs after checks.
2. Fast-forward local `main` branches.
3. Capture final status summary.

### Task 6: Final Operational Report

**Files:**
- Create/append: `docs/plans/evidence/YYYY-MM-DD/runtime-auth-sanity/README.md`

**Step 1: Record findings and residual risk**

Include:
1. what was fixed
2. what was verified
3. advisory->blocking rule baseline count start (`0/10`)

**Step 2: Provide operator runbook snippet**

Document exact command sequence for future agents:
1. fixture setup
2. preflight
3. sanity run
4. cycle checks

**Step 3: Final commit**

Run:
```bash
git -C C:/Dev/sf-quality add docs/plans/evidence
git -C C:/Dev/sf-quality commit -m "Add runtime auth sanity evidence and operator runbook"
```
