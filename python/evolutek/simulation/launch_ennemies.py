#!/usr/bin/env python3

import json
from math import pi
from multiprocessing import Process
from os import _exit, system
from signal import signal, SIGINT
from sys import argv
from time import sleep

from cellaserv.proxy import CellaservProxy
from evolutek.simulation.launch_robot import Robot, read_config

#TODO Control Interface

class Ennemie(Robot):

    def __init__(self, ennemie):

        config = ennemie[1]['config']

        cs = CellaservProxy()
        for option, value in config.items():
            cs.config.set_tmp(section=ennemie[0], option=option, value=value)

        super().__init__(ennemie[0], ennemie[1]['scripts'])

        return

        theta = ennemie[1]['theta']
        if isinstance(theta, str):
            theta = eval(theta)

        from evolutek.lib.robot import Robot as LibRobot
        robot = LibRobot()
        robot.set_pos(ennemie[1]['x'], ennemie[1]['y'], theta)


def main():

    print('[SIMULATOR] Starting ennemies')

    ennemies = read_config('ennemies')
    if ennemies is None:
        return

    for ennemie in ennemies.items():
        Ennemie(ennemie)

    while True:
        pass

if __name__ == "__main__":
    main()
