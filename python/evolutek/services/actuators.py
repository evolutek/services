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
from math import pi
from threading import Event
from time import sleep

DELAY_EV = 1.0
SAMPLE_SIZE = 10

# Emergency stop button
BAU_GPIO = 21

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

        return self.queue.run_action(method, parameters)
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
        self.robot = Robot(robot=ROBOT, match_end_cb=self.handle_match_end)
        self.queue = Act_queue()
        self.rgb_sensors = RGBSensors([1, 2], SAMPLE_SIZE)
        self.disabled = False
        self.match_end = Event()
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')

        # False = North
        # True = South
        self.anchorage = False

        # If the BAU is set at init, free the robot
        # if bau_gpio.read() == 0:
        #     self.free()

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
    @Service.action
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
    def pump_get(self, pump, buoy='unknown', mirror=False):
        valid = True
        pump = int(pump)

        try:
            buoy = Buoy(buoy)
        except:
            valid = False
        if pump > 0 and pump <= 8 and valid:
            p = pump
            if mirror and self.robot.color == self.color2:
                p = 5 - pump % 5
                if pump > 4:
                    p = p + 3
            self.pumps[p - 1].pump_get(Buoy(buoy))
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
    def pump_drop(self, pump, mirror=False):
        pump = int(pump)
        if pump > 0 and pump <= 8:
            p = pump
            if mirror and self.robot.color == self.color2:
                p = 5 - pump % 5
                if pump > 4:
                    p = p + 3
            self.pumps[p - 1].pump_drop()
        else:
            print('[ACTUATORS] Not a valid pump: %d' % pump)

    @Service.action
    @if_enabled
    def pumps_drop(self, pumps):
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
        self.cs.ax["%s-%d" % (ROBOT, 1)].move(goal=490)

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
        self.cs.ax["%s-%d" % (ROBOT, 2)].move(goal=490)


    ######################
    # HIGH LEVEL ACTIONS #
    ######################

    @Service.action
    @if_enabled
    @use_queue
    def start_lighthouse(self):
        if self.robot.color == self.color1:
            self.right_cup_holder_open()
        else:
            self.left_cup_holder_open()

        sleep(0.5)
        self.robot.tm.set_trsl_max_speed(100)
        status = self.robot.goto_avoid(x=130, y=330)
        self.robot.tm.set_trsl_max_speed(None)
        if self.queue.stop.is_set():
            return Status.unreached.value
        status = self.robot.goto_avoid(x=300, y=330)

        if self.robot.color == self.color1:
            self.right_cup_holder_close()
        else:
            self.left_cup_holder_close()

        return status.value

    @Service.action
    @if_enabled
    @use_queue
    def drop_starting_without_sort(self):
        if (self.queue.stop.is_set()):
            return Status.unreached.value
        #status = self.robot.move_trsl_avoid(100, 500, 500, 500, 1)
        status = self.robot.goto_avoid(x=600, y=300)
        self.pumps_drop([1, 2, 3, 4])
        if self.should_stop(status):
            return Status.unreached.value
        #if self.should_stop(self.robot.move_trsl_avoid(100, 500, 500, 500, 0)):
        if self.should_stop(self.robot.goto_avoid(x=500, y=300)):
            return Status.unreached.value
        self.robot.move_rot_block(pi, 5, 5, 5, 1)
        self.left_cup_holder_drop()
        self.right_cup_holder_drop()
        if self.queue.stop.is_set():
            return Status.unreached.value
        #status = self.robot.move_trsl_avoid(100, 500, 500, 500, 0)
#        status = self.robot.goto_avoid(x=700, y=300)
        self.pumps_drop([5, 6, 7, 8])
        if self.should_stop(status):
            return Status.unreached.value

        #status = self.robot.move_trsl_avoid(100, 500, 500, 500, 1)
        status = self.robot.goto_avoid(x=600, y=300)
        self.left_cup_holder_close()
        self.right_cup_holder_close()
        return Status.reached.value

    def should_stop(self, status):
        if status != Status.reached or self.queue.stop.is_set():
            print("non reached status detected!: ")
            print(status)
            return True
        return False

    @Service.action
    @if_enabled
    @use_queue
    def drop_starting_with_sort(self):
        #true == sud

        self.anchorage = self.cs.match.get_anchorage() == "south"
        self.robot.goth(pi if self.anchorage else 0)

        flip = self.anchorage ^ (self.color == self.color2)

        status = self.robot.move_trsl_avoid(150, 500, 500, 500, 1)
        self.pumps_drop([3, 4] if flip else [1, 2])
        if self.should_stop(status):
            return Status.unreached.value
        status = self.robot.move_trsl_avoid(200, 800, 800, 800, 0)

        status = self.robot.goth(pi/2)
        if not self.should_stop(status):
            if self.should_stop(robot.move_trsl_avoid(100, 500, 500, 500, 0)):
                return Status.unreached.value
        else:
            return Status.unreached.value
        status = self.robot.goth(0 if self.anchorage else pi)

        if (self.should_stop(status)):
            return Status.unreached.value
        self.left_cup_holder_drop()
        self.right_cup_holder_drop()
        sleep(0.5)
        if not self.queue.stop.is_set():
            status = self.robot.move_trsl_avoid(120, 300, 300, 300, 0)
        else:
            return Status.unreached.value
        self.pumps_drop([5, 7] if flip else [6, 8])

        status = self.robot.move_trsl_avoid(525, 300, 300, 300, 1)
        if self.should_stop(status):
            return Status.unreached.value
        self.pumps_drop([6, 8] if flip else [5, 7])
        if not self.queue.stop.is_set():
            status = self.robot.move_trsl_avoid(100, 800, 800, 800, 1)
        else:
            return Status.unreached.value
        self.left_cup_holder_close()
        self.right_cup_holder_close()

        if (self.should_stop(status)):
            return Status.unreached.value
        status = self.robot.goth(pi/2)
        if (self.queue.stop.is_set()):
            return Status.unreached.value if self.should_stop(status) else Status.reached.value
        status = self.robot.move_trsl_avoid(225, 500, 500, 500, 1)
        if self.robot.goth(pi if self.anchorage else 0) == Status.unreached:
            status = Status.unreached
        if (self.should_stop(status)):
            return Status.unreached.value
        status = self.robot.move_trsl_avoid(150, 300, 300, 300, 1)
        if self.should_stop(status):
            return Status.unreached.value
        self.pumps_drop([1, 2] if flip else [3, 4])
        self.robot.move_trsl_avoid(125, 800, 800, 800, 0)

        self.robot.goth(pi/2)

        if self.queue.stop.is_set():
            return Status.unreached.value
        status = self.robot.move_trsl_avoid(200, 500, 500, 500, 0)
        self.robot.recalibration_block(0)
        return status.value


    @Service.action
    @if_enabled
    @use_queue
    def drop_center_zone(self):

        side = self.color == self.color2

        # Get the two buoys on the front of the zone
        self.pump_get(pump=3 if side else 2)
        if self.should_stop(self.robot.move_trsl_avoid(150, 500, 500, 500, 1)):
            return Status.unreached.value
        status = self.robot.goth(-1 * pi/3)
        self.pump_get(pump=2 if side else 3)
        if self.should_stop(status):
            return Status.unreached.value
        status = self.robot.move_trsl_avoid(160, 500, 500, 500, 1)
        if self.should_stop(status):
            return Status.unreached.value
        status = self.robot.move_trsl_avoid(60, 500, 500, 500, 0)

        # Recal the robot in the zone
        if self.should_stop(status):
            return Status.unreached.value
        if  self.robot.goth(pi) == Status.unreached or self.queue.stop.is_set():
            return status.value
        if self.should_stop(self.robot.move_trsl_avoid(200, 500, 500, 500, 0)):
            return Status.unreached.value
        self.robot.recalibration(side_x=(False, True), decal_y=1511)
        if self.should_stop(self.robot.goto_avoid(1750, 1800)):
            return Status.unreached.value
        status = self.robot.goth(0)

        # Drop front buoys
        if self.should_stop(status):
            return Status.unreached.value
        if self.should_stop(self.robot.move_trsl_avoid(70, 500, 500, 500, 1)):
            return Status.unreached.value
        self.pumps_drop([1, 2, 3, 4])
        if self.should_stop(self.robot.move_trsl_avoid(85, 300, 300, 300, 0)):
            return Status.unreached.value

        pattern = self.get_pattern()
        print("PATTERN: %d" % pattern)

        # Drop Right zone
        if self.should_stop(self.robot.goth(pi/2)):
            return Status.unreached.value
        if self.should_stop(self.robot.move_trsl_avoid(75, 800, 800, 800, 1)):
            return Status.unreached.value
        self.left_cup_holder_drop()
        self.right_cup_holder_drop()
        if (self.should_stop(status)):
            return Status.unreached.value
        sleep(0.5)

        pumps = None
        if pattern == -1:
            pattern = 3

        if pattern == 1:
            pumps = ([6, 7])
        elif pattern == 2:
            pumps = ([5, 7] if side else [6, 8])
        else:
            pumps = ([5, 6] if side else [7, 8])

        self.pumps_drop(pumps)
        self.left_cup_holder_close()
        self.right_cup_holder_close()
        if (self.should_stop(status)):
            return Status.unreached.value
        sleep(1)

        if self.should_stop(self.robot.move_trsl_avoid(75, 800, 800, 800, 1)):
            return Status.unreached.value
        if self.should_stop(self.robot.goth(pi)):
            return Status.unreached.value
        if self.should_stop(self.robot.move_trsl_avoid(50, 500, 500, 500, 1)):
            return Status.unreached.value

        # Drop Left zone
        if side:
            self.right_cup_holder_drop()
        else:
            self.left_cup_holder_drop()
        if self.queue.stop.is_set():
            return Status.unreached.value
        sleep(0.5)

        self.pumps_drop([8] if side else [5])
        status = self.robot.move_trsl_avoid(100, 800, 800, 800, 1)

        if side:
            self.right_cup_holder_close()
        else:
            self.left_cup_holder_close()
        if (self.should_stop(status)):
            self.right_cup_holder_drop() if side else self.left_cup_holder_drop()
            return Status.unreached.value
        sleep(1)

        move = 3 - pattern
        self.robot.move_rot_block(pi/12 * move, 5, 5, 5, side)

        if (pattern == 3) ^ side:
            self.left_cup_holder_drop()
        else:
            self.right_cup_holder_drop()
        if self.queue.stop.is_set():
            self.left_cup_holder_close() if (pattern == 3) ^ side else self.right_cup_holder_close()
            return Status.unreached.value
        sleep(0.5)

        self.pumps_drop([4 + pattern] if side else [9 - pattern])
        if self.should_stop(self.robot.move_trsl_avoid(100, 800, 800, 800, 1)):
            self.left_cup_holder_close() if (pattern == 3) ^ side else self.right_cup_holder_close()
            return Status.unreached.value

        if (pattern == 3) ^ side:
            self.left_cup_holder_close()
        else:
            self.right_cup_holder_close()
        return Status.reached.value

    @Service.action
    @if_enabled
    @use_queue
    def wait_for_match_end():
        status = self.cs.match.get_status()
        while status['time'] < 90:
            sleep(0.5)
            status = self.cs.match.get_status()
        return Status.reached.value

    @Service.action
    @if_enabled
    @use_queue
    def get_reef_buoys(self):
        # 700 830 PI

        self.pump_get(pump=4, mirror=True)
        status = self.robot.goto_avoid(x=500, y=830)
        if self.should_stop(status):
            self.pump_drop(4)
            return Status.unreached.value
        if self.should_stop(self.robot.goth(-1 * pi/2)):
            return Status.unreached.value
        status = self.robot.goto_avoid(x=500, y=780)
        self.robot.goth(pi)

        self.pump_get(pump=1, mirror=True)
        if self.should_stop(status):
            self.pump_drop(1)
            return Status.unreached.value
            pos = self.robot.tm.get_position()
        if self.should_stop(self.robot.goto_avoid(x=200, y=780)):
            return Status.unreached.value
        status = self.robot.goto_avoid(x=350, y=780)
        return status.value

    @Service.action
    @if_enabled
    @use_queue
    def windsocks_push(self):

        if self.robot.color != self.color1: self.left_arm_open()
        else: self.right_arm_open()
        sleep(0.5)

        # TODO config
        self.robot.tm.set_delta_max_rot(1)
        self.robot.tm.set_delta_max_trsl(500)

        if self.should_stop(self.robot.goto_avoid(x=1825, y=720, mirror=True)):
            return Status.unreached.value

        if self.robot.color != self.color1:
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

        if self.should_stop(self.robot.goto_avoid(x=1825, y=600, mirror=True)):
            return Status.unreached.value
        return Status.reached.value

    @Service.action
    def get_pattern(self):
        if self.robot.color == self.color1:
            pattern_1 = ["green", "green"]
        else:
            pattern_1 = ["red", "red"]
        pattern_2 = ["green", "red"]
        pattern_3 = ["red", "green"]

        first_sensor = self.rgb_sensors.read_sensor(1, "match").split(':')[1]
        second_sensor = self.rgb_sensors.read_sensor(2, "match").split(':')[1]
        first_sensor = first_sensor.replace(' ', '')
        second_sensor = second_sensor.replace(' ', '')
        combo = [first_sensor, second_sensor]

        if combo == pattern_1:
            return 1 # red - red or green - green
        elif combo == pattern_2:
            return 2 # red - green
        elif combo == pattern_3:
            return 3 # green - red
        else:
            return -1

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

        if self.queue.stop.is_set():
            self.left_cup_holder_close()
            self.right_cup_holder_close()
            self.pumps_drop([5, 6, 7, 8])
            return Status.unreached.value
        self.robot.tm.move_trsl(400, 300, 300, 300, 0)
        sleep(2)
        self.robot.tm.free()
        sleep(0.5)
        self.left_cup_holder_close()
        self.right_cup_holder_close()
        sleep(1)

        if self.queue.stop.is_set():
            return Status.unreached.value

        status = self.robot.move_trsl_avoid(200, 300, 300, 300, 1)
        return Status.reached.value

    @Service.action
    @if_enabled
    @use_queue
    def go_to_anchorage(self):
        self.anchorage = self.cs.match.get_anchorage() == "south"
        posx = 300 if self.anchorage else 1300
        status = Status.reached
        if self.should_stop(self.robot.move_trsl_avoid(posx, 700)):
            return Status.unreached.value
        if self.should_stop(self.robot.move_trsl_avoid(posx, 200)):
            return Status.unreached.value
        self.robot.recalibration_block(0)
        return status.value

    @Service.action
    def handle_match_end(self):
        self.enable()
        self.flags_raise()
        self.free()
        self.match_end.set()
        self.disable()


def main():
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
