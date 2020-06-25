#!/usr/bin/env python3

import json
from multiprocessing import Process
from os import _exit, system
from signal import signal, SIGINT

def read_config(section):

    print('[SIMULATOR] Reading config')
    config = None
    try:
        with open('/etc/conf.d/simulation.json', 'r') as file:
            data = file.read()
            config = json.loads(data)[section]
    except Exception as e:
        print('[SIMULATOR] Failed to read config: %s' % str(e))

    return config

class Simulation:

    def __init__(self, to_launch):

        self.launched = {}
        self.launch_services(to_launch)

    def launch_services(self, to_launch):

        for script in to_launch:
            print('[SIMULATOR] Launching %s' % script)
            self.launched[script] = Process(target=system, args=[to_launch[script]])
            self.launched[script].start()

        print('[SIMULATOR] Checking if processes are alives')
        for script in self.launched:
            if not self.launched[script].is_alive():
                print('[SIMULATOR] %s is dead' % script)
                self.kill_simulation()
                return

        signal(SIGINT, self.kill_simulation)

        print('[SIMULATION] Simulation running')

    def kill_simulation(self, signal_received=None, frame=None):
        print('[SIMULATION] Killing simulation')
        for script in self.launched:
            print('[SIMULATOR] Killing %s' % script)
            self.launched[script].kill()
        _exit(0)

def main():
    print('[SIMULATION] Starting Evolutek<< simulation')

    to_launch = read_config('base_services')
    if to_launch is None:
        return

    simulation = Simulation(to_launch)

    while True:
        pass

if __name__ == "__main__":
    main()
