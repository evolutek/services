from evolutek.lib.map.point import Point

from collections import deque
from math import inf

class Node:

    def __init__(self, p, dist, heuristic, parent):
        self.p = p
        self.dist = dist
        self.heuristic = heuristic
        self.parent = parent

    def __eq__(self, p):
        return self.p == p.p

    def cost(self):
        return self.dist + self.heuristic

    def __str__(self):
        return str(self.p) + " g: %f, h:% f" % (self.dist, self.heuristic)

class Pathfinding:

    def __init__(self, map):
        self.map = map

    def a_star(self, start, end):

        start_node = Node(start, 0, 0, None)
        end_node = Node(end, 0, 0, None)

        closed = deque()
        open = deque()

        open.append(start_node)

        while len(open):
            curr = open.popleft()

            if curr == end_node:
                print('[MAP] Path found')
                path = []
                while curr:
                    path.append[curr.p]
                    curr = curr.parent
                return path[::-1]

            children = self.get_children(curr)
            for child in children:

                node = None
                for _node in open:
                    if _node == child and child.dist < _node.dist:
                        node = _node
                if child in closed or (node is not None and node.dist < child.dist):
                    continue

                if node:
                    node.dist = child.dist
                    node.parent = curr
                    node.heuristic = child.heuristic
                else:
                    open.append(child)


        print('[MAP] No path found')
        return []

    def heuristic(self, p1, p2):
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    def get_children(self, current):
        l = [
            (Point(current.p.x, current.p.y - 1), 1),
            (Point(current.p.x, current.p.y + 1), 2),
            (Point(current.p.x - 1, current.p.y), 1),
            (Point(current.p.x + 1, current.p.y), 1),
            (Point(current.p.x - 1, current.p.y - 1), 2),
            (Point(current.p.x - 1, current.p.y + 1), 2),
            (Point(current.p.x + 1, current.p.y - 1), 2),
            (Point(current.p.x + 1, current.p.y + 1), 2)
            ]

        children = []
        for point, dist in l:
            if self.map.is_point_inside(point) and self.map.map[point.x][point.y].is_empty():
                children.append(Node(point, dist, self.heuristic(current.p, point), current))

        return children

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
            cur = queue.popleft()

            if cur == end:
                break

            neighbours = self.neighbours(cur)
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
            print('[MAP] Paht found')
        else:
            print("[MAP] Desination unreachable")

        return path

    def neighbours(self, p):
        l = [
            Point(p.x - 1, p.y),
            Point(p.x + 1, p.y),
            Point(p.x, p.y - 1),
            Point(p.x, p.y + 1)
            ]

        neighbours = []
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

        n1 = _path[0]
        n2 = _path[1]
        n3 = _path[2]
        smooth = [n1]
        i = 2

        while (i < len(_path)):
            n3 = _path[i]
            mini = n2
            for j in range(i + 1, len(_path)):
                if self.is_correct_trajectory(n1, n3):
                    mini = n3
                    i = j
                n2 = n3
                n3 = _path[j]
            smooth.append(mini)
            n2 = _path[i]
            n1 = mini
            i += 1

        smooth.append(n3)
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

        path = self.dijkstra(start, end)
        return self.convert_path(self.smooth(path))
