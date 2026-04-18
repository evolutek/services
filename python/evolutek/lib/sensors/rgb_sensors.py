import adafruit_tca9548a
import adafruit_tcs34725
import board
import busio

from time import sleep

from evolutek.lib.component import Component, ComponentsHolder
from evolutek.lib.utils.color import Color

NB_CALIBRATE_MEASURES = 10

# Up -> More perturbations (more false positives)
# Down -> Better detection (more false negatives)
#SENSITIVITY = 1.25

class TCS34725(Component):

    def __init__(self, tca: adafruit_tca9548a.TCA9548A, id: int, channel: int):
        self.calibration = [1, 1, 1]
        self.sensor = None
        self.channel = channel
        self.tca = tca
        super().__init__('TCS34725', id)

    def _initialize(self):
        if self.channel < 0 or self.channel > 7:
            print('[%s] %s bad channel %d' % (self.name, self.name, self.channel))
            return False

        try:
            self.sensor = adafruit_tcs34725.TCS34725(self.tca[self.channel])
            self.sensor.integration_time = 100
            self.sensor.gain = 4
            self.sensor.active = True
        except Exception as e:
            print('[%s] Failed to initialize TCS34725 %d: %s' % (self.name, self.id, str(e)))
            return False
        return True

    def calibrate(self):
        for i in range(NB_CALIBRATE_MEASURES):
            rgb = self.sensor.color_rgb_bytes
            self.calibration[0] += rgb[0]
            self.calibration[1] += rgb[1]
            self.calibration[2] += rgb[2]
            sleep(0.1)
        self.calibration[0] /= NB_CALIBRATE_MEASURES
        self.calibration[1] /= NB_CALIBRATE_MEASURES
        self.calibration[2] /= NB_CALIBRATE_MEASURES
        # print('Setup: R = %i - G = %i - B = %i' % (self.calibration[0],self.calibration[1],self.calibration[2]))

    def read(self) -> tuple[float, float, float]:
        if not self.is_initialized:
            print('[%s] %s %d not initialized' % (self.name, self.name, self.id))
            return None

        rgb = self.sensor.color_rgb_bytes
        values = [rgb[0] / self.calibration[0], rgb[1] / self.calibration[1], rgb[2] / self.calibration[2]]

        return values

    # def detect(self, palette: list[Color]) -> Color:
    #     values = self.read()

    #     index = values.index(max(values))

    #     if rgb[index] < self.calibration[index] * SENSITIVITY:
    #         return Color.Unknown

    #     res = [Color.Red, Color.Green, Color.Blue][index]
    #     if res == Color.Blue: return Color.Green
    #     return res

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

class RGBSensors(Component): #(ComponentsHolder):

    def __init__(self, sensors: dict[int, int], address: int = 0x70):

        # if isinstance(sensors, list):
        #     tmp = {}
        #     for sensor in sensors:
        #         tmp[sensor] = [sensor]
        #     sensors = tmp

        self.address = address
        self.sensors = sensors
        self.tca = None
        self.components: dict[int, TCS34725] = {}

        super().__init__('RGB sensors', 0)

    def _initialize(self):
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
        except:
            print('[%s] Failed to open I2C bus' % self.name)
            return False

        try:
            self.tca = adafruit_tca9548a.TCA9548A(i2c, address=self.address)
        except:
            print('[%s] Failed to initialize TCA' % self.name)
            return False

        for id, channel in self.sensors.items():
            self.components[id] = TCS34725(self.tca, id, channel)

        return True

    def __getitem__(self, key: int):
        if not isinstance(key, int):
            print('[%s] bad key id' % self.name)
            return None
        if key not in self.components:
            print('[%s] %s %d not registered' % (self.name, self.name, key))
            return None
        return self.components[key]
