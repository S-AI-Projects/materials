"""Native unit tests for split_list in python-list/chunks.py.

Verifies input/output contract, smallest valid inputs, ordinary inputs,
boundary cases, input immutability, and fixture anchors.
"""

import inspect
import unittest
from pathlib import Path

import chunks


class TestSplitListContract(unittest.TestCase):
    """Test suite locking down the contract of split_list."""

    def test_precondition_anchor_present(self):
        """Verify the source fixture anchor 'chunks = []' is present with source line."""
        source_path = Path(__file__).parent / "chunks.py"
        self.assertTrue(source_path.exists(), "chunks.py does not exist")

        lines = source_path.read_text().splitlines()
        anchor_lines = [
            (idx + 1, line)
            for idx, line in enumerate(lines)
            if "chunks = []" in line and not line.strip().startswith("#")
        ]
        self.assertTrue(
            len(anchor_lines) >= 1,
            "Precondition anchor 'chunks = []' must be present in chunks.py",
        )
        line_num, line_str = anchor_lines[0]
        self.assertEqual(line_str.strip(), "chunks = []")
        self.assertGreater(line_num, 0)

    def test_smallest_valid_input_empty_list(self):
        """Smallest valid input: empty list with chunk size 1 yields empty list."""
        inp_list = []
        chunk_size = 1
        expected = []
        actual = chunks.split_list(inp_list, chunk_size)
        self.assertEqual(actual, expected)

    def test_smallest_valid_input_single_element(self):
        """Smallest non-empty list with chunk size 1 yields single chunk."""
        inp_list = [1]
        chunk_size = 1
        expected = [[1]]
        actual = chunks.split_list(inp_list, chunk_size)
        self.assertEqual(actual, expected)

    def test_ordinary_input_even_split(self):
        """Ordinary input evenly divided into equal-sized chunks."""
        inp_list = [10, 20, 30, 40]
        chunk_size = 2
        expected = [[10, 20], [30, 40]]
        actual = chunks.split_list(inp_list, chunk_size)
        self.assertEqual(actual, expected)

    def test_ordinary_input_uneven_split(self):
        """Ordinary input where the last chunk has fewer elements."""
        inp_list = [1, 2, 3, 4, 5]
        chunk_size = 2
        expected = [[1, 2], [3, 4], [5]]
        actual = chunks.split_list(inp_list, chunk_size)
        self.assertEqual(actual, expected)

    def test_ordinary_input_string_elements(self):
        """Ordinary input with string elements."""
        inp_list = ["alpha", "beta", "gamma", "delta", "epsilon"]
        chunk_size = 3
        expected = [["alpha", "beta", "gamma"], ["delta", "epsilon"]]
        actual = chunks.split_list(inp_list, chunk_size)
        self.assertEqual(actual, expected)

    def test_chunk_size_equal_to_list_length(self):
        """Boundary: chunk_size equal to list length produces single chunk."""
        inp_list = [1, 2, 3]
        chunk_size = 3
        expected = [[1, 2, 3]]
        actual = chunks.split_list(inp_list, chunk_size)
        self.assertEqual(actual, expected)

    def test_chunk_size_greater_than_list_length(self):
        """Boundary: chunk_size greater than list length produces single chunk."""
        inp_list = [1, 2, 3]
        chunk_size = 10
        expected = [[1, 2, 3]]
        actual = chunks.split_list(inp_list, chunk_size)
        self.assertEqual(actual, expected)

    def test_repeated_values_boundary(self):
        """Boundary: input with identical repeated values retains duplicate elements."""
        inp_list = [7, 7, 7, 7]
        chunk_size = 2
        expected = [[7, 7], [7, 7]]
        actual = chunks.split_list(inp_list, chunk_size)
        self.assertEqual(actual, expected)

    def test_repeated_mixed_values_boundary(self):
        """Boundary: alternating repeated values across chunk boundaries."""
        inp_list = ["a", "a", "b", "b", "a"]
        chunk_size = 2
        expected = [["a", "a"], ["b", "b"], ["a"]]
        actual = chunks.split_list(inp_list, chunk_size)
        self.assertEqual(actual, expected)

    def test_input_non_mutation(self):
        """Verify split_list does not mutate caller's original list."""
        original = [1, 2, 3, 4, 5]
        snapshot = list(original)
        _ = chunks.split_list(original, 2)
        self.assertEqual(original, snapshot, "Original list was mutated by split_list")

    def test_output_isolation(self):
        """Verify modifying returned chunks does not mutate the source list."""
        source = [100, 200, 300]
        result = chunks.split_list(source, 2)
        result[0].append(999)
        self.assertEqual(source, [100, 200, 300], "Mutating chunk affected source list")


if __name__ == "__main__":
    unittest.main()
