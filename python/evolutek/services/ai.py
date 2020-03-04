#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy

from evolutek.lib.fsm import Fsm
from evolutek.lib.goals import Goals, Avoid
#from evolutek.lib.gpio import Edge, Gpio
from evolutek.lib.robot import Robot
from evolutek.lib.settings import ROBOT

from enum import Enum
from threading import Event, Thread
from time import sleep

class States(Enum):
    Setup = "Setup"
    Waiting = "Waiting"
    Selecting = "Selecting"
    Making = "Making"
    Ending = "Ending"
    Error = "Error"

# TODO: update goals
# TODO: Config recalibration in goals
# TODO: Manage return status (action, robot)
# TODO: Manage Actuators
# TODO: Manage Avoid
# TODO: Manage Gpio

#@Service.require('actuators', ROBOT)
#@Service.require('trajman', ROBOT)
class Ai(Service):

    def __init__(self):
        print('[AI] Init')

        self.cs = CellaservProxy()
        self.robot = Robot.get_instance(robot=ROBOT)

        self.score = 0
        self.reset = Event()
        self.recalibration = Event()
        self.match_start = Event()
        self.match_end = Event()

        self.fsm = Fsm(States)
        self.fsm.add_state(States.Setup, self.setup, prevs=[States.Waiting, States.Ending])
        self.fsm.add_state(States.Waiting, self.waiting, prevs=[States.Setup])
        self.fsm.add_state(States.Selecting, self.selecting, prevs=[States.Waiting, States.Making])
        self.fsm.add_state(States.Making, self.making, prevs=[States.Selecting])
        self.fsm.add_state(States.Ending, self.ending, prevs=[States.Setup, States.Waiting, States.Selecting, States.Making])
        self.fsm.add_error_state(self.error)

        #Gpio(5, "tirette", False, edge=Edge.FALLING).auto_refresh(service=self)

        self.goals = Goals(cs=self.cs, file='lol')
        self.goal = None
        self.strategy = self.goals.strategies[0]


        super().__init__(ROBOT)
        print('[AI] Ready')
        Thread(target=self.fsm.start_fsm, args=[States.Setup]).start()


    """ SETUP """
    def setup(self):

        self.robot.tm.enable()
        #self.cs.actuators[ROBOT].reset()
        #self.robot.tm.enable_avoid()
        self.goals.reset(self.strategy)
        self.score = 0

        if self.recalibration.is_set():
            self.recalibration.clear()
            self.robot.recalibration(init=True)
            #self.robot.tm.disable_avoid()
            self.robot.goto(self.goals.start_x, self.goals.start_y)
            self.robot.goth(self.goals.start_theta)
            #self.robot.tm.enable_avoid()

        else:
            self.robot.tm.free()
            self.robot.set_pos(self.goals.start_x, self.goals.start_y, self.goals.start_theta)
            self.robot.tm.unfree()

        self.match_end.clear()

        return States.Waiting


    """ WAITING """
    def waiting(self):
        while not self.reset.is_set() and not self.match_start.is_set():
            sleep(0.1)
        self.reset.clear()
        self.match_start.clear()
        return States.Selecting


    """ SELECTING """
    def selecting(self):
        if self.match_end.is_set():
            return States.Ending

        self.goal = self.goals.get_goal()

        if self.goal is None:
            return States.Ending

        return States.Making


    """ MAKING """
    def making(self):

        print("[AI] making goal:\n%s" % str(self.goal))

        if self.match_end.is_set():
            return States.Ending

        self.robot.goto(self.goal.position.x, self.goal.position.y)
        self.robot.goth(self.goal.theta)


        if self.match_end.is_set():
            return States.Ending

        avoid = True

        for action in self.goal.actions:

            if self.match_end.is_set():
                return States.Ending

            #if avoid and not action.avoid:
            #    self.robot.tm.disable_avoid()
            #elif not avoid and action.avoid:
            #    self.robot.rm.enable_avoid()

            print("[AI] Making action:\n%s" % str(action))

            action.make()

            if action.score > 0:
                self.publish("score", value=action.score)
                self.score += action.score
                self.goal.score -= action.score

        if not avoid:
            self.robot.tm.enable_avoid()

        self.goals.finish_goal()
        if self.goal.score > 0:
            self.publish("score", value=self.goal.score)
            self.score += self.goal.score
        self.goal = None

        return States.Selecting


    """ ENDING """
    def ending(self):

        print("[AI] Match finished with score %d" % self.score)

        self.reset.wait()
        self.reset.clear()

        return States.Setup


    """ ERROR """
    def error(self):
        print('[AI] AI in error')

        self.match_end_handler()

        while True:
            pass

    """ HANDLERS """
    @Service.action("reset")
    def reset_handler(self):
        self.reset.set()

    @Service.event("match_start")
    def match_start_handler(self):
        self.match_start.set()

    @Service.event("match_end")
    @Service.action("stop_robot")
    def match_end_handler(self):
        self.match_end.set()
        self.robot.tm.free()
        self.robot.tm.disable()
        #self.cs.actuators[ROBOT].free()
        #self.cs.actuators[ROBOT].disable()

def main():
    ai = Ai()
    ai.run()

if __name__ == "__main__":
    main()
