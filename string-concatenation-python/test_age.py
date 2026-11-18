"""Regression and unit test suite for string-concatenation-python/age.py.

Verifies single-responsibility refactoring, classification boundaries,
formatting concatenation, and stdout output preservation.
"""

import io
import sys
import unittest
from contextlib import redirect_stdout

from age import age_group, format_age_group, get_age_category


class TestAgeGroupRefactoring(unittest.TestCase):
    """Test suite locking down age_group classification and formatting."""

    def test_precondition_anchors(self):
        """Verify precondition classification anchors match specification."""
        self.assertEqual(get_age_category(0), "a Child!")
        self.assertEqual(get_age_category(9), "a Child!")
        self.assertEqual(get_age_category(10), "an Adolescent!")
        self.assertEqual(get_age_category(18), "an Adolescent!")
        self.assertEqual(get_age_category(20), "an Adult!")
        self.assertEqual(get_age_category(65), "an Adult!")
        self.assertEqual(get_age_category(66), "in your Golden Years!")

    def test_smallest_valid_input_child(self):
        """Verify smallest valid input (age 0) produces 'You are a Child!'."""
        res = format_age_group(0)
        self.assertEqual(res, "You are a Child!")

    def test_ordinary_valid_inputs(self):
        """Verify ordinary inputs across all demographic categories."""
        test_cases = [
            (5, "You are a Child!"),
            (15, "You are an Adolescent!"),
            (35, "You are an Adult!"),
            (75, "You are in your Golden Years!"),
        ]
        for age, expected in test_cases:
            with self.subTest(age=age):
                self.assertEqual(format_age_group(age), expected)

    def test_age_group_stdout_printing(self):
        """Verify age_group prints the exact formatted message to stdout."""
        f = io.StringIO()
        with redirect_stdout(f):
            age_group(25)
        self.assertEqual(f.getvalue(), "You are an Adult!\n")

    def test_single_responsibility_isolation(self):
        """Verify get_age_category calculates category without string formatting prefix."""
        category = get_age_category(8)
        self.assertEqual(category, "a Child!")
        self.assertFalse(category.startswith("You are "))

        formatted = format_age_group(8)
        self.assertEqual(formatted, "You are " + category)

    def test_repeatability_and_purity(self):
        """Verify identical inputs yield identical outputs over repeated calls."""
        for _ in range(10):
            self.assertEqual(format_age_group(30), "You are an Adult!")
            self.assertEqual(get_age_category(30), "an Adult!")


if __name__ == "__main__":
    unittest.main()
