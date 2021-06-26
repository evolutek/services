from evolutek.lib.gpio.gpio import Edge, Gpio as BaseGpio, Pwm as BasePwm
from evolutek.lib.utils.boolean import get_boolean
import RPi.GPIO as GPIO


class Pwm(BasePwm):

    def __init__(self, id, name, dc=0, freq=0):

        super().__init__(id, name, dc, freq)

        self.pwm = GPIO.PWM(id, freq)
        self.start(dc)

    # Write Duty Cycle
    def write(self, dc=0):
        self.pwm.ChangeDutyCycle(dc)

    # Start PWM
    def start(self, dc=0):
        self.pwm.start(dc)

    # Stop PWM
    def stop(self):
        self.pwm.stop()


class Gpio(BaseGpio):

    def __init__(self, id, name, dir=True, event=None, edge=Edge.BOTH, default_value=False):

        super().__init__(id, name, dir, event, edge, default_value)

        if dir:
            GPIO.setup(id,  GPIO.OUT, initial=GPIO.LOW)
            self.write(default_value)
        else:
            GPIO.setup(id,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Read the gpio
    def read(self):
        self.last_value = GPIO.input(self.id)
        return self.last_value

    # Write on the gpio
    def write(self, value):
        if not self.dir:
            return

        GPIO.output(self.id, GPIO.HIGH if get_boolean(value) else GPIO.LOW)


WAS_INITIALIZED = False

# Return if the gpios was initialized
def wasInitialized():
    return WAS_INITIALIZED

# Initialize gpios
def initialize():
    global WAS_INITIALIZED
    try:
        GPIO.setmode(GPIO.BCM)
        WAS_INITIALIZED = True
    except Exception as e:
        print('[GPIO] Failed to gpio mode: %s' % str(e))
        raise Exception('[GPIO] Failed to set gpio mode')
