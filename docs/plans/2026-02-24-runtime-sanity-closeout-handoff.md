# Runtime Sanity Closeout Handoff (Next Chat)

Date: 2026-02-24
Workspace: `C:\Dev\sf-quality`
Goal: complete final runtime sanity proof and documentation closeout.

## 1) Current State Snapshot

### Repo Heads

- `sf-quality` (root) `master`: `a1d538c089ba2f1e7fb07c530c3b0a5eab703957`
- `sf-quality-db` `main`: `2a9720b3fec5bf408cebbfa2755cac7d6bdd6125`
- `sf-quality-api` `main`: `e620ddc99005ead6cd581d43814e433709613992`
- `sf-quality-app` `main`: `2f706f32c95e13107f83c21b27cbbecfb27f0d1a`

### Git Status

- `sf-quality-db`: clean
- `sf-quality-api`: clean
- `sf-quality-app`: clean
- workspace root: clean except pre-existing untracked `docs/Organization Forms Reference/`

### What Is Already Done

- Runtime defect fix merged in API:
  - PR: https://github.com/Chrisdoubleu/sf-quality-api/pull/7
  - Merge commit: `ac7c4fb08230d321453dbe29cf6208527cefcfba`
  - Fixes:
    1. PermissionGate now calls `security.usp_CheckPermission(@UserId,@PermissionCode,@PlantId)` via session context user id.
    2. Unknown SQL codes now map to `null` (middleware falls back to HTTP 500), not HTTP 0.
- Cross-repo realignment and catch-up waves merged:
  - Full execution ledger: `docs/plans/2026-02-24-cross-repo-realignment-execution-ledger.md`
  - DB freeze rule enforced: no Phase 35 feature work unless API/App blocker.
  - API Phase 4/6/8/9 scaffolds merged.
  - App Phase 1 + Phase 2/3 scaffolds merged.

## 2) Remaining Work (Only)

Complete runtime sanity proof for App -> API -> DB chain:

1. Non-admin deny probe (`403` expected).
2. Admin allow probe (non-`403` expected).

Then close documentation gaps and publish final closeout evidence.

## 3) Required Runtime Execution Steps

### Step A: Ensure Azure login and subscription

```powershell
az login
az account show --query "{subscription:name,id:id,tenant:tenantId,user:user.name}" -o table
```

Expected subscription: `Select Finishing APQP` (`0b1ff71a-737c-4463-82d3-dc50d92dd8d0`).

### Step B: Identify one admin and one non-admin OID in dev DB

Use SQL tooling you have available. If `sqlcmd` is installed:

```powershell
$server = "tcp:sql-sf-quality-0b1f-dev.database.windows.net,1433"
$db = "sqldb-quality-core-dev"
$sql = @"
SELECT
  u.CallerAzureOid,
  u.DisplayName,
  upa.AccessLevel,
  upa.IsActive
FROM security.AppUser u
LEFT JOIN security.UserPlantAccess upa
  ON upa.UserId = u.UserId
 AND upa.IsActive = 1
ORDER BY
  CASE WHEN upa.AccessLevel = 'Admin' THEN 0 ELSE 1 END,
  u.DisplayName;
"@
sqlcmd -S $server -d $db -G -Q $sql -W
```

Pick:
1. one `ADMIN_OID` (`AccessLevel='Admin'`)
2. one `NON_ADMIN_OID` (not admin)

If no admin row exists, mark `human_needed` in closeout and stop runtime proof at deny path.

### Step C: Run API locally on expected URL

In terminal 1:

```powershell
$env:ConnectionStrings__SqlDb = "Server=tcp:sql-sf-quality-0b1f-dev.database.windows.net,1433;Database=sqldb-quality-core-dev;Authentication=Active Directory Default;Encrypt=True;TrustServerCertificate=False;"
$env:ASPNETCORE_ENVIRONMENT = "Development"
dotnet run --project C:\Dev\sf-quality\sf-quality-api\src\SfQualityApi\SfQualityApi.csproj --urls http://localhost:5269
```

Health check (terminal 2):

```powershell
Invoke-WebRequest -Uri "http://localhost:5269/v1/diagnostics/health" -TimeoutSec 10 | Select-Object StatusCode,Content
```

Expect `StatusCode = 200`.

### Step D: Execute both probes

In terminal 2:

```powershell
$base = "http://localhost:5269"

function Invoke-SubmitProbe([string]$oid,[string]$label) {
  $payload = @{
    auth_typ = "aad"
    name_typ = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
    role_typ = "http://schemas.microsoft.com/ws/2008/06/identity/claims/role"
    claims = @(
      @{ typ = "http://schemas.microsoft.com/identity/claims/objectidentifier"; val = $oid },
      @{ typ = "name"; val = $label }
    )
  } | ConvertTo-Json -Depth 6 -Compress

  $principal = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
  $response = Invoke-WebRequest `
    -Uri "$base/v1/ncr/999999/submit?isValidateOnly=true" `
    -Method Post `
    -Headers @{ "X-MS-CLIENT-PRINCIPAL" = $principal } `
    -ContentType "application/json" `
    -Body "{}" `
    -SkipHttpErrorCheck

  [PSCustomObject]@{
    label = $label
    status = $response.StatusCode
    body = $response.Content
  }
}

$nonAdmin = Invoke-SubmitProbe "<NON_ADMIN_OID>" "non-admin-deny"
$admin = Invoke-SubmitProbe "<ADMIN_OID>" "admin-allow"
$nonAdmin
$admin
```

Expected:
1. `non-admin-deny` -> `403`
2. `admin-allow` -> not `403` (commonly `404` for NCR not found, which is acceptable allow-path proof)

## 4) Documentation/Evidence Updates Required After Probe

Update these files with actual probe results:

1. `sf-quality-api/.planning/phases/07-workflow-action-items/07-VERIFICATION.md`
2. `sf-quality-api/.planning/STATE.md`
3. `docs/plans/2026-02-24-cross-repo-realignment-execution-ledger.md`
4. Create runtime evidence file:
   - `docs/plans/evidence/2026-02-24-runtime-sanity-closeout.md`

Evidence file should include:
1. exact commands run
2. statuses and bodies for both probes
3. correlation IDs
4. explicit PASS/FAIL against expected outcomes
5. `human_needed` note only if admin identity unavailable

## 5) Verification Commands Before Final Claim

### API repo

```powershell
dotnet build C:\Dev\sf-quality\sf-quality-api\SfQualityApi.sln -v minimal
dotnet test C:\Dev\sf-quality\sf-quality-api\tests\SfQualityApi.Tests\SfQualityApi.Tests.csproj -v minimal
pwsh C:\Dev\sf-quality\sf-quality-api\scripts\Test-DbContractReferences.ps1 -RepoRoot C:\Dev\sf-quality\sf-quality-api
pwsh C:\Dev\sf-quality\sf-quality-api\scripts\Test-OpenApiPublication.ps1 -RepoRoot C:\Dev\sf-quality\sf-quality-api
pwsh C:\Dev\sf-quality\sf-quality-api\scripts\Invoke-CycleChecks.ps1 -ChangedOnly
```

### Workspace closeout check

From canonical sibling path:

```powershell
pwsh C:\Dev\sf-quality\sf-quality-api\scripts\Invoke-CycleChecks.ps1 -ChangedOnly
```

## 6) Branch/PR Closeout Pattern

1. Use feature branch(es), not `main/master`.
2. Commit docs/evidence updates.
3. Open PR(s), merge to `main`/`master`.
4. Fast-forward local branches.
5. Confirm final git status clean.

## 7) Copy/Paste Prompt for Next Chat

Use this exact prompt in the next chat:

```text
Continue in C:\Dev\sf-quality. Use this handoff as source of truth:
docs/plans/2026-02-24-runtime-sanity-closeout-handoff.md

Objective: finish runtime sanity closeout only.

Do:
1) Run local API with real dev DB connection.
2) Execute two probes on POST /v1/ncr/999999/submit?isValidateOnly=true:
   - one non-admin deny (expect 403)
   - one admin allow (expect non-403)
3) Capture command outputs + correlation IDs into docs/plans/evidence/2026-02-24-runtime-sanity-closeout.md
4) Update:
   - sf-quality-api/.planning/phases/07-workflow-action-items/07-VERIFICATION.md
   - sf-quality-api/.planning/STATE.md
   - docs/plans/2026-02-24-cross-repo-realignment-execution-ledger.md
5) Run verification commands (build/tests/contract checks/cycle checks).
6) Commit, push, PR, merge, sync local main/master.

Required final output:
- findings/risks first
- probe results (status/body)
- verification outputs (key lines)
- PR URL(s) + merge SHA(s)
- final local git status for root/db/api/app
- explicit statement whether cross-repo sanity is fully closed
```
