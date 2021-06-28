import ctypes
import os

from evolutek.lib.component import Component, ComponentsHolder
from functools import wraps

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

def five_times(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        for _ in range(4):
            function(*args, **kwargs)
        return function(*args, **kwargs)
    return wrapped

class AX12(Component):

    def __init__(self, id):
        self.dxl = DXL
        super().__init__('AX12', id)

    @five_times
    def dxl_get_result(self):
        return int(self.dxl.dxl_get_result())

    @five_times
    def move(self, goal):
        print(f"[{self.name}] Moving {self.id} to {goal}")
        return self.dxl.dxl_write_word(self.id, AX_GOAL_POSITION_L, int(goal))

    @five_times
    def get_present_position(self):
        return self.dxl.dxl_read_word(self.id, AX_PRESENT_POSTION_L)

    @five_times
    def get_present_speed(self):
        return self.dxl.dxl_read_word(self.id, AX_PRESENT_SPEED_L)

    @five_times
    def get_present_load(self):
        return self.dxl.dxl_read_word(self.id, AX_PRESENT_LOAD_L)

    @five_times
    def get_present_voltage(self):
        return self.dxl.dxl_read_byte(self.id, AX_PRESENT_VOLTAGE)

    @five_times
    def get_present_temperature(self):
        return self.dxl.dxl_read_byte(self.id, AX_PRESENT_TEMPERATURE)

    @five_times
    def get_cw_angle_limit(self):
        return self.dxl.dxl_read_word(self.id, AX_CW_ANGLE_LIMIT_L)

    @five_times
    def get_ccw_angle_limit(self):
        return self.dxl.dxl_read_word(self.id, AX_CCW_ANGLE_LIMIT_L)

    @five_times
    def mode_wheel(self):
        self.dxl.dxl_write_word(self.id, AX_CW_ANGLE_LIMIT_L, 0)
        return self.dxl.dxl_write_word(self.id, AX_CCW_ANGLE_LIMIT_L, 0)

    @five_times
    def mode_joint(self):
        self.dxl.dxl_write_word(self.id, AX_CW_ANGLE_LIMIT_L, 0)
        return self.dxl.dxl_write_word(self.id, AX_CCW_ANGLE_LIMIT_L, 1023)

    @five_times
    def moving_speed(self, speed):
        return self.dxl.dxl_write_word(self.id, AX_MOVING_SPEED_L, int(speed))

    @five_times
    def turn(self, side, speed):
        self.dxl.dxl_write_word(self.id, AX_MOVING_SPEED_L,
                                (2**10 if side else 0) | int(speed))

    @five_times
    def free(self):
        self.dxl.dxl_write_byte(self.id, AX_TORQUE_ENABLE_B, 0)

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

    def __dict__(self):
        return {
            'name' : self.name,
            'id' : self.id,
            'position' : self.get_present_position(),
            'speed' : self.get_present_speed(),
            'load' : self.get_present_load(),
            'voltage' : self.get_present_voltage(),
            'cw_angle_limit' : self.get_cw_angle_limit(),
            'ccw_angle_limit' : self.get_ccw_angle_limit()
        }

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
