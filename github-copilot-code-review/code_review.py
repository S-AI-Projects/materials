"""GitHub Copilot Code Review Engine and Differential Reference Model.

Provides differential testing between the production reviewer and an independent reference oracle.
Preconditions anchored in README.md:
- Line 1: Real Python tutorial 'How to Use GitHub Copilot Code Review in Pull Requests'
- Line 5: pop-quiz.zip repository archive
- Line 7: 'main' branch
- Line 8: 'feature/player-names' branch
- Line 9: 'feature/player-names-final' branch
"""

from typing import Any, Dict, List

# Precondition anchors from README.md
ARCHIVE_NAME = "pop-quiz.zip"
BRANCH_MAIN = "main"
BRANCH_PLAYER_NAMES = "feature/player-names"
BRANCH_PLAYER_NAMES_FINAL = "feature/player-names-final"
SUPPORTED_BRANCHES = (BRANCH_MAIN, BRANCH_PLAYER_NAMES, BRANCH_PLAYER_NAMES_FINAL)


def github_copilot_code_review(branch: str, diff_text: str = "") -> Dict[str, Any]:
    """Simulate GitHub Copilot Code Review on pull request changes.

    Args:
        branch: Target PR branch name.
        diff_text: Unified diff or patch text.

    Returns:
        Structured review dictionary containing status, findings, and metrics.
    """
    if not isinstance(branch, str):
        raise TypeError("Branch must be a string")
    if not isinstance(diff_text, str):
        raise TypeError("diff_text must be a string")

    # Evaluate diff lines
    lines = [line.strip() for line in diff_text.splitlines() if line.strip()]
    findings: List[str] = []

    for line in lines:
        if line.startswith("+") and not line.startswith("+++"):
            code = line[1:].strip()
            # Detect common anti-patterns flagged by review
            if "TODO" in code:
                findings.append(f"Unresolved TODO detected: {code}")
            elif "print(" in code and "debug" in code.lower():
                findings.append(f"Debug print statement should be removed: {code}")
            elif "except:" in code:
                findings.append(f"Bare except clause should specify exception type: {code}")

    # Determine status
    if not findings:
        status = "APPROVE"
        summary = "No issues detected. Code meets quality standards."
    else:
        status = "REQUEST_CHANGES"
        summary = f"Identified {len(findings)} potential improvement(s)."

    return {
        "branch": branch,
        "status": status,
        "findings": findings,
        "finding_count": len(findings),
        "summary": summary,
    }


def reference_code_review(branch: str, diff_text: str = "") -> Dict[str, Any]:
    """Independent reference oracle for code review validation.

    Independently calculates expected review verdicts and findings
    without sharing internal state with the primary reviewer.
    """
    if not isinstance(branch, str) or not isinstance(diff_text, str):
        raise TypeError("Invalid argument types")

    findings = []
    for raw_line in diff_text.splitlines():
        line = raw_line.strip()
        if len(line) > 1 and line[0] == "+" and line[1] != "+":
            content = line[1:].strip()
            if "TODO" in content:
                findings.append(f"Unresolved TODO detected: {content}")
            elif "print(" in content and "debug" in content.lower():
                findings.append(f"Debug print statement should be removed: {content}")
            elif "except:" in content:
                findings.append(f"Bare except clause should specify exception type: {content}")

    return {
        "branch": branch,
        "status": "REQUEST_CHANGES" if findings else "APPROVE",
        "findings": findings,
        "finding_count": len(findings),
        "summary": (
            f"Identified {len(findings)} potential improvement(s)."
            if findings
            else "No issues detected. Code meets quality standards."
        ),
    }
