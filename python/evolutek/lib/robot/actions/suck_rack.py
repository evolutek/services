from evolutek.lib.robot.robot_actions_imports import *


@if_enabled
@async_task
def suck_rack(self, left=True, forward=True, quantity=7):
    status = []
    forward_value = 30 if forward else -30

    if left:
        status.append(self.extend_left_vacuum(async_task=False))
    else:
        status.append(self.extend_right_vacuum(async_task=False))

    for i in range(quantity):
        status.append(self.turbine_on(async_task=False))
        sleep(1)
        status.append(self.turbine_off(async_task=False))
        status.append(self.forward(forward_value, async_task=False))
        self.cherry_count += 1
        sleep(1)

    if left:
        status.append(self.retract_left_vacuum(async_task=False))
    else:
        status.append(self.retract_right_vacuum(async_task=False))

    return RobotStatus.check(*status, score=0)
