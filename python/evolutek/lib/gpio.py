from enum import Enum
from threading import Thread
from time import sleep

from evolutek.lib.settings import SIMULATION

if SIMULATION:
    import evolutek.simulation.fake_lib.fake_gpio as GPIO
else:
    import RPi.GPIO as GPIO

# Types of edge for gpio
class Edge(Enum):
        RISING = 0
        FALLING = 1
        BOTH = 2

# Parent class IO
# id: id of the io
# name: name of io
# dir: True if output else False
# event: name of the event
class Io():

    def __init__(self, id, name, dir=True, event=None):
        self.id = id
        self.name = name
        self.dir = dir
        self.event = event
        self.value = None

        try:
            GPIO.setmode(GPIO.BCM)
        except Exception as e:
            print('Failed to gpio mode: %s' % str(e))
            raise Exception('[GPIO] Failed to set gpio mode')

    def __eq__(self, ident):
        return (ident[0] is not None and self.id == int(ident[0])) or self.name == ident[1]

    def __str__(self):
        return "id: %d\nname: %s\ndir: %s\nevent: %s\n"\
            % (self.id, self.name, str(self.dir), self.event)

    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
            'dir': self.dir,
            'event': self.event,
        }

# PWM class
# Inherit of IO class
# dc: initial Duty Cycle
# freq: Freq of the PWM
class Pwm(Io):

    def __init__(self, id, name, dc=0, freq=0):

        super().__init__(id, name, dir=True)

        GPIO.setup(id, GPIO.OUT, initial=GPIO.LOW)

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

# GPIO Class
# Inherit of IO class
# edge: Edge for automatic detection
# default_value: Default value to write on output gpio
class Gpio(Io):

    def __init__(self, id, name, dir=True, event=None, edge=Edge.BOTH, default_value=False):

        super().__init__(id, name, dir, event)
        self.edge = edge

        if dir:
            GPIO.setup(id,  GPIO.OUT, initial=GPIO.LOW)
            self.write(default_value)
        else:
            GPIO.setup(id,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Read the gpio
    def read(self):

        self.value = GPIO.input(self.id)

        return self.value

    # Write on the gpio
    def write(self, value):
        if not self.dir:
            return False

        if isinstance(value, str):
            value = value == "true"

        GPIO.output(self.id, GPIO.HIGH if value else GPIO.LOW)
        return True

    # Launch a thread on _auto_refresh
    def auto_refresh(self, refresh=0.5, callback=None):
        if self.dir:
            return

        Thread(target=self._auto_refresh, args=[refresh, callback]).start()

    # Auto refresh the gpio
    # If the gpio value change according to the edge, it will call the callback
    # Callback need to take 4 args: event, name, id & value
    def _auto_refresh(self, refresh, callback):
        while True:
            tmp = self.value
            self.read()

            if not callback is None and not tmp is None and self.value != tmp:
                if not self.edge or self.edge == Edge.BOTH:
                    callback(event=self.name if self.event is None else self.event,
                        name=self.name, id=self.id, value=self.value)
                elif self.edge == Edge.RISING and self.value == 1:
                    callback(event=self.name if self.event is None else self.event,
                        name=self.name, id=self.id, value=self.value)
                elif self.edge == Edge.FALLING and self.value == 0:
                    callback(event=self.name if self.event is None else self.event,
                        name=self.name, id=self.id, value=self.value)

            sleep(refresh)
