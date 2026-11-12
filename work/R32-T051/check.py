import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "inherit-python-string"
EVIDENCE_DIR = Path(__file__).resolve().parent


def collect_fixture_results():
    sys.path.insert(0, str(SOURCE_DIR))
    from lower_string import LowerString

    fixtures = [
        ("", ""),
        ("PyThOn", "python"),
        ("AaAa", "aaaa"),
    ]

    results = []
    for input_value, expected in fixtures:
        actual = LowerString(input_value)
        results.append(
            f"Input={input_value!r} Expected={expected!r} Actual={actual!r}"
        )
    return results


command = [
    sys.executable,
    "-m",
    "unittest",
    "discover",
    "-s",
    str(SOURCE_DIR),
    "-p",
    "test_lower_string.py",
    "-v",
]

evidence = [
    "R32-T051 LowerString regression evidence",
    f"Python: {sys.version}",
    f"Platform: {platform.platform()}",
    f"Command: {' '.join(command)}",
    "",
    "Source preconditions:",
    "lower_string.py line 1: LowerString inherits from str",
    "lower_string.py line 4: constructor accepts string",
    "lower_string.py line 5: lowercase transformation",
    "",
    "Fixture results:",
    *collect_fixture_results(),
]

result = subprocess.run(
    command,
    cwd=ROOT,
    capture_output=True,
    text=True,
)

evidence.extend(
    [
        "",
        "Test output:",
        result.stdout,
        result.stderr,
        f"Exit code: {result.returncode}",
    ]
)

evidence_file = EVIDENCE_DIR / "evidence.txt"
evidence_file.write_text("\n".join(evidence))

print("\n".join(evidence))
print(f"\nEvidence saved to: {evidence_file}")

sys.exit(result.returncode)
