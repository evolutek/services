from evolutek.lib.robot.robot_actions_imports import *


GRAB_LEVELS = [
    "GetSecond",
    "GetThird",
    "GetFourth"
]

DROP_LEVELS = [
    "Low",
    "DropSecond",
    "DropThird",
    "High"
]


@if_enabled
@async_task
def drop_until(self, amount = 1, drop_level = 0):
    amount = int(amount)
    if amount <= 0: return RobotStatus.return_status(RobotStatus.Done)
    status = []
    status.append(self.elevator_move(DROP_LEVELS[drop_level], async_task=False))
    sleep(0.5)
    status.append(self.clamp_open(async_task=False))
    sleep(0.2)
    score = min(amount, len(self.cakes_stack))
    self.cakes_stack = self.cakes_stack[amount:]
    if len(self.cakes_stack) > 0:
        status.append(self.elevator_move(GRAB_LEVELS[amount - 1 + drop_level], async_task=False))
        sleep(0.5)
        status.append(self.clamp_close(async_task=False))
        sleep(0.2)
    status.append(self.elevator_move("High", async_task=False))
    sleep(0.5)
    status.append(self.forward(-125, async_task=False))
    return RobotStatus.check(*status, score=score)


@if_enabled
@async_task
def drop_stacks(self, n=-1):
    score = 0
    i = 0
    while i != n and len(self.cakes_stack) > 0:
        r = self.drop_until(amount=3, async_task=False)
        if RobotStatus.get_status(r) == RobotStatus.Done:
            score += r['score']
        else:
            return RobotStatus.return_status(RobotStatus.Failed, score=score)
        i += 1
    return RobotStatus.return_status(RobotStatus.Done, score=score)


@if_enabled
@async_task
def drop_all(self):
    status = []
    status.append(self.clamp_open(async_task=False))
    sleep(0.5)
    status.append(self.forward(-125, async_task=False))
    sleep(1)
    print("******************* Status :", status)
    self.cakes_stack.clear()
    return RobotStatus.check(*status, score=3)
