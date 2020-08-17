from threading import Lock, Thread
from time import sleep
import adafruit_vl53l0x
from adafruit_mcp230xx.mcp23017 import MCP23017
import digitalio
import board
import busio
import time
import neopixel_spi as neopixel


# TODO:
# - Exceptions management

# Default adress of Vl53L0X
DEFAULT_ADDRESS = 0x29
# See the bottom of the file for a list of coloration functions
DEFAULT_COLORATION_FUNCTION = 'sides'

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

    def __init__(self, nb_sensors, sensor_address=DEFAULT_ADDRESS,
            front_sensors=[], right_sensors=[], back_sensors=[], left_sensors=[],
            dist_far=600, dist_near=300, coloration_function=DEFAULT_COLORATION_FUNCTION,
            expander_address=0x20, leds_gpio=None, refresh=0.1, debug=False):

        self.dist_far = dist_far
        self.dist_near = dist_near

        self.coef = 255 / (self.dist_far / 2)

        # Init I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensors = []
        self.scan = [8191]*nb_sensors

        # Init MCP
        self.mcp = MCP23017(self.i2c, address=expander_address)

        self.nb_sensors = nb_sensors
        self.refresh = refresh
        self.debug = debug
        self.sensors_address = sensor_address

        self.front_sensors = front_sensors
        self.back_sensors = back_sensors
        self.right_sensors = right_sensors
        self.left_sensors = left_sensors
        self.obstacle_front = False
        self.obstacle_back = False
        self.obstacle_right = False
        self.obstacle_left = False
        self.is_robot = False

        # Init all sensors
        self.init_sensors(sensor_address)

        # Init led strip
        self.pixel = neopixel.NeoPixel(
                leds_gpio,
                self.nb_sensors,
                brightness=0.05)
        self.coloration_function = coloration_function

        self.lock = Lock()
        Thread(target=self.loop).start()


    def init_sensors(self, sensors_address):

        # Put all XSHUT pins to LOW
        for i in range(0, self.nb_sensors):
            self.mcp.get_pin(i).switch_to_output()
            self.mcp.get_pin(i).value = False

        # Init sensor one by one and change addresses
        for i in range(0, self.nb_sensors):
            self.mcp.get_pin(i).value = True
            self.sensors.append(adafruit_vl53l0x.VL53L0X(self.i2c))
            self.sensors[i].set_address(sensors_address + i + 1)


    def loop(self):
        while True:
            is_robot = False
            for side in ['front', 'back', 'right', 'left']:
                obstacle = False
                # Reads the sensors data
                for sensor_id in getattr(self, '%s_sensors' % side):
                    sensor_index = sensor_id - 1
                    dist = self.sensors[sensor_index].range
                    if self.debug:
                        pass
                        #print("Sensor {0} measured distance: {1}".format(
                            #sensor_id, self.sensors[sensor_index].range))
                    if dist < self.dist_near: obstacle = True
                    if dist < self.dist_far: is_robot = True
                    # If the obstacle is close, registers it
                    with self.lock:
                        setattr(self, 'obstacle_%s' % side, obstacle)
                        self.is_robot = is_robot
                        self.scan[sensor_index] = dist
            for side in ['front', 'back', 'right', 'left']:
                # Updates the LEDs
                for sensor_id in getattr(self, '%s_sensors' % side):
                    sensor_index = sensor_id - 1
                    # Sets the color of the pixel
                    dist = self.scan[sensor_index]
                    px = getattr(self, 'coloration_%s'%self.coloration_function)(
                            dist, side, sensor_id)
                    self.pixel[sensor_index] = px
                    #if self.debug: print("RGB: %i %i %i" % (px[0], px[1], px[2]))
            time.sleep(self.refresh)


    def get_scan(self):
        tmp = []
        with self.lock:
            tmp = self.scan
        return tmp


    def get_front(self):
        tmp = False
        with self.lock:
            tmp = self.obstacle_front
        return tmp


    def get_back(self):
        tmp = False
        with self.lock:
            tmp = self.obstacle_back
        return tmp


    def get_left(self):
        tmp = False
        with self.lock:
            tmp = self.obstacle_left
        return tmp


    def get_right(self):
        tmp = False
        with self.lock:
            tmp = self.obstacle_right
        return tmp


    def get_is_robot(self):
        tmp = False
        with self.lock:
            tmp = self.is_robot
        return tmp


    def coloration_continuous(self, dist, side, id):
        r = 255 - dist * self.coef
        g = 255 - abs(self.dist_far / 2 - dist) * self.coef
        b = 255 - (self.dist_far - dist) * self.coef
        return (int(r if r >= 0 else 0),
                int(g if g >= 0 else 0),
                int(b if b >= 0 else 0))


    def coloration_simple(self, dist, side, id):
        if dist > self.dist_far: return (0,255,0)
        elif dist < self.dist_near: return (255,0,0)
        else: return (255,135,0)


    def coloration_sides(self, dist, side, id):
        if getattr(self, 'obstacle_%s' % side): return (255,0,0)
        if self.is_robot: return (255,135,0)
        return (0,255,0)
