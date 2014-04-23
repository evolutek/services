#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

AX_ID_COLLECT_ROTATION = "10"
AX_ID_COLLECT = "11"
AX_ID_COLLECT_ELEVATOR = "12"

# others to come

# TODO:
#  - goals need to be checked when the collector is going to be replaced
#  - use configuration variables
#  - make it stateful
#  - sleep when it's needed

class Actuators(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cs = CellaservProxy(self)

    @Service.action
    def free(self):
        for ax in [
                AX_ID_COLLECT,
                AX_ID_COLLECT_ELEVATOR,
                AX_ID_COLLECT_ROTATION
                ]:
            self.cs.ax[ax].free()

    @service.action
    def reset(self):
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=520)

        self.cs.ax[AX_ID_COLLECT_ELEVATOR].mode_joint()
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=200)

        self.cs.ax[AX_ID_COLLECT_ROTATION].mode_joint()
        self.cs.ax[AX_ID_COLLECT_ROTATION].move(goal=200)

    @Service.action
    def collector_open(self):
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=520)

    @Service.action
    def collector_close(self):
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=520)

    @Service.action
    def collector_hold(self):
        self.cs.ax[AX_ID_COLLECT].mode_wheel()
        self.cs.ax[AX_ID_COLLECT].turn(side=1, speed=512)

    @Service.action
    def collector_up(self):
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=800)

    def collector_is_up(self):
        return self.cs.ax[AX_ID_COLLECT_ELEVATOR].get_present_position == 800

    @Service.action
    def collector_down(self):
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=200)

    def collector_is_down(self):
        return self.cs.ax[AX_ID_COLLECT_ELEVATOR].get_present_position == 200

    @Service.action
    def collector_fireplace(self):
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=400)

    @Service.action
    def collector_rotate(self):
        if not self.collector_is_up():
            self.collector_up()
        rotate = 800 if self.rotation == 400 else 400
        self.cs.ax[AX_ID_COLLECT_ROTATION].move(goal=rotate)

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
