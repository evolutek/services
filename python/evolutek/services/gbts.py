#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from time import sleep

@Service.require("trajman", "pal")
class Gbts(Service):
    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman['pal']
        self.gpios = self.cs.gpios['pal']
        self.front = 2
        self.back = 5
        print('Wait for trajman')
        #self.gpios.SetGpioIn(self.front)
        #self.gpios.SetGpioIn(self.back)

    # Loop of the Service
    def main_loop(self):
        while True:
            sleep(0.1)
            moving_side = self.trajman.get_vector_trsl()['trsl_vector']
            if moving_side > 0.0 and self.gpios.ReadGpio(self.front) == 1:
                print ('Front: avoid!')
                self.publish("avoid")
                while self.self.gpios.ReadGpios(self.front) == 1:
                    sleep(0.5)
                self.publish("end_avoid")
                print ('Front: end avoid!')
            elif moving_side < 0.0 and self.gpios.ReadGpio(self.back) == 1:
                print ('Back: avoid!')
                self.publish("avoid")
                while self.gpios.ReadGpio(self.back) == 1:
                    sleep(0.5)
                self.publish("end_avoid")
                print ('Back: end avoid!')

def main():
    gbts = Gbts()
    gbts.main_loop()

if __name__ == "__main__":
    main()
