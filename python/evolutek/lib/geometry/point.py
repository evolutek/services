from math import sqrt
from shapely.geometry import Point as PointShape

# Point class
# Inherit form PointShape class from shapely
class Point(PointShape):

    # Init of the class
    # tuple: init the point from the tuple
    # dict : init the point from a dict
    def __init__(self, x, y):
        super().__init__(round(x, 3), round(y, 3))

    @staticmethod
    def from_dict(dict):
        try:
            return Point(dict['x'], dict['y'])
        except Exception as e:
            print('Failed to create point : %s' % str(e))

    @staticmethod
    def from_tuple(dict):
        try:
            return Point(tuple[0], tuple[1])
        except Exception as e:
            print('Failed to create point : %s' % str(e))

    def __str__(self):
        return "(" + str(self.x) + ', ' + str(self.y) + ")"

    def __eq__(self, p):
        return self.x == p.x and self.y == p.y

    def __lt__(self, p):
        return self.x < p.x or self.y < p.y

    # Generate a hash of the point (used when putting the object in a dict)
    def __hash__(self):
        return hash(str(self))

    def __len__(self):
        return 0

    def to_dict(self):
        return {'x': round(self.x), 'y': round(self.y)}

    def to_tuple(self):
        return (self.x, self.y)

    # Compute the euclidian distance with another point
    def dist(self, p):
        return sqrt(self.sqrdist(p))

    def sqrdist(self, p):
        if isinstance(p, dict):
            return (p['x'] - self.x) ** 2 + (p['y'] - self.y) ** 2
        return (p.x - self.x) ** 2 + (p.y - self.y) ** 2

    # Compute the median point between two point
    def average(self, p):
        """ return the average between two points """
        return Point((self.x + p.x) / 2, (self.y + p.y) / 2)

    def round(self):
        return Point(round(self.x), round(self.y))

    # Compute the minimum point between two point
    @staticmethod
    def min(p1, p2):
        if p1.x == p2.x:
            return p1 if p1.y < p2.y else p2
        return p1 if p1.x < p2.x else p2

    # Compute the maximum point between two point
    @staticmethod
    def max(p1, p2):
        if p1.x == p2.x:
            return p1 if p1.y > p2.y else p2
        return p1 if p1.x > p2.x else p2

    # Compute the mean of a list of point
    @staticmethod
    def mean(l):
        sum_x = 0
        sum_y = 0

        for p in l:
            sum_x += p.x
            sum_y += p.y

        return Point(sum_x / len(l), sum_y / len(l))
