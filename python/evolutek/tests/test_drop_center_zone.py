from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot

from math import pi
from time import sleep

cs = CellaservProxy()
robot = Robot.get_instance('pal')
actuators = cs.actuators['pal']

# side == True if yellow
side = False

# TODO : think more about back buoy drop

# Need the robot to be in (1400, 1900, 0)
def init_drop():
    actuators.pump_get(pump=3 if side else 2, buoy='red')
    robot.move_trsl_block(150, 500, 500, 500, 1)
    robot.goto_theta_block(pi/3 if side else -1 * pi / 3)
    actuators.pump_get(pump=2 if side else 3, buoy='green')
    robot.move_trsl_block(160, 500, 500, 500, 1)
    robot.move_trsl_block(60, 500, 500, 500, 0)
    robot.goto_theta_block(pi)
    robot.move_trsl_block(200, 500, 500, 500, 0)
    robot.recalibration(side_x=(False, True), side_y=(False, False), decal_y=1511)
    robot.goto_xy_block(1750, 1200 if side else 1800)
    robot.goto_theta_block(0)

# Suppose we are in (1750, 1800, 0)
def drop_front_buoys():
    robot.move_trsl_block(75, 500, 500, 500, 1)
    actuators.pump_drop(pump=1)
    actuators.pump_drop(pump=2)
    actuators.pump_drop(pump=3)
    actuators.pump_drop(pump=4)
    robot.move_trsl_block(75, 800, 800, 800, 0)
    robot.goto_xy_block(1725, 1200 if side else 1800)
    robot.goto_theta_block(0)

# Suppose we are in (1725, 1800, 0)
def drop_back_buoys():
    robot.goto_theta_block(-1 * pi/2 if side else pi/2)
    robot.move_trsl_block(100, 500, 500, 500, 1)

    # Drop green buoys
    actuators.left_cup_holder_open() # Depend of pattern
    actuators.right_cup_holder_open() # Depend of pattern
    sleep(1.5)    # TODO recompute
    actuators.pump_drop(pump=6 if side else 7) # Depend of pattern/side
    actuators.pump_drop(pump=7 if side else 6) # Depend of side
    robot.move_trsl_block(75, 800, 800, 800, 1)
    actuators.left_cup_holder_close()
    actuators.right_cup_holder_close()
    sleep(1.5)

    # Drop red buoys
    robot.goto_theta_block(pi)
    robot.move_trsl_block(50, 500, 500, 500, 1)

    if side:
        actuators.right_cup_holder_open()
    else:
        actuators.left_cup_holder_open()
    sleep(1.5)  # TODO recompute
    actuators.pump_drop(pump=8 if side else 5) # Depend of side
    robot.move_trsl_block(100, 800, 800, 800, 1)
    if side:
        actuators.right_cup_holder_close()
    else:
        actuators.left_cup_holder_close()
    sleep(1.5)


    robot.move_rot_block(pi/4, 5, 5, 5, side) # Depend of pattern(angle) and side(sens)
    actuators.left_cup_holder_open() # Depend of pattern
    actuators.right_cup_holder_open() # Depend of pattern
    sleep(1.5)  # TODO recompute
    actuators.pump_drop(pump=5 if side else 8) # Depend of pattern/side
    robot.move_trsl_block(100, 800, 800, 800, 1)
    actuators.left_cup_holder_close()
    actuators.right_cup_holder_close()

if __name__ == "__main__":
    robot.tm.disable_avoid()
    robot.tm.free()
    actuators.pump_get(pump=1, buoy='red')
    actuators.pump_get(pump=4, buoy='green')
    actuators.pump_get(pump=5, buoy='green')
    actuators.pump_get(pump=6, buoy='green')
    actuators.pump_get(pump=7, buoy='green')
    actuators.pump_get(pump=8, buoy='green')
    print('Please place buoys and the robot and press a key to continue')
    input()

    robot.set_pos(1400, 1100 if side else 1900, 0)
    robot.tm.unfree()

    print('Starting init')
    init_drop()

    print('Press a key to continue')
    input()
    print('Executing drop front')
    drop_front_buoys()

    print('Press a key to continue')
    input()
    drop_back_buoys()

    print('End testing')
