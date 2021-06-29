#!/usr/bin/env python3

from evolutek.services.robot import Robot
from evolutek.lib.utils.wrappers import event_waiter
from evolutek.lib.status import RobotStatus
from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event as CellaservEvent, Service

from evolutek.lib.ai.fsm import Fsm
from evolutek.lib.ai.goals import Goals, AvoidStrategy
from evolutek.lib.gpio.gpio import Edge
from evolutek.lib.gpio.gpio_factory import GpioType, create_gpio
from evolutek.lib.indicators.lightning_mode import LightningMode
from evolutek.lib.settings import ROBOT
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.utils.wrappers import event_waiter

from enum import Enum
from threading import Event, Thread, Timer
from time import sleep

class States(Enum):
    Setup = "Setup"
    Waiting = "Waiting"
    Selecting = "Selecting"
    Making = "Making"
    Ending = "Ending"
    Error = "Error"

# TODO :
# - interface
# - secondary goal
# - critical goal
# - manage action avoid strategies
# - set strategy

@Service.require('config')
@Service.require('actuators')
@Service.require('trajman')
@Service.require('robot')
class AI(Service):

    start_event = CellaservEvent('%s_robot_started' % ROBOT)
    stop_event = CellaservEvent('%s_robot_stopped' % ROBOT)

    def __init__(self):

        super().__init__(ROBOT)

        print('[AI] Init')

        self.cs = CellaservProxy()
        self.actuators = self.cs.actuators[ROBOT]
        self.trajman = self.cs.trajman[ROBOT]
        self.robot = self.cs.robot[ROBOT]

        self.goth = event_waiter(self.robot.goth, self.start_event, self.stop_event, callback=self.check_abort)
        self.goto = event_waiter(self.robot.goto_avoid, self.start_event, self.stop_event, callback=self.check_abort)
        self.goto_with_path = event_waiter(self.robot.goto_with_path, self.start_event, self.stop_event, callback=self.check_abort)

        self.red_led = create_gpio(23, 'red led', dir=True, type=GpioType.RPI)
        self.green_led = create_gpio(24, 'green led', dir=True, type=GpioType.RPI)

        self.tirette = create_gpio(17, 'tirette', dir=False, edge=Edge.FALLING, type=GpioType.RPI)
        self.tirette.auto_refresh(refresh=0.05, callback=self.publish)

        self.fsm = Fsm(States)
        self.fsm.add_state(States.Setup, self.setup, prevs=[States.Waiting, States.Ending])
        self.fsm.add_state(States.Waiting, self.waiting, prevs=[States.Setup])
        self.fsm.add_state(States.Selecting, self.selecting, prevs=[States.Waiting, States.Making])
        self.fsm.add_state(States.Making, self.making, prevs=[States.Selecting, States.Making])
        self.fsm.add_state(States.Ending, self.ending, prevs=[States.Setup, States.Waiting, States.Selecting, States.Making])
        self.fsm.add_error_state(self.error)

        self.lock = Lock()
        self.score = 0
        self.match_starting_time = 0
        self.current_goal = None
        self.use_pathfinding = True
        self.recalibrate_itself = Event()
        self.reset = Event()
        self.match_start = Event()
        self.match_end = Event()

        self.goals = Goals(file='/etc/conf.d/strategies.json', ai=self, robot=ROBOT)

        if not self.goals.parsed:
            print('[AI] Failed to parsed goals')
            Thread(target=self.fsm.run_error).start()

        else:
            print('[AI] Ready')
            print(self.goals)

            self.use_pathfinding = self.goals.current_strategy.use_pathfinding

            Thread(target=self.fsm.start_fsm, args=[States.Setup]).start()

    @Service.action
    def sleep(self, time):
        print('[AI] AI sleeping for %f s' % float(time))
        sleep(float(time))
        RobotStatus.return_status(RobotStatus.Done)

    def check_abort(self):
        # TODO : critical
        if self.match_end.is_set():
            self.robot.abort_action()
            return RobotStatus.Aborted
        return RobotStatus.Ok

    @Service.event('match_start')
    def match_start_handler(self):
        self.match_start.set()

    @Service.event('match_end')
    def match_end_handler(self):
        # TODO :
        # - stop critital timer

        self.actuators.rgb_led_strip_set_mode(LightningMode.Disabled.value)

        self.match_end.set()
        self.robot.abort_action()
        self.robot.disable()
        self.actuators.disable()
        self.trajman.disable()

    @Service.action
    def reset(self, recalibrate_itself=False):
        recalibrate_itself = get_boolean(recalibrate_itself)

        if recalibrate_itself:
            self.recalibrate_itself.set()
        self.reset.set()

    """ SETUP """
    def setup(self):
        # TODO :
        # - go home

        self.score = 0
        self.current_goal = None
        self.goals.reset()
        self.match_end.clear()

        self.trajman.enable()
        self.actuators.enable()
        self.robot.reset()


        if self.recalibrate_itself.is_set():
            print('[AI] Recalibrating robot')
            self.actuators.rgb_led_strip_set_mode(LightningMode.Running.value)
            self.recalibrate_itself.clear()
            self.robot.recalibration(init=True, use_queue=False)
            # TODO : go home
        else:
            print('[AI] Setting robot position')
            self.trajman.free()
            self.robot.set_pos(
                x=self.goals.starting_position.x,
                y=self.goals.starting_position.y,
                theta=self.goals.starting_theta
            )
            self.trajman.unfree()

        self.actuators.rgb_led_strip_set_mode(LightningMode.Loading.value)

        return States.Waiting

    """ WAITING """
    def waiting(self):
        # TODO :
        # - launch timer for critical goal

        while not self.reset.is_set() and not self.match_start.is_set():
            sleep(0.01)

        next = States.Setup
        if self.match_start.is_set():
            next = States.Selecting
            self.match_starting_time = time()
            print('[AI] Starting match')

        self.reset.clear()
        self.match_start.clear()

        return next

    """ SELECTING """
    def selecting(self):
        # TODO :
        # - select next goal (critical, secondary)
        # - if critical, remove it

        if self.match_end.is_set():
            return States.Ending

        self.current_goal = self.goals.get_goal()

        if self.current_goal is None:
            return States.Ending

        return States.Making

    """ MAKING """
    def making(self):
        # TODO :
        # - manage action avoid strategies
        # - abort to secondary goal

        self.actuators.rgb_led_strip_set_mode(LightningMode.Running.value)

        match_starting_time = 0
        goal_starting_time = time()
        current_goal = None
        with self.lock:
            match_starting_time = self.match_starting_time
            current_goal = self.current_goal

        print('[AI] Starting goal at %fs' % round(goal_starting_time - match_starting_time, 2))
        print(current_goal)

        if self.use_pathfinding:

            print('[AI] Going with pathfinding')
            status = RobotStatus.NotReached
            while status != RobotStatus.Reached and self.check_abort() == RobotStatus.Ok:
                status = RobotStatus.get_status(self.goto_with_path(x=current_goal.position.x, y=current_goal.position.y))

                if status == RobotStatus.Unreachable:
                    sleep(1)
                    continue

                if status == RobotStatus.Aborted:
                    return States.Making

                if status != RobotStatus.Reached:
                    return States.Error

        else:

            print('[AI] Going without pathfinding')
            status = RobotStatus.get_status(self.goto(x=current_goal.position.x, y=current_goal.position.y))

            if status == RobotStatus.Aborted:
                return States.Making

            if status != RobotStatus.Reached:
                return States.Error

        with self.lock:
            print('[AI] Reach goal position in %fs' % round(time() - goal_starting_time, 2))

        if not self.current_goal.theta is None:

            status = RobotStatus.get_status(self.goth(theta=current_goal.theta))

            if status == RobotStatus.Aborted:
                return States.Making

            if status != RobotStatus.Reached:
                return States.Error

        for action in current_goal.actions:

            action_starting_time = time()
            print('[AI] Making action at %fs' % round(action_starting_time - match_starting_time, 2))
            print(action)

            data = action.make()
            status = RobotStatus.get_status(data)

            if status == RobotStatus.Aborted:
                return States.Selecting

            # TODO : timeout

            if status != RobotStatus.Done and status != RobotStatus.Reached:
                return States.Error

            print('[AI] Finished action in %fs' % round(time() - action_starting_time, 2))

            if action.score > 0:
                score = action.score

                if 'score' in data:
                    score = int(data['score'])

                self.publish("score", value=score)

                with self.lock:
                    self.score += score

                current_goal.score -= action.score

        self.goals.finish_goal()

        with self.lock:
            print('[AI] Finished goal in %fs' % round(time() - goal_starting_time, 2))

        if current_goal.score > 0:
            self.publish("score", value=elf.current_goal.score)

            with self.lock:
                self.score += goal_score

        self.actuators.rgb_led_strip_set_mode(LightningMode.Loading.value)

        return States.Selecting

    """ ENDING """
    def ending(self):
        # TODO :
        # - stop timer

        with self.lock:
            print("[AI] Match finished with score %d in %fs" % (self.score, round(time() - self.match_starting_time, 2)))
        #self.match_end_handler()

        self.actuators.rgb_led_strip_set_mode(LightningMode.Loading.value)

        self.reset.wait()

        return States.Setup

    """ ERROR """
    def error(self):
        with self.lock:
            print('[AI] AI in error at %fs' % round(time() - self.match_starting_time, 2))
        self.match_end_handler()

        self.actuators.rgb_led_strip_set_mode(LightningMode.Error.value)

        self.reset.wait()

        return States.Setup


def main():
    ai = AI()
    ai.run()

if __name__ == '__main__':
    main()
