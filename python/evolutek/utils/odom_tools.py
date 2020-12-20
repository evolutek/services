#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot
from evolutek.utils.shell.data_printer import print_json

from argparse import ArgumentParser
from math import pi
from time import sleep

cs = None
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

    input()

    # TODO path 75, in move_trsl_block
    robot.recalibration_block(sens=0)
    robot.move_trsl_block(dest=100, acc=500, dec=500, maxspeed=500, sens=1)

    print("#########################################################")
    print("Do you want the robot to go to the mark by itself (y/n) ?")
    print("#########################################################")

    i = input()
    # TODO : Manual

    robot.move_trsl_block(dest=length, acc=speeds['tracc'], dec=speeds['trdec'], maxspeed=200, sens=1)
    robot.move_rot_block(dest=pi, acc=3, dec=3, maxspeed=3, sens=1)
    robot.move_trsl_block(dest=length, acc=speeds['tracc'], dec=speeds['trdec'], maxspeed=200, sens=1)
    robot.move_rot_block(dest=pi, acc=3, dec=3, maxspeed=3, sens=0)

    print(robot.tm.get_position())
    #robot.recalibration_block(sens=0, decal=0, set=0)
    robot.tm.move_trsl(dest=150, acc=500, dec=500, maxspeed=500, sens=0)

    sleep(1)

    newpos = robot.tm.get_position()

    print(newpos)
    robot.tm.free()

    coef = - newpos['theta'] / (2 * length + 200)

    print('The delta of theta is :', newpos['theta'])
    print('The computed coef is :', coef)

    global old
    old['left_gain'] = old['left_gain'] * (1 + coef)
    old['right_gain'] = old['right_gain'] * (1 - coef)

    print('The news gains are :', old['left_gain'], old['right_gain'])


""" Compute Diameters """
def compute_diams():
    print("########################################################")
    print("Please enter the length of the distance to mesure (mm) :")
    print("########################################################")

    length = float(input())
    print("Length = ", length)

    print("########################################################################")
    print("Please place the robot with the back near a wall, press Enter when ready")
    print("########################################################################")

    input()

    print(robot.tm.get_position())
    robot.recalibration_block(sens=0)
    print(robot.tm.get_position())

    print("#########################################################")
    print("Do you want the robot to go to the mark by itself (y/n) ?")
    print("#########################################################")

    i = input()
    oldpos = robot.tm.get_position()

    if i[0] == 'y':
        print("Going...")
        robot.move_trsl_block(dest=length, acc=100, dec=100, maxspeed=100, sens=1)

    robot.tm.free()
    sleep(0.1)

    print("#################################################################")
    print("Please place the robot on the second mark, press Enter when ready")
    print("#################################################################")

    input()

    robot.tm.unfree()
    newpos = robot.tm.get_position()

    print(oldpos)
    print(newpos)

    mesured = newpos['x'] - oldpos['x']
    print(mesured)
    coef = float(length) / float(mesured)

    global old
    diameter  = old['left_diameter'] / old['left_gain'] * coef
    old['left_diameter'] = diameter * old['left_gain']
    old['right_diameter'] = diameter * old['right_gain']

    print("The error was of :", length - mesured)
    print("The new diameter is :", diameter)
    print("The new diameters are :", old['left_diameter'], old['right_diameter'])
    print("Setting the new diameters")
    robot.tm.set_wheels_diameter(w1=old['left_diameter'] ,w2=old['right_diameter'])
    sleep(.1)

    print("#################################################")
    print("Going back to the origin, press Enter when ready.")
    print("#################################################")
    input()

    robot.move_trsl_block(dest=length, acc=speeds['tracc'], dec=speeds['trdec'], maxspeed=100, sens=0)
    robot.tm.free()


""" Compute Spacing """
def compute_spacing():
    print("##########################################")
    print("Please enter the number of turns to mesure")
    print("##########################################")

    nbturns = float(input())
    print("nbturns = ", nbturns)

    print("##########################################################")
    print("Please place the robot on the mark, press Enter when ready")
    print("##########################################################")

    input()

    robot.tm.unfree()

    print("#######################################################")
    print("Do you want the robot to do the turns by itself (y/n) ?")
    print("#######################################################")

    i = input()

    oldpos = robot.tm.get_position()

    if i[0] == 'y':
        print("Going...")
        robot.move_rot_block(dest=2 * nbturns * pi, acc=3, dec=3, maxspeed=3, sens=1)
        sleep(0.1)
        robot.tm.free()
        print("############################################################")
        print("Please replace the robot on the mark, press Enter when ready")
        print("############################################################")
    else:
        robot.tm.free()
        print("################################################################")
        print("Please make the robot do turns on itself, press Enter when ready")
        print("################################################################")

    input()

    newpos = robot.tm.get_position()
    mesured = newpos['theta'] - oldpos['theta'] + nbturns * pi
    coef = float(mesured) / float(nbturns * pi)

    global old
    old['spacing'] = old['spacing'] * coef

    print("The error was of :", newpos['theta'] - oldpos['theta'])
    print("The new spacing is :", old['spacing'])
    print("Setting the new spacing")

    robot.tm.set_wheels_spacing(spacing=old['spacing'])

    print("#################################################")
    print("Going back to the origin, press Enter when ready.")
    print("#################################################")
    input()

    robot.move_rot_block(dest=2 * nbturns * pi, acc=3, dec=3, maxspeed=3, sens=0)
    robot.tm.free()

def compute_all(gains, diams, spacing, all, config, _robot):

    robot_name = _robot

    global cs
    cs = CellaservProxy()
    global robot
    robot = Robot(robot_name)
    global old
    old = robot.tm.get_wheels()
    global speeds
    speeds = robot.tm.get_speeds()

    old['left_gain'] = float(cs.config.get(section=robot_name, option='wheel_gain1'))
    old['right_gain'] = float(cs.config.get(section=robot_name, option='wheel_gain2'))

    if not gains and not diams and not spacing:
        all = True

    print("###############################################################")
    print("## Hi ! and welcome to the wheels size computing assistant ! ##")
    print("###############################################################")

    if all:
        print('It will compute everything: gains, diameters and spacing')
    else:
        if gains:
            print('It will compute gains')
        if diams:
            print('It will compute diams')
        if spacing:
            print('It will compute spacing')

    print("Press enter when ready")
    input()

    robot.set_pos(x=1000, y=1000, theta=0)

    if all or gains:
        compute_gains()

    if all or diams:
        compute_diams()

    if all or spacing:
        compute_spacing()

    if config:
        print("##############################")
        print("Setting new values to config !")
        print("##############################")

        cs.config.set(section=robot_name, option='wheel_diam1', value=str(old['left_diameter']))
        cs.config.set(section=robot_name, option='wheel_diam2', value=str(old['right_diameter']))
        cs.config.set(section=robot_name, option='wheel_gain1', value=str(old['left_gain']))
        cs.config.set(section=robot_name, option='wheel_gain2', value=str(old['right_gain']))
        cs.config.set(section=robot_name, option='spacing', value=str(old['spacing']))

    print("##################################")
    print("## Computing wheels size done ! ##")
    print("##################################")
    print_json(old)


def main():
    parser = ArgumentParser(description='Configuration of the odometry of the robot')
    parser.add_argument("robot", help="Robot to configure")
    parser.add_argument("-g", "--gains", help="Compute wheels gains of the robot", action="store_true")
    parser.add_argument("-d", "--diams", help="Compute wheels diameters of the robot", action="store_true")
    parser.add_argument("-s", "--spacing", help="Compute wheels spacing of the robot", action="store_true")
    parser.add_argument("-a", "--all", help="Compute all odom of the robot", action="store_true")
    parser.add_argument("-c", "--config", help="Set new values to config", action="store_true")


    args = parser.parse_args()

    if args.robot not in ['pal', 'pmi']:
        print('Unknow robot')
        print('Available robot: [pal, pmi]')
        return 1

    compute_all(args.gains, args.diams, args.spacing, args.all, args.config, args.robot)

if __name__ == "__main__":
    main()
