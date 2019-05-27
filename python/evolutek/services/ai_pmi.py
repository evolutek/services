#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from evolutek.lib.goals import Goals
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
@Service.require('actuators', ROBOT)
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
        self.avoid_enabled =  True
        self.front_detected = []
        self.back_detected = []

        #self.tasks = Tasks(800, 50, pi/2, self.color!=self.color1)

        print('[AI] Initial Setup')
        super().__init__(ROBOT)
        
        self.goals = Goals(file="homo_pmi.json", mirror=self.color!=self.color1, cs=self.cs)
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
        print('open')
        self.cs.actuators[ROBOT].half_close_arms()
        sleep(1)
        print('close')
        self.cs.actuators[ROBOT].close_arms()

        self.match_thread = Thread(target=self.making)
        self.match_thread.deamon = True

        # Reset tasks
        if not self.goals.reset(self.color!=self.color1):
            print('[AI] Error')
            self.state = State.Error
            return


        if recalibration:

            sens = self.color != self.color1
            self.cs.actuators[ROBOT].recalibrate(sens_y=sens, init=True)
            self.cs.trajman[ROBOT].goto_xy(x=self.goals.start_x, y=self.goals.start_y)
            while self.cs.trajman[ROBOT].is_moving():
               sleep(0.1)
            self.cs.trajman[ROBOT].goto_theta(self.goals.start_theta)
            while self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)
        else:
            # Set Default config
            self.cs.trajman[ROBOT].free()
            self.cs.trajman[ROBOT].set_x(self.goals.start_x)
            self.cs.trajman[ROBOT].set_y(self.goals.start_y)
            self.cs.trajman[ROBOT].set_theta(self.goals.start_theta)
            self.cs.trajman[ROBOT].unfree()

        self.ending.clear()
        self.avoiding.clear()
        self.avoid_enabled =  True
        self.side = None

        self.state = State.Waiting
        print('[AI] Waiting')


    """ MAKING """
    def making(self):

        if self.state != State.Waiting:
            return


        if self.ending.isSet():
            return

        print('[AI] Making')
        self.state = State.Making

        i = 0
        while i < len(self.goals.goals):
            print("i: %d" % i)
            goal = self.goals.goals[i]
            j = 0
            while j < len(goal.path):
                pos = self.cs.trajman[ROBOT].get_position()
                path = goal.path[j]
                if Point.dist_dict(pos, {'x': path['x'], 'y': path['y']}) <= 5:
                    j += 1
                    continue

                self.cs.trajman[ROBOT].goto_xy(path['x'], path['y'])
                while self.cs.trajman[ROBOT].is_moving():
                    sleep(0.1)

                if self.ending.isSet():
                    return

                sleep(0.5)
                if self.avoiding.isSet():
                    self.wait_until()

                if 'theta' in path:
                    self.cs.trajman[ROBOT].goto_theta(path['theta'])
                    while self.cs.trajman[ROBOT].is_moving():
                        sleep(0.1)

                    if self.ending.isSet():
                        return

                    sleep(0.5)
                    if self.avoiding.isSet():
                        self.wait_until()

            k = 0
            while k < len(goal.actions):
                try:
                    print("k: %d" % k)
                    if k - 1 > len(goal.actions):
                        break
                    print('[AI] ======= Making actions')
                    action = goal.actions[k]
                    action.make()
                    while not self.ending.isSet() and not self.avoiding.isSet() and self.cs.trajman[ROBOT].is_moving():
                        print('MAKING')
                        sleep(0.1)

                    sleep(0.5)
                    if self.ending.isSet():
                        return

                    if self.avoiding.isSet():
                        self.wait_until()
                        print('AI AVOIDED, NOT GOING TO NEXT ACTION')
                        continue

                    print('MADE')

                    if self.ending.isSet():
                        return
                except Exception as e:
                    print('AI : EXCEPTION: ' + e.message)
                
                k += 1
            if goal.score > 0:
                self.publish('score', value=goal.score)
            i += 1

        print("[AI] Made all goals")

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
        self.cs.actuators[ROBOT].open_arms()
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

            sleep(0.1)
            #print('[AI] AVOID STATUS')
            #print(self.front_detected)
            #print(self.back_detected)

            if self.telemetry is None or not self.avoid_enabled:
                continue

            if self.telemetry['speed'] > 0 and len(self.front_detected) > 0:
                self.avoiding.set()
                print('AVOID FROOOOONT')
                self.cs.trajman[ROBOT].stop_asap(500, 15)
                self.side = 'front'
                print('--- front ---')
                sleep(0.5)
            elif self.telemetry['speed'] < 0 and len(self.back_detected) > 0:
                self.avoiding.set()
                print('AVOID BAAAACCCCKKKK')
                self.cs.trajman[ROBOT].stop_asap(500, 15)
                self.side = 'back'
                print('--- back ---')
                sleep(0.5)

    def wait_until(self):
        print('WAIT UNTIL')
        side = []
        if self.side == 'front':
            side = self.front_detected
        elif self.side == 'back':
            side = self.back_detected

        while not self.ending.isSet() and len(side) > 0:
            print(side)
            print('----- Avoiding ---')
            sleep(0.1)

        self.avoiding.clear()
        self.side = None
        print('DONE AVOIDING')

    """ Match Color """
    @Service.event('match_color')
    def color(self, color):
        if not color is None and color != self.color:
            self.color = color
            self.reset(recalibration=False)

    """ Reset button """
    @Service.event('%s_reset' % ROBOT)
    def reset_button(self, **kwargs):
        self.setup(recalibration=False)

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

    """" Front sensor """
    @Service.event('%s_front' % ROBOT)
    def front_detection(self, name, id, value):
        if int(value) and not name in self.front_detected:
            self.front_detected.append(name)
        elif not int(value) and name in self.front_detected:
            self.front_detected.remove(name)

    """ Back sensor """
    @Service.event('%s_back' % ROBOT)
    def back_detection(self, name, id, value):
        if int(value) and not name in self.back_detected:
            self.back_detected.append(name)
        elif not int(value) and name in self.back_detected:
            self.back_detected.remove(name)

def main():
    ai = Ai()
    ai.run()

if __name__ == '__main__':
    main()
