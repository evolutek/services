from enum import Enum
from robot_actions_imports import *

class ElevatorPosition(Enum):
    Low = (717, 246)
    GetSecond = (632, 330)
    DropSecond = (572, 387)
    GetThird = (537, 423)
    DropThird = (479, 478)
    GetFourth = (427, 531)
    High = (193, 773)

    @staticmethod
    def get_position(position):
        if isinstance(position, ElevatorPosition):
            return position
        try:
            return ElevatorPosition.__members__[position]
        except:
            return None

@if_enabled
@async_task
def elevator_clamp_open(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 0))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 180))
    return check_status(status1, status2)

@if_enabled
@async_task
def elevator_clamp_open_half(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 12))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 168))
    return check_status(status1, status2)

@if_enabled
@async_task
def elevator_clamp_close(self):
    status1 = RobotStatus.get_status(self.actuators.servo_set_angle(9, 30))
    status2 = RobotStatus.get_status(self.actuators.servo_set_angle(15, 150))
    return check_status(status1, status2)

@if_enabled
@async_task
def elevator_move(self, positon):
    if ElevatorPosition.get_position(positon) is None:
        return RobotStatus.return_status(RobotStatus.Failed)
    position = ElevatorPosition.get_position(positon)
    status1 = RobotStatus.get_status(self.actuators.ax_move(1, position[0]))
    status2 = RobotStatus.get_status(self.actuators.ax_move(2, position[1]))
    return check_status(status1, status2)
