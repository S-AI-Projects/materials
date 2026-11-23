"""Unit and regression tests for numpy-tutorial/curve_grades.py.

Preconditions:
- README.md / curve_grades.ipynb: CURVE_CENTER = 80.
- Smallest valid input fixture: [70.0] -> [80.0]
- Ordinary input fixture: [72, 35, 64, 88, 51, 90, 74, 12] -> [91.25, 54.25, 83.25, 100.0, 70.25, 100.0, 93.25, 31.25]
"""

import unittest
from curve_grades import curve


class TestCurveGrades(unittest.TestCase):
    """Test suite for curve_grades algorithm and edge cases."""

    def test_precondition_smallest_valid_input(self):
        """Smallest valid input fixture: single element grade [70.0]."""
        literal_input = [70.0]
        expected_output = [80.0]
        self.assertEqual(curve(literal_input), expected_output)

    def test_precondition_ordinary_input(self):
        """Ordinary input fixture matching curve_grades.ipynb cell 4."""
        literal_input = [72, 35, 64, 88, 51, 90, 74, 12]
        expected_output = [91.25, 54.25, 83.25, 100.0, 70.25, 100.0, 93.25, 31.25]
        actual = curve(literal_input)
        self.assertEqual(len(actual), len(expected_output))
        for a, e in zip(actual, expected_output):
            self.assertAlmostEqual(a, e, places=2)

    def test_empty_input(self):
        """Boundary input: empty list returns empty list."""
        self.assertEqual(curve([]), [])

    def test_cap_at_100(self):
        """Invariant: No grade exceeds 100%."""
        grades = [95.0, 98.0, 90.0]
        curved = curve(grades, curve_center=99.0)
        for g in curved:
            self.assertLessEqual(g, 100.0)


if __name__ == "__main__":
    unittest.main()
