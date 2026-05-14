from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.robot.robot_actuators import *

@if_enabled
@async_task
def intelli(self, side=0):
    print(f"Entering intelli from side {side}")