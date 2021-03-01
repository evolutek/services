import ctypes
import os

from evolutek.lib.component import Component, ComponentsHolder

LIBDXL_PATH = [".", "/usr/lib"]

LIBDXL_PATH_ENV = os.environ.get("LIBDXL_PATH", None)
if LIBDXL_PATH_ENV:
    LIBDXL_PATH.insert(0, LIBDXL_PATH_ENV)

DEVICE_ID = 0
BAUD_RATE = 1  # Main robot USB2AX
DXL = None

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

class AX12(Component):

    def __init__(self, id):
        self.dxl = DXL
        super().__init__('AX12', id)

    def dxl_get_result(self):
        return int(self.dxl.dxl_get_result())

    def move(self, goal):
        return self.dxl.dxl_write_word(self.id, AX_GOAL_POSITION_L, int(goal))

    def get_present_position(self):
        return self.dxl.dxl_read_word(self.id, AX_PRESENT_POSTION_L)

    def get_present_speed(self):
        return self.dxl.dxl_read_word(self.id, AX_PRESENT_SPEED_L)

    def get_present_load(self):
        return self.dxl.dxl_read_word(self.id, AX_PRESENT_LOAD_L)

    def get_present_voltage(self):
        return self.dxl.dxl_read_byte(self.id, AX_PRESENT_VOLTAGE)

    def get_present_temperature(self):
        return self.dxl.dxl_read_byte(self.id, AX_PRESENT_TEMPERATURE)

    def get_cw_angle_limit(self):
        return self.dxl.dxl_read_word(self.id, AX_CW_ANGLE_LIMIT_L)

    def get_ccw_angle_limit(self):
        return self.dxl.dxl_read_word(self.id, AX_CCW_ANGLE_LIMIT_L)

    def mode_wheel(self):
        self.dxl.dxl_write_word(self.id, AX_CW_ANGLE_LIMIT_L, 0)
        return self.dxl.dxl_write_word(self.id, AX_CCW_ANGLE_LIMIT_L, 0)

    def mode_joint(self):
        self.dxl.dxl_write_word(self.id, AX_CW_ANGLE_LIMIT_L, 0)
        return self.dxl.dxl_write_word(self.id, AX_CCW_ANGLE_LIMIT_L, 1023)

    def moving_speed(self, speed):
        return self.dxl.dxl_write_word(self.id, AX_MOVING_SPEED_L, int(speed))

    def turn(self, side, speed):
        self.dxl.dxl_write_word(self.id, AX_MOVING_SPEED_L,
                                (2**10 if side else 0) | int(speed))

    def free(self):
        self.dxl.dxl_write_byte(self.ax, AX_TORQUE_ENABLE_B, 0)

    def reset(self):
        self.move(512)

    def __str__(self):
        s = "----------\n"
        s += "AX12: %d\n" % self.id
        s += "Position: %d\n" % self.get_present_position()
        s += "Speed: %d\n" % self.get_present_speed()
        s += "Load: %d\n" % self.get_present_load()
        s += "Voltage: %d\n" % self.get_present_voltage()
        s += "CW Angle limit: %d\n" % self.get_cw_angle_limit()
        s += "CCW Angle limit: %d\n" % self.get_ccw_angle_limit()
        s += "----------"
        return s

class AX12Controller(ComponentsHolder):

    def __init__(self, ids):
        super().__init__('AX12 holder', ids, AX12)

    def _initialize(self):
        libdxl = None
        for path in LIBDXL_PATH:
            try:
                libdxl = ctypes.CDLL(path + "/libdxl.so")
            except:
                pass

        if not libdxl:
            print('[%s] Cannot load libdxl.so, check LIBDXL_PATH' % self.name)
            return False

        global DXL
        DXL = libdxl

        if DXL.dxl_initialize(DEVICE_ID, BAUD_RATE) != 1:
            print('[%s] Cannot initialize device' % self.name)
            return False

        return True
