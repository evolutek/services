#!/usr/bin/env python3

# Cellaserv
from cellaserv.service import Service, ConfigVariable
from cellaserv.proxy import CellaservProxy

# Gpio
import board
from evolutek.lib.gpio.gpio_factory import AdcType, create_adc, GpioType, create_gpio
from evolutek.lib.gpio.gpio import Edge

# Components
from evolutek.lib.actuators.ax12 import AX12Controller
from evolutek.lib.actuators.pump import PumpController
from evolutek.lib.indicators.ws2812b import WS2812BLedStrip, LightningMode
from evolutek.lib.sensors.proximity_sensors import ProximitySensors
from evolutek.lib.sensors.recal_sensors import RecalSensors
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation

# Other imports
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import Task
from evolutek.lib.utils.wrappers import if_enabled
from threading import Event
import atexit
from time import sleep

# TODO :
# - Put components config in a lib / read a JSON

# Actuators service class
@Service.require('config')
class Actuators(Service):

    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.disabled = Event()
        atexit.register(self.stop)

        self.proximity_sensors = ProximitySensors(
            {
                1 : [create_gpio(0, 'proximity_sensors1', dir=False, type=GpioType.MCP)],
                2 : [create_gpio(1, 'proximity_sensors2', dir=False, type=GpioType.MCP)]
            }
        )

        left_slope1 = float(self.cs.config.get(ROBOT, "left_slope1"))
        left_intercept1 = float(self.cs.config.get(ROBOT, "left_intercept1"))
        left_slope2 = float(self.cs.config.get(ROBOT, "left_slope2"))
        left_intercept2 = float(self.cs.config.get(ROBOT, "left_intercept2"))
        right_slope1 = float(self.cs.config.get(ROBOT, "right_slope1"))
        right_intercept1 = float(self.cs.config.get(ROBOT, "right_intercept1"))
        right_slope2 = float(self.cs.config.get(ROBOT, "right_slope2"))
        right_intercept2 = float(self.cs.config.get(ROBOT, "right_intercept2"))

        self.recal_sensors = RecalSensors(
            {
                1: [create_adc(0, "recal1", type=AdcType.ADS)],
                2: [create_adc(1, "recal2", type=AdcType.ADS)]
            }
        )
        self.recal_sensors[1].calibrate(left_slope1, left_intercept1, left_slope2, left_intercept2)
        self.recal_sensors[2].calibrate(right_slope1, right_intercept1, right_slope2, right_intercept2)

        self.bau = create_gpio(4, 'bau', event='%s-bau' % ROBOT, dir=False, type=GpioType.MCP)
        self.bau_led = create_gpio(20, 'bau led', dir=True, type=GpioType.RPI)
        self.bau.auto_refresh(refresh=0.05, callback=self.bau_callback)
        #self.bau_callback(event=self.bau.event, value=self.bau.read(), name='bau', id=self.bau.id)

        self.orange_led_strip = create_gpio(12, 'orange led strip', dir=True, type=GpioType.MCP)
        self.rgb_led_strip = WS2812BLedStrip(42, board.D12, 26, 0.25)

        try:
            self.match_color_callback(self.cs.match.get_color())
        except Exception as e:
            print('[ACTUATORS] Failed to set color: %s' % str(e))

        self.axs = AX12Controller(
            [1, 2]
        )

        acts = {
            0: [I2CActType.Servo, 180],
            1: [I2CActType.Servo, 180],
            2: [I2CActType.Servo, 180],
            3: [I2CActType.Servo, 180],
            4: [I2CActType.Servo, 180],
            8: {"type": I2CActType.ESC, "max_range": 0.5, "esc_variation": ESCVariation.Emax},
            9: {"type": I2CActType.ESC, "max_range": 0.5, "esc_variation": ESCVariation.Emax},
            10: {"type": I2CActType.ESC, "max_range": 0.5, "esc_variation": ESCVariation.Emax}
        }

        self.i2c_acts = I2CActsHandler(acts, frequency=50)

        self.all_actuators = [
            self.proximity_sensors,
            self.recal_sensors,
            self.axs,
            self.i2c_acts
        ]

        self.is_initialized = True
        for actuator in self.all_actuators:
            if not actuator.is_initialized():
                print ("[ACTUATORS] \n%s is not initialized" % (actuator.name))
                self.is_initialized = False

        if self.is_initialized:
            self.rgb_led_strip.start()
            self.enable()
            print("[ACTUATORS] Fully initialized")

    def stop(self):
        print("[ACTUATORS] Stopping")
        self.rgb_led_strip.stop()
        self.free()

    @Service.action
    def print_status(self):
        for actuators in self.all_actuators:
            print(actuators)

    #@Service.action
    def get_status(self):
        d = {}
        for actuators in self.all_actuators:
            print(actuators)
            d.update(actuators.__dict__())
        print(d)
        return d

    # Free all actuators
    @Service.action
    def free(self):
        # TODO
        pass

    # Disable Actuators
    @Service.action
    def disable(self):
        self.disabled.set()
        self.free()

    # Enable Actuators
    @Service.action
    def enable(self):
        if not self.disabled.is_set():
            return

        if self.bau.read():
            self.disabled.clear()
            self.i2c_acts.init_escs()
            for i in range(2):
                self.orange_led_strip_set(True)
                sleep(0.25)
                self.orange_led_strip_set(False)
                sleep(0.25)

    #####################
    # PROXIMITY SENSORS #
    #####################
    @Service.action
    def proximity_sensor_read(self, id):
        if self.proximity_sensors[int(id)] == None:
            return None
        return self.proximity_sensors[int(id)].read()

    #################
    # RECAL SENSORS #
    #################
    @Service.action
    def recal_sensor_read(self, id, repetitions=10):
        if self.recal_sensors[int(id)] == None:
            return None
        return self.recal_sensors[int(id)].read(repetitions=repetitions)

    #######
    # BAU #
    #######
    @Service.action
    def bau_read(self):
        return self.bau.read()

    def bau_callback(self, event, value, **kwargs):
        self.bau_led.write(value)
        self.publish(event=event, value=value, **kwargs)
        if value:
            self.enable()
        else:
            self.free()
            self.disable()

    ####################
    # ORANGE LED STRIP #
    ####################
    @Service.action
    def orange_led_strip_set(self, on):
        self.orange_led_strip.write(get_boolean(on))

    #################
    # RGB LED STRIP #
    #################
    @Service.action
    def rgb_led_strip_set_mode(self, mode):
        try:
            self.rgb_led_strip.set_mode(LightningMode(mode))
        except Exception as e:
            print('[ACTUATORS] Failed to set lightning mode: %s' % str(e))

    @Service.event('match_color')
    def match_color_callback(self, color):
        try:
            self.rgb_led_strip.set_loading_color(Color.get_by_name(color))
        except Exception as e:
            print('[ACTUATORS] Faile to set loading mode: %s' % str(e))

    #######
    # AXS #
    #######
    @if_enabled
    @Service.action
    def ax_move(self, id, pos):
        if self.axs[int(id)] == None:
            return RobotStatus.return_status(RobotStatus.Failed)
        self.axs[int(id)].move(int(pos))
        return RobotStatus.return_status(RobotStatus.Done)

    @Service.action
    def axs_free(self, ids):
        if isinstance(ids, str):
            ids = ids.split(",")

        for i in ids:
            if self.axs[int(i)] == None:
                continue
            self.axs[int(i)].free()

        return RobotStatus.return_status(RobotStatus.Done)

    @Service.action
    def ax_set_speed(self, id, speed):
        if self.axs[int(id)] == None:
            return None
        self.axs[int(id)].moving_speed(int(speed))
        return RobotStatus.return_status(RobotStatus.Done)

    ##########
    # SERVOS #
    ##########
    @Service.action
    def servo_set_angle(self, id, angle):
        if self.i2c_acts[int(id)] == None:
            return RobotStatus.return_status(RobotStatus.Failed)
        if self.i2c_acts[int(id)].set_angle(int(angle)):
            return RobotStatus.return_status(RobotStatus.Done)
        return RobotStatus.return_status(RobotStatus.Failed)

    #########
    #  ESC  #
    #########
    @Service.action
    def esc_set_speed(self, id, value):
        if self.i2c_acts[int(id)] == None:
            return RobotStatus.return_status(RobotStatus.Failed)
        if self.i2c_acts[int(id)].set_speed(float(value)):
            return RobotStatus.return_status(RobotStatus.Done)
        return RobotStatus.return_status(RobotStatus.Failed)

def main():
    actuators = Actuators()
    if not actuators.is_initialized:
        print('[ACTUATORS] Failed to initialize service')
        return
    actuators.run()

if __name__ == '__main__':
    main()
