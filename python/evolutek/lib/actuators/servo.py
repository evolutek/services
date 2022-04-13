from evolutek.lib.component import Component, ComponentsHolder
from adafruit_servokit import ServoKit

NB_CHANNEL = 16
KIT: ServoKit = None

class I2CServo(Component):
    def __init__(self, id_channel, frequency, actuation_range):
        self.frequency = frequency
        self.actuation_range = actuation_range
        self.channel = id_channel
        self.init = True
        super().__init__('Servo ', id_channel)

    def _initialize(self):
        KIT.servo[self.channel].frequency = self.frequency
        KIT.servo[self.channel].actuation_range = self.actuation_range
        KIT.servo[self.channel].angle = 180

    def set_angle(self, angle: int):
        KIT.servo[self.channel].angle = angle

class ServoHandler(ComponentsHolder):
    def __init__(self, sensors, frequency):
        self.frequency = frequency
        super().__init__('ServoHandler', sensors, I2CServo)

    def _initialize(self):
        global KIT
        try:
            KIT = ServoKit(channels=NB_CHANNEL, frequency=self.frequency)
        except:
            print('[%s] Failed to open Servo Handler' % self.name)
            return False
