from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from evolutek.lib.map.point import Point
from evolutek.lib.utils.color import Color
from time import sleep


def check_status(*args, score=0):
    for stat in args:
        stat = RobotStatus.get_status(stat)
        if stat != RobotStatus.Done and stat != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.Failed)
    return RobotStatus.return_status(RobotStatus.Done, score=score)
