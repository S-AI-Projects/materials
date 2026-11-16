"""Simple Python Read-Eval-Print Loop (REPL) using structural pattern matching.

This module demonstrates Python structural pattern matching (PEP 634)
within an interactive Read-Eval-Print Loop.

Preconditions established by source:
    Line 5: PROMPT = "\\N{SNAKE} "
    Line 6: COMMANDS = ("help", "exit", "quit")
    Line 9: def main(): - Primary interactive REPL entry point
    Line 10: Startup banner printed to sys.stdout
    Line 14: Command match guarded by command.lower() in COMMANDS
    Line 18: Exit condition matching "exit" | "quit" to break REPL loop
    Line 20: Expression evaluation matching valid eval expressions
    Line 22: Result printed if _ is not None
    Line 24: Statement execution matching valid exec statements
    Line 26: Fallback for invalid commands / syntax
    Line 28: KeyboardInterrupt handling
    Line 30: EOFError handling
    Line 33: Exception traceback reporting
"""

import ast
import sys
import traceback

PROMPT = "\N{SNAKE} "
COMMANDS = ("help", "exit", "quit")


def main():
    """Run the interactive Read-Eval-Print Loop (REPL).

    Continuously prompts the user using PROMPT ("🐍 ") and matches input against:
    - Builtin commands: "help", "exit", "quit" (case-insensitive)
    - Valid Python expressions evaluated via eval()
    - Valid Python statements executed via exec()
    - Fallback message for invalid syntax or unknown commands

    Output type and shape:
        - Return value: None (implicitly returned when loop breaks)
        - Side effects: Outputs banner and evaluation results to sys.stdout
        - Ordering: Strict sequential FIFO order matching input stream

    Preconditions:
        Line 6: COMMANDS = ("help", "exit", "quit")
        Line 10: Banner 'Type "help" for more information, "exit" or "quit" to finish.'
        Line 14: case command if command.lower() in COMMANDS:
        Line 18: case "exit" | "quit": break
    """
    print('Type "help" for more information, "exit" or "quit" to finish.')
    while True:
        try:
            match input(PROMPT):
                case command if command.lower() in COMMANDS:
                    match command.lower():
                        case "help":
                            print(f"Python {sys.version}")
                        case "exit" | "quit":
                            break
                case expression if valid(expression, "eval"):
                    _ = eval(expression)
                    if _ is not None:
                        print(_)
                case statement if valid(statement, "exec"):
                    exec(statement)
                case _:
                    print("Please type a command or valid Python")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
        except EOFError:
            print()
            exit()
        except Exception:
            traceback.print_exc(file=sys.stdout)


def valid(code, mode):
    """Check whether code is syntactically valid in given mode ('eval' or 'exec').

    Examples:
        >>> valid("1 + 1", "eval")
        True
        >>> valid("x = 10", "eval")
        False
        >>> valid("x = 10", "exec")
        True
        >>> valid("invalid @@ syntax", "eval")
        False
    """
    try:
        ast.parse(code, mode=mode)
        return True
    except SyntaxError:
        return False


if __name__ == "__main__":
    main()
