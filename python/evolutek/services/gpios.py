from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from enum import Enum
from evolutek.lib.settings import ROBOT
from threading import Lock, Thread
from time import sleep

import mraa

class Type(Enum):
        AIO = 0
        GPIO = 1
        PWM = 2
        SPI = 3
        UART = 4

class Io():

    def __init__(self, id, name, dir=True):
        self.id = id
        self.name = name
        self.value = None
        self.dir = dir
        self.port = None
        self.lock = Lock()

    def read(self):
        if self.dir:
            return None
        with self.lock:
            self.value = self.port.read()
        return self.value

    def write(self, value):
        if not self.dir:
            return False
        with self.lock:
            self.port.write(int(value))
        return True

class Aio(Io):

    def __init(self, id, name):
        super().__init__(id, name, False)
        self.port = mraa.Aio(id)

    def read(self):
        with self.lock:
            return self.port.readFloat()

class Gpio(Io):

    def __init__(self, id, name, dir):
        super().__init__(id, name, dir)
        self.port = mraa.Gpio(id)
        with lock:
            if dir:
                self.port.dir(mraa.DIR_OUT)
            else:
                self.port.dir(mraa.DIR_IN)

class Pwm(Io):

    def __init__(self, id, name, dir, period, enable):
        super().__init__(id, name, dir)
        self.port = mraa.Pwm(id)
        self.period = period
        self.port.period_us(period)
        self.port.enable(enable)
        with self.lock:
            if dir:
                self.port.dir(mraa.DIR_OUT)
            else:
                self.port.dir(mraa.DIR_IN)

def Spi(Io):

    def __init__(self, id, name):
        super().__init__(id, name)
        self.port = mraa.Spi(id)

class Uart(Io):

    def __init__(self, id, name, baud_rate):
        super().__init__(id, name, False)
        self.port = mraa.Uart(id)
        self.port.setBaudRate(baud_rate)

class Gpios(Service):

    def __init__(self):
        super().__init__(ROBOT)
        self.gpios = []

    @Service.action
    def add_gpio(self, type, id, name, dir=False, period=None, enable=None, baud_rate=None):
        if type == Type.AIO:
            self.gpios.append(Aio(id, name))
        elif type == Type.GPIO:
            self.gpios.append(Gpio(id, name, dir))
        elif type == Type.PWM:
            self.gpios.append(Pwm(id, name, dir, period, enable))
        elif type == Type.SPI:
            self.gpios.append(Spi(id, name))
        elif type == Type.UART:
            self.gpios.append(Uart(id, name, baud_rate))

    @Service.action
    def read_gpio(self, name=None, id=None):
        if name is None and id is None:
            return None

        for gpio in self.gpios:
            if (id != None and gpio.id == id) or (name != None and gpio.name == name):
                return gpio.read()

        return None

    @Service.action
    def write_gpio(self, value, name=None, id=None):
        if name is None and id is None:
            return False

        for gpio in self.gpios:
            if (id != None and gpio.id == id) or (name != None and gpio.name == name):
                return gpio.write(value)

        return False

    def update(self, refresh):
        while True:
            for gpio in self.gpios:
                if not gpio.dir:
                    tmp = gpio.value
                    new = gpio.read()
                    if tmp != new:
                        self.publish("gpios", gpio.name, gpio.id, gpio.value)
            sleep(float(refresh))

def main():
    gpios = Gpios()

    # example
    # gpios.add_gpio(type.GPIO, 9, "led", True)

    cs = CellaservProxy()
    auto = cs.config.get(section="gpios", option="auto")

    if bool(auto.decode()):
        refresh = cs.config.get(section="gpios", option="refresh")
        thread = Thread(target=gpios.update, args=[refresh])
        thread.start()

    gpios.loop()

if __name__ == "__main__":
    main()
