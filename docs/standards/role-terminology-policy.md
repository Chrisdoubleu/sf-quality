# Role Terminology Policy

## Canonical Contract
- Canonical business role naming is sourced from `sf-quality-db/database/migrations/092_seed_workflow_permissions_features.sql` Section F.
- `RoleId` is authoritative for mapping, joins, and cross-repo reconciliation.
- Active artifacts must use canonical role labels where business roles are displayed.

## Active Artifact Rule
- Do not use legacy/job-title or alias labels in active artifacts.
- Prohibited labels are defined and enforced by `scripts/role_consistency/validate_role_terminology.py` (`BANNED_TERMS` + role-context rules).

## Historical Artifact Rule
- Legacy labels are allowed only in explicitly classified historical content.
- Historical paths must be declared in `scripts/role_consistency/allowlist.yml` with rationale.

## Verification
- Run `pwsh scripts/Verify-RoleTerminology.ps1` before cross-repo handoff.
- Active violations must be zero.
