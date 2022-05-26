from evolutek.lib.robot.robot_actions_imports import *


def to_radians(degrees):
    return degrees / 180 * pi


def play_path(rbt, path):
    for i in range(len(path)):
        point = path[i]
        if point[0] == "goto":
            rbt.goto_avoid(*point[1:], async_task=False)
        elif point[0] == "turn":
            rbt.goth(to_radians(point[1]), async_task=False)
        else:
            raise Exception("Invalid instruction : " + point[0])


@if_enabled
@async_task
def collect_search_site(self):
    # Start pos = (995, 1360)
    path = [
        ("goto", 1194, 1360),
        ("turn", -50)
    ]

    play_path(self, path)

    # Be ready to collect samples
    self.snowplow_open(async_task=False)
    sleep(0.5)

    # Decress speed to have a better samples transport
    self.trajman.set_trsl_max_speed(80)

    # Transport samples (with a specific path to currectly position them)
    path = [
        ("goto", 1460, 560)
    ]

    play_path(self, path)

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
    self.goto_avoid(*back_pos, async_task=False)
    
    # Push the middle sample
    self.goto_avoid(*front_pos, async_task=False) # Forward
    self.goto_avoid(*back_pos, async_task=False) # Backward

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
    self.goth(to_radians(-45 - 30), async_task=False)
    self.goth(to_radians(-45 + 30), async_task=False)
    self.goth(to_radians(-45), async_task=False)

    # Down bumpers
    self.goto_avoid(1450, 550, async_task=False)
    self.bumper_open(async_task=False)
    sleep(0.5)
    input()

    # Push remaining samples
    self.goto_avoid(*front_pos, async_task=False) # Forward
    self.goto_avoid(*back_pos, async_task=False) # Backward

    # Close snowplows
    self.snowplow_close(async_task=False)
    sleep(0.5)

    # Up bumpers
    self.bumper_close(async_task=False)
    sleep(0.5)
