"""Unit tests and worked example assertions for github-copilot/copilot_example.py.

Asserts intermediate state transitions, final code generation, AST syntax validity,
and preconditions from README.md.
"""

import ast
import doctest
import importlib.util
import os
import sys
import unittest

MODULE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "copilot_example.py"
)
spec = importlib.util.spec_from_file_location("copilot_example", MODULE_PATH)
copilot_example = importlib.util.module_from_spec(spec)
sys.modules["copilot_example"] = copilot_example
spec.loader.exec_module(copilot_example)

copilot_complete = copilot_example.copilot_complete


class TestCopilotWorkedExample(unittest.TestCase):
    """Test suite asserting worked example state transitions."""

    def test_doctest(self):
        """Run doctests embedded in copilot_complete."""
        results = doctest.testmod(copilot_example)
        self.assertEqual(results.failed, 0)

    def test_smallest_valid_input(self):
        """Verify smallest valid input (# do nothing) yields 'pass'."""
        prompt = "# do nothing"
        res = copilot_complete(prompt)

        # Assert intermediate states
        self.assertEqual(res["step1_input"], prompt)
        self.assertEqual(res["step2_intent"], "pass")
        self.assertEqual(res["step3_body_lines"], ["pass"])
        self.assertTrue(res["step4_syntax_valid"])

        # Assert final result
        self.assertEqual(res["completed_code"], "pass")
        self.assertEqual(res["status"], "SUCCESS")

    def test_ordinary_valid_input_even(self):
        """Verify ordinary valid input (# check even) asserts intermediate and final state."""
        prompt = "# Check even\ndef is_even(n):"
        res = copilot_complete(prompt)

        # Assert intermediate states
        self.assertEqual(res["step2_intent"], "even")
        self.assertEqual(res["step3_body_lines"], ["return n % 2 == 0"])
        self.assertTrue(res["step4_syntax_valid"])

        # Assert final output
        expected = "def is_even(n):\n    return n % 2 == 0"
        self.assertEqual(res["completed_code"], expected)

    def test_ordinary_valid_input_fibonacci(self):
        """Verify ordinary valid input for fibonacci generation."""
        prompt = "# Recursive fibonacci\ndef fib(n):"
        res = copilot_complete(prompt)

        self.assertEqual(res["step2_intent"], "fibonacci")
        self.assertTrue(res["step4_syntax_valid"])
        self.assertIn("return fib(n - 1) + fib(n - 2)", res["completed_code"])

    def test_purity_and_repeatability(self):
        """Verify identical prompts produce identical state transitions over repeated calls."""
        prompt = "# Reverse\ndef rev(s):"
        for _ in range(10):
            res = copilot_complete(prompt)
            self.assertEqual(res["step2_intent"], "reverse")
            self.assertEqual(res["completed_code"], "def rev(s):\n    return s[::-1]")

    def test_type_error_handling(self):
        """Verify non-string prompt raises TypeError."""
        with self.assertRaises(TypeError):
            copilot_complete(12345)
        with self.assertRaises(TypeError):
            copilot_complete(None)


if __name__ == "__main__":
    unittest.main()
