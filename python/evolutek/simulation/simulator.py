#!/usr/bin/env python3

from importlib import import_module
import json
from os import _exit
from signal import signal, SIGINT
from threading import Thread
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable
from cellaserv.settings import make_setting

make_setting('SIMULATION', True, 'simulation', 'enable', 'SIMULATION')

class Simulation:

    def __init__(self, config):

        print('[SIMULATION] Starting simulation')

        # Launch base services
        for service in config['base_services']:
            Thread(target=self.launch_service, args=[config['base_services'][service]]).start()
        sleep(1)

        # Launch all robots
        for robot in config['robots']:
            make_setting('ROBOT', robot, 'evolutek', 'robot', 'ROBOT')
            for service in config[robot]:
                Thread(target=self.launch_service, args=[config[robot][service]]).start()
            sleep(1)

        ennemies = {}
        for ennemy in config['ennemies']:
            ennemies[ennemy] = config['ennemies'][ennemy]
            make_setting('ROBOT', ennemy, 'evolutek', 'robot', 'ROBOT')
            Thread(target=self.launch_service, args=[config['ennemies'][ennemy]['service']]).start()
            sleep(1)


        # TODO: control interface

        signal(SIGINT, self.handler)

        print('[SIMULATION] Simulation running')

    def launch_service(self, service):
        print('[SIMULATION] Lauching %s' % service)
        service = import_module(service)
        service.main()
        sleep(0.5)

    def handler(self, signal_received, frame):
        print('[SIMULATION] Killing simulation')
        _exit(0)

def main():
    print("Evolutek<< Simulator")

    with open('/etc/conf.d/simulation.json', 'r') as file:
        data = file.read()

    config = json.loads(data)

    print('[SIMULATION] Config for simualtion')
    print(config)


    simulation = Simulation(config)

    while True:
        pass

if __name__ == "__main__":
    main()
