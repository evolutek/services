from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def statuette(self):
    pickup_statuette(self)
    # Places it
    self.set_head_config(arm=2, config=2, async_task=False)
    self.set_elevator_config(arm=2, config=2, async_task=False)
    status = self.goto_avoid(120, 225, async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(0.2)
    self.pumps_drop(ids='2', async_task=False)
    sleep(0.1)
    # Moves back
    self.set_head_config(arm=2, config=0, async_task=False)
    self.set_elevator_config(arm=2, config=5, async_task=False)
    status = self.goto_avoid(x=250, y=225, async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    return RobotStatus.return_status(RobotStatus.Done)