from evolutek.lib.map.point import Point
from evolutek.lib.map.utils import *

from collections import deque
from copy import deepcopy
from planar import Polygon as PolygonPlanar
from shapely.geometry import Polygon, MultiPolygon

# TODO: add lock
# TODO : optimization

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

    def compute_graph(self, start, end, obstacles):

        # Create a queue of all points
        d = deque()
        graph = {}
        d.append(start)
        graph[start] = []

        for poly in obstacles:
            for point in poly.exterior.coords:
                new = Point(tuple=point)
                if not new in d and self.borders.contains(new):
                    d.append(new)
                    graph[new] = []

        d.append(end)
        graph[end] = []

        # Iterate over polygons to compute the vertexes
        for poly in obstacles:
            coords = poly.exterior.coords
            l = len(coords)
            for i in range(1, l):
                new = Point(tuple=coords[i])
                if not self.borders.contains(new):
                    continue

                d.remove(new)
                p1 = Point(coords[i - 1])
                p2 = Point(coords[(i + 1) % l])

                if not p1 in graph[new] and self.borders.contains(p1):
                    graph[new].append(p1)

                if not p2 in graph[new] and self.borders.contains(p2):
                    graph[new].append(p2)

                points = list(d)
                for point in points:
                    if point in graph[new] or point.to_tuple() in coords:
                        continue
                    is_colliding = False
                    for poly in obstacles:
                        if is_colliding_with_polygon(point, new, poly.exterior):
                            is_colliding = True
                            break

                    if not is_colliding:
                        graph[new].append(point)
                        graph[point].append(new)

        return graph

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

        is_colliding = False
        for poly in obstacles:
            if is_colliding_with_polygon(start, end, poly.exterior):
                is_colliding = True
                break

        # No obstacles on the trajectory
        if not is_colliding:
            return [start, end]

        graph = self.compute_graph(start, end, obstacles)

        path = dijkstra(start, end, graph)

        if path == []:
            print("[MAP] Path not found")
        else:
            print("[MAP] Path found")

        return path
