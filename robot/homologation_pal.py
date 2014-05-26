#!/usr/bin/env python3
from threading import Timer

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, Variable

from robot import Robot

class Homologation(Service):

    start = Variable('start')

    def __init__(self):
        super().__init__()
        self.robot = Robot()
        self.match_stop_timer = Timer(89, self.stop)
        self.cs = CellaservProxy()

    def setup(self):
        super().setup()
        self.robot.setup()

    @Service.thread
    def ia(self):
        self.log(msg='Waiting for start...')
        self.start.wait()
        self.match_stop_timer.start()
        self('beep_ready')
        self.log(msg='Start!')
        self.robot.goto_xy_block(x=650, y=2500)

    @Service.event
    def stop(self):
        self('beep_ok')
        self.log(msg='Stopping robot.')
        self.cs.trajman.free()
        self.cs.trajman.disable()


if __name__ == '__main__':
    ia = Homologation()
    ia.run()
