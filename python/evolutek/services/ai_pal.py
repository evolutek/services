#!/usr/bin/env python3

from cellaserv.service import Service, ConfigVariable
from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep
from threading import Thread, Timer, Event

#from evolutek.services.task_maker import get_strat
from task_maker import get_strat
from watchdog import Watchdog

src_file_strat = "strat_test"

@Service.require("trajman", "pal")
class Ai(Service):

    # Init of the PAL
    def __init__(self):
        print("Init")
        super().__init__('pal')
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman['pal']
        self.color = self.cs.config.get(section='match', option='color')

        # Set Timer
        self.stop_timer = Timer(100, self.match_stop)
        # Thread for the match
        self.match_thread = Thread(target=self.start)

        self.started = False
        # Stopped event
        self.stopped = Event()
        # Watch dog for avoiding
        self.watchdog = Watchdog(2, self.end_avoid)

        # All objectives
        self.tasks = get_strat()
        self.curr = None

        # Setup Trajman
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

    # Starting of the match
    @Service.event
    def match_start(self):
        print("Go")
        self.stop_timer.start()
        self.started = True
        self.match_thread.start()

    # Ending of the match
    def match_stop(self):
        print("Stop")
        self.trajman['pal'].free()
        self.trajman['pal'].disable()
        quit()

    # Avoid front obstacle
    @Service.event
    def front_avoid(self):
        if not self.started:
            return
        print('front')
        if self.stopped.isSet():
            print('Already stopped')
            avoid()
        print('Check moving_side')
        moving_side = self.trajman.get_vector_trsl()['trsl_vector']
        print('moving_side: ' + str(moving_side))
        if moving_side > 0.0:
            self.avoid()

    # Avoid back obstacle
    @Service.event
    def back_avoid(self):
        if not self.started:
            return
        print('back')
        if self.stopped.isSet():
            print('Already stopped')
            avoid()
        print('Check moving_side')
        moving_side = self.trajman.get_vector_trsl()['trsl_vector']
        print('moving_side: ' + str(moving_side))
        if moving_side < 0.0:
            self.avoid()

    def avoid(self):
        if self.stopped.isSet():
            print('Already stopped')
            self.watchdog.reset()
        elif self.curr and not self.curr.not_avoid:
            print("avoid")
            self.trajman['pal'].stop_asap(50, 50)
            self.stopped.set()
            self.watchdog.reset()

    def end_avoid(self):
        print("end avoid")
        self.stopped.clear()

    # Start of the match
    def start(self):
        print("Starting the match")

        while not self.tasks.empty() or self.curr:
            
            sleep(2)

            # We are avoiding
            if self.stopped.isSet():
                continue

            # New task
            if not self.curr and not self.tasks.empty():
                self.curr = self.tasks.get()
                if self.curr.speed:
                    self.set_speed(self.curr.speed)

            if not self.curr:
                continue

            print("x: " + str(self.curr.x) + " y: " + str(self.curr.y))
            self.goto_xy(self.curr.x, self.curr.y)

            # We were stopped
            if self.stopped.isSet():
                continue

            position = self.trajman.get_position()

            if abs(position['x'] - self.curr.x) > 2.0 or abs(position['y'] - self.curr.y) > 2.0:
                print('not here')
                continue

            # We can rotate
            if self.curr.theta:
                print("theta: "+ str(self.curr.theta))
                self.goto_theta(self.curr.theta)

            # We can do an action
            if self.curr.action:
                self.curr.action()

            # Current task is finish
            self.curr = None


        # We have done all our tasks
        print("Match is finished")

    # Go to x y position
    def goto_xy(self, x, y):
        self.trajman.goto_xy(x=x, y=y)
        while self.trajman.is_moving():
            sleep(0.5)

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
