from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from enum import Enum
from evolutek.lib.settings import ROBOT
from threading import Lock, Thread
from time import sleep
import RPi.GPIO as GPIO
import os

class Edge(Enum):
        RISING = 0
        FALLING = 1
        BOTH = 2

class Io():

    def __init__(self, id, name, dir=True, event=None, update=True):
        self.id = id
        self.name = name
        self.dir = dir
        self.event = event
        self.update = update

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

class Gpio(Io):

    def __init__(self, id, name, dir=True, event=None, update=True, callback=False, edge=None, callback_fct=None, default_value=False):


        super().__init__(id, name, dir, event, update)
        self.callback = callback
        self.edge = edge
        self.callback_fct = callback_fct

        GPIO.setmode(GPIO.BCM)
        if dir:
            GPIO.setup(id,  GPIO.OUT, initial=GPIO.LOW)
            self.write(default_value)
        else:
            GPIO.setup(id,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        if callback:
            if edge == Edge.RISING:
                GPIO.add_event_detect(id, GPIO.RISING, callback=self.callback_fct, bouncetime=200)
            elif edge == Edge.FALLING:
                GPIO.add_event_detect(id, GPIO.FALLING, callback=self.callback_fct, bouncetime=200)
            else:
                GPIO.add_event_detect(id, GPIO.BOTH, callback=self.callback_fct, bouncetime=200)

    def read(self):
        if self.dir:
            return None
        return GPIO.input(self.id)

    def write(self, value):
        if not self.dir:
            return False
        if isinstance(value, str):
            value = value == "true"
        if value:
            GPIO.output(self.id, GPIO.HIGH)
        else:
            GPIO.output(self.id, GPIO.LOW)
        return True

@Service.require('config')
class Gpios(Service):

    def __init__(self):
        cs = CellaservProxy()
        #self.refresh = float(cs.config.get(section='gpios', option='refresh'))
        self.refresh = 1.0
        self.gpios = []
        super().__init__(ROBOT)

    """ Action """

    @Service.action
    def add_gpio(self, id, name, dir=False, event=None, update=True, callback=False, edge=None, default_value=False):
        self.gpios.append(Gpio(id, name, dir=dir, event=event, update=update,
            callback=callback, edge=edge, callback_fct=self.callback_gpio, default_value=default_value))

    @Service.action
    def read_gpio(self, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None or not hasattr(gpio, 'read'):
            return None
        return gpio.read()

    @Service.action
    def write_gpio(self, value, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None:
            return False
        if hasattr(gpio, 'write'):
            gpio.write(value)
            return True
        return False

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

        print("id %d" % id)

        gpio = self.get_gpio(id)
        if gpio is None:
            return

        value = gpio.read()

        self.publish(event=gpio.name if gpio.event is None else gpio.event,
            name=gpio.name, id=gpio.id, value=value)

    #@Service.thread
    def update_gpios(self):
        while True:
            for gpio in self.gpios:
                if not gpio.dir and gpio.update:
                    self.callback_gpio(gpio.id)
            sleep(self.refresh)

def wait_for_beacon():
    hostname = "pi"
    while True:
        r = os.system("ping -c 1 " + hostname)
        if r == 0:
            return
        pass

def main():
    wait_for_beacon()
    gpios = Gpios()

    gpios.add_gpio(5, "tirette", False, update=False, callback=True, edge=Edge.RISING)
    gpios.add_gpio(6, "reset", False, update=False, callback=True, edge=Edge.FALLING)

    # Front gtb
    gpios.add_gpio(18, "gtb1", False, event='front_%s' % ROBOT, callback=True, edge=Edge.BOTH)
    gpios.add_gpio(23, "gtb2", False, event='front_%s' % ROBOT, callback=True, edge=Edge.BOTH)
    gpios.add_gpio(24, "gtb3", False, event='front_%s' % ROBOT, callback=True, edge=Edge.BOTH)

    # Back gtb
    gpios.add_gpio(16, "gtb4", False, event='back_%s' % ROBOT, callback=True, edge=Edge.BOTH)
    gpios.add_gpio(20, "gtb4", False, event='back_%s' % ROBOT, callback=True, edge=Edge.BOTH)
    gpios.add_gpio(21, "gtb4", False, event='back_%s' % ROBOT, callback=True, edge=Edge.BOTH)

    gpios.add_gpio(17, "relayGold", True, default_value=True)
    gpios.add_gpio(27, "relayArms", True, default_value=True)
    
    #gpios.print_gpios()

    gpios.run()

if __name__ == "__main__":
    main()
