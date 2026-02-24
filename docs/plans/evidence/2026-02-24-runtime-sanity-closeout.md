# Runtime Sanity Closeout Evidence

Date: 2026-02-24
Workspace: `C:\Dev\sf-quality`
Objective: verify runtime sanity for `POST /v1/ncr/999999/submit?isValidateOnly=true` with one deny-path probe and one allow-path probe.

## Commands Run

```powershell
az account show --query "{subscription:name,id:id,tenant:tenantId,user:user.name}" -o json
```

```powershell
pwsh C:/Dev/sf-quality/sf-quality-db/database/deploy/Test-AuthRuntimeProbePreflight.ps1 -Environment dev -PermissionCode WF.NCR.Submit
```

```powershell
. C:/Dev/sf-quality/sf-quality-db/database/deploy/Deploy-Common.ps1
$config = Get-DeployConfig -Environment dev
$conn = Connect-QualityDb @config
Invoke-Migration -Connection $conn -MigrationsDir C:/Dev/sf-quality/sf-quality-db/database/migrations -MigrationFiles @(
  '151_phase34_policy_lookup_table_exclusion.sql'
)
```

```powershell
# SQL-level validation
EXEC dbo.usp_SetSessionContext @CallerAzureOid='7CB31D63-9EA5-43EB-BCC3-BE10CA6F6C03';
SELECT TRY_CAST(SESSION_CONTEXT(N'UserId') AS INT) AS UserId,
       TRY_CAST(SESSION_CONTEXT(N'IsAdmin') AS BIT) AS IsAdmin;
EXEC security.usp_CheckPermission @UserId=TRY_CAST(SESSION_CONTEXT(N'UserId') AS INT), @PermissionCode='WF.NCR.Submit', @PlantId=NULL;
```

```powershell
# API runtime probes
$base = "http://localhost:5269"
# deny OID: 2FA67B5A-5880-4D2A-BFAD-6F5D29EBF101
# admin OID: 7CB31D63-9EA5-43EB-BCC3-BE10CA6F6C03
Invoke-WebRequest -Uri "$base/v1/ncr/999999/submit?isValidateOnly=true" -Method Post -Headers @{ "X-MS-CLIENT-PRINCIPAL" = $principal } -Body "{}" -ContentType "application/json" -SkipHttpErrorCheck
```

## Environment and Auth Context

- Azure account:
  - subscription: `Select Finishing APQP`
  - subscription id: `0b1ff71a-737c-4463-82d3-dc50d92dd8d0`
  - tenant: `337332b1-0eda-4b85-9505-52bc6e160e90`
  - user: `chris.walsh@selectfinishing.ca`
- Preflight checks:
  - `P01..P07` all `PASS`
  - includes structural guard that `PlantIsolationPolicy` excludes `dbo/audit UserPlantAccess/UserRole`

## Root Cause and Fix

1. Initial admin probe failed with `403` because admin bootstrap was blocked by RLS policy targeting auth lookup tables.
2. Migration applied: `151_phase34_policy_lookup_table_exclusion.sql`
3. Post-fix SQL validation:
   - admin OID resolves to `UserId=439`, `IsAdmin=1`
   - `security.usp_CheckPermission` for `WF.NCR.Submit` returns allow

## Final Runtime Probe Results (Post-Fix)

### Health check

- Endpoint: `GET /v1/diagnostics/health`
- Status: `200`
- Body:

```json
{"service":"sf-quality-api","status":"healthy","timestamp":"2026-02-24T20:16:32.3300401Z","correlationId":"ff4b5b6a-1661-41b4-9034-1036265ca809"}
```

### Probe 1: non-admin-deny

- OID: `2FA67B5A-5880-4D2A-BFAD-6F5D29EBF101`
- Status: `403`
- Body:

```json
{"error":"No role grants permission: WF.NCR.Submit","correlationId":"3b648026-4427-4a89-9781-71e2e2a3767e"}
```

- Correlation ID: `3b648026-4427-4a89-9781-71e2e2a3767e`

### Probe 2: admin-allow

- OID: `7CB31D63-9EA5-43EB-BCC3-BE10CA6F6C03`
- Status: `404` (non-`403` allow-path proof)
- Body:

```json
{"error":"NCR not found.","correlationId":"d7892164-22f6-48a1-bec2-53b7870ca2b6"}
```

- Correlation ID: `d7892164-22f6-48a1-bec2-53b7870ca2b6`

### Reference Probe: allow persona

- OID: `E1F7A7B8-CF77-4826-AE31-EB6128EF4202`
- Status: `404`
- Correlation ID: `d74e7583-a306-4561-81f5-99537ea0e2d9`

## Expected vs Actual

1. Non-admin deny probe expected `403`: `PASS` (`403` observed)
2. Admin allow probe expected non-`403`: `PASS` (`404` observed)

Overall runtime sanity closeout: `PASS`

## human_needed

- `human_needed = false`
- Admin allow-path evidence is now present and verified end-to-end.
