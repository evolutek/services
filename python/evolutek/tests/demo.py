#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot

from math import pi
from sys import argv
from time import sleep

cs = CellaservProxy()
ROBOT = None
robot = None

def translate(dest, acc, dec, maxspeed, sens, block):
    robot.tm.move_trsl(dest, acc, dec, maxspeed, sens) if not block else robot.move_trsl_block(dest, acc, dec, maxspeed, sens)

def rotate(dest, acc, dec, maxspeed, sens):
    robot.tm.move_rot(dest, acc, dec, maxspeed, sens)

def move_ax(id, pos):
    cs.ax["%s-%d" % (ROBOT, id)].move(goal=pos)

def dance_demo():

    pos_left_arm = 820
    pos_right_arm = 204
    translate(100, 400, 400, 500, True, True)
    translate(100, 400, 400, 500, False, True)
    rotate(pi * 8, 5, 5, 3, True)
    for i in range (8):
        move_ax(3, 630)
        move_ax(4, 630)
        cs.actuators[ROBOT].left_cup_holder_close()
        cs.actuators[ROBOT].right_cup_holder_open()
        sleep(0.5)
        move_ax(3, 480)
        move_ax(4, 480)
        cs.actuators[ROBOT].left_cup_holder_open()
        cs.actuators[ROBOT].right_cup_holder_close()
        sleep(0.5)
    cs.actuators[ROBOT].left_arm_close()
    cs.actuators[ROBOT].right_arm_close()
    cs.actuators[ROBOT].left_cup_holder_close()
    sleep(1.5)
    cs.actuators[ROBOT].flags_raise()
    sleep(2)
    cs.actuators[ROBOT].flags_low()

def main():
    if not argv[1] in ['pal', 'pmi']:
        return
    
    global ROBOT
    ROBOT = argv[1]
    global robot
    robot = Robot(argv[1])
    dance_demo()

if __name__ == '__main__':
    main()
    
