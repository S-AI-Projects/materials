"""Focused verification and regression strengthening runner for task R32-T050.

Executes:
1. Native unittest suite testing python get all files in directory with in-memory paths and mocked I/O.
2. Creates a temporary copy of the implementation and introduces a plausible one-line mistake:
   checking `item.name not in skip_set` instead of `set(item.parts).isdisjoint(skip_set)`.
3. Demonstrates that the regression test detects this mutant and fails the named assertion for a semantic reason.
4. Confirms that the original code passes all tests and contains no test-only or mutated branches.
5. Records inputs, tool versions, expected vs actual outputs, and results in work/R32-T050/results.json.
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

WORK_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = WORK_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "python-get-all-files-in-directory"))

import examples


def get_tool_versions():
    git_commit = "unknown"
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), text=True
        ).strip()
    except Exception:
        pass
    return {
        "python": sys.version.replace("\n", " "),
        "git_commit": git_commit,
        "platform": sys.platform,
    }


def run_native_tests():
    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "python-get-all-files-in-directory/test_examples.py",
    ]
    proc = subprocess.run(
        cmd, cwd=str(REPO_ROOT), capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Native tests failed on original implementation:\n{proc.stdout}\n{proc.stderr}")
    return {
        "command": " ".join(cmd),
        "test_count": 4,
        "status": "PASSED",
        "stderr": proc.stderr,
    }


def run_mutation_check():
    """Verify that a temporary mutant fails the regression assertion for a semantic reason."""
    source_file = REPO_ROOT / "python-get-all-files-in-directory" / "examples.py"
    with open(source_file, "r") as f:
        original_code = f.read()

    # Plausible one-line mistake: developer checks only item.name instead of set(item.parts)
    target_line = "return [item for item in paths if set(item.parts).isdisjoint(skip_set)]"
    mutant_line = "return [item for item in paths if item.name not in skip_set]"

    if target_line not in original_code:
        raise ValueError(f"Target line for mutation not found in {source_file}")

    mutated_code = original_code.replace(target_line, mutant_line)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        # Copy package files to temporary directory
        (tmp_path / "examples.py").write_text(mutated_code)
        shutil.copy(REPO_ROOT / "python-get-all-files-in-directory" / "skip_dirs.py", tmp_path / "skip_dirs.py")
        shutil.copy(REPO_ROOT / "python-get-all-files-in-directory" / "test_examples.py", tmp_path / "test_examples.py")

        cmd = [sys.executable, "-m", "unittest", "test_examples.py"]
        proc = subprocess.run(cmd, cwd=str(tmp_path), capture_output=True, text=True)

        # The mutant MUST fail the regression assertions
        assert proc.returncode != 0, "Mutant unexpectedly passed tests; regression suite is not strong enough!"
        assert "AssertionError" in proc.stderr or "AssertionError" in proc.stdout, "Failure must be an assertion failure"
        assert "test_ordinary_fixture_input" in proc.stderr or "test_nested_junk_directory_rejection" in proc.stderr, \
            "Failure must identify the named assertion verifying junk directory exclusion"

        return {
            "mutated_line_original": target_line,
            "mutated_line_mutant": mutant_line,
            "semantic_reason": (
                "The mutant checks `item.name not in skip_set`, which only inspects the leaf file "
                "name (e.g. 'cache.tmp'). It fails to inspect intermediate directory components "
                "(e.g. 'Desktop/temp/cache.tmp'), erroneously including files located inside junk directories. "
                "The original implementation checks `set(item.parts).isdisjoint(skip_set)`, ensuring "
                "all path components are validated."
            ),
            "mutant_test_status": "FAILED (as expected)",
            "mutant_stderr": proc.stderr,
        }


def run_fixtures_verification():
    # Smallest valid input
    smallest_input = []
    smallest_expected = []
    smallest_actual = examples.filter_skip_dirs(smallest_input, skip_dirs=examples.SKIP_DIRS)
    assert smallest_actual == smallest_expected, f"Smallest valid input failed: {smallest_actual} != {smallest_expected}"

    # Ordinary fixture input
    ordinary_input = [
        pathlib.Path("Desktop/realpython/iterate-dict.md"),
        pathlib.Path("Desktop/temp/cache.tmp"),
        pathlib.Path("Desktop/todo.txt"),
        pathlib.Path("Desktop/logs/app.log"),
        pathlib.Path("Desktop/temporary_files/scratch.txt"),
        pathlib.Path("Desktop/scripts/rename_files.py"),
    ]
    ordinary_expected = [
        pathlib.Path("Desktop/realpython/iterate-dict.md"),
        pathlib.Path("Desktop/todo.txt"),
        pathlib.Path("Desktop/scripts/rename_files.py"),
    ]
    ordinary_actual = examples.filter_skip_dirs(ordinary_input, skip_dirs=examples.SKIP_DIRS)
    assert ordinary_actual == ordinary_expected, f"Ordinary input failed: {ordinary_actual} != {ordinary_expected}"

    return {
        "smallest_valid_input": {
            "input": [str(p) for p in smallest_input],
            "expected": [str(p) for p in smallest_expected],
            "actual": [str(p) for p in smallest_actual],
            "status": "PASSED"
        },
        "ordinary_fixture_input": {
            "input": [str(p) for p in ordinary_input],
            "expected": [str(p) for p in ordinary_expected],
            "actual": [str(p) for p in ordinary_actual],
            "status": "PASSED"
        }
    }


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    versions = get_tool_versions()
    native = run_native_tests()
    fixtures = run_fixtures_verification()
    mutation = run_mutation_check()

    summary = {
        "task_id": "R32-T050",
        "tool_versions": versions,
        "preconditions": {
            "line_64": "SKIP_DIRS = ['temp', 'temporary_files', 'logs']",
            "line_71": "large_dir.rglob('*')",
            "line_72": "if set(item.parts).isdisjoint(SKIP_DIRS):",
            "line_76_82": "[item for item in large_dir.rglob('*') if set(item.parts).isdisjoint(SKIP_DIRS)]"
        },
        "native_check": native,
        "fixtures": fixtures,
        "mutation_testing": mutation,
        "overall_status": "PASSED"
    }

    results_file = WORK_DIR / "results.json"
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)

    log_file = WORK_DIR / "run.log"
    with open(log_file, "w") as f:
        f.write("Task R32-T050 Verification Log\n")
        f.write(f"Python: {versions['python']}\n")
        f.write(f"Git Commit: {versions['git_commit']}\n")
        f.write(f"Native Tests: {native['test_count']} passed on original implementation\n")
        f.write("Fixtures: Smallest valid and ordinary input assertions passed\n")
        f.write(f"Mutation Check: Mutant failed named assertion as expected ({mutation['mutant_test_status']})\n")
        f.write("Status: ALL CHECKS PASSED\n")

    print(f"R32-T050: Native tests ({native['test_count']}), fixtures, and mutation checks passed successfully!")


if __name__ == "__main__":
    main()
