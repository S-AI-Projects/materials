# R32-T032 — Test Results

Command: `python3 work/R32-T032/check.py`

Result: 3 tests passed.

| Case | Expected | Actual |
|---|---|---|
| Empty ResultsContainer | No output | No output |
| One Python job | Exact four-line job output | Matched |
| Mixed-case Python + Java job | Python job only | Matched |

HTTP requests were mocked; no live network request was made.
Environment warning: urllib3 emitted a NotOpenSSLWarning because this Python uses macOS LibreSSL. Tests still passed.
