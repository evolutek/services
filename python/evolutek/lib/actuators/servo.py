from evolutek.lib.component import Component, ComponentsHolder
from adafruit_servokit import ServoKit

NB_CHANNEL = 16
KIT: ServoKit = None

class I2CServo(Component):
    def __init__(self, id_channel, frequency, actuation_range=180):
        self.frequency = frequency
        self.actuation_range = actuation_range
        self.channel = id_channel
        self.init = True
        super().__init__('Servo ', id_channel)

    def _initialize(self):
        KIT.servo[self.channel].frequency = self.frequency
        KIT.servo[self.channel].actuation_range = self.actuation_range
        #KIT.servo[self.channel].angle = self.actuation_range if self.actuation_range != 0 else self.actuation_range + 1
        return True

    def set_angle(self, angle):
        print(f"Servo {self.channel} my angle is: {angle}")
        KIT.servo[self.channel].angle = angle

class ServoHandler(ComponentsHolder):
    def __init__(self, sensors, frequency):
        self.frequency = frequency
        super().__init__('ServoHandler', sensors, I2CServo)

    def _initialize(self):
        global KIT
        try:
            KIT = ServoKit(channels=NB_CHANNEL)
        except:
            print('[%s] Failed to open Servo Handler' % self.name)
            return False
        return True

    def set_angle_all(self, angles):
        for key, values in angles.items():
            if not isinstance(key, int):
                print('[%s] bad key id' % self.name)
                continue
            if not key in self.components:
                print('[%s] bad key id' % self.name)
                continue
            self.components[key].set_angle(values)
