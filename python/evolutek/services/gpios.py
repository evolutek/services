from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from enum import Enum
from evolutek.lib.settings import ROBOT
from threading import Lock, Thread
from time import sleep
import RPi.GPIO as GPIO

class Type(Enum):
        AIO = 0
        GPIO = 1
        PWM = 2
        SPI = 3
        UART = 4

class Edge(Enum):
        RISING = 0
        FALLING = 1
        BOTH = 2

class Io():

    def __init__(self, id, name, dir=True, event=None, update=True, callback=False, edge=None, publish=None):
        self.id = id
        self.name = name
        self.value = None
        self.dir = dir
        self.port = None
        self.event = event
        self.lock = Lock()
        self.update = update
        self.callback = callback
        self.edge = edge
        self.publish = publish
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

    def callback_fct(self, _=None):
        self.read()
        if self.publish:
            self.publish(self)

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

"""
class Aio(Io):

    def __init__(self, id, name, event=None, update=True):
        super().__init__(id, name, False, event=event, update=update)
        self.port = mraa.Aio(id)

    def read(self):
        with self.lock:
            return self.port.readFloat()
"""

"""
class Gpio(Io):

    def __init__(self, id, name, dir, event=None, callback=None, update=True):
        super().__init__(id, name, dir, event=event, update=update)
        self.port = mraa.Gpio(id)
        with self.lock:
            if dir:
                self.port.dir(mraa.DIR_OUT)
            else:
                self.port.dir(mraa.DIR_IN)
        if not dir and interrupt is not None:
            self.port.isr(mraa.EDGE_BOTH, interrupt, self)

class Pwm(Io):

    def __init__(self, id, name, dir, period, enable, event=None, update=True):
        super().__init__(id, name, dir, event=event, update=update)
        self.port = mraa.Pwm(id)
        self.period = period
        self.port.period_us(period)
        self.port.enable(enable)
        with self.lock:
            if dir:

def Spi(Io):

    def __init__(self, id, name, event=None, update=True):
        super().__init__(id, name, event=event, update=update)
        self.port = mraa.Spi(id)

class Uart(Io):

    def __init__(self, id, name, baud_rate, update=True):
        super().__init__(id, name, False, update=update)
        self.port = mraa.Uart(id)
        self.port.setBaudRate(baud_rate)
"""

class Gpios(Service):

    def __init__(self):
        cs = CellaservProxy()
        self.auto = cs.config.get(section="gpios", option="auto") == 'True'
        self.refresh = float(cs.config.get(section="gpios", option="refresh"))
        self.gpios = []
        
        super().__init__(ROBOT)

    @Service.action
    def add_gpio(self, type, id, name, dir=False, event=None, update=True, callback=False, edge=None):
        self.gpios.append(Io(id, name, dir=dir, event=event, update=update, callback=callback, edge=edge, publish=self.publish_gpio))
        #if type == Type.AIO:
        #    self.gpios.append(Aio(id, name, event=event, update=update))
        #elif type == Type.PWM:
        #    self.gpios.append(Pwm(id, name, dir, period, enable), event=event, update=update)
        #elif type == Type.SPI:
        #    self.gpios.append(Spi(id, name, event=event, update=update))
        #elif type == Type.UART:
        #    self.gpios.append(Uart(id, name, baud_rate, update=update))

    @Service.action
    def read_gpio(self, name=None, id=None):
        if name is None and id is None:
            return None

        for gpio in self.gpios:
            if (id != None and gpio.id == int(id)) or (name != None and gpio.name == name):
                return gpio.read()

        return None

    @Service.action
    def write_gpio(self, value, name=None, id=None):
        if name is None and id is None:
            return False

        for gpio in self.gpios:
            if (id != None and gpio.id == int(id)) or (name != None and gpio.name == name):
                return gpio.write(value)

        return False

    def publish_gpio(self, gpio):
        if gpio.event is None:
            self.publish(event=gpio.name, name=gpio.name, id=gpio.id, value=gpio.value)
        else:
            self.publish(event=gpio.event, name=gpio.name, id=gpio.id, value=gpio.value)

    @Service.thread
    def update(self):
        if not self.auto:
            return

        while True:
            for gpio in self.gpios:
                if not gpio.dir and not gpio.callback and gpio.update:
                    tmp = gpio.value
                    new = gpio.read()
                    if tmp != new:
                        self.publish_gpio(gpio)
            sleep(self.refresh)

def main():
    gpios = Gpios()

    gpios.add_gpio(Type.GPIO, 5, "tirette", False, callback=True, edge=Edge.RISING)
    gpios.add_gpio(Type.GPIO, 6, "reset", False, callback=True, edge=Edge.FALLING)
    
    # Front gtb
    gpios.add_gpio(Type.GPIO, 18, "gtb1", False, event='front')
    gpios.add_gpio(Type.GPIO, 23, "gtb2", False, event='front')
    gpios.add_gpio(Type.GPIO, 24, "gtb3", False, event='front')
    
    # Back gtb
    gpios.add_gpio(Type.GPIO, 16, "gtb4", False, event='back')
    gpios.add_gpio(Type.GPIO, 20, "gtb5", False, event='back')
    gpios.add_gpio(Type.GPIO, 21, "gtb6", False, event='back')

    gpios.run()

if __name__ == "__main__":
    main()
