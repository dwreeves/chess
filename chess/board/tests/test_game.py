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

    def test_game_of_the_century(self):
        game = (
            '1.Nf3 Nf6 2.c4 g6 3.Nc3 Bg7 4.d4 O-O 5.Bf4 d5 6.Qb3 dxc4 '
            '7.Qxc4 c6 8.e4 Nbd7 9.Rd1 Nb6 10.Qc5 Bg4 11.Bg5 Na4 12.Qa3 Nxc3 '
            '13.bxc3 Nxe4 14.Bxe7 Qb6 15.Bc4 Nxc3 16.Bc5 Rfe8+ 17.Kf1 Be6 '
            '18.Bxb6 Bxc4+ 19.Kg1 Ne2+ 20.Kf1 Nxd4+ 21.Kg1 Ne2+ 22.Kf1 Nc3+ '
            '23.Kg1 axb6 24.Qb4 Ra4 25.Qxb6 Nxd1 26.h3 Rxa2 27.Kh2 Nxf2 '
            '28.Re1 Rxe1 29.Qd8+ Bf8 30.Nxe1 Bd5 31.Nf3 Ne4 32.Qb8 b5 33.h4 h5 '
            '34.Ne5 Kg7 35.Kg1 Bc5+ 36.Kf1 Ng3+ 37.Ke1 Bb4+ 38.Kd1 Bb3+ '
            '39.Kc1 Ne2+ 40.Kb1 Nc3+ 41.Kc1 Rc2'
        )
        self.assertEqual(self.board.winner, None)
        self.board.move(game)
        self.assertEqual(self.board.winner, 'black')

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
