#!/usr/bin/env python3
from threading import Thread, Timer, Event
from time import sleep
import math

from cellaserv.service import Service, Variable
from cellaserv.proxy import CellaservProxy
from robot import Robot
from objective import *

import pathfinding


class ia(Service):

    match_start = Variable()

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        self.match_stop_timer = Timer(85, self.match_stop)

        self.start_event = Event()

        self.robot = Robot()
        self.robot.setup()

        self.color = None
        self.IDONTCAREABOUTPEOPLE = False

    @Service.action
    def setup_match(self, color):
        pathfinding.Init(200, 300, 15)
        self.cs('log.ia', msg="Setup done")
        if type(color) == str:
            if color[0] == "y":
                self.color = 1
            else:
                self.color = -1
        else:
            self.color = color

        self.robot.free()
        self.objectives =\
        DefaultObjectives.generate_default_objectives(self.color)

        #self.robot.set_trsl_acc(1500)
        #self.robot.set_trsl_max_speed(900)
        #self.robot.set_trsl_dec(800)
        #self.robot.set_pid_trsl(200, 0, 2000)

        #self.robot.set_rot_acc(15)
        #self.robot.set_rot_dec(15)
        #self.robot.set_rot_max_speed(15)
        #self.robot.set_pid_rot(5000, 0, 25000)
        self.robot.unfree()

    @Service.action
    def status(self):
        return {'color': self.color,
                'started': self.match_start.is_set()}


    #TODO: Check this function as a color wrapper
    def goto_xy_block(self, x, y):
        if self.color == 1:
            self.robot.goto_xy_block(x, 3000 - y)
        else:
            self.robot.goto_xy_block(x, y)



    # Called in a separate thread
    def start(self):
        print("Waiting...")
        self.cs('log.ia', msg="Waiting")
        self.match_start.wait()
        print("Start!")
        self.cs('log.ia', msg="Match started")


        # TODO: UNCOMMENT BEFORE GOING TO THE COUPE DE FRANCE
        #self.match_stop_timer.start()

        self.robot.goto_xy_block(616, 1500 + self.color * (890))
        while len(self.objectives):
            pos = self.robot.get_position()
            print(pos)
            obj = self.objectives.get_best(pos['x'], pos['y'])
            print("going to obj " +  str(obj))
            self.robot.goto_xy_block(*(obj.get_position()))
            obj.execute(self.robot, self.cs)
            self.objectives.remove(obj)
            print("--------------------")
        print("DONE")

        self.match_stop()
        return



    # Called by a timer thread
    def match_stop(self):
        self.cs('log.ia', msg='Stopping robot')
        self.cs.trajman.free()
        self.cs.trajman.disable()

    @Service.event
    def robot_near(self):
        if self.match_start.is_set() and not self.IDONTCAREABOUTPEOPLE:
            self.cs('log.ia', msg='Detected robot near')
            self.match_stop()

def main():
    service = ia()
    service.setup()

    service_thread = Thread(target=service.start)
    service_thread.start()

    Service.loop()

if __name__ == '__main__':
    main()
