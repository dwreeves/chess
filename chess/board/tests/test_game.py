import os
import sys
import unittest

try:
    fpath = os.path.dirname(__file__)
    root_dir = os.path.abspath(os.path.join(fpath, '../../..'))
    sys.path.append(root_dir)
    from chess.board import ChessBoard
finally:
    sys.path.remove(root_dir)


class TestGame(unittest.TestCase):

    def setUp(self):
        self.board = ChessBoard()

    def test_scholars_mate(self):
        game = '1.e4 e5 2.Bc4 Nc6 3.Qh5 Nf6?? 4.Qxf7#'
        self.assertEqual(self.board.winner, None)
        self.board.move(game)
        self.assertEqual(self.board.winner, 'white')

    def test_sample_game(self):
        # Game derived from:
        # https://en.wikibooks.org/wiki/Chess/Sample_chess_game
        game = (
            '1.e4 e5 2.Nf3 f6 3.Nxe5 fxe5 4.Qh5+ Ke7 5.Qxe5+ Kf7 6.Bc4+ d5 '
            '7.Bxd5+ Kg6 8.h4 h5 9.Bxb7 Bxb7 10.Qf5+ Kh6 11.d4+ g5 12.Qf7 Qe7 '
            '13.hxg5+ Qxg5 14.Rxh5#'
        )
        self.assertEqual(self.board.winner, None)
        self.board.move(game)
        self.assertEqual(self.board.winner, 'white')

    def test_incomplete_game(self):
        game = '1.e4 e5 2.Bc4 Nc6'
        self.assertEqual(self.board.winner, None)
        self.board.move(game)
        self.assertEqual(self.board.winner, None)


if __name__ == '__main__':
    unittest.main()
