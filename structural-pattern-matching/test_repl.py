"""Unit and regression tests for structural-pattern-matching/repl.py.

Verifies the interactive Read-Eval-Print Loop (main) and syntax validator (valid).
Protects against regressions in boundary comparisons, accumulation conditions,
and return/loop-termination conditions.

Preconditions established by source:
    Line 5: PROMPT = "\\N{SNAKE} "
    Line 6: COMMANDS = ("help", "exit", "quit")
    Line 9: def main():
    Line 10: print('Type "help" for more information, "exit" or "quit" to finish.')
    Line 14: case command if command.lower() in COMMANDS:
    Line 18: case "exit" | "quit":
    Line 20: case expression if valid(expression, "eval"):
    Line 22: if _ is not None:
    Line 24: case statement if valid(statement, "exec"):
    Line 26: case _:
    Line 28: except KeyboardInterrupt:
    Line 30: except EOFError:
    Line 33: except Exception:
    Line 37: def valid(code, mode):
"""

import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "structural-pattern-matching"

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

# Suppress stdout during import
with contextlib.redirect_stdout(io.StringIO()):
    import repl


def run_repl(main_func, input_sequence, raise_on_eof=True):
    """Run repl.main under strictly controlled external state.

    Args:
        main_func: Callable main() to execute (original or mutated).
        input_sequence: Iterable of strings to supply to input(PROMPT).
        raise_on_eof: If True, raise EOFError when input_sequence is exhausted.

    Returns:
        dict containing:
            - 'return_value': return value of main_func
            - 'clean': bool, True if main returned normally without exception
            - 'exc': Exception instance or None if raised
            - 'stdout': captured string from sys.stdout
            - 'lines': list of stdout lines (splitlines())
            - 'consumed': list of strings consumed by input()
            - 'prompts': list of prompt strings passed to input()
    """
    inputs_consumed = []
    prompts_seen = []
    it = iter(input_sequence)

    def mock_input(prompt=""):
        prompts_seen.append(prompt)
        try:
            val = next(it)
            inputs_consumed.append(val)
            return val
        except StopIteration:
            if raise_on_eof:
                raise EOFError("EOF reached")
            return ""

    stdout_buf = io.StringIO()
    ret = None
    clean = False
    exc = None

    with (
        patch("builtins.input", side_effect=mock_input),
        patch("sys.stdout", stdout_buf),
    ):
        try:
            ret = main_func()
            clean = True
        except SystemExit as se:
            exc = se
        except Exception as e:
            exc = e

    captured = stdout_buf.getvalue()
    return {
        "return_value": ret,
        "clean": clean,
        "exc": exc,
        "stdout": captured,
        "lines": captured.splitlines(),
        "consumed": inputs_consumed,
        "prompts": prompts_seen,
    }


def assert_repl_terminates_on_quit(main_func):
    """Named regression assertion protecting Line 18 loop-exit condition.

    In the original implementation:
        Line 18: case "exit" | "quit": break
        Input ["quit"] triggers break and main() cleanly returns None.

    In the mutated implementation:
        Line 18: case "exit": break
        Input ["quit"] fails to match, loop continues to EOF, and raises SystemExit.
    """
    res = run_repl(main_func, ["quit"])
    assert res["clean"] is True, (
        f"Expected clean termination on 'quit', but REPL raised {res['exc']!r}"
    )
    assert res["return_value"] is None, (
        f"Expected return value None, got {res['return_value']!r}"
    )
    assert res["consumed"] == ["quit"], (
        f"Expected consumed inputs ['quit'], got {res['consumed']!r}"
    )
    expected_banner = (
        'Type "help" for more information, "exit" or "quit" to finish.'
    )
    assert res["lines"] == [expected_banner], (
        f"Unexpected stdout lines: {res['lines']!r}"
    )


def assert_repl_evaluates_falsy_expression(main_func):
    """Named regression assertion protecting Line 22 accumulation condition.

    In the original implementation:
        Line 22: if _ is not None: print(_)
        Input ["0", "exit"] evaluates 0, which is not None, printing '0'.

    In the mutated implementation:
        Line 22: if _: print(_)
        Input ["0", "exit"] evaluates bool(0) as False, suppressing output '0'.
    """
    res = run_repl(main_func, ["0", "exit"])
    assert res["clean"] is True, f"REPL failed to terminate: {res['exc']!r}"
    expected_lines = [
        'Type "help" for more information, "exit" or "quit" to finish.',
        "0",
    ]
    assert res["lines"] == expected_lines, (
        f"Falsy evaluation output mismatch: {res['lines']!r} !="
        f" {expected_lines!r}"
    )


def assert_repl_case_insensitive_exit(main_func):
    """Named regression assertion protecting Line 14 boundary comparison.

    In the original implementation:
        Line 14: case command if command.lower() in COMMANDS:
        Input ["EXIT"] is converted to lowercase and cleanly breaks.

    In the mutated implementation:
        Line 14: case command if command in COMMANDS:
        Input ["EXIT"] is not in COMMANDS, falls through to eval(), raising NameError.
    """
    res = run_repl(main_func, ["EXIT"])
    assert res["clean"] is True, (
        f"Expected clean termination on uppercase 'EXIT', but got:"
        f" {res['exc']!r}"
    )
    assert res["consumed"] == ["EXIT"], (
        f"Expected consumed inputs ['EXIT'], got {res['consumed']!r}"
    )
    expected_banner = (
        'Type "help" for more information, "exit" or "quit" to finish.'
    )
    assert res["lines"] == [expected_banner], (
        f"Unexpected stdout lines: {res['lines']!r}"
    )


class TestPreconditionsAndAnchors(unittest.TestCase):
    """Verify source lines and fixture preconditions."""

    def test_line5_prompt_anchor(self):
        """Line 5 establishes PROMPT = '\\N{SNAKE} '."""
        self.assertTrue(
            hasattr(repl, "PROMPT"), "repl module must define PROMPT"
        )
        self.assertEqual(repl.PROMPT, "\N{SNAKE} ")

    def test_line6_commands_anchor(self):
        """Line 6 establishes COMMANDS = ('help', 'exit', 'quit')."""
        self.assertTrue(
            hasattr(repl, "COMMANDS"), "repl module must define COMMANDS"
        )
        self.assertEqual(repl.COMMANDS, ("help", "exit", "quit"))

    def test_line37_valid_helper_eval_mode(self):
        """Line 37 establishes valid(code, mode='eval')."""
        self.assertTrue(repl.valid("1 + 1", "eval"))
        self.assertTrue(repl.valid("[x * 2 for x in (1, 2)]", "eval"))
        self.assertFalse(repl.valid("x = 10", "eval"))
        self.assertFalse(repl.valid("invalid @@ syntax", "eval"))

    def test_line37_valid_helper_exec_mode(self):
        """Line 37 establishes valid(code, mode='exec')."""
        self.assertTrue(repl.valid("x = 10", "exec"))
        self.assertTrue(repl.valid("def foo(): pass", "exec"))
        self.assertFalse(repl.valid("def :", "exec"))


class TestSmallestAndOrdinaryInputs(unittest.TestCase):
    """Verify smallest valid inputs and ordinary valid inputs for main()."""

    def test_smallest_valid_input_exit(self):
        """Smallest valid input sequence to terminate main() cleanly is ['exit']."""
        res = run_repl(repl.main, ["exit"])
        self.assertTrue(res["clean"])
        self.assertIsNone(res["return_value"])
        self.assertEqual(res["consumed"], ["exit"])
        self.assertEqual(
            res["lines"],
            ['Type "help" for more information, "exit" or "quit" to finish.'],
        )

    def test_smallest_valid_input_quit(self):
        """Smallest valid input sequence using alternative command ['quit']."""
        res = run_repl(repl.main, ["quit"])
        self.assertTrue(res["clean"])
        self.assertIsNone(res["return_value"])
        self.assertEqual(res["consumed"], ["quit"])
        self.assertEqual(
            res["lines"],
            ['Type "help" for more information, "exit" or "quit" to finish.'],
        )

    def test_ordinary_valid_input_help_exit(self):
        """Ordinary input sequence ['help', 'exit'] displays banner, version, and exits."""
        res = run_repl(repl.main, ["help", "exit"])
        self.assertTrue(res["clean"])
        self.assertIsNone(res["return_value"])
        self.assertEqual(res["consumed"], ["help", "exit"])
        self.assertEqual(len(res["lines"]), 2)
        self.assertEqual(
            res["lines"][0],
            'Type "help" for more information, "exit" or "quit" to finish.',
        )
        self.assertEqual(res["lines"][1], f"Python {sys.version}")

    def test_ordinary_valid_input_expression_exit(self):
        """Ordinary input sequence ['1 + 1', 'exit'] evaluates expression and prints 2."""
        res = run_repl(repl.main, ["1 + 1", "exit"])
        self.assertTrue(res["clean"])
        self.assertIsNone(res["return_value"])
        self.assertEqual(res["consumed"], ["1 + 1", "exit"])
        self.assertEqual(len(res["lines"]), 2)
        self.assertEqual(
            res["lines"][0],
            'Type "help" for more information, "exit" or "quit" to finish.',
        )
        self.assertEqual(res["lines"][1], "2")


class TestEvaluationAndExecutionBranches(unittest.TestCase):
    """Verify eval, exec, falsy values, None suppression, and error handling."""

    def test_eval_numeric_multiplication(self):
        """Arithmetic evaluation ['21 * 2', 'exit'] prints '42'."""
        res = run_repl(repl.main, ["21 * 2", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["lines"][1], "42")

    def test_eval_string_concatenation(self):
        """String evaluation prints evaluated string via print() (str representation)."""
        res = run_repl(repl.main, ["'hello ' + 'world'", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["lines"][1], "hello world")

    def test_eval_falsy_zero_is_printed(self):
        """Line 22 if _ is not None: ensures 0 is printed (not suppressed as falsy)."""
        res = run_repl(repl.main, ["0", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["lines"][1], "0")

    def test_eval_falsy_empty_string_is_printed(self):
        """Empty string literal evaluated is printed as empty line via print("")."""
        res = run_repl(repl.main, ["''", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["lines"][1], "")

    def test_eval_falsy_boolean_false_is_printed(self):
        """Literal False evaluated is printed as False."""
        res = run_repl(repl.main, ["False", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["lines"][1], "False")

    def test_eval_falsy_empty_list_is_printed(self):
        """Literal empty list evaluated is printed as []."""
        res = run_repl(repl.main, ["[]", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["lines"][1], "[]")

    def test_eval_none_is_suppressed(self):
        """Line 22 if _ is not None: suppresses printing when expression evaluates to None."""
        res = run_repl(repl.main, ["None", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(len(res["lines"]), 1)
        self.assertEqual(
            res["lines"][0],
            'Type "help" for more information, "exit" or "quit" to finish.',
        )

    def test_exec_statement_no_output(self):
        """Line 24 executes statement without producing stdout output."""
        res = run_repl(repl.main, ["y = 42", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(len(res["lines"]), 1)

    def test_invalid_syntax_fallback(self):
        """Line 26 fallback prints guidance on syntax error or unknown input."""
        res = run_repl(repl.main, ["invalid @@@ syntax", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(len(res["lines"]), 2)
        self.assertEqual(
            res["lines"][1], "Please type a command or valid Python"
        )

    def test_runtime_exception_traceback_reported(self):
        """Line 33 catches runtime exception and prints traceback to sys.stdout."""
        res = run_repl(repl.main, ["1 / 0", "exit"])
        self.assertTrue(res["clean"])
        self.assertIn("ZeroDivisionError: division by zero", res["stdout"])


class TestCommandMatchingAndCaseInsensitivity(unittest.TestCase):
    """Verify case-insensitivity on all COMMANDS members."""

    def test_exit_uppercase(self):
        """'EXIT' matches 'exit' case-insensitively."""
        res = run_repl(repl.main, ["EXIT"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["consumed"], ["EXIT"])

    def test_exit_mixedcase(self):
        """'Exit' matches 'exit' case-insensitively."""
        res = run_repl(repl.main, ["Exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["consumed"], ["Exit"])

    def test_quit_uppercase(self):
        """'QUIT' matches 'quit' case-insensitively."""
        res = run_repl(repl.main, ["QUIT"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["consumed"], ["QUIT"])

    def test_quit_mixedcase(self):
        """'Quit' matches 'quit' case-insensitively."""
        res = run_repl(repl.main, ["Quit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["consumed"], ["Quit"])

    def test_help_uppercase(self):
        """'HELP' matches 'help' case-insensitively."""
        res = run_repl(repl.main, ["HELP", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["lines"][1], f"Python {sys.version}")

    def test_help_mixedcase(self):
        """'Help' matches 'help' case-insensitively."""
        res = run_repl(repl.main, ["Help", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(res["lines"][1], f"Python {sys.version}")


class TestExceptionHandlingAndSignals(unittest.TestCase):
    """Verify KeyboardInterrupt and EOFError handling."""

    def test_keyboard_interrupt_recovery(self):
        """Line 28 catches KeyboardInterrupt, prints message, and continues loop."""
        it = iter(["exit"])

        def input_with_interrupt(prompt=""):
            if not hasattr(input_with_interrupt, "interrupted"):
                input_with_interrupt.interrupted = True
                raise KeyboardInterrupt()
            return next(it)

        stdout_buf = io.StringIO()
        with (
            patch("builtins.input", side_effect=input_with_interrupt),
            patch("sys.stdout", stdout_buf),
        ):
            ret = repl.main()

        self.assertIsNone(ret)
        captured = stdout_buf.getvalue()
        self.assertIn("KeyboardInterrupt", captured)

    def test_eof_error_exit(self):
        """Line 30 catches EOFError, prints newline, and exits via exit()."""

        def input_eof(prompt=""):
            raise EOFError()

        stdout_buf = io.StringIO()
        with (
            patch("builtins.input", side_effect=input_eof),
            patch("sys.stdout", stdout_buf),
        ):
            with self.assertRaises(SystemExit):
                repl.main()


class TestControlledStateAndPurity(unittest.TestCase):
    """Verify input-mutation behavior, output shape, and repeatability."""

    def test_input_mutation_preservation(self):
        """Caller input sequence list is not mutated by main()."""
        caller_inputs = ["help", "exit"]
        caller_copy = list(caller_inputs)
        res = run_repl(repl.main, caller_inputs)
        self.assertTrue(res["clean"])
        self.assertEqual(caller_inputs, caller_copy)

    def test_output_type_and_shape(self):
        """Documented output type is NoneType, output shape is list of formatted lines."""
        res = run_repl(repl.main, ["exit"])
        self.assertIsNone(res["return_value"])
        self.assertIsInstance(res["return_value"], type(None))
        self.assertEqual(len(res["lines"]), 1)

    def test_output_ordering(self):
        """Output lines strictly follow FIFO order of commands and evaluations."""
        res = run_repl(repl.main, ["1 + 1", "2 * 3", "exit"])
        self.assertTrue(res["clean"])
        self.assertEqual(
            res["lines"],
            [
                'Type "help" for more information, "exit" or "quit" to finish.',
                "2",
                "6",
            ],
        )

    def test_fresh_equivalent_inputs(self):
        """Equivalent fresh inputs produce identical outputs under controlled state."""
        res1 = run_repl(repl.main, ["help", "exit"])
        res2 = run_repl(repl.main, ["help", "exit"])
        self.assertEqual(res1["return_value"], res2["return_value"])
        self.assertEqual(res1["lines"], res2["lines"])
        self.assertEqual(res1["consumed"], res2["consumed"])


class TestRegressionDefectDetection(unittest.TestCase):
    """Verify that named regression assertions pass on the original implementation."""

    def test_regression_quit_breaks_loop(self):
        """assert_repl_terminates_on_quit passes on original repl.main."""
        assert_repl_terminates_on_quit(repl.main)

    def test_regression_falsy_evaluation_printed(self):
        """assert_repl_evaluates_falsy_expression passes on original repl.main."""
        assert_repl_evaluates_falsy_expression(repl.main)

    def test_regression_command_case_insensitivity(self):
        """assert_repl_case_insensitive_exit passes on original repl.main."""
        assert_repl_case_insensitive_exit(repl.main)


if __name__ == "__main__":
    unittest.main()
