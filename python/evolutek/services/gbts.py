#!/usr/bin/env python3

from cellaserv.service import Service
from time import sleep
import mraa

@Service.require("trajman", "pal")
class Gbts(Service):
    def __init__(self):
        super().__init__()
        self.front = mraa.Gpio(2)
        self.back = mraa.Gpio(5)
        self.front.dir(mraa.DIR_IN)
        self.back.dir(mraa.DIR_IN)

    # Loop of the Service
    def main_loop(self):
        while True:
            if self.front.read() == 1:
                print ('Front: avoid!')
                self.publish("front_avoid")
            if self.back.read() == 1:
                print ('Back: avoid!')
                self.publish("back_avoid")
            sleep(0.5)

def main():
    gbts = Gbts()
    gbts.main_loop()

if __name__ == "__main__":
    main()
