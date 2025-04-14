#!/usr/bin/env python3
import json

from cellaserv.service import Service
from evolutek.lib.settings import ROBOT


class Ax(Service):

    def __init__(self, ax):
        super().__init__(identification="%s-%d" % (ROBOT, ax))
        self.ax = ax
        print('[AX] ax: %d initialized' % self.ax)

    @Service.action("reset")
    def ax_reset(self):
        print('[AX] Reset ax: %d' % self.ax)

    @Service.action
    def dxl_get_result(self):
        print('[AX] Getting dxl result of ax: %d' % self.ax)
        return 0

    @Service.action
    def move(self, goal):
        print('[AX] Moving ax: %d to: %s' % (self.ax, goal))
        return 0

    @Service.action
    def get_present_position(self):
        print('[AX] Getting present position of ax: %d' % self.ax)
        return 0

    @Service.action
    def get_present_speed(self):
        print('[AX] Getting present speed of ax: %d' % self.ax)
        return 0

    @Service.action
    def get_present_load(self):
        print('[AX] Getting present load of ax: %d' % self.ax)
        return 0

    @Service.action
    def get_present_voltage(self):
        print('[AX] Getting present voltage of ax: %d' % self.ax)
        return 0

    @Service.action
    def get_present_temperature(self):
        print('[AX] Getting present temperature of ax: %d' % self.ax)
        return 0

    @Service.action
    def get_cw_angle_limit(self):
        print('[AX] Getting cw angle limit of ax: %d' % self.ax)
        return 0

    @Service.action
    def get_ccw_angle_limit(self):
        print('[AX] Getting ccw angle limit of ax: %d' % self.ax)
        return 0

    @Service.action
    def mode_wheel(self):
        print('[AX] Put ax: %d in wheel mode' % self.ax)
        return 0

    @Service.action
    def mode_joint(self):
        print('[AX] Put ax: %d in joint mode' % self.ax)
        return 0

    @Service.action
    def moving_speed(self, speed):
        print('[AX] Change ax: %d moving speed to: %d' % (self.ax, int(speed)))
        return 0

    @Service.action
    def turn(self, side: "1 or -1", speed):
        print('[AX] Turn ax: %d with moving speed to: %d on side: %d' % (self.ax, int(speed), int(side)))

    @Service.action
    def free(self):
        print('[AX] Free ax: %d' % self.ax)

async def main():
    data = None
    with open('/etc/conf.d/ax.json', 'r') as ax_file:
        data = ax_file.read()
        data = json.loads(data)

    if not ROBOT in data:
        print('[AX] Failed to init axs, ROBOT not existing')
        return

    axs = [Ax(ax=i) for i in data[ROBOT]]

    await asyncio.wait([ax.done() for ax in axs])


if __name__ == '__main__':
    asyncio.run(main())
