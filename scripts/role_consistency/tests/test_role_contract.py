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
