#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

from evolutek.lib.gpio import Gpio, Pwm
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

    def get_buoy(self, buoy=BuoyUnknow):
        self.pump_gpio.write(True)
        self.buoy = buoy

    def set_buoy(self, buoy=Buoy.Unknow):
        self.buoy = buoy

    def drop_buoy(self):
        self.pump_gpio.write(False)
        self.ev_gpio.write(True)
        sleep(DELAY_EV)
        self.ev_gpio.write(False)
        self.buoy = Buoy.Empty

    def __str__(self):
        s = "Pump: %d" % self.pump_nb
        s += "Pump output: %d" % self.pump_gpio.read()
        s += "EV output: %d" % self.ev_gpio.read()
        s += "Buoy: %s" % self.buoy.value
        return s

##TODO: REWORK
## - stop
## - color sensors

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

@Service.require("ax", "1")
@Service.require("ax", "2")
@Service.require("ax", "3")
@Service.require("ax", "4")
@Service.require("trajman", ROBOT)
class Actuators(Service):

    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.robot = Robot(robot='pal')

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
            PumpActuator(11, 24, 5),
            PumpActuator(5, 7, 6),
            PumpActuator(6, 16, 7),
            PumpActuator(19, 20, 8)
        ]

        self.reset()

    @Service.action
    def reset(self, color=None):
        if color is not None and (color == self.color1 or color == self.color2):
            self.color = color

        self.disabled = False
        self.match_end.clear()

        for n in [1, 2, 3, 4, 5]:
            self.cs.ax["%s-%d" % (ROBOT, n)].move(goal=512)

        # Add all other init functions

    #TODO: All other functions

    @Service.action
    @if_enabled
    def push_windsocks(self):
        ax = 3
        if self.color != self.color1:
            ax = 4

        self.cs.ax["%s-%d" % (ROBOT, n)].move(goal=512)

        # TODO config
        return self.robot.move_trsl_block(500, 100, 100, 600, 1, 2, 2) == Status.reached

    @Service.action
    def print_status(self):
        print("--- PUMPS ---")
        for pump in self.pumps:
            print(pump)
        print("--- AX12 ---")
        for n in [1, 2, 3, 4, 5]:
            print("AX12 %d: %s" % (n, self.cs.ax["%s-%d" % (ROBOT, n)].get_present_position()))
        print("-----")

    @Service.action
    @if_enabled
    def empty_buoys(self):
        pass
        # TODO : make something intelligent

    """ FREE """
    @Service.action
    def free(self):
        for pump in self.pumps:
            pump.drop_buoy()
        for n in [1, 2, 3, 4, 5]:
            self.cs.ax[str(n)].free()

    @Service.action
    @if_enabled
    def wait(self, time):
        sleep(float(time))

    # Disable Actuators
    @Service.action
    def disable(self):
        self.disabled = True

    # Enable Actuators
    @Service.action
    def enable(self):
        self.disabled = False

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
        self.disable ()

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
