#!/usr/bin/env python3
import math
import turtle

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy

class Trajman(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()
        self.disabled = False

        self.speeds = {'trmax': 0}

        turtle.setup(height=300, width=200)
        turtle.speed('slowest')
        turtle.delay(5)
        turtle.bgpic('table2014.gif')

    @Service.action
    def goto_xy(self, x, y):
        x = int(x)/10 - 2000/10/2
        y = int(y)/10 - 3000/10/2
        print("x={x}, y={y}".format(x=x, y=y))
        turtle.goto(x=x, y=y)
        self.cs('robot_stopped')

    @Service.action
    def goto_theta(self, theta):
        turtle.setheading(float(theta) / math.pi * 180)
        self.cs('robot_stopped')

    @Service.action
    def move_trsl(self, dest, acc, dec, maxspeed, sens):
        raise Warning

    @Service.action
    def move_rot(self, dest, acc, dec, maxspeed, sens):
        raise Warning

    @Service.action
    def curve(self, dt, at, det, mt, st, dr, ar, der, mr, sr, delayed):
        raise Warning

    @Service.action
    def free(self):
        pass

    @Service.action
    def unfree(self):
        pass

    @Service.action
    def disable(self):
        self.disabled = True

    @Service.action
    def enable(self):
        self.disabled = False

    #######
    # Set #
    #######

    @Service.action
    def set_pid_trsl(self, P, I, D):
        pass

    @Service.action
    def set_pid_rot(self, P, I, D):
        pass

    @Service.action
    def set_debug(self, state):
        pass

    @Service.action
    def set_trsl_acc(self, acc):
        pass

    @Service.action
    def set_trsl_max_speed(self, maxspeed):
        self.speeds['trmax'] = maxspeed

    @Service.action
    def set_trsl_dec(self, dec):
        pass

    @Service.action
    def set_rot_acc(self, acc):
        pass

    @Service.action
    def set_rot_max_speed(self, maxspeed):
        pass

    @Service.action
    def set_rot_dec(self, dec):
        pass

    @Service.action
    def set_x(self, x):
        x = int(x)/10 - 2000/10/2
        print("x =", x)
        turtle.setx(x)

    @Service.action
    def set_y(self, y):
        y = int(y)/10 - 3000/10/2
        print("y =", y)
        turtle.sety(y)

    @Service.action
    def set_theta(self, theta):
        turtle.setheading(float(theta) * math.pi * 180)

    @Service.action
    def set_wheels_diameter(self, w1, w2):
        pass

    @Service.action
    def set_wheels_spacing(self, spacing):
        pass

    @Service.action
    def set_pwm(self, left, right):
        pass

    #######
    # Get #
    #######

    @Service.action
    def get_pid_trsl(self):
        return

    @Service.action
    def get_pid_rot(self):
        return

    @Service.action
    def get_position(self):
        return {
                "x": (turtle.xcor() + 2000/10/2) * 10,
                "y": (turtle.ycor() + 3000/10/2) * 10,
                "theta": 0,
                }

    @Service.action
    def get_speeds(self):
        return self.speeds

    @Service.action
    def get_wheels(self):
        return

    @Service.action
    def flush_serial(self):
        return

    @Service.action
    def init_sequence(self):
        pass

    @Service.action
    def flush_queue(self):
        pass

    @Service.action
    def is_moving(self):
        return False

    # Calibrate

    @Service.action
    def recalibration(self, sens):
        pass

def main():
    tm = Trajman()
    tm.run()

if __name__ == '__main__':
    main()
