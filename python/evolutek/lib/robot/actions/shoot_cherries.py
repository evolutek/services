from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def shoot_n_cherries(self, n):
    try:
        n = int(n)
    except:
        return RobotStatus.return_status(RobotStatusFailed)

    print('[ROBOT] Turning canon on !')
    status = []
    status.append(self.canon_on(async_task=False))
    while n > 0:
        print('[ROBOT] Shooting a cherry !')
        status.append(self.push_tank(async_task=False))
        sleep(2)
        status.append(self.push_canon(async_task=False))
        sleep(1)
        n -= 1
        self.cherry_count -= 1
    print('[ROBOT] Turning canon off !')
    status.append(self.canon_off(async_task=False))
    return check_status(*status, score=0)

@if_enabled
@async_task
def shoot_all_cherries(self):
    return self.empty_n_cherries(self.cherry_count, async_task=False)
