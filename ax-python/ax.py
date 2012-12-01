#!/usr/bin/env python3
import time
import os
import ctypes

from cellaserv.service import Service

AX_LOCATION = "./ax"

DXL_LOCATION = "./libdxl.so"
DEVICE_ID = 0
BAUD_RATE = 34

AX_GOAL_POSITION_L     = 30
AX_PRESENT_POSTION_L   = 36
AX_PRESENT_SPEED_L     = 38
AX_PRESENT_LOAD_L      = 40
AX_PRESENT_VOLTAGE     = 42
AX_PRESENT_TEMPERATURE = 43

class AbstractAxService(Service):

    service_name = "ax"

    def __init__(self, ax):
        super().__init__(identification=int(ax))
        self.ax = int(ax)

    @Service.action("reset")
    @Service.event("reset")
    @Service.event
    def ax_reset(self):
        self.move(500)

class SystemAxService(AbstractAxService):

    @Service.action
    def move(self, goal):
        os.system("{} {} {}".format(AX_LOCATION, self.ax, goal))

class CtypesService(AbstractAxService):

    def __init__(self, ax):
        super().__init__(ax)

        self.dxl = ctypes.CDLL(DXL_LOCATION)
        self.dxl.dxl_initialize(DEVICE_ID, BAUD_RATE)

    def __del__(self):
        self.dxl.dxl_terminate()

    @Service.action
    def move(self, goal):
        self.dxl.dxl_write_word(self.ax, AX_GOAL_POSITION_L, int(goal))

    @Service.action
    def get_present_position(self):
        return self.dxl.dxl_read_word(self.ax, AX_PRESENT_POSTION_L)

    @Service.action
    def get_present_speed(self):
        return self.dxl.dxl_read_word(self.ax, AX_PRESENT_SPEED_L)

    @Service.action
    def get_present_load(self):
        return self.dxl.dxl_read_word(self.ax, AX_PRESENT_LOAD_L)

    @Service.action
    def get_present_voltage(self):
        return self.dxl.dxl_read_byte(self.ax, AX_PRESENT_VOLTAGE)

    @Service.action
    def get_present_temperature(self):
        return self.dxl.dxl_read_byte(self.ax, AX_PRESENT_TEMPERATURE)

def main():
    ax3 = CtypesService(ax=3)
    ax5 = CtypesService(ax=5)
    ax3.setup()
    ax5.setup()

    Service.loop()

if __name__ == "__main__":
    main()
