#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

AX_ID_ARM_1 = "12"
AX_ID_ARM_2_BASE = "10"
AX_ID_ARM_2_JOINT = "11"
AX_ID_COLLECT_LEFT = "13"
AX_ID_COLLECT_RIGHT = "14"

class Actuators(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cs = CellaservProxy(self)

    @Service.action
    def collector_open(self):
        self.cs.ax[AX_ID_COLLECT_RIGHT].move(goal=830)
        sleep(.15)
        self.cs.ax[AX_ID_COLLECT_LEFT].move(goal=490)

    @Service.action
    def collector_close(self):
        self.cs.ax[AX_ID_COLLECT_LEFT].move(goal=855)
        sleep(.2)
        self.cs.ax[AX_ID_COLLECT_RIGHT].move(goal=520)

    @Service.action
    def arm_1_raise(self):
        self.cs.ax[AX_ID_ARM_1].move(goal=755)

    @Service.action
    def arm_1_lower(self):
        self.cs.ax[AX_ID_ARM_1].move(goal=400)

    @Service.action
    def arm_2_lower(self):
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=450)
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=450)
        sleep(.1)
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=387)
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=75)

    @Service.action
    def arm_2_push(self):
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=300)
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=300)

    @Service.action
    def arm_2_raise(self):
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=450)
        sleep(.2)
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=510)
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=510)

    @Service.action
    def test(self):
        self.arm_2_lower()
        self.arm_1_lower()
        self.collector_open()
        sleep(.3)
        self.arm_2_push()
        sleep(.3)
        self.arm_2_lower()
        sleep(.3)
        self.arm_1_raise()
        self.collector_close()
        self.arm_2_raise()

def main():
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
