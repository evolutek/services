from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def build_cakes(self):
    return RobotStatus.check()