from evolutek.lib.robot.robot_actions_imports import *
from random import choice

MIN_X = 600
MAX_X = 1400
MIN_Y = 600
MAX_Y = 2400

ROSE = 0
JAUNE = 1
MARRON = 2

# Format: ((x, y), couleur)
CAKES = [((225, 450 + 125), ROSE), ((225, 450 + 125 + 200), JAUNE), ((225, 3000 - 450 - 125 - 200), JAUNE), ((225, 3000 - 450 - 125), ROSE),  # x petits
        ((1000 - 275, 1125), MARRON), ((1000 - 275, 3000 - 1125), MARRON),  # x moyens -
        ((1000 + 275, 1125), MARRON), ((1000 + 275, 3000 - 1125), MARRON),  # x moyens +
        ((2000 - 225, 450 + 125), ROSE), ((2000 - 225, 450 + 125 + 200), JAUNE), ((2000 - 225, 3000 - 450 - 125 - 200), JAUNE), ((2000 - 225, 3000 - 450 - 125), ROSE)]  # x grands


@if_enabled
@async_task
def roam_stacks(self):
    for cake in CAKES:
        status = self.goto_avoid(x=cake[0][0], y=cake[0][1], async_task=False, timeout=10)
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
        sleep(5)
    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def go_grab_one(self):
    cake = random.choice(CAKES)
    # TODO: Compute offset
    status = self.goto_avoid(x=cake[0][0], y=cake[0][1], async_task=False, timeout=10)
    if RobotStatus.get_status(status) != RobotStatus.Reached:
        return RobotStatus.return_status(RobotStatus.get_status(status))
    sleep(0.5)
    self.grab_stack(async_task=False)
    sleep(1)
    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def go_grab_some(self):
    for x in range(randint(len(CAKES))):
        status = self.go_grab_one()
        if RobotStatus.get_status(status) != RobotStatus.Reached:
            return RobotStatus.return_status(RobotStatus.get_status(status))
    return RobotStatus.return_status(RobotStatus.Done, score=0)
