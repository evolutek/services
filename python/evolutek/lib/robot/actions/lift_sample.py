from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def lift_sample(self):
    self.goto_avoid(340, 1975, async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)
    self.goto_avoid(340, 1620, async_task=False)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    # self.actuators.pumps_drop(ids='2')
    return RobotStatus.return_status(RobotStatus.Done, score=0)
