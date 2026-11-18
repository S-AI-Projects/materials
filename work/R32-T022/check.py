#!/usr/bin/env python3
"""Verification check runner for Task R32-T022.

Defines and tests the supported boundaries of altair python (steps.py).
Evaluates boundary inputs, runs native unit tests, and generates evidence files.
"""

import importlib.util
import io
import os
import platform
import sys
import unittest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))

# Load steps.py
STEPS_PATH = os.path.join(REPO_ROOT, "altair-python", "steps.py")
spec = importlib.util.spec_from_file_location("steps", STEPS_PATH)
steps_module = importlib.util.module_from_spec(spec)
sys.modules["steps"] = steps_module
spec.loader.exec_module(steps_module)

# Load test_steps.py
TEST_STEPS_PATH = os.path.join(REPO_ROOT, "altair-python", "test_steps.py")
test_spec = importlib.util.spec_from_file_location("test_steps", TEST_STEPS_PATH)
test_module = importlib.util.module_from_spec(test_spec)
test_spec.loader.exec_module(test_module)

DEFAULT_STEPS_DATA = steps_module.DEFAULT_STEPS_DATA
validate_steps_data = steps_module.validate_steps_data
create_weekly_steps_chart = steps_module.create_weekly_steps_chart


def write_evidence(test_cases, test_results, unit_test_output):
    """Write verification evidence into work/R32-T022/."""
    os.makedirs(WORK_DIR, exist_ok=True)

    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Interpreter: {sys.executable}\n")

    with open(os.path.join(WORK_DIR, "test-inputs.txt"), "w") as f:
        f.write("# Precondition Anchors:\n")
        f.write("Line 21: DEFAULT_STEPS_DATA fixture definition\n")
        f.write("Line 22: Day column labels ('1-Mon' through '7-Sun')\n")
        f.write("Line 23: Steps integer counts (6200 through 3769)\n\n")
        f.write("# Boundary Test Matrix Inputs:\n")
        for inp, exp, desc in test_cases:
            f.write(f"Input: {repr(inp)} | Description: {desc}\n")

    with open(os.path.join(WORK_DIR, "expected-results.txt"), "w") as f:
        f.write("# Expected Results (Boundary Contract):\n")
        for inp, exp, desc in test_cases:
            f.write(f"Input: {repr(inp)} => Expected: {exp} ({desc})\n")

    with open(os.path.join(WORK_DIR, "actual-results.txt"), "w") as f:
        f.write("# Actual Results:\n")
        for inp, act, status, desc in test_results:
            f.write(f"Input: {repr(inp)} => Actual: {act} | Status: {status} ({desc})\n")

    with open(os.path.join(WORK_DIR, "evidence.txt"), "w") as f:
        f.write("=== Task R32-T022 Verification Evidence ===\n")
        f.write("Target: altair-python/steps.py (Boundary Contract)\n")
        f.write(f"Boundary Cases Checked: {len(test_results)}/{len(test_cases)}\n\n")
        f.write("=== Native Unit Test Output ===\n")
        f.write(unit_test_output)
        f.write("\nVerification Result: SUCCESS (Exit Code 0)\n")


def main():
    print("Running Task R32-T022 verification check...")

    # 1. Verify precondition anchors
    assert "Day" in DEFAULT_STEPS_DATA, "Missing 'Day' in DEFAULT_STEPS_DATA anchor"
    assert "Steps" in DEFAULT_STEPS_DATA, "Missing 'Steps' in DEFAULT_STEPS_DATA anchor"
    assert len(DEFAULT_STEPS_DATA["Day"]) == 7, "Anchor length != 7"

    # 2. Boundary Test Matrix
    test_cases = [
        (
            {"Day": ["1-Mon"], "Steps": [1000]},
            "Valid",
            "Smallest valid input (1 row)",
        ),
        (
            DEFAULT_STEPS_DATA,
            "Valid",
            "Ordinary valid input (7 rows)",
        ),
        (
            {"Day": [], "Steps": []},
            "Valid",
            "Valid boundary (empty dataset, 0 rows)",
        ),
        (
            None,
            "ValueError: Data cannot be None",
            "Unsupported: None data",
        ),
        (
            {"Day": ["1-Mon"]},
            "ValueError: Data must contain both 'Day' and 'Steps' fields",
            "Unsupported: Missing Steps column",
        ),
        (
            {"Steps": [5000]},
            "ValueError: Data must contain both 'Day' and 'Steps' fields",
            "Unsupported: Missing Day column",
        ),
        (
            12345,
            "ValueError: Unsupported data type: <class 'int'>",
            "Unsupported: Integer data type",
        ),
    ]

    test_results = []
    for inp, exp, desc in test_cases:
        try:
            res = validate_steps_data(inp)
            act_repr = "Valid"
            if act_repr == exp:
                status = "PASS"
            else:
                status = f"FAIL (Expected {exp}, Got {act_repr})"
                print(f"FAILED on {desc}: {status}")
                sys.exit(1)
        except ValueError as e:
            act_repr = f"ValueError: {e}"
            if act_repr == exp:
                status = "PASS"
            else:
                status = f"FAIL (Expected {exp}, Got {act_repr})"
                print(f"FAILED on {desc}: {status}")
                sys.exit(1)
        except Exception as e:
            act_repr = f"Unexpected Error: {e}"
            status = "FAIL"
            print(f"ERROR on {desc}: {act_repr}")
            sys.exit(1)

        test_results.append((inp, act_repr, status, desc))

    # 3. Native Unit Test Suite Execution
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        test_module.TestStepsBoundaryContract
    )
    result = runner.run(suite)
    unit_test_output = stream.getvalue()

    if not result.wasSuccessful():
        print("Native unit test suite failed!")
        print(unit_test_output)
        sys.exit(1)

    print(f"All {len(test_cases)} boundary test cases passed.")
    print(f"Ran {result.testsRun} native unit tests: OK.")

    # 4. Write evidence files
    write_evidence(test_cases, test_results, unit_test_output)
    print(f"Verification evidence written to {WORK_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
