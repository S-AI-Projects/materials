"""Advent of Code Grid Visualization.

Worked example of grid coordinate to symbol rendering:
  Symbol mapping (index lookup into " *o"):
    0 -> ' ' (empty passage)
    1 -> '*' (obstacle / wall)
    2 -> 'o' (goal / target)

  Traced decisive state transitions:
    grid[0, 0] = 1 -> rendered symbol '*'
    grid[1, 1] = 0 -> rendered symbol ' '
    grid[3, 3] = 2 -> rendered symbol 'o' (unique goal at row 3, col 3)
"""
import numpy as np
from colorama import Cursor

grid = np.array(
    [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1],
        [1, 0, 0, 2, 1],
        [1, 1, 1, 1, 1],
    ]
)

num_rows, num_cols = grid.shape
for row in range(num_rows):
    for col in range(num_cols):
        symbol = " *o"[grid[row, col]]
        print(f"{Cursor.POS(col + 1, row + 2)}{symbol}")
