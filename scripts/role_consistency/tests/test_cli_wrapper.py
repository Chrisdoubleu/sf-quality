from pathlib import Path
import unittest


class WrapperTests(unittest.TestCase):
    def test_wrapper_exists(self):
        self.assertTrue(Path("scripts/Verify-RoleTerminology.ps1").exists())


if __name__ == "__main__":
    unittest.main()
