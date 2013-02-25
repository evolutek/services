#!/usr/bin/env python3
from time import sleep
from cellaserv.proxy import CellaservProxy

DELAY = .5

def main():
    cs = CellaservProxy()

    sleep(.4)
    while True:
        cs.ax["1"].move(goal=560)
        cs.ax["6"].move(goal=560)

        sleep(DELAY)

        cs.ax["1"].move(goal=440)
        cs.ax["6"].move(goal=470)

        sleep(DELAY)

if __name__ == '__main__':
    main()
