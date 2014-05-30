#!/usr/bin/env python3
from threading import Thread, Timer, Event
from time import sleep
import math

from cellaserv.service import Service, Variable, ConfigVariable
from cellaserv.proxy import CellaservProxy
from robot import Robot
from objective import *
from subprocess import call

import pathfinding
from pathfinding import AvoidException
import robot_status


@Service.require("trajman.pmi")
@Service.require("actuatorspmi")
@Service.require("tracking")
class ia(Service):

    match_start = Variable('start')
    color = ConfigVariable(section='match', option='color', coerc=lambda v:
            {'red': -1, 'yellow': 1}[v])
    speed_full = ConfigVariable(section='pmi', option='trsl_max', coerc=float)
    speed_slow = ConfigVariable(section='pmi', option='trsl_min', coerc=float)

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        self.match_stop_timer = Timer(85, self.match_stop)

        self.start_event = Event()

        self.pmi = Robot('pmi')
        self.pmi.setup()
        self.pmi_stopped = False


    def setup(self):
        super().setup()

        self.cs('log.ia', msg="Setup pmi done")

        #pmi
        self.pmi.free()
        # 7 cm of the table edge
        self.pmi.set_x(60)
        # 3 cm of the fruit deposit box
        self.pmi.set_y(self.get_y(270))
        # make the collector in the fruit axes
        self.pmi.set_theta(self.get_theta(0))
        self.pmi.unfree()
        self.cs.actuatorspmi.collector_close()

    @Service.action
    def status(self):
        return {'started': self.match_start.is_set()}


    def get_position(self):
        pos = None
        while not pos:
            try:
                pos = self.pmi.get_position()
            except:
                pass
        return pos

    @Service.thread
    def start(self):
        return;
        print("Waiting...")
        self.log(msg='Waiting')
        self.match_start.wait()
        print("Start!")
        self.cs('log.ia', msg="Match started")
        self.match_stop_timer.start()

    # Called by a timer thread
    def match_stop(self):
        self.cs('log.ia', msg='Stopping robot')
        self.cs.trajman['pal'].free()
        self.cs.trajman['pal'].disable()
        self.cs.trajman['pmi'].free()
        self.cs.trajman['pmi'].disable()

    @Service.event
    def robot_near_pmi(self, x, y):
        print("Robot near pmi, stop !")
        if not self.pmi_stopped:
            self.pmi.stop_asap(trsldec=1500, rotdec=3.1)
            self.pmi_stopped = True

    # FIXME: check this shit out
    def get_theta(self, theta):
        return theta if self.color() == 1 else theta + math.pi

    # FIXME: same
    def get_y(self, y):
        return 1500 + ((1500 - y) * self.color())

    def pmi_goto_xy_block_retry(self, x, y, retries=-1):
        self.pmi_goto_xy_block(x, y)
        while self.pmi_stopped == True and retries != 0:
            sleep(0.5)
            self.pmi_stopped = False
            self.pmi_goto_xy_block(x, y)
            retries -= 1

    def pmi_goto_xy_block(self, x, y):
        self.pmi_stopped = False
        self.pmi.goto_xy_block(x, self.get_y(y))

    @Service.thread
    def start_pmi(self):
        print("Waiting pmi...")
        self.log(msg='Waiting pmi')
        self.match_start.wait()
        print("Start!")
        self.cs('log.ia', msg="PMI Match started")
        self.cs.actuatorspmi.collector_get()

        # waiting for the path to be cleared
        sleep(5)

        # fetch fruits from 1st tree
        self.pmi_goto_xy_block_retry(1100, 270)
        self.pmi.set_trsl_max_speed(200)
        self.pmi_goto_xy_block_retry(1700, 270)
        self.pmi.set_trsl_max_speed(400)
        self.cs.actuatorspmi.collector_close()

        # go to drop zone
        self.pmi_goto_xy_block_retry(410, 270)
        self.pmi.goto_theta(math.pi / 2)
        self.pmi_goto_xy_block_retry(410, 1750)

        self.cs.actuatorspmi.collector_flush()
        self.cs("beep_ok")
        self.cs.actuatorspmi.collector_close()
        sleep(1)

        # go to 2nd tree
        # near start zone
        self.pmi_goto_xy_block_retry(410, 270)
        self.pmi.goto_theta(self.get_theta(-math.pi / 2))
        # opposite cornet
        self.pmi_goto_xy_block_retry(1730, 400)
        # get fruits
        self.cs.actuatorspmi.collector_get()
        self.pmi.goto_theta(-math.pi / 2)
        self.pmi.set_trsl_max_speed(200)
        self.pmi_goto_xy_block_retry(1730, 1100)
        self.cs.actuatorspmi.collector_close()
        # come back
        self.pmi.set_trsl_max_speed(400)
        self.pmi_goto_xy_block_retry(1730, 400)
        self.pmi.goto_theta(self.get_theta(-math.pi / 2))

        # go to drop zone
        self.pmi_goto_xy_block_retry(410, 270)
        self.pmi.goto_theta(math.pi / 2)
        self.pmi_goto_xy_block_retry(410, 1750)

        self.cs.actuatorspmi.collector_flush()
        self.cs("beep_ok")
        self.cs.actuatorspmi.collector_close()
        sleep(1)

def main():
    service = ia()
    service.run()

if __name__ == '__main__':
    main()
