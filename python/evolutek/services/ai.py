#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from evolutek.lib.goals import Goals
from evolutek.lib.settings import ROBOT

from enum import Enum
from threading import Event, Thread
from time import sleep

# Hack to remove
ROBOT = "pal"

class State(Enum):
    Init = 0
    Setup = 1
    Waiting = 2
    Selecting = 3
    Making = 4
    Ending = 5
    Error = 6

@Service.require('trajman', ROBOT)
@Service.require('actuators', ROBOT)
@Service.require('avoid', ROBOT)
@Service.require('match')
class Ai(Service):

    def __init__(self):

        self.state = State.Init
        print('Init')

        # Cellaserv
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman[ROBOT]
        self.actuators = self.cs.actuators[ROBOT]
        self.avoid = self.cs.avoid[ROBOT]

        # Simple AI
        self.avoid_stat = None
        self.side = None

        # Config
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')
        self.color = self.cs.match.get_match()['color']

        self.refresh = float(self.cs.config.get(section='ai', option='refresh'))

        self.max_trsl_speed = self.cs.config.get(section=ROBOT, option='trsl_max')
        self.max_rot_speed = self.cs.config.get(section=ROBOT, option='rot_max')

        # Parameters
        self.aborting = Event()
        self.tmp_robot = None

        # Match config
        self.goals = Goals(file="keke.json", color = self.color, actuators = self.actuators, trajman = self.trajman)

        print('[AI] Initial Setup')
        super().__init__(ROBOT)
        self.setup(recalibration=False)

    @Service.thread
    def status(self):
        while True:
            self.publish(ROBOT + '_ai_status', status=str(self.state))
            sleep(self.refresh)

    @Service.event('%s_avoid_status' % ROBOT)
    def avoid_status(self, test, status={}):
        print(test)
        self.avoid_stat = status
        print(status)
    
    @Service.event('%s_reset' % ROBOT)
    @Service.action
    def setup(self, color=None, recalibration=True, **kwargs):

        if self.state != State.Init and self.state != State.Waiting and self.state != State.Ending:
            return
        self.state = State.Setup

        if isinstance(recalibration, str):
            recalibration = recalibration == "true"

        print('[AI] Setup')
        self.trajman.enable()
        self.actuators.reset()

        self.match_thread = Thread(target=self.selecting)
        self.match_thread.deamon = True

        if color is not None:
            self.color = color

        if recalibration:
            
            self.avoid.disable()

            """ Let robot recalibrate itself """
            sens = self.color == self.color2
            self.actuators.recalibrate(sens_y=sens, init=True)

            """ Goto to starting pos """
            self.trajman.goto_xy(x=self.goals.start_x, y=self.goals.start_y)
            while self.trajman.is_moving():
                sleep(0.1)
            self.trajman.goto_theta(self.goals.theta)
            while self.trajman.is_moving():
                sleep(0.1)
        else:
            """ Set Default config """
            self.trajman.free()
            self.trajman.set_x(self.goals.start_x)
            self.trajman.set_y(self.goals.start_y)
            self.trajman.set_theta(self.goals.theta)
            self.trajman.unfree()

        self.goals.reset()

        self.avoid.enable()
        self.state = State.Waiting
        print('[AI] Waiting')

    @Service.action
    def start(self):
        if self.state != State.Waiting:
            return

        print('[AI] Starting')
        self.match_thread.start()

    @Service.action
    def end(self):
        print('[AI] Ending')
        self.abort()
        self.state = State.Ending
        self.trajman.free()
        self.trajman.disable()

    @Service.action
    def abort(self, robot=None, side=None):

        if self.state != State.Making:
            return

        self.side = side

        print('[AI] Aborting')
        self.aborting.set()

        if robot is not None:
            self.tmp_robot = robot

        # Give it to the map

    def selecting(self):
        if self.state != State.Waiting and self.state != State.Making:
            return

        if self.side is not None:
            sleep(1.0)
            field = ''
            if self.side == 'front':
                field = 'front_detected'
            else:
                field = 'back_detected'
            while len(self.avoid_stat[field]) > 0:
                print('-----avoiding-----')
                sleep(0.1)
            side = None

        """ Clear abort event """
        self.aborting.clear()

        print('[AI] Selecting')
        self.state = State.Selecting

        goal = self.goals.get_goal()

        if goal is None:
            self.end()

        self.making(goal)

        # Select an action
        #optimum  = self.map.get_optimal_goal(self.goals.get_available_goals())
        #current_action = optimum[0]
        #path = optimum[1]

        #if current_action is None:
        #    self.end()

        #if path is None:
        #  self.state = State.Selecting

        self.making()

    def making(self, goal=None, path=None):

        if self.state != State.Selecting:
            return

        print('[AI] Making')
        self.state = State.Making

        """ Goto x y """
        self.trajman.goto_xy(x = goal.x, y = goal.y)
        while self.trajman.is_moving():
            sleep(0.1)
        sleep(0.2)
        if self.aborting.isSet():
            print("[AI][MAKING] Aborted")
            self.selecting()

        """ Goto theta if there is one """
        if goal.theta is not None:
            self.trajman.goto_theta(goal.theta)
            while self.trajman.is_moving():
                sleep(0.1)
            sleep(0.2)
            if self.aborting.isSet():
                print("[AI][MAKING] Aborted")
                self.selecting()

        """ Make all actions """
        for action in goal.actions:

            """ Set parameters """
            if action.trsl_speed is not None:
                self.trajman.set_trsl_max_speed(action.trsl_speed)
            if action.rot_speed is not None:
                self.trajman.set_rot_max_speed(action.rot_speed)
            if not action.avoid:
                self.avoid.disable()

            """ Make action """
            action.make()
            sleep(0.2)
            if self.aborting.isSet():
                print("[AI][MAKING] Aborted")
                self.selecting()

            """ Make things back """
            if action.trsl_speed is not None:
                self.trajman.set_trsl_max_speed(self.max_trsl_speed)
            if action.rot_speed is not None:
                self.trajman.set_rot_max_speed(self.max_rot_speed)
            if not action.avoid:
                self.avoid.enable()

        print("[AI] Finished goal")
        self.goals.finish_goal()

        self.publish('score', goal.score) # Increment score variable in match
        self.selecting()

def main():
    ai = Ai()
    ai.run()

if __name__ == '__main__':
    main()
