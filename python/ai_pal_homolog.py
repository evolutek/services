#!/usr/bin/env python3

import mraa
from evolutek.services.watchdog import Watchdog
from queue import *
from math import pi
from time import sleep
from threading import Thread, Timer, Event
from cellaserv.service import Service, ConfigVariable
from cellaserv.proxy import CellaservProxy

@Service.require("trajman", "pal")
class ia(Service):

    def __init__(self):
        super().__init__()
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman['pal']
        #self.stop_time = Timer(50, self.match_stop)
        self.thread = Thread(target=self.start)
        self.thread.daemon = True
        self.maxspeed = 100
        self.minspeed = 100
        self.started = False
        self.setup()

    @Service.event
    def match_start(self):
        if (not self.started):
            print("Go")
#            self.stop_time.start()
            self.thread.start()
    
    @Service.event
    def sharp_avoid(self):
        print("avoid")
        #self.trajman['pal'].free()
        #self.trajman['pal'].stop_asap(100000, 100000)
        #self.stop_move.set()

    def match_stop(self):
        print("Stop")
# Funny action here
        self.cs.ax["1"].move(goal = 600)
        sleep(1)
        self.cs.ax["1"].move(goal = 500)
        self.trajman['pal'].free()

    def setup(self):
        print("free !")
        self.trajman['pal'].free()
        self.trajman.set_theta(3.141592)
        self.trajman.set_x(1000)
        self.trajman.set_y(1000)
        print("Unfree !")
        self.trajman['pal'].unfree()

        print("Setup complete, waiting to receive match_start")

    def start(self):
        print("Starting the match")
        self.goto_xy(1100, 1000)
        self.goto_xy(1100, 600)
        self.goto_xy(1100, 1100)
        self.goto_xy(1900, 1100)
        self.goto_theta(1.57)
        self.goto_xy(1900, 500)
        self.goto_xy(1900, 1100)
        self.goto_xy(2200, 1100)
        self.goto_xy(2200, 450)
        self.goto_theta(0)
        self.goto_xy(1200, 400)
        self.cs.ax["1"].move(goal = 600)
        sleep(1)
        self.cs.ax["1"].move(goal = 500)

    def goto_xy(self, x, y):
        self.trajman.goto_xy(x=x, y=y)
        while self.trajman.is_moving():
            continue
        sleep(1)

    def move_trsl(self, len):
        self.trajman.move_trsl(len, 10, 10, 10, 0)
        while self.trajman.is_moving():
            continue

    def goto_theta(self, theta):
        self.trajman.goto_theta(theta=theta)
        while self.trajman.is_moving():
            continue

def main():
    ai = ia()
    ai.run()

if __name__  == '__main__':
    main()
