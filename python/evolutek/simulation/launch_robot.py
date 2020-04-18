#!/usr/bin/env python3

import json
from multiprocessing import Process
from os import _exit, system
from signal import signal, SIGINT
from sys import argv
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.settings import make_setting

ROBOT = ''
launched = {}

def launch_robot(robot, to_launch):

    global ROBOT
    ROBOT = robot

    cs = CellaservProxy()
    cs.config.set_tmp(section='simulation', option='robot', value=ROBOT)

    print('[SIMULATOR] Launching robot %s' % ROBOT)

    for service in to_launch:
        print('[SIMULATOR] Launching %s' % service)
        launched[service] = Process(target=system, args=[to_launch[service]])
        launched[service].start()

    print('[SIMULATOR] Checking if processes are alives')
    for service in launched:
        if not launched[service].is_alive():
            print('[SIMULATOR] %s is dead' % service)
            kill_robot()
            return

    signal(SIGINT, kill_robot)

    print('[SIMULATOR] Finished launching robot %s' % ROBOT)

def kill_robot(signal_received=None, frame=None):

    print('[SIMULATOR] Killing robot %s' % ROBOT)

    for service in launched:
        print('[SIMULATOR] Killing %s' % service)
        launched[service].kill()

    print('[SIMULATOR] Finished killing robot %s' % ROBOT)
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

    launch_robot(robot, services)

    while True:
        pass

if __name__ == "__main__":
    main()
