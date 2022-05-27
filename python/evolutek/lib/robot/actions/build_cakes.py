from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def build_cakes_raw(self, positions):
    return RobotStatus.check()


@if_enabled
@async_task
def build_cakes(self, theta: float):
    center = self.trajman.get_position()
    a = ()
    b = ()
    c = ()
    return build_cakes_raw()
