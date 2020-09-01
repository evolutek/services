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

RCV_SCAN = b'\x00'
RCV_ZONES = b'\x01'

LEDS_YELLOW = b'\x00'
LEDS_BLUE = b'\x01'

LEDS_DIST = b'\x00'
LEDS_ZONES = b'\x01'
LEDS_LOADING = b'\x02'
LEDS_DISABLED = b'\x03'

class Mdb:

    def __init__(self, debug=False):
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
        except Exception as e:
            print("MDB: ERROR couldn't initialise i2c bus between Teensy and RaspberryPI")
            raise(e)


    def get_scan(self):
        self.i2c.writeto(TEENSY, REQ_CHANGETYPE + RCV_SCAN)
        buf = bytearray(b'\x00' * 16)
        self.i2c.readfrom_into(TEENSY, buf)
        return list(buf)


    # Possible values: 0: Distances, 1: Zones, 2: Loading, 3: Disabled
    def set_debug_mode(self, mode):
        self.i2c.writeto(TEENSY, REQ_LEDSMODE + bytes([mode]))

    
    # True: changes color to yellow; False: changes color to blue
    def change_color(self, to_yellow):
        self.i2c.writeto(TEENSY, REQ_COLOR + (LEDS_YELLOW if to_yellow else LEDS_BLUE))


    def get_zones(self):
        
        self.i2c.writeto(TEENSY, REQ_CHANGETYPE + RCV_ZONES)
        buf = bytearray(b'\x02' * 3)
        self.i2c.readfrom_into(TEENSY, buf)
        
        err = False
        for i in buf:
            if i not in [0, 1]:
                err = True
                buf[i] = 0
        if err: print("ERROR: get_zones received erroneous data!" + str(buf))
        
        return {
                'front': buf[0] != 0,
                'back': buf[1] != 0,
                'is_robot': buf[2] != 0
               }


    def get_front(self):
        return self.get_zones()['front']
    def get_back(self):
        return self.get_zones()['back']
    def get_is_robot(self):
        return self.get_zones()['is_robot']

    
    def set_enabled(self, enabled):
        self.i2c.writeto(TEENSY, REQ_ENABLESCAN + (b'\x01' if enabled else b'\x00'))


    def enable(self, debug_mode=1): 
        self.set_enabled(True)
        self.set_debug_mode(debug_mode)
   

    def disable(self): 
        self.set_enabled(False)
        self.set_debug_mode(3)


    def set_brightness(self, brightness):
        self.i2c.writeto(TEENSY, REQ_BRIGHTNESS + bytes([brightness]))


    def error_mode(self):
        self.i2c.writeto(TEENSY, REQ_ERROR)
