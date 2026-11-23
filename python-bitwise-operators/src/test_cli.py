"""Unit and repeatable deterministic tests for CommandLineArguments in stegano/cli.py.

Preconditions:
- Line 12: CommandLineArguments dataclass in python-bitwise-operators/src/stegano/cli.py
- Smallest valid input fixture: ['image.bmp', '--decode'] -> CommandLineArguments(Path('image.bmp'), None, True, False)
- Ordinary input fixture: ['carrier.bmp', '--encode', 'secret.txt'] -> CommandLineArguments(Path('carrier.bmp'), Path('secret.txt'), False, False)
- Verifies repeatable calls, input isolation, and no reliance on live network/user/GUI.
"""

import pathlib
import sys
import unittest
from unittest.mock import patch

from stegano.cli import CommandLineArguments, parse_args


class TestCommandLineArguments(unittest.TestCase):
    """Test suite for CommandLineArguments deterministic repeatability and input isolation."""

    def setUp(self):
        # Deterministic dummy path factory that creates Path without requiring filesystem side-effects
        self.mock_validator = lambda s: pathlib.Path(s)

    def test_precondition_line12_smallest_valid_input(self):
        """Line 12: Smallest valid input fixture: Decode flag with a single bitmap path."""
        literal_inputs = ["image.bmp", "--decode"]
        expected_output = CommandLineArguments(
            bitmap=pathlib.Path("image.bmp"),
            encode=None,
            decode=True,
            erase=False,
        )
        actual = parse_args(args=literal_inputs, path_validator=self.mock_validator)
        self.assertEqual(actual, expected_output)

    def test_precondition_line12_ordinary_input(self):
        """Line 12: Ordinary input fixture: Encode flag with carrier and payload file."""
        literal_inputs = ["carrier.bmp", "--encode", "secret.txt"]
        expected_output = CommandLineArguments(
            bitmap=pathlib.Path("carrier.bmp"),
            encode=pathlib.Path("secret.txt"),
            decode=False,
            erase=False,
        )
        actual = parse_args(args=literal_inputs, path_validator=self.mock_validator)
        self.assertEqual(actual, expected_output)

    def test_repeatability_and_state_isolation(self):
        """Step 3: Run the same fixture twice in fresh isolated state and once after another valid input.
        Assert that earlier runs cannot alter later results.
        """
        smallest_inputs = ["image.bmp", "--decode"]
        ordinary_inputs = ["carrier.bmp", "-e", "secret.txt"]
        erase_inputs = ["target.bmp", "--erase"]

        # Run 1: Fresh isolated state
        run1 = parse_args(args=list(smallest_inputs), path_validator=self.mock_validator)

        # Intervening run with different input
        intervening = parse_args(args=list(ordinary_inputs), path_validator=self.mock_validator)
        self.assertEqual(intervening.bitmap, pathlib.Path("carrier.bmp"))
        self.assertEqual(intervening.encode, pathlib.Path("secret.txt"))

        # Run 2: Same fixture run after intervening input
        run2 = parse_args(args=list(smallest_inputs), path_validator=self.mock_validator)

        # Another intervening run
        intervening2 = parse_args(args=list(erase_inputs), path_validator=self.mock_validator)
        self.assertTrue(intervening2.erase)

        # Run 3: Same fixture run again
        run3 = parse_args(args=list(smallest_inputs), path_validator=self.mock_validator)

        # Assert identical results across all runs
        self.assertEqual(run1, run2)
        self.assertEqual(run2, run3)
        self.assertEqual(run1.bitmap, pathlib.Path("image.bmp"))
        self.assertIsNone(run1.encode)
        self.assertTrue(run1.decode)
        self.assertFalse(run1.erase)

    def test_sys_argv_fallback_preserves_callers(self):
        """Verify default parameters preserve callers reading sys.argv."""
        with patch.object(sys, "argv", ["stegano", "test.bmp", "-x"]):
            res = parse_args(path_validator=self.mock_validator)
            self.assertEqual(res.bitmap, pathlib.Path("test.bmp"))
            self.assertTrue(res.erase)
            self.assertFalse(res.decode)
            self.assertIsNone(res.encode)

    def test_error_when_no_mode_specified(self):
        """Verify argument parsing error when mode is missing."""
        with self.assertRaises(SystemExit):
            with patch("sys.stderr"):
                parse_args(args=["test.bmp"], path_validator=self.mock_validator)


if __name__ == "__main__":
    unittest.main()
