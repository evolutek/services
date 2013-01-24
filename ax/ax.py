#!/usr/bin/env python3
import ctypes
import os
import os.path
import sys
import time

from cellaserv.service import Service

AX_LOCATION = "./ax"

LIBDXL_PATH = [".", "/usr/lib"]

LIBDXL_PATH_ENV = os.environ.get("LIBDXL_PATH", None)
if LIBDXL_PATH_ENV:
    LIBDXL_PATH.insert(0, LIBDXL_PATH_ENV)

DEVICE_ID = 0
BAUD_RATE = 34

AX_GOAL_POSITION_L     = 30
AX_MOVING_SPEED_L      = 32
AX_PRESENT_POSTION_L   = 36
AX_PRESENT_SPEED_L     = 38
AX_PRESENT_LOAD_L      = 40
AX_PRESENT_VOLTAGE     = 42
AX_PRESENT_TEMPERATURE = 43

AX_CW_ANGLE_LIMIT_L    = 6
AX_CCW_ANGLE_LIMIT_L   = 8

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
    def move(self, goal):
        os.system("{} {} {}".format(AX_LOCATION, self.ax, goal))

class CtypesService(AbstractAxService):

    def __init__(self, ax):
        super().__init__(ax)

        libdxl = None
        for path in LIBDXL_PATH:
            try:
                libdxl = ctypes.CDLL(path + "/libdxl.so")
            except:
                pass
        if not libdxl:
            raise RuntimeError("Cannot load libdxl.so, check LIBDXL_PATH")
        self.dxl = libdxl
        # TODO: rename self.dxl to self.libdxl

        ret = self.dxl.dxl_initialize(DEVICE_ID, BAUD_RATE)
        if ret != 1:
            raise RuntimeError("Cannot initialize device")

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

    @Service.action
    def get_cw_angle_limit(self):
        return self.dxl.dxl_read_word(self.ax, AX_CW_ANGLE_LIMIT_L)

    @Service.action
    def get_ccw_angle_limit(self):
        return self.dxl.dxl_read_word(self.ax, AX_CCW_ANGLE_LIMIT_L)

    @Service.action
    def mode_wheel(self):
        self.dxl.dxl_write_word(self.ax, AX_CW_ANGLE_LIMIT_L, 0)
        return self.dxl.dxl_write_word(self.ax, AX_CCW_ANGLE_LIMIT_L, 0)

    @Service.action
    def mode_joint(self):
        self.dxl.dxl_write_word(self.ax, AX_CW_ANGLE_LIMIT_L, 0)
        return self.dxl.dxl_write_word(self.ax, AX_CCW_ANGLE_LIMIT_L, 1023)

    @Service.action
    def moving_speed(self, speed):
        return self.dxl.dxl_write_word(self.ax, AX_MOVING_SPEED_L, int(speed))

def main():
    ax3 = CtypesService(ax=3)
    ax5 = CtypesService(ax=5)
    ax3.setup()
    ax5.setup()

    Service.loop()

if __name__ == "__main__":
    main()
