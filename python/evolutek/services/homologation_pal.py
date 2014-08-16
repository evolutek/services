#!/usr/bin/env python3
from threading import Timer

from cellaserv.service import Service, Variable

from evolutek.lib.robot import robot


class Homologation(Service):

    start = Variable('start')

    def __init__(self):
        super().__init__()
        self.robot = robot
        self.match_stop_timer = Timer(89, self.stop)

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
        self.robot.tm.free()


def main():
    ia = Homologation()
    ia.run()

if __name__ == '__main__':
    main()
