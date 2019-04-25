#!/usr/bin/env python3

from collections import deque
from copy import deepcopy
from enum import Enum
from math import ceil, sqrt, inf
from evolutek.lib.point import Point

class ObstacleType(Enum):
    obstacle = 0
    robot = 1

class Square:

    def __init__(self, obstacles=None, robots=None):
        self.obstacles = [] if obstacles is None else obstacles
        self.robots = [] if robots is None else robots

    def add_obstacle(self, obstacle, type):
        if type == ObstacleType.obstacle and not obstacle in self.obstacles:
            self.obstacles.append(obstacle)
            return True
        elif type == ObstacleType.robot and not obstacle in self.robots:
            self.robots.append(obstacle)
            return True
        return False

    def remove_obstacle(self, obstacle):
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)
            return True
        elif obstacle in self.robots:
            self.robots.remove(obstacle)
            return True
        return False

    def is_obstacle(self):
        return len(self.obstacles) > 0

    def is_robot(self):
        return len(self.robots) > 0

    def is_empty(self):
        return len(self.obstacles) == 0 and len(self.robots) == 0

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
                self.map[x].append(Square())

        self.add_boundaries()

    def is_real_point_outside(self, x, y):
        return x < 0 or y < 0 or x > self.real_height or y > self.real_width

    def is_point_inside(self, p):
        return p.x >= 0 and p.x <= self.height and p.y >= 0 and p.y <= self.width

    def convert_point(self, x, y):
        return Point(int(x/self.unit), int(y/self.unit))

    def add_point_obstacle(self, x, y, tag=None, type=ObstacleType.obstacle):
        if self.is_real_point_outside(x, y):
            return False
        obs = Obstacle(tag)
        x = int(x / self.unit)
        y = int(y / self.unit)
        obs.points.append(Point(x, y))
        self.map[x][y].add_obstacle(tag, type)
        self.obstacles.append(obs)

    def add_circle_obstacle(self, x, y, radius=0, tag=None, type=ObstacleType.obstacle):
        if self.is_real_point_outside(x, y):
            return False
        obs = CircleObstacle(self.convert_point(x, y), int((radius + self.robot_radius)/self.unit), tag=tag)
        for p in obs.points:
            if self.is_point_inside(p):
                self.map[p.x][p.y].add_obstacle(tag, type)
        self.obstacles.append(obs)
        return True

    def add_rectangle_obstacle(self, x1, x2, y1, y2, tag=None, type=ObstacleType.obstacle):
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
                self.map[p.x][p.y].add_obstacle(tag, type)
        self.obstacles.append(obs)
        return True

    def add_boundaries(self):
        radius = int(self.robot_radius / self.unit)
        for x in range(radius, self.height - radius + 1):
            self.map[x][radius].add_obstacle('add_boundaries', ObstacleType.obstacle)
            self.map[x][self.width - radius].add_obstacle('boundaries', ObstacleType.obstacle)
        for y in range(radius, self.width - radius):
            self.map[radius][y].add_obstacle('add_boundaries', ObstacleType.obstacle)
            self.map[self.height - radius][y].add_obstacle('boundaries', ObstacleType.obstacle)

    def remove_obstacle(self, tag):
        for obs in self.obstacles:
            if obs == tag:
                for p in obs.points:
                    if self.is_point_inside(p):
                        self.map[p.x][p.y].remove_obstacle(tag)
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

        if not self.map[start.x][start.y].is_empty() or not self.map[end.x][end.y].is_empty():
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
            path.append(p)
            while pred[cur] in pred:
                cur = pred[cur]
                p = cur.to_dict()
                path.insert(0, p)
            p = start.to_dict()

            path.insert(0, p)

        #TODO: linearize path

        return self.convert_path(path)

    def smooth(self,path):
        if (len(path) <= 2):
            return path
        chemin = []
        n3 = path[0]
        n2 = path[1]

        chemin.append(path[0])
        for i in range(2,len(path)):
            n1 = path[i]
            if (not (n2['x'] - n3['x'] == n1['x'] - n2['x'] and n2['y'] - n3['y'] == n1['y'] - n2['y'])):
                chemin.append(n2)
            n3 = n2
            n2 = n1
        chemin.append(path[-1])
        return chemin

    def path_opti(self,path):
        if(len(path)<=2):
            return path
        cheminf = []
        n1 = path[0]
        n2 = path[1]

        cheminf.append(path[0])
        for i in range(2, len(path)):
            n3 = path[i]
            ctmp = self.smooth(self.get_path(Point(n1['x'],n1['y']),Point(n3['x'],n3['y'])))
            if (len(ctmp)<4 and ctmp[0] == n1 and ctmp[1] == n2 and ctmp[2] == n3):
                cheminf.append(n2)
            else:
                n1 = n2
            n2 = n3
        cheminf.append(path[-1])
        return cheminf

    def neighbours(self, p, map):
        l = [
                Point(p.x - 1, p.y),
                Point(p.x + 1, p.y),
                Point(p.x, p.y - 1),
                Point(p.x, p.y + 1)
                ]

        neighbours = []
        for point in l:
            if self.is_point_inside(point) and self.map[point.x][point.y].is_empty():
                neighbours.append(point)

        return neighbours

    def distance(self, p1, p2):
        #TODO: COST
        return p1.dist(p2)

    def is_correct_trajectory(self, p1, p2):

        # Compute 2nd degree equation between two points
        dy = False
        a = 0
        b = 0

        # If x1 = x2 make equation depend on y
        if p1.x == p2.x:
            dy = True
            a = (p2.x - p1.x) / (p2.y - p1.y)
            b = p1.x - a * p1.y
        else:
            a = (p2.y - p1.y) / (p2.x - p1.x)
            b = p1.y - a * p1.x

        start, end = Point.min(p1, p2), Point.max(p1, p2)

        # Nb of point to visit
        l = (end.x - start.x) if not y else (end.y - start.y)

        # Check if the line between the two points collide with something
        for i in range(1, l):
            x = 0
            y = 0
            if dy:
                y = start.y + i
                x = y * a + b
            else:
                x = start.x + i
                y = x * a + b
            p = Point(int(x), int(y))

            # Check if the current point is empty
            if not self.map[p.x][p.y].is_empty():
                return False
        return True

    def convert_path(self, path):
        l = []
        for p in path:
            l.append({'x': p.x * self.unit, 'y': p.y * self.unit})
        return l

