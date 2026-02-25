# Cross-Repo Role Terminology Consistency Remediation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Eliminate role terminology drift across active artifacts in all repos and add automated guardrails so future changes cannot reintroduce inconsistencies.

**Architecture:** Use `RoleId` as the immutable key and migration `092_seed_workflow_permissions_features.sql` Section F as the canonical business-role naming contract. Remediate active artifacts to canonical names, preserve legacy wording only in explicitly classified historical content, and enforce both rules with a cross-repo validator that runs before handoff.

**Tech Stack:** Python 3.14 (`unittest`, `csv`, `json`, `openpyxl`), PowerShell, Markdown/CSV/XLSX artifacts.

---

### Task 1: Establish Canonical Role Contract

**Files:**
- Create: `docs/standards/role-canonical-map.json`
- Create: `docs/standards/role-terminology-policy.md`
- Create: `scripts/role_consistency/tests/test_role_contract.py`
- Source of truth reference: `sf-quality-db/database/migrations/092_seed_workflow_permissions_features.sql:539-567`

**Step 1: Write the failing test**

```python
# scripts/role_consistency/tests/test_role_contract.py
import json
from pathlib import Path
import unittest

class RoleContractTests(unittest.TestCase):
    def test_canonical_map_exists_and_has_15_roles(self):
        p = Path("docs/standards/role-canonical-map.json")
        self.assertTrue(p.exists(), "canonical role map missing")
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(15, len(data["roles"]))

    def test_ids_1_9_10_13_14_are_expected(self):
        p = Path("docs/standards/role-canonical-map.json")
        data = json.loads(p.read_text(encoding="utf-8"))
        m = {str(x["roleId"]): x["roleName"] for x in data["roles"]}
        self.assertEqual("Quality Authority - Enterprise (Full)", m["1"])
        self.assertEqual("Quality Workflow Approver - Plant", m["9"])
        self.assertEqual("Quality Workflow Coordinator", m["10"])
        self.assertEqual("Floor Supervisor - Initiate & Manage", m["13"])
        self.assertEqual("Floor Reporter - Initiate Only", m["14"])

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest scripts/role_consistency/tests/test_role_contract.py -v`
Expected: FAIL with missing `role-canonical-map.json`.

**Step 3: Write minimal implementation**

```json
{
  "source": "sf-quality-db/database/migrations/092_seed_workflow_permissions_features.sql#SectionF",
  "roles": [
    {"roleId": 1, "roleName": "Quality Authority - Enterprise (Full)"},
    {"roleId": 2, "roleName": "Workflow Reopen/Cancel - Enterprise"},
    {"roleId": 3, "roleName": "Engineering Contributor - Enterprise"},
    {"roleId": 4, "roleName": "Maintenance Contributor - Enterprise"},
    {"roleId": 5, "roleName": "Operations Lead - Multi-Plant"},
    {"roleId": 6, "roleName": "Process Engineering Lead - Multi-Plant"},
    {"roleId": 7, "roleName": "Plant Workflow Manager"},
    {"roleId": 8, "roleName": "Production Workflow Lead"},
    {"roleId": 9, "roleName": "Quality Workflow Approver - Plant"},
    {"roleId": 10, "roleName": "Quality Workflow Coordinator"},
    {"roleId": 11, "roleName": "Quality Data Steward"},
    {"roleId": 12, "roleName": "Maintenance Workflow Lead"},
    {"roleId": 13, "roleName": "Floor Supervisor - Initiate & Manage"},
    {"roleId": 14, "roleName": "Floor Reporter - Initiate Only"},
    {"roleId": 15, "roleName": "Process Engineering Contributor"}
  ]
}
```

```md
# Role Terminology Policy

- Canonical role naming source is migration 092 Section F.
- Active artifacts must use canonical names when a role is represented as a business role label.
- `RoleId` is authoritative for joins and reconciliation.
- Legacy/job-title aliases are prohibited in active artifacts.
- Historical artifacts may retain legacy labels only when allowlisted with rationale.
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest scripts/role_consistency/tests/test_role_contract.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add docs/standards/role-canonical-map.json docs/standards/role-terminology-policy.md scripts/role_consistency/tests/test_role_contract.py
git commit -m "chore: add canonical role terminology contract"
```

### Task 2: Build Cross-Repo Role Terminology Validator

**Files:**
- Create: `scripts/role_consistency/validate_role_terminology.py`
- Create: `scripts/role_consistency/allowlist.yml`
- Create: `scripts/role_consistency/tests/test_validator.py`

**Step 1: Write the failing test**

```python
# scripts/role_consistency/tests/test_validator.py
import unittest
from scripts.role_consistency.validate_role_terminology import classify_line

class ValidatorTests(unittest.TestCase):
    def test_alias_detection(self):
        issue = classify_line(
            path="Reference_Architecture/Specs/Triage_Layer_Workbook/05_WorkflowTransition_QualityAlert.csv",
            line_no=9,
            line_text="93,7,...,1,Quality Authority - Enterprise (Full),...",
            active=True,
        )
        self.assertIsNotNone(issue)
        self.assertEqual("ALIAS_IN_ACTIVE", issue["type"])

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest scripts/role_consistency/tests/test_validator.py -v`
Expected: FAIL because validator module/functions do not exist.

**Step 3: Write minimal implementation**

```python
# scripts/role_consistency/validate_role_terminology.py (core shape)
from pathlib import Path
import argparse, json, re, sys

ALIASES = [
    "Quality Authority - Enterprise (Full)", "Quality Workflow Approver - Plant", "Quality Workflow Coordinator",
    "Floor Supervisor - Initiate & Manage", "Operator", "Quality Authority - Enterprise (Full)",
    "Quality Authority - Enterprise (Full)", "Quality Workflow Coordinator", "Quality Workflow Approver - Plant"
]

def classify_line(path: str, line_no: int, line_text: str, active: bool):
    for t in ALIASES:
        if t in line_text:
            return {
                "type": "ALIAS_IN_ACTIVE" if active else "ALIAS_IN_HISTORICAL",
                "path": path,
                "line": line_no,
                "term": t,
            }
    return None

# implement scan + allowlist + json report + nonzero exit on active violations
```

```yaml
# scripts/role_consistency/allowlist.yml
historical_globs:
  - "sf-quality-db/docs/handoffs/**"
  - "sf-quality-db/.planning/phases/**"
  - "docs/Organization Forms Reference/**"
  - "Reference_Architecture/Phase23_Discussion_Package/**"
reasons:
  sf-quality-db/docs/handoffs/**: "Historical handoff snapshots"
  sf-quality-db/.planning/phases/**: "Historical planning artifacts"
  docs/Organization Forms Reference/**: "External/source package content"
  Reference_Architecture/Phase23_Discussion_Package/**: "Archived discussion package"
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest scripts/role_consistency/tests/test_validator.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add scripts/role_consistency/validate_role_terminology.py scripts/role_consistency/allowlist.yml scripts/role_consistency/tests/test_validator.py
git commit -m "feat: add cross-repo role terminology validator"
```

### Task 3: Add Operator Command and Baseline Audit Report

**Files:**
- Create: `scripts/Verify-RoleTerminology.ps1`
- Create: `docs/plans/evidence/2026-02-25-role-terminology-baseline.md`
- Modify: `README.md`

**Step 1: Write the failing test**

```python
# scripts/role_consistency/tests/test_cli_wrapper.py
from pathlib import Path
import unittest

class WrapperTests(unittest.TestCase):
    def test_wrapper_exists(self):
        self.assertTrue(Path("scripts/Verify-RoleTerminology.ps1").exists())

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest scripts/role_consistency/tests/test_cli_wrapper.py -v`
Expected: FAIL wrapper missing.

**Step 3: Write minimal implementation**

```powershell
# scripts/Verify-RoleTerminology.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
python scripts/role_consistency/validate_role_terminology.py --allowlist scripts/role_consistency/allowlist.yml --report docs/plans/evidence/role-terminology-report.json
```

Add `README.md` section with command:

```md
### Role Terminology Check
Run `pwsh scripts/Verify-RoleTerminology.ps1` before cross-repo handoff.
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest scripts/role_consistency/tests/test_cli_wrapper.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add scripts/Verify-RoleTerminology.ps1 README.md docs/plans/evidence/2026-02-25-role-terminology-baseline.md scripts/role_consistency/tests/test_cli_wrapper.py
git commit -m "chore: add role terminology verification entrypoint"
```

### Task 4: Remediate Triage Workbook CSV Role Terminology

**Files:**
- Modify: `Reference_Architecture/Specs/Triage_Layer_Workbook/11_RoleGuardReference.csv`
- Modify: `Reference_Architecture/Specs/Triage_Layer_Workbook/00_MASTER_AllTransitions.csv`
- Modify: `Reference_Architecture/Specs/Triage_Layer_Workbook/05_WorkflowTransition_QualityAlert.csv`
- Modify: `Reference_Architecture/Specs/Triage_Layer_Workbook/06_WorkflowTransition_ProcessDeviation.csv`

**Step 1: Write the failing test**

```python
# scripts/role_consistency/tests/test_triage_workbook_roles.py
import csv, unittest
from pathlib import Path

class TriageWorkbookRoleTests(unittest.TestCase):
    def test_required_role_ref_is_canonical_for_required_rows(self):
        p = Path("Reference_Architecture/Specs/Triage_Layer_Workbook/05_WorkflowTransition_QualityAlert.csv")
        rows = list(csv.DictReader(p.open("r", encoding="utf-8-sig", newline="")))
        bad = [r for r in rows if (r["RequiredRoleId"] and r["RequiredRole_Ref"] in {"Quality Authority - Enterprise (Full)","Quality Workflow Coordinator","Quality Workflow Approver - Plant","Quality Authority - Enterprise (Full)"})]
        self.assertEqual([], bad)

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest scripts/role_consistency/tests/test_triage_workbook_roles.py -v`
Expected: FAIL due existing alias values.

**Step 3: Write minimal implementation**

Apply exact replacements by `RoleId`:
- `1 -> Quality Authority - Enterprise (Full)`
- `9 -> Quality Workflow Approver - Plant`
- `10 -> Quality Workflow Coordinator`
- `13 -> Floor Supervisor - Initiate & Manage`
- `14 -> Floor Reporter - Initiate Only`

Keep CSV shape unchanged and preserve parser safety (no column shifts).

**Step 4: Run tests to verify they pass**

Run:
- `python -m unittest scripts/role_consistency/tests/test_triage_workbook_roles.py -v`
- `python scripts/role_consistency/validate_role_terminology.py --allowlist scripts/role_consistency/allowlist.yml --scope active`

Expected:
- Unit test PASS.
- Validator reports zero active alias violations in triage workbook files.

**Step 5: Commit**

```bash
git add Reference_Architecture/Specs/Triage_Layer_Workbook/11_RoleGuardReference.csv Reference_Architecture/Specs/Triage_Layer_Workbook/00_MASTER_AllTransitions.csv Reference_Architecture/Specs/Triage_Layer_Workbook/05_WorkflowTransition_QualityAlert.csv Reference_Architecture/Specs/Triage_Layer_Workbook/06_WorkflowTransition_ProcessDeviation.csv scripts/role_consistency/tests/test_triage_workbook_roles.py
git commit -m "fix: normalize triage workbook role terminology to canonical names"
```

### Task 5: Remediate Triage Spec/README Role Language

**Files:**
- Modify: `Reference_Architecture/Specs/Quality_Event_Triage_Layer.md`
- Modify: `Reference_Architecture/Specs/Triage_Layer_Workbook/README.md`

**Step 1: Write the failing test**

```python
# scripts/role_consistency/tests/test_triage_docs_roles.py
from pathlib import Path
import unittest

BANNED = ["Quality Authority - Enterprise (Full)", "Quality Workflow Coordinator", "Quality Workflow Approver - Plant", "Quality Authority - Enterprise (Full)"]

class TriageDocRoleTests(unittest.TestCase):
    def test_no_alias_tokens_in_triage_spec_docs(self):
        docs = [
            Path("Reference_Architecture/Specs/Quality_Event_Triage_Layer.md"),
            Path("Reference_Architecture/Specs/Triage_Layer_Workbook/README.md"),
        ]
        for d in docs:
            text = d.read_text(encoding="utf-8-sig")
            for token in BANNED:
                self.assertNotIn(token, text, f"{token} found in {d}")

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest scripts/role_consistency/tests/test_triage_docs_roles.py -v`
Expected: FAIL with alias tokens found.

**Step 3: Write minimal implementation**

- Replace alias role labels with canonical names in transition tables.
- Where text needs hierarchy semantics, phrase as `RoleId-based authorization via RequiredRoleId` rather than `+` suffix labels.

**Step 4: Run tests to verify they pass**

Run:
- `python -m unittest scripts/role_consistency/tests/test_triage_docs_roles.py -v`
- `python scripts/role_consistency/validate_role_terminology.py --allowlist scripts/role_consistency/allowlist.yml --scope active`

Expected: PASS.

**Step 5: Commit**

```bash
git add Reference_Architecture/Specs/Quality_Event_Triage_Layer.md Reference_Architecture/Specs/Triage_Layer_Workbook/README.md scripts/role_consistency/tests/test_triage_docs_roles.py
git commit -m "fix: align triage spec docs to canonical role terminology"
```

### Task 6: Remediate Generated Excel Path Map Artifact

**Files:**
- Create: `scripts/role_consistency/remediate_quality_triage_pathmap.py`
- Modify: `docs/Quality-Event Classification/Quality_Triage_PathMap.xlsx`
- Create: `scripts/role_consistency/tests/test_pathmap_workbook_roles.py`

**Step 1: Write the failing test**

```python
# scripts/role_consistency/tests/test_pathmap_workbook_roles.py
import unittest
from pathlib import Path
import openpyxl

class PathmapRoleTests(unittest.TestCase):
    def test_dim_role_uses_canonical_names(self):
        wb = openpyxl.load_workbook(Path("docs/Quality-Event Classification/Quality_Triage_PathMap.xlsx"), data_only=True)
        ws = wb["DIM_Role"]
        headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
        i_id = headers.index("RoleId") + 1
        i_name = headers.index("RoleName") + 1
        bad = []
        for r in range(2, ws.max_row + 1):
            rid = str(ws.cell(r, i_id).value)
            name = str(ws.cell(r, i_name).value)
            if rid in {"1", "9", "10", "13", "14"} and name in {"Quality Authority - Enterprise (Full)", "Quality Workflow Approver - Plant", "Quality Workflow Coordinator", "Floor Supervisor - Initiate & Manage", "Operator"}:
                bad.append((rid, name))
        self.assertEqual([], bad)

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest scripts/role_consistency/tests/test_pathmap_workbook_roles.py -v`
Expected: FAIL with DIM_Role legacy names.

**Step 3: Write minimal implementation**

- Implement workbook patch script to:
  - normalize `DIM_Role.RoleName` by `RoleId`
  - add `ROLE_CANONICAL_XREF` sheet (`RoleId`, `CanonicalRoleName`, `LegacyOrAliasLabel`, `SourceSheet`)
  - add canonical columns in `FACT_Transition` and `PATH_STEP` while preserving original alias columns for traceability

**Step 4: Run tests to verify they pass**

Run:
- `python scripts/role_consistency/remediate_quality_triage_pathmap.py --in docs/Quality-Event\ Classification/Quality_Triage_PathMap.xlsx --out docs/Quality-Event\ Classification/Quality_Triage_PathMap.xlsx`
- `python -m unittest scripts/role_consistency/tests/test_pathmap_workbook_roles.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add scripts/role_consistency/remediate_quality_triage_pathmap.py scripts/role_consistency/tests/test_pathmap_workbook_roles.py "docs/Quality-Event Classification/Quality_Triage_PathMap.xlsx"
git commit -m "fix: normalize generated pathmap workbook roles and add canonical crosswalk"
```

### Task 7: Remediate Active DB Documentation Artifacts

**Files:**
- Modify: `sf-quality-db/docs/NCR-STATE-MACHINE.md`
- Modify: `sf-quality-db/docs/NCR-STATE-MACHINE.csv`
- Modify: `docs/plans/2026-02-23-phase34-authorization-architecture-completion-design.md`

**Step 1: Write the failing test**

```python
# scripts/role_consistency/tests/test_active_db_docs_roles.py
from pathlib import Path
import unittest

class ActiveDbDocRoleTests(unittest.TestCase):
    def test_no_legacy_business_role_names_in_active_db_docs(self):
        targets = [
            Path("sf-quality-db/docs/NCR-STATE-MACHINE.md"),
            Path("sf-quality-db/docs/NCR-STATE-MACHINE.csv"),
            Path("docs/plans/2026-02-23-phase34-authorization-architecture-completion-design.md"),
        ]
        banned = ["Quality Authority - Enterprise (Full)", "Quality Workflow Approver - Plant", "Quality Workflow Coordinator", "Floor Supervisor", "Floor Reporter"]
        for t in targets:
            txt = t.read_text(encoding="utf-8-sig")
            for b in banned:
                self.assertNotIn(b, txt, f"{b} found in {t}")

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest scripts/role_consistency/tests/test_active_db_docs_roles.py -v`
Expected: FAIL on current legacy/shortened names.

**Step 3: Write minimal implementation**

- Normalize role labels in these active docs to exact canonical strings from migration 092.
- Keep `RoleId` values unchanged.

**Step 4: Run tests to verify they pass**

Run:
- `python -m unittest scripts/role_consistency/tests/test_active_db_docs_roles.py -v`
- `python scripts/role_consistency/validate_role_terminology.py --allowlist scripts/role_consistency/allowlist.yml --scope active`

Expected: PASS.

**Step 5: Commit**

```bash
git add sf-quality-db/docs/NCR-STATE-MACHINE.md sf-quality-db/docs/NCR-STATE-MACHINE.csv docs/plans/2026-02-23-phase34-authorization-architecture-completion-design.md scripts/role_consistency/tests/test_active_db_docs_roles.py
git commit -m "fix: align active DB and plan docs to canonical role names"
```

### Task 8: Classify Historical Content and Enforce Allowlist Governance

**Files:**
- Modify: `scripts/role_consistency/allowlist.yml`
- Create: `docs/standards/role-terminology-historical-scope.md`
- Create: `scripts/role_consistency/tests/test_allowlist_integrity.py`

**Step 1: Write the failing test**

```python
# scripts/role_consistency/tests/test_allowlist_integrity.py
import unittest, yaml
from pathlib import Path

class AllowlistIntegrityTests(unittest.TestCase):
    def test_every_allowlist_glob_has_reason(self):
        p = Path("scripts/role_consistency/allowlist.yml")
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        for g in data["historical_globs"]:
            self.assertIn(g, data["reasons"], f"Missing reason for {g}")

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest scripts/role_consistency/tests/test_allowlist_integrity.py -v`
Expected: FAIL until reasons are complete for all globs.

**Step 3: Write minimal implementation**

- Ensure each historical glob has a rationale.
- Document historical scope policy: legacy terms allowed only in archived snapshots, imported evidence, or external-source research artifacts.

**Step 4: Run tests to verify they pass**

Run:
- `python -m unittest scripts/role_consistency/tests/test_allowlist_integrity.py -v`
- `python scripts/role_consistency/validate_role_terminology.py --allowlist scripts/role_consistency/allowlist.yml --scope all --enforce-allowlist-reasons`

Expected: PASS with no unclassified historical violations.

**Step 5: Commit**

```bash
git add scripts/role_consistency/allowlist.yml docs/standards/role-terminology-historical-scope.md scripts/role_consistency/tests/test_allowlist_integrity.py
git commit -m "chore: formalize historical role terminology allowlist governance"
```

### Task 9: Full Cross-Repo Verification and Evidence Closeout

**Files:**
- Create: `docs/plans/evidence/2026-02-25-role-terminology-remediation-closeout.md`
- Create: `docs/plans/evidence/2026-02-25-role-terminology-report.json`

**Step 1: Write the failing verification gate**

Define gate in evidence doc requiring:
- `active_violations = 0`
- `unclassified_historical_violations = 0`
- triage CSV parser integrity pass
- workbook canonical role checks pass

**Step 2: Run gate before final cleanup to verify fail path is reproducible**

Run:
- `pwsh scripts/Verify-RoleTerminology.ps1`
- `python -m unittest discover scripts/role_consistency/tests -v`

Expected: FAIL if any remediation tasks were skipped.

**Step 3: Write minimal implementation**

- Complete remaining fixes.
- Regenerate report JSON.
- Record exact command output summaries and counts in closeout markdown.

**Step 4: Run final verification to verify pass**

Run:
- `pwsh scripts/Verify-RoleTerminology.ps1`
- `python -m unittest discover scripts/role_consistency/tests -v`
- `@'\nimport csv, pathlib\nbase=pathlib.Path("Reference_Architecture/Specs/Triage_Layer_Workbook")\nfor p in sorted(base.glob("*.csv")):\n    rows=list(csv.reader(p.open("r",encoding="utf-8-sig",newline="")))\n    assert rows and all(len(r)==len(rows[0]) for r in rows), p\nprint("triage-csv-shape-pass")\n'@ | python -`

Expected:
- all checks PASS
- report shows zero active inconsistencies.

**Step 5: Commit**

```bash
git add docs/plans/evidence/2026-02-25-role-terminology-remediation-closeout.md docs/plans/evidence/2026-02-25-role-terminology-report.json
git commit -m "docs: publish cross-repo role terminology remediation verification evidence"
```

### Task 10: Cross-Repo Handoff and Adoption

**Files:**
- Create: `docs/plans/2026-02-25-role-terminology-remediation-handoff.md`
- Modify: `WORKSPACE-STRUCTURE.md`

**Step 1: Write the failing test**

```python
# scripts/role_consistency/tests/test_handoff_contains_runbook.py
from pathlib import Path
import unittest

class HandoffTests(unittest.TestCase):
    def test_handoff_has_required_run_commands(self):
        p = Path("docs/plans/2026-02-25-role-terminology-remediation-handoff.md")
        self.assertTrue(p.exists())
        txt = p.read_text(encoding="utf-8")
        self.assertIn("pwsh scripts/Verify-RoleTerminology.ps1", txt)
        self.assertIn("python -m unittest discover scripts/role_consistency/tests -v", txt)

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest scripts/role_consistency/tests/test_handoff_contains_runbook.py -v`
Expected: FAIL until handoff is written.

**Step 3: Write minimal implementation**

- Create handoff with:
  - canonical map source
  - active vs historical policy
  - mandatory pre-merge commands
  - ownership for future role-model updates

**Step 4: Run tests to verify they pass**

Run: `python -m unittest scripts/role_consistency/tests/test_handoff_contains_runbook.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add docs/plans/2026-02-25-role-terminology-remediation-handoff.md WORKSPACE-STRUCTURE.md scripts/role_consistency/tests/test_handoff_contains_runbook.py
git commit -m "docs: add cross-repo role terminology remediation handoff and runbook"
```

