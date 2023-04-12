from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep

def check_status(*args):
    for stat in args:
        if stat != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
    return RobotStatus.return_status(RobotStatus.Done)

@if_enabled
@async_task
def clamp_open(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 0))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 180))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_open_half(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 12))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 167))
    return check_status(status1, status2)

@if_enabled
@async_task
def clamp_close(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 25))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 155))
    return check_status(status1, status2)

@if_enabled
@async_task
def elevator_up(self):
    status1 = RobotStatus.get_status(self.actuators.ax_move(1, 512))
    status2 = RobotStatus.get_status(self.actuators.ax_move(2, 512))
    return check_status(status1, status2)

@if_enabled
@async_task
def elevator_down(self):
    status1 = RobotStatus.get_status(self.actuators.ax_move(1, 775))
    status2 = RobotStatus.get_status(self.actuators.ax_move(2, 180))
    return check_status(status1, status2)

@if_enabled
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
