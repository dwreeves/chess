from typing import List, Optional, Type, Dict
from .grid import Vector, decompose
from .config import get_option
from .utils import sign

ONE_THRU_SEVEN = [*range(-7, 0, 1), *range(1, 8)]
ALL_COLORS = {'white', 'black'}


class ChessPiece(object):
    _char: str = None
    _unicode: dict = None
    _shift_patterns: List[Vector] = None

    def __init__(self, color):
        self.color = color
        self.has_moved = False

    @property
    def color(self) -> str:
        return self._color

    @property
    def shift_patterns(self) -> List[Vector]:
        """_shift_patterns contains all possible hypothetical shifts, including
        castles and two-step moves for pawns. The ChessBoard determines whether
        the moves are legal."""
        return self._shift_patterns

    @property
    def reverse_shifts(self) -> List[Vector]:
        """For all except Pawn, reverse shifts are the same as shifts."""
        return self._shift_patterns

    @color.setter
    def color(self, val):
        if val not in ALL_COLORS:
            raise TypeError('Pieces must be either white or black.')
        self._color = val

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.color})'

    @property
    def char(self) -> str:
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
    def _direction(self) -> int:
        return 1 if self.color == 'white' else -1

    @property
    def shift_patterns(self) -> List[Vector]:
        return [
            i for i in self._shift_patterns
            if (
                sign(i.y) == self._direction
                and (abs(i.y) <= 1 or not self.has_moved)
            )
        ]

    @property
    def reverse_shifts(self, capture: bool = False) -> List[Vector]:
        return [i.reverse for i in self.shift_patterns]

    def reverse_shifts_capture(self, capture: bool = False) -> List[Vector]:
        """Similar to `reverse_shifts` but includes a check on capture. This is
        used when the option `api.notation_mismatch` is set to `error`: If a
        pawn is moving diagonally and no capture is included, or if a pawn is
        moving straight and it says capture, then these are filtered away as
        valid moves if we don't allow for notation mismatch."""
        if capture:
            return [i.reverse for i in self.shift_patterns if i.x != 0]
        else:
            return [i.reverse for i in self.shift_patterns if i.x == 0]



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
        if (Vector(x=x, y=y).norm_linf == 1) or (abs(x) == 2 and y == 0)
    ]

    @property
    def shift_patterns(self) -> List[Vector]:
        return [
            i for i in self._shift_patterns
            if abs(i.x) <= 1 or not self.has_moved
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


PIECE_NAME_TO_TYPE = {}
for piece in {Pawn, Rook, Queen, King, Bishop, Rook, Knight}:
    PIECE_NAME_TO_TYPE[piece.__name__.lower()] = piece
    PIECE_NAME_TO_TYPE[piece._char] = piece

ALL_PIECES = set(PIECE_NAME_TO_TYPE.values())


MOVE_LOOKUP_DICT_SANS_PAWNS: Dict[Vector, List[Type]] = {}

for piece in {Rook, King, Queen, Bishop, Knight}:
    # Lookup for non-Pawn moves, excluding castles.
    p = piece('white')
    p.has_moved = True
    for shift in p.shift_patterns:
        if not MOVE_LOOKUP_DICT_SANS_PAWNS.get(shift):
            MOVE_LOOKUP_DICT_SANS_PAWNS[shift] = [piece]
        else:
            MOVE_LOOKUP_DICT_SANS_PAWNS[shift].append(piece)


def _striking_distance(defending_color: str) -> Dict[Vector, List[Type]]:
    """Copying a dict over and over again is more memory intensive than
    necessary, so they're built here first."""
    d = MOVE_LOOKUP_DICT_SANS_PAWNS.copy()
    for shift in Pawn(defending_color).reverse_shifts_capture(capture=True):
        d[shift].append(Pawn)
    return d


_STRIKING_DISTANCE_BLACK_DEFENDING = _striking_distance('black')
_STRIKING_DISTANCE_WHITE_DEFENDING = _striking_distance('white')


def striking_distance(defending_color: str) -> Dict[Vector, List[Type]]:
    """Striking distance is defined relative to the piece that is being
    attacked, not the attacking piece."""
    return {
        'black': _STRIKING_DISTANCE_BLACK_DEFENDING,
        'white': _STRIKING_DISTANCE_WHITE_DEFENDING
    }[defending_color]
