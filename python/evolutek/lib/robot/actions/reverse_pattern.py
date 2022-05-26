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
    # Partie Speedy
    self.set_elevator_config(arm=1, config=0, async_task=False)
    self.set_elevator_config(arm=3, config=0, async_task=False)
    self.set_head_config(arm=2, config=2, async_task=False)
    self.set_elevator_config(arm=2, config=0, async_task=False)
    sleep(1)
    self.goto_avoid(1910, 1130, async_task=False)
    self.move_trsl(10, 150, 150, 100, 1)
    sleep(0.5)
    self.set_elevator_config(arm=1, config=4, async_task=False)
    self.set_elevator_config(arm=3, config=4, async_task=False)
    sleep(1)
    """
    Pattern = self.get_pattern()
    self.set_elevator_config(arm=1, config=0, async_task=False)
    sleep(1)
    self.set_elevator_config(arm=3, config=0, async_task=False)
    sleep(1)
    self.move_trsl(10, 150, 150, 100, 0)
    sleep(0.5)
    self.goto_avoid(1800, 1130, async_task=False)

    self.goth(-(pi/2), async_task=False)
    pattern = Pattern - 1

    # Partie Jaro
    y = 1777.5
    if (pattern in [0, 3] and self.side) or (pattern in [1, 2] and not self.side):
        y = 1592.5
    self.goto_avoid(1830, y, async_task=False)

    # Partie reza
    if self.side:
        patterns = [
                [True, True, False, False, True, True, False],
                [False, True, True, True, False, False, True],
                [True, True, False, True, False, False, True],
                [False, True, True, False, True, True, False]
            ]
    else:
        patterns = [
                [True, True, False, True, False, False, True],
                [False, True, True, False, True, True, False],
                [True, True, False, False, True, True, False],
                [False, True, True, True, False, False, True]
            ]

    if (pattern in [0, 3] and self.side) or (pattern in [1, 2] and not self.side):
        plot = 5
    else:
        plot = 6
"""
    arm_open = self.left_arm_open if self.side else self.right_arm_open
    arm_close = self.left_arm_close if self.side else self.right_arm_close

    # Default pos : 2530
    """
    while self.trajman.get_position()['y'] > 680:
        # if patterns[pattern][plot]:
        sleep(1)
        arm_open(async_task=False)
        sleep(1)
        arm_close(async_task=False)
        sleep(1)

        #plot -= 1
        pos = self.trajman.get_position()["y"] - 185
        self.goto_avoid(1830, pos, async_task=False)
    """
    coords = self.get_pattern()
    score = 5
    self.set_elevator_config(arm=1, config = 0, async_task=False)
    self.set_elevator_config(arm=3, config = 0, async_task=False)
    my_y = self.trajman.get_position()['y']
    sleep(0.5)
    if not self.side: my_y = 3000 - my_y
    self.goto_avoid(1650, my_y, async_task = False)
    self.set_elevator_config(arm=2, config = 2, async_task=False)
    self.set_head_config(arm=2, config=0, async_task=False)
    sleep(1)

    while(len(coords) != 0):
        self.goto_avoid(1830, coords[0], async_task=False)
        self.goth(1.57, async_task=False)
        score = open_arm(self.side, score, self)
        coords.pop(0)

    return RobotStatus.return_status(RobotStatus.Done, score=score)

    # #if patterns[pattern][plot]:
    #    sleep(1)
    #    arm_open(async_task=False)
    #    sleep(1)
    #    arm_close(async_task=False)