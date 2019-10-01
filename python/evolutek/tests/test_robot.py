#!/usr/bin/#!/usr/bin/env python3

from evolutek.lib.robot import Robot

def main():

    robot = Robot(robot='pal')

    robot.recalibration(init=True)

    for i in range(10):
        robot.goto_avoid(250, 250)
        robot.goto_avoid(500, 250)

    print('End test')

if __name__ == "__main__":
    main()
