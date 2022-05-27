from adafruit_pca9685 import PCA9685
import board
import busio
from enum import Enum
from time import sleep
from typing import Optional

from evolutek.lib.component import Component, ComponentsHolder

PCA: PCA9685 = None
HAS_ESC: bool = False

class I2CActType(Enum):
    Servo = "Servo"
    ESC = "ESC"

class ESCVariation(Enum):
    Default = (0.0, 0.0)
    Emax = (0.05, 0.15)

class I2CAct(Component):
    def __init__(self, id_channel: int, type: I2CActType, max_range: float = 180.0, min_pulse: int = 750, max_pulse: int = 2250, esc_variation=None):
        print(type)
        self.type = type
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.max_range = max_range
        self.esc_variation = esc_variation
        super().__init__(type.value, id_channel)
    
    def _initialize(self) -> bool:
        if self.id < 0 or self.id >= 16:
            raise ValueError(f"[{self.name}] Bad channel id {self.id}")

        self.channel = PCA.channels[self.id]

        self.min_duty = int((self.min_pulse * self.channel.frequency) / 1000000 * 0xFFFF)
        max_duty = (self.max_pulse * self.channel.frequency) / 1000000 * 0xFFFF
        self.duty_range = int(max_duty - self.min_duty)

        if self.type == I2CActType.ESC:

            global HAS_ESC
            HAS_ESC = True

            if not isinstance(self.esc_variation, ESCVariation):
                self.esc_variation = ESCVariation.Default

            self.max_range = min(self.max_range, 1.0)

        return True

    def __str__(self):
        s = "----------\n"
        s += "%s: %d\n" % (self.name, self.id)
        s += "Min/Max pulse: (%d, %d)\n" % (self.min_pulse, self.max_pulse)
        s += "Max range: %f\n" % self.max_range
        #if self.type == I2CActType.Servo:
            #s += "Angle: %f\n" % self.get_angle()
        if self.type == I2CActType.ESC:
            s += "ESC variation: %s\n" % self.esc_variation.name
            #s += "Speed: %f\n" % self.get_speed() * 100.0
        s += "----------"
        return s

    def free(self):
        self.channel.duty_cycle = 0

    @property
    def fraction(self) -> Optional[float]:
        if self.channel.duty_cycle == 0:  # Special case for disabled servos
            return None
        return (self.channel.duty_cycle - self.min_duty) / self.duty_range

    @fraction.setter
    def fraction(self, value: Optional[float]) -> None:
        if value is None:
            self.channel.duty_cycle = 0  # disable the pwm
            return
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"[{self.name}] Bad fraction {value} for servo {self.id}")
        duty_cycle = self.min_duty + int(value * self.duty_range)
        self.channel.duty_cycle = duty_cycle

    def get_angle(self) -> Optional[float]:
        if self.type != I2CActType.Servo:
            return None

        if self.fraction is None:  # special case for disabled servos
            return None

        return self.max_range * self.fraction

    def set_angle(self, angle: float) -> bool:
        if self.type != I2CActType.Servo:
            return False
        
        if angle < 0 or angle > self.max_range:
            raise ValueError(f"[{self.name}] Bad angle {angle} for servo {self.id}")

        print(f"[{self.name}] Moving {self.id} to {angle}")
        self.fraction = angle / self.max_range
        return True

    def get_speed(self):
        if self.type != I2CActType.ESC:
            return None

        if self.fraction is None:  # special case for disabled escs
            return None
        
        return self.fraction

    def set_speed(self, speed: float) -> bool:
        if self.type != I2CActType.ESC:
            return False
        if speed < 0.0 or speed > self.max_range:
            raise ValueError(f"[{self.name}] Bad speed {speed} for esc {self.id}")
 
        self.fraction = (speed + self.esc_variation.value[1])
        print(f"[{self.name}] Moving {self.id} at {self.fraction}")
        return True


class I2CActsHandler(ComponentsHolder):
    def __init__(self, acts, frequency):
        self.frequency = frequency
        super().__init__('I2CActsHandler', acts, I2CAct)
    
    def _initialize(self):
        global PCA
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            PCA = PCA9685(
                i2c,
                address=0x40,
                reference_clock_speed=25000000
            )
            PCA.frequency = self.frequency
        except:
            print('[%s] Failed to init PCA9685' % self.name)
            return False
        return True

    def init_escs(self):
        if not HAS_ESC:
            return
        for component in self.components:
            if self.components[component].type == I2CActType.ESC:
                self.components[component].set_speed(self.components[component].esc_variation.value[0])
        sleep(5)
        for component in self.components:
            if self.components[component].type == I2CActType.ESC:
                self.components[component].set_speed(0)
        return True

    def free_all(self):
        for id in self.components:
            if self.components[id] is None:
                continue
            self.components[id].free()
