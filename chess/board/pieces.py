from typing import List, Optional
from .grid import Vector
from .config import get_option
from .utils import sign

ONE_THRU_SEVEN = [*range(-7, 0, 1), *range(1, 8)]


class ChessPiece(object):
    _char: str = None
    _unicode: dict = None
    _shift_patterns: List[Vector] = None

    def __init__(self, color):
        self.color = color

    @property
    def color(self):
        return self._color

    @property
    def shift_patterns(self):
        """_shift_patterns contains all possible hypothetical shifts, including
        castles and two-step moves for pawns. The ChessBoard determines whether
        the moves are legal."""
        return self._shift_patterns

    @color.setter
    def color(self, val):
        if val not in ['white', 'black']:
            raise TypeError('Pieces must be either white or black.')
        self._color = val

    def __repr__(self):
        return f'{self.__class__.__name__}({self.color})'

    @property
    def char(self):
        if not self._char:
            raise NotImplementedError
        if get_option('display.figurine'):
            return self._unicode[self.color]
        else:
            return (
                self._char.upper() if self.color == 'white'
                else self._char.lower()
            )


class Pawn(ChessPiece):
    _char = 'P'
    _unicode = {'white': '♙', 'black': '♟'}
    _shift_patterns = [
        Vector(x=x, y=y)
        for x in [1, 0, -1]
        for y in [2, 1, -1, -2]
        if not (abs(y) == 2 and x != 0)
    ]

    @property
    def _direction(self):
        return 1 if self.color == 'white' else -1

    @property
    def shift_patterns(self):
        return [i for i in self._shift_patterns if sign(i.y) == self._direction]


class Rook(ChessPiece):
    _char = 'R'
    _unicode = {'white': '♖', 'black': '♜'}
    _shift_patterns = [
        *[Vector(x=0, y=y) for y in ONE_THRU_SEVEN],
        *[Vector(x=x, y=0) for x in ONE_THRU_SEVEN]
    ]


class Bishop(ChessPiece):
    _char = 'B'
    _unicode = {'white': '♗', 'black': '♝'}
    _shift_patterns = [
        *[Vector(x=i, y=i) for i in ONE_THRU_SEVEN],
        *[Vector(x=i, y=-i) for i in ONE_THRU_SEVEN]
    ]


class Queen(ChessPiece):
    _char = 'Q'
    _unicode = {'white': '♕', 'black': '♛'}
    _shift_patterns = [
        *[Vector(x=0, y=y) for y in ONE_THRU_SEVEN],
        *[Vector(x=x, y=0) for x in ONE_THRU_SEVEN],
        *[Vector(x=i, y=i) for i in ONE_THRU_SEVEN],
        *[Vector(x=i, y=-i) for i in ONE_THRU_SEVEN]
    ]


class King(ChessPiece):
    _char = 'K'
    _unicode = {'white': '♔', 'black': '♚'}
    _shift_patterns = [
        Vector(x=x, y=y)
        for x in [-2, 1, 0, -1, 2]
        for y in [1, 0, -1]
        if (x != 0 and y != 0) or not (x == 2 and y != 0)
    ]


class Knight(ChessPiece):
    _char = 'N'
    _unicode = {'white': '♘', 'black': '♞'}
    _shift_patterns = [
        Vector(x=x, y=y)
        for x in [1, 2, -1, -2]
        for y in [1, 2, -1, -2]
        if abs(x) != abs(y)
    ]
