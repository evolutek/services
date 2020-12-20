from threading import Lock
from time import sleep
import board
import busio

TEENSY = 0x42

REQ_COLOR = b'c'
REQ_LEDSMODE = b'l'
REQ_CHANGETYPE = b't'
REQ_ENABLESCAN = b'e'
REQ_ERROR = b'r'
REQ_BRIGHTNESS = b'b'
REQ_NEAR = b'n'
REQ_FAR = b'f'

RCV_SCAN = b'\x00'
RCV_ZONES = b'\x01'

LEDS_YELLOW = b'\x00'
LEDS_BLUE = b'\x01'

LEDS_DIST = b'\x00'
LEDS_ZONES = b'\x01'
LEDS_LOADING = b'\x02'
LEDS_DISABLED = b'\x03'

# Class to communicate with MDB using I2C
class Mdb:

    def __init__(self):

        # Init communication on I2C bus
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.send(REQ_ERROR + b'\x00')
        except Exception as e:
            print("[MDB] ERROR couldn't initialise i2c bus between Teensy and RaspberryPI")
            raise(e)

    # Send a msg to MDB usong I2C
    def send(self, msg):
        try: self.i2c.writeto(TEENSY, msg)
        except: print("[MDB] ERROR while sending message: " + str(msg))


    # Get a scan of the MDB using I2C
    def get_scan(self):
        self.send(REQ_CHANGETYPE + RCV_SCAN)
        buf = bytearray(b'\xff' * 32)
        res = [65535] * 16
        try:
            self.i2c.readfrom_into(TEENSY, buf)
            for i in range(16): res[i] = buf[i*2] * buf[i*2+1]
        except:
            print("[MDB] ERROR while reading scan data")
        return res


    # Set the debug mode of the MDB
    # Possible values: 0: Distances, 1: Zones, 2: Loading, 3: Disabled
    def set_debug_mode(self, mode):
        if not 0 <= mode <= 3:
            print('[MDB] Unknown debug mode ' + str(mode))
        self.send(REQ_LEDSMODE + bytes([mode]))


    # Set the color of the MDB
    # True: changes color to yellow; False: changes color to blue
    def set_color(self, to_yellow):
        self.send(REQ_COLOR + (LEDS_YELLOW if to_yellow else LEDS_BLUE))

    # Get the areas flags of the MDB
    def get_zones(self):

        self.send(REQ_CHANGETYPE + RCV_ZONES)
        buf = bytearray(b'\x02' * 3)
        try:
            self.i2c.readfrom_into(TEENSY, buf)
        except:
            print("[MDB] ERROR while reading zones data")

        err = False
        for i in range(len(buf)):
            if buf[i] not in [0, 1]: err = True
        if err: print("[MDB] ERROR: get_zones received erroneous data! " + str(buf))

        return {
                'front': buf[0] == 1,
                'back': buf[1] == 1,
                'is_robot': buf[2] == 1
               }

    # Get the front area flag
    def get_front(self):
        return self.get_zones()['front']
    
    # Get the back area flag
    def get_back(self):
        return self.get_zones()['back']
    
    # Get if whether a robot is near our robot
    def get_is_robot(self):
        return self.get_zones()['is_robot']

    # Set enable flag of MDB
    def set_enabled(self, enabled):
        self.send(REQ_ENABLESCAN + (b'\x01' if enabled else b'\x00'))

    # Enable MDB
    def enable(self, debug_mode=1):
        self.set_enabled(True)
        self.set_debug_mode(debug_mode)

    # Disable MDB
    def disable(self):
        self.set_enabled(False)
        self.set_debug_mode(3)

    # Set brihtness of MDB
    def set_brightness(self, brightness):
        if not 0 <= brightness <= 255:
            print('[MDB] Invalid brightness value ' + str(mode))
        self.send(REQ_BRIGHTNESS + bytes([brightness]))

    # Set error mode
    def error_mode(self, enabled=True):
        self.send(REQ_ERROR + (b'\x01' if enabled else b'\x00'))


    # Sets the near distance (for front and back flags). In millimeters
    def set_near(self, distance):
        if not 0 <= distance <= 65535:
            print('[MDB] Invalid distance value ' + str(mode))
        self.send(REQ_NEAR + bytes([distance//256, distance%256]))


    # Sets the far distance (for the is_robot flag). In millimeters
    def set_far(self, distance):
        if not 0 <= distance <= 65535:
            print('[MDB] Invalid distance value ' + str(mode))
        self.send(REQ_FAR + bytes([distance//256, distance%256]))
