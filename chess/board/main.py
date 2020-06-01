import re
from typing import List, Optional, Type
from copy import deepcopy
from dataclasses import dataclass
# TODO: upgrade to python3.8 for singledispatchmethod on `valid_move`?

from .grid import CharNumGrid, Loc, Vector, decompose, between, vector_circle
from .pieces import (
    ChessPiece, Rook, Knight, Bishop, Pawn, Queen, King,
    PIECE_NAME_TO_TYPE, striking_distance
)
from .display import repr_grid
from .config import get_option
from .utils import invert_color

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


valid_position_regex = re.compile('^[a-h][1-8]$')


def valid_position(s) -> bool:
    """Instead of doing `if pos in self.positions`, do this instead because it
    is much faster."""
    return bool(re.match(valid_position_regex, s))


class InvalidMove(Exception):
    pass


CASTLE_IDENTIFIERS = {
    '0-0': 'kingside',
    'O-O': 'kingside',
    '0-0-0': 'queenside',
    'O-O-O': 'queenside'
}


STARTING_KING_LOCS = {
    'white': 'e1',
    'black': 'e8'
}


@dataclass
class MoveAttributes:
    piece_type: Type
    player: Optional[str]
    move_from: Optional[str]
    move_from_file: Optional[str]
    move_from_rank: Optional[str]
    capture: bool
    move_to: str
    pawn_promotion: Optional[ChessPiece] = None
    check: Optional[bool] = False
    checkmate: Optional[bool] = False


def parse_move(m: str) -> MoveAttributes:
    """This function parses all non-castle moves."""
    regex_move = re.match(valid_move_regex, m)
    if not regex_move:
        raise InvalidMove('This move is not proper algebraic notation.')
    return MoveAttributes(
        piece_type=PIECE_NAME_TO_TYPE.get(regex_move[1], Pawn),
        player=None,
        move_from=None,
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
    _king_locs = {'white': None, 'black': None}

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

        # The purpose of `_king_locs` is to make it easier to find the king for
        # operations that see whether or not the king is in check: instead of
        # searching the board for the king, it just references this dict. Note
        # that modifying this dict manually can be quite dangerous, so only let
        # the code modify it for you.
        self._king_locs = STARTING_KING_LOCS.copy()

    @property
    def winner(self) -> Optional[str]:
        if self._winner:
            return self._winner
        for color in ['white', 'black']:
            if self.player_in_checkmate(color):
                return invert_color(color)
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

    def _in_kings_path(self, king_color: str, stop_after_first: bool = True):
        """Checks to see what pieces are in the king's path of a given color."""
        king_loc = Loc.from_charnum(self._king_locs[king_color])
        move_lookup = striking_distance(king_color)
        li = []
        for direction in vector_circle(7):
            for shift in decompose(direction):
                loc_to_check = (king_loc + shift).charnum
                if not valid_position(loc_to_check):
                    break
                # If a chess piece is obstructing the way, then we're going
                # to break. But we need to see if that piece could move to the
                # king.
                if isinstance(self[loc_to_check], ChessPiece):
                    if (
                        self[loc_to_check].color != king_color
                        and type(self[loc_to_check]) in move_lookup[shift]
                    ):
                        li.append(loc_to_check)
                        if stop_after_first:
                            return li
                    break
        for shift in Knight._shift_patterns:
            loc_to_check = (king_loc + shift).charnum
            if (
                valid_position(loc_to_check)
                and isinstance(self[loc_to_check], Knight)
                and self[loc_to_check].color != king_color
            ):
                li.append(loc_to_check)
                if stop_after_first:
                    return li
        return li

    def move(self, s: str):
        # If space, look for multiple moves
        if s.find(' ') > 0:
            move_list = s.replace('.', '. ').split(' ')
            for m in move_list:
                if re.match('[0-9]+\.', m) or m == '':
                    continue
                self.move(m)
            return self

        # Skip everything else if the move is a castle.
        if s in CASTLE_IDENTIFIERS:
            return self.move_castle(s)

        # Get information from the input about the move
        move_attr = parse_move(s)
        move_attr.player = self.whose_turn

        # Get the move_from location.
        move_attr.move_from = self._get_start_loc_from_move_attr(move_attr)

        # Once the move's algebraic notation has been fully parsed, the rest of
        # the logic of handling the move goes to `move_from_to`.
        return self.move_from_to(move_attr.move_from,
                                 move_attr.move_to,
                                 attributes=move_attr)

    def move_castle(self, side: str):
        """Castling is a special move involving the simultaneous movement of two
        pieces. This method handles ALL the logic of a castle: i.e. it validates
        that the castle is a legal move, performs the movements, and increments
        the move counter by +1.

        :param side: '0-0', 'O-O', '0-0-0', or 'O-O-O'.
        """
        ROOK_LOCS = {
            'white': {
                'kingside': 'h1',
                'queenside': 'a1'
            },
            'black': {
                'kingside': 'h8',
                'queenside': 'a8'
            }
        }
        SHIFTS = {
            'kingside': {
                King: Vector(x=2, y=0),
                Rook: Vector(x=-2, y=0)
            },
            'queenside': {
                King: Vector(x=-2, y=0),
                Rook: Vector(x=3, y=0)
            }
        }
        # Gather some information about what's being moved and store it in mem.
        castle_type = CASTLE_IDENTIFIERS[side]
        whose_turn = self.whose_turn
        old_king_loc = self._king_locs[whose_turn]
        old_rook_loc = ROOK_LOCS[whose_turn][castle_type]
        new_king_loc = \
            (Loc.from_charnum(old_king_loc) + SHIFTS[castle_type][King]).charnum
        new_rook_loc = \
            (Loc.from_charnum(old_rook_loc) + SHIFTS[castle_type][Rook]).charnum
        # Make sure the pieces haven't moved.
        assert not self[old_king_loc].has_moved
        assert not self[old_rook_loc].has_moved
        # Check that all the spaces between the rook and king are empty.
        # (Don't need to otherwise directly check rook can move 2-3 and king can
        # move 2; the following check is sufficient.)
        assert not self._blocked(old_rook_loc, old_king_loc, exclude_last=True)
        # Now perform the moves.
        super().move_from_to(old_king_loc, new_king_loc)
        super().move_from_to(old_rook_loc, new_rook_loc)
        # Make sure the move didn't result in going into check.
        # Register that the move has taken place
        self._moves += 1
        self[new_king_loc].has_moved = True
        self[new_rook_loc].has_moved = True
        return None

    def _get_start_loc_from_move_attr(self, move_attr: MoveAttributes) -> str:
        # Identify the subset of all possible starting positions.
        # Do this by looking at the piece type's reverse shifts.
        # If `api.notation_mismatch` is 'error', then filter Pawn moves based on
        # whether capture was denoted or not.
        if (
                (move_attr.piece_type == Pawn) and
                (get_option('api.notation_mismatch') == 'error')
        ):
            all_shifts = move_attr.piece_type(move_attr.player)\
                         .reverse_shifts_capture(capture=move_attr.capture)
        else:
            all_shifts = move_attr.piece_type(move_attr.player).reverse_shifts

        possible_starts = [
            (Loc.from_charnum(move_attr.move_to) + i).charnum
            for i
            in all_shifts
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

        # Filter those possible starts based on the board state: i.e. look for
        # pieces in `possible_starts` that match the color and piece type that
        # match to the move attributes.
        possible_starts = self.filter(
            color=move_attr.player,
            piece_type=move_attr.piece_type,
            tile_subset=possible_starts
        )

        # At this point, there should be only one piece remaining.
        if len(possible_starts) != 1:
            if len(possible_starts) == 0:
                raise InvalidMove('No pieces can move to that point.')
            elif len(possible_starts) >= 2:
                raise InvalidMove('Ambiguous move.')
            else:
                raise ValueError('Not sure what happened.')

        return possible_starts[0]

    @property
    def moves(self) -> int:
        return self._moves

    @property
    def whose_turn(self) -> str:
        return 'white' if self.moves % 2 == 0 else 'black'

    @property
    def whose_turn_it_isnt(self) -> str:
        return invert_color(self.whose_turn)

    def move_from_to(
            self,
            loc: str,
            to: str,
            safe_mode: Optional[bool] = None,
            attributes: Optional[MoveAttributes] = None
    ) -> 'ChessBoard':
        """

        :param loc:
        :param to:
        :param safe_mode:
        :param attributes: Optional. These are all move attributes parsed out
                           from the string passed in `.move()`, if algebraic
                           notation is being used.
        :return:
        """
        # First we need to validate if the move is possible:
        # - Check for obstruction if not Knight.
        # - If capturing, check for notation mismatch.
        # - Check Pawn logic: can only capture diagonally. If notation_mismatch
        #   is turned on, then we don't need to perform this step because the
        #   combination of the notation mismatch + `reverse_shifts_capture` will
        #   eliminate bad Pawn moves.
        # - Check to make sure the move does not put the active player into
        #   check or checkmate.
        if safe_mode is None:
            safe_mode = get_option('api.safe_mode')
        if safe_mode:
            if isinstance(attributes, MoveAttributes):
                valid = self._valid_move_after_shift_verification(loc, to)
            else:
                valid = self.valid_move(loc, to)
            if not valid:
                raise InvalidMove(f'{loc} to {to} is an invalid move.')
        res = super().move_from_to(loc, to, overwrite=True)
        self[to].has_moved = True
        if isinstance(self[to], King):
            self._king_locs[self[to].color] = to
        self._moves += 1
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
            if self.valid_move(loc, (Loc.from_charnum(loc) + shift).charnum)
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
            tile_subset = [i for i in tile_subset if valid_position(i)]
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
        return len(self._in_kings_path(color)) > 0

    def _blocked(
            self, loc: str, to: str, exclude_last: bool = False
    ) -> bool:
        """This function assumes that the inputs `loc` and `to` are valid
        inputs that share a cross-section or diagonal."""
        shift = Loc.from_charnum(to) - Loc.from_charnum(loc)
        magnitude = shift.norm_linf
        to_space = self[to]
        for i, pos in enumerate(between(loc, to, exclude_last=exclude_last)):
            if i + 1 < magnitude:
                if self[pos] is not None:
                    return True
            elif isinstance(self[loc], Pawn):
                return not ((
                    shift.x != 0
                    and isinstance(to_space, ChessPiece)
                    and to_space.color != self[loc].color
                ) or (
                    shift.x == 0
                    and to_space is None
                ))
            else:
                return not (
                    to_space is None
                    or to_space.color != self[loc].color
                )
        else:  # This is only reached if you exclude the last one.
            return False

    def valid_move(
            self,
            loc: str,
            to: str,
            verify_for_check: bool = True
    ) -> bool:
        # Check if piece exists in `loc`
        if self[loc] is None:
            return False
        # Check if `to` is valid location.
        try:
            self[to]
        except IndexError:
            return False
        # Check if `to` exists in shift patterns.
        # All hypothetically possible shift patterns are accounted for in the
        # `.shift_patterns` property of a piece.
        if not bool(
            (Loc.from_charnum(to) - Loc.from_charnum(loc))
            in self[loc].shift_patterns
        ):
            return False
        # If it's not the player's turn, they can't move!
        if self.whose_turn != self[loc].color:
            return False
        return self._valid_move_after_shift_verification(
            loc=loc, to=to, verify_for_check=verify_for_check
        )

    def _valid_move_after_shift_verification(
            self,
            loc: str,
            to: str,
            verify_for_check: bool = True
    ) -> bool:
        """Because we already do a lot of the checks required for the move
        during the step where we verify the algebraic notation input, we don't
        want to repeat those steps when validating whether a move is possible.
        However, we also want the user to be able to utilize the `move_from_to`
        API. So we separate out move verification into two steps.
        """
        # - If capturing, check for notation mismatch.
        # - Check Pawn logic: can only capture diagonally. Technically, if
        #   notation_mismatch is turned on, then we don't need to perform this
        #   step because the combination of the notation mismatch +
        #   `reverse_shifts_capture` will eliminate bad Pawn moves. For now, I
        #   decided I'd rather not clutter the code so I do this check as it
        #   isn't super expensive to perform.
        # - For knights, the only requirement is the square is either empty or
        #   off-color.
        if isinstance(self[loc], Knight):
            if not (self[to] is None or self[to].color != self[loc].color):
                return False
        else:
            if self._blocked(loc, to):
                return False
        # Now check to make sure the move does not put the active player into
        # check or checkmate.
        self_copy = self.copy()
        # CharNumGrid.move_from_to(self_copy, loc, to, overwrite=True)
        self_copy.move_from_to(loc, to, safe_mode=False)
        if self_copy.player_in_check(self[loc].color):
            return False
        return True

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
