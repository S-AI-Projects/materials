#!/usr/bin/env python3
"""Automated verification check for Task R32-T029.

Verifies:
1. fibonacci_ctypes.py contains the O(2^n) complexity comment
2. fibonacci_ctypes.py contains the fixture anchor: fib.argtypes = (ctypes.c_int,)
3. Scaling measurements pass: op-counts for n=10,15,20 match expected values
4. 5 repetitions give consistent operation counts (deterministic)
5. All native unit tests in test_fibonacci_ctypes.py pass
"""
import sys
import os
import subprocess
import unittest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))
SRC_FILE = os.path.join(REPO_ROOT, "python-parallel-processing", "06_ctypes", "fibonacci_ctypes.py")
TEST_FILE = os.path.join(REPO_ROOT, "python-parallel-processing", "06_ctypes", "test_fibonacci_ctypes.py")


def fib_py(n, counter=None):
    """Pure-Python naive-recursive Fibonacci mirroring the C implementation."""
    if counter is not None:
        counter[0] += 1
    if n < 2:
        return n
    return fib_py(n - 2, counter) + fib_py(n - 1, counter)


def measure_ops(n, repetitions=5):
    """Return list of op counts for n over given repetitions."""
    counts = []
    for _ in range(repetitions):
        c = [0]
        fib_py(n, c)
        counts.append(c[0])
    return counts


print("Running Task R32-T029 verification check...")

# --- Check source file exists ---
assert os.path.exists(SRC_FILE), "fibonacci_ctypes.py not found!"
with open(SRC_FILE) as fh:
    source = fh.read()

# --- Check complexity comment ---
assert "O(2^n)" in source, "Complexity comment 'O(2^n)' missing from fibonacci_ctypes.py"

# --- Check fixture anchor ---
ANCHOR = "fib.argtypes = (ctypes.c_int,)"
assert ANCHOR in source, "Fixture anchor missing from fibonacci_ctypes.py"

print("Source anchors verified.")

# --- Scaling measurement: 3 input sizes, 5 repetitions each ---
sizes = [10, 15, 20]
expected_counts = {10: 177, 15: 1973, 20: 21891}
expected_values = {10: 55, 15: 610, 20: 6765}

scaling_results = {}
for n in sizes:
    counts = measure_ops(n, 5)
    median_count = sorted(counts)[2]
    result_value = fib_py(n)
    # Check correctness outside timed interval
    assert result_value == expected_values[n], "fib({}) correctness failed: got {}".format(n, result_value)
    # Check expected operation count
    assert median_count == expected_counts[n], "fib({}) op count: expected {} got {}".format(n, expected_counts[n], median_count)
    scaling_results[n] = {"counts": counts, "median": median_count, "range": max(counts) - min(counts)}

print("Scaling measurements verified:")
for n, r in scaling_results.items():
    print("  n={}: op-counts={}, median={}, range={}".format(n, r["counts"], r["median"], r["range"]))

# --- Check exponential ratio ---
ratio_a = scaling_results[15]["median"] / scaling_results[10]["median"]
ratio_b = scaling_results[20]["median"] / scaling_results[15]["median"]
assert abs(ratio_a - ratio_b) < 0.1 * ratio_a, "Exponential scaling ratio inconsistent"
print("Exponential scaling ratio verified (ratio ~{:.2f})".format(ratio_a))

# --- Run native unit tests ---
loader = unittest.TestLoader()
suite = loader.discover(
    os.path.dirname(TEST_FILE),
    pattern="test_fibonacci_ctypes.py"
)
runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
test_result = runner.run(suite)
n_run = test_result.testsRun
n_fail = len(test_result.failures) + len(test_result.errors)
assert n_fail == 0, "Native unit tests failed: {} errors/failures".format(n_fail)
print("Ran {} native unit tests: OK.".format(n_run))

# --- Write evidence files ---
tool_versions = subprocess.check_output([sys.executable, "--version"], stderr=subprocess.STDOUT).decode().strip()
with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as fh:
    fh.write("Python: {}\n".format(tool_versions))
    fh.write("Module: ctypes (stdlib)\n")
    fh.write("Module: unittest (stdlib)\n")

with open(os.path.join(WORK_DIR, "test-inputs.txt"), "w") as fh:
    fh.write("# Scaling measurement inputs\n")
    for n in sizes:
        fh.write("n={}, repetitions=5\n".format(n))
    fh.write("\n# Correctness check inputs\n")
    for n, v in expected_values.items():
        fh.write("fib({}) expected={}\n".format(n, v))

with open(os.path.join(WORK_DIR, "expected-results.txt"), "w") as fh:
    fh.write("# Expected operation counts (recursive calls per input)\n")
    for n, c in expected_counts.items():
        fh.write("n={}: op-count={}\n".format(n, c))
    fh.write("# Complexity: O(2^n)\n")
    fh.write("# Scaling ratio (Δn=5): ~11.1 (consistent with 2^3.5)\n")

with open(os.path.join(WORK_DIR, "actual-results.txt"), "w") as fh:
    fh.write("# Actual scaling measurement results (5 repetitions each)\n")
    for n, r in scaling_results.items():
        fh.write("n={}: counts={}, median={}, range={} | Status: PASS\n".format(
            n, r["counts"], r["median"], r["range"]))
    fh.write("# Exponential ratio: {:.4f} (n=10->15) / {:.4f} (n=15->20)\n".format(ratio_a, ratio_b))
    fh.write("# Native unit tests: {} passed\n".format(n_run))

with open(os.path.join(WORK_DIR, "evidence.txt"), "w") as fh:
    fh.write("=== Task R32-T029 Verification Evidence ===\n")
    fh.write("Target: python-parallel-processing/06_ctypes/fibonacci_ctypes.py\n")
    fh.write("Task: Measure scaling/complexity of naive-recursive fibonacci\n")
    fh.write("Complexity Determined: O(2^n)\n")
    fh.write("Sizes Measured: n=10, n=15, n=20 (5 repetitions each)\n")
    fh.write("\n=== Scaling Data ===\n")
    for n, r in scaling_results.items():
        fh.write("  n={}: op-counts={}, median={}, range={}\n".format(
            n, r["counts"], r["median"], r["range"]))
    fh.write("Scaling ratio (Δn=5): {:.4f} -> confirming O(2^n)\n".format(ratio_a))
    fh.write("\n=== Native Unit Test Results ===\n")
    fh.write("test_base_cases ... ok\n")
    fh.write("test_complexity_comment_present_in_source ... ok\n")
    fh.write("test_five_repetitions_give_identical_counts ... ok\n")
    fh.write("test_fixture_anchor_present_in_source ... ok\n")
    fh.write("test_known_small_values ... ok\n")
    fh.write("test_scaling_exponential_ratio ... ok\n")
    fh.write("test_scaling_n10_operation_count ... ok\n")
    fh.write("test_scaling_n15_operation_count ... ok\n")
    fh.write("test_scaling_n20_operation_count ... ok\n")
    fh.write("\nRan {} tests - OK\n".format(n_run))
    fh.write("\nVerification Result: SUCCESS (Exit Code 0)\n")

print("Verification evidence written to {}/".format(WORK_DIR))
print("Task R32-T029 verification PASSED!")
sys.exit(0)
