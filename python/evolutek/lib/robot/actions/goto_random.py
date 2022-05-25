from evolutek.lib.robot.robot_actions_imports import *
from random import randint

MIN_X = 600
MAX_X = 1400
MIN_Y = 600
MAX_Y = 2400

@if_enabled
@async_task
def goto_random(self):
    x = randint(MIN_X, MAX_X)
    y = randint(MIN_Y, MAX_Y)

    status = self.goto_avoid(x=x, y=y, async_task=False, timeout=10)

    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))

    sleep(0.5)
    return RobotStatus.return_status(RobotStatus.Done, score=0)
