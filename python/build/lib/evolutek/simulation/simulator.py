#!/usr/bin/env python3

import collections
import os
import random
import readline
import time

from cellaserv.service import Service, ConfigVariable
from cellaserv.proxy import CellaservProxy

Vector2 = collections.namedtuple("Vector2", "x y")

YELLOW = 1
RED = -1

###############################################################################
# Fake services

TIRETTE_INSIDE = 1
TIRETTE_OUTSIDE = 0

class FakeTirette(Service):

    service_name = "tirette"

    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        self.cs = CellaservProxy()
        self.state = TIRETTE_INSIDE

    def update(self, now, delta_time):
        pass

    ################
    # Real actions

    @Service.action
    def get_state(self):
        return self.state

    ################
    # Simu actions

    @Service.action
    def set_state(self, new_state):
        self.state = new_state

    @Service.action
    def put_tirette(self):
        self.state = TIRETTE_INSIDE

    @Service.action
    def remove_tirette(self):
        self.state = TIRETTE_OUTSIDE

    @Service.action
    def send_match_start(self):
        self.state = TIRETTE_OUTSIDE
        self.cs('start')

class FakeHokuyo(Service):

    service_name = "hokuyo"

    hokuyo_freq = ConfigVariable('simulation', 'hokuyo_freq', coerc=float)
    fuzziness = ConfigVariable('simulation', 'hokuyo_fuzziness', coerc=float)

    def __init__(self, simulation, identification):
        super().__init__()

        self.simulation = simulation
        self.identification = identification

        self.position = 0 # not used
        self.cs = CellaservProxy()

        # Simulation attributes

        self.last_scan = 0
        self.do_scan = False

    ################
    # Real actions

    @Service.action
    def set_position(self, position):
        print("Fixme: hokuyo.set_position stub")
        self.position = position

    @Service.action
    def add_deadzone(self, type, x, y, radius):
        print("Fixme: hokuyo.add_deadzone stub")

    @Service.action
    def scan(self):
        print("Fixme: hokuyo.scan")
        return []

    ################
    # Simu actions

    @Service.action
    def start_scanning(self):
        self.do_scan = True

    @Service.action
    def stop_scanning(self):
        self.do_scan = False

    def update(self, now, delta_time):
        if self.do_scan and now - self.last_scan > (1 / self.hokuyo_freq()):
            self.last_scan = now

            # Compute fake positions, with blur if wanted
            positions =  []
            for robot in self.simulation.robots.values():
                x_new = robot.position.x + random.randint(-self.fuzziness(), self.fuzziness())
                y_new = robot.position.y + random.randint(-self.fuzziness(), self.fuzziness())
                pos = Vector2(x=x_new, y=y_new)
                positions.append(pos._asdict())

            # Send fake positions
            self.cs("hokuyo.robots", robots=positions)

class FakeTrajman(Service):

    service_name = 'trajman'

    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation

    ################
    # Real actions

    @Service.action
    def gotoxy(self, x, y):
        androo = self.simulation.robots['androo']
        androo.position = Vector2(x=x, y=y)

    ################
    # Simu actions

    def update(self, now, delta_time):
        pass

###############################################################################
# Simulation objects

class Robot:
    def __init__(self, position, color, name):
        self.position = position
        self.color = color
        self.name = name

        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

    def update(self, now, delta_time):
        pass

class Simulation(Service):

    tick_duration = ConfigVariable('simulation', 'tick_duration', coerc=float)
    speed_factor = ConfigVariable('simulation', 'speed_factor', coerc=float)

    def __init__(self):
        super().__init__()

        self.now = 0

        self.setup() # Setup self
        self.setup_game()
        self.setup_services()

    def setup_game(self):
        androo = Robot(Vector2(100, 1000), RED, "androo")
        plippe = Robot(Vector2(2900, 1000), YELLOW, "plippe 42")
        self.robots = {'androo': androo, 'plippe0': plippe}

    def setup_services(self):
        hokuyo1 = FakeHokuyo(self, '1')
        tirette = FakeTirette(self)
        trajman = FakeTrajman(self)
        self.services = {
                'hokuyo_1': hokuyo1,
                'tirette': tirette,
                'trajman': trajman
        }

    def start(self):
        # Setup services
        for service in self.services.values():
            service.setup()

        # Services starts listening
        Service.loop()

    # Threads

    @Service.thread
    def start_thread_simulation(self):
        while not time.sleep(self.tick_duration()):
            delta_time = self.tick_duration() * self.speed_factor()
            self.now += delta_time
            for robot in self.robots.values():
                robot.update(self.now, delta_time)
            for service in self.services.values():
                service.update(self.now, delta_time)

    @Service.thread
    def start_thread_interactive(self):
        while True:
            command = input("<< ")

            if command in ["help", "h"]:
                print("commands: \n"\
                        "help -- This help (alias: h)\n"\
                        "match-start -- Send match-start event (alias: s)\n"\
                        "hokuyo -- Start fake hokuyo (alias: h)\n"\
                        "hokuyo-stop -- Stop fake hokuyo (alias: hs)\n"\
                        "exit -- Exit simulator (alias: x)")
            elif command in ["match-start", "s"]:
                self.services['tirette'].send_match_start()
            elif command in ["hokuyo", "ho"]:
                self.services['hokuyo_1'].start_scanning()
            elif command in ["hokuyo-stop", "hs"]:
                self.services['hokuyo_1'].stop_scanning()
            elif command in ["exit", "x"]:
                os.kill(os.getpid(), 9)

def main():
    print("Evolutek<< Simulator")
    simulation = Simulation()
    simulation.start()

if __name__ == "__main__":
    main()
