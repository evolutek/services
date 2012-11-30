#!/usr/bin/env python3
import time
import os
import ctypes

from cellaserv.service import Service

AX_LOCATION = "./ax"

DXL_LOCATION = "./libdxl.so"
DEVICE_ID = 0
BAUD_RATE = 34
COMMAND_GOAL_POSITION_L = 30

class AbstractAxService(Service):

    service_name = "ax"

    def __init__(self, ax):
        super().__init__(identification=str(ax))
        self.ax = ax

    @Service.action("reset")
    @Service.event("reset")
    @Service.event
    def ax_reset(self):
        self.move(500)

class SystemAxService(AbstractAxService):

    @Service.action
    def move(self, goal, ax=None):
        if not ax:
            ax = int(self.ax)
        os.system("{} {} {}".format(AX_LOCATION, ax, goal))

class CtypesService(AbstractAxService):

    def __init__(self, ax=None):
        super().__init__(ax)

        self.dxl = ctypes.CDLL(DXL_LOCATION)
        self.dxl.dxl_initialize(DEVICE_ID, BAUD_RATE)

    def __del__(self):
        self.dxl.dxl_terminate()


    @Service.action
    def move(self, goal, ax=None):
        if not ax:
            ax = int(self.ax)
        self.dxl.dxl_write_word(int(ax), COMMAND_GOAL_POSITION_L, int(goal))

def main():
    ax3 = CtypesService(ax=3)
    ax5 = CtypesService(ax=5)
    ax3.setup()
    ax5.setup()

    Service.loop()

if __name__ == "__main__":
    main()
