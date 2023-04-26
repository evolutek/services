from enum import Enum
from robot_actions_imports import *

class ElevatorPosition(Enum):
    Low = (750, 180)
    GetSecond = (655, 305)
    DropSecond = (635, 325)
    GetThird = (605, 355)
    DropThird = (585, 375)
    GetFourth = (555, 405)
    High = (520, 450)

    @staticmethod
    def get_position(position):
        if isinstance(position, ElevatorPositions):
            return position
        try:
            return ElevatorPosition.__members__[position]
        except:
            return None

@if_enabled
@async_task
def elevator_move(self, positon):
    if ElevatorPosition.get_position(positon) is None:
        return RobotStatus.return_status(RobotStatus.Failed)
    position = ElevatorPosition.get_position(positon)
    status1 = RobotStatus.get_status(self.actuators.ax_move(1, position[0]))
    status2 = RobotStatus.get_status(self.actuators.ax_move(2, position[1]))
    return check_status(status1, status2)
