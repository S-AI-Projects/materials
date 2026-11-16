from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "python-rounding" / "rounding.py"
TEST = ROOT / "python-rounding" / "test_rounding.py"
RESULTS = ROOT / "work" / "R32-T040" / "results.txt"

original_source = SOURCE.read_text()
original_test = TEST.read_text()

expected_line = "    return int(n * multiplier) / multiplier"
mutant_line = "    return math.floor(n * multiplier) / multiplier"

assert original_source.count(expected_line) == 1, (
    "Expected exactly one truncate return statement"
)

records = []

records.append("R32-T040: truncate regression and mutation check")
records.append("==============================================")
records.append("")
records.append("Environment:")
records.append(
    subprocess.check_output(
        [sys.executable, "--version"], text=True
    ).strip()
)
records.append(
    subprocess.check_output(
        [sys.executable, "-m", "pytest", "--version"], text=True
    ).strip()
)
records.append("")
records.append("Protected source condition:")
records.append("python-rounding/rounding.py:4 defines truncate(n, decimals=0)")
records.append("python-rounding/rounding.py:5 scales by 10**decimals")
records.append("python-rounding/rounding.py:6 uses int() before division")
records.append("")
records.append("Regression inputs and independent expected outputs:")
records.append("- truncate(-0.9, 0) == 0.0")
records.append("- truncate(-12.349, 2) == -12.34")
records.append("- truncate(12.349, 2) == 12.34")
records.append("- truncate(0, 0) == 0.0")
records.append("All cases also assert that the result type is exactly float.")
records.append("")

original_command = [
    sys.executable,
    "-m",
    "pytest",
    "-q",
    str(TEST),
]

original = subprocess.run(
    original_command,
    cwd=ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

records.append("ORIGINAL IMPLEMENTATION")
records.append("Command: {} -m pytest -q {}".format(sys.executable, TEST.relative_to(ROOT)))
records.append("Exit code: {}".format(original.returncode))
records.append(original.stdout)

if original.returncode != 0:
    RESULTS.write_text("\n".join(records))
    print(original.stdout)
    raise SystemExit("Original implementation did not pass")

mutant_source = original_source.replace(expected_line, mutant_line)

with tempfile.TemporaryDirectory(prefix="r32-t040-mutant-") as temp:
    temp_dir = Path(temp)
    (temp_dir / "rounding.py").write_text(mutant_source)
    shutil.copy2(TEST, temp_dir / "test_rounding.py")

    mutant = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "test_rounding.py",
        ],
        cwd=temp_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

records.append("")
records.append("TEMPORARY MUTANT: int() replaced with math.floor()")
records.append("Mutant exists only in a temporary directory.")
records.append("Exit code: {}".format(mutant.returncode))
records.append(mutant.stdout)

expected_failure = (
    mutant.returncode != 0
    and "test_truncate_returns_float_and_truncates_toward_zero" in mutant.stdout
    and "failed" in mutant.stdout
)

if not expected_failure:
    RESULTS.write_text("\n".join(records))
    raise SystemExit("Mutant did not fail the expected regression test")

records.append("")
records.append("RESULT: PASS")
records.append("Original implementation passed.")
records.append("Temporary floor mutant failed the same named regression test.")
records.append("The real rounding.py was not modified.")

RESULTS.write_text("\n".join(records))

print(original.stdout)
print(mutant.stdout)
print("Mutation check passed.")
print("Evidence saved to work/R32-T040/results.txt")
