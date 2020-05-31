from .grid import CharNumGrid
from .config import get_option
from .pieces import ChessPiece
from typing import Optional, List


def _tile_repr(
        s: Optional[ChessPiece],
        x_padding: int = 0,
        blank: str = ' '
) -> str:
    pad = ' ' * x_padding
    content = blank if s is None else s.char
    return f'{pad}{content}{pad}'


def _sandwich(start: str, middle: str, end: str,
              joinby: str = '', mid_len: int = 7) -> str:
    return joinby.join([start, *[middle] * mid_len, end])


_top_border_tup = ('┌', '┬', '┐')
_mid_border_tup = ('├', '┼', '┤')
_bot_border_tup = ('└', '┴', '┘')


def _add_y_axis(s: str, border: bool = True) -> str:
    if not get_option('display.axis_labels'):
        return s
    vborder_char = '│' if border else ''
    line_start = ''.join(['\n  ', vborder_char])
    line_repl = ''.join(['\n{} ', vborder_char])
    s = f'\n{s}'
    s = s.replace('\n', '\n  ')
    s = s.replace(line_start, line_repl, 8).format(*reversed(range(1, 9)))
    s = s.replace('\n', '', 1)
    return s


def _add_x_axis(s: str, x_padding: int, border: bool) -> str:
    if not get_option('display.axis_labels'):
        return s
    pad = ' ' * x_padding
    border_pad = ' ' if border else ''
    x_labels = border_pad.join([f'{pad}{i}{pad}' for i in 'abcdefgh'])
    pad_axis = ' ' * len(s.split('\n')[0])
    return f'{s}\n{pad_axis}\n  {border_pad}{x_labels}{border_pad}'


def _axis_labels(s: str, x_padding: int, border: bool) -> str:
    s = _add_y_axis(s, border=border)
    s = _add_x_axis(s, x_padding=x_padding, border=border)
    return s


def repr_grid(
        chess_matrix: List[List[ChessPiece]],
        x_padding: int,
        border: bool
) -> str:
    hborder_char = '─' if border else ''
    vborder_char = '│' if border else ''
    blank_char = ' ' if border else '·'
    joinby = hborder_char * (1 + 2 * x_padding)

    rows = [
        vborder_char.join(['', *[
            _tile_repr(tile, x_padding=x_padding, blank=blank_char)
            for tile in rank
        ], ''])
        for rank in chess_matrix
    ]
    if border:
        top_border = _sandwich(*_top_border_tup, joinby=joinby)
        mid_border = _sandwich(*_mid_border_tup, joinby=joinby)
        bot_border = _sandwich(*_bot_border_tup, joinby=joinby)
        body = f'\n{mid_border}\n'.join(rows)
        res = '\n'.join([top_border, body, bot_border])
    else:
        res = '\n'.join(rows)
    return _axis_labels(res, x_padding=x_padding, border=border)
