from evolutek.lib.robot.robot_actions_imports import *

from evolutek.lib.robot.robot_actuators import ArmPositions, ClawPositions

@if_enabled
@async_task
def crack_my_back(self):
    

    return RobotStatus.return_status(RobotStatus.Done)