import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q",
     "python-311/tests/test_print_at.py"],
    cwd=root,
)
raise SystemExit(result.returncode)
