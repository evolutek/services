#!/usr/bin/env python3

from cellaserv.service import Service, ConfigVariable
from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep
from threading import Thread, Timer, Event

from evolutek.lib.task_maker import *

@Service.require("trajman", "pal")
@Service.require("actuators", "pal")
@Service.require("gbts", "pal")
@Service.require("tirette")
class Ai(Service):

    # Init of the PAL
    def __init__(self):
        print("Init")
        super().__init__('pal')
        self.cs = CellaservProxy()
        self.trajman = self.cs.trajman['pal']
        self.gbts = self.cs.gbts['pal']
        self.actuators = self.cs.actuators['pal']
        self.color = self.cs.config.get(section='match', option='color')

        # Set Timer
        #TODO
        self.stop_timer = Timer(100, self.match_stop)
        # Thread for the match
        self.match_thread = Thread(target=self.start)

        # Stopped event
        self.front_stopped = Event()
        self.back_stopped = Event()

        # All objectives
        self.tasks = homologation()
        #self.tasks = get_strat(self.color, self.actuators, 'pal')
        self.curr = None
        
        # Setup Trajman
        self.setup()

    # Setup PAL position
    def setup(self):
        #TODO: do green
        sleep(10)
        print("Setup")
        self.trajman.free()
        self.trajman.set_x(750)
        self.trajman.set_y(300 if self.color == 'green' else 300)
        #self.trajman.set_x(500)
        #self.trajman.set_y(240 if self.color == 'green' else 2760)
        self.trajman.set_theta(-pi/2 if self.color == 'green' else pi/2)
        self.trajman.unfree()
        #self.actuators.init_all()
        print("Setup complete, waiting to receive match_start")

    # Starting of the match
    @Service.event
    def match_start(self):
        print("Go")
        self.stop_timer.start()
        self.gbts.set_avoiding(True)
        print("Gas Gas Gas")
        self.match_thread.start()

    # Ending of the match
    def match_stop(self):
        print("Stop")
        self.trajman['pal'].free()
        self.trajman['pal'].disable()
        self.actuators['pal'].disable()
        quit()

    # Avoid front obstacle
    @Service.event
    def front_avoid(self):
        print('Front detection')
        #print('Check moving_side')
        #moving_side = self.trajman.get_vector_trsl()
        #print('moving_side: ' + str(moving_side))
        #if moving_side['trsl_vector'] > 0.0:
        print("Avoid")
        self.trajman['pal'].stop_asap(1000, 30)
        self.front_stopped.set()

    # Avoid back obstacle
    @Service.event
    def back_avoid(self):
        print('Back detection')
        #print('Check moving_side')
        #moving_side = self.trajman.get_vector_trsl()
        #print('moving_side: ' + str(moving_side))
        #if moving_side['trsl_vector'] < 0.0:
        print("Avoid")
        self.trajman['pal'].stop_asap(1000, 30)
        self.back_stopped.set()

    @Service.event
    def front_end_avoid(self):
        print("Front end avoid")
        self.front_stopped.clear()

    @Service.event
    def back_end_avoid(self):
        print("Back end avoid")
        self.back_stopped.clear()

    # Start of the match
    def start(self):
        print("Starting the match")

        while not self.tasks.empty() or self.curr:

            sleep(1)

            # We are avoiding
            if self.front_stopped.isSet() or self.back_stopped.isSet():
                continue

            print('Get a new task')
            # New task
            if not self.curr and not self.tasks.empty():
                self.curr = self.tasks.get()
                if self.curr.speed:
                    self.set_speed(self.curr.speed)

            if not self.curr:
                print('No new task')
                break

            print(self.curr.not_avoid)
            if self.curr.not_avoid:
                print('Not avoiding')
                self.front_stopped.clear()
                self.back_stopped.clear()
                self.gbts.set_avoiding(False)
            else:
                print('Avoiding')
                self.gbts.set_avoiding(True)
            print("x: " + str(self.curr.x) + " y: " + str(self.curr.y))
            self.goto_xy(self.curr.x, self.curr.y)

            # We were stopped
            if self.front_stopped.isSet() or self.back_stopped.isSet():
                print('Avoiding')
                continue

            # We can rotate
            if self.curr.theta:
                print("theta: "+ str(self.curr.theta))
                self.goto_theta(self.curr.theta)

            # We can do an action
            print('Do an action')
            if self.curr.action:
                if self.curr.action_param:
                    self.curr.action(self.curr.action_param)
                else:
                    self.curr.action()

            # Current task is finish
            self.curr = None

        # We have done all our tasks
        self.trajman.free()
        print("Match is finished")

    # Go to x y position
    def goto_xy(self, x, y):
        self.trajman.goto_xy(x=x, y=y)
        while self.trajman.is_moving():
            print('Moving')
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
