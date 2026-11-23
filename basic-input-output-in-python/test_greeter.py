"""Unit and regression tests for basic-input-output-in-python/greeter.py.

Preconditions cited:
- Line 1: `name = input("Please enter your name: ")` establishes prompt and stdin read.
- Line 2: `print("Hello", name, "and welcome!")` establishes stdout greeting with separation and newline.

Fixture:
- Smallest valid input: "" (empty string)
- Ordinary input: "Alice"
- Literal inputs and independently calculated expected outputs are verified against oracle.
"""

import io
import unittest
from unittest.mock import patch

from greeter import greet, run_greeter


class TestGreeter(unittest.TestCase):
    """Test suite comparing greeter against independent oracle and verifying I/O behavior."""

    def test_precondition_line1_smallest_valid_input(self):
        """Smallest valid input: empty string '' (Precondition cited: line 1 & line 2)."""
        literal_input = ""
        expected_output = "Hello  and welcome!"
        self.assertEqual(greet(literal_input), expected_output)

    def test_precondition_line2_ordinary_input(self):
        """Ordinary input: 'Alice' (Precondition cited: line 1 & line 2)."""
        literal_input = "Alice"
        expected_output = "Hello Alice and welcome!"
        self.assertEqual(greet(literal_input), expected_output)

    def test_run_greeter_io_smallest_input(self):
        """Verify run_greeter with smallest valid input '' through mocked streams."""
        stdin_mock = io.StringIO("\n")
        stdout_mock = io.StringIO()
        res = run_greeter(input_stream=stdin_mock, output_stream=stdout_mock, prompt=True)
        self.assertEqual(res, "")
        self.assertEqual(stdout_mock.getvalue(), "Please enter your name: Hello  and welcome!\n")

    def test_run_greeter_io_ordinary_input(self):
        """Verify run_greeter with ordinary input 'Alice' through mocked streams."""
        stdin_mock = io.StringIO("Alice\n")
        stdout_mock = io.StringIO()
        res = run_greeter(input_stream=stdin_mock, output_stream=stdout_mock, prompt=True)
        self.assertEqual(res, "Alice")
        self.assertEqual(stdout_mock.getvalue(), "Please enter your name: Hello Alice and welcome!\n")

    def test_mocked_sys_io_legacy_execution(self):
        """Verify run_greeter with sys.stdin and sys.stdout mocked."""
        with patch("sys.stdin", io.StringIO("Bob\n")), patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            res = run_greeter(prompt=False)
            self.assertEqual(res, "Bob")
            self.assertEqual(mock_out.getvalue(), "Hello Bob and welcome!\n")


if __name__ == "__main__":
    unittest.main()
