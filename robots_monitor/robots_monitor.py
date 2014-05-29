#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service, ConfigVariable

@Service.require('trajman')
class RobotsMonitor(Service):

    freq = ConfigVariable(section="monitor", option="frequency", coerc=float)
    mon_pos_pal = ConfigVariable(section="monitor", option="position_pal",
            coerc=eval)
    mon_pos_pmi = ConfigVariable(section="monitor", option="position_pmi",
            coerc=eval)

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

        self.monitored = set()
        self.mon_pos_pal.add_update_cb(lambda value:
                self.monitored.add(self.position_pal) if value else
                self.monitored.remove(self.position_pal))
        self.mon_pos_pmi.add_update_cb(lambda value:
                self.monitored.add(self.position_pmi) if value else
                self.monitored.remove(self.position_pmi))

        self.pal = self.cs.trajman['pal']
        self.pmi = self.cs.trajman['pmi']

    def setup(self):
        super().setup()

        if self.mon_pos_pal():
            self.monitored.add(self.position_pal)
        if self.mon_pos_pmi():
            self.monitored.add(self.position_pmi)

    def position_pal(self):
        log_name = 'log.monitor.robot_position'
        pos = self.pal.get_position()
        if pos is not None:
            self(log_name, robot="pal", **pos)

    def position_pmi(self):
        log_name = 'log.monitor.robot_position'
        self(log_name, robot="pmi", **self.pmi.get_position())

    @Service.thread
    def loop(self):
        while not sleep(float(self.freq())):
            for mon_func in self.monitored:
                mon_func()

def main():
    robots_monitor = RobotsMonitor()
    robots_monitor.run()

if __name__ == '__main__':
    main()
