#!/usr/bin/env python3
from time import sleep
import math
from threading import Thread, Timer, Event

from cellaserv.service import Service, Variable
from cellaserv.proxy import CellaservProxy
from robot import Robot


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
        self.cs('log.ia', msg="Setup done")
        if type(color) == str:
            if color[0] == "y":
                self.color = 1
            else:
                self.color = -1
        else:
            self.color = color

        self.robot.free()
        self.robot.set_x(142)
        self.robot.set_y(1500 + self.color * (1500 - 302/2 - 32))
        self.robot.set_theta(0)

        self.robot.set_trsl_dec(500)
        self.robot.set_trsl_acc(500)
        self.robot.set_pid_trsl(100, 0, 3000)
        self.robot.set_trsl_max_speed(500)

        self.robot.set_rot_acc(3)
        self.robot.set_rot_dec(3)
        self.robot.set_rot_max_speed(3)
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

        self.match_stop_timer.start()

        self.robot.goto_xy_block(600, 1500 + self.color * (1500 - 302/2 - 23))
        self.robot.goto_xy_block(1100, 1500 + self.color * 1100)
        self.cs('log.ia', message='Pushed first fire')
        self.robot.goto_theta_block(-math.pi)
        self.robot.goto_xy_block(600, 1500 + self.color * 1100)
        self.robot.goto_theta_block(math.pi / 2. * -self.color)
        self.robot.goto_xy_block(600, 1500)
        self.cs('log.ia', message='Pushed second fire')

        self.robot.goto_xy_block(600, 1500 + self.color * 150)
        speeds = self.cs.trajman.get_speeds()
        self.robot.set_trsl_max_speed(100)
        self.cs('log.ia', message='Going to scan pizzahut')

        self.robot.goto_theta_block(-math.pi)
        sleep(1)
        self.IDONTCAREABOUTPEOPLE = True
        #Starting back maneuver
        self.robot.goto_theta_block(0)

        #Going to fresque
        self.robot.set_trsl_max_speed(100)
        self.cs('log.ia', message='Going to apply pizzahut')
        self.robot.goto_xy_block(150, 1500 + self.color * 150)
        self.robot.goto_xy_block(140, 1500 + self.color * 150)
        self.cs('log.ia', message='Applied pizza hut trolol')
        self.robot.set_trsl_max_speed(speeds['trmax'])
        self.IDONTCAREABOUTPEOPLE = False

        #Going to the last fire
        self.robot.goto_xy_block(600, 1500 + self.color * 150)
        self.robot.goto_theta_block(math.pi / 2. * self.color)
        self.robot.goto_xy_block(600, 1500 + self.color * 400)
        self.robot.goto_theta_block(0)
        self.cs('log.ia', message='Last fire')
        self.robot.goto_xy_block(1600, 1500 + self.color * 400)
        self.robot.goto_theta_block(math.pi / 2. * self.color)
        self.robot.goto_xy_block(1600, 1500 + 600 * self.color)
        self.match_stop()
        return


        self.robot.goto_theta_block(math.pi / 2. * self.color)
        self.robot.goto_xy_block(1600, 1500 + self.color * 600)
        self.robot.goto_xy_block(1600, 1500 - self.color * 200)
        self.robot.goto_xy_block(600, 1500 - self.color * 600)
        self.robot.goto_xy_block(600, 1500 - self.color * 1200)

    # Called by a timer thread
    def match_stop(self):
        self.cs('log.ia', msg='Stopping robot')
        self.cs.trajman.free()
        self.cs.trajman.soft_free()

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
