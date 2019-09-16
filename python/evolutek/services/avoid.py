#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.gpio import Gpio
from evolutek.lib.settings import ROBOT

import os
from time import sleep

@Service.require("config")
@Service.require("trajman", ROBOT)
class Avoid(Service):
    def __init__(self):

        self.cs = CellaservProxy()

        # TODO : check float response from config
        #self.refresh = float(self.cs.config.get(section='avoid', option='refresh'))

        self.telemetry = None
        self.avoid = False
        self.enabled = True
        self.front = False
        self.back = False

        # init sensors
        # TODO: Config file ?
        self.front_sensors = [
            Gpio(18, "gtb1", False),
            Gpio(23, "gtb2", False),
            Gpio(24, "gtb3", False)
        ]

        self.back_sensors = [
            Gpio(16, "gtb4", False),
            Gpio(20, "gtb5", False),
            Gpio(21, "gtb6", False)
        ]

        super().__init__(ROBOT)

    def update_sensors(self):
        front = False
        back = False

        for sensor in self.front_sensors:
            front = self.front or sensor.read()

        for sensor in self.back_sensors:
            back = self.back or sensor.read()

        # Change the values after the read to avoid race conflict
        self.front = front
        self.back = back

    @Service.action
    def status(self):
        status = {
            'front' : self.front,
            'back' : self.back,
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

            self.update_sensors()

            if self.telemetry['speed'] > 0.0 and self.front:
                self.stop_robot('front')
                print("[AVOID] Front detection")
            elif self.telemetry['speed'] < 0.0 and self.back:
                self.stop_robot('back')
                print("[AVOID] Back detection")
            else:
                self.avoid = False
            sleep(0.1)

    @Service.action
    def stop_robot(self, side=None):
        try:
            self.cs.trajman[ROBOT].stop_asap(1000, 20)
            self.cs.ai[ROBOT].abort(side=side)
        except Exception as e:
            print('[AVOID] Failed to abort ai of %s: %s' % (ROBOT, str(e)))
        self.avoid = True
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
        self.front = False
        self.back = False

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
