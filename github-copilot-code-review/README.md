# How to Use GitHub Copilot Code Review in Pull Requests

This folder contains the supporting materials for the Real Python tutorial [How to Use GitHub Copilot Code Review in Pull Requests](https://realpython.com/github-copilot-code-review/).

Unzip the `pop-quiz.zip` archive, which contains a separate Git repository with the following branches:

- `main`
- `feature/player-names`
- `feature/player-names-final`

## Code Review & Differential Reference Testing

This project incorporates automated differential testing comparing the primary `github_copilot_code_review` engine with an independent reference oracle (`reference_code_review`).

### Precondition Anchors
- **Line 1:** Real Python tutorial baseline specification.
- **Line 5:** `pop-quiz.zip` source archive.
- **Line 7:** `main` base branch anchor.
- **Line 8:** `feature/player-names` initial feature branch anchor.
- **Line 9:** `feature/player-names-final` completed feature branch anchor.

### Supported Input Domains
- **Smallest Valid Input:** Empty diff string `""` on branch `main` yielding `status: APPROVE` and `findings: []`.
- **Ordinary Valid Input:** Feature changes on `feature/player-names` or `feature/player-names-final`.
- **Finding Triggers:** Explicit anti-patterns (unresolved `TODO`, debug print statements, bare `except:` clauses).

### Running Tests
Execute the native unit tests and differential comparison:
```bash
python3 github-copilot-code-review/test_code_review.py
```
Or run the automated task verification runner:
```bash
python3 work/R32-T023/check.py
```
