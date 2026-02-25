from pathlib import Path
import unittest

from scripts.role_consistency.validate_role_terminology import TERM_BY_KEY


class AdditionalDbDocRoleTests(unittest.TestCase):
    def test_active_db_docs_use_canonical_role_labels(self):
        targets = [
            Path("sf-quality-db/docs/DATABASE-ARCHITECTURE.yaml"),
            Path("sf-quality-db/docs/database-architecture/DATABASE-ARCHITECTURE.yaml"),
            Path("sf-quality-db/docs/defect-taxonomy-v3/prompts/defect-taxonomy-prompt-v3.md"),
        ]
        banned = [
            TERM_BY_KEY["corp_quality_manager"],
            TERM_BY_KEY["quality_supervisor"],
            TERM_BY_KEY["quality_coordinator"],
            TERM_BY_KEY["production_supervisor"],
        ]
        for t in targets:
            txt = t.read_text(encoding="utf-8-sig")
            for b in banned:
                self.assertNotIn(b, txt, f"{b} found in {t}")


if __name__ == "__main__":
    unittest.main()
