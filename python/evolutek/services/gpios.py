from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from enum import Enum
from evolutek.lib.settings import ROBOT
from threading import Lock, Thread
from time import sleep
import RPi.GPIO as GPIO

class Edge(Enum):
        RISING = 0
        FALLING = 1
        BOTH = 2

class Io():

    def __init__(self, id, name, dir=True, event=None):
        self.id = id
        self.name = name
        self.value = None
        self.dir = dir
        self.event = event
        self.lock = Lock()

    def __equal__(self, ident):
        return self.id == int(ident[0]) or self.name == ident[1]

    def __str__(self):
        return "id: %d\nname: %s\ndir: %s\nevent: %s\nvalue: %s"\
            % (self.id, self.name, str(self.dir), self.event, str(self.value))

    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
            'dir': self.dir,
            'event': self.event,
            'value': self.value
        }

class Gpio(Io):

    def __init__(self, id, name, dir=True, event=None, callback=False, edge=None, callback_fct=None):

        super().__init__(id, name, dir, event)
        self.callback = callback
        self.edge = edge
        self.callback_fct = callback_fct

        GPIO.setmode(GPIO.BCM)
        if dir:
            GPIO.setup(id,  GPIO.OUT, initial=GPIO.LOW)
        else:
            GPIO.setup(id,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        if callback:
            if edge == Edge.RISING:
                GPIO.add_event_detect(id, GPIO.RISING, callback=self.callback_fct)
            elif edge == Edge.FALLING:
                GPIO.add_event_detect(id, GPIO.FALLING, callback=self.callback_fct)
            else:
                GPIO.add_event_detect(id, GPIO.BOTH, callback=self.callback_fct)

    def read(self):
        if self.dir:
            return None
        with self.lock:
            self.value = GPIO.input(self.id)
        return self.value

    def write(self, value):
        if not self.dir:
            return False
        with self.lock:
            if isinstance(value, str):
                if value == "true":
                    GPIO.output(self.id, GPIO.HIGH)
                else:
                    GPIO.output(self.id, GPIO.LOW)
        return True

class Gpios(Service):

    def __init__(self):
        cs = CellaservProxy()
        self.gpios = []
        super().__init__(ROBOT)

    """ Action """

    @Service.action
    def add_gpio(self, id, name, dir=False, event=None, callback=False, edge=None):
        self.gpios.append(Gpio(id, name, dir=dir, event=event,
            callback=callback, edge=edge, callback_fct=self.callback_gpio))

    @Service.action
    def read_gpio(self, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None or not hasattr(gpio, read):
            return None
        return gpio.read()

    @Service.action
    def write_gpio(self, value, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None:
            return False
        if hasattr(gpio, write):
            gpio.write(value)
        return True

    @Service.action
    def print_gpios(self):
        print('----------')
        for gpio in self.gpios:
            print(gpio)
            print('----------')

    @Service.action
    def dump_gpios(self):
        l = []
        for gpio in self.gpios:
            l.append(gpio.__dict__())
        return l

    """ Utils """

    def get_gpio(self, id=None, name=None):
        if id is None and name is None:
            return None
        g = None
        for gpio in self.gpios:
            if gpio == (id, name):
                g = gpio
        return g

    def callback_gpio(self, id):

        gpio = self.get_gpio(id)
        if gpio is None:
            return

        tmp = gpio.value
        new = gpio.read()

        if new == tmp:
            return

        self.publish(event=gpio.name if gpio.event is None else gpio.event,
            name=gpio.name, id=gpio.id, value=gpio.value)

def main():
    gpios = Gpios()

    gpios.add_gpio(5, "tirette", False, callback=True, edge=Edge.RISING)
    gpios.add_gpio(6, "reset", False, callback=True, edge=Edge.FALLING)

    # Front gtb
    gpios.add_gpio(18, "gtb1", False, event='front_%s' % ROBOT)
    gpios.add_gpio(23, "gtb2", False, event='front_%s' % ROBOT)
    gpios.add_gpio(24, "gtb3", False, event='front_%s' % ROBOT)

    # Back gtb
    gpios.add_gpio(16, "gtb4", False, event='back_%s' % ROBOT)
    gpios.add_gpio(20, "gtb5", False, event='back_%s' % ROBOT)
    gpios.add_gpio(21, "gtb6", False, event='back_%s' % ROBOT)

    gpios.run()

if __name__ == "__main__":
    main()
