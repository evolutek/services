from evolutek.lib.robot.robot_actions_imports import *


def cleanup(self):
    pass


@if_enabled
@async_task
def lift_sample(self):
    score = 0

    status = RobotStatus.get_status(self.goto_avoid(300, 200, async_task=False, timeout=10))
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Down, async_task=False)
    sleep(0.5)

    status = RobotStatus.get_status(self.goth(-pi/2, async_task=False))
    if status == RobotStatus.Reached:
        status = RobotStatus.get_status(self.goto_avoid(300, 100, async_task=False))
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    self.pumps_get(ids="2", async_task=False)

    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)
    sleep(1)

    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)
    sleep(1)

    score += 1

    status = RobotStatus.get_status(self.goto_avoid(250, 500, async_task=False))
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Galery, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.GaleryLow, async_task=False)

    status = RobotStatus.get_status(self.goth(pi, async_task=False))
    if status == RobotStatus.Reached:
        status = RobotStatus.get_status(self.goto_avoid(195, 500, async_task=False))
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    self.pumps_drop(ids="2", async_task=False)
    sleep(0.5)

    score += 3

    status = RobotStatus.get_status(self.goto_avoid(300, 500, async_task=False))
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    return RobotStatus.return_status(RobotStatus.Done, score=score)
