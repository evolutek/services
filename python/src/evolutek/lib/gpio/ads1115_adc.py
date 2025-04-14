from adafruit_ads1x15.ads1115 import ADS1115, P0, P1, P2, P3
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
from evolutek.lib.gpio.gpio import Adc as BaseAdc


pins = [
    P0,
    P1,
    P2,
    P3
]


class Adc(BaseAdc):

    def __init__(self, id, name):

        super().__init__(id, name)

        if id < 0 or id > 3:
            raise Exception('[GPIO] Invalid pin ID for ads')

        self.chan = AnalogIn(ads, pins[id])

    # Read ADC
    def read(self):
        return self.chan.voltage


WAS_INITIALIZED = False
ads = None

# Return if the gpios was initialized
def wasInitialized():
    return WAS_INITIALIZED

# Initialize gpios
def initialize():
    global WAS_INITIALIZED
    global ads
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS1115(i2c, address=0x48)
        WAS_INITIALIZED = True
    except Exception as e:
        print('[GPIO] Failed to init ads: %s' % str(e))
        raise Exception('[GPIO] Failed to init ads')
