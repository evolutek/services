#!/usr/bin/env python3

from time import sleep
import time
from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

DELAY = 0.2


class PMI(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cs = CellaservProxy(self)
        self.count = 0
        self.isWorking = False
        self.gotoWall()

    def gotoWall(self):
        self.cs.apmi.lift(p=0)
        sleep(DELAY)
        self.cs.apmi.pliers(a="open")
        sleep(DELAY)
        self.cs.apmi.move(d=1, s=1023)

    @Service.event
    def switch(self, state):
        if state == 1 and (not self.isWorking):
            self.isWorking = True
            sleep(2)
            if (self.count % 10 >= 3) or (self.count >= 11):
                self.takeLastGlass()
                if (self.count) < 10:
                    self.nextLine()
            else:
                self.takeGlass()
                self.cs.apmi.move(d=1, s=1023)
            self.isWorking = False


    def takeGlass(self):
        self.cs.apmi.pliers(a="drop")
        sleep(1)
        self.cs.apmi.pliers(a="open")
        sleep(DELAY)
        self.cs.apmi.lift(p=0)
        sleep(2)
        self.cs.apmi.pliers(a="close")
        sleep(DELAY)
        self.cs.apmi.lift(p=950)
        self.count += 1
        sleep(2)

    def takeLastGlass(self):
        self.cs.apmi.pliers(a="drop")
        sleep(1)
        self.cs.apmi.pliers(a="open")
        sleep(DELAY)
        self.cs.apmi.lift(p=300)
        sleep(2)
        self.cs.apmi.pliers(a="close")
        sleep(DELAY)
        self.count += 1
        self.cs.apmi.move(s=512)
        sleep(3)
        self.cs.apmi.move(s=0)
        sleep(DELAY)
        self.cs.apmi.pliers(a="drop")
        sleep(1)
        self.cs.apmi.pliers(a="open")
        sleep(DELAY)
        self.cs.apmi.move(s=512, d=True)
        sleep(8)
        self.cs.apmi.move(s=0)
        sleep(DELAY)

    def nextLine(self):
        self.cs.move(s=1023, d=False)
        sleep(15)
        self.cs.apmi.rotate(a=45, d=1, s="left")
        sleep(DELAY)
        self.cs.apmi.move(d=True, s=512)
        sleep(2)
        self.cs.apmi.move(s=0)
        sleep(DELAY)
        self.cs.apmi.rotate(a=40, d=1, s="right")
        sleep(DELAY)
        self.count = 10
        self.cs.apmi.move(d=True, s=1023)

def main():
    pmi = PMI()
    pmi.run()

if __name__ == '__main__':
    main()
