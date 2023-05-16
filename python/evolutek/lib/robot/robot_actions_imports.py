from evolutek.lib.robot.robot_trajman import RecalSensor
from evolutek.lib.settings import ROBOT
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.map.point import Point

from time import sleep
from math import pi

def check_status(*args, score=0):
    for stat in args:
        if stat != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
    return RobotStatus.return_status(RobotStatus.Done, score=score)