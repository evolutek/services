from enum import Enum
import json

from evolutek.lib.geometry.point import Point

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
    respoint = Point.from_tuple(res)
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
    point = Point.from_tuple(poly.exterior.coords[nextindex])
    if not borders.contains(point): return None
    return point
