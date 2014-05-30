#!/usr/bin/env python3
from time import sleep

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

# main axs
AX_ID_COLLECT_ROTATION = "10"
AX_ID_COLLECT = "11"
AX_ID_COLLECT_ELEVATOR = "12"
AX_ID_LAUNCHER = "4"

AX_ELEVATOR_UP = 1000
AX_ELEVATOR_PUSH_FIRE = 600
AX_ELEVATOR_DOWN = 200
AX_ELEVATOR_FIREPLACE = 600
AX_COLLECTOR_OPEN = 1000
AX_COLLECTOR_CLOSE = 650
AX_COLLECTOR_PUSH_FIRE = 350
AX_ROTATION_START = 500
AX_ROTATION_END = 138

# others to come

# TODO:
#  - goals need to be checked when the collector is going to be replaced
#  - use configuration variables
#  - make it stateful
#  - sleep when it's needed

@Service.require("ax.4")
@Service.require("ax.10")
@Service.require("ax.11")
@Service.require("ax.12")
class Actuators(Service):

    def __init__(self):
        super().__init__()

        self.cs = CellaservProxy()
        self.rotation = AX_ROTATION_START

    def setup(self):
        super().setup()
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].mode_joint()
        self.cs.ax[AX_ID_COLLECT_ROTATION].mode_joint()
        self.cs.ax[AX_ID_LAUNCHER].mode_wheel()

    @Service.action
    def free(self):
        for ax in [
                AX_ID_COLLECT,
                AX_ID_COLLECT_ELEVATOR,
                AX_ID_COLLECT_ROTATION,
                AX_ID_LAUNCHER,
                ]:
            self.cs.ax[ax].free()

    @Service.action("reset")
    def collector_reset(self):
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].mode_joint()
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=AX_ELEVATOR_UP)

        sleep(1)
        self.cs.ax[AX_ID_COLLECT_ROTATION].mode_joint()
        self.cs.ax[AX_ID_COLLECT_ROTATION].move(goal=AX_ROTATION_START)
        self.rotation = AX_ROTATION_START

        sleep(2)
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_OPEN)

        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=AX_ELEVATOR_DOWN)


    @Service.action
    def collector_open(self):
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_OPEN)

    @Service.action
    def collector_close(self):
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_CLOSE)

    @Service.action
    def collector_push_fire(self):
        self.cs.ax[AX_ID_COLLECT].mode_joint()
        self.cs.ax[AX_ID_COLLECT].move(goal=AX_COLLECTOR_PUSH_FIRE)
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].mode_joint()
        self.cs.ax[AX_ID_COLLECT_ELEVATOR].move(goal=AX_ELEVATOR_PUSH_FIRE)

    @Service.action
    def collector_hold(self):
        self.cs.ax[AX_ID_COLLECT].mode_wheel()
        # increase if too weak
        self.cs.ax[AX_ID_COLLECT].turn(side=1, speed=650)

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
    def collector_has_fire(self):
        return 570 < self.cs.ax[AX_ID_COLLECT].get_present_position()

    @Service.action
    def launcher_fire(self):
        self.cs.ax[AX_ID_LAUNCHER].turn(side=1, speed=512)
        sleep(1)
        self.cs.ax[AX_ID_LAUNCHER].turn(side=1, speed=0)

    @Service.action
    def launcher_reload(self):
        self.cs.ax[AX_ID_LAUNCHER].turn(side=0, speed=512)
        sleep(1.5)
        self.cs.ax[AX_ID_LAUNCHER].turn(side=1, speed=0)

def main():
    actuators = Actuators()
    actuators.run()

if __name__ == '__main__':
    main()
