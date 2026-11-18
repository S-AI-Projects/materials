#!/usr/bin/env python3
"""Verification check runner for Task R32-T023.

Cross-checks github copilot code review against an independent reference oracle.
Evaluates smallest valid input, ordinary inputs, and anti-pattern detections.
"""

import importlib.util
import io
import os
import platform
import sys
import unittest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))

# Load code_review.py
CODE_REVIEW_PATH = os.path.join(REPO_ROOT, "github-copilot-code-review", "code_review.py")
spec = importlib.util.spec_from_file_location("code_review", CODE_REVIEW_PATH)
code_review = importlib.util.module_from_spec(spec)
sys.modules["code_review"] = code_review
spec.loader.exec_module(code_review)

# Load test_code_review.py
TEST_CODE_REVIEW_PATH = os.path.join(
    REPO_ROOT, "github-copilot-code-review", "test_code_review.py"
)
test_spec = importlib.util.spec_from_file_location("test_code_review", TEST_CODE_REVIEW_PATH)
test_module = importlib.util.module_from_spec(test_spec)
test_spec.loader.exec_module(test_module)

ARCHIVE_NAME = code_review.ARCHIVE_NAME
BRANCH_MAIN = code_review.BRANCH_MAIN
BRANCH_PLAYER_NAMES = code_review.BRANCH_PLAYER_NAMES
BRANCH_PLAYER_NAMES_FINAL = code_review.BRANCH_PLAYER_NAMES_FINAL
github_copilot_code_review = code_review.github_copilot_code_review
reference_code_review = code_review.reference_code_review


def write_evidence(test_cases, test_results, unit_test_output):
    """Write verification evidence into work/R32-T023/."""
    os.makedirs(WORK_DIR, exist_ok=True)

    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Interpreter: {sys.executable}\n")

    with open(os.path.join(WORK_DIR, "test-inputs.txt"), "w") as f:
        f.write("# Precondition Anchors from README.md:\n")
        f.write("Line 1: Real Python tutorial baseline\n")
        f.write(f"Line 5: Archive anchor {ARCHIVE_NAME}\n")
        f.write(f"Line 7: Base branch {BRANCH_MAIN}\n")
        f.write(f"Line 8: Feature branch {BRANCH_PLAYER_NAMES}\n")
        f.write(f"Line 9: Final feature branch {BRANCH_PLAYER_NAMES_FINAL}\n\n")
        f.write("# Differential Comparison Test Inputs:\n")
        for branch, diff, desc in test_cases:
            f.write(f"Branch: {branch} | Diff: {repr(diff)} | Desc: {desc}\n")

    with open(os.path.join(WORK_DIR, "expected-results.txt"), "w") as f:
        f.write("# Expected Results from Independent Reference Oracle:\n")
        for branch, diff, desc in test_cases:
            exp = reference_code_review(branch, diff)
            f.write(f"Branch: {branch} => Expected: {exp} ({desc})\n")

    with open(os.path.join(WORK_DIR, "actual-results.txt"), "w") as f:
        f.write("# Actual Results from github_copilot_code_review:\n")
        for branch, act, status, desc in test_results:
            f.write(f"Branch: {branch} => Actual: {act} | Status: {status} ({desc})\n")

    with open(os.path.join(WORK_DIR, "evidence.txt"), "w") as f:
        f.write("=== Task R32-T023 Verification Evidence ===\n")
        f.write("Target: github-copilot-code-review/README.md (Differential Reference)\n")
        f.write(f"Differential Cases Verified: {len(test_results)}/{len(test_cases)}\n")
        f.write("Primary implementation matches Independent Reference 100%.\n\n")
        f.write("=== Native Unit Test Output ===\n")
        f.write(unit_test_output)
        f.write("\nVerification Result: SUCCESS (Exit Code 0)\n")


def main():
    print("Running Task R32-T023 verification check...")

    # 1. Precondition anchors
    assert ARCHIVE_NAME == "pop-quiz.zip", "Anchor mismatch: pop-quiz.zip"
    assert BRANCH_MAIN == "main", "Anchor mismatch: main"
    assert BRANCH_PLAYER_NAMES == "feature/player-names", "Anchor mismatch: feature/player-names"
    assert (
        BRANCH_PLAYER_NAMES_FINAL == "feature/player-names-final"
    ), "Anchor mismatch: feature/player-names-final"

    # 2. Differential Test Matrix
    test_cases = [
        (BRANCH_MAIN, "", "Smallest valid input (empty diff)"),
        (BRANCH_PLAYER_NAMES, "+ valid_line = 1\n", "Ordinary clean addition"),
        (
            BRANCH_PLAYER_NAMES,
            "+ # TODO: complete player name validation\n",
            "TODO anti-pattern detection",
        ),
        (
            BRANCH_PLAYER_NAMES_FINAL,
            "+ print('DEBUGGING player score')\n",
            "Debug print detection",
        ),
        (
            BRANCH_PLAYER_NAMES_FINAL,
            "+ try:\n+     x = 1\n+ except:\n+     pass\n",
            "Bare except detection",
        ),
        (
            BRANCH_MAIN,
            (
                "+ # TODO: first\n"
                "+ print('debug msg')\n"
                "+ except:\n"
            ),
            "Multiple simultaneous findings",
        ),
    ]

    test_results = []
    for branch, diff, desc in test_cases:
        actual = github_copilot_code_review(branch, diff)
        expected = reference_code_review(branch, diff)

        if actual == expected:
            status = "PASS"
        else:
            status = f"FAIL (Expected {expected}, Got {actual})"
            print(f"FAILED on {desc}: {status}")
            sys.exit(1)

        test_results.append((branch, actual, status, desc))

    # 3. Native Unit Test Suite Execution
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        test_module.TestCodeReviewDifferential
    )
    result = runner.run(suite)
    unit_test_output = stream.getvalue()

    if not result.wasSuccessful():
        print("Native unit test suite failed!")
        print(unit_test_output)
        sys.exit(1)

    print(f"All {len(test_cases)} differential test cases passed.")
    print(f"Ran {result.testsRun} native unit tests: OK.")

    # 4. Write evidence files
    write_evidence(test_cases, test_results, unit_test_output)
    print(f"Verification evidence written to {WORK_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
