import adafruit_tca9548a
import adafruit_tcs34725
import board
import busio
from enum import Enum
from time import sleep

from evolutek.lib.component import Component, ComponentsHolder
from evolutek.lib.utils.color import RGBColor, Color

TCA = None
CALIBRATION_NB_VALUES = 10
DELTA_FOR_COLOR = 50

class TCS34725(Component):

    def __init__(self, id, channel, color_to_detect=None):
        self.calibration = RGBColor(0, 0, 0)
        self.sensor = None
        self.channel = channel
        self.color_to_detect = color_to_detect
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

    def calibrate(self):
        calibration = []
        for i in range(CALIBRATION_NB_VALUES):
            calibration.append(RGBColor.from_tupple(self.sensor.color_rgb_bytes))
            sleep(0.1)
        self.calibration = RGBColor.mean(calibration)
        print(f"[{self.name}] Sensor {self.id} calibrated with {self.calibration}")

    def read(self):
        rgb = RGBColor.from_tupple(self.sensor.color_rgb_bytes)
        rgb -= self.calibration
        color = Color.get_closest_color(rgb, self.color_to_detect if self.color_to_detect is not None else Color.__members__.values())

        print(f"[{self.name}] Sensor {self.id} detect color {color.name} with {color.value}")
        return color

    def __str__(self):
        s = "----------\n"
        s += "TCS34725: %d\n" % self.id
        s += "Channel: %d\n" % self.channel
        s += "Color: %s\n" % self.read().name
        s += "----------"
        return s

    def __dict__(self):
        return {
            "name": self.name,
            "id": self.id,
            "channel": self.channel,
            "color": self.read().name
        }

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
