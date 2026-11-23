"""Unit tests for pandas-iterate-over-rows/products.py covering failure and empty-result branches.

Precondition Anchors:
- Line 7: `cumulative_sum = []`
- Line 9: row iteration over `products`
- Line 10: `income = product.sales * product.unit_price`
"""

from collections import namedtuple
import pathlib
import sys
import unittest

PROJECT_DIR = pathlib.Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import products

ProductRow = namedtuple("ProductRow", ["sales", "unit_price"])
BrokenRow = namedtuple("BrokenRow", ["sales"])


class TestPandasIterateOverRowsFailure(unittest.TestCase):
    def test_smallest_valid_input_empty_result_branch_line9(self):
        """Smallest valid input boundary: empty iterable (0 rows) reaches the absent-result branch (line 9)."""
        empty_input = []
        expected = []
        actual = products.calculate_cumulative_income(empty_input)
        self.assertEqual(actual, expected)
        self.assertEqual(empty_input, [])  # caller state remains intact

    def test_ordinary_fixture_input_line7_14(self):
        """Ordinary fixture input: 5 monthly product sales from resources/products.csv."""
        fixture_rows = [
            ProductRow(sales=3, unit_price=0.50),
            ProductRow(sales=2, unit_price=0.53),
            ProductRow(sales=5, unit_price=0.55),
            ProductRow(sales=10, unit_price=0.71),
            ProductRow(sales=8, unit_price=0.66),
        ]
        # Independently calculated cumulative income:
        # jan: 3 * 0.50 = 1.50
        # feb: 1.50 + 2 * 0.53 = 2.56
        # mar: 2.56 + 5 * 0.55 = 5.31
        # apr: 5.31 + 10 * 0.71 = 12.41
        # may: 12.41 + 8 * 0.66 = 17.69
        expected = [1.50, 2.56, 5.31, 12.41, 17.69]
        actual = products.calculate_cumulative_income(fixture_rows)
        rounded_actual = [round(val, 2) for val in actual]
        self.assertEqual(rounded_actual, expected)

    def test_failure_path_attribute_missing_line10(self):
        """Failure branch: row missing 'unit_price' attribute triggers AttributeError at line 10."""
        invalid_input = [
            ProductRow(sales=3, unit_price=0.50),
            BrokenRow(sales=2),  # missing unit_price
        ]
        with self.assertRaises(AttributeError) as ctx:
            products.calculate_cumulative_income(invalid_input)
        self.assertIn("unit_price", str(ctx.exception))
        self.assertEqual(len(invalid_input), 2)  # caller input preserved

    def test_recovery_ordinary_call_succeeds_after_failure(self):
        """Verify ordinary valid call succeeds immediately after a raised failure."""
        invalid_input = [BrokenRow(sales=5)]
        with self.assertRaises(AttributeError):
            products.calculate_cumulative_income(invalid_input)

        # Subsequent ordinary valid call
        valid_input = [ProductRow(sales=4, unit_price=2.50)]
        actual = products.calculate_cumulative_income(valid_input)
        self.assertEqual(actual, [10.0])


if __name__ == "__main__":
    unittest.main()
