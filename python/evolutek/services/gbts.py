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
        mraa.Gpio(front).dir(mraa.DIR_IN)
        mraa.Gpio(back).dir(mraa.DIR_IN)
        self.cs = CellaservProxy()
        main_loop()

    # Read the GBT value
    def read(self, id):
        return mraa.Gpio(id).read()

    # Loop of the Service
    def main_loop(self):
        while True:
            time.sleep(0.1)
            trsl_vector = self.cs.trajman["pal"].get_vector_trsl()
            moving_side = trsl_vector["trsl_vector"]
            if moving_side > 0 and self.read(front) == 1:
                print ('Front: avoid!')
                self.publish("avoid")
                while self.read(front) == 1:
                    sleep(0.5)
                self.publish("end_avoid")
                print ('Front: end avoid!')
            elif moving_side < 0 and self.read(back) == 1:
                print ('Back: avoid!')
                self.publish("avoid")
                while self.read(back) == 1:
                    sleep(0.5)
                self.publish("end_avoid")
                print ('Back: end avoid!')

def main():
    gbts = Gbts()
    Service.run()

if __name__ == "__main__":
    main()
