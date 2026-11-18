# GitHub Copilot: Fly With Python at the Speed of Thought

Supplementing materials for the [tutorial on GitHub Copilot](https://realpython.com/github-copilot-python/) hosted on Real Python.

## Runnable Worked Example: Code Completion Mechanics

This project provides an automated, runnable worked example demonstrating GitHub Copilot code completion mechanics from input prompt through intermediate state transitions to final executable Python code.

### Preconditions & Anchors
- **Line 1:** Real Python tutorial baseline specification.
- **Line 3:** Tutorial link and supplementary materials reference.

### State Transition Pipeline
1. **Input Prompt (Step 1):** Raw comment and/or function signature (e.g. `# Check if number is even\ndef is_even(n):`).
2. **Intent Parsing (Step 2):** Extracts programming intent from prompt hints (`intent: even`).
3. **Intermediate Body Synthesis (Step 3):** Synthesizes logical body expressions (`['return n % 2 == 0']`).
4. **Syntax Verification & Assembly (Step 4):** Validates AST parsing and constructs formatted output function.

### Running the Example
Execute the standalone worked example:
```bash
python3 github-copilot/copilot_example.py
```

Run native unit tests:
```bash
python3 github-copilot/test_copilot_example.py
```

Run automated task check:
```bash
python3 work/R32-T027/check.py
```
