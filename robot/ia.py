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
        self.balloon_timer = Timer(90, self.cs.balloon.go)

        self.start_event = Event()
        self.stack_event = Event()

        self.robot = Robot()
        self.robot.setup()

        self.color = None

    @Service.event
    def match_start(self):
        self.start_event.set()

    @Service.event
    def stack(self):
        self.stack_event.set()

    @Service.action
    def setup_match(self, color):
        print("Setup")
        self.color = color

        print("Getting tracker...")
        print("Tracker: " + self.cs.tracker.init_color(color=color))
        print("Done!")

    def start(self):
        print("Start...")
        self.start_event.wait()
        print("Start!")

        self.match_stop_timer.start()
        self.balloon_timer.start()

        self.cs.trajman.set_trsl_dec(dec=1000)
        self.cs.trajman.set_pid_trsl(P=100, I=0, D=3000)
        self.cs.trajman.set_trsl_max_speed(maxspeed=800)

        self.cs.trajman.set_rot_acc(acc=15)
        self.cs.trajman.set_rot_dec(dec=15)
        self.cs.trajman.set_rot_max_speed(maxspeed=15)

        self.cs.pmi.start(color='blue' if self.color == -1 else 'red')

        self.cs.actuators.collector_open()

        print("Milieu de la table")

        if True:
            print("Cote adverse")
            self.robot.goto_xy_block(1500 - 0 * self.color, 1000)

            print("Milieu de la table")

        print("Courbe")
        #self.robot.curve_block(450, 450, 450, 225, 1, 3.14, 3.14, 3.14, 1.6, 1 if self.color == 1 else 0, 0)
        self.robot.goto_xy_block(1500 - 150 * self.color, 800)
        self.cs.actuators.collector_hold()
        self.robot.goto_theta_block(math.pi / 2 - math.pi / 2 * self.color)
        self.cs.actuators.collector_open()
        self.robot.goto_xy_block(1500 + 800 * self.color, 800)

        print("Setting glasses in place")
        self.robot.goto_xy_block(1500 + 850 * self.color, 800)
        self.robot.goto_theta_block(math.pi / 2 - math.pi / 2 * self.color)
        self.cs.actuators.collector_open()
        self.robot.goto_xy_block(1500 + 1100 * self.color, 800)

        print("Going to push")
        self.robot.goto_xy_block(1500 + 850 * self.color, 800)
        speeds = self.cs.trajman.get_speeds()
        self.robot.set_trsl_max_speed(300)
        self.cs.actuators.collector_close()
        print("Pushing")
        self.robot.goto_xy_block(1500 + 1300 * self.color, 800)

        print("Done")
        self.robot.set_trsl_max_speed(speeds['trmax'])
        self.robot.goto_xy_block(1500 + 950 * self.color, 800)

        self.cs('glass-ready1')

        # Décision 2
        #if True:
        print("Face opponent")
        self.robot.goto_theta_block(math.pi / 2 + math.pi / 2 * self.color)
        self.cs.actuators.collector_open()

        print("Going to opponent")
        if self.cs.tracker.is_safe(x=1500 - 500 * self.color, y=600):
            self.robot.goto_xy_block(1500 - 500 * self.color, 600)
        else:
            self.robot.goto_xy_block(1500 * self.color, 600)
        self.cs.actuators.collector_hold()
        sleep(.5)

        print("Going back")
        self.robot.goto_theta_block(math.pi / 2 - math.pi / 2 * self.color)
        self.cs.actuators.collector_open()
        self.robot.goto_xy_block(1500 + 1100 * self.color, 600)

        print("Going to push")
        self.robot.goto_xy_block(1500 + 850 * self.color, 600)
        self.cs.actuators.collector_close()
        speeds = self.cs.trajman.get_speeds()
        self.robot.set_trsl_max_speed(300)

        self.stack_event.wait()

        print("Pushing")
        self.robot.goto_xy_block(1500 + 1300 * self.color, 600)

        print("Done")
        self.robot.set_trsl_max_speed(speeds['trmax'])
        self.robot.goto_xy_block(1500 + 800 * self.color, 600)

        self.cs('glass-ready2')

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
