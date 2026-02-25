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
