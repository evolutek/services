from evolutek.lib.robot.actions.actions import *
from evolutek.lib.robot.robot_actuators import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from evolutek.services.robot import Robot


@if_enabled
@async_task
def grab_crates(self, side: str):
    if side == "front":
        compacting_arms = [CompactingArmId.FRONT_LEFT, CompactingArmId.FRONT_RIGHT]
        reversing_arms = [ReversingArmId.FRONT_LEFT, ReversingArmId.FRONT_RIGHT]
        color_sensors = [1, 2, 3, 4]
    else:
        raise RuntimeError("Invalid side: %s" % side)

    for i in color_sensors:
        color = not self.actuators.color_sensor_read(i)

    """
    if RobotStatus.get_status(self.toggle_pumps(pumps, True, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.forward(180 if side == "front" else -180, async_task=False)) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_plank_arm(plank_arms, PlankArmPosition.LIFT, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.move_pumps_arm(pumps_arm, PumpsArmPosition.EXPANDED, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)
    """

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def drop_crates(self, side: str):
    if side == "front":
        compacting_arms = [CompactingArmId.FRONT_LEFT, CompactingArmId.FRONT_RIGHT]
        reversing_arms = [ReversingArmId.FRONT_LEFT, ReversingArmId.FRONT_RIGHT]
        color_sensors = [1, 2, 3, 4]
    else:
        raise RuntimeError("Invalid side: %s" % side)

    for i in color_sensors:
        color = not self.actuators.color_sensor_read(i)

    # TODO

    return RobotStatus.return_status(RobotStatus.Done)
