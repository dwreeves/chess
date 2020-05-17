from .grid import CharNumGrid
from .pieces import ChessPiece, Rook, Knight, Bishop, Pawn, Queen, King
import string
from typing import Optional


def _tile_repr(s: Optional[ChessPiece], blank: str = ' ') -> str:
    return blank if s is None else s.char


class ChessBoard(CharNumGrid):
    _moves = 0

    def __init__(self, setup: bool = True):
        super().__init__(8, 8)
        if setup:
            self.restart_game()

    def restart_game(self):
        self._moves = 0
        self.clear()
        self._set_up_pieces()

    def _set_up_pieces(self):
        if not self.empty:
            raise ValueError('Cannot set up the pieces because the chess board '
                             'is not empty!')
        for rank, color in zip([1, 8], ['white', 'black']):
            self[f'a{rank}'] = Rook(color)
            self[f'b{rank}'] = Bishop(color)
            self[f'c{rank}'] = Knight(color)
            self[f'd{rank}'] = Queen(color)
            self[f'e{rank}'] = King(color)
            self[f'f{rank}'] = Knight(color)
            self[f'g{rank}'] = Bishop(color)
            self[f'h{rank}'] = Rook(color)

        for file_ in string.ascii_lowercase[:8]:
            self[f'{file_}2'] = Pawn('white')

        for file_ in string.ascii_lowercase[:8]:
            self[f'{file_}7'] = Pawn('black')

    @property
    def moves(self):
        return self._moves

    @property
    def whose_turn(self):
        return 'white' if self.moves % 2 == 0 else 'black'

    def move(self, loc, to, **kwargs):
        if kwargs:
            raise TypeError('move() got an unexpected keyword argument '
                            f'{list(kwargs)[0].__repr__()}')
        super().move(loc, to, overwrite=True)

    @property
    def _oriented(self):
        return list(reversed(list(map(list, zip(*self._mat)))))

    def __repr__(self):
        return self._big_repr_()

    def _big_repr_(self):
        top_delimit = '┌' + ('───┬' * 7) + '───┐'
        middle_delimit = '├' + ('───┼' * 7) + '───┤'
        bottom_delimit = '└' + ('───┴' * 7) + '───┘'
        rows = [
            '│ ' + ' │ '.join([_tile_repr(tile) for tile in rank]) + ' │'
            for rank in self._oriented
        ]
        body = f'\n{middle_delimit}\n'.join(rows)
        return f'{top_delimit}\n{body}\n{bottom_delimit}'

    def _med_repr_(self):
        top_delimit = '┌' + ('─┬' * 7) + '─┐'
        middle_delimit = '├' + ('─┼' * 7) + '─┤'
        bottom_delimit = '└' + ('─┴' * 7) + '─┘'
        rows = [
            '│' + '│'.join([_tile_repr(tile) for tile in rank]) + '│'
            for rank in self._oriented
        ]
        body = f'\n{middle_delimit}\n'.join(rows)
        return f'{top_delimit}\n{body}\n{bottom_delimit}'

    def _small_repr_(self):
        return '\n'.join([
            ''.join([_tile_repr(tile, blank='·') for tile in rank])
            for rank in self._oriented
        ])
