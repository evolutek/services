from distutils.command.clean import clean
from evolutek.lib.robot.robot_actions_imports import *


def to_radians(degrees):
    return degrees / 180 * pi


def cleanup(self):
    self.pumps_drop(ids="1", async_task=False)
    self.pumps_drop(ids="3", async_task=False)
    sleep(1)
    self.trajman.set_trsl_max_speed(100)
    self.set_elevator_config(arm=FrontArmsEnum.Left,  config=ElevatorConfig.Closed, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Left,  config=HeadConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right, config=HeadConfig.Closed, async_task=False)
    self.snowplow_close(async_task=False)
    self.bumper_close(async_task=False)
    sleep(1)


def play_path(rbt, path):
    for i in range(len(path)):
        point = path[i]
        if point[0] == "goto":
            status = rbt.goto_avoid(*point[1:], async_task=False, timeout=10)
        elif point[0] == "turn":
            status = rbt.goth(to_radians(point[1]), async_task=False)
        else:
            raise Exception("Invalid instruction : " + point[0])

        status = RobotStatus.get_status(status)
        if status != RobotStatus.Reached or status != RobotStatus.Done:
            return status
    return None


@if_enabled
@async_task
def collect_search_site(self):
    score = 0

    # Start pos = (995, 1360)
    path = [
        ("goto", 1194, 1360),
        ("turn", -50)
    ]

    status = play_path(self, path)
    if status:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Be ready to collect samples
    self.snowplow_open(async_task=False)
    sleep(0.5)

    # Decress speed to have a better samples transport
    self.trajman.set_trsl_max_speed(80)

    # Transport samples (with a specific path to currectly position them)
    path = [
        ("goto", 1460, 560)
    ]

    status = play_path(self, path)
    if status:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Reset move speed
    self.trajman.set_trsl_max_speed(100)

    back_pos = (1550, 460)
    front_pos = (1650, 340)

    # Down heads
    self.set_head_config(arm=FrontArmsEnum.Left,  config=HeadConfig.Down, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right, config=HeadConfig.Down, async_task=False)
    sleep(0.8)

    # Down arms
    self.set_elevator_config(arm=FrontArmsEnum.Left,  config=ElevatorConfig.Down, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Down, async_task=False)
    sleep(0.8)

    # Grab the two extern sample
    self.pumps_get(ids="1", async_task=False)
    self.pumps_get(ids="3", async_task=False)

    # Got to back pos
    status = self.goto_avoid(*back_pos, async_task=False, timeout=10)
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Push the middle sample
    status = RobotStatus.get_status(self.goto_avoid(*front_pos, async_task=False, timeout=10)) # Forward
    if status == RobotStatus.Reached:
        score += 5
        status = RobotStatus.get_status(self.goto_avoid(*back_pos, async_task=False, timeout=10)) # Backward

    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Release the two extern sample
    self.pumps_drop(ids="1", async_task=False)
    self.pumps_drop(ids="3", async_task=False)
    sleep(0.5)

    # Up arms
    self.set_elevator_config(arm=FrontArmsEnum.Left,  config=ElevatorConfig.Closed, async_task=False)
    self.set_elevator_config(arm=FrontArmsEnum.Right, config=ElevatorConfig.Closed, async_task=False)
    sleep(0.8)

    # Up heads
    self.set_head_config(arm=FrontArmsEnum.Left,  config=HeadConfig.Closed, async_task=False)
    self.set_head_config(arm=FrontArmsEnum.Right, config=HeadConfig.Closed, async_task=False)
    sleep(0.8)

    # Centralize the two remaining sample
    status = RobotStatus.get_status(self.goth(to_radians(-45 - 30), async_task=False))
    if status == RobotStatus.Reached:
        status = RobotStatus.get_status(self.goth(to_radians(-45 + 30), async_task=False))
    if status == RobotStatus.Reached:
        status = RobotStatus.get_status(self.goth(to_radians(-45), async_task=False))

    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Down bumpers
    status = RobotStatus.get_status(self.goto_avoid(1450, 550, async_task=False, timeout=10))
    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    self.bumper_open(async_task=False)
    sleep(0.5)

    # Push remaining samples
    status = RobotStatus.get_status(self.goto_avoid(*front_pos, async_task=False, timeout=10)) # Forward
    if status == RobotStatus.Reached:
        score += 5 * 2
        status = RobotStatus.get_status(self.goto_avoid(*back_pos, async_task=False, timeout=10)) # Backward

    if status != RobotStatus.Reached:
        cleanup(self)
        return RobotStatus.return_status(status, score=score)

    # Close snowplows
    self.snowplow_close(async_task=False)
    sleep(0.5)

    # Up bumpers
    self.bumper_close(async_task=False)
    sleep(0.5)

    return RobotStatus.return_status(RobotStatus.Done, score=score)
