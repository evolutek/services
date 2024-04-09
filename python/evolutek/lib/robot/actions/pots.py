from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def grab_pots(self):
    if RobotStatus.get_status(self.magnets_on([0, 1, 2], async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.05)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def release_pots(self):
    if RobotStatus.get_status(self.magnets_off([0, 1, 2], async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)

    sleep(0.05)

    return RobotStatus.return_status(RobotStatus.Done, score=0)


@if_enabled
@async_task
def move_trsl2(self, dest, acc, dec, maxspeed, sens):
    self.trajman.move_trsl(dest, acc, dec, maxspeed, sens)
