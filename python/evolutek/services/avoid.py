#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.settings import ROBOT

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

        super().__init__(ROBOT)

    @Service.thread
    def status(self):
        while True:
            s = {
                'front_detected' : self.front_detected,
                'back_detected' : self.back_detected,
                'avoid' : self.avoid,
                'enabled' : self.enabled
            }
            self.publish(ROBOT + '_avoid_status', s)
            sleep(self.refresh)

    @Service.thread
    def loop_avoid(self):
        while True:
            if self.telemetry is None:
                continue
            if not self.enabled:
                continue

            if self.telemetry['speed'] > 0.0 and len(self.front_detected) > 0:
                self.trajman.stop_asap(2000, 30)
                self.avoid = True
                print("[AVOID] Front detection")
            elif self.telemetry['speed'] < 0.0 and len(self.back_detected) > 0:
                self.trajman.stop_asap(2000, 30)
                self.avoid = True
                print("[AVOID] Back detection")
            else:
                self.avoid = False
            sleep(self.refresh)

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

    @Service.event('%s_telemetry')
    def telemetry(self, status, telemetry):
        if self.status == 'failed':
            self.telemetry = None
        else:
            self.telemetry = telemetry

def main():
    avoid = Avoid()
    avoid.run()

if __name__ == '__main__':
    main()
