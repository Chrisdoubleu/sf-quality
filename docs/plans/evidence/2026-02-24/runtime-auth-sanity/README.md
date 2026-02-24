# Runtime Auth Sanity Evidence - 2026-02-24

Date: February 24, 2026
Scope: App -> API -> DB authorization chain sanity for NCR submit gate
API merge baseline: `f4cf8f847de87e4e9341d68c873cbb043e4d1adc` (PR #8)

## Verification Baseline (API)

- `dotnet build SfQualityApi.sln -v minimal` -> PASS
- `dotnet test tests/SfQualityApi.Tests/SfQualityApi.Tests.csproj -v minimal` -> PASS (27/27)
- `pwsh scripts/Test-DbContractReferences.ps1 -RepoRoot (Get-Location)` -> PASS
- `pwsh scripts/Test-OpenApiPublication.ps1 -RepoRoot (Get-Location)` -> PASS
- `pwsh scripts/Invoke-CycleChecks.ps1 -ChangedOnly` -> PASS

## Runtime Probe Results

Endpoint under test:
- `POST /v1/ncr/999999/submit?isValidateOnly=true`

Non-admin deny probe:
- Identity: `2FA67B5A-5880-4D2A-BFAD-6F5D29EBF101`
- Status: `403`
- Body: `{"error":"No role grants permission: WF.NCR.Submit",...}`
- Result: PASS (expected deny)

Non-admin allow-path probe:
- Identity: `E1F7A7B8-CF77-4826-AE31-EB6128EF4202`
- Status: `404`
- Body: `{"error":"NCR not found.",...}`
- Result: PASS (expected non-403; auth gate passed)

Admin probe (human-run admin session):
- Operator: `chris.walsh@selectfinishing.ca`
- Source output:
  - `STATUS=404`
  - `BODY={"error":"NCR not found.","correlationId":"24da57ef-ce0f-4bd9-8c41-6a27c1b720ca"}`
- Result: PASS (expected non-403 for admin-capable path)

## Final Sanity Decision

Cross-repo runtime sanity is complete for the intended gate proof:
- One deny path (`403`) confirmed.
- One non-admin allow path (non-`403`) confirmed.
- One admin-session allow path (non-`403`) confirmed.
