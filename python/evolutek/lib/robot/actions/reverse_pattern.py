from evolutek.lib.robot.robot_actions_imports import *


def open_arm(side, score, self):
    if (side):
        self.right_arm_open(async_task = False)
        sleep(1)
        self.right_arm_close(async_task = False)
    else:
        self.left_arm_open(async_task = False)
        sleep(1)
        self.left_arm_close(async_task = False)
    return (score + 5)


@if_enabled
@async_task
def reverse_pattern(self):
    def cleanup():
        self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Closed, async_task=False)
        self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)
        self.set_elevator_config(arm=FrontArmsEnum.Left, config=ElevatorConfig.Closed, async_task=False)
        self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Closed, async_task=False)

    self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Closed, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Left, config=ElevatorConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Mid, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Center, config=ElevatorConfig.Closed, async_task=False)
    sleep(1)
    status = self.goto_avoid(1910, 1130, async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        cleanup()
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.move_trsl(10, 150, 150, 100, 1)
    sleep(0.5)
    self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.ExcavationSquares, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Left, config=ElevatorConfig.ExcavationSquares, async_task=False)
    sleep(1)
    arm_open = self.left_arm_open if self.side else self.right_arm_open
    arm_close = self.left_arm_close if self.side else self.right_arm_close
    coords = self.get_pattern()
    score = 5
    self.set_elevator_config(arm=FrontArmsEnum.Right, config = ElevatorConfig.Closed, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Left, config = ElevatorConfig.Closed, async_task=False)
    my_y = self.trajman.get_position()['y']
    sleep(0.5)
    my_y = my_y if self.side else 3000 - my_y
    status = self.goto_avoid(1650, my_y, async_task = False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        cleanup()
        return RobotStatus.return_status(RobotStatus.get_status(status))
    self.set_elevator_config(arm=FrontArmsEnum.Center, config = ElevatorConfig.Mid, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Center, config=HeadConfig.Closed, async_task=False)
    sleep(1)

    while(len(coords) != 0):
        status = self.goto_avoid(1830, coords[0], async_task=False, timeout=10)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            cleanup()
            return RobotStatus.return_status(RobotStatus.get_status(status))
        self.goth(1.57, async_task=False)
        score = open_arm(self.side, score, self)
        coords.pop(0)

    return RobotStatus.return_status(RobotStatus.Done, score=score)
