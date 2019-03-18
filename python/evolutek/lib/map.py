#!/usr/bin/env python3

from collections import deque
from copy import deepcopy
from enum import Enum
from math import ceil, sqrt, inf
from evolutek.lib.point import Point

class Obstacle:

    def __init__(self, tag=None, color="black"):
        self.points = []
        self.tag = tag
        self.color = color

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
        self.y1 = y1
        self.y2 = y2
        for x in range(x1, x2 + 1):
            self.points.append(Point(x, y1))
        for y in range(y1 + 1, y2):
            self.points.append(Point(x2, y))
        for x in range(x2, x1 - 1, -1):
            self.points.append(Point(x, y2))
        for y in range(y2 - 1, y1, -1):
            self.points.append(Point(x1, y))

class Map:

    def __init__(self, width, height, unit, robot_radius):
        self.real_width = width
        self.real_height = height
        self.width = int(width / unit)
        self.height = int(height / unit)
        self.unit = unit
        self.robot_radius = robot_radius

        self.map = []
        self.obstacles = []

        for x in range(self.height + 1):
            self.map.append([])
            for y in range(self.width + 1):
                self.map[x].append(0)

        self.add_boundaries()

    def is_real_point_outside(self, x, y):
        return x < 0 or y < 0 or x > self.real_height or y > self.real_width

    def is_point_inside(self, p):
        return p.x >= 0 and p.x <= self.height and p.y >= 0 and p.y <= self.width

    def convert_point(self, x, y):
        return Point(int(x/self.unit), int(y/self.unit))

    def add_point_obstacle(self, x, y, tag=None):
        if self.is_real_point_outside(x, y):
            return False
        obs = Obstacle(tag)
        x = int(x / self.unit)
        y = int(y / self.unit)
        obs.points.append(Point(x, y))
        self.map[x][y] += 1
        self.obstacles.append(obs)

    def add_circle_obstacle(self, x, y, radius=0, tag=None):
        if self.is_real_point_outside(x, y):
            return False
        obs = CircleObstacle(self.convert_point(x, y), int((radius + self.robot_radius)/self.unit), tag=tag)
        for p in obs.points:
            if self.is_point_inside(p):
                self.map[p.x][p.y] += 1
        self.obstacles.append(obs)
        return True

    def add_rectangle_obstacle(self, x1, x2, y1, y2, tag=None):
        if self.is_real_point_outside(x1, y1) or self.is_real_point_outside(x2, y2):
            return False
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        x1 = int((x1 - self.robot_radius) /self.unit)
        x2 = int((x2 + self.robot_radius) /self.unit)
        y1 = int((y1 - self.robot_radius) /self.unit)
        y2 = int((y2 + self.robot_radius) /self.unit)
        obs = RectangleObstacle(x1, x2, y1, y2, tag=tag)
        for p in obs.points:
            if self.is_point_inside(p):
                self.map[p.x][p.y] += 1
        self.obstacles.append(obs)
        return True

    def add_boundaries(self):
        radius = int(self.robot_radius / self.unit)
        for x in range(radius, self.height - radius + 1):
            self.map[x][radius] += 1
            self.map[x][self.width - radius] += 1
        for y in range(radius, self.width - radius):
            self.map[radius][y] += 1
            self.map[self.height - radius][y] += 1

    def remove_obstacle(self, tag):
        for obs in self.obstacles:
            if obs == tag:
                for p in obs.points:
                    if self.is_point_inside(p):
                        self.map[p.x][p.y] -= 1
                self.obstacles.remove(obs)
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

    def get_path(self, p1, p2):
        if self.is_real_point_outside(p1.x, p1.y) or self.is_real_point_outside(p2.x, p2.y):
            print('Out of map')
            return []

        start = self.convert_point(p1.x, p1.y)
        end = self.convert_point(p2.x, p2.y)

        if self.map[start.x][start.y] > 0 or self.map[end.x][end.y] > 0:
            print('Obstacle here')
            return []

        dist = []
        for x in range(self.height + 1):
            dist.append([])
            for y in range(self.width + 1):
                dist[x].append(inf)

        queue = deque()
        queue.append(start)
        dist[start.x][start.y] = 0

        pred = {}
        while len(queue) > 0:
            cur = queue.popleft()

            if cur == end:
                break

            neighbours = self.neighbours(cur, map)
            for neighbour in neighbours:
                distance = dist[cur.x][cur.y] + self.distance(cur, neighbour)
                if distance < dist[neighbour.x][neighbour.y]:
                    dist[neighbour.x][neighbour.y] = distance
                    queue.append(neighbour)
                    pred[neighbour] = cur

        print('Complete Dijkstra')

        path = []
        if end in pred:
            cur = end
            p = end.to_dict()
            path.append({'x': p['x'] * self.unit, 'y': p['y'] * self.unit})
            while pred[cur] in pred:
                cur = pred[cur]
                p = cur.to_dict()
                path.insert(0, {'x': p['x'] * self.unit, 'y': p['y'] * self.unit})
            p = start.to_dict()
            path.insert(0, {'x': p['x'] * self.unit, 'y': p['y'] * self.unit})
        #TODO: linearize path

        return path

    def neighbours(self, p, map):
        l = [
            Point(p.x - 1, p.y),
            Point(p.x + 1, p.y),
            Point(p.x, p.y - 1),
            Point(p.x, p.y + 1)
        ]

        neighbours = []
        for point in l:
            if self.is_point_inside(point) and self.map[point.x][point.y] == 0:
                    neighbours.append(point)

        return neighbours

    def distance(self, p1, p2):
        #TODO: COST
        return p1.dist(p2)
