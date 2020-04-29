import adafruit_tca9548a
import adafruit_tcs34725
import board
import busio

import time

class RGBSensors:

    def __init__(self, sensors):

        print('[RGB_SENSORS] Init RGB Sensors')

        i2c = busio.I2C(board.SCL, board.SDA)
        self.tca = adafruit_tca9548a.TCA9548A(i2c)

        self.sensors = {}

        for i in sensors:
            print('[RGB_SENSORS] Initializing RGB sensor %d' % i)
            if i < 1 and i > 8:
                print('[RGB_SENSORS] Bad RGB sensor number %d' % i)
            self.sensors[i] = adafruit_tcs34725.TCS34725(tca[i - 1])

        print('[RGB_SENSORS] RGB Sensors initialized')

    def read_sensor(i):
        print('[RGB_SENSORS] Reading RGB sensor %d' % i)
        if not i in self.sensors:
            print('[RGB_SENSORS] Bad RGB sensor  number %d' % i)
        return self.sensors.color_rgb_bytes
