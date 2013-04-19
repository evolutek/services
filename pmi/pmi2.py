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
        self.cs.apmi.move(d=1, s=1023, w="right")

    @Service.event
    def switch(self, state):
      if state == 1 and (not self.isWorking):
        self.isWorking = True
        print("Je suis le verre " + str(self.count))
        if self.count >= 3:
          self.takeLastGlass()
          self.cs.apmi.pliers(a="drop")
          sleep(1)
          self.cs.apmi.pliers(a="open")
          sleep(DELAY)
        else:
          self.takeGlass()
          self.cs.apmi.move(d=1, s=1023, w="right")
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
      self.count += 1
      self.cs.apmi.lift(p=950)
      sleep(2)

    def takeLastGlass(self):
      self.cs.apmi.pliers(a="drop")
      sleep(1)
      self.cs.apmi.pliers(a="open")
      sleep(DELAY)
      self.cs.apmi.lift(p=250)
      sleep(2)
      self.cs.apmi.pliers(a="close")
      sleep(DELAY)
      self.count += 1
      self.cs.apmi.move(s=512, d=False)
      sleep(3)
      self.cs.apmi.move(s=0,d=False)
      sleep(DELAY)

def main():
    pmi = PMI()
    pmi.run()

if __name__ == '__main__':
    main()
