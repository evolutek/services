from evolutek.lib.robot.robot_actions_imports import *

from evolutek.lib.robot.robot_actuators import *


@if_enabled
@async_task
def prepare_banner(self):
    if RobotStatus.get_status(self.move_pumps_arm(PumpsArmId.FRONT, PumpsArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.FRONT, 0.05, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.toggle_pumps(PumpsSetId.FRONT, True, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_banner(self):
    if RobotStatus.get_status(self.toggle_pumps(PumpsSetId.FRONT, False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1.2)

    if RobotStatus.get_status(self.move_pumps_arm(PumpsArmId.FRONT, PumpsArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.FRONT, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done, score=0)
