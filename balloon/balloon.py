#!/usr/bin/env python3

from threading import Timer

from cellaserv.service import Service

BALLON_DURATION = 10.
GPIO_BALLOON = 129

class Balloon(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        gpio = open('/sys/class/gpio/export', 'w')
        gpio.write('129\n')
        gpio.close()

        direction = open('/sys/class/gpio/gpio{}/direction'.format(GPIO_BALLOON), 'w')
        direction.write("out\n")
        direction.close()

    @Service.action
    def start(self):
        with open('/sys/class/gpio/gpio{}/value'.format(GPIO_BALLOON), 'w') \
                as value:
            value.write("1\n")

    @Service.action
    def stop(self):
        with open('/sys/class/gpio/gpio{}/value'.format(GPIO_BALLOON), 'w') \
                as value:
            value.write("0\n")

    @Service.action
    def go(self):
        self.start()
        self.t = Timer(BALLON_DURATION, self.stop)
        self.t.start()

def main():
    balloon = Balloon()
    balloon.run()

if __name__ == '__main__':
    main()
