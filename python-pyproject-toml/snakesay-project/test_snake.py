"""Unit and regression tests for bubble in python-pyproject-toml/snakesay-project/snakesay/snake.py.

Precondition Anchors:
- Line 12: `def bubble(message):`
- Line 13: `bubble_length = len(message) + 2` establishes 2 characters of horizontal padding.
- Lines 14-17: multi-line speech bubble format with top underscore border,
  center `( {message} )    `, and bottom overline border.
"""

import pathlib
import sys
import unittest

PROJECT_DIR = pathlib.Path(__file__).resolve().parent / "snakesay"
if str(PROJECT_DIR.parent) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR.parent))

from snakesay import snake


class TestSnakeBubble(unittest.TestCase):
    def test_smallest_valid_input(self):
        """Line 13 boundary: empty string message with bubble_length = 0 + 2 = 2."""
        message = ""
        # Independently calculated expected string:
        # line 1: newline + 1 space + 2 underscores ("\n __")
        # line 2: "(  )    "
        # line 3: " ‾‾"
        expected = "\n __\n(  )    \n ‾‾"
        actual = snake.bubble(message)
        self.assertEqual(actual, expected)

    def test_ordinary_fixture_input(self):
        """Line 13 interior: ordinary message 'Hello, World!' of length 13 (border width = 15)."""
        message = "Hello, World!"
        # Independently calculated expected string:
        expected = "\n _______________\n( Hello, World! )    \n ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾"
        actual = snake.bubble(message)
        self.assertEqual(actual, expected)

    def test_single_character_input(self):
        """Boundary message of length 1 (border width = 3)."""
        message = "X"
        expected = "\n ___\n( X )    \n ‾‾‾"
        actual = snake.bubble(message)
        self.assertEqual(actual, expected)

    def test_original_logic_equivalence(self):
        """Verify refactored bubble matches the original unrefactored inline computation."""
        test_messages = ["", "a", "snake", "Longer test string with spaces and punctuation!"]
        for msg in test_messages:
            orig_len = len(msg) + 2
            orig_expected = f"""\n {"_" * orig_len}\n( {msg} )    \n {"‾" * orig_len}"""
            actual = snake.bubble(msg)
            self.assertEqual(actual, orig_expected)


if __name__ == "__main__":
    unittest.main()
