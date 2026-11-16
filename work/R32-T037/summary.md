# R32-T037 summary

Added a deterministic SpaceRocks worked example to the final-source README.
It shows the smallest empty-list state and a bullet collision with a terminal
(size-1) asteroid. The decisive transition is the removal of the colliding
objects, followed by the win check while the spaceship remains active.

The focused runner checks source-line preconditions, both state transitions,
and the exact displayed output from the README code block.

Run from the repository root:

```bash
python3 work/R32-T037/check.py
```

See inputs-and-expected.md, results.md, test-output.txt, and
tool-versions.txt for fixtures, expected values, actual output, and tools.
