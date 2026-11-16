import io
import platform
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "how-to-use-github"
EVIDENCE_DIR = Path(__file__).resolve().parent


def collect_fixture_results():
    """Execute change_color on literal fixture inputs with mocked I/O."""
    sys.path.insert(0, str(SOURCE_DIR))
    from weather import (
        CYAN,
        RED,
        RESET,
        REVERSE,
        _select_weather_display_params,
        change_color,
    )

    fixtures = [
        ("Smallest valid input (empty string)", "", ""),
        ("Ordinary input anchor 1 (RED, thunderstorm)", RED, "\033[1;31m"),
        ("Ordinary input anchor 2 (CYAN, drizzle)", CYAN, "\033[1;36m"),
        ("Documented boundary (RESET code)", RESET, "\033[0m"),
        ("Documented boundary (REVERSE code)", REVERSE, "\033[;7m"),
    ]

    results = []
    for label, input_value, expected in fixtures:
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            ret = change_color(input_value)
            actual = mock_stdout.getvalue()

        assert ret is None, f"Expected return None for {label}, got {ret!r}"
        assert actual == expected, (
            f"Output mismatch for {label}: "
            f"expected {expected!r}, got {actual!r}"
        )
        assert not actual.endswith("\n"), (
            f"Unexpected trailing newline for {label}"
        )

        results.append(
            f"[{label}] Input={input_value!r} Expected={expected!r} "
            f"Actual={actual!r} Return={ret!r}"
        )

    # Both sides of documented weather condition boundary
    # Side A: Upper boundary of THUNDERSTORM (299)
    symbol_a, color_a = _select_weather_display_params(299)
    assert symbol_a == "💥" and color_a == RED
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        ret_a = change_color(color_a)
        actual_a = mock_stdout.getvalue()
    assert actual_a == "\033[1;31m"
    results.append(
        "[Weather condition boundary side A (weather_id=299)] "
        f"Symbol={symbol_a!r} Color={color_a!r} "
        f"Output={actual_a!r} Return={ret_a!r}"
    )

    # Side B: Lower boundary of DRIZZLE (300)
    symbol_b, color_b = _select_weather_display_params(300)
    assert symbol_b == "💧" and color_b == CYAN
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        ret_b = change_color(color_b)
        actual_b = mock_stdout.getvalue()
    assert actual_b == "\033[1;36m"
    results.append(
        "[Weather condition boundary side B (weather_id=300)] "
        f"Symbol={symbol_b!r} Color={color_b!r} "
        f"Output={actual_b!r} Return={ret_b!r}"
    )

    return results


def get_tool_versions():
    """Retrieve versions of relevant tooling."""
    ruff_ver = "unknown"
    candidates = [
        ROOT / ".venv" / "bin" / "ruff",
        Path(sys.executable).parent / "ruff",
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                proc = subprocess.run(
                    [str(candidate), "--version"],
                    capture_output=True,
                    text=True,
                )
                if proc.returncode == 0:
                    ruff_ver = proc.stdout.strip()
                    break
            except Exception:
                pass
    if ruff_ver == "unknown":
        try:
            proc = subprocess.run(
                ["ruff", "--version"],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                ruff_ver = proc.stdout.strip()
        except Exception:
            pass
    return {
        "Python": sys.version,
        "Platform": platform.platform(),
        "Ruff": ruff_ver,
    }


def main():
    tool_info = get_tool_versions()

    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(SOURCE_DIR),
        "-p",
        "test_weather.py",
        "-v",
    ]

    fixture_results = collect_fixture_results()

    evidence = [
        "R32-T052 change_color boundary evidence",
        f"Python: {tool_info['Python']}",
        f"Platform: {tool_info['Platform']}",
        f"Ruff: {tool_info['Ruff']}",
        f"Command: {' '.join(command)}",
        "",
        "Source preconditions:",
        "weather.py line 11: RED = '\\033[1;31m'",
        "weather.py line 13: CYAN = '\\033[1;36m'",
        "weather.py line 17: REVERSE = '\\033[;7m'",
        "weather.py line 18: RESET = '\\033[0m'",
        "weather.py line 21-22: def change_color(color): print(color, end='')",
        "weather.py line 31: THUNDERSTORM = range(200, 300)",
        "weather.py line 32: DRIZZLE = range(300, 400)",
        "weather.py line 133: change_color(REVERSE)",
        "weather.py line 135: change_color(RESET)",
        "weather.py line 137: change_color(color)",
        "weather.py line 143: change_color(RESET)",
        "weather.py line 157: display_params = ('💥', RED)",
        "weather.py line 159: display_params = ('💧', CYAN)",
        "",
        "Boundary Contract Table:",
        "- Parameter: color (str)",
        "- Valid domain: strings representing terminal ANSI escape codes",
        "- Smallest valid input: '' (empty string, length 0, prints nothing)",
        "- Ordinary inputs: RED ('\\033[1;31m'), CYAN ('\\033[1;36m')",
        "- Boundary inputs: RESET ('\\033[0m'), REVERSE ('\\033[;7m')",
        "- Return value: None",
        "- Mutation: None (input is immutable string)",
        "- External dependencies: sys.stdout via print(color, end='')",
        "- Trailing newline: None added (end='')",
        "- Unsupported inputs: standard Python type handling, no arbitrary "
        "rejection",
        "",
        "Fixture results:",
        *fixture_results,
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

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_file = EVIDENCE_DIR / "evidence.txt"
    evidence_file.write_text("\n".join(evidence))

    print("\n".join(evidence))
    print(f"\nEvidence saved to: {evidence_file}")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
