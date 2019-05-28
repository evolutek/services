#!/usr/bin/#!/usr/bin/env python3

from evolutek.lib.robot import Robot
from math import pi

def main():

    robot = Robot(robot='pal')

    """robot.recalibration(init=True)

    for i in range(10):
        robot.goto_avoid(250, 250)
        robot.goto_avoid(500, 250)"""

    robot.tm.free()
    robot.tm.set_x(750)
    robot.tm.set_y(330)
    robot.tm.set_theta(pi/2)

    robot.goto_with_path(750, 2300)

    print('End test')

if __name__ == "__main__":
    main()
