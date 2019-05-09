#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable
from evolutek.lib.settings import ROBOT
from evolutek.lib.watchdog import Watchdog
from threading import Event
from math import pi
from time import sleep
import os


@Service.require("ax", "11")
@Service.require("ax", "12")
class Actuators(Service):


    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()

        for n in [11, 12]:
            self.cs.ax[str(n)].mode_joint()

        self.cs.ax['11'].moving_speed(256)
        self.cs.ax['11'].moving_speed(256)
        self.color = 'yellow'
        self.color1 = self.cs.config.get(section='match', option='color1')


    """ Open Arms """
    @Service.action
    def open_arms(self):
        self.cs.ax['11'].move(goal=350)
        sleep(0.5)
        self.cs.ax['12'].move(goal=550)
        sleep(0.5)
        print('FINISHED TO OPEN ARMS')

    @Service.action
    def half_close_arm(self):
        try:
            self.color = self.cs.match.get_match()['color']
        except Exception as e:
            print("Failed to get color: %s" % str(e))
        if self.color == self.color1:
            self.cs.ax['12'].move(goal=250)
        else:
            self.cs.ax['11'].move(goal=600)
        sleep(0.5)

    """ Open Arms """
    @Service.action
    def half_close_arms(self):
        self.cs.ax['11'].move(goal=600)
        sleep(0.5)
        self.cs.ax['12'].move(goal=250)
        sleep(0.5)

    """ Close Arms """
    @Service.action
    def close_arms(self):
        self.cs.ax['12'].move(goal=0)
        sleep(0.5)
        self.cs.ax['11'].move(goal=800)
        sleep(0.5)

def wait_for_beacon():
    hostname = "pi"
    while True:
        r = os.system("ping -c 1 " + hostname)
        if r == 0:
            return
        pass

def main():
    wait_for_beacon()
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
