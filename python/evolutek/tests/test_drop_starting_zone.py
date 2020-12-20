from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot

from math import pi
from time import sleep

cs = CellaservProxy()
robot = Robot.get_instance('pmi')
actuators = cs.actuators['pmi']

# Flip = ANCHROAGE XOR SIDE
flip = False

# Need the robot to be in (800, 200, 0)
def init_drop():
    robot.goto_theta_block(pi/2)
    robot.recalibration(x=False)
    robot.goto_xy_block(800, 300)
    robot.goto_theta_block(pi if flip else 0) # Depend on the anchorage

# Suppose we are in (800, 300, 0)
def drop_south_buoys():
    robot.move_trsl_block(150, 500, 500, 500, 1)
    actuators.pump_drop(pump=3 if flip else 1) # Depend of flip
    actuators.pump_drop(pump=4 if flip else 2) # Depend of flip
    robot.move_trsl_block(200, 800, 800, 800, 0)

    robot.goto_theta_block(pi/2)
    robot.move_trsl_block(100, 500, 500, 500, 0)
    robot.goto_theta_block(0 if flip else pi) #depend of anchorage

    actuators.left_cup_holder_open()
    actuators.right_cup_holder_open()
    sleep(1.5)
    robot.move_trsl_block(120, 300, 300, 300, 0)
    sleep(1)
    actuators.pump_drop(pump=5 if flip else 6) #depend of flip
    actuators.pump_drop(pump=7 if flip else 8) #depend of flip
    robot.move_trsl_block(150, 800, 800, 800, 1)

    robot.move_trsl_block(375, 500, 500, 500, 1)
    robot.goto_theta_block(0 if flip else pi) #depend of flip

# Suppose we are in (325, 200, pi)
def drop_north_buoys():
    actuators.pump_drop(pump=6 if flip else 5) #depend of flip
    actuators.pump_drop(pump=8 if flip else 7) #depend of flip
    robot.move_trsl_block(100, 800, 800, 800, 1)
    actuators.left_cup_holder_close()
    actuators.right_cup_holder_close()
    sleep(1.5)

    robot.goto_theta_block(pi/2)
    robot.move_trsl_block(225, 500, 500, 500, 1)
    robot.goto_theta_block(pi if flip else 0) #depend of flip


    robot.move_trsl_block(150, 300, 300, 300, 1)
    actuators.pump_drop(pump=1 if flip else 3) #depend of flip
    actuators.pump_drop(pump=2 if flip else 4) #depend of flip
    robot.move_trsl_block(125, 800, 800, 800, 0)

def end_match():
    robot.goto_theta_block(pi/2)
    robot.move_trsl_block(200, 500, 500, 500, 0)
    robot.recalibration_block(0)
    actuators.flags_raise()


if __name__ == "__main__":

    robot.tm.disable_avoid()
    robot.tm.free()
    actuators.pump_get(pump=1, buoy='red')
    actuators.pump_get(pump=2, buoy='red')
    actuators.pump_get(pump=3, buoy='red')
    actuators.pump_get(pump=4, buoy='green')
    actuators.pump_get(pump=5, buoy='green')
    actuators.pump_get(pump=6, buoy='green')
    actuators.pump_get(pump=7, buoy='green')
    actuators.pump_get(pump=8, buoy='green')
    print('Please place buoys and the robot and press a key to continue')
    input()

    robot.set_pos(800, 200, 0)
    robot.tm.unfree()

    print('Starting init')
    init_drop()

    print('Press a key to continue')
    input()
    print('Executing drop front')
    drop_south_buoys()

    print('Press a key to continue')
    input()
    drop_north_buoys()

    input()
    end_match()

    print('End testing')
