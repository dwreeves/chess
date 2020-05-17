

class ChessPiece(object):
    _char = None

    def __init__(self, color):
        self.color = color

    @property
    def color(self):
        return self._color

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
        return (
            self._char.upper() if self.color == 'white'
            else self._char.lower()
        )


class Pawn(ChessPiece):
    _char = 'P'


class Rook(ChessPiece):
    _char = 'R'


class Bishop(ChessPiece):
    _char = 'B'


class Queen(ChessPiece):
    _char = 'Q'


class King(ChessPiece):
    _char = 'K'


class Knight(ChessPiece):
    _char = 'N'
