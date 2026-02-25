from pathlib import Path
import unittest

from scripts.role_consistency.validate_role_terminology import TERM_BY_KEY

BANNED = [
    TERM_BY_KEY["quality_manager_plus"],
    TERM_BY_KEY["quality_engineer_plus"],
    TERM_BY_KEY["quality_supervisor_plus"],
    TERM_BY_KEY["corp_quality_manager_short"],
]


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
