#!/usr/bin/env python3

import time

from cellaserv.service import Service, ConfigVariable
from evolutek.lib.settings import ROBOT
from cellaserv.proxy import CellaservProxy

import mraa

dist_table = [
        0,      #0
        3.1,    #5
        2.4,    #10
        1.7,    #15
        1.3,    #20
        1.1,    #25
        0.95,   #30
        0.8,    #35
        0.7,    #40
        0.67,   #45
        0.65,   #50
        0.6,    #55
        0.5,    #60
        0.45,   #65
        0.4,    #70
        0.38,   #75
        0.35    #80
]


def volt_to_cm(volt):
    for i in range(1, 16):
        if volt > dist_table[i]:
            return i * 5
    return 80

@Service.require("config")
@Service.require("trajman", "pal")
class SharpBack(Service):

    identification = ROBOT
    threshold = ConfigVariable(section="sharp", option="threshold", coerc=float)
    period = ConfigVariable(section="sharp", option="period", coerc=float)

    def __init__(self, sharps):
        super().__init__()
        self.sharps = sharps
        self.cs = CellaservProxy()

    def sharp_read(self, id):
        return mraa.Aio(id).readFloat()

    def refresh(self, id):
        tmp = volt_to_cm(self.sharp_read(id) * 5)
        tmp2 = volt_to_cm(self.sharp_read(id) * 5)
        return tmp if tmp > tmp2 else tmp2

    def looping(self, *args, **kwargs):
        while True:
            time.sleep(self.period())
            for sharp in self.sharps:
                if self.refresh(sharp) <= float(self.threshold()):
                    robot_moving_side = self.cs.trajman['pal'].get_vector_trsl()
                    robot_moving_side = robot_moving_side['trsl_vector']
                    if robot_moving_side < 0:
                        print("stop")
                        self.cs.trajman[self.identification].stop_asap(trsldec=1500, rotdec=3.1)
                        break

def main():
    sharps = [5]
    sharpback = SharpBack(sharps)
    sharpback.looping()

if __name__ == "__main__":
    main()
