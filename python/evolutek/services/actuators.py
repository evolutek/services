#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

from evolutek.lib.gpio import Gpio, Pwm
from evolutek.lib.actionqueue import Act_queue
from evolutek.lib.robot import Robot, Status
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

from enum import Enum
from functools import wraps
from threading import Event
from time import sleep
import os

DELAY_EV = 0.2

class Buoy(Enum):
    Empty = "empty"
    Green = "green"
    Red = "red"
    Unknow = "unknow"

class PumpActuator:

    def __init__(self, pump_gpio, ev_gpio, pump_nb):
        self.pump_gpio = Gpio(pump_gpio, "Pump-%d" % pump_nb, True)
        self.ev_gpio = Gpio(ev_gpio, "EV-%d" % pump_nb, True)

        self.pump_nb = pump_nb

        self.buoy = Buoy.Empty

    def pump_get(self, buoy=Buoy.Unknow):
        self.pump_gpio.write(True)
        self.buoy = buoy

    def pump_set(self, buoy=Buoy.Unknow):
        self.buoy = buoy

    def pump_drop(self):
        self.pump_gpio.write(False)
        self.ev_gpio.write(True)
        sleep(DELAY_EV)
        self.ev_gpio.write(False)
        self.buoy = Buoy.Empty

    def __str__(self):
        s = "Pump: %d/" % self.pump_nb
        s += "Pump output: %d/" % self.pump_gpio.read()
        s += "EV output: %d/" % self.ev_gpio.read()
        s += "Buoy: %s" % self.buoy.value
        return s

##TODO:
## - color sensors
## - Multiplexer

def if_enabled(method):
    """
    A method can be disabled so that it cannot be used in any circumstances.
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if self.disabled:
            self.log(what='disabled',
                    msg="Usage of {} is disabled".format(method))
            return
        return method(self, *args, **kwargs)

    return wrapped

@Service.require("ax", "%s-1" % ROBOT)
@Service.require("ax", "%s-2" % ROBOT)
@Service.require("ax", "%s-3" % ROBOT)
@Service.require("ax", "%s-4" % ROBOT)
@Service.require("ax", "%s-5" % ROBOT)
@Service.require("trajman", ROBOT)

class Actuators(Service):

    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.robot = Robot(robot='pal')
        self.queue = Act_queue()

        self.disabled = False
        self.match_end = Event()
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')

        self.color = self.color1

        try:
            self.color = self.cs.match.get_match()['color']
        except Exception as e:
            print("Failed to get color: %s" % str(e))

        for n in [1, 2, 3, 4, 5]:
            self.cs.ax["%s-%d" % (ROBOT, n)].mode_joint()

        self.pumps = [
            PumpActuator(27, 18, 1),
            PumpActuator(22, 23, 2),
            PumpActuator(10, 24, 3),
            PumpActuator(9, 25, 4),
            PumpActuator(11, 8, 5),
            PumpActuator(5, 7, 6),
            PumpActuator(6, 16, 7),
            PumpActuator(19, 20, 8)
        ]

        self.reset()

    """START"""

    def start(self):
        self.queue.run_queue()
    
    """STOP"""

    def stop(self):
        self.queue.stop_queue()

    """RESET"""

    @Service.action
    def reset(self):
        self.disabled = False
        self.match_end.clear()

        self.deploy_flags()

        sleep(0.2)

        for n in [1, 2, 3, 4, 5]:
            self.cs.ax["%s-%d" % (ROBOT, n)].move(goal=512)

        sleep(0.5)

        self.cs.ax["%s-%d" % (ROBOT, 3)].move(goal=210)
        self.cs.ax["%s-%d" % (ROBOT, 4)].move(goal=820)

        self.close_arm_right()
        self.close_arm_left()

        sleep(0.2)

    """FREE"""

    @Service.action
    def free(self):
        for pump in self.pumps:
            pump.pump_drop()
        for n in [1, 2, 3, 4, 5]:
            self.cs.ax[str(n)].free()

    """ FLAGS """

    @Service.action
    @if_enabled
    def flags_raise(self):
        self.cs.ax["%s-%d" % (ROBOT, 5)].move(goal=820)
    
    @Service.action
    @if_enabled
    def flags_low(self):
        self.cs.ax["%s-%d" % (ROBOT, 5)].move(goal=512)

    """ OTHERS """

    @Service.action
    def print_status(self):
        print("--- PUMPS ---")
        for pump in self.pumps:
            print(pump)
        print("--- AX12 ---")
        for n in [1, 2, 3, 4, 5]:
            print("AX12 %d: %s" %
                (n, self.cs.ax["%s-%d" % (ROBOT, n)].get_present_position()))
        print("--- COLOR SENSOR ---")
        print("Sensor left")
        print("Sensor right")
        print("-------------------------")

    @Service.action
    def get_status(self):
        status = {
            'pump': [],
            'ax': [],
            'sensor': []
        }
        for pump in self.pumps:
            status['pump'].append(pump)
        for n in [1, 2, 3, 4, 5]:
            status['ax'].append(self.cs.ax["%s-%d" % (ROBOT, n)].get_present_position())
        return status

    @Service.action
    @if_enabled
    def empty_buoys(self):
        pass
        # TODO : make something intelligent

    @Service.action
    @if_enabled
    def wait(self, time):
        sleep(float(time))

    # Disable Actuators
    @Service.action
    def disable(self):
        self.disabled = True
        self.stop()
        self.free()

    # Enable Actuators
    @Service.action
    def enable(self):
        self.disabled = False
        self.queue.run_queue()

    """ EVENTS """

    # Handle color changing event
    @Service.event("match_color")
    def color_handler(self, color):
        if color != self.color1 or color != self.color2:
            return
        self.color = color

    # Handle Match End
    @Service.event("match_end")
    def handle_match_end(self):
        self.free()
        self.match_end.set()
        self.disable()

    #Handle anchorage area
    @Service.event("anchorage")
    def set_anchorage(self):
        return

    """ACTIONS"""

    """LOW LEVEL"""

    """ BACK ARMS """

    @Service.action
    @if_enabled
    def close_arm_right(self):
        self.cs.ax["%s-%d" % (ROBOT, 4)].move(goal=820)

    @Service.action
    @if_enabled
    def close_arm_left(self):
        self.cs.ax["%s-%d" % (ROBOT, 3)].move(goal=820)

    @Service.action
    @if_enabled
    def open_arm_right(self):
        self.cs.ax["%s-%d" % (ROBOT, 4)].move(goal=512)

    @Service.action
    @if_enabled
    def open_arm_left(self):
        self.cs.ax["%s-%d" % (ROBOT, 3)].move(goal=512)

    """ SIDE ARMS """
    
    @Service.action
    @if_enabled
    def cup_holder_left_open(self):
        self.cs.ac["%s-%d" % (ROBOT, 2)].move(goal=512)

    @Service.action
    @if_enabled
    def cup_holder_right_open(self):
        self.cs.ac["%s-%d" % (ROBOT, 1)].move(goal=512)

    @Service.action
    @if_enabled
    def cup_holder_left_close(self):
        self.cs.ac["%s-%d" % (ROBOT, 2)].move(goal=820)

    @Service.action
    @if_enabled
    def cup_holder_right_close(self):
        self.cs.ac["%s-%d" % (ROBOT, 1)].move(goal=820)

    """HIGH LEVEL"""

    @Service.action
    @if_enabled
    def _push_windsocks(self):
        ax = 3
        if self.color != self.color1:
            ax = 4

        self.cs.ax["%s-%d" % (ROBOT, ax)].move(goal=512)

        sleep(0.2)

        # TODO config
        status = self.robot.move_trsl_avoid(
            500, 125, 125, 800, 1, 2, 2) == Status.reached

        self.cs.ax["%s-%d" % (ROBOT, ax)].move(goal=820 if ax != 3 else 210)

        sleep(0.2)

        return status

    @Service.action
    @if_enabled
    def push_windsocks(self):
        function = [self._push_windsocks, None]
        self.queue.run_action(*function)

    @Service.action
    @if_enabled
    def get_floor_buoy(self, holder):
        open_function = [(self.cup_holder_right_open if holder == 1 
            else
        self.cup_holder_left_open), None]
        trigger_pump_function = [[(self.pumps[4].pump_get() if holder == 1
            else
        self.pump[6].pump_get()), None], (self.pumps[5].pump_get() if holder == 1
            else
        self.pump[7].pump_get()), None]
        get_buoy = [open_function, trigger_pump_function]
        self.queue.run_actions(*get_buoy)

    @Service.action
    @if_enabled
    def drop_chenal(self):
        #TODO
        return


def wait_for_beacon():
    hostname = "pi"
    while True:
        r = os.system("ping -c 1 " + hostname)
        if r == 0:
            return
        pass

def main():
    #wait_for_beacon()
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
