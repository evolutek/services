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

DELAY_EV = 0.2
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
        parameters = [self, args]

        if self.queue.stop.is_set():
            return
        print(parameters)
        self.queue.run_action(method, tuple(parameters))
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

        self.cs.ax["%s-%d" % (ROBOT, 1)].moving_speed(128)
        self.cs.ax["%s-%d" % (ROBOT, 2)].moving_speed(128)
        self.cs.ax["%s-%d" % (ROBOT, 5)].moving_speed(256)

        self.left_arm_open()
        self.right_arm_open()
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

    # Free
    @Service.action
    def free(self):
        free_pump_array = []
        params = []
        for pump in self.pumps:
            free_pump_array.append(pump.pump_drop)
            params.append([])
        self.queue.run_actions(free_pump_array, [])
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


    ###############
    # CUP HOLDERS #
    ###############


    # Left CH Close
    @Service.action
    @if_enabled
    def left_cup_holder_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 1)].move(goal=820)

    # Left CH Open
    @Service.action
    @if_enabled
    def left_cup_holder_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 1)].move(goal=512)

    # Right CH Close
    @Service.action
    @if_enabled
    def right_cup_holder_close(self):
        self.cs.ax["%s-%d" % (ROBOT, 2)].move(goal=820)

    # Right CH Open
    @Service.action
    @if_enabled
    def right_cup_holder_open(self):
        self.cs.ax["%s-%d" % (ROBOT, 2)].move(goal=512)


    ######################
    # HIGH LEVEL ACTIONS #
    ######################

    @Service.action
    @if_enabled
    @use_queue
    def _windsocks_push(self):
        ax = 3
        if self.color != self.color1:
            ax = 4

        if self.queue.stop.is_set() == False:
            self.cs.ax["%s-%d" % (ROBOT, ax)].move(goal=512)
        else :
            return 
        sleep(0.2)

        # TODO config
        if self.queue.stop.is_set() == False:
            status = self.robot.move_trsl_avoid(
                500, 125, 125, 800, 1, 2, 2) == Status.reached
        else:
            return

        if self.queue.stop.is_set() == False:
            self.cs.ax["%s-%d" % (ROBOT, ax)].move(goal=820 if ax != 3 else 210)
        else:
            return 
        sleep(0.2)

        return status

#    @Service.action
 #   @if_enabled
  #  def windsocks_push(self):
   #     result = None
    #    function = [self._windsocks_push, None]
     #   self.queue.run_action(*function)
      #  result = self.queue.response_queue.get()
       # return result

    @Service.action
    @if_enabled
    def get_floor_buoy(self, pump, buoy='unknown'):
        self.pump_get(pump, buoy)

    # @Service.action
    # @if_enabled
    # def get_sorted_reef():
    #     self.left_cup_holder_open()
    #     self.right_cup_holder_open()
    #     for i in range (5, 9):
    #         ##self.pumps[i]
    #         self.get(i)
    #     self.left_cup_holder_close()
    #     self.right_cup_holder_close()
    #    # self.pum


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
