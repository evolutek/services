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

    actuators.pump_get(pump=4, buoy='green') # Depend of side
    robot.move_trsl_block(200, 500, 500, 500, 1)
    robot.goto_theta_block(-1 * pi/2)
    robot.move_trsl_block(50, 500, 500, 500, 1)
    robot.goto_theta_block(pi)

    actuators.pump_get(pump=1, buoy='red') # Depend of side
    robot.move_trsl_block(325, 500, 500, 500, 1)
    robot.move_trsl_block(150, 500, 500, 500, 0)
    robot.goto_xy_block(250, 880) # Depend of side
    robot.goto_theta_block(0)

# Suppose we are in (200, 850, 0)
def get_reef():
    actuators.left_cup_holder_open()
    actuators.right_cup_holder_open()
    sleep(1.5)
    actuators.pump_get(pump=5)
    actuators.pump_get(pump=6)
    actuators.pump_get(pump=7)
    actuators.pump_get(pump=8)
    robot.tm.move_trsl(400, 300, 300, 300, 0)
    sleep(2)
    robot.tm.free()
    sleep(1)
    actuators.left_cup_holder_close()
    actuators.right_cup_holder_close()
    sleep(1.5)
    robot.move_trsl_block(200, 300, 300, 300, 1)


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
    input()
    print('Getting reef')
    get_reef()

    print('Press a key to continue')
    input()
    print('going to center zone')
    robot.goto_xy_block(1400, 1900)
    robot.goto_theta_block(0)

    print('Press a key to continue')
    input()
    print('Starting init')
    init_drop()

    print('Press a key to continue')
    input()
    print('Executing drop front')
    drop_front_buoys()

    print('Press a key to continue')
    input()
    print('Executing drop back')
    drop_back_buoys()

    print('End testing')
