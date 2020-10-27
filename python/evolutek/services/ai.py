#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy

from evolutek.lib.fsm import Fsm
from evolutek.lib.goals import Goals, AvoidStrategy
from evolutek.lib.gpio import Edge, Gpio
from evolutek.lib.map.point import Point
from evolutek.lib.robot import Robot, Status, DELTA_POS
from evolutek.lib.settings import ROBOT

from enum import Enum
import json
from threading import Event, Thread, Timer
from time import sleep
from math import pi
import sys

class States(Enum):
    Setup = "Setup"
    Waiting = "Waiting"
    Selecting = "Selecting"
    Making = "Making"
    Ending = "Ending"
    Error = "Error"

if len(sys.argv) < 2 or sys.argv[1].lower() not in ['pal', 'pmi']:
    print("Usage: python3 ai.py <robot>")
    print("Robot can be pmi or pal")
    exit()
ROBOT=sys.argv[1].lower()

class Ai():

    def __init__(self):
        print('[AI] Init')

        # Robot handlers
        self.cs = CellaservProxy()
        self.actuators = self.cs.actuators[ROBOT]
        self.robot = Robot(robot=ROBOT, match_end_cb=self.match_end_handler)

        # Runtime variables
        self.score = 0
        self.current_goal = None
        self.use_pathfinding = True
        self.critical_timer = None
        self.critical = Event()

        self.fsm = Fsm(States)
        self.fsm.add_state(States.Setup, self.setup, prevs=[States.Waiting, States.Ending])
        self.fsm.add_state(States.Waiting, self.waiting, prevs=[States.Setup])
        self.fsm.add_state(States.Selecting, self.selecting, prevs=[States.Waiting, States.Making])
        self.fsm.add_state(States.Making, self.making, prevs=[States.Selecting, States.Making])
        self.fsm.add_state(States.Ending, self.ending, prevs=[States.Setup, States.Waiting, States.Selecting, States.Making])
        self.fsm.add_error_state(self.error)

        Gpio(17, "tirette", False, edge=Edge.FALLING).auto_refresh(callback=self.handle_tirette)

        self.goals = Goals(file='/etc/conf.d/strategies.json', ai=self, robot=ROBOT)

        if not self.goals.parsed:
            print('[AI] Failed to parsed goals')
            Thread(target=self.fsm.run_error).start()
        else:
            print('[AI] Ready')
            print(self.goals)

            self.use_pathfinding = self.goals.current_strategy.use_pathfinding

            Thread(target=self.fsm.start_fsm, args=[States.Setup]).start()

    """ SETUP """
    def setup(self):

        # Reset Robot
        self.robot.tm.enable()
        self.robot.tm.error_mdb(False)
        self.robot.tm.disable_avoid()
        self.robot.tm.set_mdb_config(mode=2)
        self.actuators.reset()

        # Reset variables
        self.current_goal = None
        self.goals.reset()
        self.score = 0


        if self.goals.critical_goal is not None:
            self.critical_timer = Timer(self.goals.timeout_critical_goal, self.critical_timeout_handler)

        #if self.cs.match.change_strategy.is_set():
        #    self.cs.match.get_strategy(ROBOT)
        #    self.cs.match.change_strategy.is_set()
        # Recalibration wanted
        if self.robot._recalibration.is_set():
            print('[AI] Recalibrating robot')
            self.robot._recalibration.clear()
            self.robot.recalibration(init=True)
            self.robot.go_home(self.goals.starting_position, self.goals.starting_theta)

        # No recalibration wanted
        else:
            print('[AI] Setting robot position')
            self.robot.tm.free()
            self.robot.set_pos(
                self.goals.starting_position.x,
                self.goals.starting_position.y,
                self.goals.starting_theta)
            self.robot.tm.unfree()

        self.robot.match_end.clear()

        return States.Waiting


    """ WAITING """
    def waiting(self):
        while not self.robot.reset.is_set() and not self.robot.match_start.is_set():
            sleep(0.01)

        next = States.Selecting if self.robot.match_start.is_set() else States.Setup
        self.robot.reset.clear()
        self.robot.match_start.clear()

        self.robot.tm.enable_avoid()
        if next == States.Selecting and self.critical_timer is not None:
            self.critical_timer.start()

        return next


    """ SELECTING """
    def selecting(self):
        if self.robot.match_end.is_set():
            return States.Ending

        if self.critical.is_set():
            self.current_goal = self.goals.get_critical_goal()
            self.critical.clear()
        else:
            self.current_goal = self.goals.get_goal()
            if not self.goals.critical_goal is None and self.current_goal.name == self.goals.critical_goal:
                self.critical_timer.stop()

        if self.current_goal is None:
            return States.Ending

        return States.Making


    """ MAKING """
    def making(self):

        print("[AI] Making goal:\n%s" % str(self.current_goal))

        if self.robot.match_end.is_set():
            return States.Ending

        if self.critical.is_set():
            return States.Selecting

        goal_score = self.current_goal.score

        status = None
        pos = self.robot.mirror_pos(x=self.current_goal.position.x, y=self.current_goal.position.y)
        pos = {"x" : pos[0], "y": pos[1]}

        current_pos = self.robot.tm.get_position()

        if Point.dist_dict(pos, current_pos) < DELTA_POS:
            print('[AI] Already on goal pos')

        else:

            print("[AI] Going %d %d" % (pos['x'], pos['y']))

            if self.use_pathfinding:
                print('[AI] Going with pathfinding')
                status = self.robot.goto_with_path(self.current_goal.position.x, self.current_goal.position.y)

                while status != Status.reached:

                    t = 0.0

                    if (self.current_goal.timeout is not None  and t > self.current_goal.timeout)\
                        or self.current_goal.secondary_goal is not None:

                        self.current_goal = self.goals.get_secondary(self.current_goal.secondary_goal)
                        return Status.Making

                    t += 100
                    sleep(0.1)

                    status = self.robot.goto_with_path(self.current_goal.position.x, self.current_goal.position.y)


            else:
                print('[AI] Going without pathfinding')

                status = self.robot.goto_avoid(self.current_goal.position.x, self.current_goal.position.y)
                # TODO : timeout ?
                # TODO : move_back

        if not self.current_goal.theta is None:

            print('[AI] Going to %s' % self.robot.mirror_pos(theta=self.current_goal.theta)[2])
            status = self.robot.goth(self.current_goal.theta)


            if status == Status.unreached:
                status = self.robot.goth(self.current_goal.theta)

                if status != Status.reached:
                    return States.error


        if self.robot.match_end.is_set():
            return States.Ending

        if self.critical.is_set():
            return States.Selecting

        avoid = True

        for action in self.current_goal.actions:

            if avoid and not action.avoid:
                self.robot.tm.disable_avoid()
                avoid = False

            if not avoid and action.avoid:
                self.robot.tm.enable_avoid()
                avoid = True

            print("[AI] Making action:\n%s" % str(action))

            status = None
            action.make()

            if action.score > 0:
                self.robot.client.publish("score", data=json.dumps({"value" : action.score}).encode())
                self.score += action.score
                goal_score -= action.score

        if not avoid:
            self.robot.tm.enable_avoid()

        self.goals.finish_goal()
        if self.current_goal.score > 0:
            self.robot.client.publish("score", data=json.dumps({"value" : goal_score}).encode())
            self.score += goal_score

        return States.Selecting


    """ ENDING """
    def ending(self):

        print("[AI] Match finished with score %d" % self.score)

        self.match_end_handler()

        self.robot.reset.wait()
        self.robot.reset.clear()

        return States.Setup


    """ ERROR """
    def error(self):
        print('[AI] AI in error')

        self.match_end_handler()

        self.robot.tm.error_mdb()

        while True:
            pass


    """ HANDLERS """
    def match_end_handler(self):
        if self.critical_timer is not None:
            self.critical_timer.stop()

        self.robot.match_end.set()
        self.robot.tm.free()
        self.robot.tm.disable()
        #self.actuators.free()
        #self.actuators.disable()

        self.robot.tm.disable_avoid()
        self.robot.tm.set_mdb_config(mode=2)

        self.critical.clear()
        self.robot.match_start.clear()
        self.robot._recalibration.clear()
        self.robot.reset.clear()

    def critical_timeout_handler(self):
        self.critical_timer.stop()
        self.critical.set()


    """ OTHERS ACTIONS """
    def set_strategy(self, index):
        status = self.goals.reset(int(index))
        if status:
            self.use_pathfinding = self.goals.current_strategy.use_pathfinding
        return status

    def sleep_ai(self, time):
        print('[AI] I am sleeping')
        sleep(float(time))


    def handle_tirette(self, **kwargs):
        del(kwargs['event'])
        data = json.dumps(kwargs).encode()
        self.robot.client.publish('tirette', data=data)

def main():
    ai = Ai()
    while True:
        pass

if __name__ == "__main__":
    main()
