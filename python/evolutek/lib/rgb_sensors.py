import adafruit_tca9548a
import adafruit_tcs34725
import board
import busio
import time

class RGBSensors:

    def __init__(self, sensors, sample_size):

        print('[RGB_SENSORS] Init RGB Sensors')

        i2c = busio.I2C(board.SCL, board.SDA)
        self.tca = adafruit_tca9548a.TCA9548A(i2c)

        self.sensors = {}
        self.calibrations = {}

        for i in sensors:
            print('[RGB_SENSORS] Initializing RGB sensor %d' % i)
            if i < 1 or i > 8:
                print('[RGB_SENSORS] Bad RGB sensor number %d' % i)
                continue
            self.sensors[i] = adafruit_tcs34725.TCS34725(self.tca[i - 1])
            self.calibration(i, sample_size)

        print('[RGB_SENSORS] RGB Sensors initialized')

    def __str__(self):
        s = '---RGB Sensors:---\n'
        for key in self.sensors:
            s += 'sensor %d with calibration %s\n' % (key, self.calibrations[i])
        return s

    def calibration(self, i, sample_size):
        print('[RGB_SENSORS] Calibrating RGB sensor %d' % i)
        if not i in self.sensors:
            print('[RGB_SENSORS] Bad RGB sensor number %d' % i)
            return None

        r, g, b = 0, 0, 0
        for i in range(sample_size):
            rgb = self.read_sensor(i)
            r += rgb[0]
            g += rgb[1]
            b += rgb[2]
            time.sleep(0.1)

        self.calibrations[i] = (r // sample_size, g // sample_size, b // sample_size)

    def read_sensor(self, i):
        print('[RGB_SENSORS] Reading RGB sensor %d' % i)
        if not i in self.sensors:
            print('[RGB_SENSORS] Bad RGB sensor  number %d' % i)
            return None
        return self.sensors[i].color_rgb_bytes
