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

    def __init__(self, ax):
        super().__init__(identification=str(ax))
        self.ax = ax

    @Service.action("reset")
    @Service.event("reset")
    @Service.event
    def ax_reset(self):
        self.move(500)

class SystemAxService(AbstractAxService):

    service_name = "ax"

    @Service.action
    def move(self, goal, ax=None):
        if not ax:
            ax = int(self.ax)
        os.system("{} {} {}".format(AX_LOCATION, ax, goal))

class CtypesService(AbstractAxService):

    service_name = "ax"

    def __init__(self):
        super().__init__()

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
    ax3 = SystemAxService(ax=3)
    ax5 = SystemAxService(ax=5)
    ax3.setup()
    ax5.setup()

    Service.loop()

if __name__ == "__main__":
    main()
