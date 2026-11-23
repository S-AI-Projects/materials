"""Basic input and output in Python greeter module.

Source line establishing preconditions:
- Line 1: `name = input("Please enter your name: ")` prompts user via stdin with
  prompt string 'Please enter your name: ' and reads string `name`.
- Line 2: `print("Hello", name, "and welcome!")` outputs formatted greeting to stdout
  with space separation and trailing newline.

Representative result:
  Input: "Alice"
  Output: "Hello Alice and welcome!\n"
  Prompt: "Please enter your name: "
"""

import sys
from typing import TextIO, Optional


def greet(name: str) -> str:
    """Pure transformation establishing expected greeting format.

    Preconditions:
      - Line 2: Format follows `print("Hello", name, "and welcome!")`.
    Parameters:
      name: Person's name string.
    Returns:
      Formatted greeting string without trailing newline.
    """
    return f"Hello {name} and welcome!"


def run_greeter(
    input_stream: Optional[TextIO] = None,
    output_stream: Optional[TextIO] = None,
    prompt: bool = True,
) -> str:
    """Executes the greeter I/O workflow under controlled external state.

    Preconditions:
      - Line 1: Prompts user and reads name from input stream.
      - Line 2: Prints greeting to output stream.

    Parameters:
      input_stream: Stream to read name from (defaults to sys.stdin).
      output_stream: Stream to write prompt/greeting to (defaults to sys.stdout).
      prompt: Whether to display prompt on output stream (mirrors input() prompt).

    Returns:
      The name that was entered.
    """
    in_stream = input_stream if input_stream is not None else sys.stdin
    out_stream = output_stream if output_stream is not None else sys.stdout

    prompt_text = "Please enter your name: "
    if prompt:
        out_stream.write(prompt_text)
        out_stream.flush()

    line = in_stream.readline()
    if line.endswith("\n"):
        name = line[:-1]
        if name.endswith("\r"):
            name = name[:-1]
    else:
        name = line

    greeting = greet(name)
    out_stream.write(greeting + "\n")
    out_stream.flush()

    return name


if __name__ == "__main__":
    name = input("Please enter your name: ")
    print("Hello", name, "and welcome!")
