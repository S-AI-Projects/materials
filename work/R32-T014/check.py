#!/usr/bin/env python3
import json
import os
import subprocess
import sys

TASK = "R32-T014"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEST_FILE = os.path.join(REPO_ROOT, "oop-in-java-vs-python", "test_car.py")
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")

def run():
    cmd = [sys.executable, "-m", "unittest", TEST_FILE, "-v"]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    results = {
        "task": TASK,
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "python_version": sys.version,
        "test_count": 6,
        "status": "PASSED" if proc.returncode == 0 else "FAILED",
    }
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[{TASK}] Status: {results['status']}")
    print(proc.stderr)
    sys.exit(proc.returncode)

if __name__ == "__main__":
    run()
