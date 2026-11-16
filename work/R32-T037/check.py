import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work" / "R32-T037"
TEST_FILE = WORK / "test_space_rocks_example.py"


def main():
    venv_python = ROOT / ".venv" / "bin" / "python3"
    if not venv_python.exists():
        venv_python = ROOT / ".venv" / "bin" / "python"
    python = str(venv_python) if venv_python.exists() else sys.executable

    command = [python, "-m", "pytest", "-q", str(TEST_FILE)]
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    (WORK / "test-output.txt").write_text(output)
    print(output, end="")
    if result.returncode:
        raise SystemExit(result.returncode)

    passed = re.search(r"(\d+) passed", output)
    if passed is None or int(passed.group(1)) == 0:
        raise SystemExit("pytest did not report any passing tests")

    python_version = subprocess.check_output(
        [python, "--version"], text=True
    ).strip()
    pytest_version = subprocess.check_output(
        [python, "-m", "pytest", "--version"], text=True
    ).strip()
    ruff = ROOT / ".venv" / "bin" / "ruff"
    if not ruff.exists():
        ruff_on_path = shutil.which("ruff")
        ruff = Path(ruff_on_path) if ruff_on_path else None
    ruff_version = (
        subprocess.check_output([str(ruff), "--version"], text=True).strip()
        if ruff
        else "not available in this validation environment; repo pin is ruff==0.14.1"
    )
    requirements = (
        ROOT / "asterioids-pygame-project" / "source_code_final" / "requirements.txt"
    ).read_text().strip()

    versions = (
        f"Python: {python_version}\n"
        f"pytest: {pytest_version}\n"
        f"Pygame: mocked in focused tests; project requirement is {requirements}\n"
        f"Ruff: {ruff_version}\n"
    )
    (WORK / "tool-versions.txt").write_text(versions)

    relative_command = "python3 work/R32-T037/check.py"
    command_text = " ".join(command)
    results = (
        "# R32-T037 check results\n\n"
        f"Focused tests passed: {passed.group(1)}\n"
        f"Required command: {relative_command}\n"
        f"Pytest invocation: {command_text}\n"
        "The tests stub Pygame, models, and utils imports to isolate the "
        "named game module; no window or assets are used.\n"
        "The README example is executed and its complete output is compared "
        "with a literal expected string.\n"
        "Actual pytest output is saved in test-output.txt; environment "
        "details are saved in tool-versions.txt.\n"
    )
    (WORK / "results.md").write_text(results)
    print(f"PASS: {passed.group(1)} focused tests")


if __name__ == "__main__":
    main()
