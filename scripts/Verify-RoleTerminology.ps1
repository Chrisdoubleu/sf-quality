Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

python scripts/role_consistency/validate_role_terminology.py `
  --allowlist scripts/role_consistency/allowlist.yml `
  --report docs/plans/evidence/2026-02-25-role-terminology-report.json `
  --scope all `
  --enforce-allowlist-reasons

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
