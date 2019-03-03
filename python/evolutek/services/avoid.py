#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.settings import ROBOT

from time import sleep

ROBOT= "pal"

@Service.require("config")
@Service.require("trajman", ROBOT)
@Service.require("gpios", ROBOT)
class Avoid(Service):
    def __init__(self):
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman[ROBOT]
        self.refresh = float(self.config.get(section='avoid', option='refresh'))

        self.telemetry = None
        self.front_detected = 0
        self.back_detected = 0
        self.avoid = False
        self.enabled = True

        super().__init__(ROBOT)

    @Service.thread
    def status(self):
        while True:
            s = {
                'front_detected' : self.front_detected,
                'back_detected' : self.back_detected,
                'avoid' : self.avoid
            }
            self.publish(ROBOT + '_avoid_status', s)
            sleep(self.refresh)

    @Service.thread
    def direction(self, value):
        while True:
            if self.telemetry is None:
                continue
            if not self.enabled:
                continue

            if self.telemetry['speed'] > 0.0 and self.front_detected > 0:
                self.trajman.stop_asap(2000, 30)
                self.avoid = True
                print("[AVOID] Front detection")
            elif self.telemetry['speed'] and self.back_detected > 0:
                self.trajman.stop_asap(2000, 30)
                self.avoid = True
                print("[AVOID] Back detection")
            else:
                self.avoid = False
            slee(self.refresh)
    
    @Service.action
    def enable(self):
        self.enabled = True

    @Service.action
    def disable(self):
        self.enabled = False

    @Service.event
    def front(self, name, id, value):
        if int(value):
            self.front_detected += 1
        elif self.front_detected > 0:
            self.front_detected -= 1

    # Update back detection
    @Service.event
    def back(self, name, id, value):
        if int(value):
            self.back_detected += 1
        elif self.back_detected > 0:
            self.back_detected -= 1

def main():
    avoid = Avoid()
    avoid.run()

if __name__ == '__main__':
    main()
