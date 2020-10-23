#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

from evolutek.lib.gpio import Gpio, Pwm, Edge
from evolutek.lib.action_queue import Act_queue
from evolutek.lib.robot import Robot, Status
from evolutek.lib.rgb_sensors import RGBSensors
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog

from enum import Enum
from functools import wraps
from threading import Event
from time import sleep

DELAY_EV = 0.5
SAMPLE_SIZE = 10

# Emergency stop button
BAU_GPIO = 21

# pattern
class Pattern(Enum):
    Case_1 = "same"
    Case_2 = "red-green"
    Case_3 = "green-red"

##################
# PUMP ACTUATORS #
##################

# Buoy Type
class Buoy(Enum):
    Empty = "empty"
    Green = "green"
    Red = "red"
    Unknown = "unknown"

# Pump actuator
class PumpActuator:

    def __init__(self, pump_gpio, ev_gpio, pump_nb):
        self.pump_gpio = Gpio(pump_gpio, "Pump-%d" % pump_nb, True)
        self.ev_gpio = Gpio(ev_gpio, "EV-%d" % pump_nb, True)

        self.pump_nb = pump_nb

        self.buoy = Buoy.Empty

    def pump_get(self, buoy=Buoy.Unknown):
        self.pump_gpio.write(True)
        self.buoy = buoy

    def pump_set(self, buoy=Buoy.Unknown):
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

def use_queue(method):
    """
    Make quit a fucntion waiting for the queue if that one is no longer running
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        parameters = [self, args, kwargs]

        if self.queue.stop.is_set():
            return

        self.queue.run_action(method, parameters)
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
        self.robot = Robot(robot=ROBOT)
        self.queue = Act_queue()
        self.rgb_sensors = RGBSensors([1, 2], SAMPLE_SIZE)
        self.disabled = False
        self.match_end = Event()
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')


        # If the BAU is set at init, free the robot
        # if bau_gpio.read() == 0:
        #     self.free()


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
        # BAU (emergency stop)
        bau_gpio = Gpio(BAU_GPIO, 'bau', dir=False, edge=Edge.BOTH)
        bau_gpio.auto_refresh(callback=self.handle_bau)


    ########
    # CORE #
    ########

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
        self.start()

    # Start
    def start(self):
        self.queue.run_queue()

    # Stop
    def stop(self):
        self.queue.stop_queue()

    # Reset
    @Service.action
    def reset(self):
        self.disabled = False
        self.match_end.clear()

        self.cs.ax["%s-%d" % (ROBOT, 5)].moving_speed(256)

        self.left_arm_open()
        self.right_arm_open()
        self.left_cup_holder_open()
        self.right_cup_holder_open()
        self.flags_raise()

        sleep(1)

        self.left_arm_close()
        self.right_arm_close()
        self.left_cup_holder_close()
        self.right_cup_holder_close()
        self.flags_low()

        sleep(1)
        self.start()

    # Free
    @Service.action
    def free(self):
        self.pumps_drop([i for i in range (1, len(self.pumps) + 1)])
        for n in [1, 2, 3, 4, 5]: # TODO : read config
            self.cs.ax["%s-%d" % (ROBOT, n)].free()


    #######
    # BAU #
    #######
    @Service.action
    def handle_bau(self, value, event='', name='', id=0):
        if value == 0:
            self.free()
            self.disable()
        else:
            self.enable()
            self.reset()


    ########
    # WAIT #
    ########
    @Service.action
    @if_enabled
    @use_queue
    def wait(self, time):
        sleep(float(time))


    ##########
    # STATUS #
    ##########

    # Print Status
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
        print("Sensor left: %s", self.rgb_sensors.read_sensor(2, "match"))
        print("Sensor right: %s", self.rgb_sensors.read_sensor(1, "match"))
        print("-------------------------")

    # Get Status
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
        status['sensor'].append(self.rgb_sensors.read_sensor(1, "match"))
        status['sensor'].append(self.rgb_sensors.read_sensor(2, "match"))
        return status


    #########
    # FLAGS #
    #########

    # Raise Flags
    @Service.action
    @if_enabled
    def flags_raise(self):
        self.cs.ax["%s-%d" % (ROBOT, 5)].move(goal=820)

    # Close flags
    @Service.action
    @if_enabled
    def flags_low(self):
        self.cs.ax["%s-%d" % (ROBOT, 5)].move(goal=512)


    #########
    # PUMPS #
    #########

    # Get Buoy
    @Service.action
    @if_enabled
    def pump_get(self, pump, buoy='unknown'):
        valid = True
        pump = int(pump)
        try:
            buoy = Buoy(buoy)
        except:
            valid = False
        if pump > 0 and pump <= 8 and valid:
            self.pumps[pump - 1].pump_get(Buoy(buoy))
            return True
        else:
            print('[ACTUATORS] Not a valid pump or color: %d' % pump)
            return False

    # Set Buoy
    @Service.action
    def pump_set(self, pump, buoy='unknown'):
        if pump > 0 and pump <= 8:
            self.pumps[pump - 1].pump_set(Buoy(buoy))
        else:
            print('[ACTUATORS] Not a valid pump: %d' % pump)

    # Drop Buoy
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
    def pumps_drop(self, pumps):
        print(pumps)
        _pumps = [self.pumps[int(p) - 1].pump_drop for p in pumps]
        try:
            self.queue.launch_multiple_actions(_pumps, [[] for i in range((len(pumps)))])
        except Exception as e:
            print (e)


    ###############
    # RGB Sensors #
    ###############

    # Read
    @Service.action
    def rgb_sensor_read(self, n):
        n = int(n)
        if n < 1 or n > 2:
            print('[ACTUATORS] Wrong rgb sensor: %d' % n)
        result = self.rgb_sensors.read_sensor(n, "match")
        print("result: {}".format(result))
        return result


    #############
    # SIDE ARMS #
    #############

    # Left Arm Close
    @Service.action
    @if_enabled
    def left_arm_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 3)].move(goal=820)

    # Left Arm Open
    @Service.action
    @if_enabled
    def left_arm_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 3)].move(goal=512)

    # Left Arm Push Windsock
    @Service.action
    @if_enabled
    def left_arm_push(self):
        self.cs.ax["%s-%d" % (ROBOT, 3)].move(goal=444)

    # Right Arm Close
    @Service.action
    @if_enabled
    def right_arm_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 4)].move(goal=204)

    # Right Arm Open
    @Service.action
    @if_enabled
    def right_arm_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 4)].move(goal=512)

    # Left Arm Push Windsock
    @Service.action
    @if_enabled
    def right_arm_push(self):
        self.cs.ax["%s-%d" % (ROBOT, 4)].move(goal=580)

    ###############
    # CUP HOLDERS #
    ###############


    # Left CH Close
    @Service.action
    @if_enabled
    def left_cup_holder_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 1)].moving_speed(256)
        self.cs.ax["%s-%d" % (ROBOT, 1)].move(goal=820)

    # Left CH Open
    @Service.action
    @if_enabled
    def left_cup_holder_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 1)].moving_speed(800)
        self.cs.ax["%s-%d" % (ROBOT, 1)].move(goal=512)

    # Left CH Drop
    @Service.action
    @if_enabled
    def left_cup_holder_drop(self):
        self.cs.ax["%s-%d" % (ROBOT, 1)].moving_speed(800)
        self.cs.ax["%s-%d" % (ROBOT, 1)].move(goal=450)

    # Right CH Close
    @Service.action
    @if_enabled
    def right_cup_holder_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 2)].moving_speed(256)
        self.cs.ax["%s-%d" % (ROBOT, 2)].move(goal=820)

    # Right CH Open
    @Service.action
    @if_enabled
    def right_cup_holder_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 2)].moving_speed(800)
        self.cs.ax["%s-%d" % (ROBOT, 2)].move(goal=512)

    # Right CH Drop
    @Service.action
    @if_enabled
    def right_cup_holder_drop(self):
        self.cs.ax["%s-%d" % (ROBOT, 2)].moving_speed(800)
        self.cs.ax["%s-%d" % (ROBOT, 2)].move(goal=450)


    ######################
    # HIGH LEVEL ACTIONS #
    ######################

    @Service.action
    @if_enabled
    @use_queue
    def windsocks_push(self):

        print("COUCOU")
        if self.color == self.color1: self.left_arm_open()
        else: self.right_arm_open()
        print("HELLO")
        sleep(0.5)

        # TODO config
        self.robot.tm.set_delta_max_rot(1)
        self.robot.tm.set_delta_max_trsl(500)

        self.robot.move_trsl_block(dest=600, acc=300, dec=300, maxspeed=400, sens=1)

        if self.color == self.color1:
            self.left_arm_push()
            sleep(0.2)
            self.left_arm_close()
        else:
            self.right_arm_push()
            sleep(0.2)
            self.right_arm_close()
        sleep(0.5)

        # TODO config
        self.robot.tm.set_delta_max_rot(0.2)
        self.robot.tm.set_delta_max_trsl(100)

        self.robot.move_trsl_block(100, 400, 400, 500, 0)

    @Service.action
    @if_enabled
    def set_pattern(self):
        if (self.color == self.color1):
            pattern_1 = ["green", "green"]
        else:
            pattern_1 = ["red", "red"]
        pattern_2 = ["red", "green"]
        pattern_3 = ["green", "red"]
        first_sensor = self.rgb_sensors.read_sensor(1, "match").split(':')[1]
        second_sensor = self.rgb_sensors.read_sensor(2, "match").split(':')[1]
        first_sensor = first_sensor.replace(' ', '')
        second_sensor = second_sensor.replace(' ', '')
        combo = [first_sensor, second_sensor]
        print(combo)
        if combo == pattern_1:
            print('case 1')
            return 1 #Pattern.Case_1
        elif combo == pattern_2:
            print('case 2')
            return 2 #Pattern.Case_2
        elif combo == pattern_3:
            print('case 3')
            return 3 #Pattern.Case_3
        else:
            print('return case 1 by default')
            return 42 #Pattern.Case_1

    @Service.action
    @if_enabled
    @use_queue
    def get_reef(self):
        self.left_cup_holder_open()
        self.right_cup_holder_open()
        sleep(0.5)
        self.pump_get(pump=5)
        self.pump_get(pump=6)
        self.pump_get(pump=7)
        self.pump_get(pump=8)
        self.robot.tm.move_trsl(400, 300, 300, 300, 0)
        sleep(2)
        self.robot.tm.free()
        sleep(0.5)
        self.left_cup_holder_close()
        self.right_cup_holder_close()
        sleep(1)
        self.robot.move_trsl_block(200, 300, 300, 300, 1)


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
        # TODO
        pass


def main():
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
