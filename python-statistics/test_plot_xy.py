"""Unit and executable documentation tests for python-statistics/plot_xy.py.

Precondition Anchors:
- Lines 15-16: coordinate arrays x and y establishing bivariate regression dataset.
- Line 18: slope, intercept, r calculation via linear regression.
- Line 19: line = f"Regression line: y={intercept:.2f}+{slope:.2f}x, r={r:.2f}"
"""

import doctest
import pathlib
import sys
import unittest

PROJECT_DIR = pathlib.Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import plot_xy


class TestPlotXYDocumentation(unittest.TestCase):
    def test_executable_docstring_example(self):
        """Execute docstring example and assert displayed output."""
        x = [0.0, 1.0]
        y = [5.0, 7.0]
        slope, intercept, r, line = plot_xy.compute_regression_line(x, y)
        expected_line = "Regression line: y=5.00+2.00x, r=1.00"
        self.assertEqual(line, expected_line)
        self.assertAlmostEqual(slope, 2.0)
        self.assertAlmostEqual(intercept, 5.0)
        self.assertAlmostEqual(r, 1.0)

    def test_smallest_valid_input(self):
        """Smallest valid input boundary: minimal line defined by 2 distinct points."""
        # Preconditions established at lines 15, 18, 19
        x = [0.0, 1.0]
        y = [5.0, 7.0]
        # Decisive state transition:
        # mean_x = 0.5, mean_y = 6.0
        # ss_xx = 0.5, ss_xy = 1.0 -> slope = 2.0
        # intercept = 6.0 - 2.0 * 0.5 = 5.0
        # r = 1.0
        slope, intercept, r, line = plot_xy.main(x=x, y=y, show=False)
        self.assertAlmostEqual(slope, 2.0)
        self.assertAlmostEqual(intercept, 5.0)
        self.assertAlmostEqual(r, 1.0)
        self.assertEqual(line, "Regression line: y=5.00+2.00x, r=1.00")

    def test_ordinary_fixture_input(self):
        """Ordinary fixture input: 5 points with minor noise."""
        x = [0.0, 1.0, 2.0, 3.0, 4.0]
        y = [5.1, 7.0, 8.9, 11.2, 12.8]
        slope, intercept, r, line = plot_xy.main(x=x, y=y, show=False)
        # Independently calculated:
        # mean_x = 2.0, mean_y = 9.0
        # ss_xx = 10.0, ss_xy = 19.6 -> slope = 1.96
        # intercept = 9.0 - 1.96 * 2.0 = 5.08
        # ss_yy = 38.5 -> r = 19.6 / sqrt(385.0) = 0.9989... -> round to 1.00
        self.assertAlmostEqual(slope, 1.96, places=2)
        self.assertAlmostEqual(intercept, 5.08, places=2)
        self.assertAlmostEqual(r, 1.0, places=2)
        self.assertEqual(line, "Regression line: y=5.08+1.96x, r=1.00")

    def test_doctest_runner(self):
        """Run doctest on plot_xy module."""
        results = doctest.testmod(plot_xy)
        self.assertEqual(results.failed, 0)
        self.assertGreater(results.attempted, 0)


if __name__ == "__main__":
    unittest.main()
