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
        print("Done?")
        if self.done:
            return
        print("Not done")

        #self.cs.trajman.set_trsl_dec(dec=1000)
        #self.cs.trajman.set_pid_trsl(P=100, I=0, D=3000)
        #self.cs.trajman.set_trsl_max_speed(maxspeed=800)

        #self.cs.trajman.set_rot_acc(acc=15)
        #self.cs.trajman.set_rot_dec(dec=15)
        #self.cs.trajman.set_rot_max_speed(maxspeed=15)

        print("Trajman ok")

        self.cs.actuators.collector_open()

        print("Milieu de la table")
        #self.robot.goto_xy_block(1500 + 400 * self.color, 1100)

        # robots self.cs.tracker.
        # DÉCISION
        if True:
            print("Cote adverse")
            sleep(.1)
            self.robot.goto_xy_block(1500 - 500 * self.color, 1000)
            #self.cs.actuators.collector_hold()
            sleep(.5)

            print("Milieu de la table")
            #self.robot.goto_xy_block(1500 + 500 * self.color, 1100)
            #self.cs.actuators.collector_open()

        print("Courbe")
        #self.robot.curve_block(1000, 1000, 1000, 315, 1, 3.14, 3.14, 3.14, 1.6, 1, 0)
        #self.robot.curve_block(785, 785, 0, 196.25, 1, 3.14, 3.14, 3.14, 0.79, 1, 0)
        sleep(.1)
        self.robot.curve_block(450, 450, 450, 225, 1, 3.14, 3.14, 3.14, 1.6, 1 if self.color == 1 else 0, 0)
        #self.robot.curve_block(400, 0, 392.5, 315, 1, 0, 0, 0, 0, 1, 1)
        #self.robot.goto_xy_block(1500 + 1100 * self.color, 600)

        print("Setting glasses in place")
        sleep(.1)
        self.robot.goto_xy_block(1500 + 850 * self.color, 800)
        sleep(.1)
        self.robot.goto_theta_block(math.pi / 2 - math.pi / 2 * self.color)
        sleep(.1)
        self.cs.actuators.collector_open()
        self.robot.goto_xy_block(1500 + 1100 * self.color, 800)

        print("Going to push")
        self.robot.goto_xy_block(1500 + 850 * self.color, 800)
        speeds = self.cs.trajman.get_speeds()
        self.robot.set_trsl_max_speed(300)
        self.cs.actuators.collector_close()
        print("Pushing")
        self.robot.goto_xy_block(1500 + 1200 * self.color, 800)

        print("Done")
        self.robot.set_trsl_max_speed(speeds['trmax'])
        self.robot.goto_xy_block(1500 + 950 * self.color, 800)

        self.cs('glass-ready1')

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

# {{{
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
# }}}

# {{{
class Homologation(Goal):

    def __init__(self, cs, robot, color):
        self.cs = cs
        self.robot = robot
        self.color = color

        self.done = False

    def goto_xy_dodge(self, x, y):
        self.robot.goto_xy_block(x=x, y=y)

        return

    def execute(self):
        if self.done:
            return
        self.done = True

        self.cs.trajman.set_trsl_dec(dec=700)
        self.cs.trajman.set_pid_trsl(P=100, I=0, D=2000)
        self.cs.trajman.set_trsl_max_speed(maxspeed=200)

        self.cs.actuators.collector_open()
        self.goto_xy_dodge(1500 + 400 * self.color, 1100)
        self.cs.actuators.collector_hold()

        # go down
        self.goto_xy_dodge(1500 + 400 * self.color, 400)

        # face our side
        self.robot.goto_theta_block(math.pi / 2 - math.pi / 2 * self.color)
        self.cs.actuators.collector_open()

        # push
        self.goto_xy_dodge(1500 + 1100 * self.color, 400)

        # go back
        self.goto_xy_dodge(1500 + 850 * self.color,  400)
        self.cs.actuators.collector_close()

        # push more
        self.goto_xy_dodge(1500 + 1200 * self.color, 400)

        # go PMI!
        self.cs.pmi.start(color='blue')
        self.cs('line')
# }}}

class IA(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()
        self.robot = Robot()
        self.robot.setup()

        self.color = None

        # Timers

        self.balloon_timer = Timer(90, self.cs.balloon.go)
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
        self.robot.robot_near_event.clear()

        self.robot.match_start.set()
        self.balloon_timer.start()

        # go PMI!
        self.cs.pmi.start(color='blue' if self.color == -1 else 'red')

        self.match_stop_timer.start()

    @Service.event
    @Service.action
    def match_stop(self):
        print("MATCH STOP")
        self.robot.match_stop.set()
        self.cs.trajman.free()
        self.cs.actuators.free()

    ###########
    # Actions #
    ###########

    @Service.action
    def setup_match(self, color):
        self.color = color
        self.goals = [
                Cups(self.cs, self.robot, self.color),
                #Gift(self.cs, self.robot, self.color),
        ]

        print("Getting tracker...")
        print("Tracker: " + self.cs.tracker.init_color(color=color))
        print("Done!")

    @Service.action
    def setup_homologation(self, color):
        self.color = color
        self.goals = [
                Homologation(self.cs, self.robot, self.color),
        ]

        print("Getting tracker...")
        print("Tracker: " + self.cs.tracker.init_color(color=color))
        print("Done!")

    # Thread

    def objectives_loop(self):
        print("start")
        self.robot.match_start.wait()
        print(self.goals)
        print(self.robot.match_stop.is_set())
        self.cs.buzzer.freq_seconds(freq=440, seconds=1)
        print(self.goals)
        print(self.robot.match_stop.is_set())

        while not self.robot.match_stop.is_set():
            print("in loop")
            for goal in self.goals:
                goal.execute()

    # OWN THREAD
    def evitement(self):
        print("Evitement start")
        #return
        self.robot.match_start.wait()
        self.robot.robot_near_event.wait()
        #self.robot.robot_far_event.clear()

        print("Evitement")

        self.cs.buzzer.freq_seconds(freq=440, seconds=1)
        self.cs.trajman.free()
        self.cs.trajman.soft_free()
        self.cs.actuators.free()

        self.robot.robot_far_event.wait()

        self.cs.trajman.soft_asserv()

def main():
    ia = IA()
    ia.setup()

    thread_ia = Thread(target=ia.objectives_loop)
    thread_ia.start()

    ia.evitement = Thread(target=ia.evitement)
    ia.evitement.start()

    Service.loop()

if __name__ == '__main__':
    main()

# vim:fdm=marker:
