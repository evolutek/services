#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from evolutek.lib.goals import Goals
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

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
    Aborting = 6
    Error = 42

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

        # Simple AI
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

        # Timer
        self.timeout_watchdog = Watchdog(5, self.timeout_handler)
        self.timeout_event = Event()

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

        if not self.goals.reset(self.color!=self.color1):
            print('[AI] Error')
            self.state = State.Error
            return

        self.cs.trajman[ROBOT].enable()
        self.cs.actuators[ROBOT].reset(self.color)
        self.cs.avoid[ROBOT].disable()

        self.match_thread = Thread(target=self.selecting)
        self.match_thread.deamon = True

        """
        if recalibration:

            self.cs.avoid[ROBOT].disable()

            sens = self.color != self.color1
            self.cs.actuators[ROBOT].recalibrate(sens_y=sens, init=True)

            self.cs.trajman[ROBOT].goto_xy(x=self.goals.start_x, y=self.goals.start_y)
            while self.cs.trajman[ROBOT].is_moving():
               sleep(0.1)
            self.cs.trajman[ROBOT].goto_theta(self.goals.start_theta)
            while self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)
        else:"""

        """ Set Default config """
        self.cs.trajman[ROBOT].free()
        self.cs.trajman[ROBOT].set_x(self.goals.start_x)
        self.cs.trajman[ROBOT].set_y(self.goals.start_y)
        self.cs.trajman[ROBOT].set_theta(self.goals.start_theta)
        self.cs.trajman[ROBOT].unfree()

        self.cs.avoid[ROBOT].enable()
        self.avoid_disable = False

        self.aborting.clear()
        self.ending.clear()
        self.timeout_event.clear()
        self.timeout_watchdog = Watchdog(5, timeout_handler)

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

        if self.avoid_disable:
            self.avoid_disable = False
            self.cs.avoid[ROBOT].enable()

        """ Goto x y """
        pos = self.cs.trajman[ROBOT].get_position()
        while sqrt((pos['x'] - goal.x)**2 + (pos['y'] - goal.y)**2) > 5:
            self.cs.trajman[ROBOT].goto_xy(x = goal.x, y = goal.y)
            while not self.ending.isSet() and not self.aborting.isSet() and self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)

            if self.ending.isSet():
                return

            if self.aborting.isSet():
                print("[AI][MAKING] Aborted")
                self.state = State.Aborting
                self.timeout_watchdog.reset()
                self.wait_until_detection_end()
                self.timeout_watchdog.stop()
                self.timeout_watchdog = Watchdog(5, timeout_handler)

            if self.ending.isSet():
                return

            tmp_pos = pos = self.cs.trajman[ROBOT].get_position()
            if self.side is not None and sqrt((pos['x'] - tmp_pos['x'])**2 + (pos['y'] - tmp_pos['y'])**2) >= 50:
                self.cs.trajman[ROBOT].move_trsl(50, 100, 100, 500, self.side=='front')

            if self.ending.isSet():
                return

            self.state = State.Making
            pos = self.cs.trajman[ROBOT].get_position()

        """ Goto theta if there is one """
        if goal.theta is not None:

            while abs(pos['theta'] - goal.theta) > 0.5:
                self.cs.trajman[ROBOT].goto_theta(goal.theta)
                while not self.ending.isSet() and not self.aborting.isSet() and self.cs.trajman[ROBOT].is_moving():
                    sleep(0.1)

                if self.ending.isSet():
                    return

                if self.aborting.isSet():
                    print("[AI][MAKING] Aborted")
                    self.state = State.Aborting
                    self.timeout_watchdog.reset()
                    self.wait_until_detection_end()
                    self.timeout_watchdog.stop()
                    self.timeout_watchdog = Watchdog(5, timeout_handler)

                if self.ending.isSet():
                    return

                self.state = State.Making
                pos = self.cs.trajman[ROBOT].get_position()

        """ Make all actions """
        i = 0
        while i < len(goal.actions):

            if self.ending.isSet():
                return

            action = goal.actions[i]

            """ Set parameters """
            if action.trsl_speed is not None:
                self.cs.trajman[ROBOT].set_trsl_max_speed(action.trsl_speed)
            if action.rot_speed is not None:
                self.cs.trajman[ROBOT].set_rot_max_speed(action.rot_speed)

            if not action.avoid and not self.avoid_disable:
                self.avoid_disable = True
                self.cs.avoid[ROBOT].disable()
            elif action.avoid and self.avoid_disable:
                self.avoid_disable = False
                self.cs.avoid[ROBOT].enable()

            """ Make action """
            action.make()
            while not self.ending.isSet() and not self.aborting.isSet() and self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)

            if self.ending.isSet():
                return

            if self.aborting.isSet():
                print("[AI][MAKING] Aborted")
                self.state = State.Aborting
                self.timeout_watchdog.reset()
                self.wait_until_detection_end()
                self.timeout_watchdog.stop()
                self.timeout_watchdog = Watchdog(5, timeout_handler)
                self.state = State.Making
                continue

            if self.ending.isSet():
                return

            """ Make things back """
            if action.trsl_speed is not None:
                self.cs.trajman[ROBOT].set_trsl_max_speed(self.max_trsl_speed)
            if action.rot_speed is not None:
                self.cs.trajman[ROBOT].set_rot_max_speed(self.max_rot_speed)

            i += 1


        print("[AI] Finished goal")
        self.goals.finish_goal()

        self.publish('score', value=goal.score) # Increment score variable in match
        self.selecting()

    """ END """
    @Service.event('match_end')
    @Service.action
    def end(self):
        print('[AI] Ending')
        self.ending.set()

        # STOP ROBOT[ROBOT]_
        self.cs.trajman[ROBOT].free()
        self.cs.trajman[ROBOT].disable()
        self.cs.actuators[ROBOT].free()
        self.cs.actuators[ROBOT].disable()

        self.state = State.Ending

    """ UTILITIES """
    @Service.thread
    def status(self):
        while True:
            self.publish(ROBOT + '_ai_status', status=str(self.state))
            sleep(self.refresh)


    @Service.event('match_start')
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
        avoid_stat = self.cs.avoid[ROBOT].status()
        if self.side is not None and avoid_stat is not None:
            field = ''
            if self.side == 'front':
                field = 'front_detected'
            else:
                field = 'back_detected'
            while not self.ending.isSet() and not self.timeout_event.isSet()\
                and avoid_stat[field] is not None and len(avoid_stat[field]) > 0:
                avoid_stat = self.cs.avoid[ROBOT].status()
                print('-----avoiding-----')
                sleep(0.1)
            if not self.timeout_event.isSet():
                self.side = None
        self.aborting.clear()
        self.timeout_event.clear()

    """ Timeout handler """
    def timeout_handler(self):
        self.timeout_event.set()

def main():
    ai = Ai()
    ai.run()

if __name__ == '__main__':
    main()
