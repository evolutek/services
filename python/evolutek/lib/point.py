from math import sqrt

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ', ' + str(self.y) + ")"

    def __eq__(self, p):
        return self.x == p.x and self.y == p.y

    def __hash__(self):
        return hash(str(self))

    def to_dict(self):
        return {'x': self.x, 'y': self.y,}

    def dist(self, p):
        if isinstance(p, dict):
            return sqrt((p['x'] - self.x) ** 2 + (p['y'] - self.y) ** 2)
        return sqrt((p.x - self.x) ** 2 + (p.y - self.y) ** 2)

    def average(self, p):
        """ return the average between two points """
        return Point((self.x + p.x) // 2, (self.y + p.y) // 2)

    @staticmethod
    def from_dict(p):
        return Point(int(p['x']), int(p['y']))

    @staticmethod
    def dist_dict(p1, p2):
        return sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

    @staticmethod
    def min(p1, p2):
        if p1.x == p2.x:
            return p1 if p1.y < p2.y else p2
        return p1 if p1.x < p2.x else p2

    @staticmethod
    def max(p1, p2):
        if p1.x == p2.x:
            return p1 if p1.y > p2.y else p2
        return p1 if p1.x > p2.x else p2

    @staticmethod
    def mean(l):
        """ return the mean of a point list """
        tot_x = 0
        tot_y = 0
        for p in l:
            tot_x += p.x
            tot_y += p.y
        return Point(int(tot_x / len(l)), int(tot_y / len(l)))
