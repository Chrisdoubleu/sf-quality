import csv
import unittest
from pathlib import Path

from scripts.role_consistency.validate_role_terminology import TERM_BY_KEY


class TriageWorkbookRoleTests(unittest.TestCase):
    def test_required_role_ref_is_canonical_for_required_rows(self):
        bad_aliases = {
            TERM_BY_KEY["quality_manager_plus"],
            TERM_BY_KEY["quality_engineer_plus"],
            TERM_BY_KEY["quality_supervisor_plus"],
            TERM_BY_KEY["corp_quality_manager_short"],
            TERM_BY_KEY["corp_quality_manager"],
            TERM_BY_KEY["quality_supervisor"],
            TERM_BY_KEY["quality_coordinator"],
            TERM_BY_KEY["production_supervisor"],
            TERM_BY_KEY["operator"],
        }
        files = [
            Path("Reference_Architecture/Specs/Triage_Layer_Workbook/00_MASTER_AllTransitions.csv"),
            Path("Reference_Architecture/Specs/Triage_Layer_Workbook/05_WorkflowTransition_QualityAlert.csv"),
            Path("Reference_Architecture/Specs/Triage_Layer_Workbook/06_WorkflowTransition_ProcessDeviation.csv"),
        ]
        bad = []
        for p in files:
            rows = list(csv.DictReader(p.open("r", encoding="utf-8-sig", newline="")))
            for r in rows:
                if not (r.get("RequiredRoleId") or "").strip():
                    continue
                ref = (r.get("RequiredRole_Ref") or "").strip()
                if ref in bad_aliases:
                    bad.append((p.as_posix(), r.get("WorkflowTransitionId"), r.get("RequiredRoleId"), ref))
        self.assertEqual([], bad)

    def test_role_guard_reference_uses_canonical_names(self):
        p = Path("Reference_Architecture/Specs/Triage_Layer_Workbook/11_RoleGuardReference.csv")
        rows = list(csv.DictReader(p.open("r", encoding="utf-8-sig", newline="")))
        expected = {
            "1": "Quality Authority - Enterprise (Full)",
            "9": "Quality Workflow Approver - Plant",
            "10": "Quality Workflow Coordinator",
            "13": "Floor Supervisor - Initiate & Manage",
            "14": "Floor Reporter - Initiate Only",
        }
        bad = []
        for r in rows:
            rid = (r.get("RoleId") or "").strip()
            if rid in expected and (r.get("RoleName") or "").strip() != expected[rid]:
                bad.append((rid, r.get("RoleName"), expected[rid]))
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
