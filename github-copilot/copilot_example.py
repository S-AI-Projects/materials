"""Runnable worked example demonstrating GitHub Copilot code completion mechanics.

Tracks code completion step-by-step from input prompt through intermediate state transitions
to the final synthesized and executable Python code.

Preconditions established in README.md:
- Line 1: Real Python tutorial 'GitHub Copilot: Fly With Python at the Speed of Thought'
- Line 3: Supplementing materials and tutorial reference
"""

import ast
from typing import Any, Dict, List


def copilot_complete(prompt: str) -> Dict[str, Any]:
    """Execute Copilot-style code completion tracking all intermediate states.

    Step 1: Input Prompt Normalization
    Step 2: Intent Parsing & Context Assembly
    Step 3: Synthesis of Intermediate Body Lines
    Step 4: Syntax Verification & Final Code Generation

    >>> result = copilot_complete("# check if even\\ndef is_even(n):")
    >>> result["status"]
    'SUCCESS'
    >>> result["completed_code"].strip()
    'def is_even(n):\\n    return n % 2 == 0'
    """
    if not isinstance(prompt, str):
        raise TypeError("Prompt must be a string")

    # Step 1: Input Prompt Normalization
    normalized_prompt = prompt.strip()
    lines = [line.strip() for line in normalized_prompt.splitlines() if line.strip()]

    # Step 2: Intent Extraction
    comment_hints: List[str] = []
    signature = ""
    for line in lines:
        if line.startswith("#"):
            comment_hints.append(line[1:].strip().lower())
        elif line.startswith("def ") or line.startswith("class "):
            signature = line

    intent = "pass"
    hint_text = " ".join(comment_hints)
    if "even" in hint_text or "is_even" in signature:
        intent = "even"
    elif "odd" in hint_text or "is_odd" in signature:
        intent = "odd"
    elif "fibonacci" in hint_text or "fib" in signature:
        intent = "fibonacci"
    elif "reverse" in hint_text or "reverse" in signature:
        intent = "reverse"

    # Step 3: Intermediate Body Synthesis
    if intent == "even":
        body_lines = ["return n % 2 == 0"]
    elif intent == "odd":
        body_lines = ["return n % 2 != 0"]
    elif intent == "fibonacci":
        body_lines = [
            "if n <= 1:",
            "    return n",
            "return fib(n - 1) + fib(n - 2)",
        ]
    elif intent == "reverse":
        body_lines = ["return s[::-1]"]
    else:
        body_lines = ["pass"]

    # Step 4: Final Code Assembly & Verification
    if signature:
        indented_body = "\n".join("    " + line for line in body_lines)
        completed_code = f"{signature}\n{indented_body}"
    else:
        completed_code = "\n".join(body_lines)

    # Validate syntax of generated Python code
    try:
        ast.parse(completed_code)
        syntax_valid = True
    except SyntaxError:
        syntax_valid = False

    return {
        "step1_input": prompt,
        "step2_intent": intent,
        "step3_body_lines": body_lines,
        "step4_syntax_valid": syntax_valid,
        "completed_code": completed_code,
        "status": "SUCCESS" if syntax_valid else "SYNTAX_ERROR",
    }


def main():
    """Run demonstration worked example."""
    sample_prompt = "# Check if number is even\ndef is_even(n):"
    res = copilot_complete(sample_prompt)
    print("=== GitHub Copilot Code Completion Worked Example ===")
    print(f"Input Prompt:\n{res['step1_input']}\n")
    print(f"Detected Intent: {res['step2_intent']}")
    print(f"Intermediate Body Lines: {res['step3_body_lines']}")
    print(f"Syntax Validated: {res['step4_syntax_valid']}\n")
    print(f"Final Completed Code:\n{res['completed_code']}")


if __name__ == "__main__":
    main()
