# Cross-Repo Realignment and Catch-Up Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enforce one canonical execution sequence across `sf-quality-db`, `sf-quality-api`, and `sf-quality-app` by freezing non-blocker DB Phase 35 work, realigning stale planning/status docs, then completing API phases `4 -> 6 -> 8/9` while starting App phases `1 -> 2/3` in lockstep.

**Architecture:** Use wave-based delivery with strict producer/consumer boundaries (`DB -> API -> App`), TDD in API/App code waves, and mandatory post-wave closeout (tests, cycle checks, evidence note, PR merge). DB remains schema-frozen at Phase 34 unless an explicit API/App blocker is proven.

**Tech Stack:** PowerShell 7, .NET 9 + xUnit, Next.js 15 + TypeScript, existing planning/contract scripts, OpenAPI artifacts, GitHub PR workflow.

---

## Canonical Sequence (What Should Be True)

1. `sf-quality-db` should remain at **Phase 34 completed**; **Phase 35 is on hold** unless a blocker for API/App is documented with evidence.
2. `sf-quality-api` should complete unfinished domain phases in this order: **4, then 6, then 8/9**.
3. `sf-quality-app` should begin **Phase 1** as soon as API catch-up starts, then execute **Phase 2 and Phase 3**.
4. Every wave closes with: repo tests, cross-repo cycle checks, evidence note, PR, merge, local main sync.

---

### Task 1: Lock Rule and Baseline Realignment Wave

**Files:**
- Create: `docs/plans/2026-02-24-cross-repo-realignment-execution-ledger.md`
- Modify: `sf-quality-db/.planning/STATE.md`
- Modify: `sf-quality-db/.planning/ROADMAP.md`
- Modify: `sf-quality-api/.planning/STATE.md`
- Modify: `sf-quality-api/.planning/ROADMAP.md`
- Modify: `sf-quality-app/.planning/STATE.md`
- Modify: `sf-quality-app/.planning/ROADMAP.md`

**Step 1: Capture baseline drift evidence**

Run:
```powershell
git -C C:/Dev/sf-quality/sf-quality-db status --short --branch
git -C C:/Dev/sf-quality/sf-quality-api status --short --branch
git -C C:/Dev/sf-quality/sf-quality-app status --short --branch
```
Expected: clean baselines before realignment edits.

**Step 2: Add rule text and canonical sequence**

Update state/roadmap docs to explicitly state:
1. No new DB Phase 35 feature work unless API/App blocker.
2. API catch-up order `4 -> 6 -> 8/9`.
3. App startup order `1 -> 2 -> 3` once API catch-up begins.

**Step 3: Record numeric correction map**

Write in ledger:
1. Current observed status.
2. Correct canonical status.
3. Reason for correction.
4. Date and author.

**Step 4: Verify planning consistency**

Run:
```powershell
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-db'; pwsh scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)"
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)"
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-app'; pwsh scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)"
```
Expected: all PASS.

**Step 5: Commit realignment wave**

Run:
```powershell
git -C C:/Dev/sf-quality add docs/plans/2026-02-24-cross-repo-realignment-execution-ledger.md
git -C C:/Dev/sf-quality/sf-quality-db add .planning/STATE.md .planning/ROADMAP.md
git -C C:/Dev/sf-quality/sf-quality-api add .planning/STATE.md .planning/ROADMAP.md
git -C C:/Dev/sf-quality/sf-quality-app add .planning/STATE.md .planning/ROADMAP.md
```
Then commit in each touched repo/workspace with message prefix `docs(plan):`.

### Task 2: Close Runtime Sanity Proof Gap Before New Feature Waves

**Files:**
- Modify: `sf-quality-api/.planning/phases/07-workflow-action-items/07-VERIFICATION.md`
- Modify: `sf-quality-api/.planning/STATE.md`
- Create: `docs/plans/evidence/2026-02-24-runtime-sanity-closeout.md`

**Step 1: Re-run non-admin deny probe (automated)**

Run against API dev instance:
```powershell
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly"
```
Expected: baseline checks pass before runtime probes.

**Step 2: Run admin allow probe**

Use admin session with `X-MS-CLIENT-PRINCIPAL` payload and call:
`POST /v1/ncr/{id}/submit?isValidateOnly=true`.
Expected: non-403 response proving allow-path reaches DB chain.

**Step 3: Record exact probe evidence**

Write status/body/correlation ID for both probes into the evidence file.

**Step 4: Update verification metadata**

Set phase verification status and note whether admin probe was automated or `human_needed` with manual command proof.

**Step 5: Commit runtime closeout docs**

Commit API planning updates and root evidence note.

### Task 3: API Catch-Up Wave A (Phase 4 Completion)

**Files:**
- Create: `sf-quality-api/tests/SfQualityApi.Tests/Endpoints/CapaEndpointsTests.cs`
- Create: `sf-quality-api/tests/SfQualityApi.Tests/Endpoints/ComplaintEndpointsTests.cs`
- Create: `sf-quality-api/src/SfQualityApi/Endpoints/CapaEndpoints.cs`
- Create: `sf-quality-api/src/SfQualityApi/Endpoints/ComplaintEndpoints.cs`
- Modify: `sf-quality-api/src/SfQualityApi/Program.cs`
- Modify: `sf-quality-api/.planning/phases/04-capa-complaint/04-RESEARCH.md`
- Modify: `sf-quality-api/.planning/phases/04-capa-complaint/04-VERIFICATION.md`
- Modify: `sf-quality-api/.planning/STATE.md`
- Modify: `sf-quality-api/.planning/ROADMAP.md`

**Step 1: Write failing endpoint mapping tests**

Test assertions should mirror existing endpoint tests:
1. endpoint file exists
2. `MapGroup("/capa")` / `MapGroup("/complaint")`
3. `.RequireAuthorization()`
4. `Program.cs` contains `v1.MapCapaEndpoints();` and `v1.MapComplaintEndpoints();`

**Step 2: Run targeted tests to confirm RED**

Run:
```powershell
dotnet test C:/Dev/sf-quality/sf-quality-api/tests/SfQualityApi.Tests/SfQualityApi.Tests.csproj -v minimal --filter "FullyQualifiedName~CapaEndpointsTests|FullyQualifiedName~ComplaintEndpointsTests"
```
Expected: FAIL because files/mappings do not exist yet.

**Step 3: Implement minimal endpoint groups**

Add CAPA and complaint endpoint extension classes as thin proc/view gateway routes only (no business-rule duplication).

**Step 4: Run API verification suite**

Run:
```powershell
dotnet build C:/Dev/sf-quality/sf-quality-api/SfQualityApi.sln -v minimal
dotnet test C:/Dev/sf-quality/sf-quality-api/tests/SfQualityApi.Tests/SfQualityApi.Tests.csproj -v minimal
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Test-DbContractReferences.ps1 -RepoRoot (Get-Location)"
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Test-OpenApiPublication.ps1 -RepoRoot (Get-Location)"
```
Expected: all PASS.

**Step 5: Close wave with cycle checks and commit**

Run:
```powershell
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly"
```
Then commit with message prefix `feat(api-phase4):`.

### Task 4: API Catch-Up Wave B (Phase 6 RCA Tools)

**Files:**
- Create: `sf-quality-api/tests/SfQualityApi.Tests/Endpoints/RcaEndpointsTests.cs`
- Create: `sf-quality-api/src/SfQualityApi/Endpoints/RcaEndpoints.cs`
- Modify: `sf-quality-api/src/SfQualityApi/Program.cs`
- Modify: `sf-quality-api/.planning/phases/06-rca-tools/06-RESEARCH.md`
- Modify: `sf-quality-api/.planning/phases/06-rca-tools/06-VERIFICATION.md`
- Modify: `sf-quality-api/.planning/STATE.md`
- Modify: `sf-quality-api/.planning/ROADMAP.md`

**Step 1: Write failing route-group tests first**

Assert file existence, route group mapping (`/rca`), authorization, and program registration.

**Step 2: Confirm RED**

Run:
```powershell
dotnet test C:/Dev/sf-quality/sf-quality-api/tests/SfQualityApi.Tests/SfQualityApi.Tests.csproj -v minimal --filter "FullyQualifiedName~RcaEndpointsTests"
```
Expected: FAIL before implementation.

**Step 3: Implement minimal RCA endpoint group**

Keep implementation thin and contract-bound to DB manifest objects only.

**Step 4: Run full API verification**

Re-run build/tests/contract checks and OpenAPI publication check.

**Step 5: Run cycle checks and commit**

Run `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` from `sf-quality-api`, then commit with prefix `feat(api-phase6):`.

### Task 5: API Catch-Up Wave C (Phases 8 and 9)

**Files:**
- Create: `sf-quality-api/tests/SfQualityApi.Tests/Endpoints/KnowledgeEndpointsTests.cs`
- Create: `sf-quality-api/tests/SfQualityApi.Tests/Endpoints/DashboardEndpointsTests.cs`
- Create: `sf-quality-api/src/SfQualityApi/Endpoints/KnowledgeEndpoints.cs`
- Create: `sf-quality-api/src/SfQualityApi/Endpoints/DashboardEndpoints.cs`
- Modify: `sf-quality-api/src/SfQualityApi/Program.cs`
- Modify: `sf-quality-api/.planning/phases/08-knowledge-traceability/08-RESEARCH.md`
- Modify: `sf-quality-api/.planning/phases/08-knowledge-traceability/08-VERIFICATION.md`
- Modify: `sf-quality-api/.planning/phases/09-dashboards-views/09-RESEARCH.md`
- Modify: `sf-quality-api/.planning/phases/09-dashboards-views/09-VERIFICATION.md`
- Modify: `sf-quality-api/.planning/STATE.md`
- Modify: `sf-quality-api/.planning/ROADMAP.md`

**Step 1: Write failing tests for both endpoint groups**

Mirror existing endpoint test style for route group + program mapping coverage.

**Step 2: Confirm RED**

Run:
```powershell
dotnet test C:/Dev/sf-quality/sf-quality-api/tests/SfQualityApi.Tests/SfQualityApi.Tests.csproj -v minimal --filter "FullyQualifiedName~KnowledgeEndpointsTests|FullyQualifiedName~DashboardEndpointsTests"
```
Expected: FAIL pre-implementation.

**Step 3: Implement knowledge and dashboard endpoint groups**

Keep API behavior as pass-through to DB views/procs with query governor and pagination conventions where applicable.

**Step 4: Run full API verification + publication checks**

Build/tests/contract scripts/OpenAPI publication must all pass.

**Step 5: Run cycle checks and commit**

Run `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` from `sf-quality-api`, then commit with prefix `feat(api-phase8-9):`.

### Task 6: App Start Wave (Phase 1 Foundation)

**Files:**
- Create: `sf-quality-app/package.json`
- Create: `sf-quality-app/tsconfig.json`
- Create: `sf-quality-app/next.config.ts`
- Create: `sf-quality-app/postcss.config.mjs`
- Create: `sf-quality-app/eslint.config.mjs`
- Create: `sf-quality-app/src/app/layout.tsx`
- Create: `sf-quality-app/src/app/page.tsx`
- Create: `sf-quality-app/src/lib/api.ts`
- Create: `sf-quality-app/src/lib/auth.ts`
- Modify: `sf-quality-app/.planning/phases/01-frontend-foundation-contract-tooling/01-RESEARCH.md`
- Modify: `sf-quality-app/.planning/phases/01-frontend-foundation-contract-tooling/01-VERIFICATION.md`
- Modify: `sf-quality-app/.planning/STATE.md`
- Modify: `sf-quality-app/.planning/ROADMAP.md`

**Step 1: Create failing contract-boundary test**

Create a small test (or script assertion) proving API calls occur only via `src/lib/api.ts` and not directly in browser components.

**Step 2: Confirm RED**

Run the new test/script and confirm failure before implementation.

**Step 3: Scaffold minimal Next.js App Router foundation**

Implement only phase-1 requirements:
1. buildable app skeleton
2. strict TypeScript
3. server-only auth/token boundary helpers
4. pinned API contract snapshot usage path

**Step 4: Run app verification**

Run:
```powershell
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-app'; pwsh scripts/Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)"
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-app'; pwsh scripts/Test-ApiContractReferences.ps1 -RepoRoot (Get-Location)"
```
Expected: PASS.

**Step 5: Run cycle checks and commit**

Run `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` from `sf-quality-app`, then commit with prefix `feat(app-phase1):`.

### Task 7: App Catch-Up Wave (Phases 2 and 3)

**Files:**
- Create: `sf-quality-app/src/components/layout/AppShell.tsx`
- Create: `sf-quality-app/src/components/layout/AppNav.tsx`
- Create: `sf-quality-app/src/components/layout/AppHeader.tsx`
- Create: `sf-quality-app/src/app/(auth)/layout.tsx`
- Create: `sf-quality-app/src/app/(auth)/dashboard/page.tsx`
- Create: `sf-quality-app/src/lib/session.ts`
- Modify: `sf-quality-app/src/lib/auth.ts`
- Modify: `sf-quality-app/src/lib/api.ts`
- Modify: `sf-quality-app/.planning/phases/02-design-system-shell-navigation/02-RESEARCH.md`
- Modify: `sf-quality-app/.planning/phases/02-design-system-shell-navigation/02-VERIFICATION.md`
- Modify: `sf-quality-app/.planning/phases/03-authentication-session-ux/03-RESEARCH.md`
- Modify: `sf-quality-app/.planning/phases/03-authentication-session-ux/03-VERIFICATION.md`
- Modify: `sf-quality-app/.planning/STATE.md`
- Modify: `sf-quality-app/.planning/ROADMAP.md`

**Step 1: Write failing tests for shell + auth propagation behavior**

Add tests that assert:
1. authenticated layout exists
2. session claims/token extraction path exists server-side
3. delegated token forwarding function is used by API client

**Step 2: Confirm RED**

Run targeted tests and confirm they fail pre-implementation.

**Step 3: Implement minimal phase-2/3 behavior**

Implement:
1. design shell and navigation primitives
2. server-side Easy Auth session parsing
3. delegated token forwarding to API boundary

**Step 4: Run app verification**

Run planning/contract scripts and app test/build commands introduced in phase 1.

**Step 5: Run cycle checks and commit**

Run `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` from `sf-quality-app`, then commit with prefix `feat(app-phase2-3):`.

### Task 8: Standardized Wave Closeout (Run After Every Wave)

**Files:**
- Modify (append each wave): `docs/plans/2026-02-24-cross-repo-realignment-execution-ledger.md`

**Step 1: Verify repo-local checks**

Run relevant repo tests and required planning/contract scripts.

**Step 2: Verify cross-repo cycle checks**

Run:
```powershell
pwsh -NoProfile -Command "Set-Location 'C:/Dev/sf-quality/sf-quality-api'; pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly"
```
Expected: PASS or explicit scoped SKIPs only.

**Step 3: Append evidence entry**

Record:
1. branch name
2. commands run
3. key PASS lines
4. risks/human-needed flags
5. PR URL and merge commit SHA

**Step 4: Merge and sync**

For each touched repo:
```powershell
git checkout main
git pull --ff-only
```
Expected: local `main` aligned with remote merge commit.

**Step 5: Confirm clean state**

Run `git status --short --branch` and record final state in ledger.

---

## DB Blocker Exception Protocol (Only If Needed)

If API/App wave discovers a true DB blocker:
1. Add blocker entry in ledger with command evidence.
2. Open a minimal DB unblock wave (single-purpose migration or data fix).
3. Re-run DB + API + App cycle checks.
4. Merge unblock first, then resume API/App wave.

No other DB Phase 35 work is allowed during this catch-up program.
