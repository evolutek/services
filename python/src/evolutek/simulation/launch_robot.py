#!/usr/bin/env python3

from sys import argv

from cellaserv.proxy import CellaservProxy
from evolutek.simulation.simulator import Simulation, read_config

#TODO Control Interface

class Robot(Simulation):

    def __init__(self, robot, to_launch):
        self.ROBOT = robot

        cs = CellaservProxy()
        cs.config.set_tmp(section='simulation', option='robot', value=self.ROBOT)

        super().__init__(to_launch)

def main():

    print('[SIMULATOR] Starting robot')

    if len(argv) < 2:
        print('[SIMULATOR] Missing robot')
        print('[SIMULATOR] Usage: $./launch_robot robot')
        return

    robot = argv[1]

    if robot not in ['pal', 'pmi']:
        print('[SIMULATOR] Robot not existing')
        print('[SIMULATOR] Available robot: pal, pmi')
        return

    to_launch = read_config('robot')
    if to_launch is None:
        return

    robot = Robot(robot, to_launch)

    while True:
        pass

if __name__ == "__main__":
    main()
