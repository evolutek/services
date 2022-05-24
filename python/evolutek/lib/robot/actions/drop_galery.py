from evolutek.lib.robot.robot_actions_imports import *
from evolutek.lib.utils.boolean import get_boolean


def cleanup(self):
    self.set_elevator_config(arm=FrontArmsEnum.Left,  config=ElevatorConfig.Closed, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Left,  config=HeadConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right, config=HeadConfig.Closed, async_task=False)
    self.pumps_drop(ids="1,3", async_task=False)
    sleep(0.5)


@if_enabled
@async_task
def drop_galery(self):
    score = 0

    # Reset middle arm position
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Closed, async_task=False)

    # Goto to galery
    status = RobotStatus.get_status(self.goto_avoid(300, 810, async_task=False))
    if status == RobotStatus.Reached:
        status = RobotStatus.get_status(self.goth(pi, async_task=False))
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Configure elevators and heads
    self.set_elevator_config(arm=FrontArmsEnum.Left,  config=ElevatorConfig.Closed, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Left,  config=HeadConfig.Mid, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right, config=HeadConfig.Mid, async_task=False)
    sleep(0.4)

    # Update score
    score += 3 if get_boolean(self.actuators.proximity_sensor_read(id = 1)) else 0
    score += 3 if get_boolean(self.actuators.proximity_sensor_read(id = 3)) else 0

    # Forward
    status = RobotStatus.get_status(self.goto_avoid(150, 810, async_task=False))
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Place sample
    self.pumps_drop(ids="1,3", async_task=False)
    sleep(0.5)

    status = RobotStatus.get_status(self.goto_avoid(300, 810, async_task=False))
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Cleanup
    cleanup(self)

    return RobotStatus.return_status(RobotStatus.Done, score=score)
