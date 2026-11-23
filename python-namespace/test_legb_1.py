"""Regression and refactoring tests for python-namespace/legb_1.py.

Preconditions:
- Line 1: `x = "global"` module-level variable.
- Line 4: `def outer():` function under test.
- Line 6: `print(x)` output to stdout.
- Smallest valid input fixture: `val=""` (empty string) -> expected output `"\n"`, return `""`.
- Ordinary input fixture: `val="ordinary"` -> expected output `"ordinary\n"`, return `"ordinary"`.
- Default caller fixture: `outer()` -> expected output `"global\n"`, return `"global"`.
"""

import io
import unittest
from unittest.mock import patch

import legb_1


class TestLegbOuter(unittest.TestCase):
    """Test suite for outer() in legb_1.py."""

    def test_precondition_line4_smallest_valid_input(self):
        """Line 4: Smallest valid input fixture: empty string val=''."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            res = legb_1.outer(val="")
            self.assertEqual(res, "")
            self.assertEqual(mock_stdout.getvalue(), "\n")

    def test_precondition_line4_ordinary_input(self):
        """Line 4: Ordinary input fixture: custom string val='ordinary'."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            res = legb_1.outer(val="ordinary")
            self.assertEqual(res, "ordinary")
            self.assertEqual(mock_stdout.getvalue(), "ordinary\n")

    def test_precondition_line1_default_call_preserves_contract(self):
        """Line 1: Default call outer() with no arguments prints global variable x."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            res = legb_1.outer()
            self.assertEqual(res, "global")
            self.assertEqual(mock_stdout.getvalue(), "global\n")

    def test_extracted_formatting_responsibility(self):
        """Verify format_scope_value returns consistent string representation."""
        self.assertEqual(legb_1.format_scope_value("test"), "test")
        self.assertEqual(legb_1.format_scope_value(""), "")


if __name__ == "__main__":
    unittest.main()
