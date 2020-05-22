from .config import get_option
from .grid import CharNumGrid, Loc, Vector
from .pieces import ChessPiece, Rook, Knight, Bishop, Pawn, Queen, King
import string
from typing import Optional, List


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
        if not self.is_empty:
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

    def move(self, to: str, **kwargs) -> 'ChessBoard':
        if kwargs:
            raise TypeError('move() got an unexpected keyword argument '
                            f'{list(kwargs)[0].__repr__()}')
        loc = 'e3'
        return super().move(loc, to, overwrite=True)

    @property
    def _oriented(self):
        return list(reversed(list(map(list, zip(*self._mat)))))

    def __repr__(self):
        out_styles = {
            'big': self._big_repr_,
            'medium': self._medium_repr_,
            'small': self._small_repr_
        }
        return out_styles[get_option('display.size')]()

    def _big_repr_(self):
        prefix = '   ' if get_option('display.axis_labels') else ''
        top_delimit = prefix + '┌' + ('───┬' * 7) + '───┐'
        middle_delimit = prefix + '├' + ('───┼' * 7) + '───┤'
        bottom_delimit = prefix + '└' + ('───┴' * 7) + '───┘'
        if get_option('display.axis_labels'):
            bottom_delimit += \
                '\n     ' + '   '.join(iter('abcdefgh')) + '  '

        rows = [
            (
                (
                    f' {str(rank_num)} '
                    if get_option('display.axis_labels')
                    else ''
                )
                + '│ '
                + ' │ '.join([_tile_repr(tile) for tile in rank])
                + ' │'
            )
            for rank, rank_num
            in zip(self._oriented, reversed(range(1, 9)))
        ]
        body = f'\n{middle_delimit}\n'.join(rows)
        return f'{top_delimit}\n{body}\n{bottom_delimit}'

    def _medium_repr_(self):
        prefix = '   ' if get_option('display.axis_labels') else ''
        top_delimit = ''.join([prefix, '┌', ('─┬' * 7), '─┐'])
        middle_delimit = ''.join([prefix, '├', ('─┼' * 7), '─┤'])
        bottom_delimit = ''.join([prefix, '└', ('─┴' * 7), '─┘'])
        if get_option('display.axis_labels'):
            bottom_delimit += \
                '\n    ' + ' '.join(iter('abcdefgh')) + '  '
        rows = [
            (
                (
                    f' {str(rank_num)} '
                    if get_option('display.axis_labels')
                    else ''
                )
                + '│'
                + '│'.join([_tile_repr(tile) for tile in rank])
                + '│'
            )
            for rank, rank_num
            in zip(self._oriented, reversed(range(1, 9)))
        ]
        body = f'\n{middle_delimit}\n'.join(rows)
        return f'{top_delimit}\n{body}\n{bottom_delimit}'

    def _small_repr_(self):
        return '\n'.join([
            (f'{rank_num}  ' if get_option('display.axis_labels') else '')
            + ''.join([_tile_repr(tile, blank='·') for tile in rank])
            for rank, rank_num in zip(self._oriented,
                                      map(str, reversed(range(1, 9))))
        ]) + '\n\n   abcdefgh' if get_option('display.axis_labels') else ''

    def valid_moves_from_loc(self, loc: str) -> List[str]:
        if not isinstance(self[loc], ChessPiece):
            return []
        return [
            (Loc.from_charnum(loc) + shift).charnum
            for shift
            in self[loc].shift_patterns
        ]

    def valid_moves_to_loc(self, loc: str) -> List[str]:
        # TODO: Add most of the game logic here.
        return [
            tile
            for tile in self.positions
            if (loc in self.valid_moves_from_loc(tile))
        ]
