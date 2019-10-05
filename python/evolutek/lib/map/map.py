#!/usr/bin/env python3

from copy import deepcopy
from enum import Enum
from math import ceil, sqrt
from evolutek.lib.map.obstacle import ObstacleType, Obstacle, CircleObstacle, RectangleObstacle
from evolutek.lib.map.point import Point

class Cell:

    def __init__(self, fixed_obstacles=None, color_obstacles=None, robots=None):
        self.fixed_obstacles = [] if fixed_obstacles is None else fixed_obstacles
        self.color_obstacles = [] if color_obstacles is None else color_obstacles
        self.robots = [] if robots is None else robots

    def add_obstacle(self, obstacle, type):
        if type == ObstacleType.fixed and not obstacle in self.fixed_obstacles:
            self.fixed_obstacles.append(obstacle)
            return True
        elif type == ObstacleType.color and not obstacle in self.color_obstacles:
            self.color_obstacles.append(obstacle)
            return True
        elif type == ObstacleType.robot and not obstacle in self.robots:
            self.robots.append(obstacle)
            return True
        return False

    def remove_obstacle(self, obstacle):
        if obstacle in self.fixed_obstacles:
            self.fixed_obstacles.remove(obstacle)
            return True
        if obstacle in self.color_obstacles:
            self.color_obstacles.remove(obstacle)
            return True
        elif obstacle in self.robots:
            self.robots.remove(obstacle)
            return True
        return False

    def is_obstacle(self):
        return len(self.fixed_obstacles) > 0 or len(self.color_obstacles) > 0

    def is_color(self):
        return len(self.color_obstacles) > 0

    def is_robot(self):
        return len(self.robots) > 0

    def is_empty(self):
        return not self.is_robot() and not self.is_obstacle()

    def __str__(self):
        s = "Cell:\n"
        s += str(self.obstacles) + "\n"
        s += str(self.robots) + "\n"
        return s


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
                self.map[x].append(Cell())

        self.add_boundaries()


    """ UTILITIES """

    def is_real_point_outside(self, p):
        return p.x < 0 or p.y < 0 or p.x > self.real_height or p.y > self.real_width

    def is_point_inside(self, p):
        return p.x >= 0 and p.x <= self.height and p.y >= 0 and p.y <= self.width

    def convert_point(self, p):
        return Point(int(p.x/self.unit), int(p.y/self.unit))

    def print_map(self):
        print('-' * (self.width + 2))
        for x in range(self.height + 1):
            s = "|"
            for y in range(self.width + 1):
                s += self.map[x][y]
            s += "|"
            print(s)
        print('-' * (self.width + 2))


    """ OBSTACLES """

    def add_obstacle(self, obstacle):
        added = False
        for p in obstacle.points:
            if self.is_point_inside(p):
                added = True
                self.map[p.x][p.y].add_obstacle(obstacle.tag, obstacle.type)
        if added:
            self.obstacles.append(obstacle)
        return added

    def remove_obstacle(self, tag):
        if tag is None:
            return False
        for obs in self.obstacles:
            if obs == tag:
                for p in obs.points:
                    if self.is_point_inside(p):
                        self.map[p.x][p.y].remove_obstacle(tag)
                self.obstacles.remove(obs)
                return True
        return False

    def add_boundaries(self):
        radius = int(self.robot_radius / self.unit)
        for x in range(radius, self.height - radius + 1):
            self.map[x][radius].add_obstacle('add_boundaries', ObstacleType.fixed)
            self.map[x][self.width - radius].add_obstacle('boundaries', ObstacleType.fixed)
        for y in range(radius, self.width - radius):
            self.map[radius][y].add_obstacle('add_boundaries', ObstacleType.fixed)
            self.map[self.height - radius][y].add_obstacle('boundaries', ObstacleType.fixed)

    def is_inside_fixed_obstacle(self, point):
        for obstacle in self.obstacles:
            if obstacle.type != ObstacleType.fixed:
                continue
            if isinstance(obstacle, RectangleObstacle):
                if point.x >= obstacle.p1.x and point.x <= obstacle.p1.x and\
                    point.y >= obstacle.p2.y and point.y <= obstacle.p2.y:
                    return True
            elif isinstance(obstacle, CircleObstacle):
                if point.dist(obstacle.center) <= obstacle.radius:
                    return True
        return False

    def is_inside_obstacle(self, point):
        for obstacle in self.obstacles:
            if isinstance(obstacle, RectangleObstacle):
                if point.x >= obstacle.p1.x and point.x <= obstacle.p2.x and\
                    point.y >= obstacle.p1.y and point.y <= obstacle.p2.y:
                    return True
            elif isinstance(obstacle, CircleObstacle):
                if point.dist(obstacle.center) <= obstacle.radius:
                    return True
        return False

    def add_obstacles(self, obstacles, mirror=False, type=ObstacleType.fixed):
        obstacles = deepcopy(obstacles)
        for obstacle in obstacles:

            if 'type' in obstacle:
                try:
                    obstacle['type'] = eval(obstacle['type'])
                except Exception as e:
                    print('Bad obstacle type: %s' % (str(e)))
                    continue

            if not 'form' in obstacle:
                print('No form in obstacle')
                continue
            form = obstacle['form']
            del obstacle['form']

            if form == 'rectangle':
                if not 'p1' in obstacle or not 'p2' in obstacle:
                    print('Bad rectangle obstacle in parsing')
                    continue
                obstacle['p1'] = Point.from_dict(obstacle['p1'])
                obstacle['p2'] = Point.from_dict(obstacle['p2'])
                if mirror:
                    obstacle['p1'].y = 3000 - obstacle['p1'].y
                    obstacle['p2'].y = 3000 - obstacle['p2'].y
                self.add_rectangle_obstacle(**obstacle, type=type)
            elif form == 'circle':
                if not 'p' in obstacle:
                    print('Bad circle obstacle in parsing')
                    continue
                obstacle['p'] = Point.from_dict(obstacle['p'])
                if mirror:
                    obstacle['p'].y = 3000 - obstacle['p'].y
                self.add_circle_obstacle(**obstacle, type=type)

            else:
                print('Obstacle form not found')

    def print_obstacles(self):
        for obstacle in self.obstacles:
            print(obstacle)

    def add_point_obstacle(self, p, tag=None, type=ObstacleType.fixed):
        if self.is_real_point_outside(p):
            return False
        obs = Obstacle(tag, type)
        _p = self.convert_point(p)
        obs.points.append(_p)
        return self.add_obstacle(obs)

    def add_rectangle_obstacle(self, p1, p2, tag=None, type=ObstacleType.fixed):
        if self.is_real_point_outside(p1) or self.is_real_point_outside(p2):
            return False
        _x1 = int((min(p1.x, p2.x) - self.robot_radius) / self.unit)
        _x2 = int((max(p1.x, p2.x) + self.robot_radius) / self.unit)
        _y1 = int((min(p1.y, p2.y) - self.robot_radius) / self.unit)
        _y2 = int((max(p1.y, p2.y) + self.robot_radius) / self.unit)
        return self.add_obstacle(RectangleObstacle(Point(_x1, _y1), Point(_x2, _y2), tag=tag, type=type))

    def add_circle_obstacle(self, p, radius=0, tag=None, type=ObstacleType.fixed):
        if self.is_real_point_outside(p):
            return False
        obs = CircleObstacle(self.convert_point(p), int((radius + self.robot_radius)/self.unit), tag=tag, type=type)
        return self.add_obstacle(obs)
