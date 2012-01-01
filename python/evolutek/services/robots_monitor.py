#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable


class RobotsMonitor(Service):

    freq = ConfigVariable(section="monitor", option="frequency", coerc=float)

    def __init__(self, identification=None):
        super().__init__(identification=identification)

        self.cs = CellaservProxy()
        self.tm = self.cs.trajman[self.robot_name]

    def position(self):
        log_name = 'log.monitor.robot_position'
        pos = self.tm.get_position()
        if pos is not None:
            self.publish(log_name, robot=self.robot_name, **pos)

    @Service.thread
    def loop(self):
        while not sleep(self.freq()):
            self.position()


@Service.require('trajman', 'pal')
class MonitorPal(RobotsMonitor):

    def __init__(self):
        self.robot_name = 'pal'
        super().__init__('pal')


@Service.require('trajman', 'pmi')
class MonitorPmi(RobotsMonitor):

    def __init__(self):
        self.robot_name = 'pmi'
        super().__init__('pmi')


def main():
    pal = MonitorPal()
    # pmi = MonitorPmi()
    Service.loop()

if __name__ == '__main__':
    main()
