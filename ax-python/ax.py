#!/usr/bin/env python3
# TODO: rewrite using cellaserv.service.Service
# TODO: use identification instead of the ax parameter
# TODO: implement move_many(((ax0, goal0), (ax1, goal1)))
import time
import os
import ctypes

from cellaserv.service import Service

AX_LOCATION = "./ax"

DXL_LOCATION = "./libdxl.so"
DEVICE_ID = 0
BAUD_RATE = 34
COMMAND_GOAL_POSITION_L = 30

class SystemAxService(Service):

    service_name = "ax"

    @Service.action
    def move(self, ax, goal):
        os.system("{} {} {}".format(AX_LOCATION, ax, goal))

class CtypesService(Service):

    service_name = "ax"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dxl = ctypes.CDLL(DXL_LOCATION)
        self.dxl.dxl_initialize(DEVICE_ID, BAUD_RATE)

    def __del__(self):
        self.dxl.dxl_terminate()

    @Service.action
    def move(self, ax, goal):
        self.dxl.dxl_write_word(int(ax), COMMAND_GOAL_POSITION_L, int(goal))

def main():
    ax = CtypesService()
    ax.run()

if __name__ == "__main__":
    main()
