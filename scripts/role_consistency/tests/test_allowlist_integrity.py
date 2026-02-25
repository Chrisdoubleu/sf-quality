import json
import unittest
from pathlib import Path


class AllowlistIntegrityTests(unittest.TestCase):
    def test_every_allowlist_glob_has_reason(self):
        p = Path("scripts/role_consistency/allowlist.yml")
        data = json.loads(p.read_text(encoding="utf-8"))
        for g in data["historical_globs"]:
            self.assertIn(g, data["reasons"], f"Missing reason for {g}")


if __name__ == "__main__":
    unittest.main()
