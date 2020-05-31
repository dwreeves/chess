import re
from typing import List, Optional, NamedTuple, Type
from copy import deepcopy
# TODO: upgrade to python3.8 for singledispatchmethod on `valid_move`?

from .grid import CharNumGrid, Loc, Vector, decompose
from .pieces import (
    ChessPiece, Rook, Knight, Bishop, Pawn, Queen, King,
    PIECE_NAME_TO_TYPE, ALL_PIECES, ALL_COLORS
)
from .display import repr_grid
from .config import get_option

# Note: this regex doesn't check by itself for invalid inputs; e.g. pawn
# promotions only happen on 1 or 8, but this won't check for that.
valid_move_regex = re.compile('''
    ^
    ([BKNQR])?          # 0- Piece name that is being moved.
    ([a-h])?            # 1- File of piece being moved.
    ([1-8])?            # 2- Rank of piece being moved.
    ([x]?)              # 3- Was the piece captured? 'x' if yes.
    ([a-h][1-8])        # 4- Spot being moved to.
    (?:=([BKNQR]))?     # 5- Pawn promotion.
    ([+#])?             # 6- Check or checkmate.
    (?:[?!]{0,2})       # Annotation (not captured)
    $
''', re.VERBOSE)


class InvalidMove(Exception):
    pass


class MoveAttributes(NamedTuple):
    piece_to_move: Type
    move_from_file: Optional[str]
    move_from_rank: Optional[str]
    capture: bool
    move_to: str
    pawn_promotion: Optional[ChessPiece] = None
    check: Optional[bool] = False
    checkmate: Optional[bool] = False


def parse_move(m: str) -> MoveAttributes:
    regex_move = re.match(valid_move_regex, m)
    if not regex_move:
        raise InvalidMove('This move is not proper algebraic notation.')
    return MoveAttributes(
        piece_to_move=PIECE_NAME_TO_TYPE.get(regex_move[1], Pawn),
        move_from_file=regex_move[2],
        move_from_rank=regex_move[3],
        capture=(regex_move[4] == 'x'),
        move_to=regex_move[5],
        pawn_promotion=PIECE_NAME_TO_TYPE.get(regex_move[6]),
        check=(regex_move[7] == '+'),
        checkmate=(regex_move[7] == '#')
    )


class ChessBoard(CharNumGrid):
    _moves = 0
    _winner = None

    def __init__(self, setup: bool = True) -> None:
        super().__init__(8, 8)
        if setup:
            self.restart_game()

    def copy(self) -> 'ChessBoard':
        return deepcopy(self)

    def restart_game(self) -> None:
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

        for file_ in 'abcdefgh':
            self[f'{file_}2'] = Pawn('white')

        for file_ in 'abcdefgh':
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
                res = res and isinstance(piece, PIECE_NAME_TO_TYPE[piece_name])
            if color:
                res = res and piece.color == color
            return res

        return [loc for loc in self.positions if filter_func(self[loc])]

    def move(self, s: str):
        # If space, look for multiple moves
        if s.find(' ') > 0:
            move_list = s.replace('.', '. ').split(' ')
            for m in move_list:
                if re.match('[0-9]+\.', m) or m == '':
                    continue
                self.move(m)
            return self
        # Get information from the input about the move
        move_attr = parse_move(s)
        # Identify the subset of all possible starting positions.
        possible_starts = [
            (Loc.from_charnum(move_attr.move_to) + i).charnum
            for i
            in (
                move_attr
                .piece_to_move(self.whose_turn)
                .reverse_shifts(capture=move_attr.capture)
            )
        ]
        # Filter based on rank and/or file if it was passed:
        if move_attr.move_from_file:
            possible_starts = list(filter(
                lambda x: x.find(move_attr.move_from_file) >= 0,
                possible_starts
            ))
        if move_attr.move_from_rank:
            possible_starts = list(filter(
                lambda x: x.find(move_attr.move_from_rank) >= 0,
                possible_starts
            ))
        # Filter those possible starts based on the board state.
        if len(possible_starts) > 1:
            possible_starts = self.filter(
                color=self.whose_turn,
                piece_type=move_attr.piece_to_move,
                tile_subset=possible_starts
            )

        if len(possible_starts) == 1:
            return self.move_from_to(possible_starts[0], move_attr.move_to)
        if len(possible_starts) == 0:
            raise InvalidMove('No pieces can move to that point.')
        else:
            raise ValueError('Not sure what happened.')

    @property
    def moves(self) -> int:
        return self._moves

    @property
    def whose_turn(self) -> str:
        return 'white' if self.moves % 2 == 0 else 'black'

    @property
    def whose_turn_it_isnt(self) -> str:
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

    def filter(
            self,
            color: Optional[str] = None,
            piece_type: Optional[Type] = None,
            tile_subset: Optional[List[str]] = None
    ):
        """Get a list of all tiles that have pieces on them and also meet
        certain criteria."""

        def _filter_func(x: ChessPiece) -> bool:
            if x is None:
                return False
            val = True
            if color:
                val = val and x.color == color
            if piece_type:
                val = val and isinstance(x, piece_type)
            return val

        if tile_subset:
            tile_subset = [i for i in tile_subset if i in self.positions]
        else:
            tile_subset = self.positions
        return [
            tile
            for tile in tile_subset
            if _filter_func(self[tile])
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

    @property
    def _oriented(self):
        return list(reversed(list(map(list, zip(*self._mat)))))

    def __repr__(self) -> str:
        out_styles = {
            'big': self._repr_big_,
            'medium': self._repr_medium_,
            'small': self._repr_small_
        }
        return out_styles[get_option('display.size')]()

    def _repr_big_(self) -> str:
        return repr_grid(self._oriented, 1, True)

    def _repr_medium_(self) -> str:
        return repr_grid(self._oriented, 0, True)

    def _repr_small_(self) -> str:
        return repr_grid(self._oriented, 0, False)
