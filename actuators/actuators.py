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
    def free(self):
        for ax in [AX_ID_ARM_1,
                AX_ID_ARM_2_BASE,
                AX_ID_ARM_2_JOINT,
                AX_ID_COLLECT_LEFT,
                AX_ID_COLLECT_RIGHT]:
            self.cs.ax[ax].free()

    @Service.action
    def collector_open(self):
        self.cs.ax[AX_ID_COLLECT_RIGHT].mode_joint()
        self.cs.ax[AX_ID_COLLECT_LEFT].mode_joint()
        self.cs.ax[AX_ID_COLLECT_RIGHT].move(goal=830)
        sleep(.3)
        self.cs.ax[AX_ID_COLLECT_LEFT].move(goal=520)

    @Service.action
    def collector_close(self):
        self.cs.ax[AX_ID_COLLECT_LEFT].mode_joint()
        self.cs.ax[AX_ID_COLLECT_RIGHT].mode_joint()
        self.cs.ax[AX_ID_COLLECT_LEFT].move(goal=855)
        sleep(.3)
        self.cs.ax[AX_ID_COLLECT_RIGHT].move(goal=520)

    @Service.action
    def collector_hold(self):
        self.cs.ax[AX_ID_COLLECT_LEFT].mode_wheel()
        self.cs.ax[AX_ID_COLLECT_RIGHT].mode_wheel()
        self.cs.ax[AX_ID_COLLECT_LEFT].turn(side=0, speed=512)
        self.cs.ax[AX_ID_COLLECT_RIGHT].turn(side=1, speed=512)

    @Service.action
    def arm_1_raise(self):
        self.cs.ax[AX_ID_ARM_1].move(goal=755)

    @Service.action
    def arm_1_lower(self):
        self.cs.ax[AX_ID_ARM_1].move(goal=400)

    @Service.action
    def arm_1_setup(self):
        self.cs.ax[AX_ID_ARM_1].move(goal=600)

    @Service.action
    def arm_1_candle_push(self):
        self.arm_1_lower()
        sleep(.5)
        self.arm_1_setup()

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
    def arm_2_candle_setup(self):
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=400)
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=80)

    @Service.action
    def arm_2_candle_push(self):
        self.cs.ax[AX_ID_ARM_2_BASE].mode_wheel()
        self.cs.ax[AX_ID_ARM_2_BASE].turn(side=1, speed=1023)
        sleep(.3)
        self.cs.ax[AX_ID_ARM_2_BASE].mode_joint()
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=400)

    @Service.action
    def arm_2_raise(self):
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=450)
        sleep(.2)
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=510)
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=510)

    @Service.action
    def arm_2_gift_setup(self):
        #self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=300)
        #self.cs.ax[AX_ID_ARM_2_BASE].move(goal=250)
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=400)
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=400)

    @Service.action
    def arm_2_gift_push(self):
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=250)
        sleep(.2)
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=0)
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=300)
        sleep(.3)
        self.cs.ax[AX_ID_ARM_2_JOINT].move(goal=400)
        self.cs.ax[AX_ID_ARM_2_BASE].move(goal=400)


    @Service.action
    def test(self):
        self.arm_2_lower()
        self.arm_1_lower()
        self.collector_open()
        sleep(.3)
        self.arm_2_push()
        sleep(.3)
        self.arm_2_lower()
        sleep(.5)
        self.arm_2_raise()
        self.arm_1_raise()
        self.collector_close()

def main():
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
