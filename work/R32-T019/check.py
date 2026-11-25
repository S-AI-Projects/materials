#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
import numpy as np
import scipy.linalg

TASK = "R32-T019"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEST_FILE = os.path.join(REPO_ROOT, "scipy-linalg", "test_complexity.py")
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
TIMINGS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timings.json")

def run():
    timings = {}
    rng = np.random.default_rng(42)
    for n in [10, 50, 200]:
        A = rng.random((n, n)) + n * np.eye(n)
        b = rng.random(n)
        t0 = time.perf_counter()
        for _ in range(5):
            x = scipy.linalg.solve(A, b)
        t1 = time.perf_counter()
        res = float(np.linalg.norm(A @ x - b))
        timings[f"n={n}"] = {
            "avg_time_sec": (t1 - t0) / 5.0,
            "residual": res,
            "passed": res < 1e-9
        }
    with open(TIMINGS_JSON, "w") as f:
        json.dump(timings, f, indent=2)

    cmd = [sys.executable, "-m", "unittest", TEST_FILE, "-v"]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    results = {
        "task": TASK,
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "python_version": sys.version,
        "test_count": 3,
        "status": "PASSED" if proc.returncode == 0 else "FAILED",
        "timings": timings
    }
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[{TASK}] Status: {results['status']}")
    print(proc.stderr)
    sys.exit(proc.returncode)

if __name__ == "__main__":
    run()
