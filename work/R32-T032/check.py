import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

subprocess.run(
    [PYTHON, "-m", "unittest", "web-scraping-bs4/test_scraper.py", "-v"],
    cwd=ROOT,
    check=True,
)
