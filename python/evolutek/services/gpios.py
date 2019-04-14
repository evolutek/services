from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from enum import Enum
from evolutek.lib.settings import ROBOT
from evolutek.lib.lcddriver import lcd
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
        if value:
            GPIO.output(self.id, GPIO.HIGH)
        else:
            GPIO.output(self.id, GPIO.LOW)
        return True

@Service.require('config')
class Gpios(Service):

    def __init__(self):
        cs = CellaservProxy()
        self.refresh = float(cs.config.get(section='gpios', option='refresh'))
        self.refresh = 1.0
        self.gpios = []
        GPIO.setmode(GPIO.BCM)
        super().__init__(ROBOT)
        self.lcd = lcd()
        self.clear_lcd()

    """ Action """

    """ GPIO """
    @Service.action
    def add_gpio(self, id, name, dir=False, event=None, update=True, edge=None, default_value=False):
        if self.get_gpio(id, name) is None:
            self.gpios.append(Gpio(id, name, dir=dir, event=event, update=update, edge=edge, default_value=default_value))

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

    """ PWM """
    @Service.action
    def add_pwm(self, id, name, dc=0, freq=0):
        if self.get_gpio(id, name) is None:
            self.gpios.append(Pwm(id, name, dc=dc, freq=freq))

    @Service.action
    def start_pwm(self, dc, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None:
            return False
        if hasattr(gpio, 'start'):
            gpio.start(dc)
            return True
        return False

    @Service.action
    def stop_pwm(self, id=None, name=None):
        gpio = self.get_gpio(id, name)
        if gpio is None:
            return False
        if hasattr(gpio, 'stop'):
            gpio.stop()
            return True
        return False

    """ LCD """
    @Service.action
    def write_lcd(self, string, line):
        if isinstance(line, str):
            line = int(line)
        self.lcd.lcd_display_string(string, line)

    @Service.action
    def write_status(self, score=None, status=None):
        self.lcd.lcd_display_string(" " * 16, 1)
        self.lcd.lcd_display_string(" " * 16, 2)
        if not score is None:
            self.lcd.lcd_display_string("Score: %s" % score, 2)
        if not status is None:
            self.lcd.lcd_display_string("Status: %s" % status, 1)

    @Service.action
    def clear_lcd(self):
        self.lcd.lcd_clear()

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
            sleep(0.025)


def wait_for_beacon():
    hostname = "pi"
    while True:
        r = os.system("ping -c 1 " + hostname)
        if r == 0:
            return
        pass

### TODO: Add gpio config in json for robots
def main():
    wait_for_beacon()
    gpios = Gpios()

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
    gpios.add_pwm(13, "ejecteur", 0, 0.3)
    gpios.add_gpio(19, "hbridge1", True)
    gpios.add_gpio(26, "hbridge2", True)
    gpios.add_gpio(4, "ejecteur_contact1", False, update=False)
    gpios.add_gpio(22, "ejecteur_contact2", False, update=False)

    gpios.run()

if __name__ == "__main__":
    main()
