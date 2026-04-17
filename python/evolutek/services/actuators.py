#!/usr/bin/env python3

# Cellaserv
from cellaserv.service import Service, ConfigVariable
from cellaserv.proxy import CellaservProxy

# GPIO
import board
from evolutek.lib.gpio.gpio_factory import AdcType, create_adc, GpioType, create_gpio
from evolutek.lib.gpio.gpio import Edge

# Components
from evolutek.lib.actuators.ax12 import AX12Controller
from evolutek.lib.actuators.pump import PumpController
from evolutek.lib.actuators.magnet import MagnetController
from evolutek.lib.indicators.ws2812b import WS2812BLedStrip, LightningMode
from evolutek.lib.sensors.proximity_sensors import ProximitySensors
from evolutek.lib.sensors.recal_sensors import RecalSensors
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.i2c_motor_board import I2CMotorBoard, I2CMotorBoardStepper

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
import json

import atexit

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

        left_recal_points = json.loads(self.cs.config.get(ROBOT, "left_recal_points"))
        right_recal_points = json.loads(self.cs.config.get(ROBOT, "right_recal_points"))

        # self.recal_sensors = RecalSensors(
        #     {
        #         1: [create_adc(0, "recal1", type=AdcType.ADS)],
        #         2: [create_adc(1, "recal2", type=AdcType.ADS)]
        #     }
        # )
        # self.recal_sensors[1].calibrate(left_recal_points)
        # self.recal_sensors[2].calibrate(right_recal_points)

        self.bau = create_gpio(20, 'bau', event='%s-bau' % ROBOT, dir=False, type=GpioType.RPI)
        #self.bau_led = create_gpio(20, 'bau led', dir=True, type=GpioType.RPI)
        self.bau.auto_refresh(refresh=0.05, callback=self.bau_callback)

        self.rgb_led_strip = WS2812BLedStrip(42, board.D12, 36, 0.25)

        try:
            self.match_color_callback(self.cs.match.get_color())
        except Exception as e:
            print('[ACTUATORS] Failed to set color: %s' % str(e))

        # self.proximity_sensors = ProximitySensors(
        #     {
        #         0: [ # Bottom right sensor
        #             create_gpio(0, 'proximity_sensors1', dir=False, type=GpioType.MCP)
        #         ],
        #         1: [ # Bottom middle sensor
        #             create_gpio(1, 'proximity_sensors2', dir=False, type=GpioType.MCP)
        #         ],
        #         2: [ # Bottom left sensor
        #             create_gpio(2, 'proximity_sensors3', dir=False, type=GpioType.MCP)
        #         ],
        #         3: [ # Clamp right sensor
        #             create_gpio(3, 'proximity_sensors4', dir=False, type=GpioType.MCP)
        #         ],
        #         4: [ # Clamp middle sensor
        #             create_gpio(4, 'pressure_sensor1', dir=False, type=GpioType.MCP)
        #         ],
        #         5: [ # Clamp middle sensor
        #             create_gpio(5, 'pressure_sensor1.1', dir=False, type=GpioType.MCP)
        #         ],
        #         6: [ # Clamp middle sensor
        #             create_gpio(6, 'pressure_sensor1.2', dir=False, type=GpioType.MCP)
        #         ],
        #         7: [ # Clamp middle sensor
        #             create_gpio(7, 'pressure_sensor1.3', dir=False, type=GpioType.MCP)
        #         ],

        #         5: [ # Clamp left sensor
        #             create_gpio(0 + 16, 'proximity_sensors5', dir=False, type=GpioType.MCP)
        #         ],
        #         6: [ # Clamp left sensor
        #             create_gpio(1 + 16, 'proximity_sensors6', dir=False, type=GpioType.MCP)
        #         ],
        #         7: [ # Clamp left sensor
        #             create_gpio(2 + 16, 'proximity_sensors7', dir=False, type=GpioType.MCP)
        #         ],
        #         8: [ # Clamp left sensor
        #             create_gpio(3 + 16, 'proximity_sensors8', dir=False, type=GpioType.MCP)
        #         ],
        #         9: [ # Clamp left sensor
        #             create_gpio(4 + 16, 'pressure_sensor2', dir=False, type=GpioType.MCP)
        #         ]
                
        #     }
        # )

        # # TODO: Check if numbers here are correct
        # self.axs = AX12Controller(
        #     [
        #         1, # Front elevator right arm
        #         2, # Front elevator left arm
        #         3, # Front right can arm
        #         4, # Front left can arm
        #     ]
        # )

        # self.i2c_servos_1 = I2CActsHandler({
        #     0: [I2CActType.Servo, 180], # Front pumps arm
        #     1: [I2CActType.Servo, 180], # Front Right
        #     2: [I2CActType.Servo, 180], # Front Mid-right
        #     3: [I2CActType.Servo, 180], # Front Mid-left
        #     4: [I2CActType.Servo, 180], # Front Left
        #     5: [I2CActType.Servo, 180], # Front Plank arm
        #     6: [I2CActType.Servo, 180], # Front Plank arm
        #     7: [I2CActType.Servo, 180], # Front Pilar arm
        #     8: [I2CActType.Servo, 180], # Front Pilar arm
        #     9: [I2CActType.Servo, 180],
        # }, frequency = 50, addr=0x40)

        # self.i2c_servos_2 = I2CActsHandler({
        #     0: [I2CActType.Servo, 180], # 
        #     1: [I2CActType.Servo, 180], # 
        #     2: [I2CActType.Servo, 180], # 
        #     3: [I2CActType.Servo, 180], # 
        #     4: [I2CActType.Servo, 180], # 
        #     5: [I2CActType.Servo, 180], # 
        #     6: [I2CActType.Servo, 180], # 
        #     7: [I2CActType.Servo, 180], # 
        #     8: [I2CActType.Servo, 180], # 
        #     9: [I2CActType.Servo, 180], # 
        # }, frequency = 50, addr=0x42)

        # self.i2c_mots = I2CMotorBoard({
        #     0: (I2CMotorBoardStepper, [0]),
        #     1: (I2CMotorBoardStepper, [1]),
        #     2: (I2CMotorBoardStepper, [2]),
        # })

        # self.pumps = PumpController({
        #     0: [
        #         create_gpio(8, 'pump1', dir=True, type=GpioType.MCP),
        #         create_gpio(10, 'pump1_ev', dir=True, type=GpioType.MCP),
        #     ],
        #     1: [
        #         create_gpio(9, 'pump2', dir=True, type=GpioType.MCP),
        #         create_gpio(11, 'pump2_ev', dir=True, type=GpioType.MCP),
        #     ],
        #     2: [
        #         create_gpio(8 + 16, 'pump3', dir=True, type=GpioType.MCP),
        #         create_gpio(10 + 16, 'pump3_ev', dir=True, type=GpioType.MCP),
        #     ],
        #     3: [
        #         create_gpio(9 + 16, 'pump4', dir=True, type=GpioType.MCP),
        #         create_gpio(11 + 16, 'pump4_ev', dir=True, type=GpioType.MCP),
        #     ],
        # })

        self.all_actuators = [
            # self.i2c_mots,
            # self.proximity_sensors,
            # self.recal_sensors,
            # self.axs,
            # self.i2c_servos_1,
            # self.i2c_servos_2,
            # self.pumps
        ]

        self.free()

        self.is_initialized = True
        for actuator in self.all_actuators:
            if not actuator.is_initialized():
                print ("[ACTUATORS] \n%s is not initialized" % (actuator.name))
                self.is_initialized = False

        if self.is_initialized:
            self.rgb_led_strip.start()
            self.enable()
            print("[ACTUATORS] Fully initialized")

        #self.bau_callback(event=self.bau.event, value=self.bau.read(), name='bau', id=self.bau.id)

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
        pass
        #self.magnets.free()
        #self.pumps.drops()
        # self.i2c_servos_1.free_all()
        # self.i2c_servos_2.free_all()
        #self.ax_free_all([1,2,3])

    # Disable Actuators
    @Service.action
    def disable(self):
        self.disabled.set()
        self.free()

    # Enable Actuators
    @Service.action
    def enable(self):
        #self.magnets.free()

        if not self.disabled.is_set():
            return

        if self.bau.read():
            self.disabled.clear()

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
    def recal_sensor_read(self, id, repetitions=10, raw=0):
        if self.recal_sensors[int(id)] == None:
            return None
        return self.recal_sensors[int(id)].read(repetitions=int(repetitions), raw=bool(int(raw)))

    #######
    # BAU #
    #######
    @Service.action
    def bau_read(self):
        return 1
        #return self.bau.read()

    def bau_callback(self, event, value, **kwargs):
        #print("BAU is {value}")
        #self.bau_led.write(value)
        self.publish(event=event, value=value, **kwargs)
        if value:
            self.enable()
        else:
            self.disable()

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
    # AXs #
    #######
    @if_enabled
    @Service.action
    def ax_move(self, id, pos):
        if self.axs[int(id)] == None:
            return RobotStatus.return_status(RobotStatus.Failed)
        self.axs[int(id)].move(int(pos))
        print(f"Move servo id {int(id)} to {pos}")
        return RobotStatus.return_status(RobotStatus.Done)

    @if_enabled
    @Service.action
    def axs_moves_ex(self, ids: list[int], positions: list[int], speeds: list[int] = None):
        for i, id in enumerate(ids):
            id = int(id)
            if self.axs[id] == None:
                continue

            if speeds is not None:
                self.axs[id].moving_speed(int(speeds[i]))

            position = int(positions[i])
            print(f"Move servo id {id} to {positions[i]}")
            self.axs[id].move(position)

        return RobotStatus.return_status(RobotStatus.Done)

    @Service.action
    def ax_free_all(self, ids):
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

    @Service.action
    def ax_get_load(self, id):
        if self.axs[int(id)] == None:
            return None
        v = self.axs[int(id)].get_present_load()
        if v > 1000:
            return v - 1000
        return v


    ##########
    # SERVOS #
    ##########
    @Service.action
    def servo_set_angle(self, id, angle):
        id = int(id)
        if id > 15:
            servos = self.i2c_servos_2
            id -= 16
        else:
            servos = self.i2c_servos_1

        if servos[int(id)] == None:
            return RobotStatus.return_status(RobotStatus.Failed)

        if servos[int(id)].set_angle(int(angle)):
            return RobotStatus.return_status(RobotStatus.Done)

        return RobotStatus.return_status(RobotStatus.Failed)

    @Service.action
    def servos_set_angles(self, ids, angles):
        ids = list(map(lambda x: int(x), ids))
        angles = list(map(lambda x: float(x), angles))

        for i, id in enumerate(ids):
            id = int(id)
            if id > 15:
                servos = self.i2c_servos_2
                id -= 16
            else:
                servos = self.i2c_servos_1

            if servos[id] == None:
                continue

            if not servos[id].set_angle(angles[i]):
                return RobotStatus.return_status(RobotStatus.Failed)

        return RobotStatus.return_status(RobotStatus.Done)

    ############
    # STEPPERS #
    ############
    @Service.action
    def stepper_goto(self, id, position, speed):
        speed = int(speed)
        if self.i2c_mots[int(id)] == None:
            return RobotStatus.return_status(RobotStatus.Failed)
        if self.i2c_mots[int(id)].goto(int(position), speed):
            return RobotStatus.return_status(RobotStatus.Done)
        return RobotStatus.return_status(RobotStatus.Failed)

    @Service.action
    def stepper_move(self, id, delta, speed):
        speed = int(speed)
        if self.i2c_mots[int(id)] == None:
            return RobotStatus.return_status(RobotStatus.Failed)
        if self.i2c_mots[int(id)].move(int(delta), speed):
            return RobotStatus.return_status(RobotStatus.Done)
        return RobotStatus.return_status(RobotStatus.Failed)

    @Service.action
    def stepper_home(self, id, speed):
        id = int(id)
        speed = int(speed)

        if self.i2c_mots[id] == None:
            return RobotStatus.return_status(RobotStatus.Failed)

        if self.i2c_mots[int(id)].home(speed):
            return RobotStatus.return_status(RobotStatus.Done)

        return RobotStatus.return_status(RobotStatus.Failed)

    #########
    # PUMPS #
    #########
    @Service.action
    def pumps_grab(self, ids: list[int]):
        _ids = []
        for id in ids:
            if self.pumps[int(id)] == None:
                continue
            _ids.append(int(id))

        if len(_ids) < 1:
            return RobotStatus.return_status(RobotStatus.Failed)

        self.pumps.gets(_ids)
        return RobotStatus.return_status(RobotStatus.Done)

    @if_enabled
    @Service.action
    def pumps_drop(self, ids: list[int], drop_delay: float):
        drop_delay = float(drop_delay)
        
        _ids = []
        for id in ids:
            if self.pumps[int(id)] == None:
                continue
            _ids.append(int(id))

        if len(_ids) < 1:
            return RobotStatus.return_status(RobotStatus.Failed)

        self.pumps.drops(_ids)
        if drop_delay > 0:
            sleep(drop_delay)
            self.pumps.stop_evs(_ids)
    
        return RobotStatus.return_status(RobotStatus.Done)

    """
    @if_enabled
    @Service.action
    def pumps_drop(self, ids: list[int]):
        _ids = []
        for id in ids:
            if self.pumps[int(id)] == None:
                continue
            _ids.append(int(id))

        if len(_ids) < 1:
            return RobotStatus.return_status(RobotStatus.Failed)

        self.pumps.drops(_ids)
        return RobotStatus.return_status(RobotStatus.Done)
    """

    @if_enabled
    @Service.action
    def pumps_stop_evs(self, ids: list[int]):
        _ids = []
        for id in ids:
            if self.pumps[int(id)] == None:
                continue
            _ids.append(int(id))

        if len(_ids) < 1:
            return RobotStatus.return_status(RobotStatus.Failed)

        self.pumps.stop_evs(_ids)
        return RobotStatus.return_status(RobotStatus.Done)

def main():
    actuators = Actuators()
    if not actuators.is_initialized:
        print('[ACTUATORS] Failed to initialize service')
        return
    actuators.run()


if __name__ == '__main__':
    main()
