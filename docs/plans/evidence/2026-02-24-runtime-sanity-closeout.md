# Runtime Sanity Closeout Evidence

Date: 2026-02-24
Workspace: `C:\Dev\sf-quality`
Objective: verify runtime sanity for `POST /v1/ncr/999999/submit?isValidateOnly=true` with one deny-path probe and one allow-path probe.

## Commands Run

```powershell
az account show --query "{subscription:name,id:id,tenant:tenantId,user:user.name}" -o json
```

```powershell
$server = "tcp:sql-sf-quality-0b1f-dev.database.windows.net,1433"
$db = "sqldb-quality-core-dev"
$user = "chris.walsh@selectfinishing.ca"

sqlcmd -S $server -d $db -G -U $user -Q @"
SELECT
  CONVERT(varchar(36),u.AzureAdObjectId) AS CallerAzureOid,
  u.DisplayName,
  upa.AccessLevel,
  upa.PlantId,
  u.IsActive
FROM dbo.AppUser u
LEFT JOIN dbo.UserPlantAccess upa
  ON upa.UserId = u.AppUserId
WHERE u.IsActive = 1
ORDER BY
  CASE WHEN upa.AccessLevel = 'Admin' THEN 0 ELSE 1 END,
  u.DisplayName;
"@ -W
```

```powershell
sqlcmd -S $server -d $db -G -U $user -Q @"
SELECT
  p.PermissionCode,
  rp.GrantType,
  r.RoleName,
  r.RoleId,
  ur.UserId,
  CONVERT(varchar(36),u.AzureAdObjectId) AS CallerAzureOid,
  u.DisplayName,
  ur.PlantId,
  ur.IsActive AS UserRoleIsActive
FROM security.Permission p
JOIN security.RolePermission rp
  ON rp.PermissionId = p.PermissionId
 AND rp.IsActive = 1
JOIN dbo.Role r
  ON r.RoleId = rp.RoleId
 AND r.IsActive = 1
LEFT JOIN dbo.UserRole ur
  ON ur.RoleId = r.RoleId
 AND ur.IsActive = 1
LEFT JOIN dbo.AppUser u
  ON u.AppUserId = ur.UserId
 AND u.IsActive = 1
WHERE p.PermissionCode = 'WF.NCR.Submit'
  AND p.IsActive = 1
ORDER BY r.RoleName, u.DisplayName;
"@ -W
```

```powershell
sqlcmd -S $server -d $db -G -U $user -Q "
SELECT COUNT(*) AS ActiveUserRoles FROM dbo.UserRole WHERE IsActive=1;
SELECT COUNT(*) AS ActiveUserPlantAccess FROM dbo.UserPlantAccess;
" -W
```

```powershell
$apiProject = "C:/Dev/sf-quality/sf-quality-api/src/SfQualityApi/SfQualityApi.csproj"
$conn = "Server=tcp:sql-sf-quality-0b1f-dev.database.windows.net,1433;Database=sqldb-quality-core-dev;Authentication=Active Directory Default;Encrypt=True;TrustServerCertificate=False;"
$adminOid = "7CB31D63-9EA5-43EB-BCC3-BE10CA6F6C03"
$nonAdminOid = "2FA67B5A-5880-4D2A-BFAD-6F5D29EBF101"

$job = Start-Job -ScriptBlock {
  param($proj,$connection)
  $env:ConnectionStrings__SqlDb = $connection
  $env:ASPNETCORE_ENVIRONMENT = "Development"
  dotnet run --project $proj --urls http://localhost:5269
} -ArgumentList $apiProject,$conn

$health = Invoke-WebRequest -Uri "http://localhost:5269/v1/diagnostics/health" -TimeoutSec 5

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
  Invoke-WebRequest -Uri "http://localhost:5269/v1/ncr/999999/submit?isValidateOnly=true" `
    -Method Post `
    -Headers @{ "X-MS-CLIENT-PRINCIPAL" = $principal } `
    -ContentType "application/json" `
    -Body "{}" `
    -SkipHttpErrorCheck
}

$nonAdmin = Invoke-SubmitProbe $nonAdminOid "non-admin-deny"
$admin = Invoke-SubmitProbe $adminOid "admin-allow"
Stop-Job -Id $job.Id
Remove-Job -Id $job.Id -Force
```

## Environment/Identity Discovery Results

- Azure account:
  - subscription: `Select Finishing APQP`
  - subscription id: `0b1ff71a-737c-4463-82d3-dc50d92dd8d0`
  - tenant: `337332b1-0eda-4b85-9505-52bc6e160e90`
  - user: `chris.walsh@selectfinishing.ca`
- Active users discovered in `dbo.AppUser`: 4 rows (`Runtime Probe - Admin`, `Runtime Probe - Allow`, `Runtime Probe - Deny`, `Phase 27 Timeout Processor Runtime`).
- `dbo.UserRole` active assignments: `0`.
- `dbo.UserPlantAccess` active assignments: `0`.
- `WF.NCR.Submit` permission grants exist at role level, but all returned rows had `UserId = NULL` (no active user-role links).

## Runtime Probe Results

### Health check

- Endpoint: `GET /v1/diagnostics/health`
- Status: `200`
- Body:

```json
{"service":"sf-quality-api","status":"healthy","timestamp":"2026-02-24T19:56:17.6553902Z","correlationId":"2af594ff-d076-4f87-a4d3-032ee84c0e76"}
```

### Probe 1: non-admin-deny

- OID: `2FA67B5A-5880-4D2A-BFAD-6F5D29EBF101`
- Status: `403`
- Body:

```json
{"error":"No role grants permission: WF.NCR.Submit","correlationId":"41f59491-19e7-49de-8297-72e6f8969b75"}
```

- Correlation ID: `41f59491-19e7-49de-8297-72e6f8969b75`

### Probe 2: admin-allow

- OID: `7CB31D63-9EA5-43EB-BCC3-BE10CA6F6C03`
- Status: `403`
- Body:

```json
{"error":"No role grants permission: WF.NCR.Submit","correlationId":"5df45e3f-5358-4d77-8b9f-9d3719157998"}
```

- Correlation ID: `5df45e3f-5358-4d77-8b9f-9d3719157998`

## Expected vs Actual

1. Non-admin deny probe expected `403`: `PASS` (`403` observed)
2. Admin allow probe expected non-`403`: `FAIL` (`403` observed)

Overall runtime sanity closeout: `PARTIAL` (deny-path verified, allow-path blocked by missing active admin-role mapping in dev DB).

## human_needed

- `human_needed = true`
- Reason: no active user-role or user-plant access assignments currently exist in dev DB, so no discoverable identity can satisfy allow-path proof for `WF.NCR.Submit`.
- Required follow-up: provision at least one active test user with a role granting `WF.NCR.Submit`, then rerun admin allow probe.
