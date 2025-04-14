from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.robot.actions.plants import *
from evolutek.lib.robot.actions.herse import *
from evolutek.lib.robot.actions.pots import *

from enum import Enum


class PlantsSet(Enum):
    TOP_LEFT = {"x": 700}
    BOTTOM_LEFT = {"x": 1200} # TODO: Set correct x
    BOTTOM_MIDDLE = {}


@if_enabled
@async_task
def collect_aligned_plants(self, plants_set):
    if isinstance(plants_set, str):
        plants_set = PlantsSet[plants_set]

    # Move in front of plants set
    if RobotStatus.get_status(self.goto(plants_set["x"], 790, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    if RobotStatus.get_status(self.down_herse(async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def collect_spread_plants(self, x, y, theta):
    pass

