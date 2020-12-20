from evolutek.lib.map.point import Point
from evolutek.lib.map.utils import *

from collections import deque
from copy import deepcopy
from planar import Polygon as PolygonPlanar
from shapely.geometry import Polygon, MultiPolygon

from time import time
# TODO: tmp obstacles

# Class to store the state of the table during matches
class Map:

    # Init of the class
    # width : width of the map (3000)
    # height : height of the map (2000)
    # robot_radius : radius of our robots (140)
    # borders : rectangle of the borders of the table
    # obstacles : fixed obstacles on the table
    # color_obstacles : obstacles depending of the color of the team
    # robots : robots on the table
    # merged_obstacles : union of all the obstacles
    # merged_map : Polygons of the table
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

    # Merge all obstacles
    def merge_obstacles(self):
        result = MultiPolygon()
        for obstacle in self.obstacles:
            result = result.union(obstacle)
        for tag in self.color_obstacles:
            result = result.union(self.color_obstacles[tag])
        for tag in self.robots:
            result = result.union(self.robots[tag])
        self.merged_obstacles = result

    # Remove obstacles to the polygon of the borders
    # Return a Polygon or a MultiPolygon
    def merge_map(self):
        result = self.borders
        merged_obstacles = self.merged_obstacles
        if isinstance(merged_obstacles, Polygon):
            merged_obstacles = [merged_obstacles]
        for poly in merged_obstacles:
            result = merge_polygons(result, poly)
        self.merged_map = result

    # Check if a point is inside the map
    def is_inside(self, p):
        return 0 <= p.x <= self.height and 0 <= p.y <= self.width

    # Add an obstacle to the map
    # poly : polygon of the obstalce
    # tag : name of the obstacle
    # type : type of the obstacle
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

    # Remove an obstacle by the tag
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

    # Add a rectagular obstacle
    # p1 : first corner
    # p2 : second corner
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

    def build_octogon(self, center, radius):
        poly = PolygonPlanar.regular(8, radius=radius, angle=22.5, center=center.to_tuple())
        l = []
        for point in poly:
            l.append((point.x, point.y))
        return Polygon(l)

    # Add an octogonal obstacle
    # center : center of the octogon
    # radius : external radius of the octogon
    def add_octogon_obstacle(self, center, radius, tag=None, type=ObstacleType.fixed):
        if not self.is_inside(center):
            return False
        octogon = self.build_octogon(center, radius+self.robot_radius)
        return self.add_obstacle(octogon, tag=tag, type=type)

    # Add the obstacles from the JSON config file
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
                if not 'center' in obstacle:
                    print('[MAP] Bad circle obstacle in parsing')
                    continue
                obstacle['center'] = Point(dict=obstacle['center'])
                if mirror:
                    obstacle['center'].y = 3000 - obstacle['center'].y
                self.add_octogon_obstacle(**obstacle, type=type)
            else:
                print('[MAP] Obstacle form not found')

    # Smoothes a path (tries to make it shorter by skipping points)
    # CurrentObs is the obstacle around which the algorithm is calculating a
    # trajectory, obstacles are all the obstacles
    # CurrentObs can be None if you want a general smooth (if you are not
    # going around an obstacle at the moment)
    def smooth_path(self, path, obstacles, currentobs=None):
        length = len(path)
        jumpSize = length-1
        # We start with the biggest possible jump and then tries smaller jumps
        while jumpSize > 1:
            current = 0
            # While the jump is possible (There is a point at the end)
            while current + jumpSize < length:
                start = path[current]
                end = path[current+jumpSize]
                inside = False if currentobs is None else \
                    currentobs.contains(start.average(end))
                collides = True if inside else \
                        is_colliding_with_polygons(start, end, obstacles)
                # If the jump is possible (no obstacle)
                if not collides:
                    # Removes the points
                    del path[current+1:current+jumpSize]
                    length -= jumpSize-1
                # Tries from the next point
                current += 1
            jumpSize -= 1

    # Finds the path that goes around the given polygon
    # The returned path is the shortest path that can "escape" from the polygon
    # i.e go to the end without colliding with the given polygon again
    def go_around(self, start, end, obstacles, polygon, hit, line, order):

        path = [hit]

        # Finds the escaping point (first p where [p, end] doesn't intersect the polygon)
        firstpoint = get_first_point(polygon, hit, line, self.borders, order)
        if firstpoint is None: return None # Blocked by border
        escapingpoint = firstpoint
        path += [escapingpoint]
        while is_colliding_with_polygon(escapingpoint, end, polygon):
            escapingpoint = get_next_point(polygon, escapingpoint, self.borders, order)
            if escapingpoint is None: return None # Blocked by border
            if escapingpoint == firstpoint: return None # Went around the poly
            path += [escapingpoint]

        # At this point path contains the points from the hit to the escaping
        # point. This path is valid but not optimal

        # Finds the first accessible point (from start)
        # TODO: Opti: mettre polygon en premier dans la liste vu que ça va souvent collide avec lui
        firstaccessible = len(path)-1
        while firstaccessible > 0 and is_colliding_with_polygons(start, path[firstaccessible], obstacles):
            firstaccessible -= 1

        # Removes all the points before the first accessible
        path = path[firstaccessible:]
        # Optimises the path if possible
        self.smooth_path(path, list(obstacles), polygon)
        return path

    # Calculates the shortest path from start to end
    # Returns the list of intermediary points (the complete path should be start+result+end)
    def get_path_rec(self, start, end, obstacles, previousNodes):

        # Gets the first collision point on the straight line from start to end
        hit, line, polygon = collision(start, end, obstacles)

        # If no collision point was found, returns no intermediary points
        if hit is None: return []

        # Tries to go around the polygon in both directions
        path1 = self.go_around(start, end, obstacles, polygon, hit, line, False)
        path2 = self.go_around(start, end, obstacles, polygon, hit, line, True)

        # If one of the nodes is already in the path, no need to consider using it
        # TODO: Regarder si c'est plus rapide d'utiliser un set pour passer en O(n)
        for node in previousNodes:
            if path1:
                for pnode in path1:
                    if node == pnode:
                        path1 = None
                        break
            if path2:
                for pnode in path2:
                    if node == pnode:
                        path2 = None
                        break

        # Gets the path from the "escaping point" to the end
        # TODO: opti: pas besoin de tester si polygon est sur le chemin pour collision
        if path1:
            res = self.get_path_rec(path1[-1], end, obstacles, previousNodes + path1)
            if res is not None: path1 += res
            else: path1 = None
        if path2:
            res = self.get_path_rec(path2[-1], end, obstacles, previousNodes + path2)
            if res is not None: path2 += res
            else: path2 = None

        if path1 is None and path2 is None: return None
        if path1 is None: return path2
        if path2 is None: return path1

        # Calculates the length of each path and returns the smaller one
        p1shorter = is_shorter(path1, path2)
        if p1shorter: return path1
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

        # Exclusion zone around the start point
        #ex = self.build_octogon(start, self.robot_radius)
        #obstacles = obstacles.difference(ex)

        if isinstance(obstacles, Polygon):
            obstacles = MultiPolygon(obstacles)

        nodes = self.get_path_rec(Point(tuple=start), Point(tuple=end), obstacles, [])

        if nodes is None:
            print("[MAP] No path found")
            return []

        path = [start] + nodes + [end]

        # Applies an additionnal smooth to handle some edge cases
        #self.smooth_path(path, obstacles)

        return path

    def is_path_valid(self, path):

        if len(path) < 2:
            return False

        obstacles = deepcopy(self.merged_obstacles)

        start = path[0]
        end = path[1]

        # Exclusion zone around the start point
        #ex = self.build_octogon(start, self.robot_radius)
        #obstacles = obstacles.difference(ex)

        prev = start
        for p in path[1:]:
            line = LineString([prev.round(), p.round()])
            for poly in obstacles:
                for i in range(len(poly.exterior.coords) - 1):
                    p1 = poly.exterior.coords[i]
                    side = LineString([
                        Point(tuple=poly.exterior.coords[i]).round(),
                        Point(tuple=poly.exterior.coords[i + 1]).round()
                    ])
                    if line.crosses(side):
                        print("[MAP] Validity check: %s collides with %s" % (line, side))
                        return False
            prev = p

        return True
