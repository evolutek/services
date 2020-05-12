from collections import deque
from enum import Enum
import json
from math import inf
from shapely.geometry import Polygon, MultiPolygon, LineString, Point as ShapelyPoint

from evolutek.lib.map.point import Point

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

    #if poly.contains(line):
        #return True

    return line.crosses(poly)

    for i in range(0, len(poly.exterior.coords) - 1):
        side = LineString([poly.exterior.coords[i], poly.exterior.coords[i + 1]])
        if line.crosses(side):
            return True

    return False

# Runs is_colliding_with_polygon on multiple polygons
def is_colliding_with_polygons(p1, p2, polys):
    for poly in polys:
        if is_colliding_with_polygon(p1, p2, poly):
            return True
    return False

# TODO: Optimise
# poly1 can be a Polygon or a MultiPolygon
# Can return a Polygon or a MultiPolygon
# Return the nearest collision if there is one else None
# The returned tuple is the collision point, the line containing
# that point and the polygon containing that line
def collision(p1, p2, obstacles):
    line = LineString([p1, p2])

    polygon = None
    closer = None
    hit = None
    dist = 0

    # Iterate over all interns polygons
    for poly in obstacles:
        new_closer, new_dist = collision_with_polygon(p1, p2, poly)
        if not new_closer is None and (closer is None or new_dist < dist):
            closer = new_closer
            dist = new_dist
            polygon = poly

    if closer: hit = Point(tuple=line.intersection(closer))
    return hit, closer, polygon

def collision_with_polygon(p1, p2, poly):

    line = LineString([p1, p2])

    closer = None
    dist = 0

    for i in range(len(poly.exterior.coords) - 1):
        side = LineString([poly.exterior.coords[i], poly.exterior.coords[i + 1]])
        new_dist = p1.distance(side)
        if line.crosses(side) and (closer is None or dist > new_dist):
            closer = side
            dist = new_dist

    return closer, dist

def path_length(path):
    res = 0
    for i in range(len(path)-2):
        res += path[i].dist(path[i+1])
    return res

# Finds point next to the hit on the polygon
# line is the line that has been hit
def get_first_point(poly, hit, line, borders, reverseorder):
    index = list(poly.exterior.coords).index(line.coords[0])
    nextindex = index + (-1 if reverseorder else 1)
    res = line.coords[0]
    # If the nextpoint is the other point of the line then
    # we are going in the wrong direction
    if poly.exterior.coords[nextindex] == line.coords[1]:
        res = line.coords[1]
    # Checks that the point is inside the bounds before returning
    respoint = Point(tuple=res)
    if not borders.contains(respoint): return None
    return respoint

# Finds the point next to the given point on the given polygon
def get_next_point(poly, point, borders, reverseorder):
    # The last point is ignored because it is the same as the first one
    nbpoints = len(poly.exterior.coords)-1
    # Gets the index of the current point in the list
    index = list(poly.exterior.coords).index(point.to_tuple())
    # Calculates the next index and loops back if necessary
    nextindex = (index + (-1 if reverseorder else 1)) % nbpoints
    # Returns the next point if possible
    point = Point(tuple=poly.exterior.coords[nextindex])
    if not borders.contains(point): return None
    return point

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

def convert_path_to_dict(path):
    new = []
    for p in path:
        new.append(p.to_dict())
    return new

def convert_path_to_point(path):
    new = []
    for p in path:
        new.append(Point(dict=p))
    return new
