#!/usr/bin/env python3

from importlib import import_module
from os import _exit
from signal import signal, SIGINT
from threading import Thread
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable
from cellaserv.settings import make_setting

make_setting('ROBOT', 'pal', 'evolutek', 'robot', 'ROBOT')
make_setting('SIMULATION', True, 'simulation', 'enable', 'SIMULATION')

class Simulation:

    def __init__(self, services):

        for key in services:
            Thread(target=self.launch_service, args=[services[key]]).start()

        signal(SIGINT, self.handler)

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

    services = {
        'config' : 'evolutek.services.config',
        'trajman' : 'evolutek.simulation.fake_trajman',
        'ax' : 'evolutek.simulation.fake_ax',
        'match' : 'evolutek.services.match'
    }

    simulation = Simulation(services)

    while True:
        pass

if __name__ == "__main__":
    main()
