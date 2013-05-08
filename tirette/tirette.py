#!/usr/bin/env python3

from threading import Timer

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

class Tirette(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cs = CellaservProxy()

        gpio = open('/sys/class/gpio/export', 'w')
        gpio.write('9\n')
        try:
            gpio.close()
        except:
            pass

        gpio = open('/sys/class/gpio/gpio9/value', 'r')
        self.state = int(gpio.readline())

        self.loop_timer = Timer(.1, self.loop)
        self.loop_timer.start()

    def loop(self):
        gpio = open('/sys/class/gpio/gpio9/value', 'r')

        tirette_on = int(gpio.readline())
        tirette_off = not tirette_on

        if tirette_on:
            self.state = 1
        if self.state == 1 and tirette_off:
            self.state = 0
            self.cs('match-start')

        self.loop_timer = Timer(.1, self.loop)
        self.loop_timer.start()

def main():
    tirette = Tirette()
    tirette.run()

if __name__ == '__main__':
    main()
