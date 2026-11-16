# Structural Pattern Matching in Python

This folder contains the code samples for the Real Python tutorial [Structural Pattern Matching in Python](https://realpython.com/structural-pattern-matching/).

## REPL Implementation & Regression Protection

`structural-pattern-matching/repl.py` provides an interactive Read-Eval-Print Loop (REPL) using structural pattern matching (`match`/`case` syntax introduced in Python 3.10 via PEP 634).

### Anchors and Preconditions

The REPL implementation relies on the following preconditions and anchors:

1. **Prompt Anchor (Line 5)**: `PROMPT = "\N{SNAKE} "` (`🐍 `) prompts the user for input.
2. **Commands Anchor (Line 6)**: `COMMANDS = ("help", "exit", "quit")` defines supported REPL commands.
3. **Banner Message (Line 10)**: Displays `'Type "help" for more information, "exit" or "quit" to finish.'` on startup.
4. **Command Matching (Lines 14–19)**:
   - Guarded by `case command if command.lower() in COMMANDS:` for case-insensitive matching.
   - `case "help":` prints `Python {sys.version}`.
   - `case "exit" | "quit":` breaks from the `while True:` loop to cleanly terminate the REPL.
5. **Expression Evaluation (Lines 20–23)**:
   - Validated via `valid(expression, "eval")`.
   - Evaluated with `_ = eval(expression)`.
   - Output condition: `if _ is not None:` ensures non-None results (including falsy results like `0`, `False`, `""`, `[]`) are displayed while suppressing `None`.
6. **Statement Execution (Lines 24–25)**:
   - Validated via `valid(statement, "exec")` and executed with `exec(statement)`.
7. **Syntax Fallback (Lines 26–27)**:
   - Catches unrecognized syntax and outputs `"Please type a command or valid Python"`.
8. **Exception Recovery (Lines 28–34)**:
   - `KeyboardInterrupt`: Prints `"\nKeyboardInterrupt"` and continues the loop.
   - `EOFError`: Prints a newline and exits cleanly.
   - General `Exception`: Prints traceback to `sys.stdout` and recovers.

### Regression & Mutation Testing

The test suite in `test_repl.py` and runner in `work/R32-T060/check.py` protect against regressions:
- **Return Condition**: Detects omission of `"quit"` from `case "exit" | "quit": break`.
- **Accumulation Condition**: Detects replacing `if _ is not None:` with truthiness `if _:`.
- **Boundary Comparison**: Detects omission of `.lower()` from `command.lower() in COMMANDS`.

## Installation

Create and activate a virtual environment:

```sh
$ python -m venv venv/
$ source venv/bin/activate
```

Install the required third-party dependencies:

```sh
(venv) $ python -m pip install -r requirements.txt
```

## Running Tests

Run focused unit tests:

```sh
python3 -m unittest discover -s structural-pattern-matching -p "test_*.py" -v
```

Run doctests:

```sh
python3 -m doctest -v structural-pattern-matching/repl.py
```

Run task verification runner:

```sh
python3 work/R32-T060/check.py
```
