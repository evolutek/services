#!/usr/bin/env python3

from collections import deque
from copy import deepcopy
from enum import Enum
import json
from math import ceil, sqrt, inf
from evolutek.lib.point import Point

class ObstacleType(Enum):
    fixed = 0
    color = 1
    robot = 2

class Square:

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
        s = "Square:\n"
        s += str(self.obstacles) + "\n"
        s += str(self.robots) + "\n"
        return s

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

class RectangleObstacle(Obstacle):

    def __init__(self, x1, x2, y1, y2, tag=None, type=ObstacleType.fixed):
        super().__init__(tag, type)
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


    """ UTILITIES """

    def is_real_point_outside(self, x, y):
        return x < 0 or y < 0 or x > self.real_height or y > self.real_width

    def is_real_point_outside_point(self, p):
        return self.is_point_inside(p.x, p.y)

    def is_point_inside(self, p):
        return p.x >= 0 and p.x <= self.height and p.y >= 0 and p.y <= self.width

    def convert_point(self, x, y):
        return Point(int(x/self.unit), int(y/self.unit))

    def convert_point_point(self, p):
        return self.convert_point(p.x, p.y)

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

    def add_point_obstacle(self, x, y, tag=None, type=ObstacleType.fixed):
        if self.is_real_point_outside(x, y):
            return False
        obs = Obstacle(tag, type)
        p = self.convert_point(x, y)
        obs.points.append(p)
        return self.add_obstacle(obs)

    def add_circle_obstacle(self, x, y, radius=0, tag=None, type=ObstacleType.fixed):
        if self.is_real_point_outside(x, y):
            return False
        obs = CircleObstacle(self.convert_point(x, y), int((radius + self.robot_radius)/self.unit), tag=tag, type=type)
        return self.add_obstacle(obs)

    def add_circle_obstacle_point(self, p, radius=0, tag=None, type=ObstacleType.fixed):
        return self.add_circle_obstacle(p.x, p.y, radius=radius, tag=tag, type=type)

    def add_rectangle_obstacle(self, x1, x2, y1, y2, tag=None, type=ObstacleType.fixed):
        if self.is_real_point_outside(x1, y1) or self.is_real_point_outside(x2, y2):
            return False
        _x1 = int((min(x1, x2) - self.robot_radius) /self.unit)
        _x2 = int((max(x1, x2) + self.robot_radius) /self.unit)
        _y1 = int((min(y1, y2) - self.robot_radius) /self.unit)
        _y2 = int((max(y1, y2) + self.robot_radius) /self.unit)
        return self.add_obstacle(RectangleObstacle(_x1, _x2, _y1, _y2, tag=tag, type=type))

    def add_rectangle_obstacle_point(self, p1, p2, tag=None, type=ObstacleType.fixed):
        return self.add_rectangle_obstacle(p1.x, p2.x, p1.y, p2.y, tag=tag, type=type)

    def add_boundaries(self):
        radius = int(self.robot_radius / self.unit)
        for x in range(radius, self.height - radius + 1):
            self.map[x][radius].add_obstacle('add_boundaries', ObstacleType.fixed)
            self.map[x][self.width - radius].add_obstacle('boundaries', ObstacleType.fixed)
        for y in range(radius, self.width - radius):
            self.map[radius][y].add_obstacle('add_boundaries', ObstacleType.fixed)
            self.map[self.height - radius][y].add_obstacle('boundaries', ObstacleType.fixed)

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

    def is_inside_fixed_obstacle(self, point):
        for obstacle in self.obstacles:
            if obstacle.type != ObstacleType.fixed:
                continue
            if isinstance(obstacle, RectangleObstacle):
                if point.x >= obstacle.x1 and point.x <= obstacle.x2 and\
                    point.y >= obstacle.y1 and point.y <= obstacle.y2:
                    return True
            elif isinstance(obstacle, CircleObstacle):
                if point.dist(obstacle.center) <= obstacle.radius:
                    return True
        return False

    def is_inside_obstacle(self, point):
        for obstacle in self.obstacles:
            if isinstance(obstacle, RectangleObstacle):
                if point.x >= obstacle.x1 and point.x <= obstacle.x2 and\
                    point.y >= obstacle.y1 and point.y <= obstacle.y2:
                    return True
            elif isinstance(obstacle, CircleObstacle):
                if point.dist(obstacle.center) <= obstacle.radius:
                    return True
        return False

    @staticmethod
    def parse_obstacle_file(file):
        with open(file, 'r') as obstacle_file:
            data = obstacle_file.read()

        data = json.loads(data)

        fixed = data['fixed_obstacles']
        color = data['color_obstacles']

        return fixed, color

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
                self.add_rectangle_obstacle_point(**obstacle, type=type)
            elif form == 'circle':
                if not 'p' in obstacle:
                    print('Bad circle obstacle in parsing')
                    continue
                obstacle['p'] = Point.from_dict(obstacle['p'])
                if mirror:
                    obstacle['p'].y = 3000 - obstacle['p'].y
                self.add_circle_obstacle_point(**obstacle, type=type)

            else:
                print('Obstacle form not found')

    def print_obstacles(self):
        for obstacle in self.obstacles:
            print(obstacle)

    """ PATHFNDING """

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
                distance = dist[cur.x][cur.y] + cur.dist(neighbour)
                if distance < dist[neighbour.x][neighbour.y]:
                    dist[neighbour.x][neighbour.y] = distance
                    queue.append(neighbour)
                    pred[neighbour] = cur

        path = []
        if end in pred:
            cur = end
            path.append(end)
            while pred[cur] in pred:
                cur = pred[cur]
                path.insert(0, cur)
            path.insert(0, start)
            print('Complete Dijkstra')
        else:
            print("Target obstructed")

        path  = self.path_opti(self.smooth(path))
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
            if (not (n2.x - n3.x == n1.x - n2.x and n2.y - n3.y == n1.y - n2.y)):
                chemin.append(n2)
            n3 = n2
            n2 = n1
        chemin.append(path[-1])
        return chemin

    def path_opti(self,path):
        if (len(path)<=2):
            print("lenpath<2")
            return path

        n1 = path[0]
        n2 = path[1]
        n3 = path[2]
        new = [n1]
        i=2

        while (i<len(path)):
            n3 = path[i]
            mini = n2
            for j in range(i+1,len(path)):
                if(self.is_correct_trajectory(n1,n3)):
                    mini = n3
                    i = j
                n2 = n3
                n3 = path[j]
            new.append(mini)
            n2 = path[i]
            n1 = mini
            i+=1

        new.append(n3)
        return new

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


    # FIXME: can cross line
    def is_correct_trajectory(self, p1, p2):

        if p1 == p2:
            return True

        # Compute 2nd degree equation between two points
        dy = False
        a = 0
        b = 0

        p1, p2 = Point.min(p1, p2), Point.max(p1, p2)
        start = Point(p1.x * self.unit, p1.y * self.unit)
        end = Point(p2.x * self.unit, p2.y * self.unit)

        # If x1 = x2 make equation depend on y
        if start.x == end.x:
            dy = True
            a = (end.x - start.x) / (end.y - start.y)
            b = start.x - a * start.y
        else:
            a = (end.y - start.y) / (end.x - start.x)
            b = start.y - a * start.x

        # Nb of point to visit
        l = (end.x - start.x) if not dy else (end.y - start.y)

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

            p = self.convert_point(x, y)

            # Check if the current point is empty
            if self.is_inside_obstacle(p):
                return False
        return True

    def convert_path(self, path):
        l = []
        for p in path:
            l.append({'x': p.x * self.unit, 'y': p.y * self.unit})
        return l
