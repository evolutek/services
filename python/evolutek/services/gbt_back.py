#!/usr/bin/env python3

from cellaserv.service import Service, ConfigVariable
from evolutek.lib.settings import ROBOT
from cellaserv.proxy import CellaservProxy
from time import sleep
import mraa

@Service.require("trajman", "pal")
class GbtFront(Service):

    identification = ROBOT
    #change section "sharp" to "gbt"

    def __init__(self, gbts):
        super().__init__()
        for gbt in gbts:
            mraa.Gpio(gbt).dir(mraa.DIR_IN)
        self.gbts = gbts
        self.cs = CellaservProxy()

    # Read the GBT value
    def read(self, id):
        return mraa.Gpio(id).read()

    # Loop of the Service
    @Service.thread
    def looping(self, *args, **kwargs):
        while True:
            time.sleep(0.1)
            trsl_vector = self.cs.trajman["pal"].get_vector_trsl()
            moving_side = trsl_vector["trsl_vector"]
            if moving_side > 0:
                for gbt in self.gbts:
                    if(self.read(gbt) == 1):
                        self.publish("front_avoid")
                        print ('Front: avoid!')
                        break

def main():
    gbts = [8, 9]
    gbt_front = GbtFront(gbts)
    Service.loop()

if __name__ == "__main__":
    main()
