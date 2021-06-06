#!/usr/bin/env python3

# Cellaserv
from cellaserv.service import Service
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
from evolutek.lib.sensors.rgb_sensors import RGBSensors

# Other imports
from evolutek.lib.utils.lma import launch_multiple_actions
from evolutek.lib.settings import ROBOT
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.wrappers import if_enabled
from threading import Event

# TODO :
# - Return status from RobotStatus (newRobot branch)
# - Put components config in a lib / read a JSON

# Actuators service class
class Actuators(Service):

    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.disabled = Event()

        self.ax = AX12Controller(
            [1, 2, 3, 4, 5, 6]
        )

        self.pumps = PumpController(
            {
                1: [
                    create_gpio(0, 'pump1', dir=True, type=GpioType.MCP),
                    create_gpio(1, 'ev1', dir=True, type=GpioType.MCP)
                ],
                2 : [
                    create_gpio(2, 'pump2', dir=True, type=GpioType.MCP),
                    create_gpio(3, 'ev2', dir=True, type=GpioType.MCP)
                ],
                3 : [
                    create_gpio(4, 'pump3', dir=True, type=GpioType.MCP),
                    create_gpio(5, 'ev3', dir=True, type=GpioType.MCP)
                ],
                4: [
                    create_gpio(6, 'pump4', dir=True, type=GpioType.MCP),
                    create_gpio(7, 'ev4', dir=True, type=GpioType.MCP)
                ],
                5 : [
                    create_gpio(8, 'pump5', dir=True, type=GpioType.MCP),
                    create_gpio(9, 'ev5', dir=True, type=GpioType.MCP)
                ],
                6 : [
                    create_gpio(10, 'pump6', dir=True, type=GpioType.MCP),
                    create_gpio(11, 'ev6', dir=True, type=GpioType.MCP)
                ],
                7 : [
                    create_gpio(12, 'pump7', dir=True, type=GpioType.MCP),
                    create_gpio(13, 'ev7', dir=True, type=GpioType.MCP)
                ],
                8 : [
                    create_gpio(14, 'pump8', dir=True, type=GpioType.MCP),
                    create_gpio(15, 'ev8', dir=True, type=GpioType.MCP)
                ],
                9 : [
                    create_gpio(18, 'pump9', dir=True, type=GpioType.MCP),
                    create_gpio(19, 'ev9', dir=True, type=GpioType.MCP)
                ],
                10 : [
                    create_gpio(20, 'pump10', dir=True, type=GpioType.MCP),
                    create_gpio(21, 'ev10', dir=True, type=GpioType.MCP)
                ]
            }
        )

        self.proximity_sensors = ProximitySensors(
            {
                1 : [create_gpio(24, 'proximity_sensors1', dir=False, type=GpioType.MCP)],
                2 : [create_gpio(25, 'proximity_sensors2', dir=False, type=GpioType.MCP)],
                3 : [create_gpio(26, 'proximity_sensors3', dir=False, type=GpioType.MCP)],
                4 : [create_gpio(27, 'proximity_sensors4', dir=False, type=GpioType.MCP)]
            }
        )

        self.recal_sensors = RecalSensors(
            {
                1: [create_adc(0, "recal1", type=AdcType.ADS)],
                2: [create_adc(1, "recal2", type=AdcType.ADS)]
            }
        )

        self.rgb_sensors = RGBSensors(
            [1, 2, 3, 4]
        )

        self.bau = create_gpio(28, 'bau', dir=False, type=GpioType.MCP)
        self.bau_led = create_gpio(20, 'bau led', dir=True, type=GpioType.RPI)
        self.bau.auto_refresh(refresh=0.1, callback=self.bau_callback)
        self.bau_led.write(self.bau_read())

        self.red_led = create_gpio(23, 'red led', dir=True, type=GpioType.RPI)
        self.green_led = create_gpio(24, 'green led', dir=True, type=GpioType.RPI)

        self.tirette = create_gpio(17, 'tirette', dir=False, edge=Edge.FALLING, type=GpioType.RPI)
        self.tirette.auto_refresh(refresh=0.1, callback=self.publish)
        self.white_led_strip = create_gpio(16, 'leds strips', dir=True, type=GpioType.MCP)

        self.rgb_led_strip = WS2812BLedStrip(42, board.D12, 16, 0.2)

        try:
            self.match_color_callback(self.cs.match.get_color())
        except Exception as e:
            print('[ACTUATORS] Failed to set color: %s' % str(e))

        self.all_actuators = [
            self.ax,
            self.pumps,
            self.proximity_sensors,
            self.recal_sensors,
            self.rgb_sensors,
            self.rgb_led_strip
        ]

        self.is_initialized = True
        for actuator in self.all_actuators:
            if not actuator.is_initialized():
                print ("[ACTUATORS] \n%s is not initialized" % (actuator.name))
                self.is_initialized = False

        if self.is_initialized:
            print("[ACTUATORS] Fully initialized")

    @Service.action
    def print_status(self):
        for actuators in self.all_actuators:
            print(actuators)

    @Service.action
    def get_status(self):
        d = {}
        for actuators in self.all_actuators:
            d.update(actuators.__dict__())
        return d

    # Free all actuators
    @Service.action
    def free(self):
        self.axs_free([1, 2, 3, 4, 5, 6])
        self.pumps_drop([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Disable Actuators
    @Service.action
    def disable(self):
        self.disabled.set()
        self.free()

    # Enable Actuators
    @Service.action
    def enable(self):
        self.disabled.clear()

    #########
    # PUMPS #
    #########
    @if_enabled
    @Service.action
    def pumps_drop(self, ids):
        if (type(ids) == str):
            ids = ids.split(",")
        func = []
        args = []
        for i in ids:
            if self.pumps[int(i)] == None:
                continue
            func.append(self.pumps[int(i)].drop)
            args.append({})
        launch_multiple_actions(func, args)

    @if_enabled
    @Service.action
    def pumps_get(self, ids):
        if (type(ids) == str):
            ids = ids.split(",")
        func = []
        args = []
        for i in ids:
            if self.pumps[int(i)] == None:
                continue
            func.append(self.pumps[int(i)].get)
            args.append({})
        launch_multiple_actions(func, args)

    #######
    # AXS #
    #######
    @if_enabled
    @Service.action
    def ax_move(self, id, pos):
        if self.ax[int(id)] == None:
            return None
        return self.ax[int(id)].move(pos)

    @Service.action
    def axs_free(self, ids):
        if (type(ids) == str):
            ids = ids.split(",")
        func = []
        args = []
        for i in ids:
            if self.ax[int(i)] == None:
                return ("[ACTUATORS] Invalid ax id: " + i)
            func.append(self.ax[int(i)].free)
            args.append({})
        launch_multiple_actions(func, args)

    @Service.action
    def ax_set_speed(self, id, speed):
        if self.ax[int(id)] == None:
            return None
        return self.ax[int(id)].moving_speed(speed)

    @Service.action
    def axs_get_status(self, ids):
        s = ""
        if (type(ids) == str):
            ids = ids.split(",")
        for i in ids:
            if self.ax[int(i)] == None:
                return ("[ACTUATORS] Invalid ax id: " + i)
            s += str(self.ax[int(i)]) + "\n"
        return s

    #################
    # COLOR SENSORS #
    #################
    @Service.action
    def color_sensor_read(self, id):
        if self.rgb_sensors[int(id)] == None:
            return None
        return self.rgb_sensors[int(id)].read().name

    #################
    # RECAL SENSORS #
    #################
    @Service.action
    def recal_sensor_read(self, id):
        if self.recal_sensors[int(id)] == None:
            return None
        return self.recal_sensors[int(id)].read()

    #####################
    # PROXIMITY SENSORS #
    #####################
    @Service.action
    def proximity_sensor_read(self, id):
        if self.proximity_sensors[int(id)] == None:
            return None
        return self.proximity_sensors[int(id)].read()

    #######
    # BAU #
    #######
    @Service.action
    def bau_read(self):
        return self.bau.read()

    def bau_callback(self, event, name, id, value):
        self.bau_led.write(value)
        self.publish(event=event, name=name, id=id, value=value)
        self.free()

    ###################
    # WHITE LED STRIP #
    ###################
    @Service.action
    def white_led_strip_set(self, on):
        if isinstance(on, str):
            on == 'true'
        self.white_led_strip.write(on)

    #################
    # RGB LED STRIP #
    #################
    @Service.action
    def rgb_led_strip_set_mode(self, mode):
        try:
            self.rgb_led_strip_set_mode(LightningMode(mode))
        except Exception as e:
            print('[ACTUATORS] Failed to set lightning mode: %s' % str(e))

    @Service.event('match_color')
    def match_color_callback(self, color):
        try:
            self.rgb_led_strip.set_loading_color(Color(color))
        except Exception as e:
            print('[ACTUATORS] Faile to set loading mode: %s' % str(e))


def main():
    actuators = Actuators()
    if not actuators.is_initialized:
        print('[ACTUATORS] Failed to initialize service')
        return
    actuators.run()

if __name__ == '__main__':
    main()
