#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

from evolutek.lib.gpio import Gpio, Pwm
from evolutek.lib.actionqueue import Act_queue
from evolutek.lib.robot import Robot, Status
from evolutek.lib.rgb_sensors import RGBSensors
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

from enum import Enum
from functools import wraps
from threading import Event
from time import sleep

DELAY_EV = 0.2
SAMPLE_SIZE = 10

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
        self.sensors = [
            RGBSensors(1, SAMPLE_SIZE),
            RGBSensors(2, SAMPLE_SIZE)
            ]

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
            PumpActuator(9, 24, 3),
            PumpActuator(11, 25, 4),
            PumpActuator(5, 8, 5),
            PumpActuator(6, 7, 6),
            PumpActuator(19, 16, 7),
            PumpActuator(26, 20, 8)
        ]

        self.reset()

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
        self.start()

    #########
    # START #
    #########   

    def start(self):
        self.queue.run_queue()
    
    ########
    # STOP #
    ########

    def stop(self):
        self.queue.stop_queue()

    #########
    # RESET #
    #########    

    @Service.action
    def reset(self):
        self.disabled = False
        self.match_end.clear()

        self.left_arm_open()
        self.open_arm_right()
        self.left_cup_holder_open()
        self.right_cup_holder_open()
        self.flags_raise()

        sleep(0.5)

        self.left_arm_close()
        self.right_arm_close()
        self.left_cup_holder_close()
        self.right_cup_holder_close()
        self.flags_low()

        sleep(0.5)
        self.start()

    ########
    # FREE #
    ########    

    @Service.action
    def free(self):
        for pump in self.pumps:
            pump.pump_drop()
        for n in [1, 2, 3, 4, 5]: # TODO : read config
            self.cs.ax[str(n)].free()

    @Service.action
    @if_enabled
    def wait(self, time):
        sleep(float(time))

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
        print("Sensor left: %s", self.sensors[1].read_sensor(2))
        print("Sensor right: %s", self.sensors[0].read_sensor(1))
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
        for n in [1, 2, 3, 4, 5]: # TODO : read config
            status['ax'].append(self.cs.ax["%s-%d" % (ROBOT, n)].get_present_position())
        status['sensor'].append(self.sensors[0].read_sensor(1))
        status['sensor'].append(self.sensors[1].read_sensor(2))
        return status

    #########
    # FLAGS #
    #########    

    @Service.action
    @if_enabled
    def flags_raise(self):
        self.cs.ax["%s-%d" % (ROBOT, 5)].move(goal=820)
    
    @Service.action
    @if_enabled
    def flags_low(self):
        self.cs.ax["%s-%d" % (ROBOT, 5)].move(goal=512)

    #########
    # PUMPS #
    #########

    @Service.action
    @if_enabled
    def pump_get(self, pump, buoy='unknow'):
        pump = int(pump)
        if pump > 0 and pump <= 8:
            self.pumps[pump - 1].pump_get(Buoy(buoy))
        else:
            print('[ACTUATORS] Not a valid pump: %d' % pump)

    @Service.action
    @if_enabled
    def pump_set(self, pump, buoy='unknow'):
        pump = int(pump)
        if pump > 0 and pump <= 8:
            self.pumps[pump - 1].pump_set(Buoy(buoy))
        else:
            print('[ACTUATORS] Not a valid pump: %d' % pump)

    @Service.action
    @if_enabled
    def pump_drop(self, pump):
        pump = int(pump)
        if pump > 0 and pump <= 8:
            self.pumps[pump - 1].pump_drop()
        else:
            print('[ACTUATORS] Not a valid pump: %d' % pump)

    @Service.action
    @if_enabled
    def rgb_sensor_read(self, n):
        return (self.sensors[n].read_sensor())

    #############
    # SIDE ARMS #
    #############
    
    @Service.action
    @if_enabled
    def right_arm_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 4)].move(goal=204)

    @Service.action
    @if_enabled
    def left_arm_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 3)].move(goal=820)

    @Service.action
    @if_enabled
    def right_arm_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 4)].move(goal=512)

    @Service.action
    @if_enabled
    def left_arm_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 3)].move(goal=512)

    ###############
    # CUP HOLDERS #
    ###############

    @Service.action
    @if_enabled
    def left_cup_holder_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 2)].move(goal=512)

    @Service.action
    @if_enabled
    def right_cup_holder_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 1)].move(goal=512)

    @Service.action
    @if_enabled
    def left_cup_holder_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 2)].move(goal=820)

    @Service.action
    @if_enabled
    def right_cup_holder_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 1)].move(goal=820)

    @Service.action
    @if_enabled
    def _windsocks_push(self):
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
    def windsocks_push(self):
        function = [self._windsocks_push, None]
        self.queue.run_action(*function)

    @Service.action
    @if_enabled
    def buoy_get_floor(self, holder):
        open_function = [(self.right_cup_holder_open if holder == 1 
            else
        self.left_cup_holder_open), None]
        trigger_pump_function = [[(self.pumps[4].pump_get() if holder == 1
            else
        self.pump[6].pump_get()), None], (self.pumps[5].pump_get() if holder == 1
            else
        self.pump[7].pump_get()), None]
        get_buoy = [open_function, trigger_pump_function]
        self.queue.run_actions(*get_buoy)

    @Service.action
    @if_enabled
    def chenal_drop(self):
        #TODO
        return
    
    ##########
    # EVENTS #
    ##########

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
    def anchorage_set(self):
        return

def main():
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
