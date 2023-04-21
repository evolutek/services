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
    status1 = RobotStatus.get_status(self.actuators.esc_set_value(13, 0.2))
    status2 = RobotStatus.get_status(self.actuators.esc_set_value(14, 0.2))
    return check_status(status1, status2)

@if_enabled
@async_task
def canon_off(self):
    status1 = RobotStatus.get_status(self.actuators.esc_set_value(13, 0))
    status2 = RobotStatus.get_status(self.actuators.esc_set_value(14, 0))
    return check_status(status1, status2)

@if_enabled
@async_task
def turbine_on(self):
    return RobotStatus.get_status(self.actuators.esc_set_value(8, 0.3))

@if_enabled
@async_task
def turbine_low_power(self):
    return RobotStatus.get_status(self.actuators.esc_set_value(8, 0.05))

@if_enabled
@async_task
def turbine_off(self):
    return RobotStatus.get_status(self.actuators.esc_set_value(8, 0))

@if_enabled
@async_task
def extend_left_vacuum(self):
    return RobotStatus.get_status(self.actuators.servo_set_angle(10, 83.6))

@if_enabled
@async_task
def retract_left_vacuum(self):
    return RobotStatus.get_status(self.actuators.servo_set_angle(10, 19.3))

@if_enabled
@async_task
def extend_right_vacuum(self):
    return RobotStatus.get_status(self.actuators.servo_set_angle(11, 160.7))

@if_enabled
@async_task
def retract_right_vacuum(self):
    return RobotStatus.get_status(self.actuators.servo_set_angle(11, 96.4))

@if_enabled
@async_task
def clamp_open(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 0))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 180))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_open_half(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 9.6))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 170.3))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_close(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 19.3))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 160.7))
    return check_status(status1, status2)

@if_enabled
@async_task
def push_canon(self):
    return RobotStatus.get_status(self.actuators.servo_set_angle(12, 180))

@if_enabled
@async_task
def push_tank(self):
    return RobotStatus.get_status(self.actuators.servo_set_angle(12, 51.4))

@if_enabled
@async_task
def push_drop(self):
    return RobotStatus.get_status(self.actuators.servo_set_angle(12, 173.6))

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

'''@if_enabled
@async_task
def grab_stack(self):
    status1 = RobotStatus.get_status(self.clamp_open_half(async_task=False))
    sleep(0.5)
    status2 = RobotStatus.get_status(self.clamp_open(async_task=False))
    sleep(0.5)
    status3 = RobotStatus.get_status(self.elevator_down(async_task=False))
    sleep(1)
    status4 = RobotStatus.get_status(self.clamp_close(async_task=False))
    sleep(0.5)
    return check_status(status1, status2, status3, status4)
'''