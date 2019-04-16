#!/usr/bin/env python3

from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy
from evolutek.lib.debug_map import Interface
from evolutek.lib.map import ObstacleType, Map as Map_lib
from evolutek.lib.point import Point
from evolutek.lib.settings import ROBOT
from evolutek.lib.tim import Tim

from math import pi, tan, sqrt
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

        self.tim_config = cs.config.get_section('tim')
        width = int(cs.config.get(section='map', option='width'))
        height = int(cs.config.get(section='map', option='height'))
        map_unit = int(cs.config.get(section='map', option='map_unit'))
        self.debug = cs.config.get(section='map', option='debug') == 'true'
        self.pal_size = int(cs.config.get(section='pal', option='robot_size_y'))
        self.pal_dist_sensor = int(cs.config.get(section='pal', option='dist_detection'))

        self.map = Map_lib(width, height, map_unit, self.pal_size)
        """ Add obstacles """
        self.map.add_rectangle_obstacle(1622, 2000, 450, 2550)
        self.map.add_rectangle_obstacle(1422, 1622, 1475, 1525)
        self.map.add_rectangle_obstacle(0, 50, 500, 2500)
        #self.map.add_circle_obstacle(1000, 1500, 150, "robot", ObstacleType.robot)

        # Example
        self.path = None
        #self.path = self.map.get_path(Point(1650, 225), Point(1650, 2775))

        # TIM
        self.lock = Lock()
        self.raw_data = []
        self.shapes = []
        self.robots = []
        self.line_of_sight = []
        self.pal_telem = None
        self.color = None
        self.tim = None

        try:
            color = cs.match.get_color()
            self.match_color(color)
        except Exception as e:
            print('Failed to get color: %s' % str(e))
            raise Exception()

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
                config['pos_y'] = 3000 - int(config['pos_y'])
                config['angle'] = - int(config['angle'])
            self.tim = Tim(config, self.debug)
        else:
            self.map.remove_obstacle('zone')
            self.tim = None

    @Service.event
    def pal_telemetry(self, status, telemetry):
        if status is not 'failed':
            self.pal_telem = telemetry
            status = self.is_facing_wall(telemetry)
            if not status is None:
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
                print(robots)
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

            #self.path = self.map.get_path(Point(1650, 225), Point(1650, 2775))
            sleep(self.refresh)

    @Service.action
    def is_facing_wall(self, telemetry):

        if self.debug:
            self.line_of_sight.clear()

        if self.map.is_real_point_outside(telemetry['x'], telemetry['y']):
            print("Error PAL out of map")
            return

        # We use theta between 0 and 2pi
        theta = telemetry['theta']
        if theta < 0:
            theta += 2 * pi

        y = False
        m = 0
        n = 0
        delta = 0.75
        if round(theta % pi, 3) > delta\
            and round(theta % (pi/2), 3) < delta:
            y = True
            m = tan((pi/2) - theta)
            n = telemetry['x'] - (m * telemetry['y'])
        else:
            m = tan(theta)
            n = telemetry['y'] - (m * telemetry['x'])

        distance = telemetry['speed'] * 0.5
        if not y:
            next_x = telemetry['x'] + (distance / sqrt(1 + m  ** 2))
            next_y = next_x * m + n
        else :
            next_y = telemetry['y'] + (distance / sqrt(1 + m ** 2))
            next_x = next_y * m + n

        sens = abs((pi/2) - theta) < abs((3*pi/2) - theta) if y else abs(0 - theta) < abs(pi - theta)

        front, back = False, False
        for i in range(int(self.pal_dist_sensor / self.map.unit) + 2):
            dist = i * self.map.unit / sqrt(1 + m ** 2)

            if y:
                y1 = int(next_y + dist)
                y2 = int(next_y - dist)
                x1 = int(y1 * m + n)
                x2 = int(y2 * m + n)
            else:
                x1 = int(next_x + dist)
                x2 = int(next_x - dist)
                y1 = int(x1 * m + n)
                y2 = int(x2 * m + n)

            p1 = self.map.convert_point(x1, y1)
            p2 = self.map.convert_point(x2, y2)


            if not sens:
                p1, p2 = p2, p1

            if self.debug:
                self.line_of_sight.append(Point(x1, y1))
                self.line_of_sight.append(Point(x2, y2))

            if not self.map.is_point_inside(p1) or self.map.map[p1.x][p1.y].is_obstacle():
                front = True
            if not self.map.is_point_inside(p2) or self.map.map[p2.x][p2.y].is_obstacle():
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
