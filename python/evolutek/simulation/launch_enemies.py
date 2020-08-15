#!/usr/bin/env python3

import json
from math import pi
from time import sleep

from cellaserv.proxy import CellaservProxy
from evolutek.simulation.launch_robot import Robot, read_config, Simulation

#TODO Control Interface

class Enemy(Robot):

    def __init__(self, enemy, to_launch):

        print(f'[SIMULATION] Launching enemy {enemy[0]}')

        config = enemy[1]['config']

        cs = CellaservProxy()
        for option, value in config.items():
            cs.config.set_tmp(section=enemy[0], option=option, value=value)

        super().__init__(enemy[0], {'service': to_launch})

        sleep(2)

        theta = enemy[1]['theta']
        if isinstance(theta, str):
            theta = eval(theta)

        from evolutek.lib.robot import Robot as LibRobot
        robot = LibRobot()
        robot.set_pos(enemy[1]['x'], enemy[1]['y'], theta)


def main():

    print('[SIMULATOR] Starting enemies')

    enemies = read_config('enemies')
    if enemies is None:
        return

    for enemy in enemies['robots'].items():
        Enemy(enemy, enemies['service'])

    if len(enemies['scripts']) > 0:
        Simulation(enemies['scripts'])

    while True:
        pass

if __name__ == "__main__":
    main()
