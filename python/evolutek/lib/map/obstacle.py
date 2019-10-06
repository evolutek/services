from enum import Enum
from evolutek.lib.map.point import Point

from math import sqrt, cos
import json

class ObstacleType(Enum):
    fixed = 0
    color = 1
    robot = 2

def is_colliding_lines(p1, p2, p3, p4):
    t0 = 0.0
    t1 = 1.0

    dx = p2.x - p1.x
    dy = p2.y - p1.y

    checks = ((-dx, -(p3.x - p1.x)),
            ( dx, p4.x - p1.x),
            (-dy, -(p4.y - p1.y)),
            ( dy, p3.y - p1.y))

    for p, q in checks:
        if p == 0 and q < 0:
            return False

    if p != 0:
        r = q / (p * 1.0)

        if p < 0:
            if r > t1:
                return False
            elif r > t0:
                t0 = r
        else:
            if r < t0:
                return False
            elif r < t1:
                t1 = r

    return True

class Obstacle:

    def __init__(self, tag=None, type=ObstacleType.fixed):
        self.points = []
        self.tag = tag
        self.type = type

    def __eq__(self, tag):
        return self.tag == tag

    def __str__(self):
        s = "--- Obstacle ---\n"
        s += "tag: %s\ntype: %s" % (self.tag, str(self.type))
        return s

    def is_inside(self, point):
        return point in self.points

    def is_colliding(self, p1, p2):
        return False

class CircleObstacle(Obstacle):

    def __init__(self, center, radius, tag=None, type=ObstacleType.fixed):
        super().__init__(tag, type)
        self.center = center
        self.radius = radius

        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                equa = ((center.x - x) - center.x)**2 + ((center.y - y) - center.y)**2
                if equa >= radius**2 - radius and equa <= radius**2 + radius:
                    self.points.append(Point(int(center.x - x), int(center.y - y)))

    def is_inside(self, point):
        return self.center.dist(point) <= self.radius

    def is_colliding(self, p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dr = sqrt(dx**2 + dy**2)
        d = p1.x * p2.y - p2.x * p1.y

        delta = self.radius**2 * dr **2 - d**2

        print(delta)
        print(self.radius)

        return delta <=0

class RectangleObstacle(Obstacle):

    def __init__(self, p1, p2, tag=None, type=ObstacleType.fixed):
        super().__init__(tag, type)
        self.p1 = p1
        self.p2 = p2
        for x in range(p1.x, p2.x + 1):
            self.points.append(Point(x, p1.y))
        for y in range(p1.y + 1, p2.y):
            self.points.append(Point(p2.x, y))
        for x in range(p2.x, p1.x - 1, -1):
            self.points.append(Point(x, p2.y))
        for y in range(p2.y - 1, p1.y, -1):
            self.points.append(Point(p1.x, y))

    def is_inside(self, point):
        return self.point.x >= self.p1.x and self.point.x <= self.p2.x and\
            self.point.y >= self.p1.y and self.point.y <= self.p2.y

    def is_colliding(self, p1, p2):
        return is_colliding_lines(p1, p2, self.p1, Point(self.p1.x, self.p2.y)) or\
            is_colliding_lines(p1, p2, self.p1, Point(self.p2.x, self.p1.y)) or\
            is_colliding_lines(p1, p2, self.p2, Point(self.p1.x, self.p2.y)) or\
            is_colliding_lines(p1, p2, self.p2, Point(self.p2.x, self.p1.y))

def parse_obstacle_file(file):
    with open(file, 'r') as obstacle_file:
        data = obstacle_file.read()

    data = json.loads(data)

    fixed = data['fixed_obstacles']
    color = data['color_obstacles']

    return fixed, color
