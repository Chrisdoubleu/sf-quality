# Role Terminology Remediation Handoff (2026-02-25)

## Verification Commands
- `pwsh scripts/Verify-RoleTerminology.ps1`
- `python -m unittest discover scripts/role_consistency/tests -v`

## Operator Notes
- Canonical role naming source: `sf-quality-db/database/migrations/092_seed_workflow_permissions_features.sql` (Section F).
- Validate workbook role labels from `docs/Quality-Event Classification/Quality_Triage_PathMap.xlsx` before external package handoff.
