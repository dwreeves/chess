import os
import sys
import unittest
from typing import Callable

try:
    fpath = os.path.dirname(__file__)
    root_dir = os.path.abspath(os.path.join(fpath, '../../..'))
    sys.path.append(root_dir)
    from chess.board.grid import Grid, Loc, Vector
finally:
    sys.path.remove(root_dir)


class TestGrid(unittest.TestCase):

    def setUp(self):
        self.grid = Grid(8, 8)
        self.grid[0, 4] = 'foo'

    def test_getitem(self):
        self.assertEqual(self.grid[0, 4], 'foo')

    def test_shift(self):
        self.grid.shift([0, 4], [1, -1])
        self.assertEqual(self.grid[1, 3], 'foo')

    def test_shift_with_vector(self):
        self.grid.shift([0, 4], Vector(1, -1))
        self.assertEqual(self.grid[1, 3], 'foo')

    def test_clear(self):
        self.grid.clear()
        self.assertEqual(self.grid[0, 4], None)

    def test_move_from_to(self):
        self.grid.move_from_to([0, 4], [6, 6])
        self.assertEqual(self.grid[6, 6], 'foo')

    def test_move_from_to_with_loc(self):
        self.grid.move_from_to(Loc(0, 4), Loc(6, 6))
        self.assertEqual(self.grid[6, 6], 'foo')

    def test_dimensions(self):
        self.assertEqual(self.grid.dimensions[0], 8)
        self.assertEqual(self.grid.dimensions[1], 8)


if __name__ == '__main__':
    unittest.main()
