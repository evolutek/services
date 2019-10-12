from evolutek.lib.map.point import Point

from collections import deque
from math import inf
import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

class Pathfinding:

    def __init__(self, map):
        self.map = map

    def a_star(self, start, end):

        frontier = PriorityQueue()
        cost = {}
        pred = {}

        frontier.put(start, 0)
        cost[start] = 0
        pred[start] = None

        while not frontier.empty():

            current = frontier.get()

            if current == end:
                break

            neighbours = self.neighbours(current)
            for neighbour in neighbours:

                new_cost = cost[current] + current.dist(neighbour)
                if neighbour not in cost or new_cost < cost[neighbour]:
                    cost[neighbour] = new_cost
                    frontier.put(neighbour, new_cost + self.heuristic(neighbour, end))
                    pred[neighbour] = current

        path = []
        if end in pred:
            current = end
            path.append(end)
            while current != start:
                path.insert(0, current)
                current = pred[current]
            print('[PATHFINDING] Path found')
        else:
            print("[PATHFINDING] Destination unreachable")

        return path

    def heuristic(self, p1, p2):
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    def dijkstra(self, start, end):
        dist = []
        for x in range(self.map.height + 1):
            dist.append([])
            for y in range(self.map.width + 1):
                dist[x].append(inf)

        queue = deque()
        queue.append(start)
        dist[start.x][start.y] = 0

        pred = {}
        while len(queue) > 0:
            current = queue.popleft()

            if current == end:
                break

            neighbours = self.neighbours(current)
            for neighbour in neighbours:
                distance = dist[current.x][current.y] + current.dist(neighbour)
                if distance < dist[neighbour.x][neighbour.y]:
                    dist[neighbour.x][neighbour.y] = distance
                    queue.append(neighbour)
                    pred[neighbour] = current

        path = []
        if end in pred:
            current = end
            path.append(end)
            while pred[current] in pred:
                current = pred[current]
                path.insert(0, current)
            path.insert(0, start)
            print('[PATHFINDING] Path found')
        else:
            print("[PATHFINDING] Destination unreachable")

        return path

    def neighbours(self, p):
        l = [
            Point(p.x - 1, p.y),
            Point(p.x + 1, p.y),
            Point(p.x, p.y - 1),
            Point(p.x, p.y + 1),
            Point(p.x - 1, p.y - 1),
            Point(p.x - 1, p.y + 1),
            Point(p.x + 1, p.y - 1),
            Point(p.x + 1, p.y + 1)
            ]

        neighbours = []
        with self.map.lock:
            for point in l:
                if self.map.is_point_inside(point) and self.map.map[point.x][point.y].is_empty():
                    neighbours.append(point)

        return neighbours

    def smooth(self, path):

        if len(path) <= 2:
            return path

        _path = []
        n3 = path[0]
        n2 = path[1]

        # Smooth line path
        _path.append(path[0])
        for i in range(2, len(path)):
            n1 = path[i]
            if not (n2.x - n3.x == n1.x - n2.x and n2.y - n3.y == n1.y - n2.y):
                _path.append(n2)
            n3 = n2
            n2 = n1
        _path.append(path[-1])

        if len(_path) <= 2:
            return _path

        return _path

        # TODO: debug
        # is_colliding not working

        smooth = []
        origin = 0
        last_valid = 1

        smooth.append(_path[origin])

        while last_valid < len(_path) - 1:
            if not self.map.is_colliding(_path[origin], _path[last_valid]):
                last_valid += 1
            else:
                smooth.append(_path[last_valid])
                origin = last_valid
                last_valid = origin + 1

        smooth.append(_path[-1])

        return smooth

    # FIXME: can cross line
    def is_correct_trajectory(self, p1, p2):

        if p1 == p2:
            return True

        # Compute 2nd degree equation between two points
        dy = False
        a = 0
        b = 0

        p1, p2 = Point.min(p1, p2), Point.max(p1, p2)
        start = Point(p1.x * self.map.unit, p1.y * self.map.unit)
        end = Point(p2.x * self.map.unit, p2.y * self.map.unit)

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

            p = self.map.convert_point(Point(x, y))

            # Check if the current point is empty
            if self.map.is_inside_obstacle(p):
                return False
        return True

    def convert_path(self, path):
        l = []
        for p in path:
            l.append({'x': p.x * self.map.unit, 'y': p.y * self.map.unit})
        return l

    def get_path(self, p1, p2):
        if self.map.is_real_point_outside(p1) or self.map.is_real_point_outside(p2):
            print('[PATHFINDING] Start or End outside map')
            return []

        start = self.map.convert_point(p1)
        end = self.map.convert_point(p2)

        if not self.map.map[start.x][start.y].is_empty() or not self.map.map[end.x][end.y].is_empty():
            print('[PATHFINDING] Destination unreachable')
            return []

        #path = self.dijkstra(start, end)
        path = self.a_star(start, end)
        return self.convert_path(self.smooth(path))
