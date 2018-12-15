#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

@Service.require("trajman", "pal")
class Avoid(Service):
    def __init__(self):
        super().__init__("pal")
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman["pal"]

        self.direction = 0
        self.front_detected = False
        self.back_detected = False
        self.is_stopped = False

    @Service.event
    def direction(self, value):
        self.direction = value
        print(self.direction)

        if self.direction > 0 and self.front_detected:
            self.trajman.stop_asap(2000, 30)
            self.is_stopped = True
            print("[AVOID] Front detection")
        elif self.direction < 0 and self.back_detected:
            self.trajman.stop_asap(2000, 30)
            self.is_stopped = True
            print("[AVOID] Back detection")
        else:
            self.is_stopped = False

    @Service.event
    def front_detection(self, value):
        self.front_detected = bool(value)

    @Service.event
    def back_detection(self, value):
        self.back_detected = bool(value)

def main():
    avoid = Avoid()
    avoid.run()

if __name__ == '__main__':
    main()
