from evolutek.lib.robot.robot_actions_imports import *

from evolutek.lib.robot.robot_actuators import *


@if_enabled
@async_task
def prepare_banner(self):
    if RobotStatus.get_status(self.move_pumps_arm(PumpsArmId.BACK, PumpsArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.BACK, 0.05, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.toggle_pumps(PumpsSetId.BACK, True, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_banner(self):
    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.BACK, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.toggle_pumps(PumpsSetId.BACK, False, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_pumps_arm(PumpsArmId.BACK, PumpsArmPosition.COLLAPSED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator_ex(ElevatorId.BACK, 0, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done, score=0)
