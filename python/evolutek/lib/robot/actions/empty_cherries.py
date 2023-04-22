from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def empty_n_cherries(self, n):
    try:
        n = int(n)
    except:
        return RobotStatus.return_status(RobotStatusFailed)
    print('[ROBOT] Turning canon on !')
    if RobotStatus.get_status(self.canon_on(async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    while n > 0:
        print('[ROBOT] Shooting a cherry !')
        if RobotStatus.get_status(self.push_tank(async_task=False)) != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(2)
        if RobotStatus.get_status(self.push_canon(async_task=False)) != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(1)
        n -= 1
        self.cherry_count -= 1
    print('[ROBOT] Turning canon off !')
    if RobotStatus.get_status(self.canon_off(async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    return RobotStatus.return_status(RobotStatus.Done, score=n)

@if_enabled
@async_task
def empty_all_cherries(self):
    return self.empty_n_cherries(self.cherry_count, async_task=False)