from adafruit_mcp230xx.mcp23017 import MCP23017
import board
import busio
from digitalio import Direction

from evolutek.lib.gpio.gpio import Edge, Gpio as BaseGpio
from evolutek.lib.utils.boolean import get_boolean

class Gpio(BaseGpio):

    def __init__(self, id, name, dir=True, event=None, edge=Edge.BOTH, default_value=False):

        super().__init__(id, name, dir, event, edge, default_value)

        if id < 0 or id > 31:
            raise Exception('[GPIO] Invalid pin ID for mcp')

        self.pin = mcp1.get_pin(id) if id < 16 else mcp2.get_pin(id - 16)
        if dir:
            self.pin.direction = Direction.OUTPUT
            self.pin.value = default_value
        else:
            self.pin.direction = Direction.INPUT

    # Read the gpio
    def read(self):
        self.last_value = self.pin.value
        return self.last_value

    # Write on the gpio
    def write(self, value):
        if not self.dir:
            return

        self.pin.value = get_boolean(value)


WAS_INITIALIZED = False
mcp1 = None
mcp2 = None

# Return if the gpios was initialized
def wasInitialized():
    return WAS_INITIALIZED

# Initialize gpios
def initialize():
    global WAS_INITIALIZED
    global mcp1
    global mcp2
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        mcp1 = MCP23017(i2c, address=0x20)
        mcp2 = MCP23017(i2c, address=0x21)
        WAS_INITIALIZED = True
    except Exception as e:
        print('[GPIO] Failed to init mcp: %s' % str(e))
        raise Exception('[GPIO] Failed to init mcp')
