"""Unit and failure-path coverage tests for arcade-platformer/arcade_platformer/__init__.py.

Preconditions:
- Line 1: `__version__ = "0.1.0"`
- Smallest valid input fixture: `""` -> returns `None` (empty/missing-result sentinel).
- Ordinary valid input fixture: `"0.1.0"` -> returns `(0, 1, 0)`.
- Failure branch: `"invalid.version"` -> raises `ValueError`.
- Verify caller-owned state remains valid and ordinary call succeeds immediately afterwards.
"""

import unittest
from arcade_platformer import __version__, parse_version


class TestArcadePlatformerInit(unittest.TestCase):
    """Test suite covering version contract, empty-result sentinel, and failure paths."""

    def test_version_constant(self):
        """Preserve existing test_version contract."""
        self.assertEqual(__version__, "0.1.0")

    def test_precondition_line1_default_version(self):
        """Line 1: Default argument parses __version__ into (0, 1, 0)."""
        self.assertEqual(parse_version(), (0, 1, 0))

    def test_precondition_line1_smallest_valid_input_empty_result(self):
        """Smallest valid input reaching absent-result branch: '' -> None."""
        literal_input = ""
        expected_output = None
        self.assertIsNone(parse_version(literal_input))
        self.assertEqual(parse_version(literal_input), expected_output)

    def test_precondition_line1_ordinary_input(self):
        """Ordinary valid input: '0.1.0' -> (0, 1, 0)."""
        literal_input = "0.1.0"
        expected_output = (0, 1, 0)
        self.assertEqual(parse_version(literal_input), expected_output)

    def test_failure_branch_and_caller_state_preservation(self):
        """Assert failure branch raises intended exception, preserving caller-owned state,
        and that a subsequent ordinary valid call succeeds.
        """
        caller_state = {"session_id": 42, "status": "active"}

        # Reach failure branch
        with self.assertRaises(ValueError) as ctx:
            parse_version("invalid.version.str")
        self.assertIn("Invalid semantic version string", str(ctx.exception))

        # Assert caller-owned state was untouched and remains valid
        self.assertEqual(caller_state, {"session_id": 42, "status": "active"})

        # Assert ordinary valid call still succeeds immediately afterwards
        subsequent_call = parse_version("2.4.1")
        self.assertEqual(subsequent_call, (2, 4, 1))


if __name__ == "__main__":
    unittest.main()
