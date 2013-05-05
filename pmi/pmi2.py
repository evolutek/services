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
#       self.first_stack_done = False
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

            if (self.count == 4): # and not self.first_stack_done
                self.push_to_border()
                self.back_to_start()
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


    def push_to_border(self):
        self.cs.apmi.move(d=True, s=1023, w="right")
        sleep(5)
        self.cs.apmi.move(s=0)
#       TODO Using the tracking to make it look like this
#       while self.not_at_border:
#           self.cs.apmi.move(s=1023, d=True, w="right")
#           sleep(DELAY)
#       self.cs.apmi.move(s=0)
        sleep(DELAY)
        self.cs.apmi.move(d=False, s=512, w="right")
        sleep(2)
        self.cs.apmi.move(s=0)
        sleep(DELAY)
#       self.fisrt_stack_done = True
#       prévient robot principal et hokuyo que la première pile est faite


    def back_to_start(self):
        self.cs.apmi.move(d=False, s=1023, w="right")
        sleep(10)
        self.cs.apmi.move(s=0)
#       TODO Faire plutot qqch comme ça
#       print un truc pour que la balise previenne quand le pmi esr à son
#           point de départ
#       while not self.is_at_start:
#           self.cs.apmi.move(d=False, s=512, w="right")
#           sleep(DELAY)
#       self.cs.apmi.move(s=0)


def main():
    pmi = PMI()
    pmi.run()


if __name__ == '__main__':
    main()
