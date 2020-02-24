from threading import Lock, Thread
from time import sleep

# TODO:
# - Replace FIXME
# - Attribute a placement to sensors (front, back, sides)

# Default adress of Vl53L0X
DEFAULT_ADDRESS = 0x29

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

class Mdb():

    def __init__(self, nb_sensors, sensor_address=0x30, expander_address=0x20, leds_gpio=None, refresh=0.1):
        # FIXME
        self.nb_sensors = nb_sensors

    def loop(self):
        # FIXME
        pass

    def get_scan(self):
        # FIXME
        return []

    def __str__(self):
        #FIXME
        pass
