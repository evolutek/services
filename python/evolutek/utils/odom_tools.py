#!/usr/bin/env python3

from cellaserv.proxy import CellaservProxy
from evolutek.utils.shell.data_printer import print_json

from argparse import ArgumentParser
from math import pi
from time import sleep


cs = None
robot = '' # pal or pmi
speeds = {}
old = {}


""" Compute Diameters """
def compute_diams():
    print("########################################################")
    print("Please enter the length of the distance to mesure (mm) :")
    print("########################################################")

    success = False
    while not success:
        try:
            length = float(input())
            success = True
        except:
            print("Try again")
    print("Length = ", length)

    print("########################################################################")
    print("Please place the robot with the back near a wall, press Enter when ready")
    print("########################################################################")

    input()

    print(cs.trajman[robot].get_position())
    cs.trajman[robot].recalibration(sens=0)
    sleep(3)
    print(cs.trajman[robot].get_position())

    print("#########################################################")
    print("Do you want the robot to go to the mark by itself (y/n) ?")
    print("#########################################################")

    i = input()
    oldpos = cs.trajman[robot].get_position()

    if i[0] == 'y':
        print("Going...")
        cs.trajman[robot].move_trsl(dest=length, acc=100, dec=100, maxspeed=100, sens=1)
        sleep(length/100 + 2)

    cs.trajman[robot].free()
    sleep(0.1)

    print("#################################################################")
    print("Please place the robot on the second mark, press Enter when ready")
    print("#################################################################")

    input()

    cs.trajman[robot].unfree()
    newpos = cs.trajman[robot].get_position()

    print(oldpos)
    print(newpos)

    mesured = newpos['x'] - oldpos['x']
    print(mesured)
    coef = float(length) / float(mesured)

    global old
    diameter = ((old['left_diameter'] + old['right_diameter']) / 2) * coef

    print("The error was of :", length - mesured)
    print("The new diameter is :", diameter)
    print("The new diameters are :", old['left_diameter'], old['right_diameter'])
    print("Setting the new diameters")
    cs.trajman[robot].set_wheels_diameter(w1=old['left_diameter'] ,w2=old['right_diameter'])
    sleep(.1)

    print("#################################################")
    print("Going back to the origin, press Enter when ready.")
    print("#################################################")
    input()

    cs.trajman[robot].move_trsl(dest=length, acc=speeds['tracc'], dec=speeds['trdec'], maxspeed=100, sens=0)
    sleep(length/100 + 2)
    cs.trajman[robot].free()


""" Compute Spacing """
def compute_spacing():
    print("##########################################")
    print("Please enter the number of turns to mesure")
    print("##########################################")

    success = False
    while not success:
        try:
            nbturns = float(input())
            success = True
        except:
            print("Try again")

    print("nbturns = ", nbturns)

    print("##########################################################")
    print("Please place the robot on the mark, press Enter when ready")
    print("##########################################################")

    input()

    cs.trajman[robot].unfree()

    print("#######################################################")
    print("Do you want the robot to do the turns by itself (y/n) ?")
    print("#######################################################")

    i = input()

    oldpos = cs.trajman[robot].get_position()

    if i[0] == 'y':
        print("Going...")
        cs.trajman[robot].move_rot(dest=2 * nbturns * pi, acc=3, dec=3, maxspeed=3, sens=1)
        sleep(nbturns*2.5 + 1)
        cs.trajman[robot].free()
        print("############################################################")
        print("Please replace the robot on the mark, press Enter when ready")
        print("############################################################")
    else:
        cs.trajman[robot].free()
        print("################################################################")
        print("Please make the robot do turns on itself, press Enter when ready")
        print("################################################################")

    input()

    newpos = cs.trajman[robot].get_position()
    mesured = newpos['theta'] - oldpos['theta'] + nbturns * pi
    coef = float(mesured) / float(nbturns * pi)

    global old
    old['spacing'] = old['spacing'] * coef

    print("The error was of :", newpos['theta'] - oldpos['theta'])
    print("The new spacing is :", old['spacing'])
    print("Setting the new spacing")

    cs.trajman[robot].set_wheels_spacing(spacing=old['spacing'])

    print("#################################################")
    print("Going back to the origin, press Enter when ready.")
    print("#################################################")
    input()

    cs.trajman[robot].move_rot(dest=2 * nbturns * pi, acc=3, dec=3, maxspeed=3, sens=0)
    sleep(nbturns*2.5 + 1)
    cs.trajman[robot].free()


def compute_all(diams, spacing, all, config, _robot):

    robot_name = _robot

    global cs
    cs = CellaservProxy()
    global robot
    robot = robot_name
    global old
    old = cs.trajman[robot].get_wheels()
    global speeds
    speeds = cs.trajman[robot].get_speeds()

    if not diams and not spacing:
        all = True

    print("###############################################################")
    print("## Hi ! and welcome to the wheels size computing assistant ! ##")
    print("###############################################################")

    if all:
        print('It will compute everything: diameters and spacing')
    else:
        if diams:
            print('It will compute diams')
        if spacing:
            print('It will compute spacing')

    print("Press enter when ready")
    input()

    cs.trajman[robot].set_x(x=1000)
    cs.trajman[robot].set_y(y=1000)
    cs.trajman[robot].set_theta(theta=0)

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
        cs.config.set(section=robot_name, option='spacing', value=str(old['spacing']))

    print("##################################")
    print("## Computing wheels size done ! ##")
    print("##################################")
    print_json(old)


def main():
    parser = ArgumentParser(description='Configuration of the odometry of the robot')
    parser.add_argument("robot", help="Robot to configure")
    parser.add_argument("-d", "--diams", help="Compute wheels diameters of the robot", action="store_true")
    parser.add_argument("-s", "--spacing", help="Compute wheels spacing of the robot", action="store_true")
    parser.add_argument("-a", "--all", help="Compute all odom of the robot", action="store_true")
    parser.add_argument("-c", "--config", help="Set new values to config", action="store_true")

    args = parser.parse_args()

    if args.robot not in ['pal', 'pmi']:
        print('Unknown robot')
        print('Available robot: [pal, pmi]')
        return 1

    compute_all(args.diams, args.spacing, args.all, args.config, args.robot)

if __name__ == "__main__":
    main()
