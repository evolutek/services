from evolutek.lib.gpio.gpio import Edge, Adc as BaseAdc, Gpio as BaseGpio, Pwm as BasePwm


# PWM class
# Inherit of IO class
# dc: initial Duty Cycle
# freq: Freq of the PWM
class Pwm(BasePwm):

    def __init__(self, id, name, dc=0, freq=0):

        super().__init__(id, name, dc, freq)

        print('[FAKE_GPIO] Init pwm: (%d; %d)' % (id, freq))

    # Write Duty Cycle
    def write(self, dc=0):
        print('[FAKE_GPIO] Changing duty cycle on pwm %d: %d' % (self.id, dc))

    # Start PWM
    def start(self, dc=0):
        print('[FAKE_GPIO] Strating pwm %d: %d' % (self.id, dc))

    # Stop PWM
    def stop(self):
        print('[FAKE_GPIO] Stoping pwm %d' % self.id)


class Adc(BaseAdc):

    def __init__(self, id, name):

        super().__init__(id, name)

        print('[FAKE_GPIO] Init adc: (%d)' % (id))

    # Read ADC
    def read(self):
        print('[FAKE_GPIO] Reading adc %d' % self.id)
        return 0.0


# GPIO Class
# Inherit of IO class
# edge: Edge for automatic detection
# default_value: Default value to write on output gpio
class Gpio(BaseGpio):

    def __init__(self, id, name, dir=True, event=None, edge=Edge.BOTH, default_value=False):

        super().__init__(id, name, dir, event, edge, default_value)

        print('[FAKE_GPIO] Setting gpio %d with dir %s' % (id, 'output' if dir else 'input'))

    # Read the gpio
    def read(self):
        print('[FAKE_GPIO] Reading gpio %d' % self.id)
        return 0

    # Write on the gpio
    def write(self, value):
        if not self.dir:
            return

        print('[FAKE_GPIO] Writing on gpio %d: %s' % (self.id, value))
