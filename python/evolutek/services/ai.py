#!/usr/bin/env python3

from cellaserv.service import Service, Event
from cellaserv.proxy import CellaservProxy
from enum import Enum
from evolutek.lib.goals import Goals
from evolutek.lib.settings import ROBOT
from threading import Event, Thread
from time import sleep

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
#@Service.require('avoid', ROBOT)
#@Service.require('gpios', ROBOT)
@Service.require('match')
#@Service.require('map')
class Ai(Service):

    def __init__(self):

        self.state = State.Init
        print('Init')

        # Cellaserv
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman[ROBOT]
        self.actuators = self.cs.actuators[ROBOT]
        # self.recalibration_event = Event(set='recalibrated')

        # Config
        #self.color1 = self.cs.config.get(section='match', option='color1')
        #self.color2 = self.cs.config.get(section='match', option='color2')
        self.color = self.cs.match.get_match()['color']
        #self.color = self.color1  #remove
        self.refresh = float(self.cs.config.get(section='ai', option='refresh'))

        self.max_trsl_speed = self.cs.config.get(section=ROBOT, option='trsl_max')
        self.max_rot_speed = self.cs.config.get(section=ROBOT, option='rot_max')

        # Parameters
        self.aborting = Event()
        self.current_action = None
        self.tmp_robot = None
        self.debug_count = 0

        # Match config
        self.goals = Goals(color = self.color, file = "keke.json")

        print('[AI] Initial Setup')
        super().__init__(ROBOT)
        self.setup(recalibration=False)

    @Service.thread
    def status(self):
        while True:
            self.publish(ROBOT + '_ai_status', status=str(self.state))
            sleep(self.refresh)

    @Service.action
    def setup(self, color=None, recalibration=True):
        print(self.state)
        if self.state != State.Init and self.state != State.Waiting and self.state != State.Ending:
            return
        self.state = State.Setup
        if isinstance(recalibration, str):
            recalibration = recalibration == "true"

        print('[AI] Setup')
        self.trajman.enable()
        self.actuators.reset()

        self.match_thread = Thread(target=self.selecting)

        if color is not None:
            self.color = color

        if recalibration:
            sens = self.color == self.color2
            self.actuators.recalibrate(sens_y = sens, init=True)
            sleep(10)

            #self.recalibration_event.wait()
            #self.recalibration_event.clear()

            self.trajman.goto_xy(x=self.goals.start_x, y=self.goals.start_y)
            while self.trajman.is_moving():
                sleep(0.1)
            self.trajman.goto_theta(self.goals.theta)
            while self.trajman.is_moving():
                sleep(0.1)
        else:
            print("[AI][TRAJMAN] Free")
            self.trajman.free()
            print("[AI][TRAJMAN] Set x")
            self.trajman.set_x(self.goals.start_x)
            print("[AI][TRAJMAN] Set y")
            self.trajman.set_y(self.goals.start_y)
            print("[AI][TRAJMAN] Theta")
            self.trajman.set_theta(self.goals.theta)
            print("[AI][TRAJMAN] Unfree")
            self.trajman.unfree()

        #self.goals.reset()

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
        self.state = State.Ending
        self.trajman.free()
        self.trajman.disable()
        self.actuators.free()
        self.actuators.disable()

    @Service.action
    def abort(self, robot):
        if self.state != State.Making:
            return

        self.debug_count -= 1

        print('[AI] Aborting')
        self.aborting.set()

        if robot is not None:
            self.tmp_robot = robot

        # Give it to the map

    def selecting(self):
        if self.state != State.Waiting and self.state != State.Making:
            return

        print('[AI] Selecting')
        self.state = State.Selecting

        self.debug_count += 1

        print("[AI] Number of actions :%d" %self.debug_count)

        if self.debug_count > 10:
            self.end()

        current_action = None
        path = None

        # Select an action
        #optimum  = self.map.get_optimal_goal(self.goals.get_available_goals())
        #current_action = optimum[0]
        #path = optimum[1]

        #if current_action is None:
        #    self.end()

        #if path is None:
        #  self.state = State.Selecting

        self.making()

    def making(self, current_acion=None, path=None):

        # Need to rework
        if self.state != State.Selecting:
            return

        print('[AI] Making')
        self.state = state.Making

        if self.aborting.isSet():
            print("[AI][MAKING] Aborted")
            self.selecting()
            
        print("[AI][MAKING] Not aborted")
        self.selecting()
            

        """
        if self.current_action.trsl_speed is not None:
            self.trajman.set_trsl_max_speed(current_action.trsl_speed)

        for point in path:
            self.trajman.goto_xy(x=point.x, y=point.y)
            while self.trajman.is_moving():
                sleep(0.5) #Is this not too much?
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

        self.publish('score', self.current_action.score) # Increment score variable in match
        self.trajman.set_trsl_max_speed(self.max_trsl_speed)
        self.trajman.set_trsl_rot_speed(self.max_rot_speed)
        """
        self.selecting()

def main():
    ai = Ai()
    ai.run()

if __name__ == '__main__':
    main()
