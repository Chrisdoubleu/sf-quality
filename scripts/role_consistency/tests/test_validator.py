import unittest

from scripts.role_consistency.validate_role_terminology import TERM_BY_KEY, classify_line


class ValidatorTests(unittest.TestCase):
    def test_alias_detection(self):
        issue = classify_line(
            path="Reference_Architecture/Specs/Triage_Layer_Workbook/05_WorkflowTransition_QualityAlert.csv",
            line_no=9,
            line_text=f"93,7,49,54,Void Alert (from Review),1,{TERM_BY_KEY['quality_manager_plus']},",
            active=True,
        )
        self.assertIsNotNone(issue)
        self.assertEqual("ALIAS_IN_ACTIVE", issue["type"])


if __name__ == "__main__":
    unittest.main()
