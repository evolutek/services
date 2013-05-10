#!/usr/bin/env python3
from threading import Thread, Event

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from robot import Robot

class ia(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        self.start_event = Event()

        self.robot = Robot()
        self.robot.setup()

        self.color = None

    @Service.event
    def match_start(self):
        self.start_event.set()

        print("Getting tracker...")
        print("Tracker: " + self.cs.tracker.init_color(color=color))
        print("Done!")

        self.cs.pmi.start(color='blue' if self.color == -1 else 'red')

    @Service.action
    def setup_match(self, color):
        self.color = color

    def start(self):
        self.start_event.wait()

        self.cs.actuators.collector_open()
        self.robot.goto_xy_block(x=1023.81, y=998.801)
        self.robot.goto_xy_block(x=1243.51, y=823.024)
        self.cs.actuators.collector_hold()
        self.robot.goto_theta_block(theta=-3.11914)
        self.cs.actuators.collector_open()
        self.robot.goto_xy_block(x=430.393, y=763.216)


def main():
    service = ia()
    service.setup()

    service_thread = Thread(target=service.start)
    service_thread.start()

    Service.loop()

if __name__ == '__main__':
    main()
