# R32-T037 check results

- Focused tests passed: 4
- Required command: python3 work/R32-T037/check.py
- Pytest invocation in the validation environment: /opt/pyvenv/bin/python3 -m pytest -q work/R32-T037/test_space_rocks_example.py
- The tests stub Pygame, models, and utils imports to isolate the named game module; they do not open a window or load assets.
- The README example is executed by a test and its complete output is compared with a literal expected string.
- Ruff was not installed in the isolated validation environment; repository requirement is ruff==0.14.1. Ruff should also be checked in the project checkout.
- Actual pytest output is saved in test-output.txt; environment details are saved in tool-versions.txt.
