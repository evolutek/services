import adafruit_tca9548a
import adafruit_tcs34725
import board
import busio
import time

class TCS34725:

    def __init__(self, id):
        self.id = id

        try:
            self.sensor = adafruit_tcs34725.TCS34725(self.id - 1)
        except:
            raise RuntimeError("[TCS34725] Failed to initialize TCS34725 %d" % self.id)

        print('[TCS34725] TCS34725 %d initialized' % self.id)

    def __str__(self):
        # TODO
        return ""

    def read(self):
        return self.sensor.color_rgb_bytes


class RGBSensors:

    def __init__(self, sensors):

        print('[RGB_SENSORS] Init RGB Sensors')

        try:
            i2c = busio.I2C(board.SCL, board.SDA)
        except:
            raise RuntimeError("[RGB_SENSORS] Failed to open I2C bus")

        try:
            self.tca = adafruit_tca9548a.TCA9548A(i2c)
        except:
            raise RuntimeError("[RGB_SENSORS] Failed to initialize TCA")

        self.sensors = {}

        for id in sensors:
            if i < 1 or i > 8:
                print('[RGB_SENSORS] Bad RGB sensor number %d' % i)
                continue
            self.sensors[i] = TCS34725(id)

    def __str__(self):
        # TODO
        return ""

    def __iter__(self):
        return iter(self.sensors)

    def __getitem__(self, key):
        if key not in self.sensors:
            print('[RGB_SENSORS] RGB sensor %d not registered' % key)
            return None
        return self.sensors[key]
