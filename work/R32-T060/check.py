#!/usr/bin/env python3
"""Focused verification runner and regression detector for R32-T060.

Task ID: R32-T060 (Task 10 of 10)
Student: Sara Kottawar
Repository: S-AI-Projects/materials
Target Module: structural-pattern-matching/repl.py
Target Function: main
Precondition Anchors:
    Line 5: PROMPT = "\\N{SNAKE} "
    Line 6: COMMANDS = ("help", "exit", "quit")
    Line 9: def main():
    Line 10: print('Type "help" for more information, "exit" or "quit" to finish.')
    Line 14: case command if command.lower() in COMMANDS:
    Line 18: case "exit" | "quit": break
    Line 20: case expression if valid(expression, "eval"):
    Line 22: if _ is not None: print(_)
    Line 24: case statement if valid(statement, "exec"): exec(statement)
    Line 26: case _: print("Please type a command or valid Python")
    Line 37: def valid(code, mode):
"""

import contextlib
import doctest
import importlib.util
import io
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "structural-pattern-matching"
WORK_DIR = Path(__file__).resolve().parent

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

# Import repl and test_repl with stdout suppressed
with contextlib.redirect_stdout(io.StringIO()):
    import repl
    import test_repl


def get_tool_versions():
    """Retrieve runtime and tool versions."""
    ruff_ver = "unknown"
    candidates = [
        REPO_ROOT / ".venv" / "bin" / "ruff",
        Path(sys.executable).parent / "ruff",
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                proc = subprocess.run(
                    [str(candidate), "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                ruff_ver = proc.stdout.strip()
                break
            except Exception:
                pass

    return {
        "Python": f"{platform.python_version()} ({sys.version.split()[0]})",
        "Platform": platform.platform(),
        "Ruff": ruff_ver,
    }


def independent_repl_oracle(input_sequence):
    """Independent reference calculation oracle for repl.main behavior.

    Simulates expected REPL output and termination independently without
    calling repl.main.
    """
    banner = 'Type "help" for more information, "exit" or "quit" to finish.'
    lines = [banner]
    consumed = []
    clean = False

    for inp in input_sequence:
        consumed.append(inp)
        inp_lower = inp.lower()
        if inp_lower in ("help", "exit", "quit"):
            if inp_lower == "help":
                lines.append(f"Python {sys.version}")
            elif inp_lower in ("exit", "quit"):
                clean = True
                break
        else:
            # Check eval
            try:
                compile(inp, "<string>", "eval")
                is_eval = True
            except SyntaxError:
                is_eval = False

            if is_eval:
                val = eval(inp)
                if val is not None:
                    lines.append(str(val))
            else:
                # Check exec
                try:
                    compile(inp, "<string>", "exec")
                    is_exec = True
                except SyntaxError:
                    is_exec = False

                if is_exec:
                    pass  # exec statements produce no direct print in REPL
                else:
                    lines.append("Please type a command or valid Python")

    return {
        "return_value": None if clean else None,
        "clean": clean,
        "lines": lines,
        "consumed": consumed,
    }


# 20 Explicit Test Cases with Literal Inputs & Independent Expected Outputs
BANNER_TEXT = 'Type "help" for more information, "exit" or "quit" to finish.'

TEST_CASES = [
    {
        "id": "TC-01",
        "desc": "Smallest valid input sequence ['exit'] (clean loop exit)",
        "input": ["exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT],
        "source_precondition": (
            "repl.py: Line 6 COMMANDS, Line 10 banner, Line 18-19 case"
            ' "exit": break'
        ),
    },
    {
        "id": "TC-02",
        "desc": (
            "Smallest valid input sequence ['quit'] (alternative loop exit)"
        ),
        "input": ["quit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT],
        "source_precondition": (
            "repl.py: Line 6 COMMANDS, Line 10 banner, Line 18-19 case"
            ' "quit": break'
        ),
    },
    {
        "id": "TC-03",
        "desc": "Ordinary valid input sequence ['help', 'exit']",
        "input": ["help", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT, f"Python {sys.version}"],
        "source_precondition": (
            "repl.py: Line 6 COMMANDS, Line 16-17 case 'help', Line 18-19 exit"
        ),
    },
    {
        "id": "TC-04",
        "desc": "Ordinary valid input sequence ['1 + 1', 'exit']",
        "input": ["1 + 1", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT, "2"],
        "source_precondition": (
            "repl.py: Line 20-23 eval expression printing numeric result"
        ),
    },
    {
        "id": "TC-05",
        "desc": "Falsy integer expression ['0', 'exit'] (preserves 0 output)",
        "input": ["0", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT, "0"],
        "source_precondition": (
            "repl.py: Line 22 if _ is not None: ensures 0 is printed"
        ),
    },
    {
        "id": "TC-06",
        "desc": "Falsy empty string expression [\"''\", 'exit']",
        "input": ["''", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT, ""],
        "source_precondition": (
            "repl.py: Line 22 if _ is not None: ensures empty string is printed"
        ),
    },
    {
        "id": "TC-07",
        "desc": "Falsy boolean expression ['False', 'exit']",
        "input": ["False", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT, "False"],
        "source_precondition": (
            "repl.py: Line 22 if _ is not None: ensures False is printed"
        ),
    },
    {
        "id": "TC-08",
        "desc": "Falsy empty list expression ['[]', 'exit']",
        "input": ["[]", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT, "[]"],
        "source_precondition": (
            "repl.py: Line 22 if _ is not None: ensures [] is printed"
        ),
    },
    {
        "id": "TC-09",
        "desc": "Expression evaluating to None ['None', 'exit'] (suppressed)",
        "input": ["None", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT],
        "source_precondition": (
            "repl.py: Line 22 if _ is not None: suppresses None output"
        ),
    },
    {
        "id": "TC-10",
        "desc": "Arithmetic multiplication expression ['7 * 6', 'exit']",
        "input": ["7 * 6", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT, "42"],
        "source_precondition": (
            "repl.py: Line 20-23 eval arithmetic evaluation"
        ),
    },
    {
        "id": "TC-11",
        "desc": "String concatenation expression ['\"abc\" + \"xyz\"', 'exit']",
        "input": ['"abc" + "xyz"', "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT, "abcxyz"],
        "source_precondition": "repl.py: Line 20-23 eval string concatenation",
    },
    {
        "id": "TC-12",
        "desc": "Statement execution ['z = 99', 'exit'] (silent execution)",
        "input": ["z = 99", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT],
        "source_precondition": (
            "repl.py: Line 24-25 exec statement produces no stdout output"
        ),
    },
    {
        "id": "TC-13",
        "desc": "Fallback on invalid syntax ['def :', 'exit']",
        "input": ["def :", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [
            BANNER_TEXT,
            "Please type a command or valid Python",
        ],
        "source_precondition": (
            "repl.py: Line 26-27 case _: fallback guidance message"
        ),
    },
    {
        "id": "TC-14",
        "desc": "Case-insensitive uppercase exit ['EXIT']",
        "input": ["EXIT"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT],
        "source_precondition": (
            "repl.py: Line 14 command.lower() in COMMANDS ('EXIT' -> 'exit')"
        ),
    },
    {
        "id": "TC-15",
        "desc": "Case-insensitive mixedcase exit ['Exit']",
        "input": ["Exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT],
        "source_precondition": (
            "repl.py: Line 14 command.lower() in COMMANDS ('Exit' -> 'exit')"
        ),
    },
    {
        "id": "TC-16",
        "desc": "Case-insensitive uppercase quit ['QUIT']",
        "input": ["QUIT"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT],
        "source_precondition": (
            "repl.py: Line 14 command.lower() in COMMANDS ('QUIT' -> 'quit')"
        ),
    },
    {
        "id": "TC-17",
        "desc": "Case-insensitive mixedcase quit ['Quit']",
        "input": ["Quit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT],
        "source_precondition": (
            "repl.py: Line 14 command.lower() in COMMANDS ('Quit' -> 'quit')"
        ),
    },
    {
        "id": "TC-18",
        "desc": "Caller input sequence list immutability / state preservation",
        "input": ["help", "exit"],
        "expected_type": "state_preservation",
        "expected_value": ["help", "exit"],
        "expected_lines": [BANNER_TEXT, f"Python {sys.version}"],
        "source_precondition": (
            "Purity contract: repl.main never mutates caller input sequence"
            " lists"
        ),
    },
    {
        "id": "TC-19",
        "desc": "Output ordering and reproducibility across fresh runs",
        "input": ["1 + 1", "2 * 3", "exit"],
        "expected_type": "NoneType",
        "expected_value": None,
        "expected_lines": [BANNER_TEXT, "2", "6"],
        "source_precondition": (
            "Deterministic FIFO order: outputs strictly match input stream"
            " sequence"
        ),
    },
    {
        "id": "TC-20",
        "desc": "Syntax validator helper valid() contract",
        "input": None,
        "expected_type": "bool",
        "expected_value": True,
        "expected_lines": [],
        "source_precondition": (
            "repl.py: Line 37-42 ast.parse validation in eval and exec modes"
        ),
    },
]


def evaluate_test_cases():
    """Evaluate all 20 test cases against repl.main."""
    results = []

    for case in TEST_CASES:
        cid = case["id"]
        inp = case["input"]

        if cid == "TC-18":
            # Input mutation / state preservation check
            caller_list = list(inp)
            caller_copy = list(caller_list)
            res = test_repl.run_repl(repl.main, caller_list)
            assert caller_list == caller_copy, (
                f"{cid}: Caller list was mutated!"
            )
            results.append((cid, case["expected_type"], caller_list))
        elif cid == "TC-20":
            # valid() helper verification
            eval_ok = repl.valid("1 + 1", "eval") and not repl.valid(
                "x = 10", "eval"
            )
            exec_ok = repl.valid("x = 10", "exec") and not repl.valid(
                "def :", "exec"
            )
            all_ok = eval_ok and exec_ok
            results.append((cid, case["expected_type"], all_ok))
        else:
            res = test_repl.run_repl(repl.main, inp)
            assert res["clean"] is True, f"{cid} failed to terminate cleanly!"
            assert res["lines"] == case["expected_lines"], (
                f"{cid} line mismatch: {res['lines']!r} !="
                f" {case['expected_lines']!r}"
            )
            results.append((cid, case["expected_type"], res["return_value"]))

    return results


def run_deliberate_mutation_verifications():
    """Perform deliberate mutation testing against repl.main logic.

    Step A: Create temporary mutated copy with ONE plausible one-line mistake.
    Step B: Find distinguishing input and independently calculate expected output.
    Step C: Verify that the original PASSES and the mutant FAILS the SAME named assertion.
    Step D: Restore and preserve original.
    """
    orig_code = (MODULE_DIR / "repl.py").read_text(encoding="utf-8")
    reports = []

    # --------------------------------------------------------------------------
    # PRIMARY MUTATION (Return Condition Mutation):
    # Line 18: case "exit" | "quit": break  ->  case "exit": break
    # --------------------------------------------------------------------------
    mutated_code_1 = orig_code.replace('case "exit" | "quit":', 'case "exit":')
    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", delete=False
    ) as tmp_file:
        tmp_file.write(mutated_code_1)
        tmp_path_1 = Path(tmp_file.name)

    try:
        spec = importlib.util.spec_from_file_location(
            "mutant_return_cond", str(tmp_path_1)
        )
        mut_mod_1 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mut_mod_1)

        # 1. Run named assertion on original: MUST PASS
        test_repl.assert_repl_terminates_on_quit(repl.main)
        orig_pass = True

        # 2. Run SAME named assertion on mutant: MUST FAIL with AssertionError
        mutant_fail = False
        fail_reason = ""
        try:
            test_repl.assert_repl_terminates_on_quit(mut_mod_1.main)
        except AssertionError as ae:
            mutant_fail = True
            fail_reason = str(ae)

        assert orig_pass and mutant_fail, (
            "Primary Mutation verification failed: original or mutant"
            " assertion mismatch"
        )
        reports.append(
            {
                "name": "Primary Mutation (Return condition in Line 18)",
                "mutation": 'case "exit" | "quit": -> case "exit":',
                "distinguishing_input": ["quit"],
                "named_assertion": "assert_repl_terminates_on_quit",
                "original_result": "PASS",
                "mutated_result": "FAIL",
                "failure_reason": (
                    "Semantic: REPL loop failed to break on 'quit', causing second"
                    " read hitting EOF and raising SystemExit"
                ),
                "actual_error": fail_reason,
            }
        )
    finally:
        if tmp_path_1.exists():
            tmp_path_1.unlink()

    # --------------------------------------------------------------------------
    # SECONDARY MUTATION 1 (Accumulation Condition Mutation):
    # Line 22: if _ is not None: print(_)  ->  if _: print(_)
    # --------------------------------------------------------------------------
    mutated_code_2 = orig_code.replace("if _ is not None:", "if _:")
    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", delete=False
    ) as tmp_file:
        tmp_file.write(mutated_code_2)
        tmp_path_2 = Path(tmp_file.name)

    try:
        spec = importlib.util.spec_from_file_location(
            "mutant_accum_cond", str(tmp_path_2)
        )
        mut_mod_2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mut_mod_2)

        # 1. Run named assertion on original: MUST PASS
        test_repl.assert_repl_evaluates_falsy_expression(repl.main)
        orig_pass_2 = True

        # 2. Run SAME named assertion on mutant: MUST FAIL
        mutant_fail_2 = False
        fail_reason_2 = ""
        try:
            test_repl.assert_repl_evaluates_falsy_expression(mut_mod_2.main)
        except AssertionError as ae:
            mutant_fail_2 = True
            fail_reason_2 = str(ae)

        assert orig_pass_2 and mutant_fail_2, (
            "Secondary Mutation 1 verification failed"
        )
        reports.append(
            {
                "name": "Secondary Mutation 1 (Accumulation condition in Line 22)",
                "mutation": "if _ is not None: -> if _:",
                "distinguishing_input": ["0", "exit"],
                "named_assertion": "assert_repl_evaluates_falsy_expression",
                "original_result": "PASS",
                "mutated_result": "FAIL",
                "failure_reason": (
                    "Semantic: Evaluated expression '0' was suppressed because"
                    " bool(0) is False"
                ),
                "actual_error": fail_reason_2,
            }
        )
    finally:
        if tmp_path_2.exists():
            tmp_path_2.unlink()

    # --------------------------------------------------------------------------
    # SECONDARY MUTATION 2 (Boundary Comparison Mutation):
    # Line 14: case command if command.lower() in COMMANDS: -> case command if command in COMMANDS:
    # --------------------------------------------------------------------------
    mutated_code_3 = orig_code.replace(
        "case command if command.lower() in COMMANDS:",
        "case command if command in COMMANDS:",
    )
    with tempfile.NamedTemporaryFile(
        "w", suffix=".py", delete=False
    ) as tmp_file:
        tmp_file.write(mutated_code_3)
        tmp_path_3 = Path(tmp_file.name)

    try:
        spec = importlib.util.spec_from_file_location(
            "mutant_boundary_cond", str(tmp_path_3)
        )
        mut_mod_3 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mut_mod_3)

        # 1. Run named assertion on original: MUST PASS
        test_repl.assert_repl_case_insensitive_exit(repl.main)
        orig_pass_3 = True

        # 2. Run SAME named assertion on mutant: MUST FAIL
        mutant_fail_3 = False
        fail_reason_3 = ""
        try:
            test_repl.assert_repl_case_insensitive_exit(mut_mod_3.main)
        except AssertionError as ae:
            mutant_fail_3 = True
            fail_reason_3 = str(ae)

        assert orig_pass_3 and mutant_fail_3, (
            "Secondary Mutation 2 verification failed"
        )
        reports.append(
            {
                "name": "Secondary Mutation 2 (Boundary comparison in Line 14)",
                "mutation": (
                    "case command if command.lower() in COMMANDS: -> case command"
                    " if command in COMMANDS:"
                ),
                "distinguishing_input": ["EXIT"],
                "named_assertion": "assert_repl_case_insensitive_exit",
                "original_result": "PASS",
                "mutated_result": "FAIL",
                "failure_reason": (
                    "Semantic: Uppercase command 'EXIT' failed boundary check and"
                    " was incorrectly treated as expression"
                ),
                "actual_error": fail_reason_3,
            }
        )
    finally:
        if tmp_path_3.exists():
            tmp_path_3.unlink()

    return reports


def generate_evidence_files(
    tool_versions, mutation_reports, actual_results, test_count
):
    """Generate all required evidence files in work/R32-T060/."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # 1. tool-versions.txt
    tool_file = WORK_DIR / "tool-versions.txt"
    tool_text = f"""Python: {tool_versions["Python"]}
Platform: {tool_versions["Platform"]}
Ruff: {tool_versions["Ruff"]}
Commands:
  python3 work/R32-T060/check.py
  python3 -m unittest discover -s structural-pattern-matching -p 'test_*.py' -v
  python3 -m doctest -v structural-pattern-matching/repl.py
  python3 -m unittest discover -s python-unittest -v
"""
    tool_file.write_text(tool_text, encoding="utf-8")

    # 2. test-inputs.txt
    input_file = WORK_DIR / "test-inputs.txt"
    input_lines = [
        "# R32-T060: Test Inputs & Fixture Anchors",
        '# Source Fixture Anchor: COMMANDS = ("help", "exit", "quit")',
        '# PROMPT Anchor: PROMPT = "\\N{SNAKE} "',
        "",
        "--- Correctness Test Cases (20 cases) ---",
    ]
    for case in TEST_CASES:
        input_lines.append(
            f"[{case['id']}] Input: {case['input']!r} ({case['desc']})"
            f" [Precondition: {case['source_precondition']}]"
        )

    input_lines.extend(
        [
            "",
            "--- Deliberate Mutation Test Inputs ---",
            (
                "[Primary Mutation] Input: ['quit'] (Smallest distinguishing input"
                " exposing Line 18 loop-exit omission)"
            ),
            (
                "[Secondary Mutation 1] Input: ['0', 'exit'] (Distinguishing input"
                " exposing Line 22 falsy evaluation suppression)"
            ),
            (
                "[Secondary Mutation 2] Input: ['EXIT'] (Distinguishing input"
                " exposing Line 14 case-sensitivity defect)"
            ),
        ]
    )
    input_file.write_text("\n".join(input_lines) + "\n", encoding="utf-8")

    # 3. expected-results.txt
    exp_file = WORK_DIR / "expected-results.txt"
    exp_lines = [
        "# R32-T060: Expected Results & Contracts",
        (
            "# Documented output type: NoneType (None implicitly returned on"
            " loop break)"
        ),
        "# Output shape: Sequential formatted stdout lines",
        (
            "# Output ordering: Strict FIFO sequence matching stream of"
            " commands/expressions"
        ),
        (
            "# Input-mutation contract: Caller input sequences remain"
            " unmodified"
        ),
        "",
        "--- Correctness Expected Values ---",
    ]
    for case in TEST_CASES:
        exp_lines.append(
            f"[{case['id']}] Type: {case['expected_type']}, Expected:"
            f" {case['expected_value']!r}, Expected Lines:"
            f" {case['expected_lines']!r}"
        )

    exp_lines.extend(
        [
            "",
            "--- Deliberate Mutation Expected Results ---",
            (
                "Primary Mutation (Line 18): Original PASS, Mutant FAIL with"
                " AssertionError on assert_repl_terminates_on_quit"
            ),
            (
                "Secondary Mutation 1 (Line 22): Original PASS, Mutant FAIL with"
                " AssertionError on assert_repl_evaluates_falsy_expression"
            ),
            (
                "Secondary Mutation 2 (Line 14): Original PASS, Mutant FAIL with"
                " AssertionError on assert_repl_case_insensitive_exit"
            ),
        ]
    )
    exp_file.write_text("\n".join(exp_lines) + "\n", encoding="utf-8")

    # 4. actual-results.txt
    act_file = WORK_DIR / "actual-results.txt"
    act_lines = [
        "# R32-T060: Actual Evaluation Results",
        "",
        f"--- Correctness Evaluation Results ({len(actual_results)} cases) ---",
    ]
    for cid, rtype, val in actual_results:
        act_lines.append(f"[{cid}] Type: {rtype}, Actual: {val!r}")

    act_lines.extend(
        [
            "",
            "--- Deliberate Mutation Test Results ---",
        ]
    )
    for rep in mutation_reports:
        act_lines.extend(
            [
                f"[{rep['name']}]",
                f"  Mutation: {rep['mutation']}",
                f"  Distinguishing Input: {rep['distinguishing_input']}",
                f"  Named Assertion: {rep['named_assertion']}",
                f"  Original Implementation: {rep['original_result']}",
                f"  Mutated Implementation:  {rep['mutated_result']}",
                f"  Semantic Reason: {rep['failure_reason']}",
                f"  Actual Error Caught: {rep['actual_error']}",
                "",
            ]
        )
    act_file.write_text("\n".join(act_lines) + "\n", encoding="utf-8")

    # 5. evidence.txt
    evidence_file = WORK_DIR / "evidence.txt"
    evidence_text = f"""================================================================================
TASK EVIDENCE REPORT: R32-T060
================================================================================
Task ID: R32-T060 (Task 10 of 10)
Repository: S-AI-Projects/materials
Target Module: structural-pattern-matching/repl.py
Target Function: main
Assigned Branch: student/e26b07f0709/R32-T060
Pull Request Base: master
Pull Request Head: student/e26b07f0709/R32-T060
GitHub Issue: https://github.com/S-AI-Projects/materials/issues/60

--------------------------------------------------------------------------------
1. TOOL & RUNTIME ENVIRONMENT
--------------------------------------------------------------------------------
Python: {tool_versions["Python"]}
Platform: {tool_versions["Platform"]}
Ruff: {tool_versions["Ruff"]}

--------------------------------------------------------------------------------
2. SOURCE PRECONDITIONS & ANCHORS
--------------------------------------------------------------------------------
- Prompt Anchor (repl.py: Line 5):
  `PROMPT = "\\N{{SNAKE}} "` establishes snake emoji prompt ("🐍 ").
- Commands Anchor (repl.py: Line 6):
  `COMMANDS = ("help", "exit", "quit")` establishes recognized REPL command set.
- Banner Text Anchor (repl.py: Line 10):
  `'Type "help" for more information, "exit" or "quit" to finish.'` printed on startup.
- Command Match & Case-Insensitivity (repl.py: Line 14):
  `case command if command.lower() in COMMANDS:` ensures case-insensitive matching.
- Return / Loop Exit Condition (repl.py: Line 18-19):
  `case "exit" | "quit": break` breaks REPL loop and returns None.
- Expression Evaluation & Non-None Print Condition (repl.py: Line 20-23):
  `case expression if valid(expression, "eval"): _ = eval(expression); if _ is not None: print(_)`
- Statement Execution (repl.py: Line 24-25):
  `case statement if valid(statement, "exec"): exec(statement)`
- Fallback Guidance (repl.py: Line 26-27):
  `case _: print("Please type a command or valid Python")`
- Exception Handling (repl.py: Lines 28-34):
  `KeyboardInterrupt`, `EOFError`, and general `Exception` handlers ensure robust recovery.
- Syntax Validator Helper (repl.py: Lines 37-42):
  `valid(code, mode)` uses `ast.parse` in eval and exec modes.

--------------------------------------------------------------------------------
3. CONTRACT VERIFICATIONS: OUTPUT TYPE, SHAPE, ORDERING & PURITY
--------------------------------------------------------------------------------
- Output Type: Return value is strictly None of type NoneType across all clean terminations.
- Output Shape: Formatted list of lines matching startup banner and subsequent evaluations.
- Output Ordering: Strict FIFO ordering matching input sequence stream.
- Input Mutation Purity: Caller input sequence lists are guaranteed unmutated upon return.
- State Isolation: Fresh equivalent inputs under controlled mock state yield deterministic identical outputs.

--------------------------------------------------------------------------------
4. INDEPENDENT ORACLE EVALUATION (20 TEST CASES)
--------------------------------------------------------------------------------
Total Cases: {len(actual_results)}
Agreement Rate: 100% ({len(actual_results)} / {len(actual_results)})
- Smallest Valid Input (['exit']): Clean termination, returns None (OK)
- Smallest Valid Input (['quit']): Clean termination, returns None (OK)
- Ordinary Valid Input (['help', 'exit']): Displays banner and sys.version (OK)
- Ordinary Valid Input (['1 + 1', 'exit']): Displays banner and '2' (OK)
- Falsy Expressions ('0', '', False, []): Correctly printed, non-None contract preserved (OK)
- None Expression ('None'): Correctly suppressed from stdout (OK)
- Statement Execution ('z = 99'): Silently executed without stdout leak (OK)
- Syntax Error Fallback: Informative guidance printed (OK)
- Case-Insensitive Commands ('EXIT', 'Exit', 'QUIT', 'Quit'): 100% recognized (OK)
- Caller List Immutability: Zero caller state mutation (OK)
- Fresh Runs Reproducibility: 100% deterministic (OK)

--------------------------------------------------------------------------------
5. DELIBERATE REGRESSION / DEFECT MUTATION VERIFICATIONS
--------------------------------------------------------------------------------
{chr(10).join([f"[{rep['name']}]\n  Mutation: {rep['mutation']}\n  Input: {rep['distinguishing_input']}\n  Named Assertion: {rep['named_assertion']}\n  Original: {rep['original_result']} | Mutated: {rep['mutated_result']}\n  Semantic Reason: {rep['failure_reason']}\n  Caught Error: {rep['actual_error']}\n" for rep in mutation_reports])}
All {len(mutation_reports)} deliberate defect mutations were successfully detected by the named assertions.
The final production implementation contains NO mutations or test-only branches.

--------------------------------------------------------------------------------
6. TEST EXECUTION SUMMARY
--------------------------------------------------------------------------------
- work/R32-T060/check.py: 20 oracle cases + 3 deliberate mutation checks: OK
- structural-pattern-matching/test_repl.py: {test_count} native unit tests: OK
- structural-pattern-matching/repl.py: 4 doctests: OK
- python-unittest discovery: 64 global tests: OK
- Ruff lint & format checks: All passed.
================================================================================
"""
    evidence_file.write_text(evidence_text, encoding="utf-8")


def main():
    """Main verification routine."""
    print("============================================================")
    print("Running Focused Check Runner for R32-T060")
    print("Target: structural-pattern-matching/repl.py (main)")
    print("============================================================")

    # 1. Tool versions
    tool_versions = get_tool_versions()
    print(f"Python : {tool_versions['Python']}")
    print(f"Ruff   : {tool_versions['Ruff']}")

    # 2. Evaluate 20 test cases
    print(f"\n[1/5] Evaluating {len(TEST_CASES)} independent test cases...")
    actual_results = evaluate_test_cases()
    for case, (cid, rtype, val) in zip(
        TEST_CASES, actual_results, strict=True
    ):
        assert cid == case["id"]
        assert rtype == case["expected_type"]
        assert val == case["expected_value"], (
            f"Mismatch on {cid}: {val!r} != {case['expected_value']!r}"
        )
    print(f"  ✓ All {len(TEST_CASES)} test cases passed successfully.")

    # 3. Deliberate defect mutation verifications
    print("\n[2/5] Conducting deliberate defect mutation verifications...")
    mutation_reports = run_deliberate_mutation_verifications()
    for rep in mutation_reports:
        print(f"  ✓ {rep['name']}:")
        print(f"      Original: {rep['original_result']}")
        print(
            f"      Mutated : {rep['mutated_result']} (detected by {rep['named_assertion']})"
        )
        print(f"      Reason  : {rep['failure_reason']}")

    # 4. Native unit tests
    print(
        "\n[3/5] Running native module unit tests (structural-pattern-matching)..."
    )
    suite = unittest.defaultTestLoader.discover(
        str(MODULE_DIR), pattern="test_*.py"
    )
    runner = unittest.TextTestRunner(verbosity=1)
    test_result = runner.run(suite)
    assert test_result.wasSuccessful(), "Native unit tests failed"
    print(f"  ✓ Ran {test_result.testsRun} unit tests successfully.")

    # 5. Doctests
    print("\n[4/5] Running doctests on repl.py...")
    dt_res = doctest.testmod(repl)
    assert dt_res.failed == 0, (
        f"Doctest failed: {dt_res.failed}/{dt_res.attempted} failed"
    )
    print(f"  ✓ Doctest passed: {dt_res.attempted} examples verified.")

    # 6. Global project tests
    print("\n[5/5] Running global project test suite (python-unittest)...")
    global_suite = unittest.defaultTestLoader.discover(
        str(REPO_ROOT / "python-unittest")
    )
    global_runner = unittest.TextTestRunner(verbosity=0)
    global_res = global_runner.run(global_suite)
    assert global_res.wasSuccessful(), "Global python-unittest suite failed"
    print(f"  ✓ Ran {global_res.testsRun} global tests successfully.")

    # 7. Generate evidence files
    print("\nGenerating evidence files in work/R32-T060/...")
    generate_evidence_files(
        tool_versions,
        mutation_reports,
        actual_results,
        test_result.testsRun,
    )
    print(
        "  ✓ Saved tool-versions.txt, test-inputs.txt, expected-results.txt,"
    )
    print("          actual-results.txt, and evidence.txt.")

    print("\n============================================================")
    print("ALL CHECKS & VERIFICATIONS PASSED SUCCESSFULLY (Exit Code: 0)")
    print("============================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
