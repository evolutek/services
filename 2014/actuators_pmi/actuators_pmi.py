#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

AX_ID_COLLECT = "3"

AX_COLLECTOR_CLOSE = 500
AX_COLLECTOR_GET = 800
AX_COLLECTOR_FLUSH = 960

@Service.require("ax.3")
class ActuatorsPMI(Service):

    #flush_retries = ConfigVariable(section='pmi', option='flush_retries')

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

    def setup(self):
        super().setup()
        self.cs.ax[AX_ID_COLLECT].mode_joint()

    @Service.action
    def free(self):
        for ax in [ AX_ID_COLLECT ]:
            self.cs.ax[ax].free()

    @Service.action
    def collector_get(self):
        self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_GET)

    @Service.action
    def collector_close(self):
        self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_CLOSE)

    @Service.action
    def collector_flush(self):
        #for i in range(0, self.flush_retries()):
        for i in range(0, 8):
            self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_FLUSH)
            sleep(.2)
            self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_GET)
            sleep(.2)

def main():
    actuators = ActuatorsPMI()
    actuators.run()

if __name__ == '__main__':
    main()
