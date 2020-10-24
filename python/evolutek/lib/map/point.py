from math import sqrt
from shapely.geometry import Point as PointShape

# Point class
# Inherit form PointShape class from shapely
class Point(PointShape):

    # Init of the class
    # tuple: init the point from the tuple
    # dict : init the point from a dict
    def __init__(self, x=0, y=0, tuple=None, dict=None):
        if tuple is not None:
            super().__init__(tuple)
        elif dict is not None:
            super().__init__(round(dict['x']), round(dict['y']))
        else:
            super().__init__(round(x, 3), round(y, 3))

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

    # Compute the eculidian dist between two point in dict
    @staticmethod
    def dist_dict(p1, p2):
        return sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

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
        tot_x = 0
        tot_y = 0
        for p in l:
            tot_x += p.x
            tot_y += p.y
        return Point(tot_x / len(l), tot_y / len(l))

    # Substract two points
    @staticmethod
    def substract(p1, p2):
        return Point(p1.x - p2.x, p1.y - p2.y)
