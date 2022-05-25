#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Event as CellaservEvent, Service

from evolutek.lib.ai.fsm import Fsm
from evolutek.lib.ai.goals import Goals, AvoidStrategy
from evolutek.lib.gpio.gpio import Edge
from evolutek.lib.gpio.gpio_factory import GpioType, create_gpio
from evolutek.lib.indicators.lightning_mode import LightningMode
from evolutek.lib.map.point import Point
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.utils.wrappers import event_waiter
from evolutek.utils.interfaces.ai_interface import AIInterface

from enum import Enum
from math import pi
from threading import Event, Lock, Thread, Timer
from time import sleep, time

DELTA_POS = 5

class States(Enum):
    Setup = "Setup"
    Waiting = "Waiting"
    Selecting = "Selecting"
    Making = "Making"
    Ending = "Ending"
    Error = "Error"

@Service.require('config')
@Service.require('actuators', ROBOT)
@Service.require('trajman', ROBOT)
@Service.require('robot', ROBOT)
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
        self.recalibration = event_waiter(self.robot.recalibration, self.start_event, self.stop_event, callback=self.check_abort)

        self.red_led = create_gpio(23, 'red led', dir=True, type=GpioType.RPI)
        self.green_led = create_gpio(24, 'green led', dir=True, type=GpioType.RPI)

        self.tirette = create_gpio(17, 'tirette', dir=False, edge=Edge.FALLING, type=GpioType.RPI)
        self.tirette.auto_refresh(refresh=0.05, callback=self.publish)

        self.fsm = Fsm(States)
        self.fsm.add_state(States.Setup, self.setup, prevs=[States.Waiting, States.Ending])
        self.fsm.add_state(States.Waiting, self.waiting, prevs=[States.Setup, States.Waiting])
        self.fsm.add_state(States.Selecting, self.selecting, prevs=[States.Waiting, States.Making])
        self.fsm.add_state(States.Making, self.making, prevs=[States.Selecting, States.Making])
        self.fsm.add_state(States.Ending, self.ending, prevs=[States.Setup, States.Waiting, States.Selecting, States.Making])
        self.fsm.add_error_state(self.error)

        self.color1 = self.cs.config.get('match', 'color1')
        self.color = self.color1
        self.bau_state = False

        self.lock = Lock()
        self.score = 0
        self.match_starting_time = 0
        self.current_goal = None
        self.use_pathfinding = True
        self.recalibrate_itself = Event()
        self.reset_event = Event()
        self.match_start = Event()
        self.match_end = Event()

        self.critical_timer = None
        self.critical_timeout = Event()

        self.goals = Goals(file='/etc/conf.d/strategies.json', ai=self, robot=ROBOT)
        if not self.goals.parsed:
            print('[AI] Failed to parsed goals')
            Thread(target=self.fsm.run_error).start()

        else:
            print('[AI] Ready with loaded goals :')
            print(self.goals)

            self.red_led.write(True)
            self.green_led.write(False)

            self.use_pathfinding = self.goals.current_strategy.use_pathfinding

            try:
                self.color_callback(self.cs.match.get_color())
            except Exception as e:
                print('[AI] Failed to set color: %s' % str(e))

            try:
                self.handle_bau(self.cs.actuators[ROBOT].bau_read())
            except Exception as e:
                print('[AI] Failed to get BAU status: %s' % str(e))
            Thread(target=self.fsm.start_fsm, args=[States.Setup]).start()

    @Service.event("match_color")
    def color_callback(self, color):
        with self.lock:
            self.color = color

    @Service.event('%s-bau' % ROBOT)
    def handle_bau(self, value, **kwargs):

        new_state = get_boolean(value)
        # If the state didn't change, return

        with self.lock:
            if new_state == self.bau_state:
                return

            self.bau_state = new_state

    @Service.action
    def sleep(self, time):
        print('[AI] AI sleeping for %f s' % float(time))
        sleep(float(time))
        return RobotStatus.return_status(RobotStatus.Done)

    def check_abort(self):
        if self.match_end.is_set() or self.critical_timeout.is_set():
            print('[AI] Aborting')
            self.robot.abort_action()
            return RobotStatus.Aborted
        return RobotStatus.Ok

    @Service.event('match_start')
    def match_start_handler(self):
        self.match_start.set()

    @Service.event('match_end')
    def match_end_handler(self):

        self.robot.abort_action()
        self.match_end.set()

        with self.lock:
            if self.critical_timer is not None:
                self.critical_timer.cancel()
        self.critical_timeout.clear()


    @Service.action
    def reset(self, recalibrate_itself=False):
        recalibrate_itself = get_boolean(recalibrate_itself)

        if recalibrate_itself:
            self.recalibrate_itself.set()
        self.reset_event.set()

    @Service.action
    def get_strategies(self):
        with self.lock:
            return self.goals.get_strategies()

    @Service.action
    def set_strategy(self, index=0, name=None):
        if name is not None:
            strategies = self.get_strategies()

            if not name in strategies:
                print('[AI] Bad strategy name')
                return

            with self.lock:
                self.goals.reset(strategies[name])

        else:
            with self.lock:
                self.goals.reset(int(index))

        with self.lock:
            self.use_pathfinding = self.goals.current_strategy.use_pathfinding
            print('[AI] Current strategy:')
            print(self.goals.current_strategy)

    """ SETUP """
    def setup(self):

        self.red_led.write(True)
        self.green_led.write(False)

        with self.lock:
            self.score = 0
            self.current_goal = None

        with self.lock:
            self.goals.reset()

        self.match_end.clear()

        self.trajman.enable()
        self.actuators.enable()
        self.robot.reset()

        if self.recalibrate_itself.is_set():
            print('[AI] Recalibrating robot')
            self.actuators.rgb_led_strip_set_mode(LightningMode.Running.value)
            self.recalibrate_itself.clear()

            self.robot.set_theta(pi/2)
            self.recalibration(x=False, y=True, x_sensor='left', init=True)
            with self.lock:
                self.goto(x=self.goals.starting_position.x, y=self.goals.starting_position.y, avoid=False, async_task=False)
                self.goth(theta=self.goals.starting_theta, async_task=False)
        else:
            print('[AI] Setting robot position')
            self.trajman.free()
            with self.lock:
                self.robot.set_pos(
                    x=self.goals.starting_position.x,
                    y=self.goals.starting_position.y,
                    theta=self.goals.starting_theta
                )
            self.trajman.unfree()

        if ROBOT == 'pal':
            self.robot.pumps_get(ids='4', async_task=False)
            self.robot.set_elevator_config(arm=2, config=2, async_task=False)

        self.reset_event.clear()
        self.actuators.rgb_led_strip_set_mode(LightningMode.Loading.value)

        return States.Waiting


    """ WAITING """
    def waiting(self):

        self.red_led.write(False)
        self.green_led.write(True)

        while not self.reset_event.is_set() and not self.match_start.is_set():
            sleep(0.01)

        if self.reset_event.is_set() and self.tirette.read():
            print('[AI] Tirette on the robot')
            self.reset_event.clear()
            return States.Waiting

        next = States.Setup
        if self.match_start.is_set():
            next = States.Selecting
            self.match_start.clear()

            with self.lock:
                self.match_starting_time = time()
                print('[AI] Starting match')

                if self.goals.critical_goal is not None:
                    self.critical_timer = Timer(self.goals.timeout_critical_goal, lambda: self.critical_timeout.set())
                    self.critical_timer.start()

        self.red_led.write(True)
        self.green_led.write(False)

        return next


    """ SELECTING """
    def selecting(self):
        # TODO :
        # - select secondary

        if self.match_end.is_set():
            return States.Ending

        if self.critical_timeout.is_set():
            print('[AI] Switching on critical goal')

            with self.lock:
                self.current_goal = self.goals.get_critical_goal()
            self.critical_timeout.clear()
        else:
            print('[AI] Selecting Goal')

            with self.lock:
                self.current_goal = self.goals.get_goal()

                if self.current_goal is None:
                    return States.Ending

                if self.current_goal.name == self.goals.critical_goal:
                    print('[AI] Critical selected, stopping timer')
                    self.critical_timer.cancel()
                    self.critical_timeout.clear()

        return States.Making


    """ MAKING """
    def making(self):

        if self.check_abort() != RobotStatus.Ok:
            return States.Selecting

        self.actuators.rgb_led_strip_set_mode(LightningMode.Running.value)

        match_starting_time = 0
        goal_starting_time = time()
        current_goal = None
        with self.lock:
            match_starting_time = self.match_starting_time
            current_goal = self.current_goal

        print('[AI] Starting goal at %fs' % round(goal_starting_time - match_starting_time, 2))
        print(current_goal)

        use_pathfinding = False
        destination = current_goal.position
        with self.lock:
            use_pathfinding = self.use_pathfinding

            if self.color != self.color1:
                destination = Point(destination.x, 3000 - destination.y)

        if Point(dict=self.trajman.get_position()).dist(destination) <= DELTA_POS:
            print('[AI] Already on goal position')

        else:
            if use_pathfinding:

                print('[AI] Going with pathfinding')
                status = RobotStatus.NotReached
                has_moved = True
                timer = None
                timeout = Event()

                while status != RobotStatus.Reached:

                    if timeout.is_set():
                        print('[AI] Timeout during pathfinding')

                        with self.lock:
                            self.current_goal = self.goals.get_secondary_goal(current_goal.secondary_goal)

                        print('[AI] Selecting secondary goal')
                        return States.Making

                    data = self.goto_with_path(x=current_goal.position.x, y=current_goal.position.y)
                    status = RobotStatus.get_status(data)

                    if status == RobotStatus.Unreachable:

                        _has_moved = get_boolean(data['has_moved'])
                        if current_goal.timeout is not None and has_moved != _has_moved:
                            if _has_moved:
                                print('[AI] Stopping timer')
                                timer.cancel()
                                timer = None
                            else:
                                print('[AI] Starting timer')
                                timer = Timer(current_goal.timeout, lambda: timeout.set())
                                timer.start()
                            has_moved = _has_moved

                        sleep(1)
                        continue

                    if status == RobotStatus.Aborted:
                        if timer is not None:
                            print('[AI] Stopping timer')
                            timer.cancel()
                        return States.Selecting

                    if status != RobotStatus.Reached:
                        if timer is not None:
                            print('[AI] Stopping timer')
                            timer.cancel()
                        return States.Error

                if timer is not None:
                    print('[AI] Stopping timer')
                    timer.cancel()

            else:

                print('[AI] Going without pathfinding')

                status = RobotStatus.get_status(self.goto(x=current_goal.position.x, y=current_goal.position.y, timeout=current_goal.timeout))

                if status == RobotStatus.Timeout:
                    print('[AI] Timeout, selecting secondary goal')

                    with self.lock:
                        self.current_goal = self.goals.get_secondary_goal(current_goal.secondary_goal)

                    return States.Making

                if status == RobotStatus.Aborted:
                    return States.Selecting

                if status != RobotStatus.Reached:
                    return States.Error

            with self.lock:
                print('[AI] Reach goal position in %fs' % round(time() - goal_starting_time, 2))

        if not current_goal.theta is None:

            status = RobotStatus.get_status(self.goth(theta=current_goal.theta))

            if status == RobotStatus.Aborted:
                return States.Selecting

            if status != RobotStatus.Reached:
                return States.Error

        for action in current_goal.actions:

            action_starting_time = time()
            print('[AI] Making action at %fs' % round(action_starting_time - match_starting_time, 2))
            print(action)

            data = action.make()
            status = RobotStatus.get_status(data)

            score = None
            if action.score > 0 and 'score' in data:
                score = int(data['score'])
                self.publish("score", value=score)

                current_goal.score -= score

                with self.lock:
                    self.score += score

            print(status)

            if status == RobotStatus.Aborted:
                return States.Selecting

            if status == RobotStatus.Timeout and action.avoid_strategy == AvoidStrategy.Timeout:
                continue

            if status == RobotStatus.NotReached and action.avoid_strategy == AvoidStrategy.Skip:
                continue

            if status != RobotStatus.Done and status != RobotStatus.Reached:
                return States.Error

            print('[AI] Finished action in %fs' % round(time() - action_starting_time, 2))

            if action.score > 0 and score is None:
                self.publish("score", value=action.score)
                current_goal.score -= action.score

                with self.lock:
                    self.score += action.score

        with self.lock:
            self.goals.finish_goal()
            print('[AI] Finished goal in %fs' % round(time() - goal_starting_time, 2))

        #if current_goal.score > 0:
        #    self.publish("score", value=current_goal.score)

        #    with self.lock:
        #        self.score += current_goal.score

        self.actuators.rgb_led_strip_set_mode(LightningMode.Loading.value)

        return States.Selecting


    """ ENDING """
    def ending(self):

        self.red_led.write(False)
        self.green_led.write(True)

        with self.lock:
            print("[AI] Match finished with score %d in %fs" % (self.score, round(time() - self.match_starting_time, 2)))

        self.actuators.rgb_led_strip_set_mode(LightningMode.Loading.value)

        self.match_end.wait()

        self.robot.disable()
        self.actuators.disable()
        self.trajman.disable()

        self.actuators.rgb_led_strip_set_mode(LightningMode.Disabled.value)
        self.reset_event.wait()

        return States.Setup


    """ ERROR """
    def error(self):

        self.red_led.write(True)
        self.green_led.write(False)

        with self.lock:
            print('[AI] AI in error at %fs' % round(time() - self.match_starting_time, 2))

        self.actuators.rgb_led_strip_set_mode(LightningMode.Error.value)

        self.robot.disable()
        self.actuators.disable()
        self.trajman.disable()

        self.actuators.rgb_led_strip_set_mode(LightningMode.Disabled.value)

        self.reset_event.wait()

        return States.Setup

def main():
    ai = AI()
    ai.run()

if __name__ == '__main__':
    main()
