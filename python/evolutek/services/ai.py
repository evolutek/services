#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from evolutek.lib.goals import Goals
from evolutek.lib.point import Point
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

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
    Aborting = 6
    Error = 42

##TODO: Check errors and set to Error State
@Service.require('avoid', ROBOT)
@Service.require('trajman', ROBOT)
@Service.require('actuators', ROBOT)
class Ai(Service):

    """ STATES """

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
        self.timeout_event = Event()

        # Match config
        #self.goals = Goals(file="simple_strategy.json", mirror=self.color!=self.color1, cs=self.cs)
        self.goals = Goals(file="test_ai.json", mirror=self.color!=self.color1, cs=self.cs)
        self.current_path = []

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

        # Make a recalibration
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
        else:
            # Set Default config
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

        self.state = State.Waiting
        print('[AI] Waiting')

    """ SELECTING """
    def selecting(self):
        if self.state != State.Waiting and self.state != State.Making:
            return

        # WAIT FOR END OF DETECTION """
        if self.ending.isSet():
            return

        # Clear abort event
        self.aborting.clear()

        print('[AI] Selecting')
        self.state = State.Selecting

        self.goal = self.goals.get_goal()

        if self.goal is None:
            self.end()

        self.making()

    """ MAKING """
    def making(self):

        if self.state != State.Selecting:
            return

        if self.ending.isSet():
            return

        print('[AI] Making')
        self.state = State.Making

        if self.avoid_disable:
            self.avoid_disable = False
            self.cs.avoid[ROBOT].enable()

        #Goto x y with path
        self.current_path = self.goal.path
        self.goto_xy_theta_with_path(self.current_path)

        #Make all actions
        self.make_actions()

        print("[AI] Finished goal")
        self.goals.finish_goal()

        if self.goal.score > 0:
            self.publish('score', value=self.goal.score) # Increment score variable in match
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


    """ UTILITIES """

    """ Publish AI status """
    #@Service.thread
    def status(self):
        while True:
            self.publish(ROBOT + '_ai_status', status=str(self.state))
            sleep(self.refresh)


    """ Match Start """
    @Service.event('match_start')
    @Service.action
    def start(self):
        if self.state != State.Waiting:
            return

        print('[AI] Starting')
        self.match_thread.start()
        return

    """ Abort """
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

    """ Wait for end detection """
    def wait_until_detection_end(self, timeout=False):
        avoid_stat = self.cs.avoid[ROBOT].status()
        if self.side is not None and avoid_stat is not None:
            field = ''
            if self.side == 'front':
                field = 'front_detected'
            else:
                field = 'back_detected'
            state = self.state
            self.state = State.Aborting
            watchdog = None
            if timeout:
                watchdog = Watchdog(5, self.timeout_handler)
                watchdog.reset()
            while not self.ending.isSet() and not self.timeout_event.isSet()\
                and avoid_stat[field] is not None and len(avoid_stat[field]) > 0:
                avoid_stat = self.cs.avoid[ROBOT].status()
                print('-----Avoiding-----')
                sleep(0.1)
            if watchdog is not None:
                watchdog.stop()
            if not self.timeout_event.isSet():
                self.side = None
            self.state = state
        self.aborting.clear()
        self.timeout_event.clear()

    """ Going Back """
    def going_back(self, last_point, max_dist):
        print('-----Going back-----')
        tmp_pos = self.cs.trajman[ROBOT].get_position()
        dist = min(last_point.dist(tmp_pos), max_dist)
        self.cs.trajman[ROBOT].move_trsl(dist, 400, 400, 600, int(self.side!='front'))
        while not self.ending.isSet() and not self.aborting.isSet() and self.cs.trajman[ROBOT].is_moving():
            sleep(0.1)

    """ Goto xy """
    def goto_xy(self):
        p = self.goal.path[0]
        while p.dist(pos) > 5:
            self.cs.trajman[ROBOT].goto_xy(x = p.x, y = p.y)
            while not self.ending.isSet() and not self.aborting.isSet() and self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)

            if self.ending.isSet():
                return

            if self.aborting.isSet():
                print("[AI][MAKING] Aborted")
                self.wait_until_detection_end(timeout=True)

            if self.ending.isSet():
                return

            if self.side is not None:
                self.going_back(pos)
                self.side = None
                # we can be in avoiding state

            if self.ending.isSet():
                return

            pos = self.cs.trajman[ROBOT].get_position()

    @Service.action
    def get_path(self):
        return self.current_path

    """ Goto with path """
    def goto_xy_theta_with_path(self):
        dest = self.current_path[-1]
        break_out = False
        while len(self.current_path) > 0:
            point = self.current_path[i]
            print("[AI] Going to x : " + str(point['x') + ", y : " + str(point['y']))
            pos = self.cs.trajman[ROBOT].get_position()
            while Point.dist_dict(point, pos) > 5:
                self.cs.trajman[ROBOT].goto_xy(x = point['x'], y = point['y'])
                while not self.ending.isSet() and not self.aborting.isSet() and self.cs.trajman[ROBOT].is_moving():
                    sleep(0.1)

                if self.ending.isSet():
                    return

                if self.aborting.isSet():
                    print("[AI][MAKING] Aborted")
                    self.wait_until_detection_end(timeout=True)

                if self.ending.isSet():
                    return

                if self.side is not None:
                    self.going_back(self.goal.path[i - 1], 250)
                    print("[AI] Self.aborting = " + str(self.aborting.isSet()))
                    #Abort when going back
                    if self.aborting.isSet():
                        self.aborting.clear()
                        self.going_back(self.goal.path[i - 1], 50)
                        self.side = None

                    if self.aborting.isSet():
                        self.aborting.clear()
                        self.side = None

                    pos = self.cs.trajman[ROBOT].get_position()
                    #Compute new path
                    try:
                        print("[AI] Computing new path")
                        tmp_path = self.cs.map.get_path(start_x=pos['x'], start_y=pos['y'], dest_x=dest['x'], dest_y=dest['y'])
                        self.current_path = tmp_path
                        #TODO : check if path is empty
                        point = tmp_path[0]
                        print("NEW PATH = " + str(tmp_path))
                        break_out = True
                        break
                    except Exception as e:
                        print("[AI] Cannot compute new path: " + str(e))

                else:
                    print("[AI] Continuing current path")

                if self.ending.isSet():
                    return

                pos = self.cs.trajman[ROBOT].get_position()

            if break_out:
                break

    """ Make actions """
    def make_actions(self):
        print("[AI] Making actions")
        i = 0
        while i < len(self.goal.actions):

            if self.ending.isSet():
                return

            action = self.goal.actions[i]

            # Set parameters
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

            # TODO: check if we are asking trajman to move
            # Make action
            action.make()
            while not self.ending.isSet() and not self.aborting.isSet() and self.cs.trajman[ROBOT].is_moving():
                sleep(0.1)

            if self.ending.isSet():
                return

            # TODO: Manage avoid strategy

            if self.aborting.isSet():
                print("[AI][MAKING] Aborted")
                self.wait_until_detection_end()
                continue

            if self.ending.isSet():
                return

            if action.score > 0:
                self.publish('score', value=self.action.score)
                self.goal.score -= action.score

            # Make things back
            if action.trsl_speed is not None:
                self.cs.trajman[ROBOT].set_trsl_max_speed(self.max_trsl_speed)
            if action.rot_speed is not None:
                self.cs.trajman[ROBOT].set_rot_max_speed(self.max_rot_speed)

            i += 1

    """ Timeout handler """
    def timeout_handler(self):
        self.timeout_event.set()

def main():
    ai = Ai()
    ai.run()

if __name__ == '__main__':
    main()
