from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def fill_n_cherries(self, n):
    try:
        n = int(n)
    except:
        return RobotStatus.return_status(RobotStatusFailed)
    print('[ROBOT] Turning arm out on !')
    if RobotStatus.get_status(self.extend_right_vacuum(async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    while n > 0:
        print('[ROBOT] Vacuuming a cherry !')
        if RobotStatus.get_status(self.turbine_on(async_task=False)) != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(2)
        if RobotStatus.get_status(self.turbine_off(async_task=False)) != RobotStatus.Done:
            return RobotStatus.return_status(RobotStatus.Failed)
        sleep(2)
        n -= 1
        self.cherry_count += 1
    print('[ROBOT] Turning canon off !')
    if RobotStatus.get_status(self.retract_right_vacuum(async_task=False)) != RobotStatus.Done:
        return RobotStatus.return_status(RobotStatus.Failed)
    return RobotStatus.return_status(RobotStatus.Done)

@if_enabled
@async_task
def fill_all_cherries(self):
    return self.fill_n_cherries(10)
