from evolutek.lib.robot.robot_actions_imports import *

@if_enabled
@async_task
def shoot_n_cherries(self, n):
    status = []
    status.append(self.elevator_move("Low", async_task=False))

    try:
        n = int(n)
    except:
        return RobotStatus.return_status(RobotStatus.Failed)

    print('[ROBOT] Turning canon on !')
    status.append(self.canon_on(async_task=False))
    sleep(0.5)
    while n > 0:
        print('[ROBOT] Shooting a cherry !')
        status.append(self.push_tank(async_task=False))
        sleep(0.65)
        status.append(self.push_canon(async_task=False))
        sleep(0.38)
        n -= 1
        self.cherry_count -= 1
    print('[ROBOT] Turning canon off !')
    status.append(self.canon_off(async_task=False))
    return RobotStatus.check(*status, score=0)

@if_enabled
@async_task
def shoot_all_cherries(self):
    return self.shoot_n_cherries(self.cherry_count, async_task=False)
