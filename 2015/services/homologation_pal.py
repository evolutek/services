#!/usr/bin/env python3
from threading import Timer
from math import pi

from cellaserv.service import Service, Event

from evolutek.lib.robot import Robot


class Homologation(Service):

    start = Event('start')

    def __init__(self):
        super().__init__()
        self.robot = Robot()
        self.match_stop_timer = Timer(89, self.stop)

    @Service.thread
    def ia(self):
        self.log(msg='Waiting for start...')
        self.start.wait()
        self.match_stop_timer.start()
        self.publish('beep_ready')
        self.log(msg='Start!')

        self.robot.goto(1000, 700)
        self.robot.goto(1750, 280)
        self.robot.goth(pi / 2)
        self.robot.goth(pi)
        self.robot.goth(-pi / 2)
        self.robot.goto(1800, 1000)

    @Service.event
    def stop(self):
        self.publish('beep_ok')
        self.log(msg='Stopping robot.')
        self.robot.tm.free()


def main():
    ia = Homologation()
    ia.run()

if __name__ == '__main__':
    main()
