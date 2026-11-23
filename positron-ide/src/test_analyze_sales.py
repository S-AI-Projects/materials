"""Focused unit and boundary contract tests for positron-ide/src/analyze_sales.py.

Verifies boundary conditions, smallest valid input, ordinary input,
empty domain boundary, and explicitly unsupported inputs.

Source fixture and contract anchors in positron-ide/src/analyze_sales.py:
    Line 9: sales = pd.read_csv(PROJECT_ROOT / "data/sales_clean.csv", parse_dates=["order_date"])
    Line 15: sales[["quantity", "unit_price", "sale_price"]]
    Line 16: sales["order_type"].value_counts()
    Line 19-20: sales.groupby(["product_category", "order_type"], as_index=False)
    Line 23: orders=("order_number", "size")
    Line 24: median_order_value=("sale_price", "median")
    Line 30-34: order_summary.pivot(index="product_category", columns="order_type", values="median_order_value")
    Line 36-40: chart_data.plot.bar(rot=0, figsize=(8, 4))
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

import analyze_sales  # noqa: E402


class TestAnalyzeSalesBoundaryContract(unittest.TestCase):
    """Test suite defining and verifying the supported boundaries of analyze_sales."""

    def setUp(self):
        # Smallest valid input fixture (1 row, literal inputs)
        self.smallest_valid_input = {
            "order_number": [1001],
            "order_date": ["2019-02-09"],
            "order_type": ["Retail"],
            "product_category": ["Olive Oil"],
            "quantity": [1],
            "unit_price": [45.0],
            "sale_price": [45.0],
        }

        # Ordinary input fixture (3 rows across categories and order types)
        self.ordinary_input = {
            "order_number": [1001, 1002, 1003],
            "order_date": ["2019-02-09", "2019-02-15", "2019-02-16"],
            "order_type": ["Retail", "Retail", "Wholesale"],
            "product_category": ["Olive Oil", "Olive Oil", "Bath products"],
            "quantity": [2, 1, 4],
            "unit_price": [45.0, 19.5, 26.0],
            "sale_price": [90.0, 19.5, 104.0],
        }

        # Valid boundary input fixture (0 rows empty schema)
        self.empty_boundary_input = {
            "order_number": [],
            "order_date": [],
            "order_type": [],
            "product_category": [],
            "quantity": [],
            "unit_price": [],
            "sale_price": [],
        }

    def test_precondition_anchors_and_schema(self):
        """Precondition established at Lines 15-24: required columns for sales analysis."""
        for col in [
            "order_number",
            "order_date",
            "order_type",
            "product_category",
            "quantity",
            "unit_price",
            "sale_price",
        ]:
            self.assertIn(col, analyze_sales.REQUIRED_COLUMNS)

    def test_smallest_valid_input(self):
        """Smallest valid input: single-row sales dataset (length 1).

        Preconditions: Lines 19-24, 30-34.
        Literal input: 1 retail order of Olive Oil with sale_price 45.0.
        Independently calculated expected output:
          - order_summary: 1 row, product_category='Olive Oil', order_type='Retail', orders=1, median_order_value=45.0
          - chart_data: index=['Olive Oil'], column 'Retail' has value 45.0
        """
        df = pd.DataFrame(self.smallest_valid_input)
        self.assertTrue(analyze_sales.validate_sales_data(df))

        summary = analyze_sales.summarize_orders(df)
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary.loc[0, "product_category"], "Olive Oil")
        self.assertEqual(summary.loc[0, "order_type"], "Retail")
        self.assertEqual(summary.loc[0, "orders"], 1)
        self.assertEqual(summary.loc[0, "median_order_value"], 45.0)

        chart = analyze_sales.build_chart_data(summary)
        self.assertIn("Retail", chart.columns)
        self.assertEqual(chart.loc["Olive Oil", "Retail"], 45.0)

    def test_ordinary_valid_input(self):
        """Ordinary input: multi-row dataset with mixed categories and order types.

        Preconditions: Lines 19-24, 30-34.
        Literal input: 3 orders (2 Olive Oil Retail with sale_prices [90.0, 19.5], 1 Bath products Wholesale with 104.0).
        Independently calculated expected output:
          - Olive Oil Retail: orders=2, median=(90.0 + 19.5)/2 = 54.75
          - Bath products Wholesale: orders=1, median=104.0
        """
        df = pd.DataFrame(self.ordinary_input)
        self.assertTrue(analyze_sales.validate_sales_data(df))

        summary = analyze_sales.summarize_orders(df)
        self.assertEqual(len(summary), 2)

        olive_oil_retail = summary[
            (summary["product_category"] == "Olive Oil")
            & (summary["order_type"] == "Retail")
        ].iloc[0]
        self.assertEqual(olive_oil_retail["orders"], 2)
        self.assertEqual(olive_oil_retail["median_order_value"], 54.75)

        bath_wholesale = summary[
            (summary["product_category"] == "Bath products")
            & (summary["order_type"] == "Wholesale")
        ].iloc[0]
        self.assertEqual(bath_wholesale["orders"], 1)
        self.assertEqual(bath_wholesale["median_order_value"], 104.0)

        chart = analyze_sales.build_chart_data(summary)
        self.assertEqual(chart.loc["Olive Oil", "Retail"], 54.75)
        self.assertEqual(chart.loc["Bath products", "Wholesale"], 104.0)

    def test_valid_boundary_empty_dataset(self):
        """Valid boundary: empty dataset (0 rows) with required columns.

        Preconditions: Lines 19-24, 30-34.
        Literal input: Empty DataFrame with required columns.
        Independently calculated expected output:
          - order_summary: empty DataFrame with correct summary columns
          - chart_data: empty DataFrame
        """
        df = pd.DataFrame(self.empty_boundary_input)
        self.assertTrue(analyze_sales.validate_sales_data(df))

        summary = analyze_sales.summarize_orders(df)
        self.assertTrue(summary.empty)
        self.assertListEqual(
            list(summary.columns),
            ["product_category", "order_type", "orders", "median_order_value"],
        )

        chart = analyze_sales.build_chart_data(summary)
        self.assertTrue(chart.empty)

    def test_unsupported_none_input(self):
        """Unsupported input: None raises ValueError.

        Preconditions: Lines 15-24 contract guard.
        """
        with self.assertRaises(ValueError) as ctx:
            analyze_sales.validate_sales_data(None)
        self.assertIn("Sales data cannot be None", str(ctx.exception))

    def test_unsupported_missing_required_column(self):
        """Unsupported input: missing 'sale_price' column raises ValueError.

        Preconditions: Line 15, 24 contract guard.
        """
        incomplete = {
            "order_number": [1001],
            "order_date": ["2019-02-09"],
            "order_type": ["Retail"],
            "product_category": ["Olive Oil"],
            "quantity": [1],
            "unit_price": [45.0],
            # 'sale_price' missing
        }
        with self.assertRaises(ValueError) as ctx:
            analyze_sales.validate_sales_data(incomplete)
        self.assertIn("Missing required columns", str(ctx.exception))
        self.assertIn("sale_price", str(ctx.exception))

    def test_unsupported_data_type(self):
        """Unsupported input: non-DataFrame non-dict type raises ValueError.

        Preconditions: Input validation contract guard.
        """
        for invalid_val in [12345, "invalid_string", [1, 2, 3]]:
            with self.subTest(invalid_val=invalid_val):
                with self.assertRaises(ValueError) as ctx:
                    analyze_sales.validate_sales_data(invalid_val)
                self.assertIn(
                    "Unsupported sales data type", str(ctx.exception)
                )

    def test_plot_sales_chart_mocked(self):
        """Verify plotting behavior with external I/O (matplotlib) mocked.

        Preconditions: Lines 36-40.
        """
        df = pd.DataFrame(self.smallest_valid_input)
        summary = analyze_sales.summarize_orders(df)
        chart = analyze_sales.build_chart_data(summary)

        with patch("matplotlib.pyplot.show") as mock_show:
            ax = analyze_sales.plot_sales_chart(chart, show=True)
            self.assertIsNotNone(ax)
            mock_show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
