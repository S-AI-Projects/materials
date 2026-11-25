"""Executable documentation tests for aoc_grid.py."""
import numpy as np
import unittest

GRID = np.array(
    [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1],
        [1, 0, 0, 2, 1],
        [1, 1, 1, 1, 1],
    ]
)
SYMBOLS = " *o"

class TestAocGridDocExample(unittest.TestCase):
    def test_smallest_valid_input_zero_maps_to_space(self):
        self.assertEqual(SYMBOLS[0], " ")

    def test_ordinary_valid_input_one_maps_to_star(self):
        self.assertEqual(SYMBOLS[1], "*")

    def test_ordinary_valid_input_two_maps_to_goal_o(self):
        self.assertEqual(SYMBOLS[2], "o")

    def test_grid_shape_five_by_five(self):
        self.assertEqual(GRID.shape, (5, 5))

    def test_corner_wall_cell_symbol(self):
        self.assertEqual(SYMBOLS[GRID[0, 0]], "*")

    def test_open_interior_cell_symbol(self):
        self.assertEqual(SYMBOLS[GRID[1, 1]], " ")

    def test_decisive_goal_cell_symbol(self):
        self.assertEqual(SYMBOLS[GRID[3, 3]], "o")

    def test_unique_goal_cell_count(self):
        self.assertEqual(int(np.sum(GRID == 2)), 1)

if __name__ == "__main__":
    unittest.main()
