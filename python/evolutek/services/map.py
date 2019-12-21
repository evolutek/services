#!/usr/bin/env python3

from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy

from evolutek.lib.map.debug_map import Interface
from evolutek.lib.map.map import parse_obstacle_file, ObstacleType, Map as Map_lib
from evolutek.lib.map.pathfinding import Pathfinding
from evolutek.lib.map.point import Point
from evolutek.lib.map.tim import Tim
from evolutek.lib.settings import ROBOT
from evolutek.lib.waiter import waitBeacon, waitConfig

from math import pi, tan, sqrt
from time import sleep

# TODO: Check with robot_size
@Service.require('config')
class Map(Service):

    def __init__(self):
        self.cs = CellaservProxy()
        waitConfig(self.cs)
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')
        self.robot_size = int(self.cs.config.get(section='match', option='robot_size'))

        self.delta_dist = float(self.cs.config.get(section='tim', option='delta_dist')) * 2
        self.refresh = float(self.cs.config.get(section='tim', option='refresh'))

        self.tim_config = self.cs.config.get_section('tim')
        width = int(self.cs.config.get(section='map', option='width'))
        height = int(self.cs.config.get(section='map', option='height'))
        map_unit = int(self.cs.config.get(section='map', option='map_unit'))
        self.debug = self.cs.config.get(section='map', option='debug') == 'true'
        self.pal_size_y = float(self.cs.config.get(section='pal', option='robot_size_y'))
        self.pal_size = float(self.cs.config.get(section='pal', option='robot_size'))
        self.pmi_size = float(self.cs.config.get(section='pmi', option='robot_size_y'))
        self.robot_dist_sensor = int(self.cs.config.get(section='pal', option='dist_detection'))

        self.map = Map_lib(width, height, self.pal_size)
        # Load obstacles
        fixed_obstacles, self.color_obstacles = parse_obstacle_file('/etc/conf.d/obstacles.json')
        self.map.add_obstacles(fixed_obstacles)

        # TODO: to remove
        self.path = []
        self.line_of_sight = []

        # Tim data: move to dict into tim
        self.raw_data = []
        self.shapes = []
        self.robots = []

        self.pal_telem = None
        self.pmi_telem = None
        self.color = None

        # TODO: Create a list
        self.tim = None

        try:
            color = self.cs.match.get_color()
            self.match_color(color)
        except Exception as e:
            print('[MAP] Failed to get color: %s\nUsing default Yellow' % str(e))
            # Default color
            self.match_color(self.color1)

        super().__init__()

    """ Event """
    @Service.event
    def match_color(self, color):
        if color != self.color:
            self.color = color

        if self.color is not None:
            # Change color obstacles position
            for obstacle in self.color_obstacles:
                if 'tag' in obstacle:
                    self.map.remove_obstacle(obstacle['tag'])
            self.map.add_obstacles(self.color_obstacles, self.color != self.color1, type=ObstacleType.color)

        # Connected to the tim or change the pos if it is already connected
        # TODO: managed multiple tim
        if not self.tim is None and self.tim.connected:
            self.tim.change_pos(self.color != self.color1)
        else:
            self.tim = Tim(self.tim_config, self.debug, self.color != self.color1)

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
    @Service.thread
    def start_debug_interface(self):
        self.interface = Interface(self.map, self)

    # TODO: debug mode not getting oppenents
    @Service.thread
    def loop_scan(self):
        while True:
            if not self.tim.connected:
                print('[MAP] TIM not connected')
                sleep(self.refresh * 10)
                self.tim.try_connection()
                continue
            if self.debug:
                self.raw_data, self.shapes, self.robots = self.tim.get_scan()
            else:
                robots = self.tim.get_scan()

                for robot in self.robots:
                    self.map.remove_obstacle(robot['tag'])
                self.robots.clear()

                i = 0
                for point in robots:
                    # Check if point is not one of our robots
                    if (self.pal_telem and point.dist(self.pal_telem) < self.delta_dist)\
                        or (self.pmi_telem and point.dist(self.pmi_telem) < self.delta_dist):
                        continue

                    tag = "robot%d" % i

                    if self.map.add_circle_obstacle(point, self.robot_size, tag=tag, type=ObstacleType.robot):
                        robot = point.to_dict()
                        robot['tag'] = tag
                        i += 1
                        self.robots.append(robot)

                    #print('[MAP] Detected %d robots' % len(self.robots))
                    #self.publish('opponents', robots=self.robots)
            #sleep(self.refresh)
            sleep(0.01)

    """ ACTION """

    @Service.action
    def get_opponnents(self):
        return self.robots

    @Service.action
    def get_path(self, origin, dest):
      print("[MAP] Path request received")
      # TODO: Remove self.path and make match display it
      if self.pmi_telem is not None:
          self.map.add_circle_otcogon_point(Point(dict=self.pmi_telem), self.pmi_size, tag='pmi', type=ObstacleType.robot)
      self.path = self.pathfinding.get_path(Point(dict=origin), Point(dict=dest))
      self.map.remove_obstacle('pmi')
      return self.path

    @Service.action
    def add_tmp_robot(self, pos):

        if pos is None:
            return False

        point = Point.from_dict(pos)

        for robot in self.robots:
            if point.dist(robot) < self.delta_dist:
                return False
        return self.map.add_circle_obstacle(point, self.robot_size, tag='tmp', type=ObstacleType.robot)

    @Service.action
    def clean_tmp_robot(self):
        self.map.remove_obstacle('tmp')

def main():
  map = Map()
  map.run()

if __name__ == '__main__':
  main()
