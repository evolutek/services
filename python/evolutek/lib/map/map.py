from evolutek.lib.map.point import Point
from evolutek.lib.map.utils import *

from collections import deque
from copy import deepcopy
from planar import Polygon as PolygonPlanar
from shapely.geometry import Polygon, MultiPolygon

from time import time
# TODO: optimization
# TODO: A* ?
# TODO: exclusion zone for start point when computin pathfinding

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

        self.obstacles = []
        self.color_obstacles = {}
        self.robots = {}

        self.merged_obstacles = None
        self.merge_obstacles()

        self.merged_map = None
        self.merge_map()

    def merge_obstacles(self):
        result = MultiPolygon()
        for obstacle in self.obstacles:
            result = result.union(obstacle)
        for tag in self.color_obstacles:
            result = result.union(self.color_obstacles[tag])
        for tag in self.robots:
            result = result.union(self.robots[tag])
        self.merged_obstacles = result

    # Return a Polygon or a MultiPolygon
    def merge_map(self):
        result = self.borders
        merged_obstacles = self.merged_obstacles
        if isinstance(merged_obstacles, Polygon):
            merged_obstacles = [merged_obstacles]
        for poly in merged_obstacles:
            result = merge_polygons(result, poly)
        self.merged_map = result

    def is_inside(self, p):
        return 0 <= p.x <= self.height and 0 <= p.y <= self.width

    def add_obstacle(self, poly, tag=None, type=ObstacleType.fixed):
        added = False

        if tag is not None:
            self.remove_obstacle(tag)

        if type == ObstacleType.fixed:
            self.obstacles.append(poly)
            added = True
        elif type == ObstacleType.color and tag is not None:
            self.color_obstacles[tag] = poly
            added = True
        elif type == ObstacleType.robot and tag is not None:
            self.robots[tag] = poly
            added = True

        if added:
            self.merge_obstacles()
            self.merge_map()
        return added

    def remove_obstacle(self, tag):
        removed = False
        if tag in self.color_obstacles:
            removed = True
            del(self.color_obstacles[tag])
        elif tag in self.robots:
            removed = True
            del(self.robots[tag])
        if removed:
            self.merge_obstacles()
            self.merge_map()
        return removed

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

    # Finds the path that goes around the given polygon
    # The returned path is the shortest path that can "escape" from the polygon
    # i.e go to the end without colliding with the given polygon again
    def go_around(self, start, end, obstacles, polygon, hit, line, order):

        path = [hit]

        # Finds the escaping point (first p where [p, end] doesn't intersect the polygon)
        escapingpoint = get_first_point(polygon, hit, line, self.borders, order)
        if escapingpoint is None: return None
        path += [escapingpoint]
        while is_colliding_with_polygon(escapingpoint, end, polygon):
            escapingpoint = get_next_point(polygon, escapingpoint, self.borders, order)
            if escapingpoint is None: return None
            path += [escapingpoint]

        # At this point path contains the points from the hit to the escaping
        # point. This path is valid but not optimal

        # Finds the first accessible point (from start)
        # TODO: Opti: mettre polygon en premier dans la liste vu que ça va souvent collide avec lui
        firstaccessible = len(path)-1
        while firstaccessible > 0 and is_colliding_with_polygons(start, path[firstaccessible], obstacles):
            firstaccessible -= 1

        # Removes all the points before the first accessible
        return path[firstaccessible:]

    # Calculates the shortest path from start to end
    # Returns the list of intermediary points (the complete path should be start+result+end)
    def get_path_rec(self, start, end, obstacles):

        # Gets the first collision point on the straight line from start to end
        hit, line, polygon = collision(start, end, obstacles)

        # If no collision point was found, returns no intermediary points
        if hit is None: return []

        #print("Start " + str(start) + " End " + str(end))

        # Tries to go around the polygon in both directions
        # TODO: ajouter un smooth sur le retour de cette fonction
        path1 = self.go_around(start, end, obstacles, polygon, hit, line, False)
        path2 = self.go_around(start, end, obstacles, polygon, hit, line, True)

        #if path1: print("Path1 " + str([pt.to_tuple() for pt in path1]))
        #if path2: print("Path2 " + str([pt.to_tuple() for pt in path2]))

        # Gets the path from the "escaping point" to the end
        # TODO: opti: pas besoin de tester si polygon est sur le chemin pour collision
        if path1: path1 += self.get_path_rec(path1[-1], end, obstacles)
        if path2: path2 += self.get_path_rec(path2[-1], end, obstacles)

        # If there is only one path, returns it
        if not path1: return path2
        if not path2: return path1

        # Calculates the length of each path and returns the smaller one
        # TODO: opti on peut faire les deux calculs en meme temps et s'arreter quand no sait qu'un des chemins est plus court
        p1l = path_length(path1)
        p2l = path_length(path2)
        if p1l < p2l: return path1
        else: return path2

    def get_path(self, start, end):

        obstacles = deepcopy(self.merged_obstacles)
        map = deepcopy(self.merged_map)

        zone = None
        if isinstance(map, Polygon):
            zone = map
        else:
            for poly in map:
                if poly.contains(start):
                    zone = poly
                    break

        if zone is None:
            print('[MAP] Start point outside current map')
            return []

        if not zone.contains(end):
            print('[MAP] End point outside current map')
            return []

        if isinstance(obstacles, Polygon):
            obstacles = MultiPolygon(obstacles)

        # Create an octogon were the robot is
        """p = PolygonPlanar.regular(8, radius=self.robot_radius, angle=22.5, center=start.to_tuple())
        l = []
        for point in p:
+            l.append((point.x, point.y))"""

        path =  [start]
        path += self.get_path_rec(Point(tuple=start), Point(tuple=end), obstacles)
        path += [end]

        return path
