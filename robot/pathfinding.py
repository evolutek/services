#!/usr/bin/env python3

# Example:
#
# pf = Pathfinding(10, 10, 0)
# pf.AddObstacle(5, 5, 1)
# path = pf.GetPath(2, 5, 8, 5)
# for p in path:
#     print(str(p))
from math import sqrt, ceil, floor
from collections import namedtuple

from math import sqrt

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cost = 1
        self.parent = None
        self.g = None
        self.totalEstimatedCost = None

    def __eq__(self, p):
        return self.x == p.x and self.y == p.y

    def distance(self, p):
        dx = self.x - p.x
        dy = self.y - p.y
        return sqrt(dx**2 + dy**2)

    def multiply(self, nb):
        self.x *= nb
        self.y *= nb

    def __str__(self):
        return str(self.x) + ", " + str(self.y)

class Obstacle:
    def __init__(self, x, y, radius, tag = "No tag"):
        self.x = x
        self.y = y
        self.r = radius
        self.tag = tag

class Map:

    # Initializes a new map (with cost set to 1)
    def __init__(self, w, h, obstacleCost, robot_radius):
        self.w = w
        self.h = h
        self.obstacleCost = obstacleCost
        self.robot_radius = robot_radius
        self.map = []
        for i in range(0, self.w + 1):
            self.map.append([])
            for j in range(0, self.h + 1):
                self.map[i].append(Point(i, j))

    # Set the cost of a cell to an obstacle
    def SetObstacle(self, x, y):
        self.map[x][y].cost = self.obstacleCost

    # Returns a point of the map
    def GetPoint(self, x, y):
        return self.map[x][y]

    # Indicates if the robot can access a cell
    def IsBlocked(self, x, y):
        if (x < self.robot_radius
            or x > self.w - self.robot_radius
            or y < self.robot_radius
            or y > self.h - self.robot_radius):
            return True;
        return self.map[x][y].cost == self.obstacleCost

    # Returns all neighbors cell of p
    def GetNghbrs(self, p):
        n = []
        n.append(self.GetPointFromMap(p.x - 1, p.y))
        n.append(self.GetPointFromMap(p.x + 1, p.y))
        n.append(self.GetPointFromMap(p.x, p.y - 1))
        n.append(self.GetPointFromMap(p.x, p.y + 1))
        n.append(self.GetPointFromMap(p.x - 1, p.y - 1))
        n.append(self.GetPointFromMap(p.x - 1, p.y + 1))
        n.append(self.GetPointFromMap(p.x + 1, p.y - 1))
        n.append(self.GetPointFromMap(p.x + 1, p.y + 1))

        return [x for x in n if x is not None]

    # Return the requested cell if it is inside the map (None else)
    def GetPointFromMap(self, x, y):
        valid = (x >= self.robot_radius
                and x <= self.w - self.robot_radius
                and y >= self.robot_radius
                and y <= self.h - self.robot_radius)
        return self.map[x][y] if valid else None

    # Indicates if a line can join points a and b without obstacle
    def LineOfSight(self, a, b):
        x0 = a.x
        y0 = a.y
        x1 = b.x
        y1 = b.y
        dx = x1 - x0
        dy = y1 - y0
        f = 0

        if dx < 0:
            dx = -dx
            sx = -1
        else:
            sx = 1

        if dy < 0:
            dy = -dy
            sy = -1
        else:
            sy = 1

        if dx >= dy:
            while x0 != x1:
                f = f + dy
                if f >= dx:
                    if self.IsBlocked(x0 + ((sx - 1) // 2), y0 + ((sy - 1) // 2)):
                        return False;
                    y0 += sy
                    f -= dx
                if f != 0\
                        and self.IsBlocked(x0 + ((sx - 1) // 2), y0 + ((sy - 1) // 2)):
                    return False
                if dy == 0\
                        and self.IsBlocked(x0 + ((sx - 1) // 2), y0)\
                        and self.IsBlocked(x0 + ((sx - 1) // 2), y0 - 1):
                    return False
                x0 += sx
        else:
            while y0 != y1:
                f = f + dx
                if f >= dy:
                    if self.IsBlocked(x0 + ((sx - 1) // 2), y0 + ((sy - 1) // 2)):
                        return False
                    x0 += sx
                    f -= dy
                if f != 0\
                        and self.IsBlocked(x0 + ((sx - 1) // 2), y0 + ((sy - 1) // 2)):
                    return False
                if (dy == 0
                        and self.IsBlocked(x0, y0 + ((sy - 1) // 2))
                        and self.IsBlocked(x0 - 1, y0 + ((sy - 1) // 2))):
                    return False
                y0 += sy

        return True;


class Pathfinding:
    ### PUBLIC PART ###

    # Initializes the Pathfinding class
    def __init__(self, map_width, map_height, robot_radius):
        self.mapw = map_width
        self.maph = map_height
        self.obstacles = []
        self.robot_radius = robot_radius
        self.obstacleCost = 10000
        pass

    # Add an obstacle in the map
    def AddObstacle(self, x, y, radius, tag = "No tag"):
        self.obstacles.append(Obstacle(x, y, radius, tag))

    # Remove an obstacle located at a specified position
    def RemoveObstacleByPosition(self, x, y):
        self.obstacles = filter(lambda o: o.x != x or o.y != y, self.obstacles)

    # Remove an obstacle that has a specific tag
    def RemoveObstacleByTag(self, tag):
        self.obstacles = filter(lambda o: o.tag != tag, self.obstacles)

    # Clear all the obstacles in the map
    def ClearObstacles(self):
        self.obstacles.clear()

    # Compute the shortest path between (rx, ry) and (dx, dy).
    # Includes the initial position of the robot (first point) and the destination (last point).
    def GetPath(self, rx, ry, dx, dy):
        self.InitPathfinding(rx, ry, dx, dy)
        if self.ThetaStar():
            path = [Point(dx, dy)]
            current = self.dest.parent
            while current != self.robot:
                path.append(current)
                current = current.parent
            path.append(Point(rx, ry))

            path.reverse()
            for i in range (1, len(path) - 1):
                path[i].multiply(self.smallerRadius)
            #print("Path found (" + str(len(path)) + " points):");
            #for p in path:
            #    print(p.toString())

            return path
        else:
            #print("No path found.")
            return []

    # Compute the lenght of a path (given by GetPath)
    def PathLen(self, path):
        l = 0
        for i in range(0, len(path) - 1):
            l += path[i].distance(path[i + 1])
        return l

    ### PRIVATE PART ###

    # Create a new map with cost set to the obstacles
    def InitPathfinding(self, rx, ry, dx, dy):
        self.opened = None
        self.closed = None

        self.smallerRadius = min(o.r for o in self.obstacles)
        self.map = Map(ceil(self.mapw / self.smallerRadius), ceil(self.maph / self.smallerRadius), self.obstacleCost, self.robot_radius)
        for o in self.obstacles:
            minX = floor((o.x - o.r - self.robot_radius) / self.smallerRadius)
            maxX = ceil((o.x + o.r + self.robot_radius) / self.smallerRadius)
            minY = floor((o.y - o.r - self.robot_radius) / self.smallerRadius)
            maxY = ceil((o.y + o.r + self.robot_radius) / self.smallerRadius)
            for i in range(minX, maxX + 1):
                for j in range(minY, maxY + 1):
                    self.map.SetObstacle(i, j)

        self.robot = self.map.GetPoint(round(rx / self.smallerRadius), round(ry / self.smallerRadius))
        self.dest= self.map.GetPoint(round(dx / self.smallerRadius), round(dy / self.smallerRadius))


    # Apply the Theta* algorithm. Returns true if a path was found, false else.
    def ThetaStar(self):
        self.robot.g = 0
        self.robot.parent = self.robot
        self.robot.totalEstimatedCost = self.robot.distance(self.dest)

        self.opened = [self.robot]
        self.closed = []

        while len(self.opened) != 0:
            s = self.opened.pop();

            if s == self.dest:
                return True

            nghbr = self.map.GetNghbrs(s)

            for n in nghbr:
                if self.closed.__contains__(n):
                    continue
                self.UpdateVertex(s, n)

            self.opened.sort(key = lambda p: p.totalEstimatedCost)
            self.opened.reverse()

        return False

    def UpdateVertex(self, s, n):
        gOld = n.g
        self.ComputeCost(s, n)
        if gOld == None or n.g < gOld:
            n.totalEstimatedCost = n.g + n.distance(self.dest)
            if not self.opened.__contains__(n):
                self.opened.append(n)

    # Update the cost of n from s
    def ComputeCost(self, s, n):
        if self.map.LineOfSight(s.parent, n):
            cost = s.parent.g + n.cost * s.parent.distance(n)
            if n.g == None or cost < n.g:
                n.parent = s.parent
                n.g = cost
        else:
            cost = s.g + n.cost * s.distance(n)
            if n.g == None or cost < n.g:
                n.parent = s
                n.g = cost

