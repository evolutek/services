from enum import Enum
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled

@if_enabled
@async_task
def clamp_open(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 0))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 180))
    return RobotStatus.return_status(RobotStatus.Done if status1 == RobotStatus.Done and status2 == RobotStatus.Done else RobotStatus.Failed)

@if_enabled
@async_task
def clamp_close(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(0, 19))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 161))
    return RobotStatus.return_status(RobotStatus.Done if status1 == RobotStatus.Done and status2 == RobotStatus.Done else RobotStatus.Failed)

@if_enabled
@async_task
def elevator_up(self):
    status1 = RobotStatus.get_status(self.actuators.ax_move(1, 777))
    status2 = RobotStatus.get_status(self.actuators.ax_move(2, 511))
    return RobotStatus.return_status(RobotStatus.Done if status1 == RobotStatus.Done and status2 == RobotStatus.Done else RobotStatus.Failed)

@if_enabled
@async_task
def elevator_down(self):
    status1 = RobotStatus.get_status(self.actuators.ax_move(1, 512))
    status2 = RobotStatus.get_status(self.actuators.ax_move(2, 246))
    return RobotStatus.return_status(RobotStatus.Done if status1 == RobotStatus.Done and status2 == RobotStatus.Done else RobotStatus.Failed)
