#!/usr/bin/env python3

from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy
from enum import Enum
#from evolutek.lib.map import Map
from evolutek.lib.goals import Goals
from evolutek.lib.settings import ROBOT
from threading import Event, Thread
from time import sleep

class State(Enum):
    Init = 0
    Setup = 1
    Waiting = 2
    Selecting = 3
    Making = 4
    Ending = 5

@Service.require('trajman', ROBOT)
@Service.require('actuators', ROBOT)
#@Service.require('avoid', ROBOT)
#@Service.require('gpios', ROBOT)
class Ai(Service):

    def __init__(self):

        self.state = State.Init
        print('Init')

        # Cellaserv
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman[ROBOT]
        self.actuators = self.cs.actuators[ROBOT]
        # self.recalibration_event = Event(set='recalibrated')

        # Config
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')
        self.color = self.color1  #@Andre : set color
        self.cs.config.set(section = "match", option = "color", value = self.color)

        self.max_trsl_speed = self.cs.config.get(section=ROBOT, option='trsl_max')
        self.max_rot_speed = self.cs.config.get(section=ROBOT, option='rot_max')

        # Parameters
        self.aborting = Event()
        self.current_action = None
        self.position = None
        self.robots = None
        self.tmp_robot = None
        self.robots = []

        # Match config
        #self.map = Map(3000, 2000, 25)
        self.goals = Goals(color = self.color, file = "keke.json")

        print('[AI] Initial Setup')
        self.setup(recalibration=False)

    @Service.action
    def setup(self, color=None, recalibration=True):
        print(self.state)
        if self.state != State.Init and self.state != State.Waiting and self.state != State.Ending:
            return
        self.state = State.Setup
        if isinstance(recalibration, str):
            recalibration = recalibration == "true"

        print('[AI] Setuping')
        self.trajman.enable()
        self.actuators.enable()
        #self.actuators.init_all()
        if color is not None:
            self.color = color

        if recalibration:
            self.recalibrate()
            self.trajman.goto_xy(x=self.goals.start_x, y=self.goals.start_y)
            while self.trajman.is_moving():
                sleep(0.1)
            self.trajman.goto_theta(self.goals.theta)
            while self.trajman.is_moving():
                sleep(0.1)
        else:
            self.trajman.free()
            self.trajman.set_x(self.goals.start_x)
            self.trajman.set_y(self.goals.start_y)
            self.trajman.set_theta(self.goals.theta)
            self.trajman.unfree()

        #self.goals.reset()

        self.state = State.Waiting
        print('[AI] Waiting')

    def recalibrate(self):
        sens = self.color == self.color2
        self.actuators.recalibrate(sens_y = sens, init=True)
        sleep(10)
        #self.recalibration_event.wait()
        #self.recalibration_event.clear()

    @Service.action
    def start(self):
        if self.state != State.Waiting:
            return

        print('[AI] Starting')
        self.selecting()

    @Service.action
    def end(self):
        print('[AI] Ending')
        self.state = State.Ending
        self.trajman.free()
        self.trajman.disable()
        self.actuators.disable_all()
        self.actuators.disable()

    @Service.action
    def abort(self, robot):
        if self.state != State.Making:
            return

        print('[AI] Aborting')
        self.aborting.set()

        if robot is not None:
            self.tmp_robot = robot

        #push back current action

    @Service.thread
    def debug(self):
        print("[AI] Current state : " + str(self.state))
        sleep(1)

    def selecting(self):
        if self.state != State.Wating or self.state != State.Making:
            return

        print('[AI] Selecting')
        self.state = State.Selecting

        current_action = None
        path = None

        # Select an action

        if current_acion is None:
            self.end()

        self.making(current_action, path)

    def making(self, current_acion, path):
        if self.state != State.Selecting:
            return

        print('[AI] Making')
        self.state = Setup.making
        if self.current_action.trsl_speed is not None:
            self.trajman.set_trsl_max_speed(current_action.trsl_speed)

        for point in path:
            self.trajman.goto_xy(x=point.x, y=point.y)
            while self.trajman.is_moving():
                sleep(0.5)
            if self.aborting.isSet():
                self.selecting()

        if self.current_action.rot_speed is not None:
            self.trajman.set_rot_max_speed(self.current_action.trsl_speed)

        if self.current_action.theta is not None:
            self.trajman.goto_theta(self.current_action.theta)

        if self.aborting.isSet():
            self.selecting()

        if not self.current_acion.avoid:
            self.avoid.disable()

        for action in self.current_acion.actions:
            action()
            if self.aborting.isSet():
                # memorize current action
                self.selecting()

        self.publish('score', self.current_acion.score)
        self.trajman.set_trsl_max_speed(self.max_trsl_speed)
        self.trajman.set_trsl_rot_speed(self.max_rot_speed)

        self.selecting()

def main():
    ai = Ai()
    ai.run()

if __name__ == '__main__':
    main()
