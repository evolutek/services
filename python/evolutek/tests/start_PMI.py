from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot

from test_drop_starting_zone import drop_south_buoys, drop_north_buoys, end_match, init_drop
from test_push_windsocks import push_windsocks
from get_first_buoys import get_reef, init_robot

from math import pi
from time import sleep

cs = CellaservProxy()
robot = Robot.get_instance('pmi')
actuators = cs.actuators['pmi']

# side == True if yellow
side = False

# TODO : think more about back buoy drop

# Need the robot to be in (980, 260, pi)
def init_get():
    robot.goto_xy_block(800, 260) # Depend of side
    robot.goto_theta_block(pi/2)
    robot.move_trsl_block(70, 500, 500, 500, 1)
    robot.goto_theta_block(pi)


# Suppose we are in (800, 330)
def get_first_buoys():
    actuators.pump_get(pump=4, buoy='green') # Depend of side
    actuators.pump_get(pump=2, buoy='red') # Depend of side
    robot.move_trsl_block(425, 500, 500, 500, 1)


    #input()
    robot.goto_theta_block(0)
    actuators.right_cup_holder_open()
    sleep(1.5)
    robot.move_trsl_block(300, 300, 300, 300, 0)
    robot.tm.free()

    #input()
    robot.move_trsl_block(300, 300, 300, 300, 1)
    actuators.right_cup_holder_close()
    sleep(1.5)
    robot.goto_xy_block(800, 330)
    robot.goto_theta_block(0)

# Suppose we are in (800, 330, 0)
def get_next_buoys():
    actuators.pump_get(pump=3, buoy='green') # Depend of side
    actuators.pump_get(pump=1, buoy='red') # Depend of side
    robot.move_trsl_block(400, 500, 500, 500, 1)

    #input()
    robot.goto_xy_block(1700, 300)

# Suppose we are in (1700, 300)
def _push_windsocks():
    robot.goto_theta_block(3 * pi /4) # depend of side
    robot.goto_xy_block(1825, 175) # depend of side
    robot.goto_theta_block(pi/2)

    #input()
    robot.recalibration_block(0)
    push_windsocks(robot, 4) # depend of side

    #input()
    robot.move_trsl_block(200, 500, 500, 500, 0)
    robot.goto_theta_block(pi) # depend of side
    robot.recalibration(y=False, side_x=(False, True))
    robot.goto_theta_block(pi/2) # depend of side
    robot.goto_xy_block(1640, 250) #depend of side
    robot.goto_theta_block(pi/2) # depend of side


if __name__ == "__main__":
    robot.tm.disable_avoid()
    robot.tm.free()
    print('Please place buoys and the robot and press a key to continue')
    input()

    robot.set_pos(980, 260, pi)
    robot.tm.unfree()

    print('Starting init')
    sleep(3)
    init_get()

    print('Press a key to continue')
    #input()
    print('Get first buoy')
    get_first_buoys()

    print('Press a key to continue')
    #input()
    print('Get next buoy')
    get_next_buoys()

    print('Press a key to continue')
    #input()
    print('Push windsocks')
    _push_windsocks()

    print('Press a key to continue')
    #input()
    print('Get reef')
    init_robot('pmi')
    get_reef()
    robot.goto_xy_block(800, 300)

    print('Press a key to continue')
    #input()
    print('Init drop')
    init_drop()

    print('Press a key to continue')
    #input()
    print('Executing drop front')
    drop_south_buoys()

    print('Press a key to continue')
    #input()
    drop_north_buoys()

    #input()
    end_match()

    print('End testing')
