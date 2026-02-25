from pathlib import Path
import unittest

from scripts.role_consistency.validate_role_terminology import TERM_BY_KEY


class ActiveDbDocRoleTests(unittest.TestCase):
    def test_no_legacy_business_role_names_in_active_db_docs(self):
        targets = [
            Path("sf-quality-db/docs/NCR-STATE-MACHINE.md"),
            Path("sf-quality-db/docs/NCR-STATE-MACHINE.csv"),
            Path("docs/plans/2026-02-23-phase34-authorization-architecture-completion-design.md"),
        ]
        banned = [
            TERM_BY_KEY["corp_quality_manager"],
            TERM_BY_KEY["quality_supervisor"],
            TERM_BY_KEY["quality_coordinator"],
            "| 13 | Floor Supervisor |",
            "| 14 | Floor Reporter |",
        ]
        for t in targets:
            txt = t.read_text(encoding="utf-8-sig")
            for b in banned:
                self.assertNotIn(b, txt, f"{b} found in {t}")


if __name__ == "__main__":
    unittest.main()
