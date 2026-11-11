"""Deterministic tests of two-document handoff enforcement."""
import unittest
from scripts.check_handoff_policy import missing_handoffs


class HandoffPolicyTests(unittest.TestCase):
    def test_both_files_present(self):
        self.assertEqual(missing_handoffs(("docs/HANDOFF.md",
            "docs/HANDOFF_MASTER.md", "rightware_si/core/postgres.py")), set())

    def test_missing_master_is_reported(self):
        self.assertEqual(missing_handoffs(("docs/HANDOFF.md",)),
            {"docs/HANDOFF_MASTER.md"})

    def test_missing_both_is_reported(self):
        self.assertEqual(missing_handoffs(("README.md",)),
            {"docs/HANDOFF.md", "docs/HANDOFF_MASTER.md"})


if __name__ == "__main__":
    unittest.main()
