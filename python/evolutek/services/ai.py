#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from evolutek.lib.ai_interface import AIInterface

from evolutek.lib.fsm import Fsm
from evolutek.lib.goals import Goals, AvoidStrategy
from evolutek.lib.gpio import Edge, Gpio
from evolutek.lib.robot import Robot, Status
from evolutek.lib.settings import ROBOT

ROBOT = "pal"

from enum import Enum
from threading import Event, Thread, Timer
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

        super().__init__(ROBOT)

        # Robot handlers
        self.cs = CellaservProxy()
        self.actuators = self.cs.actuators[ROBOT]
        self.robot = Robot.get_instance(robot=ROBOT)

        # Runtime variables
        self.score = 0
        self.current_goal = None
        self.use_pathfinding = True
        self.critical_timer = None
        self.reset = Event()
        self.recalibration = Event()
        self.match_start = Event()
        self.match_end = Event()
        self.critical = Event()

        self.fsm = Fsm(States)
        self.fsm.add_state(States.Setup, self.setup, prevs=[States.Waiting, States.Ending])
        self.fsm.add_state(States.Waiting, self.waiting, prevs=[States.Setup])
        self.fsm.add_state(States.Selecting, self.selecting, prevs=[States.Waiting, States.Making])
        self.fsm.add_state(States.Making, self.making, prevs=[States.Selecting, States.Making])
        self.fsm.add_state(States.Ending, self.ending, prevs=[States.Setup, States.Waiting, States.Selecting, States.Making])
        self.fsm.add_error_state(self.error)

        #Gpio(17, "tirette", False, edge=Edge.FALLING).auto_refresh(callback=self.publish)

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

        # Recalibration wanted
        if self.recalibration.is_set():
            print('[AI] Recalibrating robot')
            self.recalibration.clear()
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

        self.match_end.clear()

        return States.Waiting


    """ WAITING """
    def waiting(self):
        while not self.reset.is_set() and not self.match_start.is_set():
            sleep(0.01)

        next = States.Selecting if self.match_start.is_set() else States.Setup
        self.reset.clear()
        self.match_start.clear()

        self.robot.tm.enable_avoid()
        if next == States.Selecting and self.critical_timer is not None:
            self.critical_timer.start()

        return next


    """ SELECTING """
    def selecting(self):
        if self.match_end.is_set():
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

        if self.match_end.is_set():
            return States.Ending

        if self.critical.is_set():
            return States.Selecting

        goal_score = self.current_goal.score

        status = None
        pos = self.robot.mirror_pos(x=self.current_goal.position.x, y=self.current_goal.position.y)
        print("[AI] Going %d %d" % (pos[0], pos[1]))

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


        if self.match_end.is_set():
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
                self.publish("score", value=action.score)
                self.score += action.score
                goal_score -= action.score

        if not avoid:
            self.robot.tm.enable_avoid()

        self.goals.finish_goal()
        if self.current_goal.score > 0:
            self.publish("score", value=goal_score)
            self.score += goal_score

        return States.Selecting


    """ ENDING """
    def ending(self):

        print("[AI] Match finished with score %d" % self.score)

        self.match_end_handler()

        self.reset.wait()
        self.reset.clear()

        return States.Setup


    """ ERROR """
    def error(self):
        print('[AI] AI in error')

        self.match_end_handler()

        self.robot.tm.error_mdb()

        while True:
            pass


    """ HANDLERS """
    @Service.event("match_start")
    @Service.action("match_start")
    def match_start_handler(self):
        self.match_start.set()

    @Service.event("match_end")
    @Service.action("stop_robot")
    def match_end_handler(self):
        if self.critical_timer is not None:
            self.critical_timer.stop()

        self.match_end.set()
        self.robot.tm.free()
        self.robot.tm.disable()
        self.actuators.free()
        self.actuators.disable()

        self.robot.tm.disable_avoid()
        self.robot.tm.set_mdb_config(mode=2)

        self.critical.clear()
        self.match_start.clear()
        self.recalibration.clear()
        self.reset.clear()

    @Service.action("set_critical_timeout")
    def critical_timeout_handler(self):
        self.critical_timer.stop()
        self.critical.set()


    """ OTHERS ACTIONS """
    @Service.action
    def set_strategy(self, index):
        status = self.goals.reset(int(index))
        if status:
            self.use_pathfinding = self.goals.current_strategy.use_pathfinding
        return status

    @Service.action
    def set_recalibration(self, need_recal=True):
        if need_recal:
            self.recalibration.set()
        else:
            self.recalibration.clear()

    @Service.action("reset")
    def reset_handler(self):
        self.reset.set()

    @Service.action
    def set_pathfinding(self, use_pathfinding=True):
        self.use_pathfinding = use_pathfinding

    @Service.action
    def sleep_ai(self, time):
        print('[AI] I am sleeping')
        sleep(float(time))

    @Service.action
    def get_strategy(self):
        new_list = []

        for i in self.goals.strategies:
            new_list.append(i.name)

        return new_list

    @Service.thread
    def infos_interfaces(self):
        while True:
            self.publish(self.robot.robot + "_infos_interfaces", states_ai=self.fsm.running.state.name,
                         bau_status=self.robot.tm.get_bau_status())
            sleep(1)

def main():
    ai = Ai()
    ai.run()

if __name__ == "__main__":
    main()
