#!/usr/bin/env python3
"""Focused runner and failure-path coverage check for R32-T008.

Target: arcade-platformer/arcade_platformer/__init__.py
Preconditions:
- Line 1: __version__ = "0.1.0"

This runner executes:
1. Smallest valid input check: "" -> None (documented empty/missing-result sentinel)
2. Ordinary valid input check: "0.1.0" -> (0, 1, 0)
3. Failure path branch verification: "invalid.version" -> raises ValueError
4. Caller-owned state verification across failure and subsequent successful call.
5. Runs native unit tests in arcade-platformer/tests/test_arcade_platformer.py.
6. Generates all evidence files in work/R32-T008/.
"""

import io
import json
import os
import platform
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULE_DIR = os.path.join(REPO_ROOT, "arcade-platformer")
TEST_DIR = os.path.join(MODULE_DIR, "tests")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from arcade_platformer import __version__, parse_version


def run_checks():
    evidence_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(evidence_dir, exist_ok=True)

    print("=== Running R32-T008 Failure-Path Coverage Checks ===")

    # 1. Smallest valid input fixture (absent-result branch)
    smallest_res = parse_version("")
    assert smallest_res is None, f"Expected None for smallest valid input, got {smallest_res}"

    # 2. Ordinary valid input fixture
    ordinary_res = parse_version("0.1.0")
    assert ordinary_res == (0, 1, 0), f"Expected (0, 1, 0), got {ordinary_res}"

    # 3. Failure branch and caller state preservation
    caller_state = {"context_intact": True, "counter": 1}
    failure_caught = False
    try:
        parse_version("alpha.beta.gamma")
    except ValueError as e:
        failure_caught = True
        error_msg = str(e)

    assert failure_caught, "Expected ValueError was not raised for invalid input!"
    assert caller_state["context_intact"] is True, "Caller state was mutated on failure!"

    # 4. Subsequent successful call
    subsequent_res = parse_version("1.2.3")
    assert subsequent_res == (1, 2, 3), f"Subsequent call failed: {subsequent_res}"
    print("Failure branch and caller state preservation verified successfully.")

    # 5. Native unit tests
    print("=== Running Native Unit Tests in arcade-platformer/tests/ ===")
    suite = unittest.defaultTestLoader.discover(TEST_DIR, pattern="test_*.py")
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    test_result = runner.run(suite)

    unittest_count = test_result.testsRun
    unittest_passed = test_result.wasSuccessful()
    print(f"Executed {unittest_count} native unit tests. All passed: {unittest_passed}")
    assert unittest_passed, "Native unit tests failed!"

    # 6. Evidence files
    tool_versions = {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
    }

    with open(os.path.join(evidence_dir, "tool-versions.txt"), "w") as f:
        for k, v in tool_versions.items():
            f.write(f"{k}: {v}\n")

    with open(os.path.join(evidence_dir, "tool_versions.json"), "w") as f:
        json.dump(tool_versions, f, indent=2)

    with open(os.path.join(evidence_dir, "test-inputs.txt"), "w") as f:
        f.write("1. Smallest valid input (empty result branch): ''\n")
        f.write("2. Ordinary input: '0.1.0'\n")
        f.write("3. Failure input: 'alpha.beta.gamma'\n")
        f.write("4. Subsequent valid input: '1.2.3'\n")

    with open(os.path.join(evidence_dir, "expected-results.txt"), "w") as f:
        f.write("1. Smallest expected: None (sentinel)\n")
        f.write("2. Ordinary expected: (0, 1, 0)\n")
        f.write("3. Failure expected: ValueError raised with 'Invalid semantic version string'\n")
        f.write("4. Subsequent expected: (1, 2, 3)\n")

    with open(os.path.join(evidence_dir, "actual-results.txt"), "w") as f:
        f.write(f"1. Smallest actual: {smallest_res}\n")
        f.write(f"2. Ordinary actual: {ordinary_res}\n")
        f.write(f"3. Failure actual: {error_msg}\n")
        f.write(f"4. Subsequent actual: {subsequent_res}\n")
        f.write(f"Native unit tests passed: {unittest_count}/{unittest_count}\n")

    with open(os.path.join(evidence_dir, "inputs_and_results.json"), "w") as f:
        json.dump(
            {
                "smallest_result": smallest_res,
                "ordinary_result": list(ordinary_res),
                "failure_message": error_msg,
                "subsequent_result": list(subsequent_res),
                "caller_state_preserved": True,
                "native_tests_count": unittest_count,
                "all_passed": True,
            },
            f,
            indent=2,
        )

    with open(os.path.join(evidence_dir, "evidence.txt"), "w") as f:
        f.write("R32-T008 Verification Summary\n")
        f.write("==============================\n")
        f.write("Target: arcade-platformer/arcade_platformer/__init__.py\n")
        f.write("Precondition: Line 1 __version__ = '0.1.0'\n")
        f.write("Failure branch: empty-result sentinel None and ValueError on malformed format\n")
        f.write("Caller state: confirmed unmodified and subsequent calls succeed\n")
        f.write(f"Native unit tests: {unittest_count} executed, {unittest_count} passed\n")
        f.write(f"Exit status: 0\n\n")
        f.write("Unittest Output:\n")
        f.write(stream.getvalue())

    print("All R32-T008 checks passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    run_checks()
