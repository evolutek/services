from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def lift_sample(self):
    score = 0

    status = self.goto_avoid(300, 200, async_task=False, timeout=10)
    
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Down, async_task=False)
    sleep(0.5)

    self.goth(-pi/2, async_task=False)
    self.goto_avoid(300, 100, async_task=False)

    self.pumps_get(ids="2", async_task=False)
    
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)
    sleep(1)

    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)
    sleep(1)

    score += 1

    self.goto_avoid(250, 600, async_task=False)
    
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Galery, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.GaleryLow, async_task=False)

    self.goth(pi, async_task=False)
    self.goto_avoid(190, 600, async_task=False)
    
    self.pumps_drop(ids="2", async_task=False)
    sleep(0.5)

    score += 3

    self.goto_avoid(300, 600, async_task=False)

    return RobotStatus.return_status(RobotStatus.Done, score=score)
