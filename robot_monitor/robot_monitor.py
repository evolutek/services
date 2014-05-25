#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

@Service.require('trajman')
class RobotMonitor(Service):

    freq = ConfigVariable(section="monitor", option="frequency")
    mon_pos = ConfigVariable(section="monitor", option="position")

    def __init__(self, identification=None):
        super().__init__(identification)

        self.cs = CellaservProxy()

        self.monitored = set()
        self.mon_pos.add_update_cb(lambda value:
                self.monitored.add(self.mon_position) if value else
                self.monitored.remove(self.mon_position))

    def setup(self):
        super().setup()

        if self.mon_pos():
            self.monitored.add(self.mon_position)

    def mon_position(self):
        log_name = 'log.monitor.robot_position'
        if self.identification:
            log_name += '.' + self.identification
        self(log_name, **self.cs.trajman.get_position())

    @Service.thread
    def loop(self):
        while not sleep(float(self.freq())):
            for mon_func in self.monitored:
                mon_func()

def main():
    robot_monitor = RobotMonitor('pal')
    robot_monitor.run()

if __name__ == '__main__':
    main()
