#!/usr/bin/env python3
"""Verification check runner for Task R32-T041.

Locks down the contract of `split_list` in python-list/chunks.py.
Verifies preconditions, smallest valid input, ordinary inputs, domain boundaries,
repeated-value purity, and native unit test execution.
"""

import inspect
import io
import os
import platform
import sys
import unittest

# Ensure materials repository and target package are on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_DIR = os.path.join(REPO_ROOT, "python-list")
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

import chunks
from test_chunks import TestSplitListContract

WORK_DIR = os.path.dirname(os.path.abspath(__file__))


def get_precondition_anchor():
    """Locate the source line establishing the precondition anchor 'chunks = []'."""
    source_file = os.path.join(TARGET_DIR, "chunks.py")
    with open(source_file, "r") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, start=1):
        if "chunks = []" in line and not line.strip().startswith("#"):
            return idx, line.strip()
    raise AssertionError("Precondition anchor 'chunks = []' not found in chunks.py")


def write_evidence_files(anchor_info, test_cases, test_results, unit_test_output, tests_run):
    """Write standard task verification artifacts into work/R32-T041/."""
    os.makedirs(WORK_DIR, exist_ok=True)
    anchor_line, anchor_text = anchor_info

    # 1. tool-versions.txt
    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Interpreter: {sys.executable}\n")

    # 2. test-inputs.txt
    with open(os.path.join(WORK_DIR, "test-inputs.txt"), "w") as f:
        f.write("# Precondition Anchors:\n")
        f.write(f"{anchor_text} (Line {anchor_line} of python-list/chunks.py)\n\n")
        f.write("# Literal Inputs for split_list(list_object, chunk_size):\n")
        for inp, exp, desc in test_cases:
            f.write(f"Input: list_object={repr(inp[0])}, chunk_size={inp[1]} | Description: {desc}\n")

    # 3. expected-results.txt
    with open(os.path.join(WORK_DIR, "expected-results.txt"), "w") as f:
        f.write("# Expected Results (Independently Calculated):\n")
        for inp, exp, desc in test_cases:
            f.write(f"Input: list_object={repr(inp[0])}, chunk_size={inp[1]} => Expected: {repr(exp)} ({desc})\n")

    # 4. actual-results.txt
    with open(os.path.join(WORK_DIR, "actual-results.txt"), "w") as f:
        f.write("# Actual Execution Results:\n")
        for inp, act, status, desc in test_results:
            f.write(f"Input: list_object={repr(inp[0])}, chunk_size={inp[1]} => Actual: {repr(act)} | Status: {status} ({desc})\n")

    # 5. evidence.txt
    with open(os.path.join(WORK_DIR, "evidence.txt"), "w") as f:
        f.write("=== Task R32-T041 Verification Evidence ===\n")
        f.write("Target: python-list/chunks.py (split_list)\n")
        f.write(f"Precondition Anchor Verified: '{anchor_text}' at Line {anchor_line}\n")
        f.write(f"Explicit Oracle Test Cases Passed: {len(test_results)}/{len(test_cases)}\n")
        f.write(f"Native Unit Tests Executed: {tests_run} (All Passed)\n\n")
        f.write("=== Native Unit Test Output ===\n")
        f.write(unit_test_output)
        f.write("\nVerification Result: SUCCESS (Exit Code 0)\n")


def main():
    print("Running Task R32-T041 verification check...")

    # 1. Precondition and Anchor check
    anchor_info = get_precondition_anchor()
    anchor_line, anchor_text = anchor_info
    print(f"Verified precondition anchor: '{anchor_text}' at Line {anchor_line}")

    # 2. Independent Oracle Test Matrix
    test_cases = [
        (([], 1), [], "Smallest valid input (empty list)"),
        (([1], 1), [[1]], "Smallest non-empty list (single element)"),
        (([10, 20, 30, 40], 2), [[10, 20], [30, 40]], "Ordinary input (even division)"),
        (([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]], "Ordinary input (uneven division)"),
        ((["alpha", "beta", "gamma", "delta", "epsilon"], 3), [["alpha", "beta", "gamma"], ["delta", "epsilon"]], "Ordinary input with strings"),
        (([1, 2, 3], 3), [[1, 2, 3]], "Domain boundary (chunk_size == len)"),
        (([1, 2, 3], 10), [[1, 2, 3]], "Domain boundary (chunk_size > len)"),
        (([7, 7, 7, 7], 2), [[7, 7], [7, 7]], "Domain boundary (repeated integer values)"),
        ((["a", "a", "b", "b", "a"], 2), [["a", "a"], ["b", "b"], ["a"]], "Domain boundary (repeated string values)"),
        (([42], 5), [[42]], "Single element with larger chunk size"),
    ]

    test_results = []
    for inp, exp, desc in test_cases:
        list_obj, chunk_sz = inp
        # Pass a fresh copy to prevent cross-contamination
        act = chunks.split_list(list(list_obj), chunk_sz)
        if act == exp:
            status = "PASS"
        else:
            status = f"FAIL (Expected {exp}, Got {act})"
            print(f"FAILED assertion on {desc}: {status}")
            sys.exit(1)
        test_results.append((inp, act, status, desc))

    # 3. Repeated-value idempotency & non-mutation test
    original = [1, 2, 3, 4, 5]
    for _ in range(25):
        res = chunks.split_list(original, 2)
        assert res == [[1, 2], [3, 4], [5]], "Idempotency check failed"
        assert original == [1, 2, 3, 4, 5], "Input mutation detected"

    # 4. Run native unit test suite
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSplitListContract)
    test_result = runner.run(suite)
    unit_test_output = stream.getvalue()

    if not test_result.wasSuccessful():
        print("Native unit test suite failed!")
        print(unit_test_output)
        sys.exit(1)

    print(f"All {len(test_cases)} oracle test cases passed.")
    print(f"Ran {test_result.testsRun} native unit tests: OK.")

    # 5. Generate evidence files
    write_evidence_files(anchor_info, test_cases, test_results, unit_test_output, test_result.testsRun)
    print(f"Verification evidence written to {WORK_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
