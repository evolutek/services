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
        self.value = None

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

        super().__init__(id, name, dir=True, update=False)

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

    def __init__(self, id, name, dir=True, event=None, update=True, edge=None, default_value=False):

        super().__init__(id, name, dir, event, update)
        self.edge = edge

        if dir:
            GPIO.setup(id,  GPIO.OUT, initial=GPIO.LOW)
            self.write(default_value)
        else:
            GPIO.setup(id,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read(self):
        if self.dir:
            return None
        self.value = GPIO.input(self.id)
        return self.value

    def write(self, value):
        if not self.dir:
            return False
        if isinstance(value, str):
            value = value == "true"
        GPIO.output(self.id, GPIO.HIGH if value else GPIO.LOW)
        return True

@Service.require('config')
class Gpios(Service):

    def __init__(self):
        cs = CellaservProxy()
        self.refresh = float(cs.config.get(section='gpios', option='refresh'))
        self.refresh = 1.0
        self.gpios = []
        try:
            GPIO.setmode(GPIO.BCM)
        except Exception as e:
            print('Failed to gpio mode: %s' % str(e))
            raise Exception('[GPIOS] Failed to start gpios service')
        super().__init__(ROBOT)

    """ Action """

    """ GPIO """
    @Service.action
    def add_gpio(self, id, name, dir=False, event=None, update=True, edge=None, default_value=False):
        if self.get_gpio(id, name) is None:
            try:
                self.gpios.append(Gpio(id, name, dir=dir, event=event, update=update, edge=edge, default_value=default_value))
            except Exception as e:
                print("[GPIOS] Failed to add gpio %s,%s: %s" % (name, str(id), str(e)))

    @Service.action
    def read_gpio(self, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None or not hasattr(gpio, 'read'):
            return None
        value = None
        try:
            value = gpio.read()
        except Exception as e:
            print("[GPIOS] Failed to read gpio %s,%s: %s" % (gpio.name, str(gpio.id), str(e)))
        return value

    @Service.action
    def write_gpio(self, value, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None:
            return False
        if hasattr(gpio, 'write'):
            try:
                gpio.write(value)
            except Exception as e:
                print("[GPIOS] Failed to write gpio %s,%s: %s" % (gpio.name, str(gpio.id), str(e)))
                return False
            return True
        return False

    """ PWM """
    @Service.action
    def add_pwm(self, id, name, dc=0, freq=0):
        if self.get_gpio(id, name) is None:
            try:
                self.gpios.append(Pwm(id, name, dc=dc, freq=freq))
            except Exception as e:
                print("[GPIOS] Failed to add pwm %s,%s: %s" % (name, str(id), str(e)))

    @Service.action
    def start_pwm(self, dc, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None:
            return False
        if hasattr(gpio, 'start'):
            try:
                gpio.start(dc)
            except Exception as e:
                print("[GPIOS] Failed to start pwm %s,%s: %s" % (gpio.name, str(gpio.id), str(e)))
                return False
            return True
        return False

    @Service.action
    def stop_pwm(self, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None:
            return False
        if hasattr(gpio, 'stop'):
            try:
                gpio.sttop()
            except Exception as e:
                print("[GPIOS] Failed to stop pwm %s,%s: %s" % (gpio.name, str(gpio.id), str(e)))
                return False
            return True
        return False

    """ GPIOS """
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

    """ UTILS """
    def get_gpio(self, id=None, name=None):
        if id is None and name is None:
            return None
        g = None
        for gpio in self.gpios:
            if gpio == (id, name):
                g = gpio
        return g

    def callback_gpio(self, gpio):
        if gpio is None:
            return

        self.publish(event=gpio.name if gpio.event is None else gpio.event,
            name=gpio.name, id=gpio.id, value=gpio.value)

    @Service.thread
    def update_gpios(self):
        while True:
            for gpio in self.gpios:
                if not gpio.dir and gpio.update:
                    tmp = gpio.value
                    gpio.read()
                    if not tmp is None and gpio.value != tmp:
                        if not gpio.edge or gpio.edge == Edge.BOTH:
                            self.callback_gpio(gpio)
                        else:
                            if gpio.edge == Edge.RISING and gpio.value == 1:
                                self.callback_gpio(gpio)
                            elif gpio.edge == Edge.FALLING and gpio.value == 0:
                                self.callback_gpio(gpio)
            sleep(0.015)


def wait_for_beacon():
    hostname = "pi"
    while True:
        r = os.system("ping -c 1 " + hostname)
        if r == 0:
            return
        pass

# TODO: Add gpio config in json for robots
def main():
    wait_for_beacon()
    gpios = Gpios()

    if ROBOT == 'pal':
        gpios.add_gpio(5, "tirette", False, edge=Edge.FALLING)
        gpios.add_gpio(6, "%s_reset" % ROBOT, False, edge=Edge.RISING)

        # Front gtb
        gpios.add_gpio(18, "gtb1", False, event='%s_front' % ROBOT, edge=Edge.BOTH)
        gpios.add_gpio(23, "gtb2", False, event='%s_front' % ROBOT, edge=Edge.BOTH)
        gpios.add_gpio(24, "gtb3", False, event='%s_front' % ROBOT, edge=Edge.BOTH)

        # Back gtb
        gpios.add_gpio(16, "gtb4", False, event='%s_back' % ROBOT, edge=Edge.BOTH)
        gpios.add_gpio(20, "gtb5", False, event='%s_back' % ROBOT, edge=Edge.BOTH)
        gpios.add_gpio(21, "gtb6", False, event='%s_back' % ROBOT, edge=Edge.BOTH)

        gpios.add_gpio(17, "relayGold", True, default_value=True)
        gpios.add_gpio(27, "relayArms", True, default_value=True)

        # Ejecteur
        gpios.add_pwm(13, "ejecteur", 0, 1.0)
        gpios.add_gpio(19, "hbridge1", True)
        gpios.add_gpio(26, "hbridge2", True)
        gpios.add_gpio(4, "ejecteur_contact1", False, update=False)
        gpios.add_gpio(22, "ejecteur_contact2", False, update=False)

    elif ROBOT == 'pmi':

        # Front gtb
        gpios.add_gpio(18, "gtb1", False, event='%s_front' % ROBOT, edge=Edge.BOTH)
        gpios.add_gpio(23, "gtb2", False, event='%s_front' % ROBOT, edge=Edge.BOTH)

        # Back gtb
        gpios.add_gpio(16, "gtb4", False, event='%s_back' % ROBOT, edge=Edge.BOTH)
        gpios.add_gpio(20, "gtb5", False, event='%s_back' % ROBOT, edge=Edge.BOTH)

        # Reset button
        gpios.add_gpio(26, "%s_reset" % ROBOT, False, edge=Edge.RISING)

    gpios.run()

if __name__ == "__main__":
    main()
