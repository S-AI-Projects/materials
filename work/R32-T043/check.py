#!/usr/bin/env python3
"""
Automated verification check runner for R32-T043.
Task: Cross-check python formatted output (format.py) [python-formatted-output]
"""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORK_DIR = Path(__file__).resolve().parent

def get_tool_versions():
    python_ver = sys.version.replace("\n", " ")
    try:
        git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=REPO_ROOT).strip()
    except Exception as e:
        git_hash = str(e)
    return {
        "python": python_ver,
        "git_commit": git_hash
    }

def run_native_test_suite():
    cmd = [sys.executable, "-m", "unittest", "python-formatted-output/test_format.py"]
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Native unit tests failed:\n{res.stderr}\n{res.stdout}")

    test_count = 0
    for line in res.stderr.splitlines():
        if line.startswith("Ran ") and "tests" in line:
            parts = line.split()
            test_count = int(parts[1])
            break

    return {
        "command": " ".join(cmd),
        "test_count": test_count,
        "stdout": res.stdout,
        "stderr": res.stderr,
        "status": "PASSED"
    }

def run_oracle_checks():
    pkg_dir = REPO_ROOT / "python-formatted-output"
    if str(pkg_dir) not in sys.path:
        sys.path.insert(0, str(pkg_dir))

    import format as fmt_mod
    from test_format import oracle_binary

    test_domain = [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        15, 16, 17, 31, 32, 63, 64, 127, 128, 255, 256, 257, 512, 1024
    ]

    checks = []
    # Check 1: smallest valid input
    act_min = fmt_mod.format_binary(0)
    exp_min = oracle_binary(0)
    assert act_min == exp_min == "0", f"Smallest valid check failed: {act_min} != {exp_min}"
    checks.append({
        "name": "smallest_valid_input",
        "precondition_source": "format.py:Line 1",
        "input": 0,
        "expected": exp_min,
        "actual": act_min,
        "status": "PASS"
    })

    # Check 2: ordinary input
    act_ord = fmt_mod.format_binary(257)
    exp_ord = oracle_binary(257)
    assert act_ord == exp_ord == "100000001", f"Ordinary input check failed: {act_ord} != {exp_ord}"
    checks.append({
        "name": "ordinary_input",
        "precondition_source": "format.py:Line 1",
        "input": 257,
        "expected": exp_ord,
        "actual": act_ord,
        "status": "PASS"
    })

    # Enumerate all domain values
    domain_results = []
    for val in test_domain:
        expected = oracle_binary(val)
        actual = fmt_mod.format_binary(val)
        assert actual == expected, f"Mismatch at {val}: {actual} != {expected}"
        domain_results.append({
            "input": val,
            "oracle_expected": expected,
            "actual": actual,
            "match": True
        })

    return {
        "key_checks": checks,
        "enumerated_inputs_count": len(test_domain),
        "domain_results": domain_results
    }

def main_runner():
    os.makedirs(WORK_DIR, exist_ok=True)
    versions = get_tool_versions()
    native_result = run_native_test_suite()
    oracle_res = run_oracle_checks()

    summary = {
        "task_id": "R32-T043",
        "tool_versions": versions,
        "native_check": native_result,
        "oracle_comparison": oracle_res,
        "overall_status": "PASSED"
    }

    results_file = WORK_DIR / "results.json"
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)

    log_file = WORK_DIR / "run.log"
    with open(log_file, "w") as f:
        f.write("Task R32-T043 Verification\n")
        f.write(f"Python: {versions['python']}\n")
        f.write(f"Git Commit: {versions['git_commit']}\n")
        f.write(f"Native Test Command: {native_result['command']}\n")
        f.write(f"Native Test Count: {native_result['test_count']}\n")
        f.write(f"Oracle Verified Inputs Count: {oracle_res['enumerated_inputs_count']}\n")
        f.write("Status: ALL CHECKS PASSED\n")

    print(f"R32-T043: All {oracle_res['enumerated_inputs_count']} domain inputs and {native_result['test_count']} native tests passed successfully!")

if __name__ == "__main__":
    main_runner()
