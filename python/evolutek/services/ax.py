#!/usr/bin/env python3
import ctypes
import json
import os

from cellaserv.service import Service
from evolutek.lib.settings import ROBOT

LIBDXL_PATH = [".", "/usr/lib"]

LIBDXL_PATH_ENV = os.environ.get("LIBDXL_PATH", None)
if LIBDXL_PATH_ENV:
    LIBDXL_PATH.insert(0, LIBDXL_PATH_ENV)

DEVICE_ID = 0
BAUD_RATE = 1  # Main robot USB2AX

AX_TORQUE_ENABLE_B     = 24
AX_GOAL_POSITION_L     = 30
AX_MOVING_SPEED_L      = 32
AX_PRESENT_POSTION_L   = 36
AX_PRESENT_SPEED_L     = 38
AX_PRESENT_LOAD_L      = 40
AX_PRESENT_VOLTAGE     = 42
AX_PRESENT_TEMPERATURE = 43

AX_CW_ANGLE_LIMIT_L    = 6
AX_CCW_ANGLE_LIMIT_L   = 8

# Service class of an AX12
class Ax(Service):
    def __init__(self, ax):
        super().__init__(identification="%s-%d" % (ROBOT, ax))
        self.ax = ax

        # Open libdxl
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

        # Init AX12 bus
        ret = self.dxl.dxl_initialize(DEVICE_ID, BAUD_RATE)
        if ret != 1:
            raise RuntimeError("Cannot initialize device")

    # Reset AX12
    @Service.action("reset")
    def ax_reset(self):
        self.move(500)

    # Get the result of an querry
    @Service.action
    def dxl_get_result(self):
        return int(self.dxl.dxl_get_result())

    # Move the AX12
    # goal: position goal
    @Service.action
    def move(self, goal):
        return self.dxl.dxl_write_word(self.ax, AX_GOAL_POSITION_L, int(goal))

    # Get the present AX12 position
    @Service.action
    def get_present_position(self):
        return self.dxl.dxl_read_word(self.ax, AX_PRESENT_POSTION_L)

    # Get the present AX12 speed
    @Service.action
    def get_present_speed(self):
        return self.dxl.dxl_read_word(self.ax, AX_PRESENT_SPEED_L)

    # Get the present AX12 load
    @Service.action
    def get_present_load(self):
        return self.dxl.dxl_read_word(self.ax, AX_PRESENT_LOAD_L)

    # Get the present AX12 voltage
    @Service.action
    def get_present_voltage(self):
        return self.dxl.dxl_read_byte(self.ax, AX_PRESENT_VOLTAGE)

    # Get the present AX12 temperature
    @Service.action
    def get_present_temperature(self):
        return self.dxl.dxl_read_byte(self.ax, AX_PRESENT_TEMPERATURE)

    # Get the AX12 first angle limit
    @Service.action
    def get_cw_angle_limit(self):
        return self.dxl.dxl_read_word(self.ax, AX_CW_ANGLE_LIMIT_L)

    # Get the AX12 second angle limit
    @Service.action
    def get_ccw_angle_limit(self):
        return self.dxl.dxl_read_word(self.ax, AX_CCW_ANGLE_LIMIT_L)

    # Set AX12 to wheel mode
    @Service.action
    def mode_wheel(self):
        self.dxl.dxl_write_word(self.ax, AX_CW_ANGLE_LIMIT_L, 0)
        return self.dxl.dxl_write_word(self.ax, AX_CCW_ANGLE_LIMIT_L, 0)

    # Set AX12 to joint mode
    @Service.action
    def mode_joint(self):
        self.dxl.dxl_write_word(self.ax, AX_CW_ANGLE_LIMIT_L, 0)
        return self.dxl.dxl_write_word(self.ax, AX_CCW_ANGLE_LIMIT_L, 1023)

    # Set AX12 moving speed
    # speed: moving speed
    @Service.action
    def moving_speed(self, speed):
        return self.dxl.dxl_write_word(self.ax, AX_MOVING_SPEED_L, int(speed))

    # Make AX12 turning
    # side: move side
    # speed: moving speed
    @Service.action
    def turn(self, side: "1 or -1", speed):
        self.dxl.dxl_write_word(self.ax, AX_MOVING_SPEED_L,
                                (2**10 if int(side) == 1 else 0) | int(speed))

    # Free ax AX12
    @Service.action
    def free(self):
        self.dxl.dxl_write_byte(self.ax, AX_TORQUE_ENABLE_B, 0)

def main():

    # Read AX12 JSON config file
    data = None
    with open('/etc/conf.d/ax.json', 'r') as ax_file:
        data = ax_file.read()
        data = json.loads(data)

    if not ROBOT in data:
        print('[AX] Failed to init axs, ROBOT not existing')
        return

    # Init all AX12
    axs = [Ax(ax=i) for i in data[ROBOT]]

    Service.loop()

if __name__ == "__main__":
    main()
