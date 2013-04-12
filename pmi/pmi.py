#!/usr/bin/env python3

from time import sleep
import time
from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

DELAY = 0.5


class PMI(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ok = True
        self.cs = CellaservProxy(self)
        self.count = 0
        self.gotoWall()

    def gotoWall(self):
        self.cs.apmi.lift(p=0)
        sleep(DELAY)
        self.cs.apmi.pliers(a="open")
        sleep(DELAY)
        #self.cs.apmi.move(d=0, s=500)
        #sleep(8)
        #self.cs.apmi.move(d=0, s=0)
        #sleep(DELAY)
        self.cs.apmi.move(d=1, s=1023)

    @Service.event
    def switch(self, state):
        t = time.time()
        if state == 1 and self.ok:
            self.ok = False
            print("verre")
            self.last = t
            sleep(1.5)
            if self.count == 0:
                self.cs.apmi.pliers(a="close")
                sleep(DELAY)
                self.cs.apmi.lift(p=950)
                self.count += 1
                sleep(2)
                self.cs.apmi.move(d=1, s=1023, w="right")
            elif self.count >= 1 and self.count <= 4:
                self.cs.apmi.pliers(a="drop")
                sleep(1)
                self.cs.apmi.pliers(a="open")
                sleep(DELAY)
                self.cs.apmi.lift(p=0)
                sleep(2)
                self.cs.apmi.pliers(a="close")
                sleep(DELAY)
                self.count += 1
                if self.count < 4:
                    self.cs.apmi.lift(p=950)
                    sleep(2)
                    self.cs.apmi.move(d=1, s=1023, w="right")
                    sleep(DELAY)
                else:
                    self.cs.apmi.move(d=0, s=1023, w="right")
                    sleep(5)
                    self.cs.apmi.move(d=1, s=0)
                    sleep(DELAY)
                    self.cs.apmi.pliers(a="drop")
                    sleep(DELAY)
                    self.cs.apmi.pliers(a="open")
                    sleep(DELAY)
                    self.cs.apmi.move(d=0, s=500)
                    sleep(3)
                    self.cs.apmi.move(d=0, s=0)
                    sleep(DELAY)
                    self.cs.apmi.rotate(d=0, a=45, s="right")
                    sleep(DELAY)
                    self.cs.apmi.move(d=1, s=500)
                    sleep(4)
                    self.cs.apmi.move(d=0, s=0)
                    sleep(DELAY)
                    self.cs.apmi.rotate(d=1, a=25, s="right")
                    sleep(DELAY)
                    self.cs.apmi.move(d=1, s=1023, w="right")
                    self.count = 1
            self.ok = True

#    @Service.action
#    def rotation(self, angle):
#        s = angle > 0
#        angle = abs(angle)
#        ax = AX_ID_ROUE_GAUCHE if angle else AX_ID_ROUE_DROITE
#        self.cs.ax[ax].turn(side=s, speed=1023)
#        sleep(1 / (angle / 90))
#        self.cs.ax[ax].turn(side=s, speed=0)


def main():
    pmi = PMI()
    pmi.run()

if __name__ == '__main__':
    main()
