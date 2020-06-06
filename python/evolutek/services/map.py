#!/usr/bin/env python3

from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy

from evolutek.lib.map.debug_map import Interface
from evolutek.lib.map.map import parse_obstacle_file, ObstacleType, Map as Map_lib
from evolutek.lib.map.point import Point
from evolutek.lib.map.utils import convert_path_to_dict, merge_polygons
from evolutek.lib.settings import ROBOT
from evolutek.lib.map.utils import convert_path_to_dict
from evolutek.lib.settings import SIMULATION

if SIMULATION:
    from evolutek.simulation.fake_lib.fake_tim import DebugMode, Tim
else:
    from evolutek.lib.map.tim import DebugMode, Tim

import json
from shapely.geometry import Polygon, MultiPolygon
from threading import Lock
from time import sleep

# TODO: merge tims scans
# TODO: ignore obstacles
# TODO: check which is the slowest, tim or refresh ?
@Service.require('config')
class Map(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')
        self.robot_size = int(self.cs.config.get(section='match', option='robot_size'))

        self.delta_dist = float(self.cs.config.get(section='tim', option='delta_dist')) * 2
        self.refresh = int(self.cs.config.get(section='tim', option='refresh'))

        self.tim_computation_config = self.cs.config.get_section('tim')
        width = int(self.cs.config.get(section='map', option='width'))
        height = int(self.cs.config.get(section='map', option='height'))
        self.pal_size_y = float(self.cs.config.get(section='pal', option='robot_size_y'))
        self.pal_size = float(self.cs.config.get(section='pal', option='robot_size'))
        self.pmi_size = float(self.cs.config.get(section='pmi', option='robot_size_y'))

        self.debug_mode = DebugMode.normal
        self.publish('tim_debug_mode', mode=self.debug_mode.value)
        self.lock = Lock()

        self.map = Map_lib(width, height, self.pal_size)
        # Load obstacles
        fixed_obstacles, self.color_obstacles = parse_obstacle_file('/etc/conf.d/obstacles.json')
        self.map.add_obstacles(fixed_obstacles)

        # TODO: to remove
        self.path = []

        # Tim data: move to dict into tim
        self.robots = []

        self.pal_telem = None
        self.pmi_telem = None
        self.color = None

        # TODO: Create a list
        self.tim = {}

        self.tim_config = None
        with open('/etc/conf.d/tim.json', 'r') as tim_file:
            self.tim_config = tim_file.read()
            self.tim_config = json.loads(self.tim_config)

        try:
            color = self.cs.match.get_color()
            self.match_color(color)
        except Exception as e:
            print('[MAP] Failed to get color: %s\nUsing default Yellow' % str(e))
            # Default color
            self.match_color(self.color1)


    """ Event """
    @Service.event
    def match_color(self, color):
        if color != self.color:
            self.color = color

        if self.color is not None:
            # Change color obstacles position
            with self.lock:
                for obstacle in self.color_obstacles:
                    if 'tag' in obstacle:
                        self.map.remove_obstacle(obstacle['tag'])
                self.map.add_obstacles(self.color_obstacles, self.color != self.color1, type=ObstacleType.color)

            self.publish('obstacles', obstacles=self.get_obstacles())

        # Connected to the tim or change the pos if it is already connected
        for tim in self.tim_config:
            if tim['ip'] in self.tim and not self.tim[tim['ip']] is None:
                self.tim[tim['ip']].change_pos(self.color != self.color1)
            else:
                self.tim[tim['ip']] = Tim(tim, self.tim_computation_config, self.color != self.color1)

    @Service.event
    def pal_telemetry(self, status, telemetry):
        if status != 'failed':
            self.pal_telem = telemetry

    @Service.event
    def pmi_telemetry(self, status, telemetry):
        if status != 'failed':
            self.pmi_telem = telemetry


    """ THREAD """
    # TODO: Disable for beacon
    #@Service.thread
    def start_debug_interface(self):
        self.interface = Interface(self.map, self)

    #@Service.thread
    def fake_robot(self):
        robot = {'x': 750, 'y': 1500}
        ascending = True

        while True:
            #print('[TEST_MAP] Update Fake Robot')
            if ascending:
                robot['x'] += 10
                if robot['x'] > 1700:
                    robot['x'] = 1699
                    ascending = False
            else:
                robot['x'] -= 10
                if robot['x'] < 299:
                    robot['x'] = 201
                    ascending = True

            pos = Point(dict=robot)
            with self.lock:
                obstacle = self.map.add_octogon_obstacle(pos, self.robot_size, tag='fake', type=ObstacleType.robot)
            self.robots.clear()
            self.robots.append(robot)
            sleep(0.1)

    # TODO: Merge
    @Service.thread
    def loop_scan(self):
        while True:

            # Iterate over tim
            scans = []
            _scans = []
            for ip in self.tim:

                tim = self.tim[ip]

                # Not connected
                if not tim.connected:
                    continue

                scans.append(tim.get_robots())

                if self.debug_mode == DebugMode.debug_tims:
                    raw = []
                    for p in self.tim[ip].get_points():
                        raw.append(p.to_dict)

                    shapes = []
                    for p in self.tim[ip].get_shapes():
                        shapes.append(p.to_dict)

                    _scans.append((raw, shapes))

            if self.debug_mode == DebugMode.debug_tims:
                self.publish('tim_scans', scans=_scans)

            # Merge robots
            # TODO : if debug, publish merge / manage merge
            robots = []
            for scan in scans:

                new = []
                for point in scan:

                    # It's one of our robots
                    if (self.pal_telem and point.dist(self.pal_telem) < self.delta_dist)\
                        or (self.pmi_telem and point.dist(self.pmi_telem) < self.delta_dist):
                        continue

                    merged = False
                    for robot in robots:
                        # Already know this robot: merge it with the current point
                        if robot.dist(point) < self.delta_dist:
                            new.append(robot.average(point))
                            robots.remove(robot)
                            merged = True
                            break

                    # Robot not found, add it
                    if not merged:
                        new.append(point)

                # Add not merged robots
                new += robots
                robots = new

            with self.lock:

                # Remove old robots
                #for robot in self.robots:
                #    self.map.remove_obstacle(robot['tag'])
                #self.robots.clear()

                # Add robots on the map
                i = 0
                for robot in robots:
                    tag = "robot%d" % i
                    if self.map.add_octogon_obstacle(robot, self.robot_size, tag=tag, type=ObstacleType.robot):
                        d = point.to_dict()
                        d['tag'] = tag
                        i += 1
                        self.robots.append(d)

                if self.debug_mode == DebugMode.normal:
                    self.publish('tim_detected_robots', robots=self.robots)

            sleep(self.refresh / 1000)


    """ ACTION """
    @Service.action
    def get_debug_mode(self):
        return self.debug_mode.value

    @Service.action
    def set_debug_mode(self, mode):
        new_mode = None
        try:
            new_mode = DebugMode(int(mode))
        except:
            print('[MAP] Debug mode not existing')
            return
        print('[MAP] Setting debug mode to %s' % new_mode.value)
        self.debug_mode = new_mode
        self.publish('tim_debug_mode', mode=self.debug_mode.value)


    @Service.action
    def get_opponnents(self):
        return self.robots

    @Service.action
    def get_obstacles(self):
        l = []

        # Merge map
        obstacles = MultiPolygon()
        for obstacle in self.map.obstacles:
            obstacles = obstacles.union(obstacle)
        for tag in self.map.color_obstacles:
            obstacles = obstacles.union(self.map.color_obstacles[tag])

        polygons = self.map.borders
        if isinstance(obstacles, Polygon):
            obstacles = [obstacles]
        for poly in obstacles:
            polygons = merge_polygons(polygons, poly)

        if isinstance(polygons, Polygon):
            polygons = [polygons]

        # Add exterior polygons
        for poly in polygons:
            _l = []
            for p in poly.exterior.coords:
                _l.append(Point(tuple=p).to_dict())
            l.append(_l)

            # Add interior polygons
            for _poly in poly.interiors:
                _l = []
                for p in _poly.coords:
                    _l.append(Point(tuple=p).to_dict())
                l.append(_l)

        return l

    @Service.action
    def get_path(self, origin, dest):
      print("[MAP] Path request received")
      # TODO: Remove self.path and make match display it
      with self.lock:
          # TODO : check wich robot call the function and add the other
          if self.pmi_telem is not None:
              self.map.add_otcogon_point(Point(dict=self.pmi_telem), self.pmi_size, tag='pmi', type=ObstacleType.robot)
          self.path = self.map.get_path(Point(dict=origin), Point(dict=dest))
          # TODO: remove other robot
          self.map.remove_obstacle('pmi')
      return convert_path_to_dict(self.path)

    @Service.action
    def add_tmp_robot(self, pos):

        if pos is None:
            return False

        point = Point.from_dict(pos)

        for robot in self.robots:
            if point.dist(robot) < self.delta_dist:
                return False

        if (self.pal_telem and point.dist(self.pal_telem) < self.delta_dist)\
            or (self.pmi_telem and point.dist(self.pmi_telem) < self.delta_dist):
            return False

        with self.lock:
            return self.map.add_circle_obstacle(point, self.robot_size, tag='tmp', type=ObstacleType.robot)

    @Service.action
    def clean_tmp_robot(self):
        self.map.remove_obstacle('tmp')

def main():
  map = Map()
  map.run()

if __name__ == '__main__':
  main()
