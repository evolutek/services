#!/usr/bin/env python3

import json
from multiprocessing import Process
from os import _exit, system
from signal import signal, SIGINT
from sys import argv
from time import sleep

from cellaserv.proxy import CellaservProxy

#TODO Control Interface

class Robot:

    def __init__(self, robot, to_launch):
        self.ROBOT = robot
        self.launched = {}
        self.launch_robot(to_launch)

    def launch_robot(self, to_launch):

        cs = CellaservProxy()
        cs.config.set_tmp(section='simulation', option='robot', value=self.ROBOT)

        print('[SIMULATOR] Launching robot %s' % self.ROBOT)

        for service in to_launch:
            print('[SIMULATOR] Launching %s' % service)
            self.launched[service] = Process(target=system, args=[to_launch[service]])
            self.launched[service].start()

            print('[SIMULATOR] Checking if processes are alives')
        for service in self.launched:
            if not self.launched[service].is_alive():
                print('[SIMULATOR] %s is dead' % service)
                self.kill_robot()
                return

        signal(SIGINT, self.kill_robot)

        print('[SIMULATOR] Finished launching robot %s' % self.ROBOT)

    def kill_robot(self, signal_received=None, frame=None):

        print('[SIMULATOR] Killing robot %s' % self.ROBOT)

        for service in self.launched:
            print('[SIMULATOR] Killing %s' % service)
            self.launched[service].kill()

        print('[SIMULATOR] Finished killing robot %s' % self.ROBOT)
        _exit(0)

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

    print('[SIMULATOR] Reading config')
    services = []
    try:
        with open('/etc/conf.d/simulation.json', 'r') as file:
            data = file.read()
            services = json.loads(data)[robot]
    except Exception as e:
        print('[SIMULATOR] Failed to read config: %s' % str(e))
        return

    robot = Robot(robot, services)

    while True:
        pass

if __name__ == "__main__":
    main()
