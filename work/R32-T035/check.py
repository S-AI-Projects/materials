from __future__ import annotations

import os
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    project_dir = repo_root / "python-project-for-agentic-coding"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_dir / "src") + os.pathsep + env.get("PYTHONPATH", "")

    print(f"Python: {sys.version.splitlines()[0]}")
    try:
        print(f"pytest: {version('pytest')}")
    except PackageNotFoundError:
        print("pytest: not installed")

    if sys.version_info < (3, 14):
        print("ERROR: This project requires Python >=3.14.")
        return 1

    return subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_double_repeatable.py", "-q"],
        cwd=project_dir,
        env=env,
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
