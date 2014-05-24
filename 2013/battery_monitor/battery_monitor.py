#!/usr/bin/python3

from threading import Timer
from time import sleep

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy

INTERVAL_BETWEEN_CHECKS = 10.0 # seconds

class BatteryMonitor(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        self.t = Timer(INTERVAL_BETWEEN_CHECKS, self.check)
        self.t.start()

    def check(self):
        voltage = self.cs.battery.voltage()

        if voltage > 3.8:
            for i in range(4):
                self.cs.leds.set(i=i, state=1)
        elif voltage > 3.6:
            for i in range(3):
                self.cs.leds.set(i=i, state=1)
            self.cs.leds.set(i=3, state=0)
        elif voltage > 3.4:
            for i in range(2):
                self.cs.leds.set(i=i, state=1)
            for i in range(2):
                self.cs.leds.set(i=2+i, state=0)
        elif voltage > 3.2:
            self.cs.leds.set(i=0, state=1)
            for i in range(3):
                self.cs.leds.set(i=1+i, state=0)
            self.cs.buzzer.freq(freq=420)
            sleep(1)
            self.cs.buzzer.stop()
        else:
            for i in range(4):
                self.cs.leds.set(i=i, state=0)
            self.cs.buzzer.freq(freq=420)
            sleep(1)
            self.cs.buzzer.stop()

        self.t = Timer(INTERVAL_BETWEEN_CHECKS, self.check)
        self.t.start()

    @Service.action
    def stop(self):
        self.t.cancel()

    @Service.action
    def start(self):
        self.t = Timer(INTERVAL_BETWEEN_CHECKS, self.check)
        self.t.start()

def main():
    battery_monitor = BatteryMonitor()
    battery_monitor.run()

if __name__ == '__main__':
    main()
