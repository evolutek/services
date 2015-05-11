#!/usr/bin/env python3

from time import clock

from cellaserv.service import Service, ConfigVariable
from evolutek.lib.settings import ROBOT

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


class Sharp():
    def __init__(self, sharp):
        self.sharp = sharp
        self.adc = mraa.Aio(sharp)
        self.sharp_value = 0
        self.begin = clock()

    def read(self):
        return self.sharp_value

    def refresh(self):
        tmp = volt_to_cm(self.adc.readFloat() * 5)
        tmp2 = volt_to_cm(self.adc.readFloat() * 5)
        sharp_value = tmp if tmp > tmp2 else tmp2
        return sharp_value

    def init_clock(self):
        self.begin = clock()

    def get_time(self):
        cur = clock()
        return cur - self.begin

    def get_sharp(self):
        return str(self.sharp)


class SharpManager(Service):

    identification = ROBOT
    threshold = ConfigVariable(section="sharp", option="threshold", coerc=float)

    def __init__(self, sharps, *args, **kwargs):
        super().__init__()
        self.sharps = sharps
        self.looping(sharps)

    @Service.action
    def read(self, id_: str) -> float:
        id__ = int(id_)
        return self.sharps[id__].read()

    @Service.thread
    def looping(self, sharps=[], *args, **kwargs):
        while True:
            thres = False
            for sharp in sharps:
                thres |= sharp.refresh() < float(self.threshold())
                if thres:
                    if sharp.get_time() > 0.3:
                        self.publish("sharp_avoid", "n:" + sharp.get_sharp())
                        sharp.init_clock()
                    break


def main():
    sharps = [Sharp(sharp=i) for i in [1,2]]
    sharpManager = SharpManager(sharps)
    Service.loop()

if __name__ == "__main__":
    main()
