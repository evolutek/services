from evolutek.lib.robot.robot_actions_imports import *

from evolutek.lib.robot.robot_actuators import ArmsPosition


# TODO: Compute points
@if_enabled
@async_task
def move_on_side(self, x, y, speed=None, timeout=None):
    r = RobotStatus.get_status(self.goto_avoid_extend(x, y, timeout=None, speed=None, async_task=False))

    if r == RobotStatus.Timeout:
        return RobotStatus.return_status(RobotStatus.Done, score=0)

    if r != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def open_right_arm(self):
    arm_id = 0 if self.side else 1

    if RobotStatus.get_status(self.move_arm(arm_id, ArmsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def open_left_arm(self):
    arm_id = 1 if self.side else 0

    if RobotStatus.get_status(self.move_arm(arm_id, ArmsPosition.OPEN, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def close_right_arm(self):
    arm_id = 0 if self.side else 1

    if RobotStatus.get_status(self.move_arm(arm_id, ArmsPosition.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def close_left_arm(self):
    arm_id = 1 if self.side else 0

    if RobotStatus.get_status(self.move_arm(arm_id, ArmsPosition.CLOSE, async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.2)

    return RobotStatus.return_status(RobotStatus.Done, score=0)

@if_enabled
@async_task
def count_solar_points(self):
    coords = [1280, 1500, 1720]
    score = 0
    pos = self.trajman.get_position()
    y = pos["y"]
    if (not self.side):
        y = 3000 - y
    
    for i in coords:
        print(f"I : {i}  Y : {y}")
        if (y < i):
            break
        score += 5

    return RobotStatus.return_status(RobotStatus.Done, score=score)

