import ctypes
import os

from evolutek.lib.component import Component, ComponentsHolder
from functools import wraps
from threading import Lock
from time import sleep

LIBDXL_PATH = [".", "/usr/lib"]

LIBDXL_PATH_ENV = os.environ.get("LIBDXL_PATH", None)
if LIBDXL_PATH_ENV:
    LIBDXL_PATH.insert(0, LIBDXL_PATH_ENV)

DEVICE_ID = 0
BAUD_RATE = 1  # Main robot USB2AX
DXL = None

NB_TRY = 3

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

def lock_dxl(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        with self.lock:
            return method(self, *args, **kwargs)
    return wrapped

def retry_dxl_send(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        i = 0
        while i < NB_TRY:
            method(self, *args, **kwargs)

            if self._dxl_get_result() == 1:
                return True

            i += 1
            sleep(0.025)

        print(f"[{self.name}] Failed to send command to AX {self.id} after {NB_TRY} tries")
        return False
    return wrapped


class AX12(Component):

    def __init__(self, id, lock):
        self.dxl = DXL
        self.lock = lock
        super().__init__('AX12', id)

    def _dxl_get_result(self):
        return int(self.dxl.dxl_get_result())

    @lock_dxl
    @retry_dxl_send
    def move(self, goal):
        print(f"[{self.name}] Moving {self.id} to {goal}")
        self.dxl.dxl_write_word(self.id, AX_GOAL_POSITION_L, int(goal))

    @lock_dxl
    def get_present_position(self):
        return self.dxl.dxl_read_word(self.id, AX_PRESENT_POSTION_L)

    @lock_dxl
    def get_present_speed(self):
        return self.dxl.dxl_read_word(self.id, AX_PRESENT_SPEED_L)

    @lock_dxl
    def get_present_load(self):
        return self.dxl.dxl_read_word(self.id, AX_PRESENT_LOAD_L)

    @lock_dxl
    def get_present_voltage(self):
        return self.dxl.dxl_read_byte(self.id, AX_PRESENT_VOLTAGE)

    @lock_dxl
    def get_present_temperature(self):
        return self.dxl.dxl_read_byte(self.id, AX_PRESENT_TEMPERATURE)

    @lock_dxl
    def get_cw_angle_limit(self):
        return self.dxl.dxl_read_word(self.id, AX_CW_ANGLE_LIMIT_L)

    @lock_dxl
    def get_ccw_angle_limit(self):
        return self.dxl.dxl_read_word(self.id, AX_CCW_ANGLE_LIMIT_L)

    @lock_dxl
    @retry_dxl_send
    def mode_wheel(self):
        self.dxl.dxl_write_word(self.id, AX_CW_ANGLE_LIMIT_L, 0)
        self.dxl.dxl_write_word(self.id, AX_CCW_ANGLE_LIMIT_L, 0)

    @lock_dxl
    @retry_dxl_send
    def mode_joint(self):
        self.dxl.dxl_write_word(self.id, AX_CW_ANGLE_LIMIT_L, 0)
        self.dxl.dxl_write_word(self.id, AX_CCW_ANGLE_LIMIT_L, 1023)

    @lock_dxl
    @retry_dxl_send
    def moving_speed(self, speed):
        self.dxl.dxl_write_word(self.id, AX_MOVING_SPEED_L, int(speed))

    @lock_dxl
    @retry_dxl_send
    def turn(self, side, speed):
        self.dxl.dxl_write_word(self.id, AX_MOVING_SPEED_L, (2**10 if side else 0) | int(speed))

    @lock_dxl
    @retry_dxl_send
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
        self.lock = Lock()
        super().__init__('AX12 holder', ids, AX12, [self.lock])

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
