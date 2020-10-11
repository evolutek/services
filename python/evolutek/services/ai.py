#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy

from evolutek.lib.fsm import Fsm
from evolutek.lib.goals import Goals, AvoidStrategy
from evolutek.lib.gpio import Edge, Gpio
from evolutek.lib.robot import Robot, Status
from evolutek.lib.settings import ROBOT

from enum import Enum
from threading import Event, Thread
from time import sleep
from math import pi

class States(Enum):
    Setup = "Setup"
    Waiting = "Waiting"
    Selecting = "Selecting"
    Making = "Making"
    Ending = "Ending"
    Error = "Error"

@Service.require('actuators', ROBOT)
@Service.require('trajman', ROBOT)
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

        Gpio(17, "tirette", False, edge=Edge.FALLING).auto_refresh(callback=self.publish)

        # TODO : change strat file
        #self.goals = Goals(file='/etc/conf.d/strategy-%s.json' % ROBOT, ai=self)

        self.goals = Goals(file='/etc/conf.d/test_strats.json', ai=self)
        print(self.goals)
        self.goal = None

        super().__init__(ROBOT)
        print('[AI] Ready')
        Thread(target=self.fsm.start_fsm, args=[States.Setup]).start()


    """ SETUP """
    def setup(self):

        self.robot.tm.enable()

        self.robot.tm.set_mdb_config(mode=2)

        self.cs.actuators[ROBOT].reset()
        self.robot.tm.disable_avoid()

        self.goals.reset(self.strategy_index)
        self.score = 0

        if self.recalibration.is_set():
            self.recalibration.clear()
            self.robot.recalibration(init=True)
            self.robot.goto(self.goals.starting_position.x, self.goals.starting_position.y)
            self.robot.goth(self.goals.starting_theta)


        else:
            self.robot.tm.free()
            self.robot.set_pos(
                self.goals.starting_position.x,
                self.goals.starting_position.y,
                self.goals.starting_theta)
            self.robot.tm.unfree()

        self.match_end.clear()

        return States.Waiting


    """ WAITING """
    def waiting(self):
        while not self.reset.is_set() and not self.match_start.is_set():
            sleep(0.1)

        next = States.Selecting if self.match_start.is_set() else States.Setup
        self.reset.clear()
        self.match_start.clear()

        self.robot.tm.enable_avoid()
        # TODO : Change MDB mode
        # TODO : Launch critical goal timer

        return next


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

        print("[AI] Making goal:\n%s" % str(self.goal))

        if self.match_end.is_set():
            return States.Ending

        goal_score = self.goal.score

        status = self.robot.goto_with_path(self.goal.position.x, self.goal.position.y)

        if status != Status.reached:
            pass
            # TODO : retry ?
            # TODO : optional goal

        if not self.goal.theta is None:
            self.robot.goth(self.goal.theta)
            # TODO : has avoid ?

        if self.match_end.is_set():
            return States.Ending

        for action in self.goal.actions:

            if self.match_end.is_set():
                return States.Ending

            # TODO: manage Avoid

            print("[AI] Making action:\n%s" % str(action))

            action.make()

            # TODO : Check the action return

            if action.score > 0:
                self.publish("score", value=action.score)
                self.score += action.score
                goal_score -= action.score

        self.goals.finish_goal()
        if self.goal.score > 0:
            self.publish("score", value=goal_score)
            self.score += goal_score

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
    """ GO HOME """
    # def go_home(self):
    #     print('[AI] Going home before start match')
    #     self.cs.recalibration(x=True, y=True, side_x=True, side_y=False, init=True)
    #     self.cs.goto_xy_block(300, 1000)
    #     self.cs.goto_xy_block(620, 1000)
    #     self.cs.goto_theta_block(pi / 2)
    #     self.cs.move_trsl(dest=1000, acc=500, dec=500, maxspeed=300, sens=False)


    """ HANDLERS """
    @Service.action("reset")
    def reset_handler(self):
        self.reset.set()

    @Service.action
    def set_strategy(self, index):
        self.strategy_index = int(index)

    @Service.event("match_start")
    def match_start_handler(self):
        self.match_start.set()

    @Service.event("match_end")
    @Service.action("stop_robot")
    def match_end_handler(self):
        # TODO : Use leds ?

        self.match_end.set()
        self.robot.tm.free()
        self.robot.tm.disable()
        self.cs.actuators[ROBOT].free()
        self.cs.actuators[ROBOT].disable()

    # TODO : manage critical goal

    def sleep_ai(self):
        print('[AI] I am sleeping')
        sleep(1)

def main():
    ai = Ai()
    ai.run()

if __name__ == "__main__":
    main()
