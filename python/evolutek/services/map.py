#!/usr/bin/env python3

from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy
from evolutek.lib.debug_map import Interface
from evolutek.lib.map import Point, Map as Map_lib
from evolutek.lib.settings import ROBOT
from evolutek.lib.tim import Tim

from math import pi
from threading import Lock
from time import sleep

def dist(a, b):
    return (a['x'] * b['x'] + a['y'] * b['y']) ** 0.5

@Service.require('config')
class Map(Service):

    def __init__(self):
        self.raw_data = []
        cs = CellaservProxy()

        self.color1 = cs.config.get(section='match', option='color1')
        self.color2 = cs.config.get(section='match', option='color2')
        self.robot_size = int(cs.config.get(section='match', option='robot_size'))

        self.delta_dist = float(cs.config.get(section='tim', option='delta_dist'))
        self.refresh = float(cs.config.get(section='tim', option='refresh'))

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
        self.map = Map_lib(width, height, map_unit, self.pal_size)

        """ Add obstacles """
        self.map.add_rectangle_obstacle(1622, 2000, 450, 2550)
        self.map.add_rectangle_obstacle(1422, 1622, 1480, 1520)
        self.map.add_rectangle_obstacle(0, 50, 500, 2500)

        #self.map.add_circle_obstacle(1000, 1500, 150)

        # Example
        #self.path = self.map.get_path(Point(1650, 225), Point(1000, 2000))

        self.lock = Lock()
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
        print(color)
        if color != self.color:
            self.color = color
        if self.color is not None:
            self.map.remove_obstacle('zone')
            if self.color != self.color1:
                print(self.map.add_rectangle_obstacle(300, 1200, 0, 450, tag='zone'))
            else:
                print(self.map.add_rectangle_obstacle(300, 1200, 2550, 3000, tag='zone'))
            config = self.tim_config
            if self.color != self.color1:
                config['pos_y'] = 3000 - config['pos_y']
                config['angle'] *= -1
            self.tim = Tim(config)
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
            self.raw_data, data = self.tim.get_scan()

            with self.lock:

                for robot in self.robots:
                    self.map.remove_obstacle(robot['tag'])
                self.robots.clear()

                i = 0
                for point in data:
                    # Check if point is not one of our robots
                    if self.pal_telem and dist(self.pal_telem, point) < self.delta_dist:
                        continue
                    p = point.to_dict()
                    p['tag'] = "robot%d" % i
                    i += 1
                    self.robots.append(p)

            for robot in self.robots:
                self.map.add_circle_obstacle(robot['x'], robot['y'], self.robot_size, tag=robot['tag'])
            #self.publish('opponents', robots=self.robots)


            sleep(self.refresh)

    @Service.action
    def is_facing_wall(self, telemetry):

        if self.pal_telem['x'] < 0 or self.pal_telem['y'] < 0\
            or self.pal_telem['x'] > self.map.real_height\
            or self.pal_telem['y'] > self.map.real_width:
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

        x, y = int(self.pal_telem['x']/self.map.unit), int(self.pal_telem['y']/self.map.unit)
        front, back = False, False
        for i in range(int((self.pal_dist_sensor + self.pal_size) / self.map.unit)):
            fx, fy = x + (x_incr * i), y + (y_incr * i)
            if fx < 0 or fy < 0 or fx > self.map.height or fy > self.map.width\
                or self.map.map[fx][fy] > 0:
                front = True

            bx, by = x + (-x_incr * i), y + (-y_incr * i)
            if bx < 0 or by < 0 or bx > self.map.height or by > self.map.width\
                or self.map.map[bx][by] > 0:
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
