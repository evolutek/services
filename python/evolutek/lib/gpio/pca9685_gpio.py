from evolutek.lib.gpio.gpio import Gpio as BaseGpio
from evolutek.lib.utils.boolean import get_boolean

from evolutek.lib.actuators.i2c_acts import I2CAct


class PcaGpio(BaseGpio):

    def __init__(self, ch: I2CAct):
        super().__init__(ch.id, ch.name, dir=True)
        self.ch = ch

    # Read the gpio
    def read(self):
        raise NotImplementedError("PcaGpio.read")

    # Write on the gpio
    def write(self, value):
        self.ch.fraction = 1 if get_boolean(value) else 0
