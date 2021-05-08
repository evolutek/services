import adafruit_tca9548a
import adafruit_tcs34725
import board
import busio
import time

from enum import Enum
from time import sleep

from evolutek.lib.component import Component, ComponentsHolder

TCA = None
CALLIBRATE = 10
SENSITIVITY = 1.2

class Colors(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    NONE = None

class TCS34725(Component):

    def __init__(self, id, channel):
        self.callibration = [0, 0, 0]
        self.sensor = None
        self.channel = channel
        super().__init__('TCS34725', id)

    def _initialize(self):
        if self.id < 1 or self.id > 8:
            print('[%s] %s bad id %d' % (self.name, self.name, self.id))
            return False

        try:
            self.sensor = adafruit_tcs34725.TCS34725(TCA[self.channel - 1])
        except Exception as e:
            print('[%s] Failed to initialize TCS34725 %d: %s' % (self.name, self.id, str(e)))
            return False
        return True

    def setup(self):
        for i in range(CALLIBRATE):
            rgb = self.sensor.color_rgb_bytes
            self.callibration[0] += rgb[0]
            self.callibration[1] += rgb[1]
            self.callibration[2] += rgb[2]
            sleep(0.1)
        self.callibration[0] /= CALLIBRATE
        self.callibration[1] /= CALLIBRATE
        self.callibration[2] /= CALLIBRATE
        # print('Setup: R = %i - G = %i - B = %i' % (self.callibration[0],self.callibration[1],self.callibration[2]))

    def isMajorChanges(self, rgb):
        # print('R = %i - G = %i - B = %i' % (rgb))
        if (rgb[0] >= self.callibration[0] * SENSITIVITY) \
            or (rgb[1] >= self.callibration[1] * SENSITIVITY) \
            or (rgb[2] >= self.callibration[2] * SENSITIVITY):
            return True
        return False

    def read(self):
        if not self.is_initialized:
            print('[%s] %s %d not initialized' % (self.name, self.name, self.id))
            return None
        rgb = self.sensor.color_rgb_bytes
        r, g, b = rgb[0], rgb[1], rgb[2]
        colorByte = max(r, g, b)
        if not self.isMajorChanges(rgb):
            return Colors.NONE
        elif colorByte == r:
            return Colors.RED
        elif colorByte == g:
            return Colors.GREEN
        else:
            return Colors.BLUE

    def __str__(self):
        s = "----------\n"
        s += "TCS34725: %d\n" % self.id
        s += "Channel: %d\n" % self.channel
        s += "Color: %s\n" % str(self.read())
        s += "---------"
        return s

class RGBSensors(ComponentsHolder):

    def __init__(self, sensors):

        if isinstance(sensors, list):
            tmp = {}
            for sensor in sensors:
                tmp[sensor] = [sensor]
            sensors = tmp

        super().__init__('RGB sensors', sensors, TCS34725)

    def _initialize(self):
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
        except:
            print('[%s] Failed to open I2C bus' % self.name)
            return False

        try:
            global TCA
            TCA = adafruit_tca9548a.TCA9548A(i2c)
        except:
            print('[%s] Failed to initialize TCA' % self.name)
            return False

        return True

    def read_all_sensors(self):
        results = {}
        for sensor in self.components:
            results[sensor] = self.components[sensor].read()
        return results
