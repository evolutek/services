#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event as CellaservEvent, Service

from evolutek.lib.map.point import Point
from evolutek.lib.robot.robot_trajman import *
from evolutek.lib.sensors.rplidar import Rplidar
from evolutek.lib.settings import ROBOT
from evolutek.lib.utils.wrappers import event_waiter

from time import time, sleep
from threading import Lock

@Service.require('config')
@Service.require('actuators', ROBOT)
@Service.require('trajman', ROBOT)
class Robot(Service):

    start_event = CellaservEvent('%s_started' % ROBOT)
    stop_event = CellaservEvent('%s_stopped' % ROBOT)

    goto_xy = event_waiter(self.trajman.goto_xy)
    goto_theta = event_waiter(self.trajman.goto_theta)
    move_trsl = event_waiter(self.trajman.move_trsl)
    move_rot = event_waiter(self.trajman.move_rot)
    recal = event_waiter(self.recalibration)

    def __init__(self):
        self.cs = CellaservProxy()
        self.lock = Lock()

        self.color1 = self.cs.config.get('match', 'color1')
        self.side = True

        try:
            self.color_callback(self.cs.match.get_color())
        except Exception as e:
            print('[ROBOT] Failed to set color: %s' % str(e))

        self.actuators = self.cs.actuators[ROBOT]
        self.trajman = self.cs.trajman[ROBOT]

        lidar_config = self.cs.config.get_section('rplidar')

        self.lidar = Rplidar(lidar_config)
        self.lidar.start_scanning()
        self.lidar.register_callback(self.lidar_callback)

        self.last_telemetry_received = 0
        super().__init__()

    @Service.event("match_color")
    def color_callback(color):
        with self.lock:
            self.side = color == self.color1

    @Service.event("%s_telemetry" % ROBOT)
    def update_position(self, telemetry, **kwargs):
        tmp = time()
        print("[ROBOT] Time since last telemetry: " + str((tmp - self.last_telemetry_received) * 1000) + "s")
        self.last_telemetry_received = tmp
        self.lidar.set_position(Point(dict=telemetry), float(telemetry['theta']))

    def lidar_callback(self, cloud, shapes, robots):
        print('[ROBOT] Robots seen at: ')
        for robot in robots:
            print('-> ' + str(robot))

if __name__ == '__main__':
    robot = Robot()
    robot.run()
