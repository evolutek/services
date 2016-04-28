#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

# main axs
AX_ID_STAND_ELEVATOR = "10"
AX_ID_STAND_LEFT_CLAW = "12"
AX_ID_STAND_RIGHT_CLAW = "11"
AX_ID_STAND_RIGHT_GRIPPER = "13"
AX_ID_STAND_LEFT_GRIPPER = "14"
AX_ID_ARM_RIGHT = "16"
AX_ID_ARM_LEFT = "15"

AX_ELEVATOR_UP = 100
AX_ELEVATOR_DOWN = 1023
AX_CLAW_LEFT_OPEN = 1023
AX_CLAW_LEFT_CLOSE = 815
AX_CLAW_RIGHT_OPEN = 0
AX_CLAW_RIGHT_CLOSE = 214
AX_GRIPPER_RIGHT_OPEN = 700
AX_GRIPPER_RIGHT_CLOSE = 500
AX_GRIPPER_LEFT_OPEN = 400
AX_GRIPPER_LEFT_CLOSE = 700

AX_ARM_RIGHT_OPEN = 80
AX_ARM_RIGHT_CLOSE = 690
AX_ARM_LEFT_OPEN = 950
AX_ARM_LEFT_CLOSE = 400

ARM_LEFT = 0
ARM_RIGHT = 1

@Service.require("ax", "10")
@Service.require("ax", "11")
@Service.require("ax", "12")
@Service.require("ax", "13")
@Service.require("ax", "14")
@Service.require("ax", "15")
@Service.require("ax", "16")
class Actuators(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()

    def setup(self):
        super().setup()
        self.cs.ax[AX_ID_RIGHT_STAND_ELEVATOR].mode_joint()
        self.cs.ax[AX_ID_RIGHT_STAND_LEFT_CLAW].mode_joint()
        self.cs.ax[AX_ID_RIGHT_STAND_RIGHT_CLAW].mode_joint()
        self.cs.ax[AX_ID_STAND_RIGHT_GRIPPER].mode_joint()
        self.cs.ax[AX_ID_STAND_LEFT_GRIPPER].mode_joint()
        self.cs.ax[AX_ID_ARM_LEFT].mode_joint()
        self.cs.ax[AX_ID_ARM_RIGHT].mode_joint()

    @Service.action
    def free(self):
        for ax in [
                AX_ID_RIGHT_STAND_ELEVATOR,
                AX_ID_RIGHT_STAND_LEFT_CLAW,
                AX_ID_RIGHT_STAND_RIGHT_CLAW,
                AX_ID_RIGHT_STAND_RIGHT_GRIPPER,
                AX_ID_RIGHT_STAND_LEFT_GRIPPER,
                AX_ID_ARM_LEFT,
                AX_ID_ARM_RIGHT,
                ]:
            self.cs.ax[ax].free()

    @Service.action("reset")
    def actuators_reset(self):
        self.setup()
        self.cs.ax[AX_ID_ARM_LEFT].move(goal=AX_ARM_LEFT_CLOSE)
        self.cs.ax[AX_ID_ARM_RIGHT].move(goal=AX_ARM_RIGHT_CLOSE)
        self.cs.ax[AX_ID_STAND_ELEVATOR].move(goal=AX_ELEVATOR_DOWN)
        self.cs.ax[AX_ID_STAND_LEFT_CLAW].move(goal=AX_CLAW_LEFT_OPEN)
        self.cs.ax[AX_ID_STAND_RIGHT_CLAW].move(goal=AX_CLAW_RIGHT_OPEN)
        self.cs.ax[AX_ID_STAND_RIGHT_GRIPPER].move(goal=AX_GRIPPER_RIGHT_CLOSE)
        self.cs.ax[AX_ID_STAND_LEFT_GRIPPER].move(goal=AX_GRIPPER_LEFT_CLOSE)

    @Service.action
    def arm_open(self, side: int) -> None:
        if int(side) == ARM_LEFT:
            self.cs.ax[AX_ID_ARM_LEFT].move(goal=AX_ARM_LEFT_OPEN)
        else:
            self.cs.ax[AX_ID_ARM_RIGHT].move(goal=AX_ARM_RIGHT_OPEN)

    @Service.action
    def arm_close(self, side: int) -> None:
        if int(side) == ARM_LEFT:
            self.cs.ax[AX_ID_ARM_LEFT].move(goal=AX_ARM_LEFT_CLOSE)
        else:
            self.cs.ax[AX_ID_ARM_RIGHT].move(goal=AX_ARM_RIGHT_CLOSE)

    @Service.action
    def elevator_up(self):
        self.cs.ax[AX_ID_STAND_ELEVATOR].move(goal=AX_ELEVATOR_UP)

    @Service.action
    def elevator_down(self):
        self.cs.ax[AX_ID_STAND_ELEVATOR].move(goal=AX_ELEVATOR_DOWN)

    @Service.action
    def claw_open(self):
        self.cs.ax[AX_ID_STAND_LEFT_CLAW].mode_joint()
        self.cs.ax[AX_ID_STAND_RIGHT_CLAW].mode_joint()
        self.cs.ax[AX_ID_STAND_LEFT_CLAW].move(goal=AX_CLAW_LEFT_OPEN)
        self.cs.ax[AX_ID_STAND_RIGHT_CLAW].move(goal=AX_CLAW_RIGHT_OPEN)

    @Service.action
    def claw_close(self):
        self.cs.ax[AX_ID_STAND_LEFT_CLAW].mode_joint()
        self.cs.ax[AX_ID_STAND_RIGHT_CLAW].mode_joint()
        self.cs.ax[AX_ID_STAND_LEFT_CLAW].move(goal=AX_CLAW_LEFT_CLOSE)
        self.cs.ax[AX_ID_STAND_RIGHT_CLAW].move(goal=AX_CLAW_RIGHT_CLOSE)

    @Service.action
    def claw_grip(self):
        self.cs.ax[AX_ID_STAND_LEFT_CLAW].mode_wheel()
        self.cs.ax[AX_ID_STAND_RIGHT_CLAW].mode_wheel()
        self.cs.ax[AX_ID_STAND_LEFT_CLAW].turn(side=1, speed=500)
        self.cs.ax[AX_ID_STAND_RIGHT_CLAW].turn(side=-1, speed=500)

    @Service.action
    def claw_ungrip(self):
        self.cs.ax[AX_ID_STAND_LEFT_CLAW].mode_joint()
        self.cs.ax[AX_ID_STAND_RIGHT_CLAW].mode_joint()

    @Service.action
    def gripper_open(self):
        self.cs.ax[AX_ID_STAND_LEFT_GRIPPER].move(goal=AX_GRIPPER_LEFT_OPEN)
        self.cs.ax[AX_ID_STAND_RIGHT_GRIPPER].move(goal=AX_GRIPPER_RIGHT_OPEN)

    @Service.action
    def gripper_close(self):
        self.cs.ax[AX_ID_STAND_LEFT_GRIPPER].move(goal=AX_GRIPPER_LEFT_CLOSE)
        self.cs.ax[AX_ID_STAND_RIGHT_GRIPPER].move(goal=AX_GRIPPER_RIGHT_CLOSE)

def main():
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
