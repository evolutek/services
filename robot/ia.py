#!/usr/bin/env python3
from time import sleep
import math
from threading import Thread, Timer, Event

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from robot import Robot

class ia(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        self.match_stop_timer = Timer(85, self.match_stop)
        #self.balloon_timer = Timer(90, self.cs.balloon.go)

        self.start_event = Event()

        self.robot = Robot()
        self.robot.setup()

        self.color = None
        self.diam = 0

    @Service.event
    def match_start(self):
        self.start_event.set()

    @Service.action
    def setup_match(self, color):
        print("Setup")
        if type(color) == str:
            if color[0] == "y":
                self.color = 1
            else:
                self.color = -1
        else:
            self.color = color
        self.cs.trajman.set_x(142)
        self.cs.trajman.set_y(1500 + self.color * (1500 - 302/2 - 32))
        self.cs.trajman.set_theta(0)

        self.cs.trajman.set_trsl_dec(dec=500)
        self.cs.trajman.set_trsl_acc(dec=500)
        self.cs.trajman.set_pid_trsl(P=100, I=0, D=3000)
        self.cs.trajman.set_trsl_max_speed(maxspeed=500)

        self.cs.trajman.set_rot_acc(acc=10)
        self.cs.trajman.set_rot_dec(dec=10)
        self.cs.trajman.set_rot_max_speed(maxspeed=10)
        #print("Getting tracker...")
        #print("Tracker: " + self.cs.tracker.init_color(color=color))
        #print("Done!")

    def start(self):
        print("Start...")
        self.start_event.wait()
        print("Start!")

        self.match_stop_timer.start()

        #self.cs.actuators.collector_open()
        self.robot.goto_xy_block(600, 1500 + self.color * (1500 - 302/2 -
            23))
        self.robot.goto_xy_block(1100, 1500 + self.color * 1100)
        self.robot.goto_xy_block(600, 1500 + self.color * 1100)
        self.robot.goto_theta_block(math.pi / 2 * -self.color)
        self.robot.goto_xy_block(600, 1500)

        self.robot.goto_xy_block(600, 1500 + self.color * 150)
        self.robot.goto_theta_block(0)
        speeds = self.cs.trajman.get_speeds()
        self.robot.set_trsl_max_speed(100)
        self.robot.goto_xy_block(142, 1500 + self.color * 150)
        self.robot.set_trsl_max_speed(speeds['trmax'])
        self.robot.goto_xy_block(600, 1500 + self.color * 150)





    def match_stop(self):
        print("Stop")
        self.cs.trajman.free()
        self.cs.trajman.soft_free()
        self.cs.actuators.free()

def main():
    service = ia()
    service.setup()

    service_thread = Thread(target=service.start)
    service_thread.start()

    Service.loop()

if __name__ == '__main__':
    main()
