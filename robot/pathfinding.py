#!/usr/bin/env python3

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

    def __str__(self):
        return str(self.x) + ", " + str(self.y)

class Obstacle:
    def __init__(self, x, y, radius, tag = "No tag"):
        self.x = x
        self.y = y
        self.r = radius
        self.tag = tag

class Map:

    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.map = []
        for i in range(0, Data.mapw + 1):
            self.map.append([])
            for j in range(0, Data.maph + 1):
                self.map[i].append(Point(i, j))

    def GetPoint(self, x, y, radius):
        valid = (x >= robot_radius
                and x <= self.w - robot_radius
                and y >= robot_radius
                and y <= self.h - robot_radius)
        return self.map[x][y] if valid else None

    def IsBlocked(self, x, y, robot_radius):
        if (x < robot_radius
            or x > self.mapw - self.robot_radius
            or y < self.robot_radius
            or y > self.maph - self.robot_radius):
            return True;
        return self.[x][y].cost == Data.obstacleCost

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

    def GetPointFromMap(self, x, y, robot_radius):
        valid = (x >= robot_radius
                and x <= self.w - robot_radius
                and y >= robot_radius
                and y <= self.h - robot_radius)
        return self.map[x][y] if valid else None


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



class PathFinding():

    def __init__(self, map_width, map_height, robot_radius):
        self.maap = None
        self.robot = None
        self.dest = None
        self.opened = None
        self.closed = None

        self.mapw = map_width
        self.maph = map_height
        self.robot_radius = robot_radius
        self.obstacles = []
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

    # Compute the lenght of a path (given by GetPath)
    def PathLen(self, path):
        l = 0
        for i in range(0, len(path) - 1):
            l += path[i].distance(path[i + 1])
        return l

    # Compute the shortest path between (rx, ry) and (dx, dy).
    # Includes the initial position of the robot (first point) and the destination (last point).
    def GetPath(rx, ry, dx, dy):
        return self.PathFinding(rx, ry, dx, dy, self.obstacles)

    #Same as above
    def PathFinding(self, rx, ry, dx, dy, obstacles):
        global robot, dest
        InitPathfinding(rx, ry, dx, dy, obstacles)
        if ThetaStar():
            path = []
            current = dest
            while current != robot:
                path.append(current)
                current = current.parent
            path.append(robot)

            path.reverse()
            #print("Path found (" + str(len(path)) + " points):");
            #for p in path:
            #    print(p.toString())

            return path
        else:
            return []
            #print("No path found.")

    #Create a new map with cost set to the obstacles
    def InitPathfinding(self, rx, ry, dx, dy, obstacles):
        global robot, dest, opened, closed
        self.maap = []

        for o in obstacles:
            minX = o.x - o.r - Data.self.robot_radius
            maxX = o.x + o.r + Data.self.robot_radius
            minY = o.y - o.r - Data.self.robot_radius
            maxY = o.y + o.r + Data.self.robot_radius;
            for i in range(minX, maxX + 1):
                for j in range(minY, maxY + 1):
                    if (i - o.x)**2 + (j - o.y)**2 <= o.r**2:
                        self.maap[i][j].cost = Data.obstacleCost

        self.robot = self.maap[rx][ry]
        self.dest = self.maap[dx][dy]


    def UpdateVertex(self, s, n):
        global dest, opened
        gOld = n.g
        self.ComputeCost(s, n)
        if gOld == None or n.g < gOld:
            n.totalEstimatedCost = n.g + n.distance(dest)
            if not opened.__contains__(n):
                opened.append(n)


    def ComputeCost(self, s, n):
        if self.LineOfSight(s.parent, n):
            cost = s.parent.g + n.cost * s.parent.distance(n)
            if n.g == None or cost < n.g:
                n.parent = s.parent
                n.g = cost
        else:
            cost = s.g + n.cost * s.distance(n)
            if n.g == None or cost < n.g:
                n.parent = s
                n.g = cost



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

            nghbr = GetNghbrs(s)

            for n in nghbr:
                if self.closed.__contains__(n):
                    continue
                UpdateVertex(s, n)

            self.opened.sort(key = lambda p: p.totalEstimatedCost)
            self.opened.reverse()

        return False


### TEST ###

#Init(20, 20, 0)
#AddObstacle(6, 1, 1, "toto")
#AddObstacle(6, 3, 1)
#AddObstacle(6, 5, 1)
#AddObstacle(6, 7, 1)
#AddObstacle(14, 7, 1)
#AddObstacle(14, 9, 1)
#AddObstacle(14, 11, 1)
#AddObstacle(14, 13, 1)
#AddObstacle(14, 15, 1)
#AddObstacle(14, 17, 1)
#AddObstacle(14, 19, 1)
#AddObstacle(16, 11, 1)
#PathLen(GetPath(2, 4, 16, 18))

### END TEST ###
