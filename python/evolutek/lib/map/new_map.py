from evolutek.lib.map.point import Point

from copy import deepcopy
from enum import Enum
import json
from planar import Polygon as PolygonPlanar
from shapely.geometry import Polygon, MultiPolygon, LineString
from shapely.ops import cascaded_union

class ObstacleType(Enum):
    fixed = 0
    color = 1
    robot = 2

def parse_obstacle_file(file):
    with open(file, 'r') as obstacle_file:
        data = obstacle_file.read()
        data = json.loads(data)
        return data['fixed_obstacles'], data['color_obstacles']

# poly1 can be a Polygon or a MultiPolygon
# Can return a Polygon or a MultiPolygon
# Return the nearest collision if there is one else None
def collision(p1, p2, map):
    line = LineString([p1, p2])

    polygon = None
    closer = None
    dist = 0

    # Iterate over all interns polygons
    for poly in map.interiors:
        new_closer, new_dist = collision_with_polygon(p1, p2, poly)
        if not new_closer is None and (closer is None or new_dist < dist):
            closer = new_closer
            dist = new_dist
            polygon = poly

    # Iterate over the exterior polygon
    new_closer, new_dist = collision_with_polygon(p1, p2, map.exterior)
    if not new_closer is None and (closer is None or new_dist < dist):
        closer = new_closer
        polygon = map.exterior

    return closer, polygon

def collision_with_polygon(p1, p2, poly):

    line = LineString([p1, p2])

    closer = None
    dist = 0

    for i in range(0, len(poly.coords) - 1):
        side = LineString([poly.coords[i], poly.coords[i + 1]])
        new_dist = p1.distance(side)
        if line.crosses(side) and (closer is None or dist > new_dist):
            closer = side
            dist = new_dist

    return closer, dist

# TODO: poly[len(poly) -1] = poly[0]
def compute_contour(p1, p2, poly, sens):

    path = [p1]
    index = 0
    for point in poly.coords:
        if (p1.x, p1.y) == point:
            break
        index += 1

    line, _ = collision_with_polygon(path[-1], p2, poly)

    while not line is None:
        index = ((index + 1) % len(poly.coords)) if sens else (index - 1)
        p = Point(tuple=poly.coords[index])
        if p in path:
            continue
        path.append(p)
        line, _ = collision_with_polygon(path[-1], p2, poly)

    return path

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

def is_on_polygon(p, poly):
    l = LineString(poly)
    return l.contains(p)

class Map:

    def __init__(self, width, height, robot_radius):
        self.width = width
        self.height = height
        self.robot_radius = robot_radius

        self.borders = Polygon([
            (robot_radius, robot_radius),
            (height - robot_radius, robot_radius),
            (height - robot_radius, width - robot_radius),
            (robot_radius, width - robot_radius)
        ])

        self.color_obstacles = {}
        self.robots = {}

        self.merged_map = None
        self.merge_map()

    def is_inside(self, p):
        return 0 <= p.x <= self.height and 0 <= p.y <= self.width

    def add_obstacle(self, poly, tag=None, type=ObstacleType.fixed):
        added = False
        if type == ObstacleType.fixed:
            try:
                self.borders = self.borders.difference(poly)
                added = True
            except Exception as e:
                print('[MAP] Failed to compute new polygon: %s' % str(e))
        elif type == ObstacleType.color and tag is not None:
            self.color_obstacles[tag] = poly
            added = True
        elif type == ObstacleType.robot and tag is not None:
            self.robots[tag] = poly
            added = True

        if added:
            self.merged_map = self.merge_map()
        return added

    def remove_obstacle(self, tag):
        removed = False
        if tag in self.color_obstacles:
            del(self.color_obstacles[tag])
            removed = True
        if tag in self.robots:
            del(self.robots[tag])
            removed = True
        if removed:
            self.merged_map = self.merge_map()
        return False

    def add_rectangle_obstacle(self, p1, p2, tag=None, type=ObstacleType.fixed):
        if not self.is_inside(p1) or not self.is_inside(p2):
            return False

        l = [
            (p1.x - self.robot_radius, p1.y - self.robot_radius),
            (p1.x - self.robot_radius, p2.y + self.robot_radius),
            (p2.x + self.robot_radius, p2.y + self.robot_radius),
            (p2.x + self.robot_radius, p1.y - self.robot_radius)
        ]

        return self.add_obstacle(Polygon(l), tag=tag, type=type)

    def add_octogon_obstacle(self, center, radius, tag=None, type=ObstacleType.fixed):
        if not self.is_inside(center):
            return False

        poly = PolygonPlanar.regular(8, radius=radius + self.robot_radius, angle=22.5, center=center.to_tuple())
        l = []

        for point in poly:
            l.append((point.x, point.y))

        return self.add_obstacle(Polygon(l), tag=tag, type=type)

    def add_obstacles(self, obstacles, mirror=False, type=ObstacleType.fixed):
        obstacles = deepcopy(obstacles)
        for obstacle in obstacles:

            if 'type' in obstacle:
                try:
                    obstacle['type'] = eval(obstacle['type'])
                except Exception as e:
                    print('[MAP] Bad obstacle type: %s' % (str(e)))
                    continue

            if not 'form' in obstacle:
                print('[MAP] No form in obstacle')
                continue
            form = obstacle['form']
            del obstacle['form']

            if form == 'rectangle':
                if not 'p1' in obstacle or not 'p2' in obstacle:
                    print('[MAP] Bad rectangle obstacle in parsing')
                    continue
                obstacle['p1'] = Point(dict=obstacle['p1'])
                obstacle['p2'] = Point(dict=obstacle['p2'])
                if mirror:
                    obstacle['p1'].y = 3000 - obstacle['p1'].y
                    obstacle['p2'].y = 3000 - obstacle['p2'].y
                self.add_rectangle_obstacle(**obstacle, type=type)
            elif form == 'octogon':
                if not 'p' in obstacle:
                    print('[MAP] Bad circle obstacle in parsing')
                    continue
                obstacle['p'] = Point(dict=obstacle['p'])
                if mirror:
                    obstacle['p'].y = 3000 - obstacle['p'].y
                self.add_octogon_obstacle(**obstacle, type=type)
            else:
                print('[MAP] Obstacle form not found')



    # Return a Polygon or a MultiPolygon
    # TODO: debug self.merged_map
    def merge_map(self):
        result = self.borders
        for color_obstacle in self.color_obstacles:
            result = merge_polygons(result, self.color_obstacles[color_obstacle])
        for robot in self.robots:
            result = merge_polygons(result, self.robots[robot])
        self.merged_map = result
        return result

    # TODO: fix dist
    # TODO: can go througt obstacle
    def get_path_rec(self, p1, p2, map, i = 0):

        #print('Computing between')
        #print(p1)
        #print(p2)

        line, poly = collision(p1, p2, map)

        if line is None:
            #print('No collsion')
            #print('Returning path')
            return [p1, p2]

        else:
            #print('collision with: ' + str(line))
            path1 = []
            if is_on_polygon(p1, poly):
                #print('Already on polygon')
                path1 = compute_contour(p1, p2, poly, True)
                del(path1[0])
            else:
                #print('Not on polygon')
                path1 = compute_contour(Point(tuple=line.coords[1]), p2, poly, True)

            #print('new path1')
            #print(p1)
            #for point in path1:
            #    print(point)

            patha = self.get_path_rec(p1, path1[0], map, 1)
            pathb = self.get_path_rec(path1[-1], p2, map, 1)
            path1 = patha + path1[1:-1] + pathb

            path2 = []
            if is_on_polygon(p1, poly):
                path2 = compute_contour(p1, p2, poly, False)
                del(path2[0])
            else:
                path2 = compute_contour(Point(tuple=line.coords[0]), p2, poly, False)

            #print('new path2')
            #print(p1)
            #for point in path2:
            #    print(point)

            patha = self.get_path_rec(p1, path2[0], map)
            pathb = self.get_path_rec(path2[-1], p2, map)
            path2 = patha + path2[1:-1] + pathb

            dist1 = 0
            for i in range(0, len(path1) - 1):
                dist1 += path1[i].dist(path1[i + 1])

            dist2 = 0
            for i in range(0, len(path2) - 1):
                dist2 += path2[i].dist(path2[i + 1])

            if dist1 < dist2:
                #print('Returning path 1 with dist: ' + str(dist1))
                return path1
            else:
                #print('Returning path 2 with dist: ' + str(dist2))
                return path2

    def get_path(self, start, end):
        map = None

        merged_map = self.merge_map()

        if isinstance(merged_map, Polygon):
            # Only one polygon for the map
            map = merged_map
        else:
            # Get current map polygon
            for poly in merged_map:
                if poly.contains(start):
                    map = poly
                    break

        if map is None:
            print('[MAP] Start point outside current map')
            return []

        if not map.contains(end):
            print('[MAP] End point outside current map')
            return []

        path = self.get_path_rec(start, end, merged_map)

        smooth = [path[0]]
        current = 2
        while current < len(path):
            line, poly = collision(smooth[-1], path[current], merged_map)
            if not line is None:
                smooth.append(path[current - 1])
            current += 1
        smooth.append(path[-1])

        #print('[MAP] Path computed')
        return smooth
