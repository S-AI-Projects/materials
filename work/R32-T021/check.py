#!/usr/bin/env python3
"""Verification check runner for Task R32-T021.

Locks down the contract of `parse_input` in opencode/dice_improved.py.
Verifies preconditions, smallest valid input, ordinary inputs, domain boundaries,
repeated-value purity, and native unit test execution.
"""

import inspect
import io
import os
import platform
import sys
import unittest

# Ensure materials repository is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import opencode.dice_improved as dice_module
from opencode.dice_improved import MAX_DICE, MIN_DICE, parse_input
from opencode.test_dice_improved import TestParseInputContract

WORK_DIR = os.path.dirname(os.path.abspath(__file__))


def write_evidence_files(test_cases, test_results, unit_test_output):
    """Write standard task verification artifacts into work/R32-T021/."""
    os.makedirs(WORK_DIR, exist_ok=True)

    # 1. tool-versions.txt
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Interpreter: {sys.executable}\n")

    # 2. test-inputs.txt
    with open(os.path.join(WORK_DIR, "test-inputs.txt"), "w") as f:
        f.write("# Precondition Anchors:\n")
        f.write("MIN_DICE = 1 (Line 20)\n")
        f.write("MAX_DICE = 6 (Line 21)\n")
        f.write("roll_results = [] (Line 97)\n")
        f.write("dice_faces = [] (Line 157)\n\n")
        f.write("# Literal Inputs for parse_input:\n")
        for inp, exp, desc in test_cases:
            f.write(f"Input: {repr(inp)} | Description: {desc}\n")

    # 3. expected-results.txt
    with open(os.path.join(WORK_DIR, "expected-results.txt"), "w") as f:
        f.write("# Expected Results (Independently Calculated):\n")
        for inp, exp, desc in test_cases:
            exp_str = exp if isinstance(exp, str) else str(exp)
            f.write(f"Input: {repr(inp)} => Expected: {exp_str} ({desc})\n")

    # 4. actual-results.txt
    with open(os.path.join(WORK_DIR, "actual-results.txt"), "w") as f:
        f.write("# Actual Execution Results:\n")
        for inp, act, status, desc in test_results:
            f.write(f"Input: {repr(inp)} => Actual: {act} | Status: {status} ({desc})\n")

    # 5. evidence.txt
    with open(os.path.join(WORK_DIR, "evidence.txt"), "w") as f:
        f.write("=== Task R32-T021 Verification Evidence ===\n")
        f.write("Target: opencode/dice_improved.py (parse_input)\n")
        f.write(f"Preconditions Verified: MIN_DICE={MIN_DICE}, MAX_DICE={MAX_DICE}\n")
        f.write(f"Explicit Test Cases Passed: {len(test_results)}/{len(test_cases)}\n\n")
        f.write("=== Native Unit Test Output ===\n")
        f.write(unit_test_output)
        f.write("\nVerification Result: SUCCESS (Exit Code 0)\n")


def main():
    print("Running Task R32-T021 verification check...")

    # 1. Precondition and Anchor checks
    assert MIN_DICE == 1, "Precondition failed: MIN_DICE != 1"
    assert MAX_DICE == 6, "Precondition failed: MAX_DICE != 6"

    src = inspect.getsource(dice_module)
    assert "roll_results = []" in src, "Precondition anchor 'roll_results = []' missing"
    assert "dice_faces = []" in src, "Precondition anchor 'dice_faces = []' missing"

    # 2. Independent Oracle Test Matrix
    test_cases = [
        ("1", 1, "Smallest valid input"),
        (" 1 ", 1, "Smallest valid input with whitespace"),
        ("\t1\n", 1, "Smallest valid input with tabs and newlines"),
        ("2", 2, "Ordinary valid input (2)"),
        ("3", 3, "Ordinary valid input (3)"),
        ("4", 4, "Ordinary valid input (4)"),
        ("5", 5, "Ordinary valid input (5)"),
        ("6", 6, "Upper domain boundary (6)"),
        (" 6 ", 6, "Upper domain boundary with whitespace"),
        ("0", "ValueError: Please enter a number from 1 to 6.", "Below lower boundary"),
        ("-1", "ValueError: Please enter a number from 1 to 6.", "Negative boundary"),
        ("7", "ValueError: Please enter a number from 1 to 6.", "Above upper boundary"),
        ("100", "ValueError: Please enter a number from 1 to 6.", "Large out of bounds"),
        ("abc", "ValueError: Please enter a number from 1 to 6.", "Non-numeric string"),
        ("", "ValueError: Please enter a number from 1 to 6.", "Empty string"),
        ("   ", "ValueError: Please enter a number from 1 to 6.", "Whitespace-only string"),
        ("3.5", "ValueError: Please enter a number from 1 to 6.", "Float string"),
    ]

    test_results = []
    for inp, exp, desc in test_cases:
        try:
            res = parse_input(inp)
            act_repr = str(res)
            if res == exp:
                status = "PASS"
            else:
                status = f"FAIL (Expected {exp}, Got {res})"
                print(f"FAILED assertion on {desc}: {status}")
                sys.exit(1)
        except ValueError as e:
            act_repr = f"ValueError: {e}"
            if act_repr == exp:
                status = "PASS"
            else:
                status = f"FAIL (Expected {exp}, Got {act_repr})"
                print(f"FAILED assertion on {desc}: {status}")
                sys.exit(1)
        except Exception as e:
            act_repr = f"Unexpected Exception: {e}"
            status = "FAIL"
            print(f"UNEXPECTED ERROR on {desc}: {act_repr}")
            sys.exit(1)

        test_results.append((inp, act_repr, status, desc))

    # 3. Repeated-value idempotency & non-mutation test
    for _ in range(20):
        assert parse_input("1") == 1
        assert parse_input("3") == 3
        assert parse_input("6") == 6

    # 4. Run native unit test suite
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestParseInputContract)
    test_result = runner.run(suite)
    unit_test_output = stream.getvalue()

    if not test_result.wasSuccessful():
        print("Native unit test suite failed!")
        print(unit_test_output)
        sys.exit(1)

    print(f"All {len(test_cases)} oracle test cases passed.")
    print(f"Ran {test_result.testsRun} native unit tests: OK.")

    # 5. Generate evidence files
    write_evidence_files(test_cases, test_results, unit_test_output)
    print(f"Verification evidence written to {WORK_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
