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
from evolutek.lib.actuators.magnet import MagnetController
from evolutek.lib.indicators.ws2812b import WS2812BLedStrip, LightningMode
from evolutek.lib.sensors.proximity_sensors import ProximitySensors
from evolutek.lib.sensors.recal_sensors import RecalSensors
from evolutek.lib.sensors.rgb_sensors import RGBSensors, TCS34725
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

        #left_recal_points = json.loads(self.cs.config.get(ROBOT, "left_recal_points"))
        #right_recal_points = json.loads(self.cs.config.get(ROBOT, "right_recal_points"))

        #self.recal_sensors = RecalSensors(
        #    {
        #        1: [create_adc(0, "recal1", type=AdcType.ADS)],
        #        2: [create_adc(1, "recal2", type=AdcType.ADS)]
        #    }
        #)
        #self.recal_sensors[1].calibrate(left_recal_points)
        #self.recal_sensors[2].calibrate(right_recal_points)

        self.bau = create_gpio(20, 'bau', event='%s-bau' % ROBOT, dir=False, type=GpioType.RPI)
        #self.bau_led = create_gpio(20, 'bau led', dir=True, type=GpioType.RPI)
        self.bau.auto_refresh(refresh=0.05, callback=self.bau_callback)
        #self.bau_callback(event=self.bau.event, value=self.bau.read(), name='bau', id=self.bau.id)

        #self.rgb_led_strip = WS2812BLedStrip(42, board.D12, 36, 0.25)

        self.rgb_led_strip = WS2812BLedStrip(42, board.D12, 36, 1.0)
    
        try:
            self.match_color_callback(self.cs.match.get_color())
        except Exception as e:
            print('[ACTUATORS] Failed to set color: %s' % str(e))

        self.axs = AX12Controller([11,12,13,14,21,22,23,24,31,32,33,34])
        self.axs_speed = 300
        for ax in self.axs:
            self.ax_set_speed(ax, self.axs_speed)

        self.i2c_serv_1 = I2CActsHandler({
            15 : [I2CActType.Servo, 180], # 113
            14 : [I2CActType.Servo, 205, 500, 2800], #112
            13 : [I2CActType.Servo, 205, 500, 2800], # 111

            10 : [I2CActType.Servo, 205, 500, 2800], # 121
            9 : [I2CActType.Servo, 205, 500, 2800], # 122
            #8 : [I2CActType.Servo, 205, 500, 2800],

            #6 : [I2CActType.Servo, 205, 500, 2800],
            5 : [I2CActType.Servo, 205, 500, 2800], # 131
            4 : [I2CActType.Servo, 205, 500, 2800], # 132

            3 : [I2CActType.Servo, 180], # 143
            2 : [I2CActType.Servo, 205, 500, 2800], # 142
            1 : [I2CActType.Servo, 205, 500, 2800], # 141


            12 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 1
            11 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 2
            7 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 3
            0 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 4
        }, frequency=333, addr=0x40)

        self.i2c_serv_2 = I2CActsHandler({
            15 : [I2CActType.Servo, 180], # 113
            14 : [I2CActType.Servo, 205, 500, 2800], # 112
            13 : [I2CActType.Servo, 205, 500, 2800], # 111

            10 : [I2CActType.Servo, 205, 500, 2800], # 121
            9 : [I2CActType.Servo, 205, 500, 2800], # 122
            #8 : [I2CActType.Servo, 205, 500, 2800],

            #6 : [I2CActType.Servo, 205, 500, 2800],
            5 : [I2CActType.Servo, 205, 500, 2800], # 131
            4 : [I2CActType.Servo, 205, 500, 2800], # 132

            3 : [I2CActType.Servo, 180], # 143
            2 : [I2CActType.Servo, 205, 500, 2800], # 142
            1 : [I2CActType.Servo, 205, 500, 2800], # 141


            12 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 1
            11 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 2
            7 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 3
            0 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 4
        }, frequency=333, addr=0x41)

        self.i2c_serv_3 = I2CActsHandler({
            15 : [I2CActType.Servo, 180], # 113
            14 : [I2CActType.Servo, 205, 500, 2800], # 112
            13 : [I2CActType.Servo, 205, 500, 2800], # 111

            10 : [I2CActType.Servo, 205, 500, 2800], # 121
            9 : [I2CActType.Servo, 205, 500, 2800], # 122
            #8 : [I2CActType.Servo, 205, 500, 2800],

            #6 : [I2CActType.Servo, 205, 500, 2800],
            5 : [I2CActType.Servo, 205, 500, 2800], # 131
            4 : [I2CActType.Servo, 205, 500, 2800], # 132

            3 : [I2CActType.Servo, 180], # 143
            2 : [I2CActType.Servo, 205, 500, 2800], # 142
            1 : [I2CActType.Servo, 205, 500, 2800], # 141


            12 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 1
            11 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 2
            7 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 3
            0 : [I2CActType.Servo, 1, 0, 2048], # led for sensor 4
        }, frequency=333, addr=0x42)

        self.sensors = RGBSensors({
            1: [3],  # id, channel
            2: [2],
            3: [0],
            4: [1],
        })
        self.all_actuators = [
            self.i2c_serv_3,
            self.i2c_serv_2,
            self.i2c_serv_1,
            self.sensors,
            self.axs,
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

        self.bau_callback(event=self.bau.event, value=self.bau.read(), name='bau', id=self.bau.id)

    def stop(self):
        print("[ACTUATORS] Stopping")
        self.rgb_led_strip.stop()
        self.free()

    @Service.action
    def print_status(self):
        for actuators in self.all_actuators:
            print(actuators)

    @Service.action
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
        self.ax_free_all([11,12,13,14,21,22,23,24,31,32,33,34])
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

        for ax in self.axs:
            self.ax_set_speed(ax, self.axs_speed)


        if self.bau.read():
            self.disabled.clear()

      #      self.i2c_acts.init_escs()
            


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

    #################
    # COLOR SENSORS #
    #################
    @Service.action
    def color_enable(self, id, en = 1):
        id = int(id) - 1
        if id > 31:
            i2c_serv = self.i2c_serv_3
            id -= 32
        elif id > 15:
            i2c_serv = self.i2c_serv_2
            id -= 16
        else:
            i2c_serv = self.i2c_serv_1

        pca_channels = [12, 11, 7, 0]

        if i2c_serv[pca_channels[id]] == None:
            return RobotStatus.return_status(RobotStatus.Failed)

        if not i2c_serv[pca_channels[id]].set_angle(int(en)):
            return RobotStatus.return_status(RobotStatus.Failed)

        return RobotStatus.return_status(RobotStatus.Done)
    

    @Service.action
    def color_read(self, id):
        # led is controlled by the same PCA as the servos, so we need to enable the right channel on it before reading the sensor
        id = int(id)

        if self.sensors[id] == None:
            return None

        self.color_enable(id, 1)

        ret = self.sensors[id].read()

        self.color_enable(id, 0)

        return ret

    #######
    # BAU #
    #######
    @Service.action
    def bau_read(self):
        return self.bau.read()

    def bau_callback(self, event, value, **kwargs):
        #self.bau_led.write(value)
        self.publish(event=event, value=value, **kwargs)
        if value:
           self.enable()
        else:
            self.free()
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

    ##########
    # SERVOS #
    ##########
    @Service.action
    def servo_set_angle(self, id, angle):
        id = int(id)
        if id > 31:
            i2c_serv = self.i2c_serv_3
            id -= 32
        elif id > 15:
            i2c_serv = self.i2c_serv_2
            id -= 16
        else:
            i2c_serv = self.i2c_serv_1

        if i2c_serv[id] == None:
            return RobotStatus.return_status(RobotStatus.Failed)

        if i2c_serv[id].set_angle(int(angle)):
            return RobotStatus.return_status(RobotStatus.Done)

        return RobotStatus.return_status(RobotStatus.Failed)

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
    def stepper_home(self, id):
        if self.i2c_mots[int(id)] == None:
            return RobotStatus.return_status(RobotStatus.Failed)
        if self.i2c_mots[int(id)].home():
            return RobotStatus.return_status(RobotStatus.Done)
        return RobotStatus.return_status(RobotStatus.Failed)
    
    ###########
    # MAGNETS #
    ###########
    #@Service.action
    #def magnets_on(self, ids: list[int]):
    #    _ids = []
    #    for id in ids:
    #        if self.magnets[int(id)] == None:
    #            continue
    #        _ids.append(int(id))

    #    if len(_ids) < 1:
    #        return RobotStatus.return_status(RobotStatus.Failed)

    #    self.magnets.on(_ids)
    #    return RobotStatus.return_status(RobotStatus.Done)

    #@if_enabled
    #@Service.action
    #def magnets_off(self, ids: list[int]):
    #    _ids = []
    #    for id in ids:
    #        if self.magnets[int(id)] == None:
    #            continue
    #        _ids.append(int(id))

    #    if len(_ids) < 1:
    #        return RobotStatus.return_status(RobotStatus.Failed)

    #    self.magnets.off(_ids)
    #    return RobotStatus.return_status(RobotStatus.Done)

    #########
    # PUMPS #
    #########
    @Service.action
    def pumps_on(self, ids: list[int]):
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
    def pumps_off(self, ids: list[int]):
        _ids = []
        for id in ids:
            if self.pumps[int(id)] == None:
                continue
            _ids.append(int(id))

        if len(_ids) < 1:
            return RobotStatus.return_status(RobotStatus.Failed)

        self.pumps.drops(_ids)
        return RobotStatus.return_status(RobotStatus.Done)


    @if_enabled
    @Service.action
    def grab_seq(self):
        # setup
        self.ax_move(2, 0)
        self.servo_set_angle(1, 0)
        self.servo_set_angle(0, 0)
        sleep(3)
        self.servo_set_angle(1, 180)
        sleep(1)
        self.ax_move(2, 0)
        sleep(1)
        self.ax_move(2, 200)
        sleep(1)
        self.servo_set_angle(0, 180)
        sleep(2)
        self.ax_move(2, 0)
        return
        sleep(2) # grab
        self.servo_set_angle(1, 0)
        self.servo_set_angle(0, 180)
        sleep(1) # lever
        #self.ax_move(1, 263)
        #self.stepper_move(0, 800, 100000)
        sleep(1) # retourner
        self.servo_set_angle(1, 180)
        sleep(2)
        #self.ax_move(1, 568)
        self.servo_set_angle(0, 0)
        sleep(2)
        #self.stepper_move(0, -800, 100000)
        sleep(2)
        self.servo_set_angle(0, 0)



def main():
    actuators = Actuators()
    if not actuators.is_initialized:
        print('[ACTUATORS] Failed to initialize service')
        return
    actuators.run()


if __name__ == '__main__':
    main()
