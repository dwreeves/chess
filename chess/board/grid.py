from typing import Iterable, Any, Tuple
import string


class Grid(object):

    def __init__(self, x: int, y: int):
        self._mat = [[None for i in range(x)] for j in range(y)]

    def __getitem__(self, key: Tuple[int, int]):
        return self._mat[key[0]][key[1]]

    def __setitem__(self, key: Tuple[int, int], val: Any):
        self._mat[key[0]][key[1]] = val

    @property
    def dimensions(self) -> Tuple[int, int]:
        return len(self._mat), len(self._mat[0])

    def move(
            self,
            loc: Tuple[int, int],
            to: Tuple[int, int],
            overwrite: bool = False
    ):
        if self[to] is None or overwrite:
            self[loc], self[to] = None, self[loc]
        else:
            raise ValueError(f'Location {tuple(to)} is not empty.')

    def shift(self, loc: Tuple[int, int], amount: Tuple[int, int], **kwargs):
        self.move(loc, add_vector_to_point(loc, amount), **kwargs)

    def clear(self):
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                Grid.__setitem__(self, (i, j), None)

    @property
    def empty(self):
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                if Grid.__getitem__(self, (i, j)) is not None:
                    return False
        else:
            return True

    def __repr__(self):
        return '\n'.join([str(i) for i in self._mat])


def _add_two_tuples(x, y):
    return x[0] + y[0], x[1] + y[1]


def _charnum_to_num(s: str) -> Tuple[int, int]:
    return ord(s[0].lower()) - 97, int(s[1:]) - 1


def _num_to_charnum(s: Tuple[int, int]) -> str:
    return f'{string.ascii_lowercase[s[0]]}{s[1] + 1}'


def add_vector_to_point(point, vector):
    if isinstance(point, str):
        point = _charnum_to_num(point)
        return _num_to_charnum(_add_two_tuples(point, vector))
    else:
        return _add_two_tuples(point, vector)


class CharNumGrid(Grid):

    def __init__(self, x: int, y: int):
        if x > 26:
            raise ValueError("This won't work with x > 26")
        super().__init__(x, y)

    def __getitem__(self, key: str):
        return super().__getitem__(_charnum_to_num(key))

    def __setitem__(self, key: str, val):
        super().__setitem__(_charnum_to_num(key), val)
