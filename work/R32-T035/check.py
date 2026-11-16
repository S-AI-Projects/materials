import sys
from ai_agent_project import double

def record(msg: str) -> None:
    print(msg)

def main() -> None:
    record(f"Python version: {sys.version.splitlines()[0]}")
    tests = [
        ("zero", 0, 0),
        ("seven", 7, 14),
    ]
    for name, inp, expected in tests:
        result = double(inp)
        record(f"Test {name}: double({inp}) => {result} (expected {expected})")
        assert result == expected, f"{name} failed: {result} != {expected}"
    # Repeatability test
    first = double(3)
    _ = double(5)
    second = double(3)
    record(f"Repeatability: first={first}, second={second}")
    assert first == second == 6, "Repeatability test failed"
    record("All checks passed.")

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        sys.exit(str(e))
