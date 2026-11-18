"""Unit and boundary contract tests for altair-python/steps.py.

Verifies boundary conditions, smallest valid input, ordinary input,
and error handling on invalid boundaries.
"""

import importlib.util
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Load steps.py directly from the directory
MODULE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "steps.py")
spec = importlib.util.spec_from_file_location("steps", MODULE_PATH)
steps_module = importlib.util.module_from_spec(spec)
sys.modules["steps"] = steps_module
spec.loader.exec_module(steps_module)

DEFAULT_STEPS_DATA = steps_module.DEFAULT_STEPS_DATA
create_weekly_steps_chart = steps_module.create_weekly_steps_chart
validate_steps_data = steps_module.validate_steps_data


class TestStepsBoundaryContract(unittest.TestCase):
    """Test suite defining and verifying the supported boundaries of steps.py."""

    def test_precondition_anchors_and_defaults(self):
        """Verify fixture anchors: 7 days and corresponding steps exist."""
        self.assertIn("Day", DEFAULT_STEPS_DATA)
        self.assertIn("Steps", DEFAULT_STEPS_DATA)
        self.assertEqual(len(DEFAULT_STEPS_DATA["Day"]), 7)
        self.assertEqual(len(DEFAULT_STEPS_DATA["Steps"]), 7)
        self.assertEqual(DEFAULT_STEPS_DATA["Day"][0], "1-Mon")
        self.assertEqual(DEFAULT_STEPS_DATA["Steps"][0], 6200)

    def test_smallest_valid_input(self):
        """Verify smallest valid input: single-element dataset (length 1)."""
        smallest_input = {"Day": ["1-Mon"], "Steps": [5000]}
        self.assertTrue(validate_steps_data(smallest_input))
        result = create_weekly_steps_chart(smallest_input)
        self.assertIsNotNone(result)

    def test_ordinary_valid_input(self):
        """Verify ordinary valid input: standard 7-day dataset."""
        ordinary_input = {
            "Day": ["1-Mon", "2-Tue", "3-Wed", "4-Thu", "5-Fri", "6-Sat", "7-Sun"],
            "Steps": [6000, 7000, 8000, 9000, 10000, 11000, 12000],
        }
        self.assertTrue(validate_steps_data(ordinary_input))
        result = create_weekly_steps_chart(ordinary_input)
        self.assertIsNotNone(result)

    def test_valid_boundary_empty_dataset(self):
        """Verify valid boundary: empty dataset (length 0)."""
        empty_input = {"Day": [], "Steps": []}
        self.assertTrue(validate_steps_data(empty_input))
        result = create_weekly_steps_chart(empty_input)
        self.assertIsNotNone(result)

    def test_unsupported_none_input(self):
        """Verify explicitly unsupported input: None raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            validate_steps_data(None)
        self.assertIn("Data cannot be None", str(ctx.exception))

    def test_unsupported_missing_steps_column(self):
        """Verify missing 'Steps' column raises ValueError."""
        invalid_input = {"Day": ["1-Mon", "2-Tue"]}
        with self.assertRaises(ValueError) as ctx:
            validate_steps_data(invalid_input)
        self.assertIn("must contain both 'Day' and 'Steps'", str(ctx.exception))

    def test_unsupported_missing_day_column(self):
        """Verify missing 'Day' column raises ValueError."""
        invalid_input = {"Steps": [1000, 2000]}
        with self.assertRaises(ValueError) as ctx:
            validate_steps_data(invalid_input)
        self.assertIn("must contain both 'Day' and 'Steps'", str(ctx.exception))

    def test_unsupported_data_type(self):
        """Verify unsupported data types (list, int, str) raise ValueError."""
        for invalid_val in [123, ["Day", "Steps"], "invalid_string"]:
            with self.subTest(invalid_val=invalid_val):
                with self.assertRaises(ValueError):
                    validate_steps_data(invalid_val)

    def test_chart_creation_pipeline_with_mock_altair(self):
        """Verify Chart call chain when altair is present or mocked."""
        mock_alt = MagicMock()
        mock_chart = MagicMock()
        mock_mark = MagicMock()
        mock_alt.Chart.return_value = mock_chart
        mock_chart.mark_bar.return_value = mock_mark
        mock_mark.encode.return_value = "configured_chart"

        with patch.object(steps_module, "alt", mock_alt):
            chart = create_weekly_steps_chart(DEFAULT_STEPS_DATA)
            mock_alt.Chart.assert_called_once()
            mock_chart.mark_bar.assert_called_once()
            mock_mark.encode.assert_called_once_with(x="Day", y="Steps")
            self.assertEqual(chart, "configured_chart")


if __name__ == "__main__":
    unittest.main()
