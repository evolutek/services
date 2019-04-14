#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from evolutek.lib.goals import Goals
from evolutek.lib.settings import ROBOT

from enum import Enum
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
##TODO: Do we need to depend of avoid ?
@Service.require('avoid', ROBOT)
@Service.require('trajman', ROBOT)
@Service.require('actuators', ROBOT)
@Service.require('match')
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

        # Config
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color = self.cs.match.get_match()['color']

        self.refresh = float(self.cs.config.get(section='ai', option='refresh'))

        self.max_trsl_speed = self.cs.config.get(section=ROBOT, option='trsl_max')
        self.max_rot_speed = self.cs.config.get(section=ROBOT, option='rot_max')

        # Parameters
        self.aborting = Event()
        self.ending = Event()
        self.tmp_robot = None

        # Match config
        self.goals = Goals(file="get_palet.json", mirror=self.color!=self.color1, cs=self.cs)

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
        self.trajman.enable()
        self.actuators.reset(self.color)

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
        self.trajman.set_theta(self.goals.theta)
        self.trajman.unfree()

        if not self.goals.reset(self.color!=self.color1):
            print('[AI] Error')
            self.state = State.Error
            return

        self.avoid.enable()

        self.aborting.clear()
        self.ending.clear()

        self.state = State.Waiting
        print('[AI] Waiting')

    """ SELECTING """
    def selecting(self):
        if self.state != State.Waiting and self.state != State.Making:
            return

        if self.ending.isSet():
            return

        """ WAIT FOR END OF DETECTION """
        ##TODO: patch

        self.wait_until_detection_end()

        """ Clear abort event """
        self.aborting.clear()

        if self.ending.isSet():
            return

        print('[AI] Selecting')
        self.state = State.Selecting

        goal = self.goals.get_goal()

        if goal is None:
            self.end()

        self.making(goal)

        ##TODO: Select an action

        self.making()

    """ WAIT FOR END OF DETECTION """
    def wait_until_detection_end(self):

        self.avoid_stat = self.avoid.status()
        if self.side is not None and self.avoid_stat is not None:
            sleep(1.0)
            field = ''
            if self.side == 'front':
                field = 'front_detected'
            else:
                field = 'back_detected'
            while self.avoid_stat[field] is not None and len(self.avoid_stat[field]) > 0:
                if self.ending.isSet():
                    return
                self.avoid_stat = self.avoid.status()
                print('-----avoiding-----')
                sleep(0.3)
            side = None


    """ MAKING """
    def making(self, goal=None, path=None):

        if self.state != State.Selecting:
            return

        if self.ending.isSet():
            return

        print('[AI] Making')
        self.state = State.Making

        """ Goto x y """
        self.trajman.goto_xy(x = goal.x, y = goal.y)
        while self.trajman.is_moving():
            sleep(0.1)
        sleep(1)
        if self.ending.isSet():
            return
        if self.aborting.isSet():
            print("[AI][MAKING] Aborted")
            self.selecting()

        """ Goto theta if there is one """
        if goal.theta is not None:
            self.trajman.goto_theta(goal.theta)
            while self.trajman.is_moving():
                sleep(0.1)
            sleep(1)
            if self.ending.isSet():
                return
            if self.aborting.isSet():
                print("[AI][MAKING] Aborted")
                #self.aborting()
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
            while self.trajman.is_moving():
                sleep(0.1)
            sleep(1)
            if self.ending.isSet():
                return
            if self.aborting.isSet():
                print("[AI][MAKING] Aborted")
                self.wait_until_detection_end()
                action.make()
                while self.trajman.is_moving():
                    sleep(0.1)
            """ Make things back """
            if action.trsl_speed is not None:
                self.trajman.set_trsl_max_speed(self.max_trsl_speed)
            if action.rot_speed is not None:
                self.trajman.set_rot_max_speed(self.max_rot_speed)
            if not action.avoid:
                self.avoid.enable()

            if self.ending.isSet():
                return

        print("[AI] Finished goal")
        self.goals.finish_goal()

        self.publish('score', value=goal.score) # Increment score variable in match
        self.selecting()

    """ END """
    @Service.action
    def end(self):
        print('[AI] Ending')

        # STOP ROBOT
        self.trajman.free()
        self.trajman.disable()
        self.actuators.free()
        self.actuators.disable()

        self.ending.set()
        self.state = State.Ending

    """ UTILITIES """
    @Service.thread
    def status(self):
        while True:
            self.publish(ROBOT + '_ai_status', status=str(self.state))
            sleep(self.refresh)


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

def main():
    ai = Ai()
    ai.run()

if __name__ == '__main__':
    main()
