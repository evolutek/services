from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller
from status import check_status

@if_enabled
@async_task
def canon_on(self):
    status1 = RobotStatus.get_status(self.actuators.esc_set_speed(9, 0.35))
    status2 = RobotStatus.get_status(self.actuators.esc_set_speed(10, 0.35))
    return check_status(status1, status2)

@if_enabled
@async_task
def canon_off(self):
    status1 = RobotStatus.get_status(self.actuators.esc_set_speed(9, 0))
    status2 = RobotStatus.get_status(self.actuators.esc_set_speed(10, 0))
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
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(2, 100)))

@if_enabled
@async_task
def retract_left_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(2, 25)))

@if_enabled
@async_task
def extend_right_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(3, 100)))

@if_enabled
@async_task
def retract_right_vacuum(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(3, 175)))

@if_enabled
@async_task
def clamp_open(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 15))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(1, 165))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_open_half(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 30))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(1, 150))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_close(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 40))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(1, 140))
    return check_status(status1, status2)

@if_enabled
@async_task
def push_canon(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(4, 180)))

@if_enabled
@async_task
def push_tank(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(4, 55)))

@if_enabled
@async_task
def push_drop(self):
    return RobotStatus.return_status(RobotStatus.get_status(self.actuators.servo_set_angle(12, 172)))
