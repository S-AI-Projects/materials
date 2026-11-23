"""
Unit and regression tests for python get all files in directory (examples.py).

Precondition & Fixture Anchors:
- Line 64: SKIP_DIRS = ["temp", "temporary_files", "logs"]
- Line 71: large_dir.rglob("*")
- Line 72: if set(item.parts).isdisjoint(SKIP_DIRS):
- Lines 76-82: [item for item in large_dir.rglob("*") if set(item.parts).isdisjoint(SKIP_DIRS)]
"""

import pathlib
import sys
import unittest

PROJECT_DIR = pathlib.Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import examples


class TestGetAllFilesInDirectory(unittest.TestCase):
    def setUp(self):
        # Anchor from Line 64
        self.skip_dirs = examples.SKIP_DIRS
        self.assertEqual(self.skip_dirs, ["temp", "temporary_files", "logs"])

    def test_smallest_valid_input_empty_and_single(self):
        """Smallest valid input boundary: empty path collection and single item boundaries."""
        # Empty input (Line 72 isdisjoint on empty set)
        literal_input_empty = []
        expected_empty = []
        actual_empty = examples.filter_skip_dirs(literal_input_empty, skip_dirs=self.skip_dirs)
        self.assertEqual(actual_empty, expected_empty)

        # Single path not matching skip_dirs
        single_valid = [pathlib.Path("notes.txt")]
        expected_valid = [pathlib.Path("notes.txt")]
        self.assertEqual(examples.filter_skip_dirs(single_valid, skip_dirs=self.skip_dirs), expected_valid)

        # Single path matching skip_dirs directly
        single_skip = [pathlib.Path("logs")]
        expected_skip = []
        self.assertEqual(examples.filter_skip_dirs(single_skip, skip_dirs=self.skip_dirs), expected_skip)

    def test_ordinary_fixture_input(self):
        """Ordinary fixture input exercising both allowed paths and nested skip_dirs exclusions."""
        literal_input = [
            pathlib.Path("Desktop/realpython/iterate-dict.md"),
            pathlib.Path("Desktop/temp/cache.tmp"),
            pathlib.Path("Desktop/todo.txt"),
            pathlib.Path("Desktop/logs/app.log"),
            pathlib.Path("Desktop/temporary_files/scratch.txt"),
            pathlib.Path("Desktop/scripts/rename_files.py"),
        ]

        # Independently calculated expected output based on Line 72 contract:
        # Paths with parts containing 'temp', 'logs', or 'temporary_files' are excluded.
        expected_output = [
            pathlib.Path("Desktop/realpython/iterate-dict.md"),
            pathlib.Path("Desktop/todo.txt"),
            pathlib.Path("Desktop/scripts/rename_files.py"),
        ]

        actual_output = examples.filter_skip_dirs(literal_input, skip_dirs=self.skip_dirs)
        self.assertEqual(actual_output, expected_output)

    def test_invariants_preserved(self):
        """Verify output type, shape, ordering, and input immutability invariants."""
        input_paths = [
            pathlib.Path("Desktop/todo.txt"),
            pathlib.Path("Desktop/temp/cache.tmp"),
            pathlib.Path("Desktop/scripts/rename_files.py"),
        ]
        input_snapshot = list(input_paths)

        result = examples.filter_skip_dirs(input_paths, skip_dirs=self.skip_dirs)

        # Output type & shape
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, pathlib.Path)
        self.assertEqual(len(result), 2)

        # Ordering: preserves original relative order
        self.assertEqual(result, [
            pathlib.Path("Desktop/todo.txt"),
            pathlib.Path("Desktop/scripts/rename_files.py"),
        ])

        # Input immutability
        self.assertEqual(input_paths, input_snapshot)

    def test_nested_junk_directory_rejection(self):
        """Specifically assert that deeply nested files inside junk directories are excluded.

        A plausible one-line bug like checking `item.name not in skip_dirs` would fail
        this assertion because item.name is 'subfile.txt' (not in skip_dirs), whereas
        item.parts contains 'temp'.
        """
        nested_junk_path = pathlib.Path("nested/dir/temp/subfile.txt")
        result = examples.filter_skip_dirs([nested_junk_path], skip_dirs=self.skip_dirs)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
