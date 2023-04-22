from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller

def check_status(*args):
    for stat in args:
        if stat != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
    return RobotStatus.return_status(RobotStatus.Done)

@if_enabled
@async_task
def canon_on(self):
    status1 = RobotStatus.get_status(self.actuators.esc_set_speed(13, 0.4))
    status2 = RobotStatus.get_status(self.actuators.esc_set_speed(14, 0.4))
    return check_status(status1, status2)

@if_enabled
@async_task
def canon_off(self):
    status1 = RobotStatus.get_status(self.actuators.esc_set_speed(13, 0))
    status2 = RobotStatus.get_status(self.actuators.esc_set_speed(14, 0))
    return check_status(status1, status2)

@if_enabled
@async_task
def turbine_on(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.esc_set_speed(8, 0.1)))

@if_enabled
@async_task
def turbine_off(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.esc_set_speed(8, 0)))

@if_enabled
@async_task
def extend_left_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(10, 83.6)))

@if_enabled
@async_task
def retract_left_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(10, 19.3)))

@if_enabled
@async_task
def extend_right_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(11, 96.4)))

@if_enabled
@async_task
def retract_right_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(11, 160.7)))

@if_enabled
@async_task
def clamp_open(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 0))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 180))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_open_half(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 12))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 168))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_close(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 30))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 150))
    return check_status(status1, status2)

@if_enabled
@async_task
def push_canon(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(12, 180)))

@if_enabled
@async_task
def push_tank(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(12, 51.4)))

@if_enabled
@async_task
def push_drop(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(12, 150)))

@if_enabled
@async_task
def elevator_up(self):
    status1 = RobotStatus.get_status(self.actuators.ax_move(1, 512))
    status2 = RobotStatus.get_status(self.actuators.ax_move(2, 180))
    return check_status(status1, status2)

@if_enabled
@async_task
def elevator_down(self):
    status1 = RobotStatus.get_status(self.actuators.ax_move(1, 775))
    status2 = RobotStatus.get_status(self.actuators.ax_move(2, 512))
    return check_status(status1, status2)

 check_status(status1, status2, status3, status4)
