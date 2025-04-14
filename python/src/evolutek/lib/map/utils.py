from collections import deque
from enum import Enum
import json
from math import inf
from shapely.geometry import Polygon, MultiPolygon, LineString, Point as ShapelyPoint

from evolutek.lib.map.point import Point

# Possible types of obstacle
class ObstacleType(Enum):
    fixed = 0
    color = 1
    robot = 2

# Read the JSON config file for obstacles
def parse_obstacle_file(file):
    with open(file, 'r') as obstacle_file:
        data = obstacle_file.read()
        data = json.loads(data)
        return data['fixed_obstacles'], data['color_obstacles']

# Check if a line is colling with a polygon
def is_colliding_with_polygon(p1, p2, poly):
    line = LineString([p1, p2])
    return line.crosses(poly)

# Runs is_colliding_with_polygon on multiple polygons
def is_colliding_with_polygons(p1, p2, polys):
    line = LineString([p1, p2])
    for poly in polys:
        if line.crosses(poly):
            return True
    return False

# Returns the nearest collision if there is one else None
# The returned tuple is the collision point, the line containing
# that point and the polygon containing that line
def collision(p1, p2, obstacles):

    line = LineString([p1, p2])
    collpolygon = None
    collside = None
    collpoint = None
    colldistsqr = 0

    for poly in obstacles:
        # For every side of the polygon that collides with line
        for side in collision_with_polygon(line, poly):
            # Calculates the distance to the intersection point
            hit = Point(tuple=line.intersection(side))
            distsqr = p1.sqrdist(hit)
            # If this hit is closer, saves it
            if collpoint is None or distsqr < colldistsqr:
                collpolygon = poly
                collside = side
                collpoint = hit
                colldistsqr = distsqr

    return collpoint, collside, collpolygon

# Returns all the sides of poly that collide with line
def collision_with_polygon(line, poly):
    res = []
    for i in range(len(poly.exterior.coords) - 1):
        side = LineString([poly.exterior.coords[i], poly.exterior.coords[i + 1]])
        if line.crosses(side):
            res.append(side)
    return res

def path_length(path):
    res = 0
    for i in range(len(path)-2):
        res += path[i].dist(path[i+1])
    return res

# Returns True if the path p1 is shorter than the path p2, False otherwise
def is_shorter(p1, p2):
    n1, n2 = len(p1), len(p2)
    l1, l2 = 0, 0
    i1, i2 = 1, 1
    while True:
        if l1 < l2:
            if i1 >= n1: return True
            l1 += p1[i1-1].dist(p1[i1])
            i1 += 1
        else:
            if i2 >= n2: return False
            l2 += p2[i2-1].dist(p2[i2])
            i2 += 1

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

# Merge two polygons
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


# Convert a path to a list of dict
def convert_path_to_dict(path):
    new = []
    for p in path:
        new.append(p.to_dict())
    return new

# Convert a list of dict to a path
def convert_path_to_point(path):
    new = []
    for p in path:
        new.append(Point(dict=p))
    return new
