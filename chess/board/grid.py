"""Affine field maths; no references to chess (except in this docstring)"""
from typing import Iterable, Any, Tuple, NamedTuple, List
import string
import math
from .utils import sign


class Loc(NamedTuple):
    x: int = 0
    y: int = 0

    @property
    def charnum(self) -> str:
        return f'{string.ascii_lowercase[self.x]}{self.y + 1}'

    @classmethod
    def from_charnum(cls, charnum: str):
        return cls(ord(charnum[0].lower()) - 97, int(charnum[1:]) - 1)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)


class Vector(NamedTuple):
    x: int = 0
    y: int = 0

    @property
    def unit_l1(self):
        return self.__class__(x=sign(self.x), y=sign(self.y))

    @property
    def norm_linf(self):
        return max(abs(self.x), abs(self.y))

    @property
    def unit_l2(self):
        return self / self.norm_l2

    @property
    def norm_l2(self) -> float:
        return math.sqrt((self.x ** 2) + (self.y ** 2))

    def __add__(self, other):
        return other.__class__(other.x + self.x, other.y + self.y)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __truediv__(self, other):
        return self.__class__(self.x / other, self.y / other)

    def __mul__(self, other):
        return self.__class__(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__class__(self.x * other, self.y * other)


class Grid(object):

    def __init__(self, x: int, y: int):
        self._mat = [[None for i in range(x)] for j in range(y)]

    def __getitem__(self, key: tuple):
        if key[0] < 0 or key[1] < 0:
            raise IndexError('Must use non-negative integers in index.')
        return self._mat[key[0]][key[1]]

    def __setitem__(self, key: tuple, val: Any):
        if key[0] < 0 or key[1] < 0:
            raise IndexError('Must use non-negative integers in index.')
        self._mat[key[0]][key[1]] = val

    def __len__(self):
        x, y = self.dimensions
        return x * y

    @property
    def dimensions(self) -> Tuple[int, int]:
        return len(self._mat), len(self._mat[0])

    def move_from_to(
            self,
            loc: Any,
            to: Any,
            overwrite: bool = False
    ):
        if self[to] is None or overwrite:
            self[loc], self[to] = None, self[loc]
        else:
            raise ValueError(f'Location {tuple(to)} is not empty.')
        return self

    def peek(self, loc: Loc, amount: Vector):
        return self[loc + amount]

    def shift(self, loc: Loc, amount: Vector, **kwargs):
        return self.move_from_to(
            Loc(*loc), Loc(*loc) + Vector(*amount),
            **kwargs
        )

    def clear(self):
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                self.__setitem__(Loc(i, j), None)

    @property
    def is_empty(self):
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                if self.__getitem__(Loc(i, j)) is not None:
                    return False
        else:
            return True

    def __repr__(self):
        return '\n'.join([str(i) for i in self._mat])

    def __iter__(self):
        return self

    def _loc(self, val: int) -> Loc:
        return Loc(val // self.dimensions[0], val % self.dimensions[1])

    def __next__(self):
        try:
            self._idx += 1
        except AttributeError:
            self._idx = 0
        if self._idx >= len(self):
            raise StopIteration
        return self[self._loc(self._idx)]

    @property
    def positions(self) -> list:
        return [self._loc(i) for i in range(len(self))]


class CharNumGrid(Grid):

    def __init__(self, x: int, y: int):
        if x > 26:
            raise ValueError("This won't work with x > 26")
        super().__init__(x, y)

    def __getitem__(self, key: str) -> Any:
        if isinstance(key, tuple):
            return super().__getitem__(key)
        else:
            return super().__getitem__(Loc.from_charnum(key))

    def __setitem__(self, key: str, val) -> None:
        if isinstance(key, tuple):
            super().__setitem__(key, val)
        else:
            super().__setitem__(Loc.from_charnum(key), val)

    def shift(self, loc: Loc, amount: Vector, **kwargs):
        if isinstance(loc, tuple):
            return super().shift(loc, amount, **kwargs)
        else:
            return super().shift(Loc.from_charnum(loc), amount, **kwargs)

    def _loc(self, val: int) -> str:
        return super()._loc(val).charnum

    def peek(self, loc: str, amount: Vector):
        if isinstance(loc, tuple):
            return super().peek(loc, amount)
        else:
            return super().peek(Loc.from_charnum(loc), amount)


def decompose(vector: Vector) -> List[Vector]:
    if abs(vector.x) != abs(vector.y) and vector.x != 0 and vector.y != 0:
        raise ValueError
    return [vector.unit_l1 * i for i in range(1, vector.norm_linf + 1)]
