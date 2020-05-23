from .grid import CharNumGrid
from .config import get_option
from .pieces import ChessPiece
from typing import Optional


def _tile_repr(s: Optional[ChessPiece], blank: str = ' ') -> str:
    return blank if s is None else s.char


class ChessReprMixin(CharNumGrid):

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
