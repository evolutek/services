#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.sensors.rplidar import Rplidar
from evolutek.lib.map.point import Point
from time import time, sleep
from evolutek.lib.settings import ROBOT

@Service.require('config')
@Service.require('trajman', ROBOT)
class Robot(Service):

    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()

        lidar_config = self.cs.config.get_section('rplidar')

        self.lidar = Rplidar(lidar_config)
        self.lidar.start_scanning()
        self.lidar.register_callback(self.callback_lidar)

        self.last_telemetry_received = 0

    @Service.event("%s_telemetry" % ROBOT)
    def update_position(self, telemetry, **kwargs):
        tmp = time()
        print("[ROBOT] Time since last telemetry: " + str((tmp - self.last_telemetry_received) * 1000) + "s")
        self.last_telemetry_received = tmp
        self.lidar.set_position(Point(dict=telemetry), float(telemetry['theta']))

    def callback_lidar(self, cloud, shapes, robots):
        print('[ROBOT] Robots seen at: ')
        for robot in robots:
            print('-> ' + str(robot))

if __name__ == '__main__':
    robot = Robot()
    robot.run()
