#!/usr/bin/env python3

from copy import deepcopy
from math import ceil, sqrt

wall = "X"
ground = " "

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x: %s, y:%s" % (str(self.x), str(self.y))

    def dist(self, p):
        return sqrt((self.x  - p.x) + (self.y  - p.y))

    def __eq__(self, p):
        return self.x == p.x and self.y == p.y

class Obstacle:

    def __init__(self, tag=None):
        self.points = []
        self.tag = tag

    def __eq__(self, tag):
        return self.tag == tag

class CircleObstacle(Obstacle):

    def __init__(self, center, radius, tag=None):
        super().__init__(tag)
        self.center = center
        self.radius = radius

        for x in range(-radius, radius + 1):
                for y in range(-radius, radius + 1):
                    equa = ((center.x - x) - center.x)**2 + ((center.y - y) - center.y)**2
                    if equa >= radius**2 - radius and equa <= radius**2 + radius:
                        self.points.append(Point(int(center.x - x), int(center.y - y)))

    def __str__(self):
        return "center: [%s], radius: %s" % (str(self.center), str(self.radius))

class RectangleObstacle(Obstacle):

    def __init__(self, x1, x2, y1, y2, tag=None):
        super().__init__(tag)
        self.x1 = x1
        self.x2 = x2
        if x1 > x2:
            x1, x2 = x2, x1
        self.y1 = y1
        self.y2 = y2
        if y1 > y2:
            y1, y2 = y2, y1

        for x in range(x1, x2 + 1):
            self.points.append(Point(x, y1))
        for y in range(y1 + 1, y2):
            self.points.append(Point(x2, y))
        for x in range(x2, x1 - 1, -1):
            self.points.append(Point(x, y2))
        for y in range(y2 - 1, y1, -1):
            self.points.append(Point(x1, y))

class Path:

    def __init__(self, begin, end):
        self.cost = 0
        self.begin = begin
        self.end = end
        self.path = []

    def add_point(self, p):
        self.path.append(p)

    def __str__(self):
        s = "Begin: (%s)\n" % str(self.begin)
        for p in self.path:
            s += "(%s)\n" % str(p)
        s += "End: (%s)" % str(self.end)
        return s

class Map:

    def __init__(self, width, height, unit):
        self.real_width = width
        self.real_height = height
        self.width = int(width / unit)
        self.height = int(height / unit)
        self.unit = unit
        self.map = []
        self.obstacles = []

        for x in range(self.height + 1):
            self.map.append([])
            for y in range(self.width + 1):
                self.map[x].append(ground)

    def add_circle_obstacle(self, x, y, radius, tag=None):
        if x - radius < 0 or y - radius < 0 or x + radius > self.real_height or y + radius > self.real_width:
            return False
        obs = CircleObstacle(Point(int(x/self.unit), (y/self.unit)), int(radius/self.unit), tag=tag)
        for p in obs.points:
            self.map[p.x][p.y] = wall
        self.obstacles.append(obs)
        return True

    def add_rectangle_obstacle(self, x1, x2, y1, y2, tag=None):
        if x1 < 0 or x1 > self.real_height or x2 < 0 or x2 > self.real_height \
            or y1 < 0 or y1 > self.real_width or y2 < 0 or y2 > self.real_width:
            return False
        x1 = int(x1/self.unit)
        x2 = int(x2/self.unit)
        y1 = int(y1/self.unit)
        y2 = int(y2/self.unit)
        obs = RectangleObstacle(x1, x2, y1, y2, tag=tag)
        for p in obs.points:
            self.map[p.x][p.y] = wall
        self.obstacles.append(obs)
        return True

    def add_boundaries(self, robot_radius):
        radius = int(robot_radius / self.unit)
        for x in range(radius, self.height - radius + 1):
            self.map[x][radius] = wall
            self.map[x][self.width - radius] = wall
        for y in range(radius, self.width - radius):
            self.map[radius][y] = wall
            self.map[self.height - radius][y] = wall

    def remove_obstacle(self, tag):
        for obs in self.obstacles:
            if obs == tag:
                for point in obs.points:
                    self.map[point.x][point.y] = ground
                return True
        return False

    def print_map(self):
        print('-' * (self.width + 2))
        for x in range(self.height + 1):
            s = "|"
            for y in range(self.width + 1):
                s += self.map[x][y]
            s += "|"
            print(s)
        print('-' * (self.width + 2))
