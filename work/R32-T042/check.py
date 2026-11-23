#!/usr/bin/env python3
"""
Automated verification check runner for R32-T042.
Task: Define the supported boundaries of python circular imports (main.py) [python-circular-imports]
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
    cmd = [sys.executable, "-m", "unittest", "python-circular-imports/broken/test_main.py"]
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Native unit tests failed:\n{res.stderr}\n{res.stdout}")
    
    # Extract test count
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

def run_boundary_checks():
    # Import main with broken dir on path
    broken_dir = REPO_ROOT / "python-circular-imports" / "broken"
    if str(broken_dir) not in sys.path:
        sys.path.insert(0, str(broken_dir))
    
    import main

    checks = []

    # Check 1: Smallest valid input
    input_1 = {"name": "", "price": 0.0, "quantity": 0, "add_shipping": True}
    expected_1 = 4.99
    actual_1 = main.calculate_order_total(**input_1)
    assert actual_1 == expected_1, f"Expected {expected_1}, got {actual_1}"
    checks.append({
        "name": "smallest_valid_input_with_shipping",
        "precondition_source": "main.py:Lines 3-5",
        "input": input_1,
        "expected": expected_1,
        "actual": actual_1,
        "status": "PASS"
    })

    # Check 2: Smallest valid input without shipping
    input_2 = {"name": "", "price": 0.0, "quantity": 0, "add_shipping": False}
    expected_2 = 0.0
    actual_2 = main.calculate_order_total(**input_2)
    assert actual_2 == expected_2, f"Expected {expected_2}, got {actual_2}"
    checks.append({
        "name": "smallest_valid_input_no_shipping",
        "precondition_source": "main.py:Lines 3-4",
        "input": input_2,
        "expected": expected_2,
        "actual": actual_2,
        "status": "PASS"
    })

    # Check 3: Ordinary input
    input_3 = {"name": "Laptop", "price": 1000.0, "quantity": 1, "add_shipping": True}
    expected_3 = 1004.99
    actual_3 = main.calculate_order_total(**input_3)
    assert actual_3 == expected_3, f"Expected {expected_3}, got {actual_3}"
    checks.append({
        "name": "ordinary_input",
        "precondition_source": "main.py:Lines 3-5",
        "input": input_3,
        "expected": expected_3,
        "actual": actual_3,
        "status": "PASS"
    })

    # Check 4: Circular import boundary precondition (Line 1)
    import_raised = False
    for mod in list(sys.modules.keys()):
        if mod.startswith("shop"):
            del sys.modules[mod]
    try:
        from shop.product import Product
    except ImportError as e:
        import_raised = True
        err_msg = str(e)
    assert import_raised, "Expected ImportError on unmitigated circular import"
    checks.append({
        "name": "circular_import_precondition_line1",
        "precondition_source": "main.py:Line 1",
        "input": "from shop.product import Product",
        "expected": "ImportError: cannot import name 'Product' from partially initialized module 'shop.product'",
        "actual": f"ImportError: {err_msg}",
        "status": "PASS"
    })

    return checks

def main_runner():
    os.makedirs(WORK_DIR, exist_ok=True)
    versions = get_tool_versions()
    native_result = run_native_test_suite()
    boundary_checks = run_boundary_checks()

    summary = {
        "task_id": "R32-T042",
        "tool_versions": versions,
        "native_check": native_result,
        "boundary_checks": boundary_checks,
        "overall_status": "PASSED"
    }

    results_file = WORK_DIR / "results.json"
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)

    log_file = WORK_DIR / "run.log"
    with open(log_file, "w") as f:
        f.write(f"Task R32-T042 Verification\n")
        f.write(f"Python: {versions['python']}\n")
        f.write(f"Git Commit: {versions['git_commit']}\n")
        f.write(f"Native Test Command: {native_result['command']}\n")
        f.write(f"Native Test Count: {native_result['test_count']}\n")
        f.write(f"Boundary Checks Ran: {len(boundary_checks)}\n")
        f.write(f"Status: ALL CHECKS PASSED\n")

    print(f"R32-T042: All {len(boundary_checks)} boundary checks and {native_result['test_count']} native tests passed successfully!")

if __name__ == "__main__":
    main_runner()
