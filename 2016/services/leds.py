#!/usr/bin/env python3

import fcntl

from cellaserv.service import Service

LEDS_COUNT = 4

class Leds(Service):

    def __init__(self):
        super().__init__()

        try:
            self._leds = open('/dev/leds0')
        except:
            self._leds = open('/dev/leds')

        for i in range(LEDS_COUNT):
            fcntl.ioctl(self._leds, 0, i)

    @Service.action
    def set(self, i, state):
        i = int(i)
        if i >= LEDS_COUNT:
            return "i > LEDS_COUNT"
        fcntl.ioctl(self._leds, int(state), i)

    @Service.action
    def reset(self):
        for i in range(LEDS_COUNT):
            fcntl.ioctl(self._leds, 0, i)

def main():
    leds = Leds()
    leds.run()

if __name__ == "__main__":
    main()
