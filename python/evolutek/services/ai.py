#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from evolutek.lib.goals import Goals
from evolutek.lib.settings import ROBOT

from enum import Enum
from math import sqrt
from threading import Event, Thread
from time import sleep

class State(Enum):
    Init = 0
    Setup = 1
    Waiting = 2
    Selecting = 3
    Making = 4
    Ending = 5
    Error = 6

##TODO: Check errors and set to Error State
@Service.require('avoid', ROBOT)
@Service.require('trajman', ROBOT)
@Service.require('actuators', ROBOT)
class Ai(Service):

    """ INIT """
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
        self.avoid_disable = False

        # Config
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color = None
        try:
            self.color = self.cs.match.get_match()['color']
        except Exception as e:
            print('Failed to set color: %s' % (str(e)))

        self.refresh = float(self.cs.config.get(section='ai', option='refresh'))

        self.max_trsl_speed = self.cs.config.get(section=ROBOT, option='trsl_max')
        self.max_rot_speed = self.cs.config.get(section=ROBOT, option='rot_max')

        # Parameters
        self.aborting = Event()
        self.ending = Event()
        self.tmp_robot = None

        # Match config
        self.goals = Goals(file="simple_strategy.json", mirror=self.color!=self.color1, cs=self.cs)

        print('[AI] Initial Setup')
        super().__init__(ROBOT)
        self.setup(recalibration=False)

    """ SETUP """
    @Service.event('%s_reset' % ROBOT)
    @Service.action
    def setup(self, color=None, recalibration=True, **kwargs):

        if self.state != State.Init and self.state != State.Waiting and self.state != State.Ending:
            return
        self.state = State.Setup

        if isinstance(recalibration, str):
            recalibration = recalibration == "true"

        print('[AI] Setup')

        try:
            self.color = self.cs.match.get_match()['color']
        except Exception as e:
            print('Failed to set color: %s' % (str(e)))

        self.trajman.enable()
        self.actuators.reset(self.color)
        self.avoid.disable()

        self.match_thread = Thread(target=self.selecting)
        self.match_thread.deamon = True

        if color is not None:
            self.color = color

        #if recalibration:

         #   self.avoid.disable()

            """ Let robot recalibrate itself """
          #  sens = self.color != self.color1
          #  self.actuators.recalibrate(sens_y=sens, init=True)

            """ Goto to starting pos """
           # self.trajman.goto_xy(x=self.goals.start_x, y=self.goals.start_y)
           # while self.trajman.is_moving():
           #    sleep(0.1)
           # self.trajman.goto_theta(self.goals.theta)
           # while self.trajman.is_moving():
            #    sleep(0.1)
        #else:
        """ Set Default config """
        self.trajman.free()
        self.trajman.set_x(self.goals.start_x)
        self.trajman.set_y(self.goals.start_y)
        self.trajman.set_theta(self.goals.start_theta)
        self.trajman.unfree()

        if not self.goals.reset(self.color!=self.color1):
            print('[AI] Error')
            self.state = State.Error
            return

        self.avoid.enable()
        self.avoid_disable = False

        self.aborting.clear()
        self.ending.clear()

        self.state = State.Waiting
        print('[AI] Waiting')

    """ SELECTING """
    def selecting(self):
        if self.state != State.Waiting and self.state != State.Making:
            return

        """ WAIT FOR END OF DETECTION """
        ##TODO: patch

        self.wait_until_detection_end()

        if self.ending.isSet():
            return

        """ Clear abort event """
        self.aborting.clear()

        print('[AI] Selecting')
        self.state = State.Selecting

        goal = self.goals.get_goal()

        if goal is None:
            self.end()

        self.making(goal)

        ##TODO: Select a goal

    """ MAKING """
    def making(self, goal=None, path=None):

        if self.state != State.Selecting:
            return

        if self.ending.isSet():
            return

        print('[AI] Making')
        self.state = State.Making

        """ Goto x y """
        pos = self.trajman.get_position()
        while sqrt((pos['x'] - goal.x)**2 + (pos['y'] - goal.y)**2) > 5:
            self.trajman.goto_xy(x = goal.x, y = goal.y)
            while not self.ending.isSet() and not self.aborting.isSet() and self.trajman.is_moving():
                sleep(0.1)

            if self.ending.isSet():
                return
            #if self.aborting.isSet():
            #    print("[AI][MAKING] Aborted")
            #    self.selecting()
            if self.aborting.isSet():
                self.wait_until_detection_end()

            pos = self.trajman.get_position()

        """ Goto theta if there is one """
        if goal.theta is not None:

            while abs(pos['theta'] - goal.theta) > 0.5:
                self.trajman.goto_theta(goal.theta)
                while not self.ending.isSet() and not self.aborting.isSet() and self.trajman.is_moving():
                sleep(0.1)

                if self.ending.isSet():
                    return
                #if self.aborting.isSet():
                #    print("[AI][MAKING] Aborted")
                #    self.selecting()

                if self.aborting.isSet():
                    self.wait_until_detection_end()

                pos = self.trajman.get_position()

        """ Make all actions """
        i = 0
        while i < len(goal.actions):

            if self.ending.isSet():
                return

            action = goal.actions[i]

            """ Set parameters """
            if action.trsl_speed is not None:
                self.trajman.set_trsl_max_speed(action.trsl_speed)
            if action.rot_speed is not None:
                self.trajman.set_rot_max_speed(action.rot_speed)

            if not action.avoid and not self.avoid_disable:
                self.avoid_disable = True
                self.avoid.disable()
            elif action.avoid and self.avoid_disable:
                self.avoid_disable = False
                self.avoid.enable()

            """ Make action """
            action.make()
            while not self.ending.isSet() and not self.aborting.isSet() and self.trajman.is_moving():
                sleep(0.1)

            if self.ending.isSet():
                return

            if self.aborting.isSet():
                print("[AI][MAKING] Aborted")
                self.wait_until_detection_end()
                continue

            if self.ending.isSet():
                return

            """ Make things back """
            if action.trsl_speed is not None:
                self.trajman.set_trsl_max_speed(self.max_trsl_speed)
            if action.rot_speed is not None:
                self.trajman.set_rot_max_speed(self.max_rot_speed)

            i += 1

        if self.avoid_disable:
            self.avoid_disable = False
            self.avoid.enable()

        print("[AI] Finished goal")
        self.goals.finish_goal()

        self.publish('score', value=goal.score) # Increment score variable in match
        self.selecting()

    """ END """
    @service.event('match_end')
    @Service.action
    def end(self):
        print('[AI] Ending')
        self.ending.set()

        # STOP ROBOT
        self.trajman.free()
        self.trajman.disable()
        self.actuators.free()
        self.actuators.disable()

        self.state = State.Ending

    """ UTILITIES """
    @Service.thread
    def status(self):
        while True:
            self.publish(ROBOT + '_ai_status', status=str(self.state))
            sleep(self.refresh)


    @service.event('match_start')
    @Service.action
    def start(self):
        if self.state != State.Waiting:
            return

        print('[AI] Starting')
        self.match_thread.start()
        return

    """ ABORT """
    @Service.action
    def abort(self, robot=None, side=None):

        if self.state != State.Making:
            return

        self.side = side

        print('[AI] Aborting')
        self.aborting.set()

        if robot is not None:
            self.tmp_robot = robot

        ##TODO Give tmp robot to the map
        ##TODO: Manage tmp robots

    """ WAIT FOR END OF DETECTION """
    def wait_until_detection_end(self):

        self.avoid_stat = self.avoid.status()
        if self.side is not None and self.avoid_stat is not None:
            field = ''
            if self.side == 'front':
                field = 'front_detected'
            else:
                field = 'back_detected'
            while not self.ending.isSet() and self.avoid_stat[field] is not None and len(self.avoid_stat[field]) > 0:
                self.avoid_stat = self.avoid.status()
                print('-----avoiding-----')
                sleep(0.1)
            side = None

def main():
    ai = Ai()
    ai.run()

if __name__ == '__main__':
    main()
