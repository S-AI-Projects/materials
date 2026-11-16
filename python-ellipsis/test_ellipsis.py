"""Unit and regression tests for python-ellipsis/ellipsis_example.py.

Preconditions established by source:
    Line 1: def do_nothing(): ... - Function definition using Ellipsis literal.
    Line 4: do_nothing() - Execution fixture with zero arguments.
"""

import contextlib
import dis
import doctest
import io
from pathlib import Path
import subprocess
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "python-ellipsis"

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

# Mock stdout during import to prevent polluting test discovery
with contextlib.redirect_stdout(io.StringIO()):
    import ellipsis_example


class TestPreconditionsAndAnchors(unittest.TestCase):
    """Verify source lines and fixture preconditions."""

    def test_line1_do_nothing_callable(self):
        """Line 1 establishes do_nothing function definition."""
        self.assertTrue(
            hasattr(ellipsis_example, "do_nothing"),
            "ellipsis_example module must define do_nothing",
        )
        self.assertTrue(
            callable(ellipsis_example.do_nothing),
            "do_nothing must be callable",
        )

    def test_line4_zero_arg_invocation(self):
        """Line 4 establishes zero-argument invocation fixture do_nothing()."""
        result = ellipsis_example.do_nothing()
        self.assertIsNone(
            result, "Line 4 do_nothing() execution must return None"
        )


class TestSmallestAndOrdinaryInputs(unittest.TestCase):
    """Verify smallest valid input and ordinary inputs."""

    def test_smallest_valid_input_zero_args(self):
        """Smallest valid input is calling do_nothing() with zero arguments."""
        result = ellipsis_example.do_nothing()
        self.assertIsNone(result)

    def test_ordinary_input_single_integer(self):
        """Ordinary input: single integer argument."""
        literal_input = 42
        result = ellipsis_example.do_nothing(literal_input)
        self.assertIsNone(result)

    def test_ordinary_input_string(self):
        """Ordinary input: string argument."""
        literal_input = "test_string_payload"
        result = ellipsis_example.do_nothing(literal_input)
        self.assertIsNone(result)

    def test_multiple_positional_args(self):
        """Multiple positional arguments."""
        result = ellipsis_example.do_nothing(1, 2, 3, "alpha", [10, 20])
        self.assertIsNone(result)

    def test_keyword_arguments(self):
        """Keyword arguments."""
        result = ellipsis_example.do_nothing(key="value", mode=True, count=100)
        self.assertIsNone(result)

    def test_mixed_positional_and_keyword_args(self):
        """Mixed positional and keyword arguments."""
        result = ellipsis_example.do_nothing(
            1, 2, item="test", meta={"active": True}
        )
        self.assertIsNone(result)


class TestStatePreservationAndImmutability(unittest.TestCase):
    """Verify caller-owned state is preserved and unmutated."""

    def test_caller_state_unmutated_list(self):
        """Caller list passed as argument remains strictly unmutated."""
        caller_list = [1, 2, 3, {"nested": 4}]
        caller_copy = [1, 2, 3, {"nested": 4}]
        ellipsis_example.do_nothing(caller_list)
        self.assertEqual(
            caller_list,
            caller_copy,
            "Caller list must not be mutated by do_nothing",
        )

    def test_caller_state_unmutated_dict(self):
        """Caller dictionary passed as argument remains strictly unmutated."""
        caller_dict = {"a": 1, "b": [10, 20]}
        caller_copy = {"a": 1, "b": [10, 20]}
        ellipsis_example.do_nothing(caller_dict)
        self.assertEqual(
            caller_dict,
            caller_copy,
            "Caller dict must not be mutated by do_nothing",
        )

    def test_caller_state_unmutated_set(self):
        """Caller set passed as argument remains strictly unmutated."""
        caller_set = {10, 20, 30}
        caller_copy = {10, 20, 30}
        ellipsis_example.do_nothing(caller_set)
        self.assertEqual(
            caller_set,
            caller_copy,
            "Caller set must not be mutated by do_nothing",
        )


class TestBytecodeAndComplexityInvariants(unittest.TestCase):
    """Verify bytecode structure, operation count, and purity."""

    def test_bytecode_instruction_count(self):
        """Disassembled bytecode contains exactly 3 instructions confirming O(1) operations."""
        instructions = list(dis.get_instructions(ellipsis_example.do_nothing))
        opnames = [inst.opname for inst in instructions]
        self.assertEqual(
            len(instructions),
            3,
            f"Expected exactly 3 bytecode instructions, got {len(instructions)}: {opnames}",
        )
        self.assertIn("RETURN_VALUE", opnames)

    def test_purity_and_idempotency(self):
        """Repeated invocations consistently return None without state accumulation."""
        for _ in range(100):
            res = ellipsis_example.do_nothing()
            self.assertIsNone(res)


class TestScriptExecutionAndDoctests(unittest.TestCase):
    """Verify standalone script execution and doctests."""

    def test_standalone_script_execution(self):
        """Standalone script execution completes with returncode 0."""
        proc = subprocess.run(
            [sys.executable, str(MODULE_DIR / "ellipsis_example.py")],
            cwd=str(MODULE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"Script execution failed with returncode {proc.returncode}: {proc.stderr}",
        )
        self.assertEqual(proc.stdout, "")

    def test_doctests_pass(self):
        """Doctests in ellipsis_example module pass cleanly."""
        dt_res = doctest.testmod(ellipsis_example)
        self.assertEqual(
            dt_res.failed,
            0,
            f"Doctests failed: {dt_res.failed}/{dt_res.attempted}",
        )
        self.assertGreaterEqual(dt_res.attempted, 3)


if __name__ == "__main__":
    unittest.main()
