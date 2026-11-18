"""Unit and isolated repeatability test suite for python-csv/read_csv_with_pandas.py.

Verifies deterministic execution across repeated calls, input isolation,
dependency injection seams, and source precondition citations.
"""

import io
import os
import unittest
from unittest.mock import MagicMock

from read_csv_with_pandas import FallbackDataFrame, load_hr_data, run_demo

SMALLEST_CSV = (
    "Name,Hire Date,Salary,Sick Days remaining\n"
    "Graham Chapman,03/15/14,50000.00,10\n"
)


class TestReadCsvRepeatability(unittest.TestCase):
    """Test suite evaluating isolated repeatability and dependency seams."""

    def setUp(self):
        self.csv_dir = os.path.dirname(os.path.abspath(__file__))
        self.hrdata_path = os.path.join(self.csv_dir, "hrdata.csv")

    def test_precondition_anchors(self):
        """Verify hrdata.csv exists and has expected header and row count."""
        self.assertTrue(os.path.exists(self.hrdata_path), "hrdata.csv fixture missing")
        with open(self.hrdata_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        self.assertEqual(lines[0], "Name,Hire Date,Salary,Sick Days remaining")
        self.assertEqual(len(lines) - 1, 6, "Expected 6 employee rows")

    def test_smallest_valid_input_isolated(self):
        """Verify smallest valid input (1 data row) via in-memory StringIO buffer."""
        buf = io.StringIO(SMALLEST_CSV)
        df = load_hr_data(buf)
        self.assertEqual(len(df), 1)
        self.assertIn("Graham Chapman", df["Name"][0])
        self.assertEqual(df["Salary"][0], "50000.00")

    def test_ordinary_valid_input_hrdata_fixture(self):
        """Verify ordinary valid input loading full hrdata.csv."""
        df = load_hr_data(self.hrdata_path)
        self.assertEqual(len(df), 6)
        self.assertEqual(df["Name"][0], "Graham Chapman")
        self.assertEqual(df["Name"][5], "Michael Palin")

    def test_repeatability_over_repeated_calls(self):
        """Verify 10 repeated calls produce bit-for-bit identical outputs."""
        results = []
        for _ in range(10):
            df = load_hr_data(self.hrdata_path)
            results.append(df.to_dict())

        first = results[0]
        for r in results[1:]:
            self.assertEqual(r, first, "Output must be strictly deterministic across calls")

    def test_input_isolation(self):
        """Verify mutating caller structures does not affect subsequent read_csv calls."""
        df1 = load_hr_data(self.hrdata_path)
        records1 = df1.to_dict()
        records1[0]["Name"] = "MUTATED_NAME"

        df2 = load_hr_data(self.hrdata_path)
        self.assertEqual(df2["Name"][0], "Graham Chapman")
        self.assertNotEqual(df2["Name"][0], "MUTATED_NAME")

    def test_dependency_injection_seam(self):
        """Verify custom reader injection seam functions as intended."""
        mock_reader = MagicMock(return_value="mocked_data_frame")
        res = load_hr_data(self.hrdata_path, reader=mock_reader)
        self.assertEqual(res, "mocked_data_frame")
        mock_reader.assert_called_once()

    def test_renamed_columns_mapping(self):
        """Verify header=0 with custom names maps columns correctly."""
        buf = io.StringIO(SMALLEST_CSV)
        df = load_hr_data(
            buf,
            header=0,
            names=["Employee", "Hired", "Salary", "Sick Days"],
        )
        self.assertEqual(df.columns, ["Employee", "Hired", "Salary", "Sick Days"])
        self.assertEqual(df["Employee"][0], "Graham Chapman")


if __name__ == "__main__":
    unittest.main()
