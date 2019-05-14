#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from evolutek.lib.tasks import Tasks
from evolutek.lib.point import Point
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

from enum import Enum
from math import pi
from threading import Event, Thread
from time import sleep

class State(Enum):
    Init = 0
    Setup = 1
    Waiting = 2
    Making = 4
    Ending = 5
    Aborting = 6
    Error = 42

@Service.require('gpios', ROBOT)
@Service.require('ax', '11')
@Service.require('ax', '12')
@Service.require('trajman', ROBOT)
class Ai(Service):

    """ STATES """

    """ INIT """
    def __init__(self):

        self.state = State.Init
        print('Init')

        self.cs = CellaservProxy()

        self.telemetry = None

        # Config
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color = None
        try:
            self.color = self.cs.match.get_color()
        except Exception as e:
            print('Failed to set color: %s' % (str(e)))

        self.refresh = float(self.cs.config.get(section='ai', option='refresh'))

        # Parameters
        self.side = None
        self.avoiding = Event()
        self.ending = Event()

        self.tasks = Tasks(800, 50, pi/2, self.color!=self.color1)

        print('[AI] Initial Setup')
        super().__init__(ROBOT)
        self.setup(recalibration=False)

    """ SETUP """
    @Service.action
    def setup(self, recalibration=True):

        if self.state != State.Init and self.state != State.Waiting and self.state != State.Ending:
            return
        self.state = State.Setup

        if isinstance(recalibration, str):
            recalibration = recalibration == "true"

        print('[AI] Setup')

        self.cs.trajman[ROBOT].enable()
        self.open_arms()
        self.close_arms()

        self.match_thread = Thread(target=self.making)
        self.match_thread.deamon = True

        # Reset tasks
        self.tasks.reset(self.color!=selfcolor1)

        if recalibration:

            sens = self.color != self.color1
            self.cs.actuators[ROBOT].recalibrate(sens_y=sens, init=True)

            # TODO: Change goals
            self.cs.trajman[ROBOT].goto_xy(x=self.tasks.start_x, y=self.tasks.start_y)
            while self.cs.trajman[ROBOT].is_moving():
               sleep(0.1)
            self.cs.trajman[ROBOT].goto_theta(self.tasks.start_theta)
            while self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)
        else:
            # Set Default config
            self.cs.trajman[ROBOT].free()
            self.cs.trajman[ROBOT].set_x(self.tasks.start_x)
            self.cs.trajman[ROBOT].set_y(self.tasks.start_y)
            self.cs.trajman[ROBOT].set_theta(self.tasks.start_theta)
            self.cs.trajman[ROBOT].unfree()

        self.ending.clear()

        self.state = State.Waiting
        print('[AI] Waiting')

    """ MAKING """
    def making(self):

        # TODO: Add avoid

        if self.state != State.Waiting:
            return

        if self.ending.isSet():
            return

        print('[AI] Making')
        self.state = State.Making

        i = 0
        while i < len(self.tasks.tasks):
            pos = self.cs.trajman[ROBOT].get_position()
            if Point.dist_dict(pos, {'x': tasks.tasks[i].x, 'y': tasks.tasks[i].y}) <= 5:
                i += 1

            task = tasks.tasks[i]
            self.goto_xy(task.x, task.y)
            while not self.ending.isSet()  and not self.avoiding.isSet() and self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)

            if self.ending.isSet():
                return

            if self.avoiding.isSet():
                pass
                # TODO: wait

            if not task.theta is None:
                self.cs.trajman[ROBOT].goto_theta(task.theta)
                while not self.ending.isSet() and self.cs.trajman[ROBOT].is_moving():
                    sleep(0.1)

                if self.ending.isSet():
                    return

                if self.avoiding.isSet():
                    pass
                    # TODO: wait

            if not task.action is None:
                task.action_make()

                while self.cs.trajman[ROBOT].is_moving():
                    sleep(0.1)

                if self.ending.isSet():
                    return

                if self.avoiding.isSet():
                    pass
                    # TODO: wait

            if task.score > 0:
                self.publish('score', value=task.score)

        print("[AI] Maked all actions")

        self.end()


    """ END """
    @Service.event('match_end')
    @Service.action
    def end(self):
        print('[AI] Ending')
        self.ending.set()

        # STOP ROBOT[ROBOT]_
        self.cs.trajman[ROBOT].free()
        self.cs.trajman[ROBOT].disable()
        self.open_arms()
        self.cs.ax['11'].free()
        self.cs.ax['12'].free()


    """ UTILITIES """

    """ Publish AI status """
    @Service.thread
    def status(self):
        while True:
            self.publish(ROBOT + '_ai_status', status=str(self.state))
            sleep(self.refresh)

    @Service.thread
    def loop_avoid(self):
        while True:
            if self.telemetry is None:
                continue

            front = False
            back = False

            # TODO: Read GPIOS

            if self.telemetry['speed'] > 0 and front:
                self.stop_asap(1000, 20)
                side = 'front'
                self.avoiding.set()
            elif self.telemetry['speed'] < 0 and back:
                self.stop_asap(1000, 20)
                side = 'back'
                self.avoiding.set()

            sleep(0.1)

    """ Match Color """
    @Service.event('match_color')
    def color(self, color):
        if not color is None and color != self.color:
            self.color = color
            self.reset(recalibration=False)

    """ Reset button """
    @Service.event('%s_reset' % ROBOT)
    def reset_button(self, **kwargs):
        self.reset(recalibration=True)

    """ PMI Telemetry """
    @Service.event('%s_telemetry' % ROBOT)
    def telemetry(self, status, telemetry):
        if self.status == 'failed':
            self.telemetry = None
        else:
            self.telemetry = telemetry

    """ Match Start """
    @Service.event('match_start')
    @Service.action
    def start(self):
        if self.state != State.Waiting:
            return

        print('[AI] Starting')
        self.match_thread.start()
        return

    """ Open Arms """
    @Service.action
    def open_arms(self):
        self.cs.ax['11'].move(goal=662)
        sleep(0.5)
        self.cs.ax['12'].move(goal=462)
        sleep(0.5)

    """ Close Arms """
    @Service.action
    def close_arms(self):
        self.cs.ax['12'].move(goal=812)
        sleep(0.5)
        self.cs.ax['11'].move(goal=212)
        sleep(0.5)

def main():
    ai = Ai()
    ai.run()

if __name__ == '__main__':
    main()
