"""Unit and differential reference tests for github-copilot-code-review.

Cross-checks github_copilot_code_review against an independent reference oracle.
"""

import importlib.util
import os
import sys
import unittest

MODULE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "code_review.py")
spec = importlib.util.spec_from_file_location("code_review", MODULE_PATH)
code_review = importlib.util.module_from_spec(spec)
sys.modules["code_review"] = code_review
spec.loader.exec_module(code_review)

ARCHIVE_NAME = code_review.ARCHIVE_NAME
BRANCH_MAIN = code_review.BRANCH_MAIN
BRANCH_PLAYER_NAMES = code_review.BRANCH_PLAYER_NAMES
BRANCH_PLAYER_NAMES_FINAL = code_review.BRANCH_PLAYER_NAMES_FINAL
SUPPORTED_BRANCHES = code_review.SUPPORTED_BRANCHES
github_copilot_code_review = code_review.github_copilot_code_review
reference_code_review = code_review.reference_code_review


class TestCodeReviewDifferential(unittest.TestCase):
    """Test suite comparing code review implementation against independent reference."""

    def test_precondition_anchors(self):
        """Verify README precondition anchors."""
        self.assertEqual(ARCHIVE_NAME, "pop-quiz.zip")
        self.assertEqual(BRANCH_MAIN, "main")
        self.assertEqual(BRANCH_PLAYER_NAMES, "feature/player-names")
        self.assertEqual(BRANCH_PLAYER_NAMES_FINAL, "feature/player-names-final")
        self.assertEqual(len(SUPPORTED_BRANCHES), 3)

    def test_smallest_valid_input_differential(self):
        """Verify smallest valid input produces matching approval."""
        primary = github_copilot_code_review(BRANCH_MAIN, "")
        reference = reference_code_review(BRANCH_MAIN, "")

        self.assertEqual(primary, reference)
        self.assertEqual(primary["status"], "APPROVE")
        self.assertEqual(primary["findings"], [])
        self.assertEqual(primary["finding_count"], 0)

    def test_ordinary_valid_input_clean_feature_branch(self):
        """Verify ordinary valid clean diff on player-names feature branch."""
        diff = "+ def get_player_name():\n+     return 'Alice'\n"
        primary = github_copilot_code_review(BRANCH_PLAYER_NAMES, diff)
        reference = reference_code_review(BRANCH_PLAYER_NAMES, diff)

        self.assertEqual(primary, reference)
        self.assertEqual(primary["status"], "APPROVE")
        self.assertEqual(primary["finding_count"], 0)

    def test_ordinary_valid_input_with_findings(self):
        """Verify ordinary input triggering review findings matches reference."""
        diff = (
            "+ # TODO: handle edge cases\n"
            "+ print('debugging user state')\n"
            "+ try:\n"
            "+     process()\n"
            "+ except:\n"
            "+     pass\n"
        )
        primary = github_copilot_code_review(BRANCH_PLAYER_NAMES_FINAL, diff)
        reference = reference_code_review(BRANCH_PLAYER_NAMES_FINAL, diff)

        self.assertEqual(primary, reference)
        self.assertEqual(primary["status"], "REQUEST_CHANGES")
        self.assertEqual(primary["finding_count"], 3)
        self.assertEqual(len(primary["findings"]), 3)

    def test_repeated_call_idempotence(self):
        """Verify purity and repeatability over repeated calls."""
        diff = "+ name = 'test'\n"
        for _ in range(10):
            res1 = github_copilot_code_review(BRANCH_MAIN, diff)
            res2 = reference_code_review(BRANCH_MAIN, diff)
            self.assertEqual(res1, res2)

    def test_type_error_handling(self):
        """Verify non-string inputs raise TypeError."""
        with self.assertRaises(TypeError):
            github_copilot_code_review(123, "")
        with self.assertRaises(TypeError):
            github_copilot_code_review(BRANCH_MAIN, None)
        with self.assertRaises(TypeError):
            reference_code_review(123, "")
        with self.assertRaises(TypeError):
            reference_code_review(BRANCH_MAIN, None)


if __name__ == "__main__":
    unittest.main()
