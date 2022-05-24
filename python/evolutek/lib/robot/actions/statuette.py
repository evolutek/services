from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def statuette(self):
    def cleanup():
        print("\n\n\n\n\nCLEANUP\n\n\n\n\n")
        self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Closed, async_task=False)
        self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.StoreStatuette, async_task=False)
    has_dropped = pickup_statuette(self)
    score = 0
    if (has_dropped):
        print("SUCCESS : Statuette dropped")
        score += 20
    else:
        print("FAILURE : Statuette not dropped")
    # Places it
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Mid, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Mid, async_task=False)
    status = self.goto_avoid(140, 225, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        cleanup()
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(0.2)
    self.pumps_drop(ids='2', async_task=False)
    sleep(0.1)
    # Moves back
    status = self.goto_avoid(x=250, y=225, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        cleanup()
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(0.3)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Closed, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.StoreStatuette, async_task=False)
    return RobotStatus.return_status(RobotStatus.Done, score=score)
