import os
import sys
import unittest

try:
    fpath = os.path.dirname(__file__)
    root_dir = os.path.abspath(os.path.join(fpath, '../../..'))
    sys.path.append(root_dir)
    from chess.board import ChessBoard, set_option, reset_option
    from chess.board.config import ALL
finally:
    sys.path.remove(root_dir)


class TestDisplay(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        reset_option(ALL)
        self.board = ChessBoard()

    def test_small_display(self):
        set_option('display.size', 'small')
        self.assertEqual(
            repr(self.board),
            '8 rnbqkbnr\n'
            '7 pppppppp\n'
            '6 ········\n'
            '5 ········\n'
            '4 ········\n'
            '3 ········\n'
            '2 PPPPPPPP\n'
            '1 RNBQKBNR\n'
            '          \n' 
            '  abcdefgh'
        )

    def test_medium_display(self):
        set_option('display.size', 'medium')
        self.assertEqual(
            repr(self.board),
            '  ┌─┬─┬─┬─┬─┬─┬─┬─┐\n'
            '8 │r│n│b│q│k│b│n│r│\n'
            '  ├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '7 │p│p│p│p│p│p│p│p│\n'
            '  ├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '6 │ │ │ │ │ │ │ │ │\n'
            '  ├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '5 │ │ │ │ │ │ │ │ │\n'
            '  ├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '4 │ │ │ │ │ │ │ │ │\n'
            '  ├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '3 │ │ │ │ │ │ │ │ │\n'
            '  ├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '2 │P│P│P│P│P│P│P│P│\n'
            '  ├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '1 │R│N│B│Q│K│B│N│R│\n'
            '  └─┴─┴─┴─┴─┴─┴─┴─┘\n'
            '                   \n'
            '   a b c d e f g h '
        )

    def test_big_display(self):
        # set_option('display.size', 'big')
        self.assertEqual(
            repr(self.board),
            '  ┌───┬───┬───┬───┬───┬───┬───┬───┐\n'
            '8 │ r │ n │ b │ q │ k │ b │ n │ r │\n'
            '  ├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '7 │ p │ p │ p │ p │ p │ p │ p │ p │\n'
            '  ├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '6 │   │   │   │   │   │   │   │   │\n'
            '  ├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '5 │   │   │   │   │   │   │   │   │\n'
            '  ├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '4 │   │   │   │   │   │   │   │   │\n'
            '  ├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '3 │   │   │   │   │   │   │   │   │\n'
            '  ├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '2 │ P │ P │ P │ P │ P │ P │ P │ P │\n'
            '  ├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '1 │ R │ N │ B │ Q │ K │ B │ N │ R │\n'
            '  └───┴───┴───┴───┴───┴───┴───┴───┘\n'
            '                                   \n'
            '    a   b   c   d   e   f   g   h  '
        )

    def test_small_display_no_labels(self):
        set_option('display.size', 'small')
        set_option('display.axis_labels', False)
        self.assertEqual(
            repr(self.board),
            'rnbqkbnr\n'
            'pppppppp\n'
            '········\n'
            '········\n'
            '········\n'
            '········\n'
            'PPPPPPPP\n'
            'RNBQKBNR'
        )

    def test_medium_display_no_labels(self):
        set_option('display.size', 'medium')
        set_option('display.axis_labels', False)
        self.assertEqual(
            repr(self.board),
            '┌─┬─┬─┬─┬─┬─┬─┬─┐\n'
            '│r│n│b│q│k│b│n│r│\n'
            '├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '│p│p│p│p│p│p│p│p│\n'
            '├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '│ │ │ │ │ │ │ │ │\n'
            '├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '│ │ │ │ │ │ │ │ │\n'
            '├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '│ │ │ │ │ │ │ │ │\n'
            '├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '│ │ │ │ │ │ │ │ │\n'
            '├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '│P│P│P│P│P│P│P│P│\n'
            '├─┼─┼─┼─┼─┼─┼─┼─┤\n'
            '│R│N│B│Q│K│B│N│R│\n'
            '└─┴─┴─┴─┴─┴─┴─┴─┘'
        )

    def test_big_display_no_labels(self):
        # set_option('display.size', 'big')
        set_option('display.axis_labels', False)
        self.assertEqual(
            repr(self.board),
            '┌───┬───┬───┬───┬───┬───┬───┬───┐\n'
            '│ r │ n │ b │ q │ k │ b │ n │ r │\n'
            '├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '│ p │ p │ p │ p │ p │ p │ p │ p │\n'
            '├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '│   │   │   │   │   │   │   │   │\n'
            '├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '│   │   │   │   │   │   │   │   │\n'
            '├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '│   │   │   │   │   │   │   │   │\n'
            '├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '│   │   │   │   │   │   │   │   │\n'
            '├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '│ P │ P │ P │ P │ P │ P │ P │ P │\n'
            '├───┼───┼───┼───┼───┼───┼───┼───┤\n'
            '│ R │ N │ B │ Q │ K │ B │ N │ R │\n'
            '└───┴───┴───┴───┴───┴───┴───┴───┘'
        )


if __name__ == '__main__':
    unittest.main()
