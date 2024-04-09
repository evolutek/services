from evolutek.lib.robot.robot_actions_imports import *

from evolutek.lib.robot.robot_actuators import HersePosition


@if_enabled
@async_task
def up_herse(self):
    if RobotStatus.get_status(self.move_herse(HersePosition.UP, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def down_herse(self):
    if RobotStatus.get_status(self.move_herse(HersePosition.DOWN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done, score=0)
