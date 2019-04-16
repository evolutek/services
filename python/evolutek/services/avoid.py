#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.settings import ROBOT

import os
from time import sleep

@Service.require("config")
@Service.require("trajman", ROBOT)
class Avoid(Service):
    def __init__(self):
        self.cs = CellaservProxy()
        self.refresh = float(self.cs.config.get(section='avoid', option='refresh'))

        self.telemetry = None
        self.front_detected = []
        self.back_detected = []
        self.avoid = False
        self.enabled = True

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


            ## TODO Before stop, check if it is normal if a robot is in front of us
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

        ##TODO: compute pos of tmp robot
        try:
            self.cs.trajman[ROBOT].stop_asap(1000, 20)
            self.cs.ai[ROBOT].abort(side=side)
        except Exception as e:
            print('[AVOID] Failed to abort ai of %s: %s' % (ROBOT, str(e)))
            return
        self.avoid = True
        print('[AVOID] Stopping robot, %s detection triggered' % side)

    @Service.action
    def enable(self):
        self.enabled = True

    @Service.action
    def disable(self):
        self.enabled = False
        self.telemetry = None

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
