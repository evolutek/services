#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

@Service.require("trajman", "pal")
class Avoid(Service):
    def __init__(self):
        super().__init__("pal")
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman["pal"]
        self.direction = True
        self.is_stopped = False

    #@Service.event
    def direction(self, value):
        self.direction = value
        print(self.direction)

    @Service.event
    def front_detection(self):
        print(self.direction)
        if self.direction == True:
            self.trajman.stop_asap(2000, 30)
            self.is_stopped = True

    @Service.event
    def back_detection(self):
        print(self.direction)
        if self.direction == False:
            self.trajman.stop_asap(2000, 30)
            self.is_stopped = True

    @Service.event
    def back_end_detection(self):
        self.is_stopped = False
        print("Robot stopped being stopped")

    @Service.event
    def front_end_detection(self):
        self.is_stopped = False
        print("Robot stopped being stopped")

def main():
    avoid = Avoid()
    avoid.run()

if __name__ == '__main__':
    main()
