#!/usr/bin/env python3

from time import sleep
from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service


DELAY = 0.2


class PMI(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cs = CellaservProxy(self)
        self.count = 0
        self.isWorking = False
        self.go_to_wall()

    def go_to_wall(self):
        self.cs.apmi.lift(p=0)
        sleep(DELAY)
        self.cs.apmi.pliers(a="open")
        sleep(DELAY)
        self.cs.apmi.move(d=1, s=1023, w="right")

    @Service.event
    def switch(self, state):
        if state == 1 and (not self.isWorking):
            self.is_working = True
            self.take_glass()
            if (self.count % 4 == 0):  # And not self.first_stack_done
                self.hold_back()
                if self.count == 4:
                    new_line()
            else:
                self.cs.apmi.move(d=True, s=1023, w="right")
            self.is_working = False

    def take_glass(self):
        sleep(2)
        self.cs.apmi.pliers(a="drop")
        sleep(1)
        self.cs.apmi.pliers(a="open")
        sleep(DELAY)

        if self.count < 3:
            self.cs.apmi.lift(p=0)
            sleep(2)
            self.cs.apmi.pliers(a="close")
            sleep(DELAY)
            self.cs.apmi.lift(p=950)
            sleep(2)
        else:
            self.cs.apmi.lift(p=300)
            sleep(2)
            self.cs.apmi.pliers(a="close")
            sleep(DELAY)

        self.count += 1

    def hold_back(self):
        self.cs.apmi.move(d=False s=512)
        sleep(5)
        self.cs.apmi.move(s=0)
        sleep(DELAY)
        self.cs.apmi.pliers(a="drop")
        sleep(1)
        self.cs.apmi.plier(a="open")
        sleep(DELAY)

    def new_line(self):
        self.cs.apmi.move(d=False, s=512)
        sleep(3)
        self.cs.apmi.move(s=0)
        sleep(DELAY)
        self.cs.apmi.rotate(d=False, s="left", a=45)
        sleep(DELAY)
        self.cs.apmi.move(d=1, s=500)
        sleep(4)
        self.cs.apmi.move(s=0)
        sleep(DELAY)
        self.cs.apmi.rotate(d=True, a=25, s="left")
        sleep(DELAY)
        self.cs.apmi.move(d=True, s=1023)


def main():
    pmi = PMI()
    pmi.run()


if __name__ == '__main__':
    main()
