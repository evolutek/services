from evolutek.lib.robot.robot_actions_imports import *
from evolutek.services.robot import Robot

from evolutek.lib.robot.robot_actuators import ElevatorPosition, ClampsPosition


@if_enabled
@async_task
def grab_plants(self: Robot):
    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.3)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def place_plants(self, n=-1):
    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.LOW, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    if RobotStatus.get_status(self.move_clamps([0, 1, 2], ClampsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.3)

    if RobotStatus.get_status(self.move_elevator(ElevatorPosition.HIGH, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=0)
