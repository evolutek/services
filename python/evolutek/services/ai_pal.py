#!/usr/bin/env python3

from cellaserv.service import Service, ConfigVariable
from cellaserv.proxy import CellaservProxy
import mraa
from math import pi
from time import sleep
from threading import Thread, Timer, Event

#from evolutek.services.task_maker import get_strat_orange
from task_maker import get_strat_orange

src_file_strat = "strat_test"

@Service.require("trajman", "pal")
class Ai(Service):

    # Init of the PAL
    def __init__(self):
        print("Init")
        super().__init__()
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman['pal']
        self.color = self.cs.config.get(section='match', option='color')  #set a boolean instead ?
        # Set Timer
        self.stop_timer = Timer(100, self.match_stop)
        # Thread for the match
        self.match_thread = Thread(target=self.start)

        # Stopped event
        self.stopped = Event()

        # All objectives
        self.tasks = get_strat_orange()
       #get_startegy(src_file_strat, self.color = 'green')

        self.setup()

    # Setup PAL position
    def setup(self):
        print("Setup")
        self.trajman.free()
        self.trajman.set_theta(-pi/2)
        self.trajman.set_x(483)
        self.trajman.set_y(2750)
        self.trajman['pal'].unfree()
        print("Setup complete, waiting to receive match_start")

    # Start Event
    @Service.event
    def match_start(self):
        print("Go")
        self.stop_timer.start()
        self.match_thread.start()

    # Avoid the obstacle
    @Service.event
    def avoid(self):
        if not self.tasks[0].not_avoid:
            print("avoid")
            self.trajman['pal'].free()
            self.stopped.set()

    @Service.event
    def end_avoid(self):
        print("end avoid")
        self.stopped.clear()

    # End of the match
    def match_stop(self):
        print("Stop")
        self.trajman['pal'].free()
        self.trajman['pal'].disable()

    # Start of the match
    def start(self):
        print("Starting the match")

        while not self.tasks.is_empty():
            if self.stopped.isSet(): # there's an obstacle
                continue

            if self.tasks[0].speed:
                self.set_speed(self.tasks[o].speed)

            self.goto_xy(self.tasks[0].x, self.tasks[0].y)
            if self.stopped.isSet(): # there's an obstacle
                continue

            if self.tasks[0].theta: # robot arrived at destination
                self.goto_theta(self.tasks[0].theta)

                if self.tasks[0].action:
                    self.tasks[0].action()

                self.tasks.get()
        print("Match is finished")

    # Go to x y position
    def goto_xy(self, x, y):
        self.trajman.goto_xy(x=x, y=y)
        while self.trajman.is_moving():
            continue

    # Do a movement in tranlation
    def move_trsl(self, len):
        self.trajman.move_trsl(len, 10, 10, 10, 0)
        while self.trajman.is_moving():
            continue

    # Go to theta
    def goto_theta(self, theta):
        self.trajman.goto_theta(theta=theta)
        while self.trajman.is_moving():
            continue

    # Set max speed
    def set_speed(self, speed):
        self.trajman.set_trsl_max_speed(speed)

def main():
    ai = Ai()
    ai.run()

if __name__  == '__main__':
    main()
