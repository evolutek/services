from math import pi
from sys import argv

from cellaserv.proxy import CellaservProxy
from evolutek.lib.gpio import Edge, Gpio
from evolutek.lib.robot import Point, Robot

cs = CellaservProxy()
ROBOT = None
robot = None


def go_home(robot):
    if robot == "pal":
        point = Point(620, 120)
    else:
        point = Point(960, 120)
    robot.go_home(point, pi / 2)


def main():
    selected_robot = argv[1]
    if not selected_robot in ["pal", "pmi"]:
        print("select a valid robot")
        return

    global ROBOT
    ROBOT = selected_robot
    global robot
    robot = Robot(selected_robot)
    go_home(robot)


if __name__ == "__main__":
    main()
