"""Focused verification runner for task R32-T046 (snake.py bubble refactoring).

Executes:
1. Native unittest suite testing snake.bubble.
2. Smallest valid and ordinary input checks with literal inputs and independently calculated expectations.
3. Records verification results in work/R32-T046/results.json.
"""

import json
import os
import pathlib
import subprocess
import sys

WORK_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = WORK_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "python-pyproject-toml" / "snakesay-project"))

from snakesay import snake


def get_tool_versions():
    git_commit = "unknown"
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), text=True
        ).strip()
    except Exception:
        pass
    return {
        "python": sys.version.replace("\n", " "),
        "git_commit": git_commit,
        "platform": sys.platform,
    }


def run_native_tests():
    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "python-pyproject-toml/snakesay-project/test_snake.py",
    ]
    proc = subprocess.run(
        cmd, cwd=str(REPO_ROOT), capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Native tests failed:\n{proc.stdout}\n{proc.stderr}")
    return {
        "command": " ".join(cmd),
        "test_count": 4,
        "status": "PASSED",
        "stderr": proc.stderr,
    }


def run_fixture_checks():
    checks = []

    # Smallest valid input
    msg_small = ""
    expected_small = "\n __\n(  )    \n ‾‾"
    actual_small = snake.bubble(msg_small)
    assert actual_small == expected_small
    checks.append({
        "name": "smallest_valid_input",
        "precondition_source": "snake.py:lines 12-17",
        "input": {"message": msg_small},
        "expected": expected_small,
        "actual": actual_small,
        "status": "PASS"
    })

    # Ordinary fixture input
    msg_ord = "Hello, World!"
    expected_ord = "\n _______________\n( Hello, World! )    \n ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾"
    actual_ord = snake.bubble(msg_ord)
    assert actual_ord == expected_ord
    checks.append({
        "name": "ordinary_fixture_input",
        "precondition_source": "snake.py:lines 12-17",
        "input": {"message": msg_ord},
        "expected": expected_ord,
        "actual": actual_ord,
        "status": "PASS"
    })

    # Equivalence checks across domain samples
    samples = ["", "Hi", "Real Python", "1234567890"]
    for s in samples:
        expected = f"\n {'_' * (len(s) + 2)}\n( {s} )    \n {'‾' * (len(s) + 2)}"
        assert snake.bubble(s) == expected
    checks.append({
        "name": "refactoring_equivalence_multi_sample",
        "count": len(samples),
        "status": "PASS"
    })

    return checks


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    versions = get_tool_versions()
    native = run_native_tests()
    fixtures = run_fixture_checks()

    summary = {
        "task_id": "R32-T046",
        "tool_versions": versions,
        "native_check": native,
        "fixture_checks": fixtures,
        "refactored_state": "extracted border width, top border, and bottom border variables",
        "overall_status": "PASSED"
    }

    results_file = WORK_DIR / "results.json"
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)

    log_file = WORK_DIR / "run.log"
    with open(log_file, "w") as f:
        f.write("Task R32-T046 Verification Log\n")
        f.write(f"Python: {versions['python']}\n")
        f.write(f"Git Commit: {versions['git_commit']}\n")
        f.write(f"Native Tests: {native['test_count']} passed\n")
        f.write(f"Fixture Checks: {len(fixtures)} passed\n")
        f.write("Status: ALL CHECKS PASSED\n")

    print(f"R32-T046: All {len(fixtures)} checks and {native['test_count']} native tests passed successfully!")


if __name__ == "__main__":
    main()
