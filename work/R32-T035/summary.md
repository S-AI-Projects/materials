# R32-T035 verification notes

## Changes
- Added focused pytest coverage for `double(0)`, `double(7)`, and repeatability across an intervening call.
- Updated `check.py` to invoke the focused pytest test through the active Python interpreter, set the source import path, report the Python and pytest versions, and return pytest's exit status.

## Verification status
The tests and Ruff have not been confirmed as passing in this environment. The available sandbox interpreter was reported as Python 3.9.6, while the project requires Python >=3.14. The pinned development dependencies were also unavailable for installation. Run the verification script with Python 3.14 and the project's development dependencies installed before treating the checks as passed.
