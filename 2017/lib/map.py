from math import cos, sin, hypot, pi
from collections import namedtuple


# http://stackoverflow.com/questions/19458291/efficient-vector-point-class-in-python
class Vector2(namedtuple('Vector2', ('x', 'y'))):

    def __abs__(self):
        return type(self)(abs(self.x), abs(self.y))

    def __add__(self, other):
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return type(self)(self.x - other.x, self.y - other.y)

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        """Uses the Euclidean norm to calculate the distance."""
        return hypot((self.x - other.x), (self.y - other.y))

    def rotated_by(self, theta):
        return type(self)(x=self.x*cos(-theta) - self.y*sin(-theta),
                          y=self.x*sin(-theta) + self.y*cos(-theta))


class Vector3(namedtuple('Vector3', ('x', 'y', 'theta'))):

    def __abs__(self):
        return type(self)(abs(self.x), abs(self.y), self.theta % (2*pi))

    def __add__(self, other):
        return type(self)(self.x + other.x, self.y + other.y,
                          (self.theta + other.theta) % (2*pi))

    def __sub__(self, other):
        return type(self)(self.x - other.x, self.y - other.y,
                          (self.theta - other.theta) % (2*pi))

    def distance_to(self, other):
        """Uses the Euclidean norm to calculate the distance."""
        return hypot((self.x - other.x), (self.y - other.y))

    def rotated_by(self, theta):
        return type(self)(x=self.x*cos(-theta) - self.y*sin(-theta),
                          y=self.x*sin(-theta) + self.y*cos(-theta),
                          theta=(self.theta + theta) % (2*pi))

    def to_2(self):
        return Vector2(x=self.x, y=self.y)


class Map:
    @staticmethod
    def inside(vec: 'Vector2', margin=0):
        """
        Returns true if the point is inside the map.

        :param int margin: if positive: margin inside the map, else outside
        """
        return not (vec.x - margin < 0
                    or vec.x + margin > 3000
                    or vec.y - margin < 0
                    or vec.y + margin > 2000)


class Circle(namedtuple('Circle', 'x y r')):
    def contains(self, vec: 'Vector2'):
        center = Vector2(self.x, self.y)
        return center.distance_to(vec) <= self.r
