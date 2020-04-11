#!/usr/bin/env python3

from importlib import import_module
import json

from os import _exit, system
import pexpect
from signal import signal, SIGINT
from sys import argv, stdout
from time import sleep
from threading import Thread

from cellaserv.settings import make_setting

ROBOT = ''
launched = {}

def launch_robot(robot, to_launch):

    ROBOT = robot

    make_setting('ROBOT', ROBOT, 'evolutek', 'robot', 'ROBOT')

    print('[SIMULATOR] Launching robot %s' % ROBOT)

    for service in to_launch:
        Thread(target=launch_service, args=[to_launch[service]]).start()

    sleep(5)

    """for service in launched:
        if not launched[service].isalive():
            print('[SIMULATOR] Service %s not alive, killing robot' % service)
            kill_robot()"""

    signal(SIGINT, kill_robot)

    print('[SIMULATOR] Finished launching robot %s' % ROBOT)

def launch_service(service):
    print('[SIMULATION] Lauching %s' % service)
    service = import_module(service)
    service.main()
    sleep(0.5)

def kill_robot(signal_received=None, frame=None):

    print('[SIMULATIOR] Killing robot %s' % ROBOT)

    """for service in launched:
        launched[service].kill(SIGINT)"""

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
