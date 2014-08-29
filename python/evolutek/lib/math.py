from math import hypot
from collections import namedtuple


# http://stackoverflow.com/questions/19458291/efficient-vector-point-class-in-python
class Vector2D(namedtuple('Vector2D', ('x', 'y'))):

    def __abs__(self):
        return type(self)(abs(self.x), abs(self.y))

    def __int__(self):
        return type(self)(int(self.x), int(self.y))

    def __add__(self, other):
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return type(self)(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return type(self)(self.x * other, self.y * other)

    def __div__(self, other):
        return type(self)(self.x / other, self.y / other)

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        """Uses the Euclidean norm to calculate the distance."""
        return hypot((self.x - other.x), (self.y - other.y))
