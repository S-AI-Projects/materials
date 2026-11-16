"""Regression and contract tests for python-operator-module/min_max.py.

Preconditions established by source:
    Line 1: prices = [100, 45, 345, 639] - Initial price list fixture anchor
    Line 3: print(min(prices)) - Extrema computation and presentation (min)
    Line 4: print(max(prices)) - Extrema computation and presentation (max)
"""

import contextlib
import io
from pathlib import Path
import subprocess
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "python-operator-module"

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

# Mock stdout during import to prevent polluting test discovery
with contextlib.redirect_stdout(io.StringIO()):
    import min_max


def independent_min_max_oracle(items):
    """Independent reference calculation oracle using sorted sequence.

    Calculates extrema without calling min() or max() to verify results
    against an independent algorithmic implementation.
    """
    if hasattr(items, "__iter__") and not isinstance(items, (str, bytes)):
        seq = list(items)
    else:
        seq = [items]
    if not seq:
        raise ValueError("Cannot calculate extrema for empty sequence")
    sorted_seq = sorted(seq)
    return sorted_seq[0], sorted_seq[-1]


class TestPreconditionsAndAnchors(unittest.TestCase):
    """Verify source lines and fixture preconditions."""

    def test_line1_prices_anchor(self):
        """Line 1 establishes prices = [100, 45, 345, 639]."""
        self.assertTrue(
            hasattr(min_max, "prices"), "min_max module must expose prices"
        )
        self.assertEqual(
            min_max.prices,
            [100, 45, 345, 639],
            "Line 1 anchor prices must equal [100, 45, 345, 639]",
        )

    def test_line3_line4_preconditions(self):
        """Lines 3 & 4 establish min(prices) == 45 and max(prices) == 639."""
        expected_min = 45
        expected_max = 639
        self.assertEqual(min(min_max.prices), expected_min)
        self.assertEqual(max(min_max.prices), expected_max)


class TestSmallestAndOrdinaryInputs(unittest.TestCase):
    """Verify smallest valid input and ordinary input."""

    def test_smallest_valid_input_single_element_list(self):
        """Smallest valid input is a single-element list [100]."""
        literal_input = [100]
        expected = (100, 100)
        oracle_expected = independent_min_max_oracle(literal_input)
        self.assertEqual(expected, oracle_expected)

        actual = min_max.get_min_max(literal_input)
        self.assertEqual(
            actual,
            expected,
            f"Input={literal_input!r}, expected={expected!r}, actual={actual!r}",
        )

    def test_smallest_valid_input_single_element_tuple(self):
        """Smallest valid input as a single-element tuple (45,)."""
        literal_input = (45,)
        expected = (45, 45)
        self.assertEqual(expected, independent_min_max_oracle(literal_input))
        actual = min_max.get_min_max(literal_input)
        self.assertEqual(actual, expected)

    def test_ordinary_input_prices_anchor(self):
        """Ordinary input is prices = [100, 45, 345, 639] from line 1."""
        literal_input = [100, 45, 345, 639]
        expected = (45, 639)
        oracle_expected = independent_min_max_oracle(literal_input)
        self.assertEqual(expected, oracle_expected)

        actual = min_max.get_min_max(literal_input)
        self.assertEqual(
            actual,
            expected,
            f"Input={literal_input!r}, expected={expected!r}, actual={actual!r}",
        )

    def test_default_invocation(self):
        """Calling get_min_max() without args defaults to prices anchor."""
        expected = (45, 639)
        actual = min_max.get_min_max()
        self.assertEqual(actual, expected)


class TestIndependentOracleEquivalence(unittest.TestCase):
    """Compare get_min_max against independent sorting oracle across varied inputs."""

    def test_two_elements_ordered(self):
        inp = [10, 20]
        expected = (10, 20)
        self.assertEqual(expected, independent_min_max_oracle(inp))
        self.assertEqual(min_max.get_min_max(inp), expected)

    def test_descending_elements(self):
        inp = [50, 40, 30, 20, 10]
        expected = (10, 50)
        self.assertEqual(expected, independent_min_max_oracle(inp))
        self.assertEqual(min_max.get_min_max(inp), expected)

    def test_identical_elements(self):
        inp = [7, 7, 7, 7]
        expected = (7, 7)
        self.assertEqual(expected, independent_min_max_oracle(inp))
        self.assertEqual(min_max.get_min_max(inp), expected)

    def test_negative_integers(self):
        inp = [-10, -45, -345, -5]
        expected = (-345, -5)
        self.assertEqual(expected, independent_min_max_oracle(inp))
        self.assertEqual(min_max.get_min_max(inp), expected)

    def test_mixed_signs(self):
        inp = [-50, 0, 100, -20, 30]
        expected = (-50, 100)
        self.assertEqual(expected, independent_min_max_oracle(inp))
        self.assertEqual(min_max.get_min_max(inp), expected)

    def test_floating_point_numbers(self):
        inp = [1.5, 0.25, 9.75, 4.0]
        expected = (0.25, 9.75)
        self.assertEqual(expected, independent_min_max_oracle(inp))
        self.assertEqual(min_max.get_min_max(inp), expected)

    def test_tuple_input(self):
        inp = (100, 45, 345, 639)
        expected = (45, 639)
        self.assertEqual(expected, independent_min_max_oracle(inp))
        self.assertEqual(min_max.get_min_max(inp), expected)

    def test_positional_arguments_multiple(self):
        expected = (45, 639)
        actual = min_max.get_min_max(100, 45, 345, 639)
        self.assertEqual(actual, expected)

    def test_positional_arguments_pair(self):
        expected = (42, 99)
        actual = min_max.get_min_max(42, 99)
        self.assertEqual(actual, expected)


class TestOrderingAndReturnType(unittest.TestCase):
    """Verify return type and output ordering invariant."""

    def test_return_type_is_tuple(self):
        result = min_max.get_min_max([100, 45, 345, 639])
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_ordering_invariant_min_precedes_max(self):
        test_cases = [
            [100, 45, 345, 639],
            [100],
            [50, 40, 30, 20, 10],
            [-10, 0, 10],
            [7, 7, 7],
        ]
        for inp in test_cases:
            minimum, maximum = min_max.get_min_max(inp)
            self.assertLessEqual(
                minimum,
                maximum,
                f"For input {inp}, minimum ({minimum}) must be <= maximum ({maximum})",
            )


class TestInputImmutability(unittest.TestCase):
    """Verify input collections are not mutated."""

    def test_input_list_not_mutated(self):
        original = [100, 45, 345, 639]
        cloned = list(original)
        min_max.get_min_max(cloned)
        self.assertEqual(
            cloned,
            original,
            "Input list must not be modified or reordered in-place",
        )


class TestSideEffectsAndStdout(unittest.TestCase):
    """Verify side effects: get_min_max is pure, script execution prints 45 then 639."""

    def test_get_min_max_pure_no_stdout(self):
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            min_max.get_min_max([100, 45, 345, 639])
        self.assertEqual(
            captured.getvalue(),
            "",
            "get_min_max should have no stdout side-effects",
        )

    def test_script_execution_stdout(self):
        script_path = MODULE_DIR / "min_max.py"
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            proc.stdout,
            "45\n639\n",
            "Standalone execution must print 45 and 639 to stdout",
        )


class TestAliasesAndErrorHandling(unittest.TestCase):
    """Verify function aliases and empty sequence error behavior."""

    def test_aliases_identical(self):
        self.assertIs(min_max.min_max, min_max.get_min_max)
        self.assertIs(min_max.python_operator_module, min_max.get_min_max)

    def test_empty_sequence_raises_value_error(self):
        with self.assertRaises(ValueError):
            min_max.get_min_max([])


if __name__ == "__main__":
    unittest.main()
