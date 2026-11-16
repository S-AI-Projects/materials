"""Unit and regression tests for python-flatten-list/flatten.py.

Verifies the contract, behavior, intermediate states, and executable worked
example for flatten_extend.

Preconditions established by source:
    Line 7: flat_list = [] - Initial accumulator list for flatten_extend
    Line 14: flat_list = [] - Initial accumulator list for flatten_concatenation
"""

import contextlib
import doctest
import io
from pathlib import Path
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "python-flatten-list"

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import flatten  # noqa: E402


def independent_flatten_oracle(matrix):
    """Independent reference calculation oracle for flattening nested iterables.

    Uses an independent nested list comprehension to compute the flattened
    sequence without invoking flatten_extend or list.extend().
    """
    return [item for row in matrix for item in row]


class TestPreconditionsAndAnchors(unittest.TestCase):
    """Verify source lines, data anchors, and public interface."""

    def setUp(self):
        self.source_path = MODULE_DIR / "flatten.py"
        self.assertTrue(self.source_path.is_file(), "flatten.py must exist")
        self.source_lines = self.source_path.read_text(
            encoding="utf-8"
        ).splitlines()

    def test_anchor_preconditions_in_source(self):
        """Verify the two flat_list = [] fixture anchors exist in flatten.py.

        Anchor 1: Line 7 in original baseline establishes flat_list = []
                  accumulator for flatten_extend.
        Anchor 2: Line 14 in original baseline establishes flat_list = []
                  accumulator for flatten_concatenation.
        """
        stripped_lines = [line.strip() for line in self.source_lines]
        matching_indices = [
            idx + 1
            for idx, line in enumerate(stripped_lines)
            if line == "flat_list = []"
        ]
        self.assertGreaterEqual(
            len(matching_indices),
            2,
            f"Expected at least two 'flat_list = []' anchors, found at lines {matching_indices}",
        )

    def test_flatten_extend_callable(self):
        """Verify flatten_extend is exposed and callable."""
        self.assertTrue(hasattr(flatten, "flatten_extend"))
        self.assertTrue(callable(flatten.flatten_extend))


class TestSmallestAndOrdinaryInputs(unittest.TestCase):
    """Verify smallest valid input and ordinary inputs with literal values."""

    def test_smallest_valid_input_empty_list(self):
        """Smallest valid input is an empty list [].

        Line 7 establishes flat_list = [].
        With zero rows, loop does not execute, returning [].
        """
        literal_input = []
        expected = []
        oracle_expected = independent_flatten_oracle(literal_input)
        self.assertEqual(expected, oracle_expected)

        actual = flatten.flatten_extend(literal_input)
        self.assertEqual(actual, expected)
        self.assertIsInstance(actual, list)
        self.assertIsNot(actual, literal_input)

    def test_smallest_valid_input_single_empty_row(self):
        """Smallest valid input with row is [[]].

        Line 7 establishes flat_list = [].
        Row 1 is empty, extending flat_list with [] yields [].
        """
        literal_input = [[]]
        expected = []
        oracle_expected = independent_flatten_oracle(literal_input)
        self.assertEqual(expected, oracle_expected)

        actual = flatten.flatten_extend(literal_input)
        self.assertEqual(actual, expected)
        self.assertIsInstance(actual, list)

    def test_ordinary_input_3x3_matrix(self):
        """Ordinary input: 3x3 matrix [[1, 2, 3], [4, 5, 6], [7, 8, 9]].

        Line 7 establishes flat_list = [].
        Intermediate states:
          Initial: []
          Step 1: [1, 2, 3]
          Step 2: [1, 2, 3, 4, 5, 6]
          Step 3: [1, 2, 3, 4, 5, 6, 7, 8, 9]
        """
        literal_input = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        oracle_expected = independent_flatten_oracle(literal_input)
        self.assertEqual(expected, oracle_expected)

        actual = flatten.flatten_extend(literal_input)
        self.assertEqual(actual, expected)

    def test_ordinary_input_2x2_matrix(self):
        """Ordinary input: 2x2 matrix [[1, 2], [3, 4]]."""
        literal_input = [[1, 2], [3, 4]]
        expected = [1, 2, 3, 4]
        oracle_expected = independent_flatten_oracle(literal_input)
        self.assertEqual(expected, oracle_expected)

        actual = flatten.flatten_extend(literal_input)
        self.assertEqual(actual, expected)


class TestIntermediateStatesAndDecisiveTransition(unittest.TestCase):
    """Verify hand-calculated intermediate states and decisive state transition."""

    def test_intermediate_states_trace(self):
        """Trace step-by-step state transitions for 3x3 matrix.

        Decisive state transition:
        flat_list.extend(row) modifies accumulator flat_list in-place,
        unpacking elements of row into the existing list buffer.
        """
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        # Manual execution following flatten.py line 7-10
        flat_list = []  # Line 7
        self.assertEqual(flat_list, [])
        accumulator_id = id(flat_list)

        # Iteration 1
        row1 = matrix[0]
        flat_list.extend(row1)
        self.assertEqual(flat_list, [1, 2, 3])
        self.assertEqual(len(flat_list), 3)
        self.assertEqual(
            id(flat_list), accumulator_id, "extend must mutate in-place"
        )

        # Iteration 2
        row2 = matrix[1]
        flat_list.extend(row2)
        self.assertEqual(flat_list, [1, 2, 3, 4, 5, 6])
        self.assertEqual(len(flat_list), 6)
        self.assertEqual(
            id(flat_list), accumulator_id, "extend must mutate in-place"
        )

        # Iteration 3
        row3 = matrix[2]
        flat_list.extend(row3)
        self.assertEqual(flat_list, [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(len(flat_list), 9)
        self.assertEqual(
            id(flat_list), accumulator_id, "extend must mutate in-place"
        )

        # Result matches flatten_extend
        self.assertEqual(flat_list, flatten.flatten_extend(matrix))

    def test_caller_input_not_mutated(self):
        """Verify that flatten_extend does not mutate the caller's input."""
        original_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        cloned_matrix = [list(row) for row in original_matrix]

        result = flatten.flatten_extend(cloned_matrix)
        self.assertEqual(
            cloned_matrix, original_matrix, "Input matrix must not be mutated"
        )
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8, 9])


class TestIndependentOracleEquivalence(unittest.TestCase):
    """Verify equivalence between flatten_extend and independent oracle across 20 cases."""

    TEST_CASES = [
        {
            "id": "TC-01",
            "desc": "Smallest valid input (empty)",
            "input": [],
            "expected": [],
        },
        {
            "id": "TC-02",
            "desc": "Single empty row",
            "input": [[]],
            "expected": [],
        },
        {
            "id": "TC-03",
            "desc": "Ordinary 3x3 consecutive integers",
            "input": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            "expected": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        },
        {
            "id": "TC-04",
            "desc": "Ordinary 2x2 matrix",
            "input": [[1, 2], [3, 4]],
            "expected": [1, 2, 3, 4],
        },
        {
            "id": "TC-05",
            "desc": "Single element matrix",
            "input": [[42]],
            "expected": [42],
        },
        {
            "id": "TC-06",
            "desc": "Single row multiple elements",
            "input": [[10, 20, 30]],
            "expected": [10, 20, 30],
        },
        {
            "id": "TC-07",
            "desc": "Multiple single-element rows",
            "input": [[1], [2], [3], [4]],
            "expected": [1, 2, 3, 4],
        },
        {
            "id": "TC-08",
            "desc": "String words",
            "input": [["apple", "banana"], ["cherry", "date"]],
            "expected": ["apple", "banana", "cherry", "date"],
        },
        {
            "id": "TC-09",
            "desc": "Character letters",
            "input": [["a", "b", "c"], ["d", "e"]],
            "expected": ["a", "b", "c", "d", "e"],
        },
        {
            "id": "TC-10",
            "desc": "Negative integers",
            "input": [[-5, -4], [-3, -2], [-1, 0]],
            "expected": [-5, -4, -3, -2, -1, 0],
        },
        {
            "id": "TC-11",
            "desc": "Floating point numbers",
            "input": [[1.1, 2.2], [3.3, 4.4]],
            "expected": [1.1, 2.2, 3.3, 4.4],
        },
        {
            "id": "TC-12",
            "desc": "Mixed heterogeneous types",
            "input": [[1, "two"], [3.0, True, None]],
            "expected": [1, "two", 3.0, True, None],
        },
        {
            "id": "TC-13",
            "desc": "Ragged irregular rows",
            "input": [[1], [2, 3, 4], [5, 6]],
            "expected": [1, 2, 3, 4, 5, 6],
        },
        {
            "id": "TC-14",
            "desc": "Interspersed empty rows",
            "input": [[], [1, 2], [], [3, 4], []],
            "expected": [1, 2, 3, 4],
        },
        {
            "id": "TC-15",
            "desc": "Multiple empty rows",
            "input": [[], [], []],
            "expected": [],
        },
        {
            "id": "TC-16",
            "desc": "List of tuples",
            "input": [(1, 2), (3, 4), (5, 6)],
            "expected": [1, 2, 3, 4, 5, 6],
        },
        {
            "id": "TC-17",
            "desc": "Tuple of lists",
            "input": ([1, 2], [3, 4]),
            "expected": [1, 2, 3, 4],
        },
        {
            "id": "TC-18",
            "desc": "Duplicate elements",
            "input": [[1, 1], [1, 1], [2, 2]],
            "expected": [1, 1, 1, 1, 2, 2],
        },
        {
            "id": "TC-19",
            "desc": "Zero-filled matrix",
            "input": [[0, 0, 0], [0, 0, 0]],
            "expected": [0, 0, 0, 0, 0, 0],
        },
        {
            "id": "TC-20",
            "desc": "Generated sequence",
            "input": [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
            "expected": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        },
    ]

    def test_all_cases_match_oracle_and_expected(self):
        """Verify each of the 20 test cases matches oracle and explicit expected."""
        for case in self.TEST_CASES:
            with self.subTest(case_id=case["id"], desc=case["desc"]):
                literal_input = case["input"]
                expected = case["expected"]
                oracle_val = independent_flatten_oracle(literal_input)

                self.assertEqual(
                    oracle_val,
                    expected,
                    f"Oracle mismatch for {case['id']}: {oracle_val} != {expected}",
                )

                actual = flatten.flatten_extend(literal_input)
                self.assertEqual(
                    actual,
                    expected,
                    f"Actual mismatch for {case['id']}: {actual} != {expected}",
                )


class TestDocumentationAndWorkedExample(unittest.TestCase):
    """Verify docstrings, doctests, and execution of the worked example."""

    def test_doctest_execution(self):
        """Execute doctest on flatten module and verify zero failures."""
        results = doctest.testmod(flatten)
        self.assertEqual(
            results.failed,
            0,
            f"Doctest failed {results.failed} out of {results.attempted} tests",
        )

    def test_worked_example_execution_if_present(self):
        """Execute run_worked_example if defined, asserting its displayed output."""
        if hasattr(flatten, "run_worked_example"):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                flatten.run_worked_example()
            output = buf.getvalue()
            self.assertIn("flatten_extend", output)
            self.assertIn("Smallest Valid Input", output)
            self.assertIn("Ordinary Input", output)
            self.assertIn("flat_list = []", output)
            self.assertIn("[1, 2, 3, 4, 5, 6, 7, 8, 9]", output)
            self.assertIn("Decisive transition", output)


class TestExistingSupportedBehavior(unittest.TestCase):
    """Verify that all sibling flattening implementations are preserved intact."""

    def test_sibling_functions_agreement(self):
        """All flatten variants in flatten.py produce equivalent results for ordinary input."""
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        functions = [
            flatten.flatten_extend,
            flatten.flatten_concatenation,
            flatten.flatten_comprehension,
            flatten.flatten_chain,
            flatten.flatten_reduce_lambda,
            flatten.flatten_reduce_add,
            flatten.flatten_reduce_concat,
            flatten.flatten_reduce_iconcat,
            flatten.flatten_sum,
        ]

        for func in functions:
            with self.subTest(func=func.__name__):
                actual = func(matrix)
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
