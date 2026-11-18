"""Unit and failure behavior test suite for python-recursion/names.py.

Verifies failure branches, absent-result sentinels, empty list boundaries,
and recursive leaf item traversal.
"""

import copy
import unittest

from names import ABSENT_SENTINEL, count_names, find_name, names


class TestNamesRecursionFailureBehavior(unittest.TestCase):
    """Test suite covering failure, sentinel, and domain boundary behavior in names.py."""

    def test_precondition_anchors(self):
        """Verify fixture hierarchy and total leaf count anchors."""
        self.assertEqual(names[0], "Adam", "Precondition anchor Line 15 mismatch")
        self.assertEqual(names[1][0], "Bob", "Precondition anchor Line 17 mismatch")
        self.assertIn("Chet", names[1][1], "Precondition anchor Line 19 mismatch")
        self.assertEqual(count_names(names), 10, "Total leaf items anchor must be 10")

    def test_smallest_valid_input_empty_list_boundary(self):
        """Verify valid empty list boundary yields absent sentinel and 0 count."""
        empty_tree = []
        self.assertIsNone(find_name("Adam", empty_tree))
        self.assertEqual(count_names(empty_tree), 0)

    def test_ordinary_valid_input_found_leaves(self):
        """Verify ordinary valid searches locate top-level and deeply nested leaves."""
        self.assertEqual(find_name("Adam", names), "Adam")
        self.assertEqual(find_name("Bob", names), "Bob")
        self.assertEqual(find_name("Chet", names), "Chet")
        self.assertEqual(find_name("Ann", names), "Ann")

    def test_absent_result_sentinel_path(self):
        """Verify absent name triggers documented terminal sentinel None."""
        absent_names = ["Zachary", "Zelda", "Unknown", ""]
        for missing in absent_names:
            with self.subTest(missing=missing):
                res = find_name(missing, names)
                self.assertIs(res, ABSENT_SENTINEL)

    def test_failure_branch_invalid_tree_type(self):
        """Verify non-list tree argument raises TypeError."""
        invalid_trees = [123, "not_a_list", {"a": 1}, None]
        for bad_tree in invalid_trees:
            if bad_tree is None:
                continue  # None defaults to names
            with self.subTest(bad_tree=bad_tree):
                with self.assertRaises(TypeError):
                    find_name("Adam", bad_tree)
                with self.assertRaises(TypeError):
                    count_names(bad_tree)

    def test_failure_branch_invalid_target_type(self):
        """Verify non-string target argument raises TypeError."""
        invalid_targets = [123, ["Adam"], {"name": "Adam"}, None]
        for bad_target in invalid_targets:
            with self.subTest(bad_target=bad_target):
                with self.assertRaises(TypeError):
                    find_name(bad_target, names)

    def test_immutability_invariant(self):
        """Verify names hierarchy is not mutated by traversal operations."""
        names_snapshot = copy.deepcopy(names)
        find_name("Chet", names)
        find_name("Absent", names)
        count_names(names)
        self.assertEqual(names, names_snapshot)


if __name__ == "__main__":
    unittest.main()

