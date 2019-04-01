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
    def mean(l):
        """ return the mean of a point list """
        tot_x = 0
        tot_y = 0
        for p in l:
            tot_x += p.x
            tot_y += p.y
        return Point(int(tot_x / len(l)), int(tot_y / len(l)))
