from .grid import CharNumGrid, Loc, Vector, decompose
from .pieces import ChessPiece, Rook, Knight, Bishop, Pawn, Queen, King
from .display import ChessReprMixin
import string
from typing import List
# TODO: upgrade to python3.8 for singledispatchmethod on `valid_move`?


class InvalidMove(Exception):
    pass


class ChessBoard(ChessReprMixin, CharNumGrid):
    _moves = 0

    def __init__(self, setup: bool = True):
        super().__init__(8, 8)
        if setup:
            self.restart_game()

    def restart_game(self):
        self._moves = 0
        self.clear()
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

    def move_from_to(self, loc: str, to: str, **kwargs) -> 'ChessBoard':
        if kwargs:
            raise TypeError('move() got an unexpected keyword argument '
                            f'{list(kwargs)[0].__repr__()}')
        if not self.valid_move(loc, to):
            raise InvalidMove(f'{loc} to {to} is an invalid move.')
        res = super().move_from_to(loc, to, overwrite=True)
        self[to].has_moved = True
        return res

    def valid_moves_from_loc(self, loc: str) -> List[str]:
        if not isinstance(self[loc], ChessPiece):
            return []
        return [
            (Loc.from_charnum(loc) + shift).charnum
            for shift
            in self[loc].shift_patterns
            if self.valid_move(loc, (Loc.from_charnum(loc) + shift).charnum)
        ]

    def valid_moves_to_loc(self, loc: str) -> List[str]:
        # TODO: Add most of the game logic here.
        return [
            tile
            for tile in self.positions
            if (loc in self.valid_moves_from_loc(tile))
        ]

    def valid_move(self, loc: str, to: str) -> bool:
        # TODO: add castling

        # If there is no piece in `loc`, there's nothing to be moved.
        if self[loc] is None:
            return False
        # Weed out invalid `to` locations.
        try:
            self[to]
        except IndexError:
            return False
        # All hypothetically possible shift patterns are accounted for in the
        # `.shift_patterns` property of a piece.
        in_shift_patterns = (Loc.from_charnum(to) - Loc.from_charnum(loc)) \
                            in self[loc].shift_patterns
        if not in_shift_patterns:
            return False
        # For knights, the only requirement is the square is either empty or
        # off-color.
        shift = Loc.from_charnum(to) - Loc.from_charnum(loc)
        if isinstance(self[loc], Knight):
            return self[to] is None or self[to].color != self[loc].color
        # Pawns can only capture diagonally
        if isinstance(self[loc], Pawn) and abs(shift.x) == 1:
            # TODO: Add en passant
            return self[to] is not None and self[to].color != self[loc].color
        # For everyone else, the move must be decomposed.
        components = decompose(shift)
        for i, step in enumerate(components):
            loc_step = self.peek(loc, step)
            if loc_step is not None:
                # Pawns moving straight cannot capture.
                if isinstance(self[loc], Pawn) and step.x == 0:
                    return False
                elif i + 1 == len(components):
                    return self[to] is None or self[to].color != self[loc].color
                else:
                    return False
        else:
            return self[to] is None or self[to].color != self[loc].color

