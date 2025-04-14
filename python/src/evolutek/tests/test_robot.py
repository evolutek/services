#!/usr/bin/#!/usr/bin/env python3

from evolutek.lib.robot import Robot
from math import pi
from time import sleep

def main():

    robot = Robot(robot='pal')

    #robot.recalibration(init=True)

    robot.tm.free()
    robot.set_pos(250, 250, pi)

    sleep(2)

    #robot.goto(x=850, y=1750)

    """for i in range(10):
        print(robot.goto_avoid(250, 250))
        print(robot.goto_avoid(1750, 2750))"""

    for i in range(10):
        print(robot.goto_with_path(1400, 2300))
        print(robot.goto_with_path(250, 250))

    print('End test')

if __name__ == "__main__":
    main()
