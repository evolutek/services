#!/usr/bin/env python3

import time

from cellaserv.service import Service, ConfigVariable
from evolutek.lib.settings import ROBOT
from time import sleep
import mraa

class SicksFront(Service):

    identification = ROBOT
#change section "sharp" to "sick_gtb6"
    #period = ConfigVariable(section="sharp", option="period", coerc=float)

    def __init__(self, sicks):
        super().__init__()
        for sick in sicks:
            mraa.Gpio(sick).dir(mraa.DIR_IN)
        self.sicks = sicks

    def read(self, id):
        return mraa.Gpio(id).read()

    @Service.thread
    def looping(self, *args, **kwargs):
        while True:
            time.sleep(0.1)
#change publish message x)
            for sick in self.sicks:
                if(self.read(sick) == 1):
                    self.publish("sharp_avoid")
                    print ('Sharp: avoid !')
                    break

def main():
    sicks = [8, 9]
    sicksfront = SicksFront(sicks)
    Service.loop()

if __name__ == "__main__":
    main()
