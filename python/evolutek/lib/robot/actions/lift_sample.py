from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def lift_sample(self):
    self.goto_avoid(340, 1975, async_task=False)
    self.set_elevator_config(arm=2, config=2, async_task=False)
    self.set_elevator_config(arm=2, config=0, async_task=False)
    self.goto_avoid(340, 1620, async_task=False)
    # self.actuators.pumps_drop(ids='2')