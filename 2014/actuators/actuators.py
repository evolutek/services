#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

AX_ID_COLLECT_ROTATION = "10"
AX_ID_COLLECT = "11"
AX_ID_COLLECT_ELEVATOR = "12"

AX_ELEVATOR_UP = 1000
AX_ELEVATOR_DOWN = 0
AX_ELEVATOR_FIREPLACE = 300
AX_COLLECTOR_OPEN = 1000
AX_COLLECTOR_CLOSE = 650
AX_ROTATION_START = 320
AX_ROTATION_END = 0

# others to come

# TODO:
#  - goals need to be checked when the collector is going to be replaced
#  - use configuration variables
#  - make it stateful
#  - sleep when it's needed

class Actuators(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()


    @Service.action
    def free(self):
        for ax in [
                AX_ID_COLLECT,
                AX_ID_COLLECT_ELEVATOR,
                AX_ID_COLLECT_ROTATION
                ]:
            self.cs.ax[ax].free()

    @Service.action("reset")
    def collector_reset(self):
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].mode_joint()
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=AX_ELEVATOR_UP)

        sleep(.5)
        self.cs.ax[AX_ID_COLLECT_ROTATION].mode_joint()
        self.cs.ax[AX_ID_COLLECT_ROTATION].move(goal=AX_ROTATION_START)
        self.rotation = AX_ROTATION_START

        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_OPEN)
        
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=AX_ELEVATOR_UP)


    @Service.action
    def collector_open(self):
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_OPEN)

    @Service.action
    def collector_close(self):
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_CLOSE)

    @Service.action
    def collector_hold(self):
        self.cs.ax[AX_ID_COLLECT].mode_wheel()
        # increase if too weak
        self.cs.ax[AX_ID_COLLECT].turn(side=-1, speed=350)

    @Service.action
    def collector_up(self):
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=AX_ELEVATOR_UP)

    def collector_is_up(self):
        return self.cs.ax[AX_ID_COLLECT_ELEVATOR].get_present_position == AX_ELEVATOR_UP

    @Service.action
    def collector_down(self):
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=AX_ELEVATOR_DOWN)

    def collector_is_down(self):
        return self.cs.ax[AX_ID_COLLECT_ELEVATOR].get_present_position == AX_ELEVATOR_DOWN

    @Service.action
    def collector_fireplace(self):
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=AX_ELEVATOR_FIREPLACE)

    @Service.action
    def collector_rotate(self):
        if not self.collector_is_up():
            self.collector_up()

        if self.rotation == AX_ROTATION_START:
            self.rotation = AX_ROTATION_END
        else:
            self.rotation = AX_ROTATION_START

        self.cs.ax[AX_ID_COLLECT_ROTATION].move(goal=self.rotation)

    @Service.action
    def test(self):
        self.collector_open()
        self.collector_down()
        self.collector_close()
        self.collector_hold()
        self.collector_up() # facultatif
        self.collector_rotate()
        self.collector_fireplace()
        self.collector_open()

def main():
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
