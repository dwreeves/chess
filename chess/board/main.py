from .grid import CharNumGrid, Loc, Vector, decompose
from .pieces import (
    ChessPiece, Rook, Knight, Bishop, Pawn, Queen, King, PIECE_TYPES
)
from .display import ChessReprMixin
import string
import re
from typing import List, Optional
from copy import deepcopy
# TODO: upgrade to python3.8 for singledispatchmethod on `valid_move`?


def valid_move_notation(s: str) -> bool:
    return bool(re.match(
        '([BKNQR]?(([a-h])|([a-h][1-8]))?[x]?[a-h][1-8])'
        '|([a-h][1|8]=[BKNQR])[+]?',
        s
    ))


class InvalidMove(Exception):
    pass


class ChessBoard(ChessReprMixin, CharNumGrid):
    _moves = 0
    _winner = None

    def __init__(self, setup: bool = True):
        super().__init__(8, 8)
        if setup:
            self.restart_game()

    def copy(self):
        return deepcopy(self)

    def restart_game(self):
        self._moves = 0
        self._winner = None
        self.clear()
        for rank, color in zip([1, 8], ['white', 'black']):
            self[f'a{rank}'] = Rook(color)
            self[f'b{rank}'] = Knight(color)
            self[f'c{rank}'] = Bishop(color)
            self[f'd{rank}'] = Queen(color)
            self[f'e{rank}'] = King(color)
            self[f'f{rank}'] = Bishop(color)
            self[f'g{rank}'] = Knight(color)
            self[f'h{rank}'] = Rook(color)

        for file_ in string.ascii_lowercase[:8]:
            self[f'{file_}2'] = Pawn('white')

        for file_ in string.ascii_lowercase[:8]:
            self[f'{file_}7'] = Pawn('black')

    @property
    def winner(self) -> Optional[str]:
        if self._winner:
            return self._winner
        for color in ['white', 'black']:
            if self.player_in_checkmate(color):
                return color
        return None

    def find_piece_locs(
            self,
            piece_name: Optional[str] = None,
            color: Optional[str] = None
    ) -> List[str]:
        def filter_func(piece: ChessPiece):
            if piece is None:
                return False
            res = True
            if piece_name:
                res = res and isinstance(piece, PIECE_TYPES[piece_name])
            if color:
                res = res and piece.color == color
            return res
        return [loc for loc in self.positions if filter_func(self[loc])]

    def move(self, s: str):
        if s.find(' ') > 0:
            move_list = s.replace('.', '. ').split(' ')
            for m in move_list:
                if re.match('[0-9]+\.', m) or m == '':
                    continue
                self.move(m)
            return self
        if not valid_move_notation(s):
            raise InvalidMove('Cannot parse the input as a valid move.')
        regex = re.match('.*?([BKNQR]?)[x]?([a-h][1-8])[^a-h1-8]*$', s)
        piece = regex[1] or 'pawn'
        to = regex[2]
        valid_pieces = self.find_piece_locs(piece_name=piece,
                                            color=self.whose_turn)
        valid_move = self.valid_moves_to_loc(to, from_subset=valid_pieces)
        if len(valid_move) == 1:
            return self.move_from_to(valid_move[0], to)
        if len(valid_move) == 0:
            raise InvalidMove('No pieces can move to that point.')
        else:
            raise ValueError('Not sure what happened.')

    @property
    def moves(self):
        return self._moves

    @property
    def whose_turn(self):
        return 'white' if self.moves % 2 == 0 else 'black'

    @property
    def whose_turn_it_isnt(self):
        return 'black' if self.moves % 2 == 0 else 'white'

    def move_from_to(
            self,
            loc: str,
            to: str,
            check_if_valid: bool = True,
            **kwargs
    ) -> 'ChessBoard':
        if kwargs:
            raise TypeError('move() got an unexpected keyword argument '
                            f'{list(kwargs)[0].__repr__()}')
        if check_if_valid and not self.valid_move(loc, to):
            raise InvalidMove(f'{loc} to {to} is an invalid move.')
        res = super().move_from_to(loc, to, overwrite=True)
        self[to].has_moved = True
        self._moves += 1
        if check_if_valid:
            if self.player_in_checkmate(self.whose_turn):
                self._winner = self.whose_turn_it_isnt
        return res

    def valid_moves_from_loc(
            self,
            loc: str,
            look_for_check: bool = True
    ) -> List[str]:
        if not isinstance(self[loc], ChessPiece):
            return []
        return [
            (Loc.from_charnum(loc) + shift).charnum
            for shift
            in self[loc].shift_patterns
            if self.valid_move(loc,
                               (Loc.from_charnum(loc) + shift).charnum,
                               look_for_check=look_for_check)
        ]

    def valid_moves_to_loc(
            self,
            loc: str,
            look_for_check: bool = True,
            from_subset: list = None
    ) -> List[str]:
        # TODO: Add most of the game logic here.
        from_subset = from_subset or self.positions
        return [
            tile
            for tile in self.positions
            if (
                (loc in self.valid_moves_from_loc(
                    tile, look_for_check=look_for_check)
                 )
                and tile in from_subset
            )
        ]

    def all_valid_moves(self) -> list:
        return [
            (loc, move)
            for loc in self.positions
            for move in self.valid_moves_from_loc(loc)
        ]

    def player_in_checkmate(self, color: str) -> bool:
        if self.player_in_check(color):
            if not self.all_valid_moves():
                return True
        return False

    def player_in_check(self, color: str) -> bool:
        for tile, loc in zip(self, self.positions):
            if isinstance(tile, King) and tile.color == color:
                return len(
                    self.valid_moves_to_loc(loc, look_for_check=False)
                ) > 0

    def valid_move(
            self,
            loc: str,
            to: str,
            look_for_check: bool = True
    ) -> bool:
        valid_before_check = self._valid_move(loc, to)
        if (not valid_before_check) or (not look_for_check):
            return valid_before_check
        # If it's not the player's turn, they can't move!
        if self.whose_turn != self[loc].color:
            return False
        player = self[loc].color
        cb = self.copy()
        cb.move_from_to(loc=loc, to=to, check_if_valid=False)
        return not cb.player_in_check(player)

    def _valid_move(self, loc: str, to: str) -> bool:
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

