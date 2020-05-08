from enum import Enum
from threading import Thread
from time import sleep

from evolutek.lib.settings import SIMULATION

if SIMULATION:
    import evolutek.simulation.fake_lib.fake_gpio as GPIO
else:
    import RPi.GPIO as GPIO

class Edge(Enum):
        RISING = 0
        FALLING = 1
        BOTH = 2

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

class Pwm(Io):

    def __init__(self, id, name, dc=0, freq=0):

        super().__init__(id, name, dir=True)

        GPIO.setup(id, GPIO.OUT, initial=GPIO.LOW)

        self.pwm = GPIO.PWM(id, freq)
        self.start(dc)

    def write(self, dc=0):
        self.pwm.ChangeDutyCycle(dc)

    def start(self, dc=0):
        self.pwm.start(dc)

    def stop(self):
        self.pwm.stop()

class Gpio(Io):

    def __init__(self, id, name, dir=True, event=None, edge=Edge.BOTH, default_value=False):

        super().__init__(id, name, dir, event)
        self.edge = edge

        if dir:
            GPIO.setup(id,  GPIO.OUT, initial=GPIO.LOW)
            self.write(default_value)
        else:
            GPIO.setup(id,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read(self):

        self.value = GPIO.input(self.id)

        return self.value

    def write(self, value):
        if not self.dir:
            return False

        if isinstance(value, str):
            value = value == "true"

        GPIO.output(self.id, GPIO.HIGH if value else GPIO.LOW)
        return True

    def auto_refresh(self, refresh=0.5, service=None):
        if self.dir:
            return

        Thread(target=self._auto_refresh, args=[refresh, service]).start()

    def _auto_refresh(self, refresh, service):
        while True:
            tmp = self.value
            self.read()

            if not service is None and not tmp is None and self.value != tmp:
                if not self.edge or self.edge == Edge.BOTH:
                    self.callback_gpio(service)
                else:
                    if self.edge == Edge.RISING and self.value == 1:
                        self.callback_gpio(service)
                    elif self.edge == Edge.FALLING and self.value == 0:
                        self.callback_gpio(service)

            sleep(refresh)

    def callback_gpio(self, service):
        service.publish(event=self.name if self.event is None else self.event,
            name=self.name, id=self.id, value=self.value)
