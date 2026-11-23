"""
Reference comparison regression tests for python-formatted-output/format.py.
Compares Python formatted output against an independent algorithmic reference oracle.
"""

import unittest
from pathlib import Path
import sys

PKG_DIR = Path(__file__).resolve().parent
if str(PKG_DIR) not in sys.path:
    sys.path.insert(0, str(PKG_DIR))

import format as fmt_mod


def oracle_binary(val: int) -> str:
    """Independent reference implementation converting non-negative int to binary string.
    Does NOT call format(), f-string or % formatting.
    """
    if val < 0:
        raise ValueError("Oracle only handles non-negative ints")
    if val == 0:
        return "0"
    bits = []
    current = val
    while current > 0:
        bits.append(str(current % 2))
        current //= 2
    return "".join(reversed(bits))


class TestFormattedOutputReferenceComparison(unittest.TestCase):
    def test_precondition_line1_ordinary_input(self):
        """Precondition: Line 1 establishes `f"{257:b}"`.
        Literal input: 257.
        Expected output independently calculated: 256 + 1 = 2^8 + 2^0 -> "100000001".
        """
        expected = "100000001"
        actual = fmt_mod.format_binary(257)
        self.assertEqual(actual, expected)
        self.assertEqual(actual, oracle_binary(257))

    def test_precondition_line1_smallest_valid_input(self):
        """Precondition: Line 1 establishes binary formatting for non-negative ints.
        Smallest valid input: 0.
        Expected output independently calculated: "0".
        """
        expected = "0"
        actual = fmt_mod.format_binary(0)
        self.assertEqual(actual, expected)
        self.assertEqual(actual, oracle_binary(0))

    def test_oracle_comparison_across_at_least_20_inputs(self):
        """Step 3: Enumerate at least 20 small valid inputs and compare outputs against the oracle."""
        test_inputs = [
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            15, 16, 17, 31, 32, 63, 64, 127, 128, 255, 256, 257, 512, 1024
        ]
        self.assertGreaterEqual(len(test_inputs), 20)

        for val in test_inputs:
            expected = oracle_binary(val)
            actual = fmt_mod.format_binary(val)
            self.assertEqual(
                actual, expected,
                f"Mismatch for input {val}: expected {expected}, got {actual}"
            )

    def test_precondition_line4_character_formatting(self):
        """Precondition: Line 4 establishes character formatting `f"{42:c}"`.
        Literal input: 42. Expected output: "*".
        Smallest valid code point: 0. Expected output: "\x00".
        """
        self.assertEqual(fmt_mod.format_char(42), "*")
        self.assertEqual(fmt_mod.format_char(0), "\x00")

    def test_invalid_type_guard(self):
        """Ensure non-int inputs raise TypeError rather than arbitrary results."""
        with self.assertRaises(TypeError):
            fmt_mod.format_binary("257")  # type: ignore
        with self.assertRaises(TypeError):
            fmt_mod.format_char("42")  # type: ignore


if __name__ == "__main__":
    unittest.main()
