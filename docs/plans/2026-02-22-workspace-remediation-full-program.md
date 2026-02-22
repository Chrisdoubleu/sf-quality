# Workspace Remediation Full Program Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Execute the full remediation program (Stages 0-7) across workspace root and child repos with strict producer-first gates and no contract-chain breakage.

**Architecture:** This plan uses a strict stage-gated control model where workspace-root docs define sequence and gates, and each child repo implements only owned changes. Every consumer step is blocked until producer evidence is green and artifacts are refreshed when contract surfaces change. Boundary guardrails (DB cross-schema DML checks and API inline SQL checks) are permanent controls, not one-time cleanup.

**Tech Stack:** PowerShell 7, GitHub Actions YAML, SQL Server/T-SQL migrations, C# ASP.NET Core 9, Dapper, Markdown planning/governance docs.

---

Execution discipline: `@superpowers:test-driven-development`, `@superpowers:verification-before-completion`, `@superpowers:systematic-debugging`.

### Task 1: Create Program Execution Ledger

**Files:**
- Create: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Test: `Reference_Architecture/WORKSPACE_REMEDIATION_DEEP_DIVE_EXECUTION_SAFE_PLAN.md`

**Step 1: Write the failing test**

```powershell
Test-Path .\docs\plans\2026-02-22-workspace-remediation-execution-ledger.md
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: `pwsh -NoProfile -Command "Test-Path .\docs\plans\2026-02-22-workspace-remediation-execution-ledger.md"`  
Expected: `False`

**Step 3: Write minimal implementation**

```markdown
# Workspace Remediation Execution Ledger

Date: 2026-02-22
Program Doc: Reference_Architecture/WORKSPACE_REMEDIATION_DEEP_DIVE_EXECUTION_SAFE_PLAN.md

## Gate Status
- GATE-BASELINE: pending
- GATE-DB29-API35: pending
- GATE-API34-API35: pending
- GATE-DB25-DB26: pending
- GATE-DB26-DB261: pending
- GATE-ABAC-DECISION: pending
- GATE-DB261-API36: pending
- GATE-DB32-API7: pending
- GATE-SKILL-SYNC: pending
- GATE-QF-ENTRY: pending
- GATE-STABILITY-3PH: pending
```

**Step 4: Run test to verify it passes**

Run: `pwsh -NoProfile -Command "Test-Path .\docs\plans\2026-02-22-workspace-remediation-execution-ledger.md"`  
Expected: `True`

**Step 5: Commit**

```bash
git add docs/plans/2026-02-22-workspace-remediation-execution-ledger.md
git commit -m "docs: add remediation execution ledger scaffold"
```

### Task 2: Stage 0A Baseline Evidence Capture

**Files:**
- Create: `docs/plans/evidence/2026-02-22/stage-0a/README.md`
- Modify: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Test: `sf-quality-db/database/deploy/Test-EnforcementRegistry.ps1`
- Test: `sf-quality-db/database/deploy/Test-DbContractManifest.ps1`
- Test: `sf-quality-db/database/deploy/Test-SqlStaticRules.ps1`
- Test: `sf-quality-db/scripts/Invoke-CycleChecks.ps1`

**Step 1: Write the failing test**

```powershell
Test-Path .\docs\plans\evidence\2026-02-22\stage-0a\README.md
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: `pwsh -NoProfile -Command "Test-Path .\docs\plans\evidence\2026-02-22\stage-0a\README.md"`  
Expected: `False`

**Step 3: Write minimal implementation**

```powershell
# From workspace root
New-Item -ItemType Directory -Force -Path .\docs\plans\evidence\2026-02-22\stage-0a | Out-Null

Set-Location .\sf-quality-db
pwsh .\database\deploy\Test-EnforcementRegistry.ps1 -RepoRoot (Get-Location) *> ..\docs\plans\evidence\2026-02-22\stage-0a\db-enforcement.txt
pwsh .\database\deploy\Test-DbContractManifest.ps1 -RepoRoot (Get-Location) *> ..\docs\plans\evidence\2026-02-22\stage-0a\db-contract-manifest.txt
pwsh .\database\deploy\Test-SqlStaticRules.ps1 -RepoRoot (Get-Location) *> ..\docs\plans\evidence\2026-02-22\stage-0a\db-static-rules.txt
pwsh .\scripts\Invoke-CycleChecks.ps1 *> ..\docs\plans\evidence\2026-02-22\stage-0a\cycle-checks.txt
Set-Location ..
```

Update ledger entry for `GATE-BASELINE` with file references.

**Step 4: Run test to verify it passes**

Run: `pwsh -NoProfile -Command "Test-Path .\docs\plans\evidence\2026-02-22\stage-0a\README.md"`  
Expected: `True`

**Step 5: Commit**

```bash
git add docs/plans/evidence/2026-02-22/stage-0a docs/plans/2026-02-22-workspace-remediation-execution-ledger.md
git commit -m "docs: capture stage 0a baseline evidence"
```

### Task 3: Stage 0B API CI Scope Hardening

**Files:**
- Modify: `sf-quality-api/.github/workflows/planning-contract-validation.yml`
- Test: `sf-quality-api/.github/workflows/planning-contract-validation.yml`
- Test: `sf-quality-api/src/SfQualityApi/Program.cs`

**Step 1: Write the failing test**

```powershell
Select-String -Path .\sf-quality-api\.github\workflows\planning-contract-validation.yml -Pattern "src/\*\*" -Quiet
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: `pwsh -NoProfile -Command "Select-String -Path .\sf-quality-api\.github\workflows\planning-contract-validation.yml -Pattern 'src/\*\*' -Quiet"`  
Expected: `False`

**Step 3: Write minimal implementation**

```yaml
on:
  pull_request:
    paths:
      - ".planning/**"
      - "scripts/**"
      - "src/**"
      - "appsettings*.json"
      - "SfQualityApi.sln"
```

Keep existing `validation_mode` logic unchanged.

**Step 4: Run test to verify it passes**

Run: `pwsh -NoProfile -Command "Select-String -Path .\sf-quality-api\.github\workflows\planning-contract-validation.yml -Pattern 'src/\*\*' -Quiet"`  
Expected: `True`

**Step 5: Commit**

```bash
git -C sf-quality-api add .github/workflows/planning-contract-validation.yml
git -C sf-quality-api commit -m "ci: include runtime source paths in planning-contract validation triggers"
```

### Task 4: Stage 0B App CI Scope Hardening

**Files:**
- Modify: `sf-quality-app/.github/workflows/planning-contract-validation.yml`
- Test: `sf-quality-app/.github/workflows/planning-contract-validation.yml`

**Step 1: Write the failing test**

```powershell
Select-String -Path .\sf-quality-app\.github\workflows\planning-contract-validation.yml -Pattern "(src/\*\*|app/\*\*|components/\*\*)" -Quiet
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: `pwsh -NoProfile -Command "Select-String -Path .\sf-quality-app\.github\workflows\planning-contract-validation.yml -Pattern '(src/\*\*|app/\*\*|components/\*\*)' -Quiet"`  
Expected: `False`

**Step 3: Write minimal implementation**

```yaml
on:
  pull_request:
    paths:
      - ".planning/**"
      - "scripts/**"
      - "src/**"
      - "app/**"
      - "components/**"
      - "package.json"
      - "pnpm-lock.yaml"
```

Preserve advisory/blocking mode switch behavior.

**Step 4: Run test to verify it passes**

Run: `pwsh -NoProfile -Command "Select-String -Path .\sf-quality-app\.github\workflows\planning-contract-validation.yml -Pattern '(src/\*\*|app/\*\*|components/\*\*)' -Quiet"`  
Expected: `True`

**Step 5: Commit**

```bash
git -C sf-quality-app add .github/workflows/planning-contract-validation.yml
git -C sf-quality-app commit -m "ci: include runtime app paths in planning-contract validation triggers"
```

### Task 5: Stage 0C DB Cross-Schema DML Boundary Guard

**Files:**
- Create: `sf-quality-db/database/deploy/cross-schema-dml-allowlist.json`
- Modify: `sf-quality-db/database/deploy/Test-SqlStaticRules.ps1`
- Test: `sf-quality-db/database/deploy/Test-SqlStaticRules.ps1`
- Test: `sf-quality-db/database/migrations`

**Step 1: Write the failing test**

```powershell
Set-Location .\sf-quality-db
pwsh .\database\deploy\Test-SqlStaticRules.ps1 -RepoRoot (Get-Location)
Set-Location ..
```

Expected: does not yet enforce cross-schema DML ownership rule (missing violation class).

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: no `cross-schema dml` check output.

**Step 3: Write minimal implementation**

```json
{
  "allowed": [
    {
      "schema": "workflow",
      "target": "workflow.StatusHistory",
      "reason": "temporary compatibility window",
      "expiresOn": "2026-06-30"
    }
  ]
}
```

```powershell
# In Test-SqlStaticRules.ps1 (core rule idea)
if ($statementType -in @("INSERT","UPDATE","DELETE") -and $sourceSchema -ne $targetSchema) {
    if (-not (Test-AllowlistedCrossSchemaMutation -Source $sourceSchema -Target $targetObject -Allowlist $allowlist)) {
        throw "Cross-schema DML violation: $sourceSchema -> $targetObject"
    }
}
```

**Step 4: Run test to verify it passes**

Run: `Set-Location .\sf-quality-db; pwsh .\database\deploy\Test-SqlStaticRules.ps1 -RepoRoot (Get-Location); Set-Location ..`  
Expected: guard executes, only allowlisted exceptions pass.

**Step 5: Commit**

```bash
git -C sf-quality-db add database/deploy/Test-SqlStaticRules.ps1 database/deploy/cross-schema-dml-allowlist.json
git -C sf-quality-db commit -m "feat(db-guard): enforce cross-schema DML ownership with allowlist"
```

### Task 6: Stage 0C API Inline SQL Boundary Guard

**Files:**
- Create: `sf-quality-api/scripts/Test-InlineSqlBoundaries.ps1`
- Modify: `sf-quality-api/.github/workflows/planning-contract-validation.yml`
- Test: `sf-quality-api/scripts/Test-InlineSqlBoundaries.ps1`
- Test: `sf-quality-api/src/SfQualityApi/Endpoints`

**Step 1: Write the failing test**

```powershell
Test-Path .\sf-quality-api\scripts\Test-InlineSqlBoundaries.ps1
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: `pwsh -NoProfile -Command "Test-Path .\sf-quality-api\scripts\Test-InlineSqlBoundaries.ps1"`  
Expected: `False`

**Step 3: Write minimal implementation**

```powershell
param([string]$RepoRoot = (Get-Location))
$endpointFiles = Get-ChildItem -Path "$RepoRoot/src/SfQualityApi/Endpoints" -Filter *.cs -Recurse
$violations = @()
foreach ($f in $endpointFiles) {
  $txt = Get-Content $f.FullName -Raw
  if ($txt -match "CommandType\.Text" -or $txt -match "\$@\"" -or $txt -match "SELECT\s+.+\s+FROM") {
    $violations += $f.FullName
  }
}
if ($violations.Count -gt 0) {
  Write-Error ("Inline SQL boundary violations:`n" + ($violations -join "`n"))
  exit 1
}
Write-Host "No inline SQL boundary violations found."
```

Add workflow step:

```yaml
- name: Inline SQL boundary check
  shell: pwsh
  run: ./scripts/Test-InlineSqlBoundaries.ps1 -RepoRoot (Get-Location)
```

**Step 4: Run test to verify it passes**

Run: `Set-Location .\sf-quality-api; pwsh .\scripts\Test-InlineSqlBoundaries.ps1 -RepoRoot (Get-Location); Set-Location ..`  
Expected: exit code `0` when no violations, non-zero when violations exist.

**Step 5: Commit**

```bash
git -C sf-quality-api add scripts/Test-InlineSqlBoundaries.ps1 .github/workflows/planning-contract-validation.yml
git -C sf-quality-api commit -m "feat(api-guard): add inline SQL boundary checker and wire into CI"
```

### Task 7: Stage 0C Retire Global Patch Marker Check

**Files:**
- Modify: `sf-quality-db/.planning/enforcement/ENFORCEMENT-REGISTRY.json`
- Modify: `sf-quality-db/database/deploy/Test-EnforcementRegistry.ps1`
- Test: `sf-quality-db/.planning/enforcement/ENFORCEMENT-REGISTRY.json`
- Test: `sf-quality-db/database/deploy/Test-EnforcementRegistry.ps1`

**Step 1: Write the failing test**

```powershell
Select-String -Path .\sf-quality-db\.planning\enforcement\ENFORCEMENT-REGISTRY.json -Pattern "ENF-CLAUDE-GSD-GLOBAL-PATCHES" -Quiet
```

Expected: `True` (present before retirement)

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: `True`

**Step 3: Write minimal implementation**

```json
{
  "id": "ENF-REPO-GOVERNED-CHECKS-ONLY",
  "status": "active",
  "notes": "All active checks must be repository-governed and CI-safe."
}
```

```powershell
# Test-EnforcementRegistry.ps1
# Remove dependency on machine-local global patch markers.
$requiredChecks = @("ENF-REPO-GOVERNED-CHECKS-ONLY", "ENF-...other-active-checks...")
```

**Step 4: Run test to verify it passes**

Run:  
`pwsh -NoProfile -Command "Select-String -Path .\sf-quality-db\.planning\enforcement\ENFORCEMENT-REGISTRY.json -Pattern 'ENF-CLAUDE-GSD-GLOBAL-PATCHES' -Quiet"`  
Expected: `False`  

Run:  
`Set-Location .\sf-quality-db; pwsh .\database\deploy\Test-EnforcementRegistry.ps1 -RepoRoot (Get-Location); Set-Location ..`  
Expected: pass without machine-specific false positives.

**Step 5: Commit**

```bash
git -C sf-quality-db add .planning/enforcement/ENFORCEMENT-REGISTRY.json database/deploy/Test-EnforcementRegistry.ps1
git -C sf-quality-db commit -m "chore(enforcement): retire global patch marker check from active enforcement"
```

### Task 8: Stage 1 Execute DB Phase 23

**Files:**
- Modify: `sf-quality-db/.planning/STATE.md`
- Modify: `sf-quality-db/.planning/ROADMAP.md`
- Test: `sf-quality-db/database/deploy/Apply-Phase23*.ps1`
- Test: `sf-quality-db/database/deploy/Verify-Phase23*.sql`

**Step 1: Write the failing test**

```powershell
Set-Location .\sf-quality-db
Select-String -Path .\.planning\STATE.md -Pattern "Phase 23 complete" -Quiet
Set-Location ..
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: `False`

**Step 3: Write minimal implementation**

```powershell
Set-Location .\sf-quality-db
pwsh .\database\deploy\Apply-Phase23.ps1 -Environment dev
pwsh .\database\deploy\Verify-Phase23.ps1 -Environment dev
Set-Location ..
```

Update planning docs to reflect completion with date and evidence links.

**Step 4: Run test to verify it passes**

Run:  
`Set-Location .\sf-quality-db; Select-String -Path .\.planning\STATE.md -Pattern 'Phase 23 complete' -Quiet; Set-Location ..`  
Expected: `True`

**Step 5: Commit**

```bash
git -C sf-quality-db add .planning/STATE.md .planning/ROADMAP.md
git -C sf-quality-db commit -m "docs(db-phase23): record phase 23 completion"
```

### Task 9: Stage 1 Execute DB Phase 24 and Archive v2.0

**Files:**
- Modify: `sf-quality-db/.planning/STATE.md`
- Modify: `sf-quality-db/.planning/milestones/*`
- Modify: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Test: `sf-quality-db/database/deploy/Apply-Phase24*.ps1`
- Test: `sf-quality-db/scripts/Invoke-CycleChecks.ps1`

**Step 1: Write the failing test**

```powershell
Set-Location .\sf-quality-db
Select-String -Path .\.planning\STATE.md -Pattern "v2.0 archived" -Quiet
Set-Location ..
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: `False`

**Step 3: Write minimal implementation**

```powershell
Set-Location .\sf-quality-db
pwsh .\database\deploy\Apply-Phase24.ps1 -Environment dev
pwsh .\database\deploy\Verify-Phase24.ps1 -Environment dev
pwsh .\scripts\Invoke-CycleChecks.ps1
Set-Location ..
```

Update milestone docs and ledger for Stage 1 gate pass.

**Step 4: Run test to verify it passes**

Run:  
`Set-Location .\sf-quality-db; Select-String -Path .\.planning\STATE.md -Pattern 'v2.0 archived' -Quiet; Set-Location ..`  
Expected: `True`

**Step 5: Commit**

```bash
git -C sf-quality-db add .planning/STATE.md .planning/milestones
git -C sf-quality-db commit -m "docs(db-v2): archive v2.0 after phase 24 completion"
```

### Task 10: Stage 2 Reconcile Workspace Root Architecture Artifacts

**Files:**
- Modify: `Reference_Architecture/Execution_Plan.md`
- Modify: `Reference_Architecture/ENTERPRISE_ARCHITECTURE_ASSESSMENT_AND_REMEDIATION_PLAN.md`
- Modify: `Reference_Architecture/GSD_Seeding/DB_Planning/V3_PHASE_CONTEXTS/25-CONTEXT.md`
- Modify: `Reference_Architecture/GSD_Seeding/DB_Planning/V3_PHASE_CONTEXTS/26-CONTEXT.md`
- Modify: `Reference_Architecture/GSD_Seeding/DB_Planning/REQUIREMENTS_ADDITIONS.md`
- Modify: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Test: `Reference_Architecture/Execution_Plan.md`
- Test: `Reference_Architecture/ENTERPRISE_ARCHITECTURE_ASSESSMENT_AND_REMEDIATION_PLAN.md`

**Step 1: Write the failing test**

```powershell
$hasStruct = Select-String -Path .\Reference_Architecture\Execution_Plan.md -Pattern "STRUCT-" -Quiet
$hasApi36 = Select-String -Path .\Reference_Architecture\Execution_Plan.md -Pattern "API Phase 3.6" -Quiet
($hasStruct -and $hasApi36)
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: `pwsh -NoProfile -Command "$hasStruct = Select-String -Path .\Reference_Architecture\Execution_Plan.md -Pattern 'STRUCT-' -Quiet; $hasApi36 = Select-String -Path .\Reference_Architecture\Execution_Plan.md -Pattern 'API Phase 3.6' -Quiet; ($hasStruct -and $hasApi36)"`  
Expected: `False`

**Step 3: Write minimal implementation**

```markdown
### Reconciliation Addendum

- Namespace split: keep `ARCH-*`, add `STRUCT-01..10`.
- Phase 25 expanded for STRUCT-01/02/03.
- Phase 26.1 inserted for ABAC deepening gate outcomes.
- API Phase 3.6 inserted for ports/adapters refactor.
- Pre-QF gate requires STRUCT-10 FK policy decision.
```

**Step 4: Run test to verify it passes**

Run: command from Step 2  
Expected: `True`

**Step 5: Commit**

```bash
git add Reference_Architecture/Execution_Plan.md Reference_Architecture/ENTERPRISE_ARCHITECTURE_ASSESSMENT_AND_REMEDIATION_PLAN.md Reference_Architecture/GSD_Seeding/DB_Planning/V3_PHASE_CONTEXTS/25-CONTEXT.md Reference_Architecture/GSD_Seeding/DB_Planning/V3_PHASE_CONTEXTS/26-CONTEXT.md Reference_Architecture/GSD_Seeding/DB_Planning/REQUIREMENTS_ADDITIONS.md docs/plans/2026-02-22-workspace-remediation-execution-ledger.md
git commit -m "docs(ref-arch): reconcile execution plan and assessment with STRUCT namespace and API 3.6"
```

### Task 11: Stage 3 Initialize DB v3.0 Planning State

**Files:**
- Modify: `sf-quality-db/.planning/REQUIREMENTS.md`
- Modify: `sf-quality-db/.planning/ROADMAP.md`
- Modify: `sf-quality-db/.planning/PROJECT.md`
- Modify: `sf-quality-db/.planning/STATE.md`
- Modify: `sf-quality-db/.planning/phases/*`
- Test: `sf-quality-db/scripts/Test-PlanningConsistency.ps1`

**Step 1: Write the failing test**

```powershell
Set-Location .\sf-quality-db
Select-String -Path .\.planning\REQUIREMENTS.md -Pattern "STRUCT-01" -Quiet
Set-Location ..
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: `False`

**Step 3: Write minimal implementation**

```markdown
## STRUCT Requirements (v3.0)
- STRUCT-01 ... STRUCT-10
```

Add phase pointers and milestone references to roadmap/project/state files.

**Step 4: Run test to verify it passes**

Run:  
`Set-Location .\sf-quality-db; Select-String -Path .\.planning\REQUIREMENTS.md -Pattern 'STRUCT-01' -Quiet; pwsh .\scripts\Test-PlanningConsistency.ps1 -RepoRoot (Get-Location); Set-Location ..`  
Expected: `True` + planning consistency passes.

**Step 5: Commit**

```bash
git -C sf-quality-db add .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/PROJECT.md .planning/STATE.md .planning/phases
git -C sf-quality-db commit -m "docs(db-v3): initialize v3.0 planning with STRUCT requirement set"
```

### Task 12: Stage 4 Producer-First Gate DB29 then API3.5 Prereq

**Files:**
- Modify: `sf-quality-db/database/migrations/*phase29*`
- Modify: `sf-quality-db/.planning/contracts/db-contract-manifest.json`
- Modify: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Test: `sf-quality-db/scripts/Invoke-CycleChecks.ps1`

**Step 1: Write the failing test**

```powershell
Set-Location .\sf-quality-db
Select-String -Path .\.planning\contracts\db-contract-manifest.json -Pattern "audit\.ApiCallLog" -Quiet
Set-Location ..
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: `False`

**Step 3: Write minimal implementation**

```sql
CREATE TABLE audit.ApiCallLog (
  ApiCallLogId bigint IDENTITY(1,1) PRIMARY KEY,
  CorrelationId uniqueidentifier NOT NULL,
  Route nvarchar(256) NOT NULL,
  StatusCode int NOT NULL,
  CreatedAtUtc datetime2(7) NOT NULL DEFAULT sysutcdatetime()
);
```

Refresh manifest if contract surface changed; run cycle checks.

**Step 4: Run test to verify it passes**

Run:  
`Set-Location .\sf-quality-db; Select-String -Path .\.planning\contracts\db-contract-manifest.json -Pattern 'audit\.ApiCallLog' -Quiet; pwsh .\scripts\Invoke-CycleChecks.ps1; Set-Location ..`  
Expected: `True` + cycle checks pass.

**Step 5: Commit**

```bash
git -C sf-quality-db add database/migrations .planning/contracts/db-contract-manifest.json
git -C sf-quality-db commit -m "feat(db29): add ApiCallLog producer artifacts and publish contract updates"
```

### Task 13: Stage 4 API 3.4 Behavioral Completion

**Files:**
- Modify: `sf-quality-api/src/SfQualityApi/Middleware/CorrelationIdMiddleware.cs`
- Modify: `sf-quality-api/src/SfQualityApi/Middleware/ErrorHandlingMiddleware.cs`
- Modify: `sf-quality-api/src/SfQualityApi/Infrastructure/SqlErrorMapper.cs`
- Create: `sf-quality-api/tests/SfQualityApi.Tests/Middleware/CorrelationIdMiddlewareTests.cs`
- Create: `sf-quality-api/tests/SfQualityApi.Tests/Middleware/ErrorHandlingMiddlewareTests.cs`
- Create: `sf-quality-api/tests/SfQualityApi.Tests/Infrastructure/SqlErrorMapperTests.cs`
- Test: `sf-quality-api/tests/SfQualityApi.Tests`

**Step 1: Write the failing test**

```csharp
[Fact]
public void Maps_50414_To_Accepted()
{
    var status = SqlErrorMapper.Map(50414);
    Assert.Equal(StatusCodes.Status202Accepted, status);
}
```

Add tests for invalid correlation header and SQL error number stash.

**Step 2: Run test to verify it fails**

Run: `dotnet test .\sf-quality-api\tests\SfQualityApi.Tests\SfQualityApi.Tests.csproj -v minimal`  
Expected: failures for `50414 -> 202`, correlation GUID validation, and `SqlErrorNumber` context stash.

**Step 3: Write minimal implementation**

```csharp
// CorrelationIdMiddleware.cs
if (request.Headers.TryGetValue("X-Correlation-ID", out var raw) && Guid.TryParse(raw, out var parsed))
{
    context.TraceIdentifier = parsed.ToString();
}
else
{
    context.TraceIdentifier = Guid.NewGuid().ToString();
}
```

```csharp
// ErrorHandlingMiddleware.cs
context.Items["SqlErrorNumber"] = sqlErrorNumber;
```

```csharp
// SqlErrorMapper.cs
50414 => StatusCodes.Status202Accepted,
```

**Step 4: Run test to verify it passes**

Run:  
`dotnet test .\sf-quality-api\tests\SfQualityApi.Tests\SfQualityApi.Tests.csproj -v minimal`  
`dotnet build .\sf-quality-api\SfQualityApi.sln`  
Expected: all tests pass; build succeeds.

**Step 5: Commit**

```bash
git -C sf-quality-api add src/SfQualityApi/Middleware/CorrelationIdMiddleware.cs src/SfQualityApi/Middleware/ErrorHandlingMiddleware.cs src/SfQualityApi/Infrastructure/SqlErrorMapper.cs tests/SfQualityApi.Tests
git -C sf-quality-api commit -m "fix(api3.4): enforce correlation id, sql error stash, and 50414 accepted mapping"
```

### Task 14: Stage 5 DB Phase 25 Structural Boundary Hardening

**Files:**
- Modify: `sf-quality-db/database/migrations/*phase25*`
- Modify: `sf-quality-db/.planning/phases/25-*`
- Test: `sf-quality-db/database/deploy/Test-SqlStaticRules.ps1`

**Step 1: Write the failing test**

```powershell
Set-Location .\sf-quality-db
Select-String -Path .\database\migrations\*.sql -Pattern "quality\.StatusHistory|workflow\.usp_TransitionState" -SimpleMatch
Set-Location ..
```

Expected: direct foreign-context mutation pattern still present.

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: at least one hit.

**Step 3: Write minimal implementation**

```sql
-- Adapter-proc direction
CREATE PROCEDURE workflow.usp_RecordStatusChange
  @EntityType nvarchar(50),
  @EntityId bigint,
  @StatusCode nvarchar(50)
AS
BEGIN
  INSERT INTO workflow.StatusHistory (EntityType, EntityId, StatusCode)
  VALUES (@EntityType, @EntityId, @StatusCode);
END
```

Replace direct status history writes with adapter proc calls from owning context.

**Step 4: Run test to verify it passes**

Run:  
`Set-Location .\sf-quality-db; pwsh .\database\deploy\Test-SqlStaticRules.ps1 -RepoRoot (Get-Location); Set-Location ..`  
Expected: no unallowlisted cross-schema DML violations.

**Step 5: Commit**

```bash
git -C sf-quality-db add database/migrations .planning/phases
git -C sf-quality-db commit -m "feat(db25): add adapter-proc boundary and remove direct foreign-context status writes"
```

### Task 15: Stage 5 ABAC Decision Gate and Optional Phase 26.1

**Files:**
- Create: `sf-quality-db/.planning/decisions/ADR-2026-02-22-abac-decision-gate.md`
- Modify: `sf-quality-db/.planning/phases/26-*`
- Modify: `sf-quality-db/.planning/phases/26.1-*` (if implementing)
- Test: `sf-quality-db/.planning/decisions/ADR-2026-02-22-abac-decision-gate.md`
- Test: `sf-quality-db/database/deploy/Verify-Phase26*.sql`

**Step 1: Write the failing test**

```powershell
Test-Path .\sf-quality-db\.planning\decisions\ADR-2026-02-22-abac-decision-gate.md
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: `pwsh -NoProfile -Command "Test-Path .\sf-quality-db\.planning\decisions\ADR-2026-02-22-abac-decision-gate.md"`  
Expected: `False`

**Step 3: Write minimal implementation**

```markdown
# ADR: ABAC Deepening Decision Gate (2026-02-22)

## Trigger Checklist
- Multi-department ownership? [yes/no]
- SoD/audit finding? [yes/no]
- Same-plant visibility restrictions needed? [yes/no]
- External audit/customer ABAC ask? [yes/no]

## Decision
- Implement Phase 26.1: [yes/no]
- If no, revisit date: YYYY-MM-DD
```

If any trigger is `yes`, implement 26.1 with department/jurisdiction deny tests.

**Step 4: Run test to verify it passes**

Run:  
`pwsh -NoProfile -Command "Test-Path .\sf-quality-db\.planning\decisions\ADR-2026-02-22-abac-decision-gate.md"`  
Expected: `True`

If implemented:
`Set-Location .\sf-quality-db; pwsh .\database\deploy\Verify-Phase261.ps1 -Environment dev; Set-Location ..`  
Expected: deny tests pass.

**Step 5: Commit**

```bash
git -C sf-quality-db add .planning/decisions/ADR-2026-02-22-abac-decision-gate.md .planning/phases
git -C sf-quality-db commit -m "docs(db26): close ABAC decision gate and record implementation/defer path"
```

### Task 16: Stage 5 Complete DB 27/28/30 with Contract Gates

**Files:**
- Modify: `sf-quality-db/database/migrations/*phase27*`
- Modify: `sf-quality-db/database/migrations/*phase28*`
- Modify: `sf-quality-db/database/migrations/*phase30*`
- Modify: `sf-quality-db/.planning/contracts/db-contract-manifest.json` (if required)
- Modify: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Test: `sf-quality-db/scripts/Invoke-CycleChecks.ps1`

**Step 1: Write the failing test**

```powershell
Set-Location .\sf-quality-db
Select-String -Path .\.planning\STATE.md -Pattern "Phase 30 complete" -Quiet
Set-Location ..
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: `False`

**Step 3: Write minimal implementation**

```powershell
Set-Location .\sf-quality-db
pwsh .\database\deploy\Apply-Phase27.ps1 -Environment dev
pwsh .\database\deploy\Apply-Phase28.ps1 -Environment dev
pwsh .\database\deploy\Apply-Phase30.ps1 -Environment dev
pwsh .\scripts\Invoke-CycleChecks.ps1
Set-Location ..
```

Include outbox compatibility window handling in phase 28.

**Step 4: Run test to verify it passes**

Run:  
`Set-Location .\sf-quality-db; Select-String -Path .\.planning\STATE.md -Pattern 'Phase 30 complete' -Quiet; pwsh .\scripts\Invoke-CycleChecks.ps1; Set-Location ..`  
Expected: `True` + cycle checks pass.

**Step 5: Commit**

```bash
git -C sf-quality-db add database/migrations .planning/STATE.md .planning/contracts/db-contract-manifest.json
git -C sf-quality-db commit -m "feat(db27-30): complete structural phase chain with gated contract publication"
```

### Task 17: Stage 5 API Phase 3.6 Ports/Adapters Refactor

**Files:**
- Create: `sf-quality-api/src/SfQualityApi/Ports/INcrReadPort.cs`
- Create: `sf-quality-api/src/SfQualityApi/Ports/INcrWritePort.cs`
- Create: `sf-quality-api/src/SfQualityApi/Adapters/SqlNcrPortAdapter.cs`
- Modify: `sf-quality-api/src/SfQualityApi/Endpoints/NcrEndpoints.cs`
- Modify: `sf-quality-api/src/SfQualityApi/Program.cs`
- Create: `sf-quality-api/tests/SfQualityApi.Tests/Endpoints/NcrEndpointPortBoundaryTests.cs`
- Test: `sf-quality-api/scripts/Test-InlineSqlBoundaries.ps1`
- Test: `sf-quality-api/tests/SfQualityApi.Tests`

**Step 1: Write the failing test**

```csharp
[Fact]
public void Endpoints_Do_Not_Use_CommandTypeText()
{
    var endpointCode = File.ReadAllText("src/SfQualityApi/Endpoints/NcrEndpoints.cs");
    Assert.DoesNotContain("CommandType.Text", endpointCode);
}
```

**Step 2: Run test to verify it fails**

Run: `dotnet test .\sf-quality-api\tests\SfQualityApi.Tests\SfQualityApi.Tests.csproj -v minimal`  
Expected: endpoint boundary test fails.

**Step 3: Write minimal implementation**

```csharp
public interface INcrReadPort
{
    Task<NcrDto?> GetByIdAsync(long id, CancellationToken ct);
}

public sealed class SqlNcrPortAdapter : INcrReadPort, INcrWritePort
{
    private readonly IDbConnectionFactory _factory;
    public async Task<NcrDto?> GetByIdAsync(long id, CancellationToken ct)
        => await _factory.WithConnectionAsync(
            async cn => await cn.QueryFirstOrDefaultAsync<NcrDto>(
                "dbo.usp_Ncr_GetById",
                new { NcrId = id },
                commandType: CommandType.StoredProcedure));
}
```

Wire adapter into DI and endpoints.

**Step 4: Run test to verify it passes**

Run:  
`Set-Location .\sf-quality-api; pwsh .\scripts\Test-InlineSqlBoundaries.ps1 -RepoRoot (Get-Location); dotnet test .\tests\SfQualityApi.Tests\SfQualityApi.Tests.csproj -v minimal; dotnet build .\SfQualityApi.sln; Set-Location ..`  
Expected: boundary script pass, tests pass, build pass.

**Step 5: Commit**

```bash
git -C sf-quality-api add src/SfQualityApi/Ports src/SfQualityApi/Adapters src/SfQualityApi/Endpoints/NcrEndpoints.cs src/SfQualityApi/Program.cs tests/SfQualityApi.Tests/Endpoints/NcrEndpointPortBoundaryTests.cs
git -C sf-quality-api commit -m "feat(api3.6): add ports/adapters and remove endpoint inline SQL in target scope"
```

### Task 18: Stage 6 Parallel Track Planning Sync

**Files:**
- Modify: `sf-quality-db/.planning/ROADMAP.md`
- Modify: `sf-quality-api/.planning/ROADMAP.md`
- Modify: `sf-quality-app/.planning/ROADMAP.md`
- Modify: `sf-quality-app/.planning/STATE.md`
- Modify: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Test: `sf-quality-db/scripts/Invoke-CycleChecks.ps1`
- Test: `sf-quality-api/scripts/Test-PlanningConsistency.ps1`
- Test: `sf-quality-app/scripts/Test-PlanningConsistency.ps1`

**Step 1: Write the failing test**

```powershell
Set-Location .\sf-quality-app
Select-String -Path .\.planning\ROADMAP.md -Pattern "API contract readiness gate" -Quiet
Set-Location ..
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: `False`

**Step 3: Write minimal implementation**

```markdown
## Stage 6 gating
- DB 31/32/33 progress independently.
- API 5-10 require producer gate checks.
- App 1-10 only starts after API publication gates are green.
```

**Step 4: Run test to verify it passes**

Run:  
`Set-Location .\sf-quality-app; Select-String -Path .\.planning\ROADMAP.md -Pattern 'API contract readiness gate' -Quiet; pwsh .\scripts\Test-PlanningConsistency.ps1 -RepoRoot (Get-Location); Set-Location ..`  
Expected: `True` + planning consistency pass.

**Step 5: Commit**

```bash
git -C sf-quality-db add .planning/ROADMAP.md
git -C sf-quality-api add .planning/ROADMAP.md
git -C sf-quality-app add .planning/ROADMAP.md .planning/STATE.md
git -C sf-quality-db commit -m "docs(stage6): align db roadmap with parallel track gates"
git -C sf-quality-api commit -m "docs(stage6): align api roadmap with producer dependencies"
git -C sf-quality-app commit -m "docs(stage6): enforce api readiness gate before app execution"
```

### Task 19: Stage 7 Quality Forms Entry Gate and STRUCT-10

**Files:**
- Create: `Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/08_inspection_fk_policy.md`
- Modify: `Reference_Architecture/Execution_Plan.md`
- Modify: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Test: `Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/08_inspection_fk_policy.md`

**Step 1: Write the failing test**

```powershell
Test-Path .\Reference_Architecture\Quality_Forms_Module\04_packages\quality-inspection-forms-module-package\docs\08_inspection_fk_policy.md
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: `pwsh -NoProfile -Command "Test-Path .\Reference_Architecture\Quality_Forms_Module\04_packages\quality-inspection-forms-module-package\docs\08_inspection_fk_policy.md"`  
Expected: `False`

**Step 3: Write minimal implementation**

```markdown
# Inspection FK Policy (STRUCT-10)

## Hard FK Required
- Intra-bounded-context ownership relationships

## Soft Reference Required
- Cross-context integration links (with validation proc + audit trail)

## Entry Gate
- QF phases remain blocked until this policy is approved and referenced in Stage 7 gate checklist.
```

**Step 4: Run test to verify it passes**

Run: `pwsh -NoProfile -Command "Test-Path .\Reference_Architecture\Quality_Forms_Module\04_packages\quality-inspection-forms-module-package\docs\08_inspection_fk_policy.md"`  
Expected: `True`

**Step 5: Commit**

```bash
git add Reference_Architecture/Quality_Forms_Module/04_packages/quality-inspection-forms-module-package/docs/08_inspection_fk_policy.md Reference_Architecture/Execution_Plan.md docs/plans/2026-02-22-workspace-remediation-execution-ledger.md
git commit -m "docs(qf-gate): add STRUCT-10 inspection FK policy and gate linkage"
```

### Task 20: Anti-Drift Controls and Stability Evidence Gate

**Files:**
- Create: `docs/plans/2026-02-22-workspace-remediation-stability-report.md`
- Modify: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Modify: `sf-quality-db/.planning/phases/*/closeout*.md`
- Modify: `sf-quality-api/.planning/phases/*/closeout*.md`
- Test: `sf-quality-db/database/deploy/Test-SqlStaticRules.ps1`
- Test: `sf-quality-api/scripts/Test-InlineSqlBoundaries.ps1`

**Step 1: Write the failing test**

```powershell
Test-Path .\docs\plans\2026-02-22-workspace-remediation-stability-report.md
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: `pwsh -NoProfile -Command "Test-Path .\docs\plans\2026-02-22-workspace-remediation-stability-report.md"`  
Expected: `False`

**Step 3: Write minimal implementation**

```markdown
# Stability Report (GATE-STABILITY-3PH)

## Window
- Phase A: [id/date]
- Phase B: [id/date]
- Phase C: [id/date]

## Required Results
- DB cross-schema DML violations: 0
- API inline SQL violations: 0
- Allowlist additions: 0

## Decision
- Stability gate: PASS|FAIL
```

Add closeout checklist field:

```markdown
- Skill Sync: Updated|No Change (with rationale/date)
```

**Step 4: Run test to verify it passes**

Run:  
`Set-Location .\sf-quality-db; pwsh .\database\deploy\Test-SqlStaticRules.ps1 -RepoRoot (Get-Location); Set-Location ..`  
`Set-Location .\sf-quality-api; pwsh .\scripts\Test-InlineSqlBoundaries.ps1 -RepoRoot (Get-Location); Set-Location ..`  
Expected: both pass with zero violations for each phase in the 3-phase window.

**Step 5: Commit**

```bash
git add docs/plans/2026-02-22-workspace-remediation-stability-report.md docs/plans/2026-02-22-workspace-remediation-execution-ledger.md
git -C sf-quality-db add .planning/phases
git -C sf-quality-api add .planning/phases
git commit -m "docs(stability): add 3-phase anti-drift evidence gate and closeout sync fields"
```

### Task 21: Program Closeout Verification Sweep

**Files:**
- Modify: `docs/plans/2026-02-22-workspace-remediation-execution-ledger.md`
- Test: `sf-quality-db/scripts/Invoke-CycleChecks.ps1`
- Test: `sf-quality-db/database/deploy/Test-EnforcementRegistry.ps1`
- Test: `sf-quality-db/database/deploy/Test-SqlStaticRules.ps1`
- Test: `sf-quality-api/scripts/Test-PlanningConsistency.ps1`
- Test: `sf-quality-api/scripts/Test-DbContractReferences.ps1`
- Test: `sf-quality-api/scripts/Test-OpenApiPublication.ps1`
- Test: `sf-quality-app/scripts/Test-PlanningConsistency.ps1`
- Test: `sf-quality-app/scripts/Test-ApiContractReferences.ps1`

**Step 1: Write the failing test**

```powershell
Select-String -Path .\docs\plans\2026-02-22-workspace-remediation-execution-ledger.md -Pattern "Program Status: COMPLETE" -Quiet
```

Expected: `False`

**Step 2: Run test to verify it fails**

Run: same as Step 1  
Expected: `False`

**Step 3: Write minimal implementation**

```powershell
Set-Location .\sf-quality-db
pwsh .\database\deploy\Test-EnforcementRegistry.ps1 -RepoRoot (Get-Location)
pwsh .\database\deploy\Test-SqlStaticRules.ps1 -RepoRoot (Get-Location)
pwsh .\scripts\Invoke-CycleChecks.ps1
Set-Location ..

Set-Location .\sf-quality-api
pwsh .\scripts\Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)
pwsh .\scripts\Test-DbContractReferences.ps1 -RepoRoot (Get-Location)
pwsh .\scripts\Test-OpenApiPublication.ps1 -RepoRoot (Get-Location)
dotnet build .\SfQualityApi.sln
Set-Location ..

Set-Location .\sf-quality-app
pwsh .\scripts\Test-PlanningConsistency.ps1 -RepoRoot (Get-Location)
pwsh .\scripts\Test-ApiContractReferences.ps1 -RepoRoot (Get-Location)
Set-Location ..
```

Update ledger:

```markdown
Program Status: COMPLETE
Completion Date: 2026-02-22
```

**Step 4: Run test to verify it passes**

Run: command from Step 1  
Expected: `True` and all verification commands exit `0`.

**Step 5: Commit**

```bash
git add docs/plans/2026-02-22-workspace-remediation-execution-ledger.md
git commit -m "docs(closeout): mark full remediation program complete after final verification sweep"
```

---

## Notes for Execution Session

1. Run this plan in an isolated worktree (`@superpowers:using-git-worktrees`) before touching child repos.
2. Execute task-by-task with `@superpowers:executing-plans`; do not batch skip gates.
3. If any gate fails, immediately switch to `@superpowers:systematic-debugging` and follow amendment protocol.
