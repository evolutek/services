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

class Gpio(Service):

    def __init__(self, id, name, type, dir):
        self.id = id
        self.name = name
        self.value = None
        self.dir = dir
        self.type = type
        self.port = None
        self.lock = Lock()

        if type == Type.AIO:
            self.port = mraa.Aio(id)

        if type == Type.GPIO:
            self.port = mraa.Gpio(id)
            if dir:
                self.port.dir(mraa.DIR_OUT)
            else:
                self.port.dir(mraa.DIR_IN)

        if type == Type.PWM:
            self.port = mraa.Pwm(id)

    def read_value(self):
        if self.dir:
            return None

        with self.lock:
            if self.type == Type.AIO:
                self.value = self.port.ReadFloat()
            if self.type == Type.GPIO or Type.PWM:
                self.value.read()

        return self.value

    def write_value(self, value):
        if not self.dir or self.type == Type.AIO:
            return False

        with self.lock:
            self.value = value
            self.port.write(int(value))

        return True

class Gpios(Service):

    def __init__(self):
        super().__init__(ROBOT)
        self.gpios = []

    def add_gpio(self, id, name, type, dir):
        self.gpios.append(Gpio(id, name, type, dir))

    @Service.action
    def read_gpio(self, name=None, id=None):
        if name is None and id is None:
            return None

        if name is None:
            for gpio in self.gpios:
                if gpio.id == id:
                    return gpio.read_walue()

        else:
            for gpio in self.gpios:
                if gpio.name == name:
                    return gpio.read_value()

        return None

    @Service.action
    def write_gpio(self, name=None, id=None, value=None):
        if name is None and id is None:
            return False

        if name is None:
            for gpio in self.gpios:
                if gpio.id == id:
                    return gpio.write_value(value)

        else:
            for gpio in self.gpios:
                if gpio.name == name:
                    return gpio.write_value(value)

        return False

    def update(self, refresh):
        while True:
            for gpio in self.gpios:
                if gpio.dir:
                    tmp = gpio.value
                    new = gpio.read_value()
                    if tmp != new:
                        self.publish("gpios", gpio.name, gpio.id, gpio.value)
            sleep(refresh)

def main():
    gpios = Gpios()
    gpios.add_gpio(9, "led", Type.GPIO, True)

    cs = CellaservProxy()
    auto = cs.config.get(section="gpios", option="auto")

    if str(auto):
        refresh = cs.config.get(section="gpios", option="refresh")
        thread = Thread(target=gpios.update, args=[refresh])
        thread.start()

    gpios.loop()

if __name__ == "__main__":
    main()
