import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = ROOT / "python-microservices-with-grpc" / "marketplace"

result = subprocess.run(
    [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "marketplace_unit_test.py",
    ],
    cwd=MARKETPLACE,
)

sys.exit(result.returncode)
