#!/usr/bin/#!/usr/bin/env python3

from evolutek.lib.robot import Robot

def main():

    robot = Robot(robot='pal')
    robot.tm.set_x(0)
    robot.tm.set_y(0)
    robot.tm.set_theta(0)

    for i in range(10):
        robot.goto_avoid(250, 0)
        robot.goto_avoid(0, 0)

    print('End test')

if __name__ == "__main__":
    main()
