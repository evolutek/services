from threading import Lock, Thread
from time import sleep
import adafruit_vl53l0x
from adafruit_mcp230xx.mcp23017 import MCP23017
import digitalio
import board
import busio
import time
import neopixel

# TODO:
# - Replace FIXME
# - Attribute a placement to sensors (front, back, sides)

# Default adress of Vl53L0X
DEFAULT_ADDRESS = 0x29
MAX_DIST = 1000

# MDB Class

# __init__(nb_sensors, sensor_address, expander_address, leds_gpio, refresh):
#   - nb_sensors        : Number of VL53L0X
#   - sensor_address    : Address of the first sensors
#   - expander_address  : Address of the Gpio Expander
#   - leds_gpio         : Gpio of the led strip
#   - refresh           : Refresh of the loop
# Sensors wil be between sensor_address and sensor_address + nb_sensors - 1
# Will init the gpio expanders, sensors and led_strip
# Will launch a thread for the loop

# loop():
# Loop to get scan with a certain refresh
# Must run in a thread
# Will use a lock to update the data of the class

# get_scan:
#   Will return a scan (a list of measurement)

# __str__():
# Return a string of the status of the MDB

class Mdb:

    def __init__(self, nb_sensors, sensor_address=0x29, front_led=[16, 1, 2, 3], right_led=[4, 5, 6, 7], back_led=[8, 9, 10, 11],
                 left_led=[12, 13, 14, 15], expander_address=0x20, leds_gpio=None, refresh=0.1, debug=0):
        self.coef = 255 / (MAX_DIST / 2)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensors = []
        self.scan = []
        self.mcp = MCP23017(self.i2c, address=expander_address)
        self.nb_sensors = nb_sensors
        self.sleep = refresh
        self.pixel = None
        self.debug = debug
        self.sensors_address = sensor_address
        self.position = {"back": (False, back_led), "front": (False, front_led),  "right": (False, right_led), "left": (False, left_led)}
        self.init_sensor()
        self.lock = Lock()
        Thread(target=self.loop).run()

    def init_sensor(self):
        for i in range(0, self.nb_sensors + 1):
            self.mcp.get_pin(i + 8).switch_to_output()

        for i in range(0, self.nb_capteur + 1):
            print("INIT_Sensor: {0}".format(i + 1))
            self.mcp.get_pin(i + 8).value = True
            self.sensors.append(adafruit_vl53l0x.VL53L0X(self.i2c, address=0x29))
            self.sensors[i].set_address(0x29 + i + 1)
        self.pixel = neopixel.NeoPixel(board.D27, self.nb_capteur, brightness=10)

    def loop(self):
        while True:
            for i in range(0, self.nb_sensors + 1):
                self.dist = self.sensors[i].range
                if self.dist > MAX_DIST:
                    self.pixel[i] = (0,0,0)
                elif self.dist > 500:
                    if i in self.position["front"][1]:
                        self.position["front"][0] = True
                    elif i in self.position["right"][1]:
                        self.position["right"][0] = True
                    elif i in self.position["back"][1]:
                        self.position["back"][0] = True
                    else:
                        self.position["left"] = True

                    r = 255 - self.dist * self.coef
                    g = 255 - abs(MAX_DIST / 2 - self.dist) * self.coef
                    b = 255 - (MAX_DIST - self.dist) * self.coef
                    self.pixel[i] = (int(r if r >= 0 else 0),
                                     int(g if g >= 0 else 0),
                                     int(b if b >= 0 else 0))
                else:
                    r = 255 - self.dist * self.coef
                    g = 255 - abs(MAX_DIST / 2 - self.dist) * self.coef
                    b = 255 - (MAX_DIST - self.dist) * self.coef
                    self.pixel[i] = (int(r if r >= 0 else 0),
                                     int(g if g >= 0 else 0),
                                     int(b if b >= 0 else 0))
                if self.debug != 0:
                    print("Range: {0}".format(self.sensors[i].range))
                with self.lock:
                    self.scan[i] = self.sensors[i].range
            time.sleep(self.sleep)

    def get_scan(self):
        with self.lock:
            return self.scan

    def __str__(self):
        return ""
