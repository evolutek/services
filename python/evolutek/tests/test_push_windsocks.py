from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot, Point
from evolutek.lib.gpio import Gpio, Edge

from sys import argv
from math import pi
from time import sleep

cs = CellaservProxy()
ROBOT = 'pmi'
robot = Robot.get_instance('pmi')

def push_windsocks(robot, ax) :
    #self.cs.ax["%s-%d" % (ROBOT, ax)].move(goal=512)

    cs.actuators[ROBOT].left_arm_open() if ax == 3 else cs.actuators[ROBOT].right_arm_open()


    # TODO config
    robot.tm.set_delta_max_rot(1)
    robot.tm.set_delta_max_trsl(500)

    robot.tm.move_trsl(dest=625, acc=800, dec=800, maxspeed=1000, sens=1)

    sleep(2)

    #self.cs.ax["%s-%d" % (ROBOT, ax)].move(goal=820 if ax != 3 else 210)
    cs.actuators[ROBOT].left_arm_close() if ax == 3 else cs.actuators[ROBOT].right_arm_close()

    robot.tm.set_delta_max_rot(0.2)
    robot.tm.set_delta_max_trsl(100)

    robot.move_trsl_block(100, 400, 400, 500, 0)


def test():
    robot.recalibration(init=True)
    robot.goto(1830, 200)
    robot.goth(pi / 2)
    robot.recalibration_block(sens=0)
    push_windsocks(robot, 4)


def main():
    selected_robot = argv[1]
    if not selected_robot in ['pal', 'pmi']:
        print("select a valid robot")
        return
    global ROBOT
    ROBOT = selected_robot
    global robot
    robot = Robot(selected_robot)
    test()

if __name__ == "__main__":
    main()
