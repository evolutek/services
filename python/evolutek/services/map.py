#!/usr/bin/env python3

from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy
from evolutek.lib.debug_map import Interface
from evolutek.lib.map import ObstacleType, Map as Map_lib
from evolutek.lib.point import Point
from evolutek.lib.settings import ROBOT
from evolutek.lib.tim import Tim

from math import pi
from threading import Lock
from time import sleep

@Service.require('config')
class Map(Service):

    def __init__(self):

        cs = CellaservProxy()

        self.color1 = cs.config.get(section='match', option='color1')
        self.color2 = cs.config.get(section='match', option='color2')
        self.robot_size = int(cs.config.get(section='match', option='robot_size'))

        self.delta_dist = float(cs.config.get(section='tim', option='delta_dist'))
        self.refresh = float(cs.config.get(section='tim', option='refresh'))
        self.debug = cs.config.get(section='tim', option='debug') == 'True'

        self.tim_config = {
            'min_size' : float(cs.config.get(section='tim', option='min_size')),
            'max_distance' : float(cs.config.get(section='tim', option='max_distance')),
            'ip' : cs.config.get(section='tim', option='ip'),
            'port' : int(cs.config.get(section='tim', option='port')),
            'pos_x' : int(cs.config.get(section='tim', option='pos_x')),
            'pos_y' : int(cs.config.get(section='tim', option='pos_y')),
            'angle' : float(cs.config.get(section='tim', option='angle'))
        }

        width = int(cs.config.get(section='map', option='width'))
        height = int(cs.config.get(section='map', option='height'))
        map_unit = int(cs.config.get(section='map', option='map_unit'))
        self.pal_size = int(cs.config.get(section='pal', option='robot_size_y'))
        self.pal_dist_sensor = int(cs.config.get(section='pal', option='dist_detection'))

        self.map = Map_lib(width, height, map_unit, self.pal_size)
        """ Add obstacles """
        self.map.add_rectangle_obstacle(1622, 2000, 450, 2550)
        self.map.add_rectangle_obstacle(1422, 1622, 1475, 1525)
        self.map.add_rectangle_obstacle(0, 50, 500, 2500)
        self.map.add_circle_obstacle(1000, 1500, 150, "robot", ObstacleType.robot)

        # Example
        self.path = self.map.get_path(Point(1650, 225), Point(1650, 2775))

        # TIM
        self.lock = Lock()
        self.raw_data = []
        self.shapes = []
        self.robots = []
        self.pal_telem = None
        self.color = None
        self.tim = None

        try:
            color = cs.match.get_color()
            self.match_color(color)
        except Exception as e:
            print('Failed to get color: %s' % str(e))

        super().__init__()

    @Service.thread
    def start_debug_interface(self):
        self.interface = Interface(self.map, self)

    @Service.event
    def match_color(self, color):
        if color != self.color:
            self.color = color
        if self.color is not None:
            self.map.remove_obstacle('zone')
            if self.color != self.color1:
                self.map.add_rectangle_obstacle(300, 1200, 0, 450, tag='zone')
            else:
                self.map.add_rectangle_obstacle(300, 1200, 2550, 3000, tag='zone')
            config = self.tim_config
            if self.color != self.color1:
                config['pos_y'] = 3000 - config['pos_y']
                config['angle'] *= -1
            self.tim = Tim(config, self.debug)
        else:
            self.map.remove_obstacle('zone')
            self.tim = None

    @Service.event
    def pal_telemetry(self, status, telemetry):
        if status is not 'failed':
            self.pal_telem = telemetry
            status = self.is_facing_wall(telemetry)
            self.publish("pal_near_wall", status=status)

    @Service.thread
    def loop_scan(self):
        while True:
            if self.tim is None:
                print('TIM not connected')
                sleep(self.refresh * 10)
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
                    if self.pal_telem and point.dist(self.pal_telem) < self.delta_dist:
                        continue
                    robot = point.to_dict()
                    robot['tag'] = "robot%d" % i
                    i += 1
                    self.robots.append(robot)

                for robot in self.robots:
                    self.map.add_circle_obstacle(robot['x'], robot['y'], self.robot_size, tag=robot['tag'], type=ObstacleType.robot)
                    self.publish('opponents', robots=self.robots)

            self.path = self.map.get_path(Point(1650, 225), Point(1650, 2775))
            sleep(self.refresh)

    @Service.action
    def is_facing_wall(self, telemetry):

        if self.map.is_real_point_outside(telemetry['x'], telemetry['y']):
            print("Error PAL out of map")
            return

        x_incr, y_incr = 0, 0
        if telemetry['theta'] > pi/4 and telemetry['theta'] <= 3*pi/4:
            y_incr = -1
        elif telemetry['theta'] > 3*pi/4 and telemetry['theta'] <= 5*pi/4:
            x_incr = 1
        elif telemetry['theta'] > 5*pi/4 and telemetry['theta'] <= 7*pi/4:
            y_incr = 1
        else:
            x_incr = 1

        p = self.map.convert_point(telemetry['x'], telemetry['y'])
        front, back = False, False
        for i in range(int((self.pal_dist_sensor + self.pal_size) / self.map.unit)):
            f = Point(p.x + (x_incr * i), p.y + (y_incr * i))
            if not self.map.is_point_inside(f) or self.map.map[f.x][f.y].is_obstacle():
                front = True

            b = Point(p.x + (-x_incr * i), p.y + (-y_incr * i))
            if not self.map.is_point_inside(b) or self.map.map[b.x][b.y].is_obstacle():
                back = True

            if front and back:
                break

        return  {'front': front, 'back': back}

"""
    @Service.action
    def get_optimal_goal(self, goals):
      optimum = None
      for goal in goals:
        option = dijkstra_path(goal)
        if optimum is None || option.cost < optimum.cost:
          # optimum -> Cfeate dict here

      return optimum

"""
if __name__ == '__main__':
  map = Map()
  map.run()
