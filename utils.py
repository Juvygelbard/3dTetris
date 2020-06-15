import numpy as np
from itertools import product
from engine import Position, Cube


def product_idx(idx):
    l = [list(range(i)) for i in idx]
    for p in product(*l):
        yield p


class Element:
    def __init__(self, X, Y, Z, color):
        self.X, self.Y, self.Z = X, Y, Z
        self.box = Cube(Position(X + 0.5, Y, Z + 0.5, 0, 0, 0), 1, color)

    def set_position(self, X, Y, Z):
        self.X, self.Y, self.Z = X, Y, Z
        self.box.set_position(X + 0.5, Y, Z + 0.5, 0, 0, 0)

    def move(self, dX, dY, dZ):
        self.X += dX
        self.Y += dY
        self.Z += dZ
        self.box.move(dX, dY, dZ, 0, 0, 0)


class Shape:
    AXIS = ((0, 1),
            (1, 2),
            (0, 2))

    def __init__(self, src, color, X, Y, Z):
        self.X, self.Y, self.Z = X, Y, Z
        self._shape = np.shape(src)
        self._map = np.full(self._shape, -1, dtype=np.int8)
        self._elements = list()
        idx = 0
        for i, j, k in product_idx(self._shape):
            if src[i, j, k] != 0:
                self._map[i, j, k] = idx
                idx += 1
                self._elements.append(Element(i + X, j + Y, k + Z, color))

    def elements(self):
        return self._elements

    def iterate(self):
        for i, j, k in product_idx(self._shape):
            idx = self._map[i, j, k]
            if idx >= 0:
                yield self._elements[idx].X, self._elements[idx].Y, self._elements[idx].Z

    def rotate(self, axis, n):
        self._map = np.rot90(self._map, n, Shape.AXIS[axis])
        for i, j, k in product_idx(self._shape):
            idx = self._map[i, j, k]
            if idx >= 0:
                self._elements[idx].set_position(i + self.X, j + self.Y, k + self.Z)

    def move(self, dX, dY, dZ):
        self.X += dX
        self.Y += dY
        self.Z += dZ
        for e in self._elements:
            e.move(dX, dY, dZ)