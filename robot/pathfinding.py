#!/usr/bin/env python3

### API ###

# Initializes the map (must be called once, at the beginning)
def Init(map_width, map_height, robot_radius):
    Data.mapw = map_width
    Data.maph = map_height
    Data.robot_radius = robot_radius

# Add an obstacle in the map
def AddObstacle(x, y, radius, tag = "No tag"):
    Data.obstacles.append(Obstacle(x, y, radius, tag))

# Remove an obstacle located at a specified position
def RemoveObstacleByPosition(x, y):
    Data.obstacles = filter(lambda o: o.x != x or o.y != y, Data.obstacles)

# Remove an obstacle that has a specific tag
def RemoveObstacleByTag(tag):
    Data.obstacles = filter(lambda o: o.tag != tag, Data.obstacles)

# Clear all the obstacles in the map
def ClearObstacles():
    Data.obstacles.clear()

# Compute the shortest path between (rx, ry) and (dx, dy).
# Includes the initial position of the robot (first point) and the destination (last point).
def GetPath(rx, ry, dx, dy):
    return PathFinding(rx, ry, dx, dy, Data.obstacles)

# Compute the lenght of a path (given by GetPath)
def PathLen(path):
    l = 0
    for i in range(0, len(path) - 1):
        l += path[i].distance(path[i + 1])
    return l

### END API ###

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

class Data:
    # Constants
    mapw = 0
    maph = 0
    robot_radius = 0

    # Obstacles
    obstacles = []

    # Utility
    obstacleCost = 10000

def PathFinding(rx, ry, dx, dy, obstacles):
    global maap, robot, dest, opened, closed
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


def InitPathfinding(rx, ry, dx, dy, obstacles):
    global maap, robot, dest, opened, closed
    maap = []
    for i in range(0, Data.mapw + 1):
        maap.append([])
        for j in range(0, Data.maph + 1):
            maap[i].append(Point(i, j))

    for o in obstacles:
        minX = o.x - o.r - Data.robot_radius; maxX = o.x + o.r + Data.robot_radius;
        minY = o.y - o.r - Data.robot_radius; maxY = o.y + o.r + Data.robot_radius;
        for i in range(minX, maxX + 1):
            for j in range(minY, maxY + 1):
                if (i - o.x)**2 + (j - o.y)**2 <= o.r**2:
                    maap[i][j].cost = Data.obstacleCost

    robot = maap[rx][ry]
    dest = maap[dx][dy]

def ThetaStar():
    global maap, robot, dest, opened, closed
    robot.g = 0
    robot.parent = robot
    robot.totalEstimatedCost = robot.distance(dest)

    opened = [ robot ]
    closed = []

    while len(opened) != 0:
        s = opened.pop();

        if s == dest:
            return True

        nghbr = GetNghbrs(s)

        for n in nghbr:
            if closed.__contains__(n):
                continue
            UpdateVertex(s, n)

        opened.sort(key = lambda p: p.totalEstimatedCost)
        opened.reverse()

    return False

def UpdateVertex(s, n):
    global maap, robot, dest, opened, closed
    gOld = n.g
    ComputeCost(s, n)
    if gOld == None or n.g < gOld:
        n.totalEstimatedCost = n.g + n.distance(dest)
        if not opened.__contains__(n):
            opened.append(n)

def ComputeCost(s, n):
    if LineOfSight(s.parent, n):
        cost = s.parent.g + n.cost * s.parent.distance(n)
        if n.g == None or cost < n.g:
            n.parent = s.parent
            n.g = cost
    else:
        cost = s.g + n.cost * s.distance(n)
        if n.g == None or cost < n.g:
            n.parent = s
            n.g = cost

def LineOfSight(a, b):
    x0 = a.x; y0 = a.y;
    x1 = b.x; y1 = b.y;
    dx = x1 - x0; dy = y1 - y0;
    f = 0;

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
            f = f + dy;
            if f >= dx:
                if IsBlocked(x0 + ((sx - 1) // 2), y0 + ((sy - 1) // 2)):
                    return False;
                y0 += sy
                f -= dx
            if f != 0 and IsBlocked(x0 + ((sx - 1) // 2), y0 + ((sy - 1) // 2)):
                return False
            if dy == 0 and IsBlocked(x0 + ((sx - 1) // 2), y0) and IsBlocked(x0 + ((sx - 1) // 2), y0 - 1):
                return False
            x0 += sx
    else:
        while y0 != y1:
            f = f + dx
            if f >= dy:
                if IsBlocked(x0 + ((sx - 1) // 2), y0 + ((sy - 1) // 2)):
                    return False
                x0 += sx
                f -= dy
            if f != 0 and IsBlocked(x0 + ((sx - 1) // 2), y0 + ((sy - 1) // 2)):
                return False
            if dy == 0 and IsBlocked(x0, y0 + ((sy - 1) // 2)) and IsBlocked(x0 - 1, y0 + ((sy - 1) // 2)):
                return False
            y0 += sy

    return True;

def IsBlocked(x, y):
    global maap
    if x < Data.robot_radius or x > Data.mapw - Data.robot_radius or y < Data.robot_radius or y > Data.maph - Data.robot_radius:
        return True;

    return maap[x][y].cost == Data.obstacleCost;

def GetNghbrs(p):
    n = []
    n.append(GetPointFromMap(p.x - 1, p.y))
    n.append(GetPointFromMap(p.x + 1, p.y))
    n.append(GetPointFromMap(p.x, p.y - 1))
    n.append(GetPointFromMap(p.x, p.y + 1))
    n.append(GetPointFromMap(p.x - 1, p.y - 1))
    n.append(GetPointFromMap(p.x - 1, p.y + 1))
    n.append(GetPointFromMap(p.x + 1, p.y - 1))
    n.append(GetPointFromMap(p.x + 1, p.y + 1))

    return [x for x in n if x is not None]

def GetPointFromMap(x, y):
    global maap
    valid = x >= Data.robot_radius and x <= Data.mapw - Data.robot_radius and y >= Data.robot_radius and y <= Data.maph - Data.robot_radius
    return maap[x][y] if valid else None

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
