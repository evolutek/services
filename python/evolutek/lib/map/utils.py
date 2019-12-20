from collections import deque
from enum import Enum
import json
from math import inf
from shapely.geometry import Polygon, MultiPolygon, LineString

class ObstacleType(Enum):
    fixed = 0
    color = 1
    robot = 2

def parse_obstacle_file(file):
    with open(file, 'r') as obstacle_file:
        data = obstacle_file.read()
        data = json.loads(data)
        return data['fixed_obstacles'], data['color_obstacles']

def is_colliding_with_polygon(p1, p2, poly):

    line = LineString([p1, p2])

    for i in range(0, len(poly.coords) - 1):
        side = LineString([poly.coords[i], poly.coords[i + 1]])
        if line.crosses(side):
            return True

    return False

def merge_polygons(poly1, poly2):
    # poly1 is a Polygon
    if isinstance(poly1, Polygon):
        return poly1.difference(poly2)

    # poly1 is a MultiPolygon
    l = []
    for poly in poly1:
        result = poly.difference(poly2)

        if isinstance(result, Polygon):
            # the result is just a Polygon, add it to the list
            l.append(result)
        else:
            # the result is a MultiPolygon, add each Polygon
            for r in result:
                l.append(r)

    # return a MultiPolygon
    return MultiPolygon(l)

def dijkstra(start, end, graph):
    queue = deque()
    queue.append(start)

    pred = {}
    dist = {}
    for point in graph:
        dist[point] = inf
    dist[start] = 0

    while len(queue) > 0:
        current = queue.popleft()

        if current == end:
            break

        neighbours = graph[current]
        for neighbour in neighbours:
            distance = dist[current] + neighbour.dist(current)
            if distance < dist[neighbour]:
                dist[neighbour] = distance
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

    return path
