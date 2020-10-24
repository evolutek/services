from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot

from test_drop_center_zone import init_drop, drop_front_buoys, drop_back_buoys

from math import pi
from time import sleep

cs = CellaservProxy()
robot = Robot.get_instance('pal')
actuators = cs.actuators['pal']

# side == True if yellow
side = False

# TODO : think more about back buoy drop

# Need the robot to be in (700, 280, pi/2)
def init_get():
    robot.goto_xy_block(700, 830) # Depend of side
    robot.goto_theta_block(pi)

    actuators.get_reef_buoys()

    robot.goto_xy_block(250, 880) # Depend of side
    robot.goto_theta_block(0)

def init_robot(_robot):
    global robot
    robot = Robot.get_instance(_robot)
    global actuators
    actuators = cs.actuators[_robot]

if __name__ == "__main__":
    robot.tm.disable_avoid()
    robot.tm.free()
    print('Please place buoys and the robot and press a key to continue')
    input()

    robot.set_pos(700, 280, pi/2)
    robot.tm.unfree()

    print('Starting init')
    init_get()

    print('Press a key to continue')
    #input()
    print('Getting reef')
    actuators.get_reef()

    print('Press a key to continue')
    #input()
    print('going to center zone')
    robot.goto_xy_block(1400, 1900)
    robot.goto_theta_block(0)

    print('Press a key to continue')
    #input()
    print('Starting init')
    init_drop()

    print('Press a key to continue')
    #input()
    print('Executing drop front')
    drop_front_buoys()

    print('Press a key to continue')
    #input()
    print('Executing drop back')
    drop_back_buoys()

    print('Press a key to continue')
    #input()
    print('Going back to base')
    robot.goto_xy_block(800, 700) #Depend of side
    robot.goto_theta_block(pi) #Depend of anchorage
    robot.move_trsl_block(500, 500, 500, 500, 1)
    robot.goto_theta_block(pi/2) #Depend of side
    sleep(10)
    robot.move_trsl_block(500, 500, 500, 500, 0)
    robot.recalibration_block(0)
    actuators.flags_raise()

    print('End testing')
