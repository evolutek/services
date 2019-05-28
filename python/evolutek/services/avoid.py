#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.point import Point
from evolutek.lib.settings import ROBOT

from math import cos, sin, tan, pi, sqrt
import os
from threading import Lock
from time import sleep

dist_sensor_x = 115
dist_sensor_y = 125

# TODO: map sensors
sensors = {
    'gtb1': {'x': dist_sensor_x, 'y': dist_sensor_y},
    'gtb2': {'x': dist_sensor_x, 'y': 0},
    'gtb3': {'x': dist_sensor_x, 'y': -dist_sensor_y},
    'gtb4': {'x': -dist_sensor_x, 'y': dist_sensor_y},
    'gtb5': {'x': -dist_sensor_x, 'y': 0},
    'gtb6': {'x': -dist_sensor_x, 'y': -dist_sensor_y}
}

@Service.require("config")
@Service.require("trajman", ROBOT)
class Avoid(Service):
    def __init__(self):
        self.cs = CellaservProxy()

        #self.refresh = float(self.cs.config.get(section='avoid', option='refresh'))
        #self.robot_dist_sensor = int(self.cs.config.get(section=ROBOT, option='dist_detection'))
        #self.robot_size = int(self.cs.config.get(section='match', option='robot_size'))

        self.telemetry = None
        self.front_detected = []
        self.back_detected = []
        self.avoid = False
        self.enabled = True
        self.tmp_robot = None

        super().__init__(ROBOT)

    @Service.action
    def status(self):
        status = {
            'front' : self.front_detected,
            'back' : self.back_detected,
            'avoid' : self.avoid,
            'enabled' : self.enabled
        }

        return status

    @Service.thread
    def loop_avoid(self):
        while True:
            if self.telemetry is None:
                continue
            if not self.enabled:
                continue

            if self.telemetry['speed'] > 0.0 and len(self.front_detected) > 0:
                self.stop_robot('front')
                print("[AVOID] Front detection")
            elif self.telemetry['speed'] < 0.0 and len(self.back_detected) > 0:
                self.stop_robot('back')
                print("[AVOID] Back detection")
            else:
                self.avoid = False
            sleep(0.1)

    @Service.action
    def stop_robot(self, side=None):
        print('----- Aborting: %s ---' % side)

        try:
            self.cs.trajman[ROBOT].stop_asap(1000, 20)
            self.cs.ai[ROBOT].abort(side=side)
        except Exception as e:
            print('[AVOID] Failed to abort ai of %s: %s' % (ROBOT, str(e)))
        self.avoid = True
        #sensor = self.compute_sensor_pos(side)
        #self.tmp_robot = self.compute_tmp_robot(sensor.to_dict(), side)
        print('[AVOID] Stopping robot, %s detection triggered' % side)
        sleep(0.5)

    @Service.action
    def enable(self):
        print('----- ENABLE -----')
        self.enabled = True

    @Service.action
    def disable(self):
        print('----- DISABLE -----')
        self.enabled = False
        self.telemetry = None
        self.tmp_robot = None

    @Service.event('%s_front' % ROBOT)
    def front_detection(self, name, id, value):
        if int(value) and not name in self.front_detected:
            self.front_detected.append(name)
        elif not int(value) and name in self.front_detected:
            self.front_detected.remove(name)

    @Service.event('%s_back' % ROBOT)
    def back_detection(self, name, id, value):
        print(id)
        if int(value) and not name in self.back_detected:
            self.back_detected.append(name)
        elif not int(value) and name in self.back_detected:
            self.back_detected.remove(name)

    @Service.event('%s_telemetry' % ROBOT)
    def telemetry(self, status, telemetry):
        if not self.enabled or self.status == 'failed':
            self.telemetry = None
        else:
            self.telemetry = telemetry

    @Service.action
    def compute_sensor_pos(self, side):
        pos = self.cs.trajman[ROBOT].get_position()
        stat = self.status()

        s = []

        for sensor in stat[side]:
            sensor_pos = sensors[sensor]
            s.append(Point(pos['x'] + sensor_pos['x'], pos['y'] + sensor_pos['y']))

        cos_val = cos(pos['theta'])
        sin_val = sin(pos['theta'])

        new_s = []
        for sensor in s:
            new_s.append(Point(
            (sensor.x - pos['x']) * cos_val - (sensor.y - pos['y']) * sin_val + pos['x'],
            (sensor.x - pos['x']) * sin_val + (sensor.y - pos['y']) * cos_val + pos['y']
            ))

        return Point.mean(new_s)

    @Service.action
    def compute_tmp_robot(self, pos, side):

        print(pos)
        print(side)

        # We use theta between 0 and 2pi
        theta = self.cs.trajman[ROBOT].get_position()['theta']
        if theta < 0:
            theta += 2 * pi

        y = False
        m = 0
        n = 0
        delta = 0.1
        if abs(pi/2 - theta) < delta or abs(3*pi/2 - theta) < delta:
            y = True
            m = tan((pi/2) - theta)
            n = pos['x'] - (m * pos['y'])
        else:
            m = tan(theta)
            n = pos['y'] - (m * pos['x'])

        sens = theta > pi / 2 and theta < 3 * pi / 2 if not y else theta > pi

        dist = (self.robot_dist_sensor + self.robot_size) / sqrt(1 + m ** 2)

        print(dist)

        if sens ^ (side != 'front'):
            dist *= -1

        print(dist)

        new_x = 0
        new_y = 0
        if y:
            new_y = int(pos['y'] + dist)
            new_x = int(new_y * m + n)
        else:
            new_x = int(pos['x'] + dist)
            new_y = int(new_x * m + n)

        return Point(new_x, new_y)

    @Service.action
    def get_tmp_robot(self):
        if self.tmp_robot is None:
            return
        return self.tmp_robot.to_dict()

def wait_for_beacon():
    hostname = "pi"
    while True:
        r = os.system("ping -c 1 " + hostname)
        if r == 0:
            return
        pass

def main():
    wait_for_beacon()
    avoid = Avoid()
    avoid.run()

if __name__ == '__main__':
    main()
