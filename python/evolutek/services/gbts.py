#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from time import sleep
import mraa

@Service.require("trajman", "pal")
class Gbts(Service):

    def __init__(self):
        self.front = 2
        self.back = 8
        super().__init__()
        mraa.Gpio(self.front).dir(mraa.DIR_IN)
        mraa.Gpio(self.back).dir(mraa.DIR_IN)
        self.cs = CellaservProxy()

    # Read the GBT value
    def read(self, id):
        return mraa.Gpio(id).read()

    # Loop of the Service
    def main_loop(self):
        while True:
            trsl_vector = self.cs.trajman["pal"].get_vector_trsl()
            moving_side = trsl_vector["trsl_vector"]
            if moving_side > 0 and self.read(self.front) == 1:
                print ('Front: avoid!')
                self.publish("avoid")
                while self.read(self.front) == 1:
                    sleep(0.5)
                self.publish("end_avoid")
                print ('Front: end avoid!')
            elif moving_side < 0 and self.read(self.back) == 1:
                print ('Back: avoid!')
                self.publish("avoid")
                while self.read(self.back) == 1:
                    sleep(0.5)
                self.publish("end_avoid")
                print ('Back: end avoid!')
            sleep(0.1)

def main():
    gbts = Gbts()
    gbts.main_loop()

if __name__ == "__main__":
    main()
