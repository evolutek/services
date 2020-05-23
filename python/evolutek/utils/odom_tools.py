#!/usr/bin/env python3

from evolutek.lib.robot import Robot

from argparse import ArgumentParser
from math import pi

robot = None
speeds = {}
old = {}


""" Compute Gains """
def compute_gains():
    print("########################################################")
    print("Please enter the length of the distance to mesure (mm) :")
    print("########################################################")

    length = float(input())
    print("Length = ", length)

    print("########################################################################")
    print("Please place the robot with the back near a wall, press Enter when ready")
    print("########################################################################")

    robot.recalibration(y = False, init=True)
    robot.move_trsl_block(dest=lenth, acc=speeds['tracc'], dec=speeds['trdec'], maxspeed=100, sense=1)
    robot.move_rot_block(dest=pi, acc=3, dec=3, maxspeed=3)
    robot.move_trsl_block(dest=lenth, acc=speeds['tracc'], dec=speeds['trdec'], maxspeed=100, sense=1)
    robot.move_rot_block(dest=pi, acc=3, dec=3, maxspeed=3)
    robot.recalibration(y = False, init=True)

    #TODO: disable reset theta
    robot.tm.recalibration_block(sens=0, decal=0)
    robot.tm.unfree()

    newpos = robot.tm.get_position()
    robot.free()

    coef = -1 * newpos['theta'] / length

    print('The delta of theta is :', -1 * newpos['theta'])
    print('The computed coef is :', coef)

    left_gain = old['left_gain'] * (1 + coef)
    right_gain = old['right_gain'] * (1 - coef)

    print('The news gains are :', left_gain, right_gain)

    robot.tm.set_wheels_gains(g1=left_gain, g2=right_gain)
    sleep(0.1)


""" Compute Diameters """
def compute_diams():
    print("########################################################")
    print("Please enter the length of the distance to mesure (mm) :")
    print("########################################################")

    length = float(input)
    print("Length = ", length)

    print("########################################################################")
    print("Please place the robot with the back near a wall, press Enter when ready")
    print("########################################################################")

    robot.recalibration(y = False, init=True)

    print("################################################################")
    print("Do you want the robot to go to the mark by itself (y/n) ?")
    print("################################################################")

    if input()[0] == 'y':
        print("Going...")
        robot.move_trsl_block(dest=lenth, acc=speeds['tracc'], dec=speeds['trdec'], maxspeed=100, sense=1)

    robot.tm.free()
    sleep(0.1)

    print("################################################################")
    print("Do you want the robot to go to the mark by itself (y/n) ?")
    print("################################################################")

    if input()[0] == 'y':
        print("Going...")
        robot.goto_xy_block(1000 + length, 1000)
    sleep(0.1)
    robot.tm.free()

    print("#################################################################")
    print("Please place the robot on the second mark, press Enter when ready")
    print("#################################################################")

    input()

    robot.tm.unfree()
    newpos = robot.tm.get_position()

    mesured = newpos['x'] - 1000
    coef = float(length) / float(mesured)

    left_diameter = old['left_diameter'] * coef
    right_diameter = old['right_diameter'] * coef

    print("The error was of :", length - mesured)
    print("The new diameters are :", left_diameter, right_diameter)
    print("Setting the new diameters")
    robot.tm.set_wheels_diameter(w1=left_diameter ,w2=right_diameter)
    sleep(.1)

    print("#################################################")
    print("Going back to the origin, press Enter when ready.")
    print("#################################################")
    input()

    robot.move_trsl_block(dest=lenth, acc=speeds['tracc'], dec=speeds['trdec'], maxspeed=100, sense=0)
    robot.tm.free()


""" Compute Spacing """
def compute_spacing():
    print("##########################################")
    print("Please enter the number of turns to mesure")
    print("##########################################")

    nbturns = float(input())
    print("nbturns = ", nbturns)

    print("########################################################################")
    print("Please place the robot with the back near a wall, press Enter when ready")
    print("########################################################################")

    robot.recalibration(y = False, init=True)

    print("#######################################################")
    print("Do you want the robot to do the turns by itself (y/n) ?")
    print("#######################################################")

    if input()[0] == 'y':
        print("Going...")
        robot.move_rot_block(dest=2 * nbturns * math.pi, acc=3, dec=3, maxspeed=3, sens=1)
        sleep(0.1)
        robot.tm.free()
        print("############################################################")
        print("Please replace the robot on the mark, press Enter when ready")
        print("############################################################")
    else:
        print("################################################################")
        print("Please make the robot do turns on itself, press Enter when ready")
        print("################################################################")

    input()

    newpos = robot.tm.get_position()
    mesured = newpos['theta'] + nbturns * math.pi
    coef = float(mesured) / float(nbturns * math.pi)
    spacing = old['spacing'] * coef

    print("The error was of :", newpos['theta'])
    print("The new spacing is :", spacing)
    print("Setting the new spacing")

    robot.tm.set_wheels_spacing(spacing=spacing)
    robot.move_rot_block(dest=nbturns * math.pi, acc=3, dec=3, maxspeed=3, sens=0)
    robot.tm.free()

def main():
    parser = ArgumentParser(description='Configuration of the odometry of the robot')
    parser.add_argument("robot", help="Robot to configure")
    parser.add_argument("-g", "--gains", help="Compute wheels gains of the robot", action="store_true")
    parser.add_argument("-d", "--diams", help="Compute wheels diameters of the robot", action="store_true")
    parser.add_argument("-s", "--spacing", help="Compute wheels spacing of the robot", action="store_true")
    parser.add_argument("-a", "--all", help="Compute all odom of the robot", action="store_true")

    args = parser.parse_args()

    if args.robot not in ['pal', 'pmi']:
        print('Unknow robot')
        print('Available robot: [pal, pmi]')
        return 1

    print("###############################################################")
    print("## Hi ! and welcome to the wheels size computing assistant ! ##")
    print("###############################################################")
    print("Press enter when ready")
    input()

    global robot
    robot = Robot(args.robot)
    global old
    old = robot.tm.get_wheels()
    global speeds
    speeds = robot.tm.get_speeds()

    if args.all or args.gains:
        compute_gains()

    if args.all or args.diams:
        compute_diams()

    if args.all or args.spacing:
        compute_spacing()

    print("#############################################")
    print("## GO TO THE MOTOR CARD AND SET THE VALUES ##")
    print("#############################################")
    print(robot.tm.get_wheels())

if __name__ == "__main__":
    main()
