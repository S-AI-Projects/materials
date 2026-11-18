"""Regression and unit test suite for opencode/dice_improved.py.

Covers input/output contract, boundary validation, precondition anchors,
and pure non-mutating execution of `parse_input`.
"""

import inspect
import unittest
from typing import List

from opencode import dice_improved
from opencode.dice_improved import (
    MAX_DICE,
    MIN_DICE,
    generate_dice_faces_diagram,
    parse_input,
    roll_dice,
)


class TestParseInputContract(unittest.TestCase):
    """Test suite locking down the contract of parse_input."""

    def test_precondition_anchors_and_constants(self):
        """Verify constant anchors and source precondition lines."""
        self.assertEqual(MIN_DICE, 1, "MIN_DICE must be 1 (established near Line 20)")
        self.assertEqual(MAX_DICE, 6, "MAX_DICE must be 6 (established near Line 21)")

        # Verify source data anchors exist in module source
        module_source = inspect.getsource(dice_improved)
        self.assertIn(
            "roll_results = []",
            module_source,
            "Anchor roll_results = [] must be present in roll_dice",
        )
        self.assertIn(
            "dice_faces = []",
            module_source,
            "Anchor dice_faces = [] must be present in _get_dice_faces",
        )

    def test_smallest_valid_input(self):
        """Verify smallest valid input ('1') returns integer 1."""
        literal_input = "1"
        expected_output = 1
        actual_output = parse_input(literal_input)
        self.assertEqual(actual_output, expected_output)
        self.assertIsInstance(actual_output, int)

    def test_smallest_valid_input_with_whitespace(self):
        """Verify smallest valid input with leading and trailing whitespace."""
        literal_input = "  1  \n"
        expected_output = 1
        self.assertEqual(parse_input(literal_input), expected_output)

    def test_ordinary_valid_input_three(self):
        """Verify ordinary valid input ('3') returns integer 3."""
        literal_input = "3"
        expected_output = 3
        actual_output = parse_input(literal_input)
        self.assertEqual(actual_output, expected_output)

    def test_ordinary_valid_inputs_two_four_five(self):
        """Verify ordinary inputs 2, 4, 5 return their respective integers."""
        test_cases = [("2", 2), ("4", 4), ("5", 5)]
        for literal_input, expected in test_cases:
            with self.subTest(literal_input=literal_input):
                self.assertEqual(parse_input(literal_input), expected)

    def test_upper_boundary_input(self):
        """Verify upper boundary input ('6') returns integer 6."""
        literal_input = "6"
        expected_output = 6
        self.assertEqual(parse_input(literal_input), expected_output)

    def test_repeated_value_and_purity(self):
        """Verify repeated calls with identical inputs produce identical outputs without state mutation."""
        for _ in range(10):
            self.assertEqual(parse_input("3"), 3)
            self.assertEqual(parse_input("1"), 1)
            self.assertEqual(parse_input("6"), 6)

    def test_input_immutability(self):
        """Verify caller input string is not modified or mutated."""
        input_str = "4"
        cached_id = id(input_str)
        result = parse_input(input_str)
        self.assertEqual(result, 4)
        self.assertEqual(id(input_str), cached_id)

    def test_below_minimum_boundary_raises_value_error(self):
        """Verify input below MIN_DICE raises ValueError with expected message."""
        invalid_inputs = ["0", "-1", "-99"]
        for val in invalid_inputs:
            with self.subTest(val=val):
                with self.assertRaises(ValueError) as ctx:
                    parse_input(val)
                self.assertEqual(
                    str(ctx.exception),
                    f"Please enter a number from {MIN_DICE} to {MAX_DICE}.",
                )

    def test_above_maximum_boundary_raises_value_error(self):
        """Verify input above MAX_DICE raises ValueError with expected message."""
        invalid_inputs = ["7", "8", "100"]
        for val in invalid_inputs:
            with self.subTest(val=val):
                with self.assertRaises(ValueError) as ctx:
                    parse_input(val)
                self.assertEqual(
                    str(ctx.exception),
                    f"Please enter a number from {MIN_DICE} to {MAX_DICE}.",
                )

    def test_non_integer_strings_raise_value_error(self):
        """Verify non-numeric strings raise ValueError."""
        non_integers = ["abc", "one", "1.5", "3.0", "NaN", "@#$"]
        for val in non_integers:
            with self.subTest(val=val):
                with self.assertRaises(ValueError):
                    parse_input(val)

    def test_empty_and_whitespace_strings_raise_value_error(self):
        """Verify empty and whitespace strings raise ValueError."""
        empty_inputs = ["", " ", "   ", "\t\n"]
        for val in empty_inputs:
            with self.subTest(val=val):
                with self.assertRaises(ValueError):
                    parse_input(val)


if __name__ == "__main__":
    unittest.main()
