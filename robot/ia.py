#!/usr/bin/env python3

import math
from time import sleep

from threading import Thread, Timer, Event

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

from robot import Robot

class Goal:
    def __init__(self, cs, robot, x, y, points):
        self.cs = cs
        self.robot = robot
        self.x = x
        self.y = y
        self.points = points

class Cups(Goal):
    def __init__(self, cs, robot, color):
        super().__init__(cs, robot, 1500 + 1000 * color, 1050, 100)
        self.color = color

        self.done = False

    def execute(self):
        if self.done:
            return

        self.cs.trajman.set_trsl_dec(dec=700)
        self.cs.trajman.set_pid_trsl(P=100, I=0, D=2000)

        self.cs.actuators.collector_open()

#        import pdb; pdb.set_trace()

        print("Milieu de la table")
        #self.robot.goto_xy_block(1500 + 400 * self.color, 1100)

        # robots self.cs.tracker.
        # DÉCISION
        if True:
            print("Coté adverse")
            self.robot.goto_xy_block(1500 - 500 * self.color, 1100)
            #self.cs.actuators.collector_hold()
            sleep(.5)

            print("Milieu de la table")
            #self.robot.goto_xy_block(1500 + 500 * self.color, 1100)
            #self.cs.actuators.collector_open()

        print("Courbe")
        #self.robot.curve_block(1000, 1000, 1000, 315, 1, 3.14, 3.14, 3.14, 1.6, 1, 0)
        #self.robot.curve_block(785, 785, 0, 196.25, 1, 3.14, 3.14, 3.14, 0.79, 1, 0)
        self.robot.curve_block(450, 450, 450, 225, 1, 3.14, 3.14, 3.14, 1.6, 1, 0)
        self.robot.get_position()
        #self.robot.curve_block(400, 0, 392.5, 315, 1, 0, 0, 0, 0, 1, 1)
        #self.robot.goto_xy_block(1500 + 1100 * self.color, 600)

        print("Setting glasses in place")
        self.robot.goto_xy_block(1500 + 850 * self.color, 600)
        self.robot.goto_theta_block(math.pi / 2 - math.pi / 2 * self.color)
        self.cs.actuators.collector_open()
        self.robot.goto_xy_block(1500 + 1100 * self.color, 600)

        print("Going to push")
        self.robot.goto_xy_block(1500 + 850 * self.color, 600)
        speeds = self.cs.trajman.get_speeds()
        self.robot.set_trsl_max_speed(300)
        self.cs.actuators.collector_close()
        print("Pushing")
        self.robot.goto_xy_block(1500 + 1200 * self.color, 600)

        print("Done")
        self.robot.set_trsl_max_speed(speeds['trmax'])
        self.robot.goto_xy_block(1500 + 900 * self.color, 600)

        # Décision 2
        if True:
            print("Face opponent")
            self.robot.goto_theta_block(math.pi / 2 + math.pi / 2 * self.color)
            self.cs.actuators.collector_open()

            print("Going to opponent")
            self.robot.goto_xy_block(1500 - 500 * self.color, 600)
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
            print("Pushing")
            self.robot.goto_xy_block(1500 + 1200 * self.color, 600)

            print("Done")
            self.robot.set_trsl_max_speed(speeds['trmax'])
            self.robot.goto_xy_block(1500 + 800 * self.color, 600)

        self.done = True

class Gift(Goal):

    def __init__(self, cs, robot, color):
        self.cs = cs
        self.robot = robot
        self.color = color

        self.gifts_done= [False]*4
        self.arm_setup = False

    def setup(self):
        if not self.arm_setup:
            self.arm_setup = True
            self.cs.actuators.arm_2_gift_setup()

    def unsetup(self):
        self.arm_setup = False
        self.cs.actuators.arm_2_raise()

    def execute(self):
        #import pdb; pdb.set_trace()

        # Find nearest gift not done & no
        for i in range(4): # 4 gifts
            if not self.gifts_done[i]:
                ###
                # TODO: Évitement
                ####

                self.setup()
                self.robot.goto_xy_block(600 + 600 * i + 85 * -self.color - 20, 400)
                self.robot.goto_theta_block(math.pi / 2 + math.pi / 2 * self.color)
                self.cs.actuators.arm_2_gift_push()
                sleep(.6)
                self.gifts_done[i] = True

        self.unsetup()

class HomologationPoints(Goal):

    def __init__(self, cs, robot, color):
        self.cs = cs
        self.robot = robot
        self.color = color

        self.done = False

    def execute(self):
        if self.done:
            return

        self.cs.trajman.set_trsl_dec(dec=700)
        self.cs.trajman.set_pid_trsl(P=100, I=0, D=2000)

        self.cs.actuators.collector_open()
        self.robot.goto_xy_block(1500 + 400 * self.color, 1100)
        self.cs.actuators.collector_hold()
        sleep(.5)

        # face our side
        self.robot.goto_theta_block(math.pi / 2 - math.pi / 2 * self.color)
        self.cs.actuators.collector_open()

        self.robot.goto_xy_block(1500 + 1200 * self.color, 1100)

        self.robot.goto_xy_block(1500 + 850 * self.color, 1100)
        self.cs.actuators.collector_close()
        self.robot.goto_xy_block(1500 + 1200 * self.color, 1100)
        self.robot.goto_xy_block(1500 + 850 * self.color, 1100)

        # XXX: pmi start

        self.done = True

class HomologationEvitement(Goal):

    def __init__(self, cs, robot, color):
        self.cs = cs
        self.robot = robot
        self.color = color

        self.done = False

        self.square = [
                (1500 + 1000 * self.color, 1000),
                (1500 + 1000 * self.color, 500),
                (1500 + 500 * self.color, 500),
                (1500 + 500 * self.color, 1000),
        ]

    def execute(self):
        if self.done:
            return
        self.done = True

        self.cs.trajman.set_trsl_dec(dec=700)
        self.cs.trajman.set_pid_trsl(P=100, I=0, D=2000)
        self.cs.trajman.set_trsl_max_speed(maxspeed=500)

        while True:
            for x, y in self.square:
                self.robot.is_stopped.clear()
                self.cs.trajman.goto_xy(x=x, y=y)
                while not self.robot.is_stopped.is_set():

                    if (self.robot.robot_near_event.is_set()
                            or self.robot.match_stop.is_set()):
                        self.cs.trajman.free()
                        return

                    sleep(.1)

class IA(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()
        self.robot = Robot()
        self.robot.setup()

        self.color = None

        # Timers

        #self.balloon_timer = Timer(90, self.cs.balloon.go) XXX
        self.match_stop_timer = Timer(85, self.match_stop)

        # Events
        self.robot.match_start = Event()
        self.robot.match_stop = Event()

        # Goals
        # Goals are set in setup()
        self.goals = []

    ##########
    # Events #
    ##########

    @Service.event
    @Service.action
    def match_start(self):
        print('Match start')
        self.robot.match_start.set()
        #self.balloon_timer.start() XXX
        self.match_stop_timer.start()
        self.cs.apmi.move(s=500, d=1)
        sleep(4)
        self.cs.apmi.move(s=0, d=1)

    @Service.event
    @Service.action
    def match_stop(self):
        print("MATCH STOP")
        self.cs.trajman.free()
        self.robot.match_stop.set()
        import os
        os.system('killall cellaserv')
        #self.actuators.free() XXX

    ###########
    # Actions #
    ###########

    @Service.action
    def setup_match(self, color):
        self.color = color
        self.goals = [
                #Cups(self.cs, self.robot, self.color),
                Gift(self.cs, self.robot, self.color),
        ]

    @Service.action
    def setup_homologation(self, color):
        self.color = color
        self.goals = [
                HomologationPoints(self.cs, self.robot, self.color),
                HomologationEvitement(self.cs, self.robot, self.color),
        ]

    # Thread

    def objectives_loop(self):
        self.robot.match_start.wait()

        while not self.robot.match_stop.is_set():
            for goal in self.goals:
                goal.execute()

def main():
    ia = IA()
    ia.setup()

    thread_ia = Thread(target=ia.objectives_loop)
    thread_ia.start()

    Service.loop()

if __name__ == '__main__':
    main()
