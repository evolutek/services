#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

import os
from time import sleep

@Service.require("config")
@Service.require("trajman", ROBOT)
@Service.require("gpios", ROBOT)
class Avoid(Service):
    def __init__(self):
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman[ROBOT]
        self.refresh = float(self.cs.config.get(section='avoid', option='refresh'))

        self.telemetry = None
        self.front_detected = []
        self.back_detected = []
        self.avoid = False
        self.enabled = True
        self.near_wall_status = None
        self.watchdog = Watchdog(timeout=1.0, userHandler=self.reset_wall)

        super().__init__(ROBOT)

    @Service.thread
    def status(self):
        while True:
            status = {
                'front_detected' : self.front_detected,
                'back_detected' : self.back_detected,
                'avoid' : self.avoid,
                'enabled' : self.enabled
            }
            self.publish(ROBOT + '_avoid_status', status=status)
            sleep(0.5)

    @Service.thread
    def loop_avoid(self):
        while True:
            if self.telemetry is None:
                continue
            if not self.enabled:
                continue

            ## TODO Before stop, check if it is normal if a robot is in front of us
            front_wall = (self.near_wall_status is not None and not self.near_wall_status['front']) or False
            back_wall = (self.near_wall_status is not None and not self.near_wall_status['back']) or False
            if not front_wall and self.telemetry['speed'] > 0.0 and len(self.front_detected) > 0:
                self.stop_robot('front')
                print("[AVOID] Front detection")
            elif not back_wall and self.telemetry['speed'] < 0.0 and len(self.front_detected) < 0:
                self.stop_robot('back')
                print("[AVOID] Back detection")
            else:
                self.avoid = False
            sleep(0.1)

    @Service.action
    def stop_robot(self, side=None):
        self.trajman.stop_asap(1500, 30)
        self.avoid = True
        print('[AVOID] Stopping robot, %s detection triggered' % side)

        ##TODO: compute pos of tmp robot

        try:
            self.cs.ai[ROBOT].abort(side=side)
        except Exception as e:
            print('Failed to abort ai of %s: %s' % (ROBOT, str(e)))

    @Service.action
    def enable(self):
        self.enabled = True

    @Service.action
    def disable(self):
        self.enabled = False

    @Service.event('%s_front' % ROBOT)
    def front_detection(self, name, id, value):
        if int(value) and not name in self.front_detected:
            self.front_detected.append(name)
        elif not int(value) and name in self.front_detected:
            self.front_detected.remove(name)

    @Service.event('%s_back' % ROBOT)
    def back_detection(self, name, id, value):
        if int(value) and not name in self.back_detected:
            self.back_detected.append(name)
        elif not int(value) and name in self.back_detected:
            self.back_detected.remove(name)

    @Service.event('%s_telemetry' % ROBOT)
    def telemetry(self, status, telemetry):
        if self.status == 'failed':
            self.telemetry = None
        else:
            self.telemetry = telemetry

    @Service.event("%s_near_wall" % ROBOT)
    def near_wall(self, status):
        self.near_wall_status = status
        self.watchdog.reset()

    def reset_wall(self):
        self.near_wall_status = None

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
